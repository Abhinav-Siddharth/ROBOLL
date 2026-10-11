"""Metrics derived from traces, without changing archived runner semantics."""
from .faults import build_fault
from .tasks import get_task


def episode_costs(row):
    fault = build_fault(get_task(row['task']), row['cell'], row['seed'])
    anchor = sum(s['skill'] == fault.skill and s['params'].get('obj') == fault.target
                 for s in row['steps'])
    failures = sum(s['code'] != 'OK' for s in row['steps'])
    return {'anchor_attempts': anchor, 'total_failures': failures,
            'total_failure_cost': failures,
            'anchor_regret': max(0, anchor - row['oracle_attempts']),
            'legacy_regret': row['regret']}


def outcome_flags(row):
    success = row['outcome'] == 'success'
    no_human = row['human_queries'] == 0
    return {'autonomous_success': success and no_human,
            'human_assisted_success': success and not no_human,
            'raw_correct': bool(row['correct']),
            'no_human_correct': bool(row['correct']) and no_human,
            'autonomous_solvable_or_permanent_correct':
                bool(row['correct']) and (not row['solvable'] or no_human)}


def task_cluster_boot(df, a, b, metric, mask, alpha=0.05/3, seed=0, n_boot=10000):
    """Pair units first, then resample entire tasks, preserving the row-mean estimand."""
    import numpy as np
    piv = df[mask].pivot_table(index=['task', 'cell', 'seed'], columns='method',
                              values=metric, aggfunc='mean')
    if a not in piv or b not in piv:
        return np.nan, np.nan, np.nan, 0
    differences = (piv[a] - piv[b]).dropna()
    if differences.empty:
        return np.nan, np.nan, np.nan, 0
    grouped = differences.groupby(level='task')
    sums = grouped.sum().to_numpy()
    sizes = grouped.size().to_numpy()
    draws = np.random.default_rng(seed).integers(0, len(sums), (n_boot, len(sums)))
    means = sums[draws].sum(axis=1) / sizes[draws].sum(axis=1)
    lo, hi = np.percentile(means, [100*alpha/2, 100*(1-alpha/2)])
    return float(differences.mean()), float(lo), float(hi), len(differences)
