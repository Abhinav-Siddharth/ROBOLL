import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('phase3b_analysis',ROOT/'analysis/phase3b.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


@pytest.mark.parametrize('scheme',['paired_row','task_cluster'])
def test_constant_paired_difference_has_known_interval(scheme):
    matrix=np.array([[0,.25],[.5,.75],[.25,.5],[.75,1.]])
    mean,lo,hi,samples=module.bootstrap_matrix(matrix,['a','a','b','b'],scheme,n_boot=300)
    assert np.allclose(mean,[.375,.625])
    assert np.allclose(samples[:,1]-samples[:,0],.25)


def test_task_clusters_preserve_unequal_row_mean_estimand():
    matrix=np.array([[1.],[0.],[0.]])
    mean,lo,hi,samples=module.bootstrap_matrix(matrix,['a','b','b'],'task_cluster',n_boot=1000)
    assert mean[0]==pytest.approx(1/3)
    assert set(samples[:,0])=={0.,1/3,1.}


def test_all_noise_columns_share_the_same_draws():
    # Different p/method columns have fixed paired differences despite task heterogeneity.
    x=np.array([0.,.2,.6,.1])
    matrix=np.column_stack([x,x+.1,x+.2,x+.3])
    _,_,_,samples=module.bootstrap_matrix(matrix,['a','a','b','b'],'task_cluster',n_boot=200)
    assert np.allclose(samples[:,3]-samples[:,0],.3)


@pytest.mark.parametrize('differences,ties,brackets',[
    ([.3,.2,.1,.05],[],[]),
    ([.3,.1,-.1,-.2],[],[(.1,.2)]),
    ([.2,0,-.1,.1],[.1],[(0,.2),(.2,.3)]),
    ([0,0,0,0],[0,.1,.2,.3],[]),
])
def test_crossover_brackets_ties_and_no_observation(differences,ties,brackets):
    result=module.crossing([0,.1,.2,.3],differences)
    assert result['ties']==ties
    assert [(r['p_low'],r['p_high']) for r in result['brackets']]==brackets


def test_exact_point_tie_does_not_satisfy_above():
    df=pd.DataFrame([dict(task=t,cell='TR-P',seed=0,method=m,**{k:1 for k in module.METRICS})
                     for t in ('a','b') for m in ('B4','B5')])
    rows=module.stats(df,'overall','fixture',dict(alpha=.05/3,n_boot=100,seed=0))
    difference=next(r for r in rows if r['method']=='B5' and r['other']=='B4')
    assert difference['mean']==0 and not difference['mean']>0


def test_mismatched_grid_and_noise_are_rejected():
    c=dict(task='t01',cell='TR-P',method='B5',seed=0,noise_p=.2)
    row=dict(c,model='qwen',episode_id='qwen|B5|t01|TR-P|0|noise=20')
    module.validate([row],'qwen',[c])
    with pytest.raises(ValueError):module.validate([row,row],'qwen',[c])
    with pytest.raises(ValueError):module.validate([{**row,'noise_p':.1}],'qwen',[c])


def test_output_guard_rejects_archived_results():
    with pytest.raises(ValueError):module.allowed_output(ROOT/'results/v2')
