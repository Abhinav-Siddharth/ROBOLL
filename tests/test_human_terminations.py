import importlib.util
from pathlib import Path

import pandas as pd
import pytest

spec=importlib.util.spec_from_file_location('human_terminations',Path(__file__).resolve().parents[1]/'analysis/human_terminations.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def fixture():
    return pd.DataFrame([dict(method='B',group=g,cell=g,raw_correct=correct,solvable=solvable,
                              human_queries=queries,outcome=outcome)
        for g,correct,solvable,queries,outcome in [('P',True,False,0,'abstain'),
          ('P',True,False,1,'escalate'),('F',True,True,1,'success'),('F',False,True,1,'cutoff')]])


def test_known_termination_decomposition():
    result=module.summarize(fixture())[0]
    assert result['raw_correct']==3
    assert result['permanent_no_human_abstain']==1
    assert result['permanent_with_human_escalate']==1
    assert result['human_assisted_success']==1
    assert result['fraction_correct_with_human']==2/3
    assert result['fraction_correct_permanent_escalation']==1/3
    assert result['permanent_abstain_rate']==0.5


def test_zero_correct_denominator_is_undefined():
    result=module.summarize(fixture().iloc[[-1]])[0]
    assert result['fraction_correct_with_human'] is None
    assert result['permanent_abstain_rate'] is None


def test_inconsistent_permanent_outcome_rejected():
    df=fixture();df.loc[0,'outcome']='success'
    with pytest.raises(ValueError,match='permanent termination'):
        module.summarize(df)
