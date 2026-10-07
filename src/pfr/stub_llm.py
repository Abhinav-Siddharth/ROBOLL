"""A fake model for dry runs and tests (--model stub). NOT used for any reported result.

It lets you test the whole pipeline (runner, logging, analysis) in seconds without Ollama.
 * MODE   -> pseudo-random choice (deterministic in the seed and prompt)
 * MODIFY -> first allowed value
 * REPLAN -> a small heuristic planner (re-targets goto before a pick, inserts a prerequisite visit)
"""
from __future__ import annotations

import hashlib
import json
import re


def _block(text: str, marker: str):
    for line in text.splitlines():
        if line.startswith(marker + ": "):
            return json.loads(line[len(marker) + 2:])
    return None


def respond(messages: list, schema: dict, seed: int) -> dict:
    user = messages[-1]["content"]
    props = schema["properties"]
    if "mode" in props:
        h = int(hashlib.sha256(f"{seed}|{user}".encode()).hexdigest(), 16)
        modes = props["mode"]["enum"]
        content = {"mode": modes[h % len(modes)], "why": "stub"}
    elif "new_value" in props:
        content = {"param_field": props["param_field"]["enum"][0], "new_value": props["new_value"]["enum"][0]}
    else:
        content = {"steps": _replan(user)}
    return {"content": content, "tokens": 0, "latency_s": 0.0}


def _replan(user: str) -> list:
    obs = _block(user, "OBSERVATION")
    plan = _block(user, "REMAINING_PLAN") or []
    err = _block(user, "ERROR") or {}
    locs = ("table", "counter", "shelf", "drawer", "sink")
    new = []
    for k, s in enumerate(plan):
        s = dict(s)
        if s.get("skill") == "goto" and k + 1 < len(plan) and plan[k + 1].get("skill") == "pick":
            true = obs["objects"].get(plan[k + 1]["obj"])
            if true in locs:
                s["loc"] = true
        if k == 0 and s.get("skill") == "pick":
            true = obs["objects"].get(s["obj"])
            if true in locs and true != obs["robot_loc"]:
                new.append({"skill": "goto", "loc": true})
        new.append(s)
    m = re.match(r"precondition: prior visit to (\w+) required", err.get("detail", ""))
    if m:
        new = [{"skill": "goto", "loc": m.group(1)}, {"skill": "goto", "loc": obs["robot_loc"]}] + new
    return new
