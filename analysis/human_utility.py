"""Exploratory correctness minus human-query cost, with paired resampling."""
import argparse
from pathlib import Path

from pfr.exploratory import LABEL, ALPHA, N_BOOT, SEED, load, scopes, bootstrap, break_even, write_csv, safe_output


def utility(df, cost):
    return df.raw_correct.astype(float) - cost*df.human_queries


def analyze(datasets, out):
    out = safe_output(out)
    episodes, means, comparisons, crossings = [], [], [], []
    for version, path in datasets.items():
        df = load(path)
        for cost in [0.25, 0.5, 1.0]:
            df['utility'] = utility(df, cost)
            for row in df[['episode_id','task','cell','seed','method','raw_correct','human_queries','utility']].to_dict('records'):
                episodes.append(dict(version=version, c=cost, **row, status=LABEL))
            for scope, part in scopes(df):
                for scheme in ['paired_row', 'task_cluster']:
                    for row in bootstrap(part, 'utility', scheme):
                        dest = comparisons if row['other'] else means
                        dest.append(dict(version=version, scope=scope, c=cost, **row))
        for scope, part in scopes(df):
            group = part.groupby('method')[['raw_correct', 'human_queries']].mean()
            dc = float(group.loc['B5','raw_correct']-group.loc['B4','raw_correct'])
            dq = float(group.loc['B5','human_queries']-group.loc['B4','human_queries'])
            cstar, reading = break_even(dc, dq)
            crossings.append(dict(version=version, scope=scope, comparison='B5 - B4',
                                  correct_delta=dc, human_queries_delta=dq, c_star=cstar,
                                  reading=reading, status=LABEL))
    for name, rows in [('utility_episodes',episodes),('utility_means',means),
                       ('utility_comparisons',comparisons),('break_even',crossings)]:
        write_csv(rows, out/f'{name}.csv')
    (out/'README.md').write_text(
        '# Exploratory human-help analysis\n\nEvery number here is "'+LABEL+'".\n\n'
        'U(c) = raw_correct - c * human_queries; c = 0.25, 0.5, 1.0. '
        'Correctness includes permanent abstain/escalate and solvable success. '
        'Every query is penalized, including queries in incorrect episodes. '
        'Overall means give equal weight to each logged task/cell/seed unit. '
        'v1 means qwen.jsonl, the corrected archived dataset; qwen_pre_fix.jsonl is only the earlier ST-F archive.\n\n'
        f'Paired row and task-cluster percentile CIs use {N_BOOT} draws, seed {SEED}, '
        f'confidence {1-ALPHA:.9f} (matching the primary 0.05/3 alpha). '
        'The same resampled units are used across methods; comparison intervals bootstrap paired differences. '
        'Whole-task resampling preserves the row-mean estimand even with unequal task sizes. '
        'These marginal intervals do not control all post-data comparisons as a family. '
        'Degenerate empirical bootstrap CIs are not proof of zero population uncertainty.\n\n'
        'c_star solves delta_correct - c * delta_queries = 0. An outside-range root is reported, '
        'but is not a break-even in [0,1]. Equal intercept and slope means equality throughout the interval. '
        'Costs are chosen after seeing the data and do not estimate real human burden.\n')
    print(f'{LABEL}: {len(means)} means, {len(comparisons)} paired comparisons, {len(crossings)} break-even rows')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v1',required=True);p.add_argument('--v2',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();analyze({'v1':a.v1,'v2':a.v2},Path(a.out))
