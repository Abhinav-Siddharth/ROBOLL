"""Frozen prospective Phase 3b estimates; no model calls or primary-analysis edits."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pfr.metrics import episode_costs, outcome_flags
from pfr.phase3b_runtime import episode_id, run_coordinates

ROOT=Path(__file__).resolve().parents[1]
METRICS=['no_human_correct','raw_correct','autonomous_success','permanent_abstain',
         'human_queries','total_failure_cost']
STATUS='prospective Phase 3b; defined after v2 and before Phase 3b inference'


def load_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def validate(rows, model, coordinates):
    expected={episode_id(model,c):c for c in coordinates}
    actual=[r['episode_id'] for r in rows]
    if len(actual)!=len(set(actual)) or set(actual)!=set(expected):
        raise ValueError('Missing, duplicate or unexpected episode grid')
    for row in rows:
        c=expected[row['episode_id']]
        for key,value in c.items():
            if row.get(key,0 if key=='noise_p' else None)!=value:
                raise ValueError('Coordinate/noise mismatch')
        if row['model']!=model:raise ValueError('Mixed model identities')


def extract(rows):
    records=[]
    for row in rows:
        record={k:row[k] for k in ('task','cell','seed','method','model','human_queries')}
        record.update(outcome_flags(row),episode_costs(row))
        record.update(noise_p=row.get('noise_p',0),
                      permanent_abstain=not row['solvable'] and row['outcome']=='abstain')
        records.append(record)
    return pd.DataFrame(records)


def bootstrap_matrix(matrix,tasks,scheme,*,alpha=.05/3,n_boot=10000,seed=0):
    matrix=np.asarray(matrix,dtype=float)
    if matrix.ndim!=2 or not len(matrix) or not np.isfinite(matrix).all():
        raise ValueError('Require a finite nonempty matched matrix')
    tasks=np.asarray(tasks)
    if len(tasks)!=len(matrix):raise ValueError('Task labels do not match units')
    if scheme=='paired_row':sums=matrix;sizes=np.ones(len(matrix))
    elif scheme=='task_cluster':
        unique=sorted(set(tasks))
        sums=np.array([matrix[tasks==t].sum(axis=0) for t in unique])
        sizes=np.array([np.sum(tasks==t) for t in unique])
    else:raise ValueError('Unknown bootstrap scheme')
    draws=np.random.default_rng(seed).integers(0,len(sums),(n_boot,len(sums)))
    samples=np.empty((n_boot,matrix.shape[1]))
    for start in range(0,n_boot,250):
        d=draws[start:start+250]
        samples[start:start+250]=sums[d].sum(axis=1)/sizes[d].sum(axis=1)[:,None]
    lo,hi=np.quantile(samples,[alpha/2,1-alpha/2],axis=0)
    return matrix.mean(axis=0),lo,hi,samples


def stats(df,scope,version,options,*,noise=False):
    unit=['task','cell','seed']
    columns=['noise_p','method'] if noise else ['method']
    records=[];labels=[];parts=[]
    for metric in METRICS:
        pivot=df.pivot(index=unit,columns=columns,values=metric).sort_index().sort_index(axis=1)
        if pivot.isna().any().any():raise ValueError('Incomplete paired units')
        labels.extend([(metric,c if noise else (0,c)) for c in pivot.columns])
        parts.append(pivot.to_numpy(dtype=float))
    matrix=np.concatenate(parts,axis=1);tasks=pivot.index.get_level_values('task').tolist()
    for scheme in ('paired_row','task_cluster'):
        means,lo,hi,samples=bootstrap_matrix(matrix,tasks,scheme,**options)
        base=dict(version=version,scope=scope,bootstrap=scheme,n_units=len(matrix),
                  n_tasks=len(set(tasks)),confidence=1-options['alpha'],
                  n_boot=options['n_boot'],bootstrap_seed=options['seed'],status=STATUS)
        for i,(metric,(p,method)) in enumerate(labels):
            records.append(dict(**base,metric=metric,noise_p=p,method=method,other='',
                                mean=means[i],ci_lo=lo[i],ci_hi=hi[i]))
            if method=='B5':
                for other in ('B1','B2','B3','B4'):
                    label=(metric,(p,other))
                    if label not in labels:continue
                    j=labels.index(label);delta=samples[:,i]-samples[:,j]
                    low,high=np.quantile(delta,[options['alpha']/2,1-options['alpha']/2])
                    records.append(dict(**base,metric=metric,noise_p=p,method=method,other=other,
                                        mean=means[i]-means[j],ci_lo=low,ci_hi=high))
    return records


def crossing(ps, differences):
    if len(ps)!=len(differences) or len(ps)<2 or sorted(ps)!=list(ps):
        raise ValueError('Require ordered noise grid')
    if not np.isfinite(differences).all():raise ValueError('Nonfinite crossover values')
    ties=[float(p) for p,d in zip(ps,differences) if d==0]
    brackets=[]
    nonzero=[i for i,d in enumerate(differences) if d!=0]
    for i,j in zip(nonzero,nonzero[1:]):
        if differences[i]*differences[j]<0:
            brackets.append(dict(p_low=float(ps[i]),p_high=float(ps[j]),
                                 through_sampled_tie=bool(j>i+1)))
    return dict(ties=ties,brackets=brackets,
                reading=('Crossover bracket(s) observed at tested levels' if brackets else
                         'No crossover was observed at the tested noise levels in [0,0.3]'))


def allowed_output(path):
    path=Path(path).resolve();allowed=ROOT/'results/derived_v3'
    if path.is_relative_to(ROOT) and path!=allowed and not path.is_relative_to(allowed):
        raise ValueError('Repository outputs must be under results/derived_v3')
    path.mkdir(parents=True,exist_ok=True);return path


def analyze(paths,out,*,spec=None):
    spec=spec or json.loads((ROOT/'configs/phase3b_hypotheses.json').read_text())
    out=allowed_output(out)
    raw={name:load_rows(path) for name,path in paths.items()}
    all0=[{**c,'seed':0} for c in run_coordinates(spec,'seed1')]
    validate(raw['seed0'],spec['qwen_model'],all0)
    for name in ('seed1','seed2'):validate(raw[name],spec['qwen_model'],run_coordinates(spec,name))
    validate(raw['second_model'],spec['second_model'],all0)
    for name in ('noise_p01','noise_p02','noise_p03'):
        validate(raw[name],spec['qwen_model'],run_coordinates(spec,name))
    data={name:extract(rows) for name,rows in raw.items()}
    options={k:spec['bootstrap'][k] for k in ('alpha','n_boot','seed')}
    tables=[]
    datasets={k:data[k] for k in ('seed0','seed1','seed2','second_model')}
    datasets['qwen_pooled']=pd.concat([data[k] for k in ('seed0','seed1','seed2')],ignore_index=True)
    for version,df in datasets.items():
        for scope,part in [('overall',df)]+[(c,df[df.cell==c]) for c in spec['cells']]:
            tables.extend(stats(part,scope,version,options))
    pd.DataFrame(tables).to_csv(out/'summaries.csv',index=False)
    summary=pd.DataFrame(tables)
    summary[summary.version.isin(['seed0','seed1','seed2','qwen_pooled'])].to_csv(out/'per_seed_and_pooled.csv',index=False)
    summary[summary.version.isin(['seed0','second_model'])].to_csv(out/'per_model.csv',index=False)
    model_rows=[]
    for method in spec['methods']:
        a=data['seed0'][data['seed0'].method==method].set_index(['task','cell','seed']).sort_index()
        b=data['second_model'][data['second_model'].method==method].set_index(['task','cell','seed']).sort_index()
        if not a.index.equals(b.index):raise ValueError('Unmatched cross-model units')
        matrix=b[METRICS].to_numpy(dtype=float)-a[METRICS].to_numpy(dtype=float)
        for scheme in ('paired_row','task_cluster'):
            estimate,lo,hi,_=bootstrap_matrix(matrix,a.index.get_level_values('task'),scheme,**options)
            for i,metric in enumerate(METRICS):
                model_rows.append(dict(method=method,metric=metric,comparison='second_model minus Qwen seed 0',
                    bootstrap=scheme,mean=estimate[i],ci_lo=lo[i],ci_hi=hi[i],status=STATUS))
    pd.DataFrame(model_rows).to_csv(out/'model_comparisons.csv',index=False)
    base=data['seed0'];base=base[(base.cell!='NONE') & base.method.isin(spec['noise_methods'])]
    noise=pd.concat([base]+[data[k] for k in ('noise_p01','noise_p02','noise_p03')],ignore_index=True)
    noise_stats=pd.DataFrame(stats(noise,'faulted_only','qwen_noise_seed0',options,noise=True))
    noise_stats.to_csv(out/'noise_curves.csv',index=False)
    means=noise.groupby(['noise_p','method']).no_human_correct.mean().unstack()
    ps=means.index.tolist();d=(means.B5-means.B4).tolist();cross=crossing(ps,d)
    (out/'crossovers.json').write_text(json.dumps(dict(noise_ps=ps,differences=d,**cross),indent=2)+'\n')
    decisions=[]
    for seed in (0,1,2):
        for other in ('B2','B3','B4'):
            v=summary[(summary.version==f'seed{seed}') & (summary.scope=='overall') &
                      (summary.metric=='no_human_correct') & (summary.method=='B5') & (summary.other==other)]
            for r in v.to_dict('records'):
                decisions.append(dict(hypothesis='S1',seed=seed,comparison='B5 - '+other,
                    point_rule_holds=bool(r['mean']>0),**{k:r[k] for k in ('bootstrap','mean','ci_lo','ci_hi')}))
    m=summary[(summary.version=='second_model') & (summary.scope=='overall') &
              (summary.metric=='no_human_correct') & (summary.method=='B5') & (summary.other=='B4')]
    for r in m.to_dict('records'):
        decisions.append(dict(hypothesis='M1',seed=0,comparison='B5 - B4',point_rule_holds=bool(r['mean']>0),
            **{k:r[k] for k in ('bootstrap','mean','ci_lo','ci_hi')}))
    for r in noise_stats[(noise_stats.metric=='no_human_correct') & (noise_stats.method=='B5') &
                         (noise_stats.other=='B4')].to_dict('records'):
        decisions.append(dict(hypothesis='N1',seed=0,noise_p=r['noise_p'],comparison='B5 - B4',
            point_rule_holds='',**{k:r[k] for k in ('bootstrap','mean','ci_lo','ci_hi')}))
    pd.DataFrame(decisions).to_csv(out/'hypotheses.csv',index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
    for ax,scheme in zip(axes,('paired_row','task_cluster')):
        for method in spec['noise_methods']:
            part=noise_stats[(noise_stats.bootstrap==scheme)&(noise_stats.metric=='no_human_correct')&
                             (noise_stats.method==method)&(noise_stats.other=='')].sort_values('noise_p')
            ax.errorbar(part.noise_p,part['mean'],yerr=[part['mean']-part.ci_lo,part.ci_hi-part['mean']],
                        marker='o',capsize=3,label=method)
        ax.set(xlabel='Diagnostic corruption probability',title=scheme,ylim=(0,1.03))
        ax.grid(alpha=.25);ax.legend()
    axes[0].set_ylabel('Correct termination with zero human queries')
    fig.tight_layout();fig.savefig(out/'noise_curves.png',dpi=160);plt.close(fig)
    s1=all(r['point_rule_holds'] for r in decisions if r['hypothesis']=='S1')
    m1=all(r['point_rule_holds'] for r in decisions if r['hypothesis']=='M1')
    claims=['| Claim | Supporting file/row | Value with CI | Status | Allowed wording |',
            '|---|---|---|---|---|']
    s1_values='; '.join(f"seed {r['seed']} {r['comparison']} {r['mean']:.6f} [{r['ci_lo']:.6f}, {r['ci_hi']:.6f}] ({r['bootstrap']})" for r in decisions if r['hypothesis']=='S1')
    m1_values='; '.join(f"{r['mean']:.6f} [{r['ci_lo']:.6f}, {r['ci_hi']:.6f}] ({r['bootstrap']})" for r in decisions if r['hypothesis']=='M1')
    claims.append('| S1: B5 above B2/B3/B4 in all three seeds | results/derived_v3/hypotheses.csv, S1 rows | '+s1_values+' | '+('SUPPORTED' if s1 else 'NOT SUPPORTED')+' | '+('B5 had strictly higher observed overall no-human correctness than B2, B3 and B4 in each of the three tested seeds.' if s1 else 'The prespecified ordering did not hold for every comparator in every tested seed.')+' |')
    claims.append('| M1: second-model B5 minus B4 positive | results/derived_v3/hypotheses.csv, M1 rows | '+m1_values+' | '+('SUPPORTED' if m1 else 'NOT SUPPORTED')+' | '+('On the tested second model and seed 0, B5 had higher observed overall no-human correctness than B4; the intervals quantify uncertainty separately.' if m1 else 'A strictly positive observed B5–B4 difference was not found on the tested second model and seed.')+' |')
    n_values='; '.join(f"p={r['noise_p']}: {r['mean']:.6f} [{r['ci_lo']:.6f}, {r['ci_hi']:.6f}] ({r['bootstrap']})" for r in decisions if r['hypothesis']=='N1')
    n_word=cross['reading']+'. Brackets: '+json.dumps(cross['brackets'])+'; sampled ties: '+json.dumps(cross['ties'])+'. No exact between-grid crossover is established.'
    claims.append('| N1: measured noise curves and crossover | results/derived_v3/noise_curves.csv and crossovers.json | '+n_values+' | SUPPORTED as descriptive measurements | '+n_word+' |')
    (out/'CLAIMS_PHASE3B.md').write_text('## Prospective Phase 3b evidence\n\n'+STATUS+'. All intervals are marginal 98.3333% percentile intervals, not simultaneous coverage. S1/M1 decisions use the registered point rule.\n\n'+'\n'.join(claims)+'\n')
    (out/'README.md').write_text('# Phase 3b derived outputs\n\n'+STATUS+'.\n\nNo-human correctness includes correct permanent abstention; autonomous_success is separate. Equal weighting applies to task/cell/seed rows. Seed pooling retains all three fixed seeds within task clusters; it does not estimate a population distribution over seeds. Noise curves jointly resample all methods and p levels. The p=0 reference and second-model controls are reused as specified.\n\nNo optional interpolation or post-hoc subgroup analyses were added. None of these outputs replace H1–H4 or archived v1/v2 artifacts.\n')
    result=dict(S1_point_rule=s1,M1_point_rule=m1,N1=cross,input_rows={k:len(v) for k,v in raw.items()})
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    spec=json.loads((ROOT/'configs/phase3b_hypotheses.json').read_text())
    for name in ('seed0','seed1','seed2','second_model','noise_p01','noise_p02','noise_p03'):
        default=spec['baseline'] if name=='seed0' else spec['full_outputs'][name]
        p.add_argument('--'+name.replace('_','-'),type=Path,default=ROOT/default)
    p.add_argument('--out',type=Path,default=ROOT/'results/derived_v3')
    args=p.parse_args();analyze({k:getattr(args,k) for k in
        ('seed0','seed1','seed2','second_model','noise_p01','noise_p02','noise_p03')},args.out,spec=spec)
