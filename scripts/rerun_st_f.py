#!/usr/bin/env python
"""Rerun affected ST-F episodes after fixing the generator flaw and update results/raw/qwen.jsonl."""
import json
import time
from pathlib import Path
from tqdm import tqdm

from pfr.tasks import TASKS
from pfr.methods import make_method
from pfr.llm import LLMClient
from pfr.runner import run_episode

CHANGED_TASKS = ['t01', 't02', 't04', 't07', 't09', 't10', 't13', 't16', 't17', 't18', 't19', 't20']
METHODS = ["B0", "B1", "B2", "B3", "B4", "B5"]

def main():
    tasks_dict = {t["id"]: t for t in TASKS}
    methods = {m: make_method(m, "configs/policy.yaml") for m in METHODS}
    
    out_path = Path("results/raw/qwen.jsonl")
    temp_results = Path("results/raw/st_f_rerun_partial.jsonl")
    
    # Load any already completed from partial rerun if resuming
    done = {}
    if temp_results.exists():
        for line in open(temp_results):
            if line.strip():
                row = json.loads(line)
                done[row["episode_id"]] = row
        print(f"Loaded {len(done)} already finished episodes from {temp_results}")
    
    todo = []
    for tid in CHANGED_TASKS:
        for m in METHODS:
            ep_id = f"qwen2.5:7b|{m}|{tid}|ST-F|0"
            if ep_id not in done:
                todo.append((tid, m, ep_id))
                
    print(f"Total episodes to run: {len(todo)} (out of {len(CHANGED_TASKS) * len(METHODS)})")
    
    with open(temp_results, "a") as f_out:
        for tid, m, ep_id in tqdm(todo, desc="Rerunning ST-F"):
            task = tasks_dict[tid]
            llm = LLMClient("qwen2.5:7b", base_seed=0, temp=0.7)
            t0 = time.time()
            row = run_episode(task, "ST-F", 0, methods[m], llm, max_failures=8)
            dt = time.time() - t0
            done[ep_id] = row
            f_out.write(json.dumps(row) + "\n")
            f_out.flush()
            
    print(f"Completed all {len(done)} rerun episodes. Merging into {out_path}...")
    
    # Read existing qwen.jsonl and replace the updated episodes
    old_rows = [json.loads(l) for l in open(out_path) if l.strip()]
    merged = []
    replaced_count = 0
    for r in old_rows:
        ep_id = r["episode_id"]
        if ep_id in done:
            merged.append(done[ep_id])
            replaced_count += 1
        else:
            merged.append(r)
            
    assert len(merged) == len(old_rows) == 1320, f"Expected 1320 rows, got {len(merged)}"
    assert replaced_count == len(done) == 72, f"Expected 72 replaced, got {replaced_count}"
    
    # Write atomically
    tmp_path = out_path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        for r in merged:
            f.write(json.dumps(r) + "\n")
    tmp_path.replace(out_path)
    
    print(f"Successfully updated {out_path} with {replaced_count} fresh ST-F episodes!")
    if temp_results.exists():
        temp_results.unlink()

if __name__ == "__main__":
    main()
