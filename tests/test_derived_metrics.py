import pytest


def test_costs_separate_anchor_calls_from_other_failures():
    from pfr.metrics import episode_costs
    row = {'task': 't01', 'cell': 'TR-T1', 'seed': 0, 'oracle_attempts': 2,
           'regret': 7, 'steps': [
               {'skill': 'pick', 'params': {'obj': 'apple'}, 'code': 'EXEC_TRANSIENT'},
               {'skill': 'pick', 'params': {'obj': 'apple'}, 'code': 'OK'},
               *[{'skill': 'place', 'params': {'obj': 'apple'}, 'code': 'PRECOND_UNMET'} for _ in range(7)]]}
    costs = episode_costs(row)
    assert costs == {'anchor_attempts': 2, 'total_failures': 8,
                     'total_failure_cost': 8, 'anchor_regret': 0, 'legacy_regret': 7}


def test_costs_count_repeated_successful_anchor_calls():
    from pfr.metrics import episode_costs
    row = {'task': 't01', 'cell': 'NONE', 'seed': 0, 'oracle_attempts': 1,
           'regret': 0, 'steps': [{'skill': 'pick', 'params': {'obj': 'apple'}, 'code': 'OK'}] * 2}
    assert episode_costs(row)['anchor_attempts'] == 2
    assert episode_costs(row)['anchor_regret'] == 1
