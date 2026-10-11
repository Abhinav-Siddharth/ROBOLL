"""Companion figures with literal-cost and no-human labels, separate from frozen primary plots."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from compare_versions import augmented, PRIMARY


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jsonl')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    df=augmented(args.jsonl)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    methods=PRIMARY.METHOD_ORDER;groups=['T','F','P'];width=0.8/len(methods)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,metric,title in zip(axes,['anchor_regret','total_failure_cost'],
                               ['Literal anchor regret','Total failed executions']):
        for j,method in enumerate(methods):
            values=[df[(df.method==method)&(df.group==group)][metric].mean() for group in groups]
            ax.bar(np.arange(len(groups))+j*width,values,width,label=method)
        ax.set_xticks(np.arange(len(groups))+0.4-width/2,['Transient','Fixable','Permanent'])
        ax.set_ylabel('Mean per episode');ax.set_title(title)
    axes[0].legend(ncol=3,fontsize=8)
    fig.tight_layout();fig.savefig(out/'fig5_literal_costs.png',dpi=200);plt.close(fig)
    heat=df.pivot_table(index='cell',columns='method',values='no_human_correct',aggfunc='mean')
    heat=heat.reindex(PRIMARY.CELL_ORDER)[methods]
    fig,ax=plt.subplots(figsize=(7,5))
    im=ax.imshow(heat.to_numpy(),vmin=0,vmax=1,cmap='viridis',aspect='auto')
    ax.set_xticks(range(len(methods)),methods);ax.set_yticks(range(len(heat)),heat.index)
    for i in range(len(heat)):
        for j in range(len(methods)):
            val=heat.iloc[i,j];ax.text(j,i,f'{val:.2f}',ha='center',va='center',
                                      color='white' if val<0.6 else 'black',fontsize=8)
    ax.set_title('Correct termination with zero human queries')
    fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(out/'fig6_no_human_correct.png',dpi=200);plt.close(fig)
    (out.parent/'figure_captions.md').write_text(
        '# V2 figure captions\n\n'
        'Figures 1-4 use the unchanged primary analysis script. Figure 1 counts raw correctness, '
        'including human-assisted success and permanent escalation. Figure 2 shows the archived '
        'global-failure-based legacy regret, not literal anchor regret. Figure 3 includes policy '
        'decisions and excludes cutoff; Figure 4 counts logical request tokens, including cache reuse.\n\n'
        'Figure 5 separately shows literal anchor regret and total non-OK execution counts. '
        'The oracle forces the initial attempt. Figure 6 requires zero human queries for correct '
        'termination; it includes permanent abstention and does not imply task completion on permanent cells.\n')
    print('Companion literal-cost and zero-human figures written to',out)
