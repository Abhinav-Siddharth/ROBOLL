import importlib.util
from pathlib import Path

import pandas as pd
import pytest

spec=importlib.util.spec_from_file_location('claims_evidence',Path(__file__).resolve().parents[1]/'analysis/claims_evidence.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_missing_arguments_are_counted_separately_from_other_failures():
    row={'correct':False,'steps':[
        dict(skill='place',params={'obj':'cup','loc':None,'orient':'upright'},code='PRECOND_UNMET',detail='invalid call: loc=None'),
        dict(skill='pick',params={'obj':'cup','grasp':'side'},code='STATE_MISMATCH',detail='not found'),
        dict(skill='goto',params={'loc':'table'},code='OK',detail='ok')]}
    assert module.omission_counts(row)==dict(omitted=1,invalid=1,calls=3,failures=2,exposed=1,failed=1,exposed_failed=1)


@pytest.mark.parametrize('scheme',['paired_row','task_cluster'])
def test_weighted_ratio_is_not_mean_of_episode_ratios(scheme):
    df=pd.DataFrame(dict(task=['a','b'],yes=[1,3],total=[2,6]))
    result=module.ratio_ci(df,'yes','total',scheme)
    assert result['mean']==result['ci_lo']==result['ci_hi']==0.5
    assert result['numerator']==4 and result['denominator']==8


def test_undefined_ratio_rejected():
    with pytest.raises(ValueError,match='Undefined ratio'):
        module.ratio_ci(pd.DataFrame(dict(task=['a'],yes=[0],total=[0])),'yes','total','paired_row')


def test_majority_wording_rejected_for_less_than_half():
    assert module.majority_status(38,100)=='NOT SUPPORTED'
    assert module.majority_status(50,100)=='NOT SUPPORTED'
    assert module.majority_status(51,100)=='PARTIAL'


def test_same_code_different_context_changes_reference_policy_mode():
    rows=module.dependency_examples(dict(transient_retry_cap=3,state_replan_cap=2,precond_replan_cap=2,
                                        total_failure_budget=6,exhausted_action='escalate'))
    assert [r['mode'] for r in rows]==['retry','escalate','modify','abstain','replan','abstain','escalate']
    assert all(r['repeat_equal'] for r in rows)


def test_markdown_claims_include_status_and_escape_pipes():
    text=module.render([dict(claim='A|B',support='fixture row 1',value='1 [1,1]',status='SUPPORTED',allowed='Use fixture wording')])
    assert 'A\\|B' in text
    assert 'exploratory, defined after seeing the data' in text
    assert '| SUPPORTED | Use fixture wording |' in text
