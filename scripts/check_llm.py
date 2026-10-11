"""Do schema outputs always parse (20 calls per schema)? Does the cache work?

    python scripts/check_llm.py qwen2.5:7b      # run it TWICE: the second run must be (almost) instant
"""
import sys
import time

from pfr import prompts
from pfr.env import Call, Result
from pfr.llm import LLMClient

model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:7b"
task = {"goal_text": "put the apple on the table"}
call = Call("pick", {"obj": "apple", "grasp": "top"})
res = Result(ok=False, code="PARAM_MISMATCH", detail="grasp invalid for apple", param_field="grasp")

t0 = time.time()
bad = 0
parse_failures = 0
for seed in range(20):
    c = LLMClient(model, base_seed=seed)
    out = c.call(prompts.mode_messages(task, call, res, history=[], remaining=7, untried=["side", "pinch"], n_fail=1),
                 prompts.MODE_SCHEMA)
    bad += out is None or out.get("mode") not in ["retry", "modify", "replan", "escalate", "abstain"]
    out = c.call(prompts.modify_messages(task, call, res, "grasp", ["side", "pinch"]),
                 prompts.modify_schema("grasp", ["side", "pinch"]))
    bad += out is None or out.get("new_value") not in ["side", "pinch"]
    out = c.call(prompts.replan_messages(task, call, res, [call.to_flat()], {"robot_loc": "counter", "holding": None,
                 "drawer_open": False, "objects": {"apple": "counter"}}), prompts.REPLAN_SCHEMA)
    bad += out is None or "steps" not in out
    parse_failures += c.parse_failures
print(f"60 calls, {bad} bad outputs, {parse_failures} exhausted parse/schema failures, {time.time() - t0:.1f}s total")
if bad or parse_failures:
    sys.exit(1)
