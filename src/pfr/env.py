"""Tabletop/kitchen simulator: world model, 5 skills, structured results.

Conventions
-----------
* A skill call is a `Call(skill, args)`. In prompts and task files it appears
  in "flat" form: {"skill": "pick", "obj": "apple", "grasp": "top"}.
* Every execution returns a `Result` with one of five codes.
* Precondition rules (this is what the tests check):
    - pick:  gripper must be empty                       -> PRECOND_UNMET
             object must be at the robot's location      -> STATE_MISMATCH
             if object is in the drawer, drawer is open   -> PRECOND_UNMET
    - place: must hold the object                         -> PRECOND_UNMET
             robot must be at `loc`                       -> PRECOND_UNMET
             placing into the drawer needs it open        -> PRECOND_UNMET
    - open / close: robot at the drawer, right drawer state -> PRECOND_UNMET
    - malformed call (unknown skill / bad argument value)  -> PRECOND_UNMET
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Literal, Optional

from pydantic import BaseModel

LOCS = ["table", "counter", "shelf", "drawer", "sink"]
OBJECTS = ["apple", "cup", "plate", "knob_key", "bowl"]
CONTAINERS = ["drawer"]
GRASPS = ["top", "side", "pinch"]
ORIENTS = ["upright", "flat"]
FORCES = ["low", "med", "high"]
SKILLS = ["goto", "pick", "place", "open", "close"]

# Which argument names each skill takes, and the allowed values of each argument.
SKILL_ARGS = {
    "goto": ["loc"],
    "pick": ["obj", "grasp"],
    "place": ["obj", "loc", "orient"],
    "open": ["container", "force"],
    "close": ["container"],
}
VALUES = {
    "loc": LOCS,
    "obj": OBJECTS,
    "container": CONTAINERS,
    "grasp": GRASPS,
    "orient": ORIENTS,
    "force": FORCES,
}
# The one parameter of each skill that MODIFY is allowed to change.
PARAM_FIELD = {"pick": "grasp", "place": "orient", "open": "force"}
# The argument that names the thing a skill acts on (used to match "the same step").
TARGET_ARG = {"pick": "obj", "place": "obj", "open": "container", "close": "container"}
# Used when an LLM replan leaves an argument out.
DEFAULTS = {"grasp": "top", "orient": "upright", "force": "med", "container": "drawer"}

Code = Literal["OK", "EXEC_TRANSIENT", "PARAM_MISMATCH", "STATE_MISMATCH", "PRECOND_UNMET"]


class Result(BaseModel):
    ok: bool
    code: Code
    detail: str
    param_field: Optional[str] = None


def _ok() -> Result:
    return Result(ok=True, code="OK", detail="ok")


def _fail(code: str, detail: str, param_field: Optional[str] = None) -> Result:
    return Result(ok=False, code=code, detail=detail, param_field=param_field)


@dataclass
class Call:
    skill: str
    args: dict = field(default_factory=dict)

    def to_flat(self) -> dict:
        return {"skill": self.skill, **self.args}

    @staticmethod
    def from_flat(d: dict) -> "Call":
        skill = d.get("skill")
        names = SKILL_ARGS.get(skill, [])
        return Call(skill, {k: d.get(k, DEFAULTS.get(k)) for k in names})

    def key(self) -> tuple:
        return (self.skill, tuple(sorted(self.args.items())))

    def __str__(self) -> str:
        inner = ", ".join(f"{k}={v}" for k, v in self.args.items())
        return f"{self.skill}({inner})"


class Env:
    def __init__(self, init_state: dict):
        s = copy.deepcopy(init_state)
        self.robot_loc: str = s["robot_loc"]
        self.holding: Optional[str] = s.get("holding")
        self.drawer_open: bool = s.get("drawer_open", False)
        self.obj_loc: dict = dict(s["objects"])

    # ------------------------------------------------------------------ state
    def observe(self) -> dict:
        """The TRUE visible state."""
        return {
            "robot_loc": self.robot_loc,
            "holding": self.holding,
            "drawer_open": self.drawer_open,
            "objects": dict(self.obj_loc),
        }

    def goal_satisfied(self, goal: dict) -> bool:
        if self.holding is not None:
            return False
        for obj, loc in goal.get("at", {}).items():
            if self.obj_loc.get(obj) != loc:
                return False
        want_open = goal.get("drawer_open")
        if want_open is not None and self.drawer_open != want_open:
            return False
        return True

    # -------------------------------------------------------------- execution
    def execute(self, call: Call) -> Result:
        spec = SKILL_ARGS.get(call.skill)
        if spec is None:
            return _fail("PRECOND_UNMET", f"invalid call: unknown skill {call.skill!r}")
        for k in spec:
            v = call.args.get(k)
            if v not in VALUES[k]:
                return _fail("PRECOND_UNMET", f"invalid call: {k}={v!r}")
        return getattr(self, f"_{call.skill}")(**{k: call.args[k] for k in spec})

    def _goto(self, loc: str) -> Result:
        self.robot_loc = loc
        return _ok()

    def _pick(self, obj: str, grasp: str) -> Result:
        if self.holding is not None:
            return _fail("PRECOND_UNMET", "precondition: gripper_empty")
        if self.obj_loc.get(obj) != self.robot_loc:
            return _fail("STATE_MISMATCH", "object not found at current location")
        if self.obj_loc[obj] == "drawer" and not self.drawer_open:
            return _fail("PRECOND_UNMET", "precondition: drawer_open")
        self.holding = obj
        self.obj_loc[obj] = "gripper"
        return _ok()

    def _place(self, obj: str, loc: str, orient: str) -> Result:
        if self.holding != obj:
            return _fail("PRECOND_UNMET", "precondition: holding_object")
        if self.robot_loc != loc:
            return _fail("PRECOND_UNMET", f"precondition: robot_at_{loc}")
        if loc == "drawer" and not self.drawer_open:
            return _fail("PRECOND_UNMET", "precondition: drawer_open")
        self.obj_loc[obj] = loc
        self.holding = None
        return _ok()

    def _open(self, container: str, force: str) -> Result:
        if self.robot_loc != "drawer":
            return _fail("PRECOND_UNMET", "precondition: robot_at_drawer")
        if self.drawer_open:
            return _fail("PRECOND_UNMET", "precondition: drawer_closed")
        self.drawer_open = True
        return _ok()

    def _close(self, container: str) -> Result:
        if self.robot_loc != "drawer":
            return _fail("PRECOND_UNMET", "precondition: robot_at_drawer")
        if not self.drawer_open:
            return _fail("PRECOND_UNMET", "precondition: drawer_open")
        self.drawer_open = False
        return _ok()
