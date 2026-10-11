"""Derive transparent costs and sensitivity outputs into an explicit new directory."""
import argparse
import importlib.util
from pathlib import Path

import pandas as pd
from pfr.metrics import episode_costs, outcome_flags, task_cluster_boot

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
    fields = ('autonomous_success', 'human_assisted_success', 'raw_correct',
              'no_human_correct', 'autonomous_solvable_or_permanent_correct')
    for field in fields:
        df[field] = [outcome_flags(row)[field] for row in df.to_dict('records')]
    df[['episode_id', 'method', 'task', 'cell', 'seed', *fields]].to_csv(
        out/'episode_outcomes.csv', index=False)
    counts = df.groupby(['method', 'cell'])[list(fields)].sum()
    counts.insert(0, 'n', df.groupby(['method', 'cell']).size())
    for field in fields:
        counts[field+'_rate'] = counts[field] / counts['n']
    counts.to_csv(out/'outcomes_by_cell.csv')
    overall = df.groupby('method')[list(fields)].sum()
    overall.insert(0, 'n', df.groupby('method').size())
    for field in fields:
        overall[field+'_rate'] = overall[field] / overall['n']
    overall.to_csv(out/'outcomes_overall.csv')
    solvable = df[df.solvable].groupby('method').agg(
        n=('solvable', 'size'), autonomous_success=('autonomous_success', 'sum'),
        human_assisted_success=('human_assisted_success', 'sum'))
    solvable['autonomous_success_rate'] = solvable.autonomous_success / solvable.n
    solvable.to_csv(out/'solvable_success.csv')
    (out/'metric_definitions.md').write_text(
        '# Derived metric definitions\n\n'
        'anchor_attempts counts every call matching the original first pick target.\n'
        'anchor_regret = max(0, anchor_attempts - oracle_attempts).\n'
        'total_failure_cost = total_failures = count of non-OK execution steps.\n'
        'legacy_regret retains the archived runner regret, including non-anchor failures.\n'
        'The oracle convention forces the original initial attempt before recovery.\n\n'
        'autonomous_success: success and human_queries == 0.\n'
        'human_assisted_success: success and human_queries > 0.\n'
        'raw_correct: success on solvable cells; abstain/escalate on permanent cells.\n'
        'no_human_correct: raw_correct and human_queries == 0.\n'
        'autonomous_solvable_or_permanent_correct: raw_correct and '
        '(permanent or human_queries == 0); this retains permanent human escalation.\n')
    h2 = []
    for metric in ('anchor_regret', 'total_failure_cost', 'legacy_regret'):
        for other in ('B0', 'B4', 'B3'):
            d, lo, hi, n = PRIMARY.paired_boot(df, 'B5', other, metric, df.group.eq('P'))
            h2.append(dict(hypothesis='H2', comparison=f'B5 - {other}',
                           subset_metric=f'P-cell {metric}', n_pairs=n,
                           diff=round(d, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                           reading=PRIMARY.reading(lo, hi, True)))
    pd.DataFrame(h2).to_csv(out/'h2_cost_definitions.csv', index=False)
    # Reuse the exact primary hypothesis selections; only the resampling unit changes.
    import inspect
    import ast
    source = inspect.getsource(PRIMARY.main)
    tree = ast.parse(source)
    assignment = next(node for node in tree.body[0].body
                      if isinstance(node, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'tests' for t in node.targets))
    specs = eval(compile(ast.Expression(assignment.value), '<frozen hypothesis masks>', 'eval'),
                 {'df': df, 'g': df.group})
    cluster = []
    for hid, a, b, metric, mask, label, negative in specs:
        d, lo, hi, n = task_cluster_boot(df, a, b, metric, mask)
        cluster.append(dict(hypothesis=hid, comparison=f'{a} - {b}', subset_metric=label,
                            n_pairs=n, diff=round(d, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                            reading=PRIMARY.reading(lo, hi, negative)))
    pd.DataFrame(cluster).to_csv(out/'hypotheses_task_cluster.csv', index=False)
    print(f'{len(df)} unique episodes; costs and H2 definitions written to {out}')
    return df


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('jsonl')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    derive(a.jsonl, a.out)
