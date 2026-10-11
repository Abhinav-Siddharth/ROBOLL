"""Check an exact experiment batch and report invalid calls and success splits."""
import argparse
import csv
import json
from pathlib import Path
import yaml
from pfr.experiment import expected_ids, validate_rows


def summarize(path, config, out):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    expected = expected_ids(yaml.safe_load(Path(config).read_text()))
    selected = [r for r in rows if r['episode_id'] in expected]
    verdict = validate_rows(selected, expected)
    result = []
    for method, cell in sorted({(r['method'], r['cell']) for r in selected}):
        subset = [r for r in selected if r['method'] == method and r['cell'] == cell]
        failed = [s for r in subset for s in r['steps'] if s['code'] != 'OK']
        invalid = [s for s in failed if 'invalid call' in s['detail']]
        result.append(dict(method=method, cell=cell, n=len(subset),
                           invalid_episodes=sum(any('invalid call' in s['detail'] for s in r['steps']) for r in subset),
                           invalid_steps=len(invalid), failed_steps=len(failed),
                           autonomous_success=sum(r['outcome']=='success' and r['human_queries']==0 for r in subset),
                           assisted_success=sum(r['outcome']=='success' and r['human_queries']>0 for r in subset),
                           parse_failures=sum(r['parse_failures'] for r in subset),
                           wall_time_s=sum(r.get('wall_time_s', 0) for r in subset)))
    out = Path(out)
    with out.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    print(json.dumps(verdict, indent=2))
    print('method cell n invalid_episodes invalid_steps autonomous_success assisted_success')
    for r in result:
        print(*(r[k] for k in ['method','cell','n','invalid_episodes','invalid_steps',
                              'autonomous_success','assisted_success']))
    return verdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jsonl')
    parser.add_argument('--config', required=True)
    parser.add_argument('--out', required=True)
    a = parser.parse_args()
    summarize(a.jsonl, a.config, a.out)
