# Pre-registration (write BEFORE the main run; commit)

**Date/time:** ____  
**Git commit:** ____ (`git rev-parse --short HEAD`)  
**Prompt version:** `prompts-frozen-v1`  
**Model:** qwen2.5:7b  
**Seeds:** [0]  
**Estimated hours (from pilot):** ____  

## Design
20 tasks × 11 fault cells × 1 seed × 6 methods (B0–B5).  
Faulted step = first `pick` of each task (later picks of the same object count as the same step).  
Max failures per episode = 8.  
Pilot go/no-go must pass before this run is launched.

## Methods (frozen)
| ID | Rule |
|----|------|
| B0 | Always retry until cap |
| B1 | 3 attempts total, then abstain |
| B2 | LLM mode from **current error only** (no history) |
| B3 | Always replan (LLM), no history |
| B4 | LLM mode with **full failure history** |
| B5 | Explicit rules on code + counts (`configs/policy.yaml`) |

Modify/replan content for B2/B4/B5 uses the same prompts; B4 vs B5 differs only in **who picks the mode**.

## Primary metrics
1. **Correct termination** — solvable cell → `success`; unsolvable (P) cell → `abstain` or `escalate`.
2. **Regret** = max(0, attempts_on_faulted_step − oracle_attempts).  
   Oracle: NONE 1; T-n → n+1; F → 2; P → 1.

## Secondary metrics (report, not confirmatory)
Loop rate, decision mix, tokens, latency, human-query (escalate) count.

## Hypotheses
- **H1:** Methods are similar at low persistence (TR-T1, TR-T2).
- **H2:** B5 has lower regret and lower loop rate than B0, B3, and B4 on **P** cells.
- **H3:** B5 does not reduce correctness on **F** cells vs B3 and B4.
- **H4:** B1 ties B5 on **P** cells but loses on **F** cells and TR-T3.
- **Side question:** Does history help the LLM? (B4 vs B2, all cells.)

## Comparisons and test
Paired bootstrap over matched `(task, cell, seed)` units, 10,000 resamples.  
Primary comparisons (98.3% CI, Bonferroni for 3): **B5 vs B1**, **B5 vs B4**, **B5 vs B3** on all-cell correctness.  
Other rows in `results/tables/hypotheses.csv` are secondary.

## If results are null
Report them as null.  
- B4 ≈ B5 → a capable LLM can recover a similar policy from history.  
- B4 < B5 → an explicit policy is still worth it.  
Both are valid findings. **Do not** change faults, prompts, thresholds, or metrics after seeing main-run results.

## Frozen before the run
- `configs/policy.yaml` (B5 thresholds)
- `src/pfr/prompts.py` (tagged `prompts-frozen-v1`)
- `configs/main.yaml`
- This file + git tag `prereg-v1`

## Post-run deviations and amendments
- **2026-10-10 (commit `eead494`):** Fixed an environment generator bug where candidate location sampling for `ST-F` did not exclude the target object's goal location, causing 6/20 tasks to start with their goal already satisfied at t=0. The candidate list in `src/pfr/faults.py` was updated to exclude `task['goal']['at'].get(anchor['obj'])`. Exactly 72 affected episodes across 12 tasks were re-run; pre-fix results were archived at `results/raw/qwen_pre_fix.jsonl`. Method rankings and hypothesis CI conclusions remained completely unchanged (`results/tables/st_f_sensitivity.csv`).