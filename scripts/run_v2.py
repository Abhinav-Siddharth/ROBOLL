"""Run a new-format batch with immutable identity and explicit provenance."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import yaml
from pfr.experiment import protect_output, expected_ids, validate_rows
from pfr.logging_utils import load_done_ids, log_episode
from pfr.tasks import TASKS
from record_metadata import MARKER, get_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--batch', required=True)
    a = ap.parse_args()
    os.chdir(ROOT)
    output = protect_output(a.out)
    config = yaml.safe_load(Path(a.config).read_text())
    expected = expected_ids(config)
    provenance = json.loads((ROOT/'results/meta.txt').read_text().split(MARKER, 1)[1])
    digest = next(m['digest'] for m in get_json('tags')['models'] if m['name'] == provenance['model'])
    server = get_json('version')['version']
    if digest != provenance['model_digest'] or server != provenance['ollama_server_version']:
        raise SystemExit('Model/server identity changed; refusing inference under this amendment')
    os.environ['PFR_CACHE'] = str(ROOT/'results/cache_v2')
    os.environ['PFR_CACHE_NAMESPACE'] = 'v2-format'
    os.environ['PFR_MODEL_DIGEST'] = digest
    os.environ['PFR_OLLAMA_VERSION'] = server
    # Cache identity is read at module import, after configuring the new namespace.
    from pfr.llm import LLMClient
    from pfr.runner import run_episode
    from pfr.methods import make_method
    code = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], text=True):
        raise SystemExit('Tracked code is dirty; commit it before recording run provenance')
    existing = [json.loads(l) for l in output.read_text().splitlines() if l.strip()] if output.exists() else []
    if len({r['episode_id'] for r in existing}) != len(existing):
        raise SystemExit('Duplicate existing rows')
    if any(not r.get('reused') and (r.get('model_digest') != digest or r.get('cache_namespace') != 'v2-format')
           for r in existing):
        raise SystemExit('Existing rows have different or missing inference identity')
    done = load_done_ids(str(output))
    methods = {m: make_method(m) for m in config['methods']}
    tasks = TASKS if config.get('tasks') == 'all' else TASKS[:int(config['tasks'])]
    start = time.monotonic()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    executed = 0
    for seed in config['seeds']:
        for task in tasks:
            for cell in config['cells']:
                for name in config['methods']:
                    eid = f"{provenance['model']}|{name}|{task['id']}|{cell}|{seed}"
                    if eid in done:
                        continue
                    client = LLMClient(provenance['model'], seed, config['temperature'])
                    begin = time.monotonic()
                    row = run_episode(task, cell, seed, methods[name], client, config['max_failures'])
                    row.update(reused=False, dataset_version='v2-format', batch=a.batch,
                               code_commit=code, amendment_commit='9924f5e', model_digest=digest,
                               ollama_server_version=server, inference_options=provenance['options'],
                               cache_namespace='v2-format', cache_hits=client.cache_hits,
                               parse_retries=client.parse_retries,
                               wall_time_s=time.monotonic()-begin,
                               recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                    log_episode(row, str(output))
                    done.add(eid)
                    executed += 1
                    if executed % 10 == 0:
                        print(f'{a.batch}: {executed} newly completed; {len(done)} total in output; '
                              f'elapsed={time.monotonic()-start:.1f}s', flush=True)
    rows = [json.loads(l) for l in output.read_text().splitlines() if l.strip()]
    selected = [r for r in rows if r['episode_id'] in expected]
    verdict = validate_rows(selected, expected)
    summary = {**verdict, 'batch': a.batch, 'newly_executed': executed, 'started_at_utc': started,
               'wall_time_s': time.monotonic()-start, 'code_commit': code,
               'config': a.config, 'config_sha256': hashlib.sha256(Path(a.config).read_bytes()).hexdigest()}
    (ROOT/'audit/phase2'/f'{a.batch}-run.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
