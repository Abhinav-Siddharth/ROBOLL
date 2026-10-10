import pytest

from pfr.faults import CELLS
from pfr.llm import LLMClient
from pfr.methods import make_method
from pfr.runner import run_episode
from pfr.tasks import TASKS
from pfr.viz.state import ReplayMismatch, reconstruct


def row_for(task, cell, method):
    return run_episode(task, cell, 0, make_method(method), LLMClient("stub", 0))


@pytest.mark.parametrize("cell", CELLS)
@pytest.mark.parametrize("method", ["B0", "B3", "B4"])
def test_replay_reproduces_every_logged_code_and_outcome(cell, method):
    # 11 cells x 3 methods x 20 tasks = 660 real episodes replayed against their own logs
    for t in TASKS:
        row = row_for(t, cell, method)
        ep = reconstruct(row)
        assert len(ep.frames) == len(row["steps"])
        if row["outcome"] == "success":
            assert ep.final_goal_ok


def test_mismatch_is_detected():
    row = row_for(TASKS[0], "TR-T1", "B0")
    row["steps"][1]["code"] = "OK"          # the faulted pick actually failed
    with pytest.raises(ReplayMismatch):
        reconstruct(row)


def test_st_fault_object_starts_elsewhere():
    ep = reconstruct(row_for(TASKS[0], "ST-P", "B0"))
    assert ep.initial["objects"]["apple"] == "gone"
    assert "gone" in ep.hidden


def test_no_degenerate_st_f_tasks_at_t0():
    """Verify that with the fix, 0 of 20 tasks have ST-F hidden location equal to goal location."""
    from pfr.env import Env
    from pfr.faults import FaultyEnv, build_fault
    bad = []
    for t in TASKS:
        f = build_fault(t, "ST-F", 0)
        e = Env(t["init_state"]); FaultyEnv(e, f)
        if e.goal_satisfied(t["goal"]):
            bad.append(t["id"])
    assert bad == []

