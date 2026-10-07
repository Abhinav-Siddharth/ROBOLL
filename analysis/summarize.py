"""Quick tables + the go/no-go test.

    python analysis/summarize.py results/raw/pilot.jsonl
"""
import glob
import json
import sys

import pandas as pd

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)


def load(paths):
    rows = []
    for p in paths:
        with open(p) as f:
            rows += [json.loads(l) for l in f if l.strip()]
    return pd.DataFrame(rows)


def main(paths):
    df = load(paths)
    print(f"{len(df)} episodes | methods {sorted(df.method.unique())} | cells {df.cell.nunique()}\n")

    agg = dict(n=("correct", "size"), correct=("correct", "mean"), attempts=("attempts_on_faulted_step", "mean"),
               regret=("regret", "mean"), loop=("loop", "mean"), human=("human_queries", "mean"),
               tokens=("tokens", "mean"), latency=("latency_s", "mean"))
    print("== per cell x method ==")
    print(df.groupby(["cell", "method"]).agg(**agg).round(2).to_string())
    print("\n== overall per method ==")
    print(df.groupby("method").agg(**agg).round(2).to_string())
    print("\n== correctness by cell (rows) and method (columns) ==")
    print(df.pivot_table(index="cell", columns="method", values="correct", aggfunc="mean").round(2).to_string())
    print("\n== decision counts per method ==")
    dec = df.explode("decisions").dropna(subset=["decisions"]).reset_index(drop=True)
    if len(dec):
        print(pd.crosstab(dec.method, dec.decisions).to_string())

    print("\n== GO / NO-GO ==")
    ok_all = True
    P = df[df.group == "P"]
    for m in ["B0", "B3"]:
        if m in set(df.method):
            v = P[P.method == m].regret.mean()
            ok = v >= 4
            ok_all &= ok
            print(f"[{'PASS' if ok else 'FAIL'}] {m} wastes >= 4 attempts on P cells (mean regret {v:.2f})")
    if {"B0", "B4"} <= set(df.method):
        pc = df.pivot_table(index="cell", columns="method", values="correct", aggfunc="mean")
        n_diff = int(((pc["B4"] - pc["B0"]).abs() > 0.05).sum())
        ok = n_diff >= 2
        ok_all &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] B4 differs from B0 in {n_diff} cells (need >= 2)")
    if "B3" in set(df.method):
        v = df[(df.method == "B3") & df.solvable].correct.mean()
        ok = v < 0.9
        ok_all &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] B3 not at ceiling on solvable cells (correct {v:.2f}, need < 0.90)")
    if "parse_failures" in df:
        pf = int(df.parse_failures.sum())
        print(f"[INFO] schema parse failures across the run: {pf}")
    print("\nRESULT:", "GO" if ok_all else "NO-GO (fix the setup before building anything else)")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(glob.glob("results/raw/*.jsonl")))
