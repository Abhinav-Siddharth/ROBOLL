"""Needs pybullet; skipped (not failed) if it is not installed. Headless, no rendering."""
import numpy as np
import pytest

pytest.importorskip("pybullet")

from pfr.faults import CELLS  # noqa: E402
from pfr.llm import LLMClient  # noqa: E402
from pfr.methods import make_method  # noqa: E402
from pfr.runner import run_episode  # noqa: E402
from pfr.tasks import TASKS  # noqa: E402
from pfr.viz.scene import Scene  # noqa: E402
from pfr.viz.state import reconstruct  # noqa: E402


@pytest.fixture(scope="module")
def sc():
    s = Scene(gui=False, render=False, speed=8.0)
    yield s
    s.close()


def play(sc, task, cell, method):
    row = run_episode(task, cell, 0, make_method(method), LLMClient("stub", 0))
    ep = reconstruct(row)
    sc.load_state(ep.initial)
    for fr in ep.frames:
        sc.run_step(fr)
    return ep


def test_every_clean_task_ends_with_objects_at_their_goal_and_ik_is_accurate(sc):
    for t in TASKS:
        sc.max_ik_err = 0.0
        ep = play(sc, t, "NONE", "B0")
        assert ep.final_goal_ok
        for obj, loc in t["goal"]["at"].items():
            assert np.linalg.norm(sc.obj_pos(obj) - sc.slot_pos(loc, obj)) < 0.01, (t["id"], obj)
        assert sc.held is None
        assert sc.max_ik_err < 0.03, (t["id"], sc.max_ik_err)


@pytest.mark.parametrize("cell", CELLS)
def test_every_fault_cell_replays_without_error_and_scene_matches_world(sc, cell):
    for t in TASKS[:6]:
        ep = play(sc, t, cell, "B3")
        last = ep.frames[-1].after
        for obj, loc in last["objects"].items():
            if loc in ("gone", "gripper"):
                continue
            assert np.linalg.norm(sc.obj_pos(obj) - sc.slot_pos(loc, obj)) < 0.01, (t["id"], cell, obj)
        assert (sc.held is None) == (last["holding"] is None)


def test_drawer_slides_and_returns(sc):
    t4 = next(t for t in TASKS if t["id"] == "t04")
    play(sc, t4, "NONE", "B0")
    assert sc.slide == 0.0                      # the plan closes the drawer again
    t6 = next(t for t in TASKS if t["id"] == "t06")
    play(sc, t6, "NONE", "B0")
    assert sc.slide == 0.0


def test_malformed_calls_are_refused_not_crashed(sc):
    from pfr.viz.state import Frame
    st = {"robot_loc": "table", "holding": None, "drawer_open": False,
          "objects": {"apple": "counter", "cup": "shelf", "plate": "sink", "knob_key": "drawer", "bowl": "table"}}
    sc.load_state(st)
    for skill, params in [("goto", {"loc": "kitchen"}), ("goto", {"loc": None}), ("pick", {"obj": "banana", "grasp": "top"}),
                          ("place", {"obj": None, "loc": "mars", "orient": "flat"}), ("dance", {}), ("open", {})]:
        sc.run_step(Frame(1, skill, params, "PRECOND_UNMET", "invalid call", "", st, st))
