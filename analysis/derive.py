"""Derive transparent costs and sensitivity outputs into an explicit new directory."""
import argparse
import importlib.util
from pathlib import Path

import pandas as pd
from pfr.metrics import episode_costs

SPEC = importlib.util.spec_from_file_location('frozen_primary', Path(__file__).with_name('make_figures.py'))
PRIMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRIMARY)


def derive(path, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    df = PRIMARY.load([str(path)])
    if df.model.nunique() != 1 or df.duplicated(['task', 'cell', 'seed', 'method']).any():
        raise ValueError('Derivation requires one model and unique task/cell/seed/method units')
    for field in ('anchor_attempts', 'total_failures', 'total_failure_cost', 'anchor_regret', 'legacy_regret'):
        df[field] = [episode_costs(row)[field] for row in df.to_dict('records')]
    df[['episode_id', 'method', 'task', 'cell', 'seed', 'anchor_attempts', 'total_failures',
        'total_failure_cost', 'anchor_regret', 'legacy_regret']].to_csv(out/'episode_costs.csv', index=False)
    df.groupby('method')[['anchor_attempts', 'total_failures', 'total_failure_cost',
                         'anchor_regret', 'legacy_regret']].mean().to_csv(out/'costs_overall.csv')
    h2 = []
    for metric in ('anchor_regret', 'total_failure_cost', 'legacy_regret'):
        for other in ('B0', 'B4', 'B3'):
            d, lo, hi, n = PRIMARY.paired_boot(df, 'B5', other, metric, df.group.eq('P'))
            h2.append(dict(hypothesis='H2', comparison=f'B5 - {other}',
                           subset_metric=f'P-cell {metric}', n_pairs=n,
                           diff=round(d, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                           reading=PRIMARY.reading(lo, hi, True)))
    pd.DataFrame(h2).to_csv(out/'h2_cost_definitions.csv', index=False)
    print(f'{len(df)} unique episodes; costs and H2 definitions written to {out}')
    return df


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('jsonl')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    derive(a.jsonl, a.out)
