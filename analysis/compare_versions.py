"""Descriptive version comparison and secondary matched-context ablation."""
import argparse
import importlib.util
from pathlib import Path
import pandas as pd
from pfr.metrics import episode_costs, outcome_flags, task_cluster_boot

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('primary_comparison', ROOT/'analysis/make_figures.py')
PRIMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRIMARY)


def augmented(path):
    df = PRIMARY.load([str(path)])
    if df.model.nunique() != 1 or df.duplicated(['task','cell','seed','method']).any():
        raise ValueError('Comparison needs unique units from one model')
    records = df.to_dict('records')
    for fn in (episode_costs, outcome_flags):
        fields = pd.DataFrame([fn(r) for r in records])
        for field in fields:
            df[field] = fields[field]
    return df


def compare(v1, v2, ablation, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    old, new = augmented(v1), augmented(v2)
    metric_names = ['raw_correct','no_human_correct','autonomous_solvable_or_permanent_correct',
                    'autonomous_success','human_assisted_success','anchor_regret',
                    'total_failure_cost','legacy_regret','loop','human_queries','tokens','latency_s']
    result = []
    for method in sorted(old.method.unique()):
        a, b = old[old.method.eq(method)], new[new.method.eq(method)]
        if len(a) != len(b):
            raise ValueError('Version method sizes differ')
        for metric in metric_names:
            result.append(dict(method=method, metric=metric, n=len(a),
                               v1=float(a[metric].mean()), v2=float(b[metric].mean()),
                               delta=float(b[metric].mean()-a[metric].mean())))
    pd.DataFrame(result).to_csv(out/'comparison.csv', index=False)
    per_cell = []
    for method, cell in sorted({(r.method,r.cell) for r in new.itertuples()}):
        a=old[(old.method==method)&(old.cell==cell)]
        b=new[(new.method==method)&(new.cell==cell)]
        for metric in ['raw_correct','no_human_correct','autonomous_success','human_assisted_success','anchor_regret','total_failure_cost']:
            per_cell.append(dict(method=method,cell=cell,metric=metric,n=len(a),
                                 v1=float(a[metric].mean()),v2=float(b[metric].mean()),
                                 delta=float(b[metric].mean()-a[metric].mean())))
    pd.DataFrame(per_cell).to_csv(out/'comparison_by_cell.csv',index=False)
    if ablation:
        extra = augmented(ablation)
        matched = pd.concat([new[new.cell.ne('NONE')], extra], ignore_index=True)
        tests=[]
        for baseline in ['B2','B4']:
            for metric in ['raw_correct','no_human_correct','autonomous_success','anchor_regret','total_failure_cost']:
                for unit, boot in [('paired_row',PRIMARY.paired_boot),('task_cluster',task_cluster_boot)]:
                    d,lo,hi,n=boot(matched,'B2C',baseline,metric,matched.index.notna())
                    tests.append(dict(comparison=f'B2C - {baseline}',metric=metric,
                                      bootstrap=unit,n_pairs=n,diff=d,ci_lo=lo,ci_hi=hi,
                                      reading=PRIMARY.reading(lo,hi,metric in ['anchor_regret','total_failure_cost']),
                                      status='secondary post-audit ablation'))
        pd.DataFrame(tests).to_csv(out/'ablation_comparisons.csv',index=False)
        matched.groupby('method')[metric_names].mean().to_csv(out/'faulted_method_means.csv')
    print(f'Version comparison: {len(result)} method/metric rows written to {out}')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--v1',default=str(ROOT/'results/raw/qwen.jsonl'))
    ap.add_argument('--v2',default=str(ROOT/'results/raw/qwen_v2.jsonl'))
    ap.add_argument('--ablation')
    ap.add_argument('--out',default=str(ROOT/'results/v2'))
    args=ap.parse_args()
    compare(args.v1,args.v2,args.ablation,args.out)
