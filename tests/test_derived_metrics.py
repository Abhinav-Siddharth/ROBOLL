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


def test_permanent_escalation_is_not_no_human_correct():
    from pfr.metrics import outcome_flags
    row = {'outcome': 'escalate', 'solvable': False, 'correct': True, 'human_queries': 1}
    assert outcome_flags(row) == {'autonomous_success': False, 'human_assisted_success': False,
                                 'raw_correct': True, 'no_human_correct': False,
                                 'autonomous_solvable_or_permanent_correct': True}


def test_human_assisted_success_is_only_raw_correct():
    from pfr.metrics import outcome_flags
    row = {'outcome': 'success', 'solvable': True, 'correct': True, 'human_queries': 1}
    flags = outcome_flags(row)
    assert flags['human_assisted_success']
    assert flags['raw_correct']
    assert not flags['autonomous_success']
    assert not flags['no_human_correct']
    assert not flags['autonomous_solvable_or_permanent_correct']
