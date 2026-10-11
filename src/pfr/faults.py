"""Fault injector: 11 cells, hidden regimes, oracle quantities.

Every fault is anchored on ONE skill call: the FIRST `pick` of the task
(skill="pick", target=<object>). Any later pick of that same object (for
example inside a replan) is treated as the same faulted step.

Permanent and fixable faults emit the SAME code and the SAME detail text.
The agent can only tell them apart from the failure history.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from .env import GRASPS, LOCS, Call, Env, Result

CELLS = ["NONE", "TR-T1", "TR-T2", "TR-T3", "TR-P", "PAR-F", "PAR-P", "ST-F", "ST-P", "PRE-F", "PRE-P"]

# kind: which failure mechanism. regime: none / clears / fixable / permanent.
# group: T (transient, clears by itself), F (fixable), P (permanent), none.
# oracle = attempts on the faulted step an all-knowing agent needs
#   (NONE 1, T-n n+1, F 2, P 1).
CELL_INFO = {
    "NONE":  dict(kind="NONE", regime="none",      n_clear=0, solvable=True,  oracle=1, group="none"),
    "TR-T1": dict(kind="TR",   regime="clears",    n_clear=1, solvable=True,  oracle=2, group="T"),
    "TR-T2": dict(kind="TR",   regime="clears",    n_clear=2, solvable=True,  oracle=3, group="T"),
    "TR-T3": dict(kind="TR",   regime="clears",    n_clear=3, solvable=True,  oracle=4, group="T"),
    "TR-P":  dict(kind="TR",   regime="permanent", n_clear=0, solvable=False, oracle=1, group="P"),
    "PAR-F": dict(kind="PAR",  regime="fixable",   n_clear=0, solvable=True,  oracle=2, group="F"),
    "PAR-P": dict(kind="PAR",  regime="permanent", n_clear=0, solvable=False, oracle=1, group="P"),
    "ST-F":  dict(kind="ST",   regime="fixable",   n_clear=0, solvable=True,  oracle=2, group="F"),
    "ST-P":  dict(kind="ST",   regime="permanent", n_clear=0, solvable=False, oracle=1, group="P"),
    "PRE-F": dict(kind="PRE",  regime="fixable",   n_clear=0, solvable=True,  oracle=2, group="F"),
    "PRE-P": dict(kind="PRE",  regime="permanent", n_clear=0, solvable=False, oracle=1, group="P"),
}
CAUSE_CODE = {
    "NONE": None,
    "TR": "EXEC_TRANSIENT",
    "PAR": "PARAM_MISMATCH",
    "ST": "STATE_MISMATCH",
    "PRE": "PRECOND_UNMET",
}


@dataclass
class Fault:
    cell: str
    kind: str
    regime: str
    group: str
    cause_code: Optional[str]
    step_idx: int            # index of the anchor step in the ORIGINAL plan
    skill: str               # anchor skill ("pick")
    target: str              # anchor object
    n_clear: int
    solvable: bool
    oracle_attempts: int
    param_field: Optional[str] = None   # PAR
    hidden_fix: Optional[str] = None    # PAR: right grasp. ST: true location. PRE: prerequisite location.
    true_loc: Optional[str] = None      # ST: where the object really is ("gone" if permanent)
    prereq_loc: Optional[str] = None    # PRE: location that must be visited first
    cleared: bool = False
    attempts: int = 0                   # anchor executions seen while the fault was active (TR)
    prereq_done: bool = False           # PRE

    def matches(self, call: Call) -> bool:
        return call.skill == self.skill and call.args.get("obj") == self.target

    def apply_reset(self, env: Env) -> None:
        """Called once at episode start. ST faults change the world."""
        if self.kind == "ST":
            env.obj_loc[self.target] = self.true_loc

    def clear(self, env: Env) -> None:
        """A human fixed the problem (only called for solvable faults)."""
        self.cleared = True
        if self.kind == "ST":
            env.obj_loc[self.target] = env.robot_loc


def build_fault(task: dict, cell: str, seed: int = 0) -> Fault:
    info = CELL_INFO[cell]
    plan = task["plan"]
    idx = next(i for i, s in enumerate(plan) if s["skill"] == "pick")
    anchor = plan[idx]
    # Simulate the clean plan up to the anchor to learn where the robot is then.
    env = Env(task["init_state"])
    visited = []
    for s in plan[:idx]:
        c = Call.from_flat(s)
        env.execute(c)
        if c.skill == "goto":
            visited.append(c.args["loc"])
    robot_at = env.robot_loc
    orig_loc = env.obj_loc[anchor["obj"]]

    f = Fault(
        cell=cell, kind=info["kind"], regime=info["regime"], group=info["group"],
        cause_code=CAUSE_CODE[info["kind"]], step_idx=idx, skill="pick", target=anchor["obj"],
        n_clear=info["n_clear"], solvable=info["solvable"], oracle_attempts=info["oracle"],
    )
    if f.kind == "PAR":
        f.param_field = "grasp"
        g0 = anchor["grasp"]
        f.hidden_fix = GRASPS[(GRASPS.index(g0) + 1) % len(GRASPS)]
    elif f.kind == "ST":
        if f.regime == "fixable":
            rng = random.Random(f"{task['id']}|{cell}|{seed}")
            target_goal = task["goal"]["at"].get(anchor["obj"])
            candidates = sorted(l for l in LOCS if l not in (orig_loc, "drawer", target_goal))
            f.true_loc = rng.choice(candidates)
        else:
            f.true_loc = "gone"
        f.hidden_fix = f.true_loc
    elif f.kind == "PRE":
        candidates = [l for l in ["sink", "shelf", "counter", "table"]
                      if l != robot_at and l not in visited]
        f.prereq_loc = candidates[0]
        f.hidden_fix = f.prereq_loc
    return f


class FaultyEnv:
    """Wraps Env. All fault logic lives here; Env stays clean."""

    def __init__(self, env: Env, fault: Fault):
        self.env = env
        self.fault = fault
        fault.apply_reset(env)

    def observe(self) -> dict:
        return self.env.observe()

    def execute(self, call: Call) -> Result:
        invalid = self.env.validate_call(call)
        if invalid is not None:
            return invalid
        f = self.fault
        if f.kind != "NONE" and not f.cleared:
            r = self._intercept(call)
            if r is not None:
                return r
        return self.env.execute(call)

    def _intercept(self, call: Call) -> Optional[Result]:
        f = self.fault
        # PRE: the prerequisite call itself (goto prereq_loc)
        if f.kind == "PRE" and call.skill == "goto" and call.args.get("loc") == f.prereq_loc:
            if f.regime == "permanent":
                return Result(ok=False, code="PRECOND_UNMET",
                              detail=f"precondition: path to {f.prereq_loc} blocked")
            r = self.env.execute(call)
            if r.ok:
                f.prereq_done = True
            return r
        if not f.matches(call):
            return None
        # ---- the anchor call
        if f.kind == "TR":
            f.attempts += 1
            if f.regime == "permanent" or f.attempts <= f.n_clear:
                return Result(ok=False, code="EXEC_TRANSIENT", detail="execution error: motion timeout")
            return None
        if f.kind == "PAR":
            val = call.args.get(f.param_field)
            if f.regime == "permanent" or val != f.hidden_fix:
                return Result(ok=False, code="PARAM_MISMATCH",
                              detail=f"{f.param_field} invalid for {f.target}", param_field=f.param_field)
            return None
        if f.kind == "PRE":
            if not f.prereq_done:
                return Result(ok=False, code="PRECOND_UNMET",
                              detail=f"precondition: prior visit to {f.prereq_loc} required")
            return None
        return None  # ST: the world itself differs, Env returns STATE_MISMATCH
