"""estimate main-run hours from the pilot.

    python scripts/estimate_hours.py results/raw/pilot.jsonl
Uses the recorded LLM latency per episode (cached calls keep their original latency), scaled to
220 episodes per method (20 tasks x 11 cells x 1 seed).
"""
import collections
import json
import sys

rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
n_main = int(sys.argv[2]) if len(sys.argv) > 2 else 220
by = collections.defaultdict(list)
for r in rows:
    by[r["method"]].append(r["latency_s"])
total = 0.0
for m, v in sorted(by.items()):
    mean = sum(v) / len(v)
    total += mean * n_main
    print(f"{m}: {mean:.1f} s/episode (from {len(v)} pilot episodes)")
print(f"estimated main run: {total / 3600:.1f} hours")
