"""Post-data descriptive analysis. No model calls or changes to primary analysis."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .metrics import episode_costs, outcome_flags

LABEL = 'exploratory, defined after seeing the data'
ALPHA = 0.05/3
N_BOOT = 10000
SEED = 0
KEYS = ['task', 'cell', 'seed']


def load(path):
    records = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    df = pd.DataFrame(records)
    if df.empty or df.model.nunique() != 1 or df.duplicated(KEYS+['method']).any():
        raise ValueError('Require nonempty unique units from one model')
    if (df.human_queries < 0).any() or not np.equal(df.human_queries, np.floor(df.human_queries)).all():
        raise ValueError('human_queries must be nonnegative integers')
    for fn in [episode_costs, outcome_flags]:
        extra = pd.DataFrame([fn(row) for row in records])
        for field in extra:
            df[field] = extra[field]
    df['group'] = df.cell.map(lambda cell: 'none' if cell == 'NONE' else ('T' if cell.startswith('TR-T') else cell[-1]))
    return df


def resampled_means(matrix, tasks, scheme, draws):
    """Preserve the row-mean estimand when whole unequal-sized tasks are sampled."""
    if scheme == 'paired_row':
        return matrix[draws].mean(axis=1)
    if scheme != 'task_cluster':
        raise ValueError('Unknown bootstrap scheme')
    unique = sorted(set(tasks))
    sums = np.array([matrix[np.array(tasks) == task].sum(axis=0) for task in unique])
    sizes = np.array([sum(t == task for t in tasks) for task in unique])
    return sums[draws].sum(axis=1)/sizes[draws].sum(axis=1)[:, None]


def bootstrap(df, metric, scheme, alpha=ALPHA, n_boot=N_BOOT, seed=SEED):
    pivot = df.pivot(index=KEYS, columns='method', values=metric).sort_index().sort_index(axis=1)
    if pivot.empty or pivot.isna().any().any():
        raise ValueError('Paired bootstrap requires complete matched units')
    matrix = pivot.to_numpy(dtype=float)
    tasks = pivot.index.get_level_values('task').tolist()
    n = len(matrix) if scheme == 'paired_row' else len(set(tasks))
    draws = np.random.default_rng(seed).integers(0, n, (n_boot, n))
    means = resampled_means(matrix, tasks, scheme, draws)
    result = []
    methods = list(pivot.columns)
    def row(a, b, estimate, samples):
        lo, hi = np.percentile(samples, [alpha/2*100, (1-alpha/2)*100])
        return dict(method=a, other=b, metric=metric, bootstrap=scheme, n_units=len(matrix),
                    n_tasks=len(set(tasks)), mean=float(estimate), ci_lo=float(lo), ci_hi=float(hi),
                    confidence=1-alpha, n_boot=n_boot, seed=seed, status=LABEL)
    for i, method in enumerate(methods):
        result.append(row(method, '', matrix[:, i].mean(), means[:, i]))
        for j in range(i):
            result.append(row(method, methods[j], (matrix[:, i]-matrix[:, j]).mean(), means[:, i]-means[:, j]))
    return result


def scopes(df):
    yield 'overall', df
    for cell in sorted(df.cell.unique()):
        yield cell, df[df.cell == cell]


def break_even(correct_delta, queries_delta):
    if queries_delta == 0:
        return (None, 'equal for every c in [0,1]' if correct_delta == 0 else 'no break-even in [0,1]')
    value = correct_delta/queries_delta
    return value, ('break-even in [0,1]' if 0 <= value <= 1 else 'no break-even in [0,1]')


def write_csv(rows, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def safe_output(path):
    path = Path(path).resolve()
    root = Path(__file__).resolve().parents[2]
    allowed = root/'results/derived_v2'
    if path != allowed and allowed not in path.parents and root in path.parents:
        raise ValueError('Repository outputs must be under results/derived_v2')
    path.mkdir(parents=True, exist_ok=True)
    return path
