import json
import subprocess
import sys

import pytest

from pfr.faults import CELLS
from pfr.llm import LLMClient
from pfr.methods import make_method
from pfr.runner import run_episode
from pfr.tasks import TASKS

T1 = TASKS[0]


def run(cell, method, task=T1, seed=0, model="stub"):
    return run_episode(task, cell, seed, make_method(method), LLMClient(model, seed))


def test_row_has_all_fields():
    row = run("NONE", "B0")
    for k in ["episode_id", "task", "cell", "seed", "model", "method", "steps", "outcome", "correct",
              "attempts_on_faulted_step", "loop", "human_queries", "tokens", "latency_s", "regret"]:
        assert k in row
    assert row["steps"][0]["skill"] == "goto"
    assert set(row["steps"][0]) >= {"attempt", "skill", "params", "code", "decision"}


def test_clean_episode_succeeds_for_every_task():
    for t in TASKS:
        row = run("NONE", "B0", task=t)
        assert row["outcome"] == "success" and row["correct"] and row["attempts_on_faulted_step"] == 1
        assert row["regret"] == 0 and not row["loop"]


@pytest.mark.parametrize("cell,n", [("TR-T1", 1), ("TR-T2", 2), ("TR-T3", 3)])
def test_b0_solves_transient_cells(cell, n):
    row = run(cell, "B0")
    assert row["correct"] and row["attempts_on_faulted_step"] == n + 1 and row["regret"] == 0


@pytest.mark.parametrize("cell", ["TR-P", "PAR-P", "ST-P", "PRE-P"])
def test_b0_loops_on_permanent_cells(cell):
    row = run(cell, "B0")
    assert row["outcome"] == "cap_exceeded" and row["loop"] and not row["correct"]
    assert row["regret"] >= 4


def test_b0_cannot_fix_fixable_cells():
    for cell in ["PAR-F", "ST-F", "PRE-F"]:
        row = run(cell, "B0")
        assert not row["correct"] and row["outcome"] == "cap_exceeded"


def test_b3_with_stub_planner_fixes_state_and_precondition_faults():
    for cell in ["ST-F", "PRE-F"]:
        row = run(cell, "B3")
        assert row["correct"], (cell, row["outcome"], row["steps"][-3:])
        assert row["attempts_on_faulted_step"] == 2 and row["regret"] == 0


def test_b3_loops_on_permanent_state_fault():
    row = run("ST-P", "B3")
    assert row["loop"] and not row["correct"]


def test_modify_replan_escalate_paths_run_with_stub_b4():
    """B4 with the random stub model exercises every branch of the runner without crashing."""
    seen = set()
    for t in TASKS[:6]:
        for cell in CELLS:
            row = run(cell, "B4", task=t)
            seen.update(row["decisions"])
            assert row["outcome"] in {"success", "abstain", "escalate", "cap_exceeded", "incomplete"}
    assert {"retry", "modify", "replan", "abstain"} <= seen


def test_cli_resume_skips_done_episodes(tmp_path):
    out = tmp_path / "o.jsonl"
    cfg = tmp_path / "c.yaml"
    cfg.write_text("tasks: 1\ncells: [NONE, TR-T1]\nseeds: [0]\nmethods: [B0, B3]\nmax_failures: 8\n")
    cmd = [sys.executable, "-m", "pfr.runner", "--config", str(cfg), "--model", "stub", "--out", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    n1 = len(out.read_text().splitlines())
    assert n1 == 4
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "0 to run" in r.stdout
    assert len(out.read_text().splitlines()) == n1
    assert all(json.loads(l)["model"] == "stub" for l in out.read_text().splitlines())
