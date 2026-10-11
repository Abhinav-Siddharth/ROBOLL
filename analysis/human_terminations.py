"""Exploratory decomposition of observed correct outcomes by human involvement."""
import argparse

from pfr.exploratory import LABEL, load, write_csv, safe_output


def summarize(df):
    rows=[]
    selections=[('overall','all',df)]
    selections += [('group',str(g),part) for g,part in df.groupby('group')]
    selections += [('cell',str(c),part) for c,part in df.groupby('cell')]
    for kind,scope,part in selections:
        for method,data in part.groupby('method'):
            correct=data.raw_correct.astype(bool)
            human=data.human_queries>0
            permanent=~data.solvable.astype(bool)
            abstain=correct & permanent & ~human & data.outcome.eq('abstain')
            escalate=correct & permanent & human & data.outcome.eq('escalate')
            if int((correct & permanent).sum()) != int(abstain.sum()+escalate.sum()):
                raise ValueError('Unclassified correct permanent termination')
            no_human=correct & ~human
            with_human=correct & human
            assisted=correct & ~permanent & human & data.outcome.eq('success')
            if int(with_human.sum()) != int(escalate.sum()+assisted.sum()):
                raise ValueError('Unclassified correct human outcome')
            n=len(data);ncorrect=int(correct.sum());nperm=int(permanent.sum())
            rows.append(dict(scope_kind=kind,scope=scope,method=method,n=n,n_permanent=nperm,
                raw_correct=ncorrect,no_human_correct=int(no_human.sum()),
                correct_with_human=int(with_human.sum()),human_assisted_success=int(assisted.sum()),
                permanent_no_human_abstain=int(abstain.sum()),permanent_with_human_escalate=int(escalate.sum()),
                raw_correct_rate=ncorrect/n,no_human_correct_rate=float(no_human.mean()),
                correct_with_human_rate=float(with_human.mean()),
                fraction_correct_with_human=int(with_human.sum())/ncorrect if ncorrect else None,
                fraction_correct_permanent_escalation=int(escalate.sum())/ncorrect if ncorrect else None,
                permanent_abstain_rate=int(abstain.sum())/nperm if nperm else None,
                permanent_escalate_rate=int(escalate.sum())/nperm if nperm else None,status=LABEL))
    return rows


def analyze(datasets,out):
    out=safe_output(out);rows=[]
    for version,path in datasets.items():
        rows += [dict(version=version,**r) for r in summarize(load(path))]
    write_csv(rows,out/'human_terminations.csv')
    print(f'{LABEL}: {len(rows)} termination/dependence rows; dependence describes observed human involvement, not a counterfactual effect')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--v1',required=True);p.add_argument('--v2',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();analyze({'v1':a.v1,'v2':a.v2},a.out)
