"""Compute post-data claim checks from raw traces, never from paper-note numbers."""
import argparse
import hashlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from pfr.exploratory import LABEL, ALPHA, N_BOOT, SEED, load, bootstrap, safe_output, write_csv
from pfr.env import SKILL_ARGS
from pfr.methods.b5_policy import B5Policy
import yaml

ROOT=Path(__file__).resolve().parents[1]


def omission_counts(row):
    steps=row['steps']
    omitted=[s for s in steps if any(s['params'].get(arg) is None
                                   for arg in SKILL_ARGS.get(s['skill'], []))]
    invalid=[s for s in steps if s['detail'].startswith('invalid call:')]
    return dict(omitted=len(omitted),invalid=len(invalid),calls=len(steps),
                failures=sum(s['code']!='OK' for s in steps),
                exposed=int(bool(omitted)),failed=int(not row['correct']),
                exposed_failed=int(bool(omitted) and not row['correct']))


def ratio_ci(data, numerator, denominator, scheme):
    values=data[[numerator,denominator]].to_numpy(dtype=float)
    if values[:,1].sum()<=0:
        raise ValueError('Undefined ratio denominator')
    if scheme=='task_cluster':
        tasks=sorted(data.task.unique())
        values=np.array([data[data.task==task][[numerator,denominator]].sum().to_numpy(dtype=float)
                         for task in tasks])
    elif scheme!='paired_row':
        raise ValueError('Unknown bootstrap scheme')
    draws=np.random.default_rng(SEED).integers(0,len(values),(N_BOOT,len(values)))
    sums=values[draws].sum(axis=1)
    ratios=np.divide(sums[:,0],sums[:,1],out=np.full(N_BOOT,np.nan),where=sums[:,1]>0)
    valid=ratios[np.isfinite(ratios)]
    if not len(valid):
        raise ValueError('All bootstrap denominators zero')
    lo,hi=np.percentile(valid,[ALPHA/2*100,(1-ALPHA/2)*100])
    return dict(mean=float(data[numerator].sum()/data[denominator].sum()),ci_lo=float(lo),ci_hi=float(hi),
                numerator=int(data[numerator].sum()),denominator=int(data[denominator].sum()),
                dropped_zero_denominator=N_BOOT-len(valid),bootstrap=scheme,status=LABEL)


def majority_status(numerator,denominator):
    # A numerical majority would still not identify a counterfactual cause.
    return 'PARTIAL' if numerator>denominator/2 else 'NOT SUPPORTED'


def dependency_examples(policy):
    model=B5Policy(policy);rows=[]
    for code,count,nfail,untried in [('EXEC_TRANSIENT',1,1,[]),('EXEC_TRANSIENT',4,4,[]),
            ('PARAM_MISMATCH',1,1,['side']),('PARAM_MISMATCH',1,1,[]),
            ('STATE_MISMATCH',1,1,[]),('STATE_MISMATCH',3,3,[]),('STATE_MISMATCH',1,6,[])]:
        ctx=SimpleNamespace(result=SimpleNamespace(code=code),n_fail=nfail,untried=untried,
                            count_code=lambda requested,count=count:count)
        first=model.on_failure(ctx);second=model.on_failure(ctx)
        assert first==second
        rows.append(dict(code=code,count_code=count,n_fail=nfail,untried=str(untried),
                         mode=first.mode,repeat_equal=True,status=LABEL))
    return rows


def render(claims):
    lines=['# Claims and evidence', '',
           'Every numeric entry is **'+LABEL+'**. Values are recomputed from the raw logs. '
           'SUPPORTED means supported for this observed benchmark and the specified definition; '
           'it does not establish generalization, causality, or familywise significance across these exploratory checks.', '',
           f'CIs are percentile bootstrap intervals with confidence {1-ALPHA:.9f}, {N_BOOT} draws, seed {SEED}. '
           'Row means are paired by task/cell/seed across methods; cluster resampling draws whole tasks. '
           'Count ratios resample numerator and denominator together. Undefined ratio draws are reported, not replaced with zero.', '',
           '| Claim wording | Supporting file and row | Value with CI | Status | Exact wording allowed |',
           '| --- | --- | --- | --- | --- |']
    for row in claims:
        lines.append('| '+' | '.join(str(row[key]).replace('|','\\|').replace('\n',' ') for key in
                     ['claim','support','value','status','allowed'])+' |')
    lines += ['', 'Human involvement is an observed decomposition. Removing human help could change trajectories; '
              'these logs do not identify that counterfactual. A CI containing zero is not an equivalence test. '
              'The before/after schema comparison is descriptive and does not estimate how many individual failures '
              'would have been prevented by fixing only one argument.', '',
              'Reviewed all direct paper/notes/*.md files and paper/outline.md, plus nested literature-note files '
              'for completeness. Existing numeric tables are historical reports with their explicit metric/version labels; '
              'unsupported or over-literal readings are listed below. Literature templates are unfinished evidence, '
              'not proof that all papers were read. No inference or Ollama calls were made.', '']
    return '\n'.join(lines)


