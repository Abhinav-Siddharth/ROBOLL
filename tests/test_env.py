import copy

import pytest

from pfr.env import Call, Env
from pfr.tasks import TASKS


def run_plan(task):
    env = Env(task["init_state"])
    results = [env.execute(Call.from_flat(s)) for s in task["plan"]]
    return env, results


def test_twenty_tasks_with_4_to_8_steps():
    assert len(TASKS) == 20
    assert len({t["id"] for t in TASKS}) == 20
    for t in TASKS:
        assert 4 <= len(t["plan"]) <= 8, t["id"]


@pytest.mark.parametrize("task", TASKS, ids=[t["id"] for t in TASKS])
def test_clean_plan_succeeds(task):
    env, results = run_plan(task)
    assert all(r.ok for r in results), [r.detail for r in results if not r.ok]
    assert env.goal_satisfied(task["goal"])


@pytest.mark.parametrize("task", TASKS, ids=[t["id"] for t in TASKS])
def test_goal_not_already_satisfied(task):
    assert not Env(task["init_state"]).goal_satisfied(task["goal"])


def fresh():
    return Env(copy.deepcopy(TASKS[0]["init_state"]))  # apple@counter, robot@table, drawer closed


def test_observe_returns_state():
    obs = fresh().observe()
    assert obs["robot_loc"] == "table"
    assert obs["holding"] is None
    assert obs["drawer_open"] is False
    assert obs["objects"]["apple"] == "counter"


def test_precondition_violations_return_precond_unmet():
    # pick while gripper is full
    e = fresh()
    e.execute(Call("goto", {"loc": "counter"}))
    assert e.execute(Call("pick", {"obj": "apple", "grasp": "top"})).ok
    r = e.execute(Call("pick", {"obj": "apple", "grasp": "top"}))
    assert r.code == "PRECOND_UNMET"
    # pick from a closed drawer
    e = fresh()
    e.execute(Call("goto", {"loc": "drawer"}))
    assert e.execute(Call("pick", {"obj": "knob_key", "grasp": "pinch"})).code == "PRECOND_UNMET"
    # place without holding
    e = fresh()
    assert e.execute(Call("place", {"obj": "apple", "loc": "table", "orient": "flat"})).code == "PRECOND_UNMET"
    # place at a location other than where the robot is
    e = fresh()
    e.execute(Call("goto", {"loc": "counter"}))
    e.execute(Call("pick", {"obj": "apple", "grasp": "top"}))
    assert e.execute(Call("place", {"obj": "apple", "loc": "shelf", "orient": "flat"})).code == "PRECOND_UNMET"
    # place into a closed drawer
    e = fresh()
    e.execute(Call("goto", {"loc": "counter"}))
    e.execute(Call("pick", {"obj": "apple", "grasp": "top"}))
    e.execute(Call("goto", {"loc": "drawer"}))
    assert e.execute(Call("place", {"obj": "apple", "loc": "drawer", "orient": "flat"})).code == "PRECOND_UNMET"
    # open / close away from the drawer
    e = fresh()
    assert e.execute(Call("open", {"container": "drawer", "force": "low"})).code == "PRECOND_UNMET"
    assert e.execute(Call("close", {"container": "drawer"})).code == "PRECOND_UNMET"
    # open twice / close a closed drawer
    e = fresh()
    e.execute(Call("goto", {"loc": "drawer"}))
    assert e.execute(Call("close", {"container": "drawer"})).code == "PRECOND_UNMET"
    assert e.execute(Call("open", {"container": "drawer", "force": "low"})).ok
    assert e.execute(Call("open", {"container": "drawer", "force": "low"})).code == "PRECOND_UNMET"


def test_object_not_here_is_state_mismatch():
    e = fresh()  # robot at table, apple at counter
    r = e.execute(Call("pick", {"obj": "apple", "grasp": "top"}))
    assert r.code == "STATE_MISMATCH"


def test_malformed_calls_are_precond_unmet():
    e = fresh()
    assert e.execute(Call("fly", {})).code == "PRECOND_UNMET"
    assert e.execute(Call("goto", {"loc": "moon"})).code == "PRECOND_UNMET"
    assert e.execute(Call("pick", {"obj": "apple", "grasp": None})).code == "PRECOND_UNMET"


def test_failed_calls_do_not_change_state():
    e = fresh()
    before = e.observe()
    e.execute(Call("pick", {"obj": "apple", "grasp": "top"}))  # STATE_MISMATCH
    assert e.observe() == before
