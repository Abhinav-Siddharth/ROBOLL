# pfr: persistent failure recovery for LLM-based robot agents

Controlled simulator study: when a skill keeps failing, should the agent retry, modify, replan, escalate or abstain?
Methods B0-B5, 20 tasks, 11 fault cells (transient / fixable / permanent), regret against an oracle attempt count.

## Setup
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt && pip install -e .
    ollama pull qwen2.5:7b

## Tests (no model needed)
    pytest -q

## Dry run with the fake model (seconds, no Ollama)
    python -m pfr.runner --config configs/pilot.yaml --model stub --out /tmp/stub.jsonl
    python analysis/summarize.py /tmp/stub.jsonl

## Reproduce the results
    python -m pfr.runner --config configs/pilot.yaml --model qwen2.5:7b --out results/raw/pilot.jsonl
    python analysis/summarize.py results/raw/pilot.jsonl          # go / no-go
    bash scripts/run_main.sh                                       # 1320 episodes, resumable
    python analysis/make_figures.py results/raw/qwen.jsonl         # figures/ and results/tables/

## Layout
    src/pfr/env.py        simulator (5 skills, structured results)
    src/pfr/tasks.py      20 tasks
    src/pfr/faults.py     11 fault cells, oracle attempts
    src/pfr/prompts.py    frozen prompts (v1)
    src/pfr/llm.py        Ollama wrapper + cache
    src/pfr/runner.py     episode loop + CLI
    src/pfr/methods/      B0-B5
    configs/              pilot, main, timing, policy thresholds
    analysis/             summarize.py (go/no-go), make_figures.py
    paper/                claim, prereg, notes, outline

## Pilot stages

`configs/pilot.yaml` is stage 1 only: 5 tasks x 11 cells x B0/B3/B4 = 165 episodes.
The archived `results/raw/pilot.jsonl` contains a later six-method pilot of 330 episodes.
To reproduce that design explicitly use `--methods B0,B1,B2,B3,B4,B5`; do not append to
or overwrite the archive. Use a new output path and record the exact config.

An editable install declares runtime and analysis dependencies. Test and viewer tools
are available through `pip install -e '.[test,viz]'`. Viewer dependencies are optional.

## Phase 2 replication

The prospective amendment is in `paper/prereg.md` (commit `9924f5e`).
V1 is preserved at `results/raw/qwen.jsonl`; v2 is primary at
`results/raw/qwen_v2.jsonl` with 800 new faulted episodes and 520 proven unchanged
controls. Reuse source IDs and hashes are recorded in each reused row. The 200-row
matched-context B2C ablation is `results/raw/qwen_v2_ablation.jsonl`.

New runs use `scripts/run_v2.py` and `results/cache_v2`, including model digest,
Ollama version and options in their cache identity. The legacy cache stays readable.
These batches are already complete; use a new dataset path for a new experiment.
Never write to the source archives or regenerate original tables/figures in place.

Inspect `audit/phase2/GATE_REPORT.md` for actual commands, test transcripts, wall
measurements and limitations. Derived v1 metrics are in `results/derived_v1/`.
V2 primary tables are in `results/v2/results/tables/`, additional definitions and
cluster intervals in `results/v2/derived/`, and figures in `results/v2/figures/`.
`results/v2/comparison.csv` gives before/after values; ablation comparisons are
secondary and use the same 200 faulted cases for every method.

Verification without inference:

```bash
PYTHONPATH='' .venv/bin/python scripts/verify_phase2.py
PYTHONPATH='' .venv/bin/python -m pytest -q
```

Primary analysis requires an explicit dataset argument and a new working directory.
Do not use the implicit raw-file glob, which would pool pilot and archived versions.
The primary regret field retains its original global-failure-based convention.
Companion tables/figures report literal anchor regret and total failure cost.
Neither low regret nor correct permanent termination implies goal completion.
