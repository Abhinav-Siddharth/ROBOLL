"""Episode loop + CLI.

    python -m pfr.runner --config configs/pilot.yaml --model qwen2.5:7b --out results/raw/pilot.jsonl
    python -m pfr.runner --config configs/pilot.yaml --model stub --out /tmp/stub.jsonl     # dry run

Resumes: episode_ids already in --out are skipped.
"""
from __future__ import annotations

import argparse
from collections import Counter

import yaml
from tqdm import tqdm

from . import prompts
from .core import MODES, Ctx
from .env import PARAM_FIELD, TARGET_ARG, VALUES, Call, Env
from .faults import CELLS, FaultyEnv, build_fault
from .llm import LLMClient
from .logging_utils import load_done_ids, log_episode
from .methods import make_method
from .tasks import TASKS


def _untried(call: Call, param_field, history: list) -> list:
    if not param_field:
        return []
    tried = {call.args.get(param_field)}
    tgt = TARGET_ARG[call.skill]
    for e in history:
        c = e["call"]
        if c.get("skill") == call.skill and c.get(tgt) == call.args.get(tgt):
            tried.add(c.get(param_field))
    return [v for v in VALUES[param_field] if v not in tried]


def run_episode(task: dict, cell: str, seed: int, method, llm: LLMClient, max_failures: int = 8,
                observation_transform=None) -> dict:
    fault = build_fault(task, cell, seed)
    env = Env(task["init_state"])
    fenv = FaultyEnv(env, fault)
    plan = [Call.from_flat(s) for s in task["plan"]]
    i = 0
    history, steps = [], []
    n_fail, attempt_no = 0, 0
    anchor_ok, human_queries = False, 0
    outcome = None
    fail_counts = Counter()

    while i < len(plan):
        call = plan[i]
        res = fenv.execute(call)
        attempt_no += 1
        step = {"attempt": attempt_no, "skill": call.skill, "params": dict(call.args),
                "code": res.code, "detail": res.detail, "decision": ""}
        steps.append(step)
        if res.ok:
            if fault.matches(call):
                anchor_ok = True
            i += 1
            continue

        observed = res
        if observation_transform is not None:
            observed, evidence = observation_transform(res, call, attempt_no)
            if observed.ok or observed.code == "OK":
                raise ValueError("Failure observation transforms cannot turn failures into success")
            if set(evidence) & set(step):
                raise ValueError("Observation audit metadata cannot replace true execution fields")
            step.update(evidence)
        n_fail += 1
        fail_counts[call.key()] += 1
        if n_fail >= max_failures:
            step["decision"] = "cutoff"
            outcome = "cap_exceeded"
            break

        param_field = PARAM_FIELD.get(call.skill)
        untried = _untried(call, param_field, history)
        ctx = Ctx(task=task, call=call, result=observed, history=list(history), n_fail=n_fail,
                  max_failures=max_failures, param_field=param_field, untried=untried, llm=llm)
        decision = method.on_failure(ctx)
        mode = decision.mode if decision.mode in MODES else "abstain"
        step["decision"] = mode
        history.append({"call": call.to_flat(), "code": observed.code, "detail": observed.detail, "decision": mode})

        if mode == "retry":
            continue
        if mode == "modify":
            if param_field and untried:
                out = llm.call(prompts.modify_messages(task, call, observed, param_field, untried),
                               prompts.modify_schema(param_field, untried))
                new_value = out.get("new_value") if out else None
                if new_value not in untried:
                    new_value = untried[0]
                plan[i] = Call(call.skill, {**call.args, param_field: new_value})
            else:
                step["note"] = "modify_noop"  # nothing to modify: acts like a retry
            continue
        if mode == "replan":
            out = llm.call(
                prompts.replan_messages(task, call, observed, [c.to_flat() for c in plan[i:]], fenv.observe()),
                prompts.REPLAN_SCHEMA)
            new_steps = (out or {}).get("steps", [])
            plan = plan[:i] + [Call.from_flat(s) for s in new_steps]
            continue
        if mode == "escalate":
            human_queries += 1
            if fault.solvable:
                fault.clear(env)   # the human fixes it; execution continues
                continue
            outcome = "escalate"   # the human says: impossible
            break
        if mode == "abstain":
            outcome = "abstain"
            break

    if outcome is None:
        outcome = "success" if env.goal_satisfied(task["goal"]) else "incomplete"

    solvable = fault.solvable
    correct = (outcome == "success") if solvable else (outcome in ("abstain", "escalate"))
    attempts = n_fail + (1 if anchor_ok else 0)
    loop = outcome == "cap_exceeded" or any(v >= 3 for v in fail_counts.values())
    return {
        "episode_id": f"{llm.model}|{method.name}|{task['id']}|{cell}|{seed}",
        "task": task["id"], "cell": cell, "group": fault.group, "seed": seed,
        "model": llm.model, "method": method.name,
        "steps": steps, "outcome": outcome, "solvable": solvable, "correct": bool(correct),
        "n_fail": n_fail, "attempts_on_faulted_step": attempts,
        "oracle_attempts": fault.oracle_attempts,
        "regret": max(0, attempts - fault.oracle_attempts),
        "loop": bool(loop), "human_queries": human_queries,
        "decisions": [h["decision"] for h in history],
        "tokens": llm.tokens, "latency_s": llm.latency, "llm_calls": llm.n_calls,
        "parse_failures": llm.parse_failures, "prompt_version": prompts.PROMPT_VERSION,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--methods", default=None, help="comma list, overrides the config, e.g. B0,B3")
    ap.add_argument("--policy", default="configs/policy.yaml")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    tasks = TASKS if cfg.get("tasks", "all") == "all" else TASKS[: int(cfg["tasks"])]
    cells = CELLS if cfg.get("cells", "all") == "all" else cfg["cells"]
    seeds = cfg.get("seeds", [0])
    method_names = args.methods.split(",") if args.methods else cfg["methods"]
    max_failures = cfg.get("max_failures", 8)
    temp = cfg.get("temperature", 0.7)
    methods = {m: make_method(m, args.policy) for m in method_names}

    done = load_done_ids(args.out)
    todo = [(s, t, c, m) for s in seeds for t in tasks for c in cells for m in method_names
            if f"{args.model}|{m}|{t['id']}|{c}|{s}" not in done]
    print(f"{len(done)} episodes already done, {len(todo)} to run -> {args.out}")
    for s, t, c, m in tqdm(todo):
        llm = LLMClient(args.model, base_seed=s, temp=temp)
        row = run_episode(t, c, s, methods[m], llm, max_failures)
        log_episode(row, args.out)


if __name__ == "__main__":
    main()
