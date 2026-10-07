"""Day 6: figures + tables from results/raw/*.jsonl.

    python analysis/make_figures.py results/raw/qwen.jsonl
Outputs: figures/fig1..fig4 (png), results/tables/*.csv
"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CELL_ORDER = ["NONE", "TR-T1", "TR-T2", "TR-T3", "TR-P", "PAR-F", "PAR-P", "ST-F", "ST-P", "PRE-F", "PRE-P"]
METHOD_ORDER = ["B0", "B1", "B2", "B3", "B4", "B5"]
MODES = ["retry", "modify", "replan", "escalate", "abstain"]
N_BOOT = 10000
ALPHA = 0.05 / 3   # 3 pre-registered primary comparisons, Bonferroni-adjusted


def load(paths):
    rows = []
    for p in paths:
        with open(p) as f:
            rows += [json.loads(l) for l in f if l.strip()]
    df = pd.DataFrame(rows)
    df["correct"] = df["correct"].astype(float)
    df["loop"] = df["loop"].astype(float)
    return df


def paired_boot(df, a, b, metric, mask, alpha=ALPHA, seed=0):
    """Mean of (metric[a] - metric[b]) over matched (task, cell, seed) units, with a bootstrap CI."""
    sub = df[mask]
    piv = sub.pivot_table(index=["task", "cell", "seed"], columns="method", values=metric, aggfunc="mean")
    if a not in piv or b not in piv:
        return np.nan, np.nan, np.nan, 0
    d = (piv[a] - piv[b]).dropna().to_numpy()
    if len(d) == 0:
        return np.nan, np.nan, np.nan, 0
    rng = np.random.default_rng(seed)
    means = d[rng.integers(0, len(d), (N_BOOT, len(d)))].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(d.mean()), float(lo), float(hi), len(d)


def reading(lo, hi, better_if_negative):
    if np.isnan(lo):
        return "n/a"
    if lo > 0 or hi < 0:
        good = (hi < 0) if better_if_negative else (lo > 0)
        return "CI excludes 0 (A better)" if good else "CI excludes 0 (A worse)"
    return "CI includes 0 (no clear difference)"


def main(paths):
    df = load(paths)
    os.makedirs("figures", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)
    methods = [m for m in METHOD_ORDER if m in set(df.method)]
    cells = [c for c in CELL_ORDER if c in set(df.cell)]

    # ---------- tables
    overall = df.groupby("method").agg(
        n=("correct", "size"), correct=("correct", "mean"), regret=("regret", "mean"), loop=("loop", "mean"),
        human_queries=("human_queries", "mean"), tokens=("tokens", "mean"), latency_s=("latency_s", "mean")
    ).reindex(methods).round(3)
    overall.to_csv("results/tables/overall.csv")
    by_cell = df.pivot_table(index="cell", columns="method", values="correct", aggfunc="mean").reindex(cells)[methods].round(2)
    by_cell.to_csv("results/tables/correct_by_cell.csv")
    by_group = df.pivot_table(index="group", columns="method", values=["correct", "regret", "loop"], aggfunc="mean").round(2)
    by_group.to_csv("results/tables/by_group.csv")
    print(overall.to_string(), "\n")

    # ---------- hypothesis table (paired bootstrap, Bonferroni-adjusted CI)
    g = df.group
    tests = [
        # id, A, B, metric, mask, label, better_if_negative
        ("H1", "B5", "B1", "correct", g.eq("T") & df.cell.isin(["TR-T1", "TR-T2"]), "T1/T2 correctness", False),
        ("H1", "B5", "B3", "correct", g.eq("T") & df.cell.isin(["TR-T1", "TR-T2"]), "T1/T2 correctness", False),
        ("H2", "B5", "B0", "regret", g.eq("P"), "P-cell regret", True),
        ("H2", "B5", "B4", "regret", g.eq("P"), "P-cell regret", True),
        ("H2", "B5", "B3", "regret", g.eq("P"), "P-cell regret", True),
        ("H2", "B5", "B4", "loop", g.eq("P"), "P-cell loop rate", True),
        ("H2", "B5", "B3", "loop", g.eq("P"), "P-cell loop rate", True),
        ("H3", "B5", "B4", "correct", g.eq("F"), "F-cell correctness", False),
        ("H3", "B5", "B3", "correct", g.eq("F"), "F-cell correctness", False),
        ("H4", "B1", "B5", "correct", g.eq("P"), "P-cell correctness", False),
        ("H4", "B1", "B5", "regret", g.eq("P"), "P-cell regret", True),
        ("H4", "B1", "B5", "correct", g.eq("F") | df.cell.eq("TR-T3"), "F + T3 correctness", False),
        ("MAIN", "B5", "B1", "correct", df.index.notna(), "all-cell correctness", False),
        ("MAIN", "B5", "B4", "correct", df.index.notna(), "all-cell correctness", False),
        ("MAIN", "B5", "B3", "correct", df.index.notna(), "all-cell correctness", False),
        ("MAIN", "B4", "B2", "correct", df.index.notna(), "does history help the LLM? (B4 vs B2)", False),
    ]
    rows = []
    for hid, a, b, metric, mask, label, neg in tests:
        d, lo, hi, n = paired_boot(df, a, b, metric, mask)
        rows.append(dict(hypothesis=hid, comparison=f"{a} - {b}", subset_metric=label, n_pairs=n,
                         diff=round(d, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3), reading=reading(lo, hi, neg)))
    hyp = pd.DataFrame(rows)
    hyp.to_csv("results/tables/hypotheses.csv", index=False)
    print(hyp.to_string(index=False))

    # ---------- fig1: correctness heatmap
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(by_cell.to_numpy(), vmin=0, vmax=1, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(methods)), methods)
    ax.set_yticks(range(len(cells)), cells)
    for i in range(len(cells)):
        for j in range(len(methods)):
            v = by_cell.iloc[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", color="white" if v < 0.6 else "black", fontsize=8)
    ax.set_title("Correct termination by fault cell and method")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig("figures/fig1_correct_heatmap.png", dpi=200)
    plt.close(fig)

    # ---------- fig2: regret by regime group
    groups = [x for x in ["T", "F", "P"] if x in set(df.group)]
    fig, ax = plt.subplots(figsize=(7, 4))
    w = 0.8 / len(methods)
    for k, m in enumerate(methods):
        vals = [df[(df.method == m) & (df.group == gg)].regret.mean() for gg in groups]
        ax.bar(np.arange(len(groups)) + k * w, vals, w, label=m)
    ax.set_xticks(np.arange(len(groups)) + 0.4 - w / 2, [{"T": "transient (T1-T3)", "F": "fixable", "P": "permanent"}[x] for x in groups])
    ax.set_ylabel("mean regret (excess attempts over oracle)")
    ax.set_title("Wasted attempts by fault regime")
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig("figures/fig2_regret_by_regime.png", dpi=200)
    plt.close(fig)

    # ---------- fig3: decision heatmaps (B4 vs B5)
    dec = df.explode("decisions").dropna(subset=["decisions"]).reset_index(drop=True)
    dec = dec[dec.decisions.isin(MODES)]
    show = [m for m in ["B4", "B5"] if m in set(df.method)]
    if show and len(dec):
        fig, axes = plt.subplots(1, len(show), figsize=(5 * len(show), 5), squeeze=False)
        for ax, m in zip(axes[0], show):
            ct = pd.crosstab(dec[dec.method == m].cell, dec[dec.method == m].decisions).reindex(index=cells, columns=MODES).fillna(0)
            frac = ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
            ax.imshow(frac.to_numpy(), vmin=0, vmax=1, cmap="magma", aspect="auto")
            ax.set_xticks(range(len(MODES)), MODES, rotation=30)
            ax.set_yticks(range(len(cells)), cells)
            for i in range(len(cells)):
                for j in range(len(MODES)):
                    ax.text(j, i, f"{frac.iloc[i, j]:.2f}", ha="center", va="center", color="white" if frac.iloc[i, j] < 0.6 else "black", fontsize=7)
            ax.set_title(f"{m}: decision mix per cell")
        fig.tight_layout()
        fig.savefig("figures/fig3_decisions.png", dpi=200)
        plt.close(fig)

    # ---------- fig4: tokens vs correctness
    fig, ax = plt.subplots(figsize=(5.5, 4))
    for m in methods:
        sub = df[df.method == m]
        ax.scatter(sub.tokens.mean(), sub.correct.mean(), s=60)
        ax.annotate(m, (sub.tokens.mean(), sub.correct.mean()), textcoords="offset points", xytext=(5, 5))
    ax.set_xlabel("mean LLM tokens per episode")
    ax.set_ylabel("correct termination rate")
    ax.set_title("Cost vs correctness")
    fig.tight_layout()
    fig.savefig("figures/fig4_tokens_vs_correct.png", dpi=200)
    plt.close(fig)
    print("\nsaved figures/fig1..fig4 and results/tables/*.csv")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(glob.glob("results/raw/*.jsonl")))
