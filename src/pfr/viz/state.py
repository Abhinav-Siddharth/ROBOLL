"""Rebuild the true world state of a logged episode, step by step. NO pybullet needed.

The JSONL row stores every executed call and its result code, but not the world.
We re-run the SAME deterministic Env + FaultyEnv on the logged calls and check that
every result code matches the log. A mismatch means the log and the code have
diverged, so a replay would be lying: we raise instead of drawing it.

Only one thing happens outside the logged calls: when a step's decision was
"escalate" on a solvable fault, the runner calls fault.clear(env) (the human fixes
it). We do the same here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..env import Call, Env
from ..faults import FaultyEnv, build_fault
from ..tasks import TASKS

TASK_BY_ID = {t["id"]: t for t in TASKS}


class ReplayMismatch(RuntimeError):
    pass


@dataclass
class Frame:
    attempt: int
    skill: str
    params: dict
    code: str
    detail: str
    decision: str
    before: dict
    after: dict
    human_fixed: bool = False
    note: str = ""


@dataclass
class Episode:
    row: dict
    task: dict
    initial: dict                      # true world at t=0 (ST faults already applied)
    hidden: str                        # one line: what the agent cannot see
    frames: list = field(default_factory=list)
    final_goal_ok: bool = False


def hidden_truth(fault) -> str:
    k = fault.kind
    if k == "NONE":
        return "no fault"
    if k == "TR":
        if fault.regime == "permanent":
            return f"pick({fault.target}) will time out forever (permanent)"
        return f"pick({fault.target}) times out {fault.n_clear}x, then works"
    if k == "PAR":
        if fault.regime == "permanent":
            return f"no grasp works for {fault.target} (permanent)"
        return f"only grasp='{fault.hidden_fix}' works for {fault.target}"
    if k == "ST":
        if fault.regime == "permanent":
            return f"{fault.target} is gone (permanent)"
        return f"{fault.target} is really at '{fault.true_loc}'"
    if k == "PRE":
        if fault.regime == "permanent":
            return f"path to '{fault.prereq_loc}' is blocked (permanent)"
        return f"must visit '{fault.prereq_loc}' before picking {fault.target}"
    return ""


def reconstruct(row: dict, task: Optional[dict] = None) -> Episode:
    task = task or TASK_BY_ID[row["task"]]
    fault = build_fault(task, row["cell"], row["seed"])
    env = Env(task["init_state"])
    fenv = FaultyEnv(env, fault)
    ep = Episode(row=row, task=task, initial=env.observe(), hidden=hidden_truth(fault))
    for expected_attempt, s in enumerate(row["steps"], 1):
        if s["attempt"] != expected_attempt:
            raise ReplayMismatch(f"{row['episode_id']}: attempt order differs at {expected_attempt}")
        call = Call(s["skill"], dict(s["params"]))
        before = env.observe()
        res = fenv.execute(call)
        if res.code != s["code"]:
            raise ReplayMismatch(
                f"{row['episode_id']} attempt {s['attempt']}: log says {s['code']}, replay says {res.code}")
        if res.detail != s["detail"]:
            raise ReplayMismatch(
                f"{row['episode_id']} attempt {s['attempt']}: detail differs "
                f"({s['detail']!r} vs {res.detail!r})")
        fixed = False
        if s["decision"] == "escalate" and fault.solvable:
            fault.clear(env)
            fixed = True
        ep.frames.append(Frame(s["attempt"], s["skill"], dict(s["params"]), s["code"], s["detail"],
                               s["decision"], before, env.observe(), fixed, s.get("note", "")))
    ep.final_goal_ok = env.goal_satisfied(task["goal"])
    if (row["outcome"] == "success") != ep.final_goal_ok:
        raise ReplayMismatch(f"{row['episode_id']}: outcome disagrees with final goal")
    expected_correct = (row["outcome"] == "success" if fault.solvable
                        else row["outcome"] in ("abstain", "escalate"))
    if row["correct"] != expected_correct:
        raise ReplayMismatch(f"{row['episode_id']}: correctness disagrees with outcome")
    return ep
