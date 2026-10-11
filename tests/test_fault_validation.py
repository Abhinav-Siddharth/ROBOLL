import pytest
from pfr.env import Call, Env
from pfr.faults import build_fault, FaultyEnv
from pfr.tasks import TASKS


@pytest.mark.parametrize('cell', ['TR-T1', 'PAR-F', 'PRE-F'])
def test_malformed_anchor_is_validated_before_fault_interception(cell):
    task = TASKS[0]
    fault = build_fault(task, cell, 0)
    env = Env(task['init_state'])
    fenv = FaultyEnv(env, fault)
    before = env.observe()
    result = fenv.execute(Call('pick', {'obj': 'apple', 'grasp': None}))
    assert result.code == 'PRECOND_UNMET'
    assert result.detail == 'invalid call: grasp=None'
    assert fault.attempts == 0
    assert not fault.prereq_done
    assert env.observe() == before


def test_invalid_pick_does_not_clear_transient_fault():
    fault = build_fault(TASKS[0], 'TR-T1', 0)
    env = Env(TASKS[0]['init_state'])
    fenv = FaultyEnv(env, fault)
    fenv.execute(Call('goto', {'loc': 'counter'}))
    fenv.execute(Call('pick', {'obj': 'apple', 'grasp': None}))
    assert fenv.execute(Call('pick', {'obj': 'apple', 'grasp': 'top'})).code == 'EXEC_TRANSIENT'
    assert fenv.execute(Call('pick', {'obj': 'apple', 'grasp': 'top'})).code == 'OK'
