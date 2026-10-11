"""All prompt text lives here. FREEZE this file. Never edit prompts afterwards
(the cache key includes the prompt, so edits also invalidate cached results)."""
from __future__ import annotations

import json

from .env import CONTAINERS, FORCES, GRASPS, LOCS, OBJECTS, ORIENTS, SKILLS

PROMPT_VERSION = "v1"

SYSTEM = ("You are the recovery module of a household robot. A skill execution has failed and you "
          "must decide how to react. Answer only with JSON that matches the schema.")

# ------------------------------------------------------------------ schemas
MODE_SCHEMA = {
    "type": "object",
    "properties": {
        "mode": {"enum": ["retry", "modify", "replan", "escalate", "abstain"]},
        "why": {"type": "string"},
    },
    "required": ["mode", "why"],
}

REPLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "properties": {
                    "skill": {"enum": SKILLS},
                    "loc": {"enum": LOCS},
                    "obj": {"enum": OBJECTS},
                    "container": {"enum": CONTAINERS},
                    "grasp": {"enum": GRASPS},
                    "orient": {"enum": ORIENTS},
                    "force": {"enum": FORCES},
                },
                "required": ["skill"],
            },
        }
    },
    "required": ["steps"],
}


def modify_schema(param_field: str, allowed: list) -> dict:
    return {
        "type": "object",
        "properties": {"param_field": {"enum": [param_field]}, "new_value": {"enum": list(allowed)}},
        "required": ["param_field", "new_value"],
    }


# ------------------------------------------------------------------ text blocks
MODE_HELP = """Recovery options:
- retry: execute the same skill call again, unchanged.
- modify: change one parameter of the same skill call (grasp, orient or force) and execute it again.
- replan: ask the planner to produce a new plan from the current world state.
- escalate: ask a human operator for help (costly, but a human may be able to fix the problem).
- abstain: stop and report that the task cannot be completed."""

SKILL_MENU = f"""Available skills (use exactly these names):
- goto(loc): loc in {LOCS}
- pick(obj, grasp): obj in {OBJECTS}, grasp in {GRASPS}
- place(obj, loc, orient): orient in {ORIENTS}
- open(container, force): container in {CONTAINERS}, force in {FORCES}
- close(container)"""


def _msgs(user: str) -> list:
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


# ------------------------------------------------------------------ MODE (B2, B4)
def mode_messages(task, call, result, history=None, remaining=None, untried=None, n_fail=None) -> list:
    """history=None -> NO history (method B2). history=list -> full history (method B4)."""
    lines = [
        f"Task: {task['goal_text']}",
        f"Failed skill call: {json.dumps(call.to_flat())}",
        f"Error code: {result.code}",
        f"Error detail: {result.detail}",
    ]
    if history is not None:
        lines.append(f"Failures so far in this episode (including this one): {n_fail}")
        lines.append(f"The episode is cut off and counted as failed after more failures: {remaining} remain.")
        if history:
            lines.append("Earlier failures, each with the recovery decision that was taken:")
            for i, e in enumerate(history, 1):
                lines.append(f"  {i}. call={json.dumps(e['call'])} code={e['code']} "
                             f"detail={e['detail']} decision={e['decision']}")
        else:
            lines.append("This is the first failure in this episode.")
        if untried is not None:
            lines.append(f"Parameter values not yet tried for this call: {untried}")
    lines += ["", MODE_HELP, "", "Choose the best recovery option."]
    return _msgs("\n".join(lines))


# ------------------------------------------------------------------ MODIFY
def modify_messages(task, call, result, param_field, allowed) -> list:
    lines = [
        f"Task: {task['goal_text']}",
        f"Failed skill call: {json.dumps(call.to_flat())}",
        f"Error code: {result.code}",
        f"Error detail: {result.detail}",
        f"Choose a new value for the parameter '{param_field}'. Allowed values: {allowed}",
    ]
    return _msgs("\n".join(lines))


# ------------------------------------------------------------------ REPLAN
def replan_messages(task, call, result, remaining_plan, obs) -> list:
    """Single-line JSON blocks with fixed markers so the stub model can parse them."""
    lines = [
        f"Task: {task['goal_text']}",
        "OBSERVATION: " + json.dumps(obs),
        "FAILED_STEP: " + json.dumps(call.to_flat()),
        "ERROR: " + json.dumps({"code": result.code, "detail": result.detail}),
        "REMAINING_PLAN: " + json.dumps(remaining_plan),
        "",
        SKILL_MENU,
        "",
        "Write the complete list of steps still needed to achieve the task, starting from the robot's "
        "current state. The first step you write is executed next. Use only the skills above.",
    ]
    return _msgs("\n".join(lines))
