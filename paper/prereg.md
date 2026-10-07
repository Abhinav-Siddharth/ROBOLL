# Pre-registration (write BEFORE the main run; commit; tag prereg-v1)

Date/time: ____        Git commit of code: ____        Prompt version: v1        Model: qwen2.5:7b        Seeds: [0]

## Design
20 tasks x 11 fault cells x 1 seed x 6 methods (B0-B5). Faulted step = first `pick` of each task.

## Primary metrics
1. Correct termination (solvable cell -> goal reached; unsolvable cell -> abstain or escalate).
2. Regret = max(0, attempts on the faulted step - oracle attempts). Oracle: NONE 1, T-n n+1, F 2, P 1.

## Hypotheses
- H1: methods are similar at low persistence (TR-T1, TR-T2).
- H2: B5 has lower regret and loop rate than B0, B3 and B4 on P cells.
- H3: B5 does not reduce correctness on F cells (compared with B3 and B4).
- H4: B1 (3 attempts then abstain) ties B5 on P cells but loses on F cells and TR-T3.
Side question: does history help the LLM? (B4 vs B2, all cells.)

## Comparisons and test
Paired bootstrap over matched (task, cell, seed) units, 10,000 resamples, 98.3% CI (Bonferroni for 3 primary comparisons: B5 vs B1, B5 vs B4, B5 vs B3 on all-cell correctness). Other rows in results/tables/hypotheses.csv are secondary (report them, do not call them confirmatory).

## If results are null
Report them as null. A B4 ~ B5 result means "a capable LLM recovers the same policy from history"; a B4 < B5 result means "an explicit policy is worth it". Both are findings. Do not change faults, prompts, thresholds or metrics after seeing main-run results.

## Frozen before the run
configs/policy.yaml (thresholds), src/pfr/prompts.py (text), configs/main.yaml.
