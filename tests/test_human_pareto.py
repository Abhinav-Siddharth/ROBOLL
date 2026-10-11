import importlib.util
from pathlib import Path

import pandas as pd

spec=importlib.util.spec_from_file_location('human_pareto',Path(__file__).resolve().parents[1]/'analysis/human_pareto.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_known_pareto_tradeoff_and_dominance():
    df=pd.DataFrame(dict(method=['A','B','C','D'],total_failure_cost=[1,2,3,1],
                         no_human_correct=[0.5,1.0,0.4,0.5]))
    result=module.pareto(df).set_index('method')
    assert result.pareto.to_dict()=={'A':True,'B':True,'C':False,'D':True}


def test_aggregate_before_pareto_comparison():
    df=pd.DataFrame(dict(method=['A','A','B'],total_failure_cost=[0,4,3],
                         no_human_correct=[0,1,0.4]))
    result=module.pareto(df).set_index('method')
    assert result.loc['A','total_failure_cost']==2
    assert result.loc['A','no_human_correct']==0.5
    assert not result.loc['B','pareto']