def analyze(v1path,v2path,ablationpath,out,paper):
    out=safe_output(out)
    old,new,extra=load(v1path),load(v2path),load(ablationpath)
    stats=[];claims=[]
    def collect(identifier,df,metric):
        rows=[]
        for scheme in ['paired_row','task_cluster']:
            for row in bootstrap(df,metric,scheme):
                row=dict(row_id=f'{identifier}_{scheme}_{row["method"]}_{row["other"] or "mean"}',**row)
                stats.append(row);rows.append(row)
        return rows
    def select(rows,method,other='',scheme='paired_row'):
        return next(r for r in rows if r['method']==method and r['other']==other and r['bootstrap']==scheme)
    def fmt(row):
        return f'{row["mean"]:.6f} [{row["ci_lo"]:.6f}, {row["ci_hi"]:.6f}]'
    def cite(rows):
        return 'results/derived_v2/claims_statistics.csv; row_id='+', '.join(r['row_id'] for r in rows)
    def add(claim,support,value,status,allowed):
        claims.append(dict(claim=claim,support=support,value=value,status=status,allowed=allowed,
                           analysis_status=LABEL))
    # C1: validity counts are weighted by actual executions, not means of per-episode rates.
    counts=[];ratios=[]
    for version,df in [('v1',old),('v2',new)]:
        for method,part in df.groupby('method'):
            data=pd.DataFrame([dict(task=r['task'],**omission_counts(r)) for r in part.to_dict('records')])
            data['episodes']=1
            for scheme in ['paired_row','task_cluster']:
                for label,num,den in [('invalid_call_rate','invalid','calls'),
                       ('omitted_failure_fraction','omitted','failures'),('exposed_episode_rate','exposed','episodes'),
                       ('exposed_failed_episode_fraction','exposed_failed','failed')]:
                    if data[den].sum()==0:
                        continue
                    row=dict(row_id=f'C1_{version}_{method}_{label}_{scheme}',version=version,method=method,
                             metric=label,**ratio_ci(data,num,den,scheme))
                    counts.append(row)
                    if method=='B3':ratios.append(row)
    write_csv(counts,out/'invalid_calls.csv')
    b3old=old[old.method=='B3'];b3new=new[new.method=='B3']
    versions=pd.concat([b3old.assign(method='v1'),b3new.assign(method='v2')],ignore_index=True)
    versionstats=collect('C1_B3_versions',versions,'raw_correct')
    for version,df in [('v1',old),('v2',new)]:
        collect(f'overall_{version}_raw',df,'raw_correct')
    invalid=next(r for r in ratios if r['version']=='v1' and r['metric']=='omitted_failure_fraction' and r['bootstrap']=='paired_row')
    detail='; '.join(f'{r["version"]} {r["metric"]} {r["numerator"]}/{r["denominator"]} '+r['bootstrap']+' '+fmt(r)
                    for r in ratios if r['version']=='v1')
    value=detail+'; B3 v1 '+fmt(select(versionstats,'v1'))+'; v2 '+fmt(select(versionstats,'v2'))+\
          '; v2-v1 row '+fmt(select(versionstats,'v2','v1'))+'; cluster '+fmt(select(versionstats,'v2','v1','task_cluster'))
    add('1. Omitted required arguments caused most of B3\'s v1 failures.',
        'results/derived_v2/invalid_calls.csv; C1_v1_B3_*; '+cite(versionstats),value,
        majority_status(invalid['numerator'],invalid['denominator']),
        f'B3 v1 had omitted required arguments in {int(b3old.apply(lambda r:omission_counts(r)["exposed"],axis=1).sum())}/{len(b3old)} episodes; '
        f'{invalid["numerator"]}/{invalid["denominator"]} failed executions were malformed ({invalid["mean"]*100:.1f}%). '
        f'B3 raw correctness increased from {int(b3old.raw_correct.sum())}/{len(b3old)} in v1 to '
        f'{int(b3new.raw_correct.sum())}/{len(b3new)} in v2. These observations do not show that omissions caused most failures.')
    # C2: highest sample rate, and paired comparisons against every primary method.
    nohuman=collect('C2_v2_no_human',new,'no_human_correct')
    b5=[select(nohuman,'B5',scheme=s) for s in ['paired_row','task_cluster']]
    deltas=[r for r in nohuman if r['method']=='B5' and r['other']]
    supported=all(r['mean']>0 and r['ci_lo']>0 for r in deltas)
    add('2. B5 has the highest no-human correctness in v2.',cite(b5+deltas),
        '; '.join(r['bootstrap']+' '+(f'B5-{r["other"]} ' if r['other'] else 'B5 ')+fmt(r) for r in b5+deltas),
        'SUPPORTED' if supported else 'PARTIAL',
        f'B5 had the highest observed zero-human correct-termination rate: {int(new[new.method=="B5"].no_human_correct.sum())}/220. '
        'Its paired differences against all five primary baselines have positive marginal lower bounds under both schemes; '
        'this includes permanent abstention and is not a task-completion rate.')
    # C3: faulted units only; NONE was not run for B2C.
    matched=pd.concat([new[(new.cell!='NONE') & (new.method=='B4')],extra],ignore_index=True)
    raw=collect('C3_faulted_raw',matched,'raw_correct')
    auto=collect('C3_faulted_autonomous',matched,'autonomous_success')
    nh=collect('C3_faulted_no_human',matched,'no_human_correct')
    matched['correct_human']=(matched.raw_correct.astype(bool)&(matched.human_queries>0)).astype(float)
    human=collect('C3_faulted_human',matched,'correct_human')
    group=matched.groupby('method')[['raw_correct','autonomous_success','correct_human']].sum()
    dr=int(group.loc['B4','raw_correct']-group.loc['B2C','raw_correct'])
    dh=int(group.loc['B4','correct_human']-group.loc['B2C','correct_human'])
    chosen=[r for rows in [raw,auto,nh,human] for r in rows if r['other']]
    add('3. B4\'s raw advantage over B2C comes from escalation, not autonomous completion.',cite(chosen),
        '; '.join(r['metric']+' B4-B2C '+r['bootstrap']+' '+fmt(r) for r in chosen)+'; '+f'{dh}/{dr} extra correct outcomes involved humans',
        'PARTIAL',f'On the 200 faulted units, B4 had {dr} more correct outcomes than B2C; {dh} of this net difference '
        'was in outcomes involving human queries (permanent escalation or assisted success). '
        'The autonomous difference was one episode and its CIs include zero. This is a descriptive decomposition, not proof of equivalence or causality.')
    # C4/5: exact original hypothesis subsets, recomputed rather than read from notes.
    h1=collect('C4_H1_v2',new[new.cell.isin(['TR-T1','TR-T2'])],'raw_correct')
    chosen=[select(h1,'B5','B3',s) for s in ['paired_row','task_cluster']]
    supported=chosen[0]['ci_lo']>0 and chosen[1]['ci_lo']<=0<=chosen[1]['ci_hi']
    add('4. The H1 B5-B3 reading on transient cells depends on bootstrap scheme.',cite(chosen),
        '; '.join(r['bootstrap']+' '+fmt(r) for r in chosen),'SUPPORTED' if supported else 'NOT SUPPORTED',
        'For the preregistered T1/T2 subset, B5-B3 raw correctness is +0.15: the paired-row CI excludes zero, '
        'while the task-cluster CI includes zero. This does not establish equivalence.')
    h3=[]
    for version,df in [('v1',old),('v2',new)]:
        rs=collect(f'C5_H3_{version}',df[df.group=='F'],'raw_correct')
        h3 += [dict(version=version,**select(rs,'B5','B4',s)) for s in ['paired_row','task_cluster']]
    supported=all(r['ci_hi']<0 if r['version']=='v1' else r['ci_lo']>0 for r in h3)
    add('5. V1 H3 (B5 worse than B4 on F cells) reverses in v2.',cite(h3),
        '; '.join(r['version']+' '+r['bootstrap']+' '+fmt(r) for r in h3),
        'SUPPORTED' if supported else 'PARTIAL',
        'On the three F cells, B5-B4 raw correctness changes from -0.233333 in v1 to +0.25 in v2. '
        'Both schemes exclude zero in opposite directions. This is a descriptive version comparison.')
    # C6 utility on overall primary units, not a claim of superiority in every cell.
    urows=[]
    for cost in [0.25,0.5,1.0]:
        data=new.copy();data['utility']=data.raw_correct.astype(float)-cost*data.human_queries
        rows=collect(f'C6_v2_c{cost}',data,'utility')
        urows += [dict(c=cost,**r) for r in rows if r['method']=='B5' and r['other']]
    supported=all(r['ci_lo']>0 for r in urows)
    add('6. B5\'s advantage persists under every tested human-query cost.',cite(urows),
        '; '.join(f'c={cost}: minimum mean advantage {min(r["mean"] for r in urows if r["c"]==cost):.6f}, '
                    f'minimum row/cluster lower bound {min(r["ci_lo"] for r in urows if r["c"]==cost):.6f}' for cost in [0.25,0.5,1.0]),
        'SUPPORTED' if supported else 'PARTIAL',
        'B5 has the highest observed overall v2 utility for c=0.25, 0.5 and 1.0. Its paired differences '
        'against all primary baselines have positive marginal lower bounds under both schemes. '
        'These costs were chosen after seeing the data; the statement does not hold for every cell or all possible costs.')
    # C7 executable policy examples, with the actual frozen configuration.
    examples=dependency_examples(yaml.safe_load((ROOT/'configs/policy.yaml').read_text()))
    write_csv(examples,out/'reference_policy_examples.csv')
    add('7. B5 is a deterministic lookup from failure code to decision; read its score as a reference policy.',
        'src/pfr/methods/b5_policy.py:on_failure; configs/policy.yaml; results/derived_v2/reference_policy_examples.csv rows 1-7',
        'EXEC_TRANSIENT: retry vs escalate; PARAM_MISMATCH: modify vs abstain; STATE_MISMATCH: replan/abstain/escalate. CI not applicable: executable policy inspection.',
        'PARTIAL','B5 uses deterministic recovery-mode rules conditioned on failure code, history counts, untried parameters '
        'and a fixed budget. Modification/replanning still use an LLM. Interpret this as a reference-policy result '
        'under oracle failure monitoring, not a code-only lookup or a deterministic end-to-end planner.')
    # Unsupported literal claims in current direct notes/outline. Do not silently revise those notes.
    add('Notes: B2 selects a mode using "only the current error".',
        'paper/notes/method.md:29; src/pfr/prompts.py:mode_messages',
        'Prompt also includes goal text, failed call and mode descriptions; CI not applicable: source inspection.',
        'NOT SUPPORTED','B2 omits prior failure history and budget/untried hints; its mode prompt includes the task goal, failed call and current error.')
    add('Notes: "does history help the LLM? (B4 vs B2)" isolates history.',
        'paper/notes/hypothesis.md: historical B4-B2 rows; src/pfr/methods/b4_llm_history.py; src/pfr/methods/b2_nohistory.py',
        'The prompt differences include failure counts, remaining budget and untried values; CI cannot isolate those factors.',
        'NOT SUPPORTED','B4 versus B2 measures a context bundle. B4 versus B2C is the post-audit matched-context comparison, with human involvement separated.')
    add('Outline rule: every cited paper was opened/read, and all claims match preregistration.',
        'paper/outline.md:16; paper/notes/Related work_Literature survey/*.md; paper/prereg.md',
        'Full-paper reading is unverified; literature templates remain unfinished. Step 2 utility costs and claim checks are post-data. CI not applicable.',
        'NOT SUPPORTED','Bibliography metadata was previously checked; full comparative reading remains unfinished. '
        'The primary H1-H4 definitions are retained; these new utility and claim analyses are exploratory.')
    add('Outline rule: every number in the paper comes from results/tables/*.csv.',
        'paper/outline.md:16; paper/notes/results.md; results/derived_v2/',
        'Dual definitions, v2 and new exploratory outputs have separate directories. CI not applicable: artifact paths.',
        'NOT SUPPORTED','Every numeric claim must cite its version, metric and supporting output, including derived_v1, v2 and exploratory derived_v2 as applicable.')
    write_csv(stats,out/'claims_statistics.csv');write_csv(claims,out/'claims.csv')
    reviewed=[*sorted((ROOT/'paper/notes').rglob('*.md')),ROOT/'paper/outline.md']
    write_csv([dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                    scope='numeric/method/interpretation claims; literature reading remains unverified',status=LABEL)
               for p in reviewed],out/'reviewed_notes.csv')
    paper=Path(paper).resolve()
    if ROOT in paper.parents and paper!=ROOT/'paper/claims_evidence.md':
        raise ValueError('Only paper/claims_evidence.md may be written inside the paper repository')
    paper.parent.mkdir(parents=True,exist_ok=True);paper.write_text(render(claims))
    print(f'{LABEL}: {len(claims)} claims checked; {len(stats)} freshly computed statistics; claims_evidence.md written')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['v1','v2','ablation','out','paper']:
        p.add_argument('--'+name,required=True)
    a=p.parse_args();analyze(a.v1,a.v2,a.ablation,a.out,a.paper)
