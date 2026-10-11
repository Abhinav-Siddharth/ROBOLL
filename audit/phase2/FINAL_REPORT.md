# Phase 2 completion report

All requested gates are complete. The user authorized completing the full protocol on 2026-10-11. The prospective amendment was committed as `9924f5e` before any v2 inference. No new benchmark seeds, model, or KL study were introduced.

## Verified execution and preservation

| Check | Command/evidence | Key output | Status |
|---|---|---|---|
| Working-tree tests | `PYTHONPATH='' .venv/bin/python -m pytest tests -q -p no:cacheprovider` with temporary cache paths; final-worktree-tests.txt | 425 passed in 3.14s | VERIFIED |
| Clean-clone tests | Exact command in final-clone-tests.txt; clean-clone editable install with declared dependencies | 425 passed in 2.80s; 0 skips/failures | VERIFIED |
| Import isolation | Fresh interpreter from `/tmp`; final-clone-imports.txt | dev checkout on sys.path: False; imports under /tmp/pfr-phase2-final-clone | VERIFIED |
| Protected v1 artifacts | `PYTHONPATH='' .venv/bin/python scripts/verify_phase2.py`; gate4-integrity.txt and final-clone-integrity.txt | 19 original log/table/figure hashes unchanged | VERIFIED |
| Main v2 grid | Same integrity command | 1320 exact unique IDs: 800 new, 520 proven reused | VERIFIED |
| Ablation grid | Same integrity command | 200 exact unique B2C IDs | VERIFIED |
| Calls and reconstruction | Same integrity command | zero invalid calls, exhausted parse/schema failures and replay mismatches in both v2 files | VERIFIED |
| Saved metrics | Independent calculations in scripts/verify_phase2.py | all saved costs, groups, failures, decisions and human counts match 1320 v1, 1320 v2 and 200 ablation rows | VERIFIED |
| Cached model outputs | `PYTHONPATH='' .venv/bin/python audit/phase2/cache_verify.py results/raw/qwen_v2.jsonl results/raw/qwen_v2_ablation.jsonl` | 5278 requests, 2752 unique keys, 0 missing/mismatched; no omitted place.loc | VERIFIED |
| Design freeze | Frozen hashes in prereg_manifest.json and exact transmitted-text comparison in gate3-frozen-design.txt | primary analysis, task and policy hashes unchanged; default B2/B4 prompt text unchanged | VERIFIED |

Clean-clone source commit: d0a954092e6e41a7aea285dd1fc8557af42ef12d. The final report/evidence commit after it changes no tested source, tests, configs, paper notes or datasets. The isolated environment used Python 3.12, NumPy 2.5.4, pandas 3.0.6, pydantic 2.14.0, jsonschema 4.26.0, pytest 9.1.1 and the existing local PyBullet 3.2.7 wheel. Source-building PyBullet and other OS/Python combinations remain UNVERIFIED.

## What changed

Gate 1 has separate commits and actual failing-before/passing-after transcripts for every item. It adds trace-derived literal anchor attempts/regret, total failure cost and preserved legacy regret; explicit autonomous/assisted definitions; task-cluster intervals; interrupted-tail quarantine; stronger replay guards; dependency declarations; current model/server metadata; and CSV-generated paper notes with narrowed claims and verified bibliography metadata. Archived runner metric semantics remain unchanged.

The format repair adds skill-specific required arguments and runtime schema validation, and validates calls before fault interception. Every original method uses the same repaired replan interface. New cache identity includes the namespace, model digest, server version and context option, while legacy keys stay readable. Extra integrity fixes preserve original batch timing on repeated invocations and check IDs against row coordinates. These have their own regression transcripts and commits.

## Gate 3 result

Command: `PYTHONPATH='' .venv/bin/python scripts/run_v2.py --config configs/v2_gate.yaml --out results/raw/qwen_v2.jsonl --batch gate3`. Its transcript and manifest are gate3-inference.txt and gate3-run.json. Structural continuation was independent of success rates.

| Method | ST-F autonomous / assisted, n=20 | PRE-F autonomous / assisted, n=20 |
|---|---:|---:|
| B2 | 0 / 0 | 0 / 0 |
| B3 | 16 / 0 | 17 / 0 |
| B4 | 3 / 9 | 0 / 6 |
| B5 | 16 / 0 | 17 / 0 |

VERIFIED: all 160 IDs unique and complete; invalid-call and exhausted parse/schema-failure counts are zero; all replay checks pass. The 60-request smoke check also had zero bad outputs or exhausted parsing/schema failures. Actual wall time: smoke 51.6s; gate 736.65s (12.28 min); remaining 640 episodes 1988.04s (33.13 min); ablation 632.35s (10.54 min). These are observed invocation times, distinct from saved request latency sums.

## V1 vs v2

