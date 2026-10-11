"""Exploratory failure-cost / no-human-correctness Pareto plot."""
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pfr.exploratory import LABEL, load, write_csv, safe_output


def pareto(df):
    means = df.groupby('method')[['total_failure_cost','no_human_correct']].mean().reset_index()
    means['n'] = means.method.map(df.groupby('method').size())
    means['pareto'] = [not any((other.total_failure_cost <= row.total_failure_cost
                               and other.no_human_correct >= row.no_human_correct)
                              and (other.total_failure_cost < row.total_failure_cost
                                   or other.no_human_correct > row.no_human_correct)
                              for other in means.itertuples()) for row in means.itertuples()]
    return means


def analyze(datasets, out):
    out=safe_output(out)
    records=[]
    fig,axes=plt.subplots(1,len(datasets),figsize=(10,4),squeeze=False)
    for ax,(version,path) in zip(axes[0],datasets.items()):
        data=pareto(load(path))
        for row in data.to_dict('records'):
            records.append(dict(version=version,**row,status=LABEL))
            ax.scatter(row['total_failure_cost'],row['no_human_correct'],
                       marker='*' if row['pareto'] else 'o',s=110 if row['pareto'] else 45)
            ax.annotate(row['method'],(row['total_failure_cost'],row['no_human_correct']),
                        xytext=(5,5),textcoords='offset points')
        ax.set_title(version);ax.set_xlabel('Mean total failed executions')
        ax.set_ylabel('Correct termination with zero human queries')
        ax.set_ylim(0,1);ax.grid(alpha=0.2)
    fig.suptitle(LABEL,fontsize=10);fig.tight_layout()
    fig.savefig(out/'pareto.png',dpi=200);plt.close(fig)
    write_csv(records,out/'pareto.csv')
    print(f'{LABEL}: {len(records)} Pareto method/version rows; pareto.png written')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v1',required=True);p.add_argument('--v2',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();analyze({'v1':a.v1,'v2':a.v2},a.out)
