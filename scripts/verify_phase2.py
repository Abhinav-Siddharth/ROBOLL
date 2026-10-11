"""Verify archived hashes, frozen design and completed new experiment coverage."""
import hashlib
import json
from pathlib import Path
import yaml
from pfr.experiment import expected_ids, validate_rows
from pfr.faults import CELLS, build_fault
from pfr.env import Call
from pfr.tasks import get_task
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]


def verify_saved_metrics(rows):
    for row in rows:
        fault = build_fault(get_task(row['task']),row['cell'],row['seed'])
        failures=[s for s in row['steps'] if s['code']!='OK']
        keys=Counter(Call(s['skill'],s['params']).key() for s in failures)
        anchor_ok=any(s['code']=='OK' and fault.matches(Call(s['skill'],s['params'])) for s in row['steps'])
        attempts=len(failures)+int(anchor_ok)
        expected={'group':fault.group,'solvable':fault.solvable,'oracle_attempts':fault.oracle_attempts,
                  'n_fail':len(failures),'attempts_on_faulted_step':attempts,
                  'regret':max(0,attempts-fault.oracle_attempts),
                  'human_queries':sum(s['decision']=='escalate' for s in row['steps']),
                  'loop':row['outcome']=='cap_exceeded' or any(v>=3 for v in keys.values()),
                  'decisions':[s['decision'] for s in failures if s['decision']!='cutoff']}
        for key,value in expected.items():
            assert row[key]==value,(row['episode_id'],key,row[key],value)
        coordinate=f"{row['model']}|{row['method']}|{row['task']}|{row['cell']}|{row['seed']}"
        assert coordinate==row['episode_id']
    print(f'VERIFIED: all saved cost/group/failure/decision metrics for {len(rows)} rows')


if __name__=='__main__':
    protected=json.loads((ROOT/'audit/phase2/protected_sha256.json').read_text())
    for name,digest in protected.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise SystemExit(f'Protected v1 artifact changed: {name}')
    print(f'VERIFIED: {len(protected)} protected v1 artifacts unchanged')
    frozen=json.loads((ROOT/'audit/phase2/prereg_manifest.json').read_text())
    for name,key in [('analysis/make_figures.py','primary_analysis_sha256'),
                     ('configs/policy.yaml','policy_sha256'),('src/pfr/tasks.py','tasks_sha256')]:
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==frozen[key],name
    print('VERIFIED: primary analysis, policy and tasks remain frozen')
    rows=[json.loads(l) for l in (ROOT/'results/raw/qwen_v2.jsonl').read_text().splitlines() if l.strip()]
    config=dict(tasks='all',cells=CELLS,seeds=[0],methods=['B0','B1','B2','B3','B4','B5'])
    print('V2',validate_rows(rows,expected_ids(config)))
    verify_saved_metrics(rows)
    assert sum(r['reused'] for r in rows)==520
    assert sum(not r['reused'] for r in rows)==800
    digest=json.loads((ROOT/'results/meta.txt').read_text().split('PFR_PHASE2_PROVENANCE_JSON\n',1)[1])['model_digest']
    assert all(r['model_digest']==digest for r in rows if not r['reused'])
    assert all(r['reuse_source_sha256']==protected['results/raw/qwen.jsonl'] for r in rows if r['reused'])
    ablation=[json.loads(l) for l in (ROOT/'results/raw/qwen_v2_ablation.jsonl').read_text().splitlines() if l.strip()]
    cfg=yaml.safe_load((ROOT/'configs/v2_ablation.yaml').read_text())
    print('Ablation',validate_rows(ablation,expected_ids(cfg)))
    verify_saved_metrics(ablation)
    original=[json.loads(l) for l in (ROOT/'results/raw/qwen.jsonl').read_text().splitlines() if l.strip()]
    verify_saved_metrics(original)
    assert all(not r['reused'] and r['model_digest']==digest for r in ablation)
    print('VERIFIED: 800 new main episodes, 520 proven reused controls, 200 new ablation episodes')