Command: `PYTHONPATH='' .venv/bin/python analysis/compare_versions.py --ablation results/raw/qwen_v2_ablation.jsonl`. Full values are results/v2/comparison.csv and comparison_by_cell.csv; status VERIFIED from the saved datasets.

| Method | V1 raw correctness | V2 raw correctness | V1 literal anchor regret | V2 literal anchor regret |
|---|---:|---:|---:|---:|
| B0 | 36.4% | 36.4% | 4.182 | 4.182 |
| B1 | 63.6% | 63.6% | 1.000 | 1.000 |
| B2 | 45.5% | 45.5% | 3.468 | 3.464 |
| B3 | 9.1% | 52.7% | 2.636 | 2.559 |
| B4 | 68.2% | 70.9% | 3.227 | 3.264 |
| B5 | 81.4% | 95.5% | 0.900 | 0.868 |

On solvable cells, v2 autonomous successes are B2 100/140, B3 116/140, B4 103/140 and B5 133/140. B4 has 15 additional human-assisted successes. Across all 220 episodes, v2 zero-human correctness is B4 103/220 (46.8%) and B5 190/220 (86.4%). These denominator-220 figures include correct permanent abstention and must not be described as permanent-cell-only rates.

Primary H2 still favors B5 on permanent-cell legacy regret and loops. Literal-anchor H2 sensitivity also favors B5. H3 reverses its B5-B4 F-cell reading: v1 difference -0.233; v2 +0.250 with paired-row CI [0.117, 0.400]. H1 B5-B3 T1/T2 has row CI [0.025, 0.300] but task-cluster CI [0.000, 0.350]. The clustering choice materially changes that reading; a CI including zero does not establish equivalence. These outputs use the unchanged primary script and additional explicitly named sensitivity analyses.

## Matched-context ablation

Command: `PYTHONPATH='' .venv/bin/python scripts/run_v2.py --config configs/v2_ablation.yaml --out results/raw/qwen_v2_ablation.jsonl --batch gate4-ablation`. B2C receives current failure count, remaining budget and untried values, with no prior failure history. All methods below use the same 200 faulted task/cell/seed cases.

| Method | Raw correct | Zero-human correct | Autonomous task success | Assisted task success |
|---|---:|---:|---:|---:|
| B2 | 80/200 = 40.0% | 80/200 = 40.0% | 80 | 0 |
| B2C | 88/200 = 44.0% | 82/200 = 41.0% | 82 | 3 |
| B4 | 136/200 = 68.0% | 83/200 = 41.5% | 83 | 15 |

VERIFIED: B2C-B4 raw difference is -0.240; paired-row CI [-0.325, -0.160], task-cluster CI [-0.343375, -0.140]. The zero-human difference is -0.005, CI [-0.025, 0.015] under both schemes. History's observed advantage conditional on the hints is primarily assistance/escalation, not a clear autonomous-completion advantage. This is a secondary post-audit comparison, not a model-independent claim or a familywise guarantee over all exploratory rows.

## What remains uncertain or untrustworthy

- Independent inference replication, more seeds/models, physical execution, all real 3D/IK trajectories and GUI behavior remain UNVERIFIED. No new seeds/model or KL study was run.
- Format validity does not guarantee an executable or complete plan. Residual failures include ignored prerequisite visits, failure to navigate to the object, and omitted drawer closure. Goal text does not explicitly state every formal drawer predicate, although remaining plans contain close actions. The causal effect of goal-specification clarity is UNVERIFIED; v2 was kept frozen.
- A valid empty replan remains `incomplete`, including three B5 ST-P episodes; it is not retrospectively relabeled as abstention. Low anchor regret alone can reward unsuccessful termination and is reported alongside total failures and correctness.
- V1's full historical server identity is unknown. Before/after numbers are descriptive; this one-model/seed study does not isolate all runtime variation or establish generalization.
- Bootstrap intervals are conditional on this small scripted task set. Cluster sensitivities are visible and do not replace primary results.
- Bibliography titles/authors/IDs were checked against official arXiv metadata; a full comparative literature review and an assembled submission manuscript remain unfinished. Neither is claimed as completed by these repair gates.

## Deliverables

- audit/phase2/GATE_REPORT.md: each gate and exact execution transcripts.
- paper/prereg.md: historical corrections plus the prospective amendment.
- results/raw/qwen_v2.jsonl: primary v2, including marked proven reuse.
- results/raw/qwen_v2_ablation.jsonl: separate 200-row B2C ablation.
- results/derived_v1/: dual costs, named outcomes and cluster sensitivities.
- results/v2/: primary tables, companion metrics/figures, comparisons and ablation outputs.
- paper/notes/results.md and hypothesis.md: CSV-generated v1/v2 dual reporting.

Every gate is finished; source artifacts remain preserved. The next scientific work should address the documented limitations through a new prospective protocol rather than silently changing these data.
