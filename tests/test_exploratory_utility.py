import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pfr.exploratory import bootstrap, resampled_means, break_even, safe_output

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('human_utility',ROOT/'analysis/human_utility.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def paired_fixture():
    return pd.DataFrame([dict(task=f't{i}',cell='X',seed=0,method=m,value=value)
                         for i in range(3) for m,value in [('B4',0.0),('B5',1.0)]])


def test_utility_penalizes_every_query_including_incorrect():
    df=pd.DataFrame(dict(raw_correct=[True,False,True],human_queries=[2,1,0]))
    assert module.utility(df,0.5).tolist()==[0.0,-0.5,1.0]


@pytest.mark.parametrize('scheme',['paired_row','task_cluster'])
def test_known_paired_difference(scheme):
    rows=bootstrap(paired_fixture(),'value',scheme,n_boot=100)
    delta=next(r for r in rows if r['other']=='B4')
    assert (delta['mean'],delta['ci_lo'],delta['ci_hi'])==(1.0,1.0,1.0)
    assert delta['n_units']==3


def test_cluster_unequal_sizes_keep_row_estimand():
    result=resampled_means(np.array([[1.0],[0.0],[0.0]]),['a','b','b'],
                           'task_cluster',np.array([[0,0],[1,1],[0,1]]))
    assert np.allclose(result[:,0],[1.0,0.0,1/3])


def test_pairing_not_unpaired_intervals():
    df=paired_fixture();df['value']=[i//2 for i in range(6)]
    result=bootstrap(df,'value','paired_row',n_boot=100)
    delta=next(r for r in result if r['other'])
    assert delta['ci_lo']==delta['ci_hi']==0
    assert result[0]['ci_hi']>result[0]['ci_lo']


def test_missing_pair_rejected():
    with pytest.raises(ValueError,match='complete matched'):
        bootstrap(paired_fixture().iloc[:-1],'value','paired_row',n_boot=10)


@pytest.mark.parametrize('dc,dq,expected,reading',[(0.5,1,0.5,'break-even in [0,1]'),
    (0.5,-1,-0.5,'no break-even in [0,1]'),(0,0,None,'equal for every c in [0,1]'),
    (1,0,None,'no break-even in [0,1]')])
def test_break_even_known_answers(dc,dq,expected,reading):
    assert break_even(dc,dq)==(expected,reading)


def test_output_cannot_overwrite_primary():
    with pytest.raises(ValueError,match='derived_v2'):
        safe_output(ROOT/'results/v2')
