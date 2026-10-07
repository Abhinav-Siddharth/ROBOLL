import pytest

from pfr.env import GRASPS, Call, Env
from pfr.faults import CELL_INFO, CELLS, FaultyEnv, build_fault
from pfr.logging_utils import load_done_ids, log_episode
from pfr.tasks import TASKS

IDS = [t["id"] for t in TASKS]


def setup(task, cell):
    fault = build_fault(task, cell, seed=0)
    env = Env(task["init_state"])
    fenv = FaultyEnv(env, fault)
    # run the clean plan up to (not including) the anchor
    for s in task["plan"][: fault.step_idx]:
        assert fenv.execute(Call.from_flat(s)).ok
    anchor = Call.from_flat(task["plan"][fault.step_idx])
    return fault, env, fenv, anchor


def test_eleven_cells():
    assert len(CELLS) == 11 and set(CELLS) == set(CELL_INFO)


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_none(task):
    fault, env, fenv, anchor = setup(task, "NONE")
    assert fenv.execute(anchor).ok


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_transient_clears_at_attempt_n_plus_1(task, n):
    fault, env, fenv, anchor = setup(task, f"TR-T{n}")
    for _ in range(n):
        r = fenv.execute(anchor)
        assert (not r.ok) and r.code == "EXEC_TRANSIENT"
    assert fenv.execute(anchor).ok
    assert fault.oracle_attempts == n + 1


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_transient_permanent_never_clears(task):
    fault, env, fenv, anchor = setup(task, "TR-P")
    for _ in range(12):
        assert fenv.execute(anchor).code == "EXEC_TRANSIENT"


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_param_fixable_clears_with_hidden_value(task):
    fault, env, fenv, anchor = setup(task, "PAR-F")
    r = fenv.execute(anchor)
    assert r.code == "PARAM_MISMATCH" and r.param_field == "grasp"
    assert fault.hidden_fix in GRASPS and fault.hidden_fix != anchor.args["grasp"]
    # every wrong value fails, the hidden one works
    for g in GRASPS:
        c = Call("pick", {**anchor.args, "grasp": g})
        assert fenv.execute(c).ok == (g == fault.hidden_fix)


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_param_permanent_no_value_works(task):
    fault, env, fenv, anchor = setup(task, "PAR-P")
    for g in GRASPS:
        r = fenv.execute(Call("pick", {**anchor.args, "grasp": g}))
        assert r.code == "PARAM_MISMATCH"


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_state_fixable_needs_goto_true_location(task):
    fault, env, fenv, anchor = setup(task, "ST-F")
    r = fenv.execute(anchor)
    assert r.code == "STATE_MISMATCH"
    true_loc = fenv.observe()["objects"][fault.target]
    assert true_loc == fault.true_loc and true_loc != "gone"
    assert fenv.execute(Call("goto", {"loc": true_loc})).ok
    assert fenv.execute(anchor).ok


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_state_permanent_object_is_gone(task):
    fault, env, fenv, anchor = setup(task, "ST-P")
    assert fenv.observe()["objects"][fault.target] == "gone"
    assert fenv.execute(anchor).code == "STATE_MISMATCH"
    for loc in ["table", "counter", "shelf", "drawer", "sink"]:
        fenv.execute(Call("goto", {"loc": loc}))
        assert fenv.execute(anchor).code == "STATE_MISMATCH"


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_state_fixable_and_permanent_have_same_code_and_text(task):
    _, _, f1, a1 = setup(task, "ST-F")
    _, _, f2, a2 = setup(task, "ST-P")
    r1, r2 = f1.execute(a1), f2.execute(a2)
    assert (r1.code, r1.detail) == (r2.code, r2.detail)


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_precondition_fixable_after_prerequisite(task):
    fault, env, fenv, anchor = setup(task, "PRE-F")
    r = fenv.execute(anchor)
    assert r.code == "PRECOND_UNMET"
    robot_at = env.robot_loc
    assert fenv.execute(Call("goto", {"loc": fault.prereq_loc})).ok
    assert fenv.execute(Call("goto", {"loc": robot_at})).ok
    assert fenv.execute(anchor).ok


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_precondition_permanent_prerequisite_always_fails(task):
    fault, env, fenv, anchor = setup(task, "PRE-P")
    assert fenv.execute(anchor).code == "PRECOND_UNMET"
    for _ in range(3):
        assert fenv.execute(Call("goto", {"loc": fault.prereq_loc})).code == "PRECOND_UNMET"
        assert fenv.execute(anchor).code == "PRECOND_UNMET"


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_precondition_f_and_p_same_first_failure(task):
    _, _, f1, a1 = setup(task, "PRE-F")
    _, _, f2, a2 = setup(task, "PRE-P")
    r1, r2 = f1.execute(a1), f2.execute(a2)
    assert (r1.code, r1.detail) == (r2.code, r2.detail)


def test_oracle_attempts_table():
    expect = {"NONE": 1, "TR-T1": 2, "TR-T2": 3, "TR-T3": 4, "TR-P": 1,
              "PAR-F": 2, "PAR-P": 1, "ST-F": 2, "ST-P": 1, "PRE-F": 2, "PRE-P": 1}
    for c, v in expect.items():
        assert CELL_INFO[c]["oracle"] == v
    assert [c for c in CELLS if not CELL_INFO[c]["solvable"]] == ["TR-P", "PAR-P", "ST-P", "PRE-P"]


def test_log_episode_roundtrip(tmp_path):
    p = str(tmp_path / "x.jsonl")
    log_episode({"episode_id": "a", "v": 1}, p)
    log_episode({"episode_id": "b", "v": 2}, p)
    assert load_done_ids(p) == {"a", "b"}
