"""Prospective Phase 3b execution accounting; archived inference is unchanged.

Importing this module never contacts a model server.  The backend, filesystem
root and event sink are injectable so all failure gates can be tested offline.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import copy
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Callable

from jsonschema import ValidationError, validate

from . import llm as legacy_llm


class BatchStopped(RuntimeError):
    """An explicit prospective stop rule was reached."""


class CacheMismatch(BatchStopped):
    """A cache entry is missing, malformed, or has the wrong identity."""


def json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass
class BatchHealth:
    backend_attempts: int = 0
    completed_responses: int = 0
    json_schema_failures: int = 0
    transport_failures: int = 0
    exhausted_calls: int = 0
    backend_wall_time_s: float = 0.0
    events: list = field(default_factory=list)
    event_sink: Callable | None = field(default=None, repr=False)

    def emit(self, event):
        self.events.append(event)
        if self.event_sink:
            self.event_sink(event)

    def completed(self, *, invalid=False):
        self.completed_responses += 1
        self.json_schema_failures += int(invalid)
        # Integer comparison preserves the strict boundary: exactly 1% passes.
        if self.json_schema_failures * 100 > self.completed_responses:
            raise BatchStopped(
                f'Backend JSON/schema failure rate exceeds 1%: '
                f'{self.json_schema_failures}/{self.completed_responses}')

    def summary(self):
        return {key: getattr(self, key) for key in (
            'backend_attempts', 'completed_responses', 'json_schema_failures',
            'transport_failures', 'exhausted_calls', 'backend_wall_time_s')}


class Phase3bLLMClient:
    """The frozen call interface, with request-level stop and cache evidence.

    Each episode receives its own namespace.  A cold run refuses an already
    present entry instead of overwriting historical response/timing evidence.
    """

    def __init__(self, model, base_seed=0, temp=0.7, *, cache_dir, namespace,
                 identity, health=None, cold=False, offline=False, backend=None):
        if temp != 0.7 or identity.get('num_ctx') != 4096:
            raise ValueError('Phase 3b options are frozen at temperature=.7, num_ctx=4096')
        if not identity.get('model_digest') or not identity.get('ollama_version'):
            raise ValueError('Model digest and server version are required')
        if not namespace or namespace == 'legacy-v1':
            raise ValueError('A new Phase 3b cache namespace is required')
        if cold and offline:
            raise ValueError('Cold inference and offline replay are mutually exclusive')
        self.model, self.base_seed, self.temp = model, base_seed, temp
        self.cache_dir, self.namespace = Path(cache_dir), namespace
        self.identity = dict(identity)
        self.health = health if health is not None else BatchHealth()
        self.cold, self.offline = cold, offline
        self.backend = backend or legacy_llm._ollama_chat
        self.n_calls = self.tokens = self.parse_failures = 0
        self.cache_hits = self.parse_retries = 0
        self.latency = 0.0
        self.cache_keys = []
        self.request_log = []

    def _identity(self, messages, schema, seed):
        return dict(model=self.model, namespace=self.namespace, identity=self.identity,
                    seed=seed, temperature=self.temp,
                    messages_sha256=json_hash(messages), schema_sha256=json_hash(schema))

    def _record(self, saved, key, cache_hit):
        self.tokens += saved['tokens']
        self.latency += saved['latency_s']
        self.parse_retries += saved.get('parse_retries', 0)
        self.cache_hits += int(cache_hit)
        self.cache_keys.append(key)
        self.request_log.append(dict(
            cache_key=key, cache_hit=cache_hit,
            logical_seed=saved['request_identity']['seed'],
            response_sha256=json_hash(saved['content']),
            parse_retries=saved.get('parse_retries', 0)))
        return saved['content']

    def call(self, messages, schema):
        seed = self.base_seed * 1000 + self.n_calls
        self.n_calls += 1
        key = legacy_llm.cache_key(self.model, messages, schema, seed, self.temp,
                                   self.namespace, self.identity)
        path = self.cache_dir / f'{key}.json'
        request_identity = self._identity(messages, schema, seed)
        if path.exists():
            if self.cold:
                raise CacheMismatch('Cold namespace already contains a request entry')
            try:
                saved = json.loads(path.read_text())
                if saved.get('request_identity') != request_identity:
                    raise ValueError('request identity changed')
                validate(saved['content'], schema)
                if not isinstance(saved['tokens'], int) or saved['tokens'] < 0:
                    raise ValueError('invalid token count')
                if not isinstance(saved['latency_s'], (int, float)) or saved['latency_s'] < 0:
                    raise ValueError('invalid latency')
                if saved.get('parse_retries') not in (0, 1, 2):
                    raise ValueError('invalid retry count')
            except (OSError, ValueError, KeyError, ValidationError) as error:
                raise CacheMismatch(f'Invalid cache entry {key}: {error}') from error
            return self._record(saved, key, True)
        if self.offline:
            raise CacheMismatch(f'Offline cache miss: {key}')

        for retry in range(3):
            out = None
            backend_seed = seed + 100003 * retry
            event = dict(namespace=self.namespace, cache_key=key,
                         logical_seed=seed, backend_seed=backend_seed,
                         retry_index=retry, model=self.model)
            start = time.monotonic()
            self.health.backend_attempts += 1
            try:
                out = self.backend(self.model, messages, schema, backend_seed, self.temp)
                validate(out['content'], schema)
            except (json.JSONDecodeError, KeyError, AttributeError, ValidationError) as error:
                elapsed = time.monotonic() - start
                self.health.backend_wall_time_s += elapsed
                event.update(status='json_schema_failure', elapsed_s=elapsed,
                             error_type=type(error).__name__, error=str(error))
                if isinstance(error, json.JSONDecodeError):
                    event['invalid_response'] = error.doc
                elif isinstance(error, ValidationError):
                    event['invalid_response'] = out['content'] if out else error.instance
                self.health.emit(event)
                self.health.completed(invalid=True)
                continue
            except Exception as error:
                elapsed = time.monotonic() - start
                self.health.backend_wall_time_s += elapsed
                self.health.transport_failures += 1
                event.update(status='transport_failure', elapsed_s=elapsed,
                             error_type=type(error).__name__, error=str(error))
                self.health.emit(event)
                raise BatchStopped(f'Transport/server failure: {error}') from error
            elapsed = time.monotonic() - start
            self.health.backend_wall_time_s += elapsed
            event.update(status='valid', elapsed_s=elapsed, tokens=out['tokens'])
            self.health.emit(event)
            self.health.completed()
            saved = {**out, 'parse_retries': retry, 'request_identity': request_identity}
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Never replace a historical response, including in a racing process.
            with path.open('x') as handle:
                json.dump(saved, handle, sort_keys=True)
                handle.write('\n')
            return self._record(saved, key, False)
        self.parse_failures += 1
        self.health.exhausted_calls += 1
        raise BatchStopped('Exhausted all three frozen JSON/schema attempts')


def episode_id(model, coordinate):
    value = f"{model}|{coordinate['method']}|{coordinate['task']}|{coordinate['cell']}|{coordinate['seed']}"
    if coordinate.get('noise_p', 0):
        value += f"|noise={round(coordinate['noise_p'] * 100)}"
    return value


def episode_namespace(run_namespace, model, coordinate):
    return f'{run_namespace}/episode-{json_hash(episode_id(model, coordinate))}'


def run_coordinates(spec, design, *, smoke=False):
    if smoke:
        if design not in spec['smoke']:
            raise ValueError('No preregistered smoke sample for this design')
        return copy.deepcopy(spec['smoke'][design])
    if design not in spec['full_outputs']:
        raise ValueError('Unknown frozen design')
    seed = int(design[-1]) if design in ('seed1', 'seed2') else 0
    p = int(design[-2:]) / 10 if design.startswith('noise_p') else 0
    methods = spec['methods'] if design.startswith('seed') else (
        spec['noise_methods'] if p else spec['faulted_methods'])
    cells = spec['cells'] if design.startswith('seed') else spec['cells'][1:]
    return [dict(task=f't{i:02}', cell=cell, method=method, seed=seed, noise_p=p)
            for i in range(1, 21) for cell in cells for method in methods]


def assert_hashes(root, expected):
    root = Path(root).resolve()
    for name, digest in expected.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or file_hash(path) != digest:
            raise BatchStopped(f'Frozen input missing or changed: {name}')


def protected_output(root, relative, allowed, *, resume=False, provenance=None):
    """Only a declared new destination can be created or validated for resume."""
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or relative not in allowed:
        raise BatchStopped('Output is not a preregistered new destination')
    if path.exists():
        if not resume:
            raise BatchStopped('Output already exists; refusing to overwrite it')
        if not provenance:
            raise BatchStopped('Resume requires immutable provenance')
        for line in path.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise BatchStopped('Partial output retained; disclose before a fresh run') from error
            if any(row.get(k) != v for k, v in provenance.items()):
                raise BatchStopped('Existing row provenance differs from requested run')
    return path


def check_row(row):
    from .viz.state import reconstruct
    from .env import Call, Env
    from .tasks import get_task
    task = get_task(row['task'])
    validator = Env(task['init_state'])
    for step in row['steps']:
        if validator.validate_call(Call(step['skill'], step['params'])) is not None:
            raise BatchStopped(f"Invalid executed skill call: {row['episode_id']}")
    reconstruct(row)
    if row.get('parse_failures'):
        raise BatchStopped('Exhausted logical request in recorded row')


def replay_cached_row(row, *, cache_dir):
    from .methods import make_method
    from .noise import make_observer
    from .runner import run_episode
    from .tasks import get_task
    check_row(row)
    client = Phase3bLLMClient(
        row['model'], row['seed'], cache_dir=cache_dir,
        namespace=row['cache_namespace'], identity=row['cache_identity'], offline=True)
    task = get_task(row['task'])
    fresh = run_episode(task, row['cell'], row['seed'], make_method(row['method']),
                        client, 8, observation_transform=make_observer(
                            task, row['cell'], row['seed'], row['noise_p']))
    fresh['episode_id'] = episode_id(row['model'], row)
    if row.get('reused'):
        fresh['prompt_version'] = row['prompt_version']
    differences = [key for key, value in fresh.items() if value != row.get(key)]
    if differences or client.cache_keys != row['cache_keys']:
        raise CacheMismatch(f"Cache-only replay mismatch: {row['episode_id']}: {differences}")
    return dict(logical_calls=client.n_calls, cache_hits=client.cache_hits)


def prove_model_independent_reuse(source, model, source_hash, commit):
    from .methods import make_method
    from .reuse import NoInferenceClient
    from .runner import run_episode
    from .tasks import get_task
    if (source['method'] not in ('B0', 'B1') and source['cell'] != 'NONE') or source['llm_calls']:
        raise BatchStopped('Attempted reuse of a model-dependent source row')
    fresh = run_episode(get_task(source['task']), source['cell'], source['seed'],
                        make_method(source['method']), NoInferenceClient(model, source['seed']))
    ignored = {'model', 'episode_id', 'prompt_version'}
    differences = [key for key, value in fresh.items()
                   if key not in ignored and value != source.get(key)]
    if differences:
        raise BatchStopped(f'Deterministic second-model reuse mismatch: {differences}')
    # Preserve the archived label; all actual execution fields were reconstructed.
    fresh['prompt_version'] = source['prompt_version']
    fresh.update(reused=True, noise_p=0, reuse_source_model=source['model'],
                 reuse_source_episode_id=source['episode_id'],
                 reuse_source_file='results/raw/qwen_v2.jsonl', reuse_source_sha256=source_hash,
                 reuse_verification_commit=commit,
                 reuse_verification='Fresh deterministic execution; model calls prohibited')
    return fresh


def check_model_metadata(model, spec, tags, version, show):
    matches = [item for item in tags.get('models', []) if item.get('name') == model]
    if len(matches) != 1:
        raise BatchStopped('Requested model is not uniquely installed')
    entry = matches[0]
    if version.get('version') != spec['ollama_version']:
        raise BatchStopped('Ollama server differs from frozen version')
    if model == spec['qwen_model'] and entry.get('digest') != spec['qwen_digest']:
        raise BatchStopped('Qwen digest differs from frozen primary model')
    if model not in (spec['qwen_model'], spec['second_model']):
        raise BatchStopped('Model is outside the frozen design')
    if not entry.get('digest') or not entry.get('size'):
        raise BatchStopped('Installed model digest/size is unavailable')
    return dict(model=model, model_digest=entry['digest'], model_size_bytes=entry['size'],
                ollama_server_version=version['version'], details=show.get('details', {}),
                template_sha256=hashlib.sha256(show.get('template', '').encode()).hexdigest(),
                model_parameters=show.get('parameters', ''), options=dict(temperature=.7, num_ctx=4096))


def validate_grid(rows, model, coordinates):
    expected = {episode_id(model, c): c for c in coordinates}
    ids = [r['episode_id'] for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise BatchStopped('Unexpected, missing or duplicate episode IDs')
    for row in rows:
        coordinate = expected[row['episode_id']]
        if row['model'] != model or any(row.get(key) != value for key, value in coordinate.items()):
            raise BatchStopped('Episode ID or noise identity disagrees with coordinates')
        check_row(row)
    return dict(rows=len(rows), unique_ids=len(ids), invalid_calls=0, replay_mismatches=0)


def safe_run_id(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', value):
        raise ValueError('Run ID must be a short filename-safe identifier')
    return value
