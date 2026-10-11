"""Verify archived hashes, frozen design and completed new experiment coverage."""
import hashlib
import json
from pathlib import Path
import yaml
from pfr.experiment import expected_ids, validate_rows
from pfr.faults import CELLS

ROOT = Path(__file__).resolve().parents[1]


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
    assert sum(r['reused'] for r in rows)==520
    assert sum(not r['reused'] for r in rows)==800
    digest=json.loads((ROOT/'results/meta.txt').read_text().split('PFR_PHASE2_PROVENANCE_JSON\n',1)[1])['model_digest']
    assert all(r['model_digest']==digest for r in rows if not r['reused'])
    assert all(r['reuse_source_sha256']==protected['results/raw/qwen.jsonl'] for r in rows if r['reused'])
    ablation=[json.loads(l) for l in (ROOT/'results/raw/qwen_v2_ablation.jsonl').read_text().splitlines() if l.strip()]
    cfg=yaml.safe_load((ROOT/'configs/v2_ablation.yaml').read_text())
    print('Ablation',validate_rows(ablation,expected_ids(cfg)))
    assert all(not r['reused'] and r['model_digest']==digest for r in ablation)
    print('VERIFIED: 800 new main episodes, 520 proven reused controls, 200 new ablation episodes')
