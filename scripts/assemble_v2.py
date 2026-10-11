"""Append only independently proven unaffected rows to the completed 800-row v2 run."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from pfr.experiment import expected_ids, validate_rows, protect_output
from pfr.faults import CELLS
from pfr.logging_utils import log_episode
from pfr.reuse import verified_reuse


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', default='results/raw/qwen_v2.jsonl')
    a = ap.parse_args()
    out = protect_output(a.out)
    source = Path('results/raw/qwen.jsonl')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    rows = [json.loads(l) for l in source.read_text().splitlines() if l.strip()]
    fresh = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    fault_config = dict(tasks='all', cells=CELLS[1:], seeds=[0], methods=['B2','B3','B4','B5'])
    validate_rows([r for r in fresh if not r.get('reused')], expected_ids(fault_config))
    commit = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    done = {r['episode_id'] for r in fresh}
    reusable = [r for r in rows if r['method'] in ('B0','B1') or r['cell']=='NONE']
    proven = [verified_reuse(r, digest, commit) for r in reusable]
    for row in proven:
        if row['episode_id'] not in done:
            log_episode(row, str(out))
    all_rows = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    primary_config = dict(tasks='all', cells=CELLS, seeds=[0], methods=['B0','B1','B2','B3','B4','B5'])
    verdict = validate_rows(all_rows, expected_ids(primary_config))
    verdict.update(reused_rows=sum(r['reused'] for r in all_rows), newly_inferred_rows=sum(not r['reused'] for r in all_rows),
                   source_sha256=digest, verification_commit=commit)
    Path('audit/phase2/gate4-reuse-proof.json').write_text(json.dumps(verdict, indent=2)+'\n')
    print(json.dumps(verdict, indent=2))
