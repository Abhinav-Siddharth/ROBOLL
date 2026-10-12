"""Reproduce v2 from archived responses with the model backend prohibited."""
import argparse
import json
from pathlib import Path

from pfr import llm
from pfr.methods import make_method
from pfr.noise import make_observer
from pfr.runner import run_episode
from pfr.tasks import get_task
from pfr.viz.state import reconstruct

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT, *, full=True):
    root = Path(root)
    spec = json.loads((root/'configs/phase3b_hypotheses.json').read_text())
    rows = [json.loads(line) for line in (root/spec['baseline']).read_text().splitlines()]
    coordinates = {(r['task'], r['cell'], r['method']) for r in spec['smoke']['seed1']}
    if not full:
        rows = [r for r in rows if (r['task'], r['cell'], r['method']) in coordinates]
        if len(rows) != 20:
            raise ValueError('Predetermined regression grid does not contain 20 rows')
    def prohibited(*args, **kwargs):
        raise AssertionError('Offline check attempted a server request')
    before = (llm.CACHE_DIR, llm.CACHE_NAMESPACE, llm.CACHE_IDENTITY, llm._ollama_chat)
    llm.CACHE_DIR = str(root/'results/cache_v2')
    llm.CACHE_NAMESPACE = 'v2-format'
    llm.CACHE_IDENTITY = dict(model_digest=spec['qwen_digest'],
                             ollama_version=spec['ollama_version'], num_ctx=4096)
    llm._ollama_chat = prohibited
    calls = hits = reused = 0
    try:
        for row in rows:
            client = llm.LLMClient(row['model'], row['seed'])
            task = get_task(row['task'])
            fresh = run_episode(task, row['cell'], row['seed'], make_method(row['method']),
                                client, 8, observation_transform=make_observer(
                                    task, row['cell'], row['seed'], 0))
            if row.get('reused'):
                fresh['prompt_version'] = row['prompt_version']
                reused += 1
            differences = [key for key, value in fresh.items() if value != row.get(key)]
            if differences:
                raise ValueError(f"{row['episode_id']}: differences {differences}")
            reconstruct(row)
            calls += client.n_calls
            hits += client.cache_hits
    finally:
        llm.CACHE_DIR, llm.CACHE_NAMESPACE, llm.CACHE_IDENTITY, llm._ollama_chat = before
    result = dict(rows=len(rows), fresh_rows=len(rows)-reused, reused_rows=reused,
                  execution_field_mismatches=0, cache_hits=hits, llm_calls=calls,
                  server_requests=0, replay_mismatches=0,
                  comparison='All legacy payload fields; reused prompt_version preserved')
    print('OFFLINE_SEED0_CHECK '+json.dumps(result, sort_keys=True))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--sample', action='store_true')
    a = p.parse_args()
    check(a.root, full=not a.sample)
