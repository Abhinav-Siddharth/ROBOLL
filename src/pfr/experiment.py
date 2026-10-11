"""Identity and validity checks for new-format experiments."""
from pathlib import Path
from .tasks import TASKS
from .viz.state import reconstruct


def protect_output(path):
    path = Path(path).resolve()
    root = Path(__file__).resolve().parents[2]
    forbidden = {root/'results/raw/qwen.jsonl', root/'results/raw/qwen_pre_fix.jsonl',
                 root/'results/raw/pilot.jsonl'}
    if path in forbidden:
        raise ValueError('Archived experiment outputs may not be written')
    return path


def expected_ids(config, model='qwen2.5:7b'):
    tasks = TASKS if config.get('tasks', 'all') == 'all' else TASKS[:int(config['tasks'])]
    return {f"{model}|{m}|{t['id']}|{c}|{s}" for s in config['seeds']
            for t in tasks for c in config['cells'] for m in config['methods']}


def validate_rows(rows, expected):
    ids = [r['episode_id'] for r in rows]
    if len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError('Unexpected, missing or duplicate episode IDs')
    invalid = sum('invalid call' in s['detail'] for r in rows for s in r['steps'])
    parse_failures = sum(r['parse_failures'] for r in rows)
    if invalid or parse_failures:
        raise ValueError(f'Invalid calls={invalid}, exhausted parse/schema failures={parse_failures}')
    for row in rows:
        reconstruct(row)
    return {'rows': len(rows), 'unique_ids': len(set(ids)), 'invalid_calls': invalid,
            'parse_failures': parse_failures, 'replay_mismatches': 0}
