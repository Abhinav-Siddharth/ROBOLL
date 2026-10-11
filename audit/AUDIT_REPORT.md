# Phase 1 audit report

Audit date: 11 October 2026, Asia/Kolkata. Repository: `/home/abhi_pop/pfr`. HEAD: `8fe3485492790990051a8f9d5d9ce77a71fb11a2`.

No repository file was changed by this audit. Scratch clone, environments, scripts, derived outputs and this report are under `/tmp`. No Ollama inference, model download, policy experiment rerun, commit or in-place regeneration was performed. Tests used the repository's fake model as part of the authorized full test suite. Constructive feasibility checks executed hand-written skill sequences, not LLM policies. Your latest instruction overrides the pasted instruction to create `audit/AUDIT_REPORT.md`, so that path was not created.

**Verdict:** The dataset is complete and its saved computations reproduce. The main correctness ranking is a verified description of these traces. Interpretation as autonomous recovery, literal faulted-step regret, or an isolated causal effect of history needs repair. The planner schema permits malformed calls, and the cost metric counts failures outside its named step.

## Evidence and status conventions

VERIFIED means a check ran and supported the stated observation. FAILED means a promised property or stated claim was tested and contradicted. UNVERIFIED means it was not established, with the reason stated. A verified bug is still a failed requirement. Proposed fixes and future timing are recommendations, not verified outcomes.

All custom scripts are retained beside this report. Their output files contain the full output, including numerators and denominators. They only read the repository; any files they create are in `/tmp/pfr-audit-evidence`.

Command prefix used for custom scripts:

```bash
PYTHONPATH='' PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/pfr-audit-mpl   /home/abhi_pop/pfr/.venv/bin/python
```

Commands A1 through A6 below refer to that prefix followed by:

| ID | Script | Output |
|---|---|---|
| A1 | `/tmp/pfr-audit-evidence/check.py` | `check.out` |
| A2 | `/tmp/pfr-audit-evidence/extra.py` | `extra.out` |
| A3 | `/tmp/pfr-audit-evidence/more.py` | `more.out` |
| A4 | `/tmp/pfr-audit-evidence/edge.py` | `edge.out` |
| A5 | `/tmp/pfr-audit-evidence/cache.py` | `cache.out` |
| A6 | `/tmp/pfr-audit-evidence/metrics.py` | `metrics.out` |

These commands, script source, quoted output and statuses support the findings below. No assertion of model behavior under a repaired schema is made.

## A. Inventory and checkout state

**FAILED: clean checkout requirement.** Command: `git status --short`; rerun at the end with the same output as at the start. Thirteen tracked files are deleted, five tracked files modified, and three untracked status entries exist, including a directory containing ten notes:

```text
 D RUNBOOK_DAY8.md
 D paper/competitors.md
 D paper/course.md
 D paper/notes/CAPE.md
 D paper/notes/FRAMES.md
 D paper/notes/Graph_Harness.md
 D paper/notes/Reflective_Test_Time_Planning.md
 D paper/notes/Retry_Switch_Abstain.md
 D paper/notes/Self_Healing_Orchestrators.md
 D paper/notes/TOOL_MAZE.md
 D paper/notes/YALE.md
 D paper/notes/_template.md
 D paper/notes/faults.md
 M requirements.txt
 M scripts/bench.py
 M scripts/check_llm.py
 M src/pfr/methods/__init__.py
 M src/pfr/prompts.py
?? paper/Closest_papers.md
?? "paper/notes/Related work_Literature survey/"
?? run_tests.sh
```

**VERIFIED:** `git diff -- requirements.txt scripts/bench.py scripts/check_llm.py src/pfr/methods/__init__.py src/pfr/prompts.py` shows a local pytest pin to `9.1.1` and four docstring edits. The prompt edit does not change the transmitted prompts or schema. Deleted literature notes have untracked counterparts in a different directory, but deleted `competitors.md` and `course.md` do not have same-name counterparts. Their content was not restored.

**VERIFIED:** `git log --all --oneline -- '**/RUNBOOK*' '*RUNBOOK*'` returns only `06f8af8 ... Day 8 ...`. No 7-day runbook was found in the current repository or its reachable runbook history. `git show HEAD:RUNBOOK_DAY8.md` supplies the deleted Day 8 checklist. Its old six-task ST-F warning is historical, superseded by the generator fix. A literal day-by-day 7-day plan cannot be verified; the progress checklist below is derived from README and paper outline.

Full file inventory appears in Appendix A. It includes all tracked code, configs, scripts, tables, figures, paper files and demos. `configs/timing.yaml` is a candidate filename for README's promised timing configuration, not an explicitly specified filename. No timing config exists among the three actual configs. `docs/` runbook paths were checked as fallback locations, not claimed deliverables.

**FAILED: complete paper/submission artifacts.** Command: `cat paper/outline.md paper/refs.bib; wc -c paper/refs.bib; rg --files`. Output: `paper/refs.bib` is 17 bytes and contains only `%Papers refered.`. The outline and section notes exist; no assembled paper PDF, TeX or Word manuscript is present. Citation validity, novelty and whether cited papers were previously opened are **UNVERIFIED**, since repository artifacts do not establish them and external literature was not audited.

## B. Progress and dataset completeness

**VERIFIED: exact grid.** Command A1:

```text
INTEGRITY rows 1320 unique 1320 duplicates 0 missing 0 unexpected 0
```

Expected IDs were constructed independently from 20 task IDs, 11 cells, methods B0 through B5, seed 0 and model `qwen2.5:7b`. The expected set equals the actual set. Every cell has exactly 20 rows for every method:

| Cell | B0 | B1 | B2 | B3 | B4 | B5 |
|---|---:|---:|---:|---:|---:|---:|
| NONE | 20 | 20 | 20 | 20 | 20 | 20 |
| TR-T1 | 20 | 20 | 20 | 20 | 20 | 20 |
| TR-T2 | 20 | 20 | 20 | 20 | 20 | 20 |
| TR-T3 | 20 | 20 | 20 | 20 | 20 | 20 |
| TR-P | 20 | 20 | 20 | 20 | 20 | 20 |
| PAR-F | 20 | 20 | 20 | 20 | 20 | 20 |
| PAR-P | 20 | 20 | 20 | 20 | 20 | 20 |
| ST-F | 20 | 20 | 20 | 20 | 20 | 20 |
| ST-P | 20 | 20 | 20 | 20 | 20 | 20 |
| PRE-F | 20 | 20 | 20 | 20 | 20 | 20 |
| PRE-P | 20 | 20 | 20 | 20 | 20 | 20 |

Derived 7-day checklist, rather than an invented reconstruction of unavailable daily instructions:

| Stage | Progress | Evidence/status |
|---|---|---|
| Simulator, tasks and fault taxonomy | Done, with metric/design qualifications | A1/A2: all 140 solvable task-cell pairs have constructive solutions; full tests pass |
| Local model installation, latency benchmark, schema smoke tests | Partial verification | `results/meta.txt` exists; caches and logs verified by A5. Live Ollama health, benchmark and 20-call schema smoke tests not run, because new inference requires approval |
| Methods and freeze | Implementation done; documentation partial | Six method files and two tags exist. `prereg.md` date/time, commit and estimated hours remain blank |
| Pilot and go/no-go | Saved pilot passes; config mismatch | `summarize.py` outputs GO; A6 finds 330 rows, all six methods, five tasks, one seed. Current pilot config selects only B0/B3/B4, which would produce 165 rows |
| Main benchmark | Done | A1: exact 1320-ID grid; A5: all cached requests reconcile |
| Tables, figures, hypothesis analysis | Computations done; interpretation partial | A2: five tables and four main figures reproduce exactly. Paper notes have stale values and stronger causal claims than checked evidence |
| Final manuscript, references, submission | Not evidenced as complete | Empty bibliography and no assembled paper. Submission outside the repository is UNVERIFIED |
| Day 8 replay | Headless checks and artifacts done; GUI unverified | 1320 state replays pass; 60-episode scene check reports 0.01 cm; videos decode; existing contrast HUD visually inspected |

Pilot verification command:

```bash
PYTHONPATH='' PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/pfr-audit-mpl  /home/abhi_pop/pfr/.venv/bin/python analysis/summarize.py results/raw/pilot.jsonl
```

Key output:

```text
[PASS] B0 wastes >= 4 attempts on P cells (mean regret 7.00)
[PASS] B3 wastes >= 4 attempts on P cells (mean regret 7.00)
[PASS] B4 differs from B0 in 7 cells (need >= 2)
[PASS] B3 not at ceiling on solvable cells (correct 0.14, need < 0.90)
[INFO] schema parse failures across the run: 0
RESULT: GO
```

This verifies the script's criteria, not the scientific adequacy of criteria that can also be satisfied by malformed planner output. Actual preregistration timing relative to execution is **UNVERIFIED**: tags and commit chronology exist, but episode timestamps and completed registration metadata do not.

## C. Fresh-clone reproducibility

**VERIFIED: current working tree tests.** Command, from `/home/abhi_pop/pfr`:

```bash
PYTHONPATH='' PYTHONDONTWRITEBYTECODE=1 PFR_CACHE=/tmp/pfr-audit-cache  MPLCONFIGDIR=/tmp/pfr-audit-mpl .venv/bin/python -m pytest -q  -p no:cacheprovider --basetemp=/tmp/pfr-audit-tests
```

Output: `384 passed in 2.63s`. Counts: **384 passed, 0 skipped, 0 failed, 0 errors**.

**VERIFIED: isolated clone of committed HEAD, not a copy of the dirty working tree.** Commands:

```bash
git clone --no-hardlinks /home/abhi_pop/pfr /tmp/pfr-audit-20261011
/home/abhi_pop/pfr/.venv/bin/python -m venv /tmp/pfr-audit-20261011-venv
PYTHONPATH='' PIP_CACHE_DIR=/tmp/pfr-audit-pip-cache  /tmp/pfr-audit-20261011-venv/bin/python -m pip install  -e /tmp/pfr-audit-20261011 -r /tmp/pfr-audit-20261011/requirements.txt --prefer-binary
```

The initial sandboxed editable install failed resolving setuptools because DNS/network access was unavailable. Network access for the isolated install was subsequently granted by automatic approval review, and the core install succeeded. An attempted viewer dependency install downloaded PyBullet source; it was cancelled before compilation to avoid a long build. Instead, the already available local wheel was installed:

```bash
PYTHONPATH='' /tmp/pfr-audit-20261011-venv/bin/python -m pip install  --no-index --no-deps  /home/abhi_pop/.cache/pip/wheels/72/95/1d/b336e5ee612ae9a019bfff4dc0bedd100ee6f0570db205fdf8/pybullet-3.2.7-cp312-cp312-linux_x86_64.whl
```

Before installing that wheel, the full test command yielded:

```text
SKIPPED [1] tests/test_viz_scene.py:5: could not import 'pybullet': No module named 'pybullet'
370 passed, 1 skipped in 0.73s
```

This is one skipped module at collection, not fourteen reported skipped test items. After wheel installation, command from `/tmp/pfr-audit-20261011`:

```bash
PYTHONPATH='' PYTHONDONTWRITEBYTECODE=1 PFR_CACHE=/tmp/pfr-audit-fresh-cache  MPLCONFIGDIR=/tmp/pfr-audit-mpl /tmp/pfr-audit-20261011-venv/bin/python  -m pytest -q -rs -p no:cacheprovider  --basetemp=/tmp/pfr-audit-fresh-with-viz-tests
```

Output: `384 passed in 2.87s`. Counts: **384 passed, 0 skipped, 0 failed, 0 errors**.

Fresh dependencies included Python 3.12.3, pytest 9.1.1, NumPy 2.5.4, pandas 3.0.6, pydantic 2.14.0 and PyBullet 3.2.7. The dev environment used NumPy 2.5.3. Source-building PyBullet, installing on another OS and the full optional video dependency installation in the fresh venv are **UNVERIFIED**. No long build was launched.

**VERIFIED: imports from outside either checkout.** From `/tmp`, the fresh interpreter imported `pfr`, `pfr.runner` and `pfr.viz.state`:

```text
pfr /tmp/pfr-audit-20261011/src/pfr/__init__.py
runner /tmp/pfr-audit-20261011/src/pfr/runner.py
Requires-Dist None
dev checkout on sys.path False
```

**FAILED: editable install alone declares necessary dependencies.** Command A3 and fresh `importlib.metadata.metadata('pfr').get_all('Requires-Dist')` both return `None`. `pyproject.toml` declares no runtime dependencies. A bare `pip install -e .` therefore does not supply pydantic, yaml or tqdm, nor the test tools. The README explicitly installs `requirements.txt` first, and that complete route was tested successfully. No tested core import depended on the development checkout.

## D. Re-derived tables, figures and pre-fix comparison

**VERIFIED: every existing CSV reproduces byte-for-byte.** From a scratch working directory:

```bash
cd /tmp/pfr-audit-evidence/rederived
PYTHONPATH='' PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/pfr-audit-mpl  /home/abhi_pop/pfr/.venv/bin/python /home/abhi_pop/pfr/analysis/make_figures.py  /home/abhi_pop/pfr/results/raw/qwen.jsonl
```

This script produces four tables. A2 separately reconstructs the fifth, `st_f_sensitivity.csv`, from both raw datasets. Key output:

```text
TABLE_BYTE_DIFF by_group.csv False
TABLE_BYTE_DIFF correct_by_cell.csv False
TABLE_BYTE_DIFF hypotheses.csv False
TABLE_BYTE_DIFF overall.csv False
TABLE_BYTE_DIFF st_f_sensitivity.csv False
FIGURE_BYTE_DIFF fig1_correct_heatmap.png False
FIGURE_BYTE_DIFF fig2_regret_by_regime.png False
FIGURE_BYTE_DIFF fig3_decisions.png False
FIGURE_BYTE_DIFF fig4_tokens_vs_correct.png False
```

This validates derivation from saved metrics. It does not validate the intended meaning of the metrics.

**VERIFIED: pre-fix identity and zero interval changes.** Commands:

```bash
git show -s --format='%h %cI %s' 06f8af8 eead494 ef8ea10 HEAD
git diff 06f8af8 HEAD -- results/tables/hypotheses.csv
```

`06f8af8` exists and precedes `eead494`. The diff produces no output. A1/A2:

```text
ARCHIVE equal to commit 06f8af8 raw True
HYPOTHESES rows 16 16 changed_rows 0 changed_intervals 0
```

The complete list of changed stored intervals is therefore **empty**. To avoid trusting an old table, the same figure-analysis command was also run on `qwen_pre_fix.jsonl` in `/tmp/pfr-audit-evidence/pre-rederived`; `diff -u` against `git show 06f8af8:results/tables/hypotheses.csv` also produced no output. Both old and new hypothesis tables independently reproduce. These are the stored three-decimal bounds, not a claim about a different metric definition or a repaired-schema experiment.

**VERIFIED: ST-F fix scope.** A2 executes old and current generator code and reports twelve changed task locations:

```text
['t01','t02','t04','t07','t09','t10','t13','t16','t17','t18','t19','t20']
expected_affected_episodes 72
old_initial_goal_true ['t01','t04','t07','t13','t17','t19']
```

A1 compares whole JSON rows: **29 rows differ**, all in ST-F, spanning all twelve changed tasks. Seventy-two affected IDs and 29 changed rows are compatible because rerun/cached execution can yield identical records. **UNVERIFIED:** that all 72 IDs actually invoked new inference, or even that all were executed again; identical row contents and a script declaring 72 do not prove execution provenance. The amendment's “exactly 72 ... re-run” is stronger than the artifact evidence alone establishes.

`cat paper/prereg.md paper/notes/setup.md` shows claims that rankings and hypothesis CI conclusions remained unchanged. Those narrow claims are supported. ST-F regret values did change: B3 **6.45 to 6.70**, B5 **2.75 to 2.80**. Neither file explicitly claims exact unchanged regret values or bounds. Their evidence pointer to the sensitivity table supports ST-F rankings; actual interval equality was verified separately against `hypotheses.csv`.

## E1. Invalid-call hallucinations

**FAILED: replan schema guarantees executable calls. VERIFIED: omission mechanism.** A1/A3:

```text
SCHEMA required ['skill']
Call.from_flat place(obj=apple, loc=None, orient=upright)
result ... code='PRECOND_UNMET' detail='invalid call: loc=None'
INVALID DETAILS Counter({'invalid call: loc=None': 720})
```

`loc` is optional in the schema and has no fallback in `Call.from_flat`. It is required by `Env.execute` for `place`. Cached raw planner output was also checked offline, so argument omission is not inferred solely from postprocessed calls. A5 reconciles all 4,504 requests with cache entries and finds numerous planned `place` calls lacking `loc`; some planned calls are never reached, so their counts are not the executed-invalid-step denominator.

The table below gives, for each LLM-using method and cell, **episodes with at least one invalid call / total episodes**, followed by **invalid-call failure steps / all failure steps**. `0/0` is undefined as a rate, not zero percent. Every invalid call observed here is an omitted place location.

| Cell | B2 episodes; failure steps | B3 episodes; failure steps | B4 episodes; failure steps | B5 episodes; failure steps |
|---|---|---|---|---|
| NONE | 0/20 (0%); 0/0 (N/A) | 0/20 (0%); 0/0 (N/A) | 0/20 (0%); 0/0 (N/A) | 0/20 (0%); 0/0 (N/A) |
| TR-T1 | 0/20 (0%); 0/20 (0.0%) | 20/20 (100%); 126/156 (80.8%) | 0/20 (0%); 0/20 (0.0%) | 0/20 (0%); 0/20 (0.0%) |
| TR-T2 | 0/20 (0%); 0/40 (0.0%) | 20/20 (100%); 105/156 (67.3%) | 0/20 (0%); 0/40 (0.0%) | 0/20 (0%); 0/40 (0.0%) |
| TR-T3 | 0/20 (0%); 0/60 (0.0%) | 19/20 (95%); 86/160 (53.8%) | 0/20 (0%); 0/60 (0.0%) | 0/20 (0%); 0/60 (0.0%) |
| TR-P | 0/20 (0%); 0/160 (0.0%) | 1/20 (5%); 1/160 (0.6%) | 0/20 (0%); 0/144 (0.0%) | 0/20 (0%); 0/80 (0.0%) |
| PAR-F | 0/20 (0%); 0/33 (0.0%) | 14/20 (70%); 82/156 (52.6%) | 0/20 (0%); 0/33 (0.0%) | 0/20 (0%); 0/33 (0.0%) |
| PAR-P | 0/20 (0%); 0/160 (0.0%) | 0/20 (0%); 0/160 (0.0%) | 0/20 (0%); 0/131 (0.0%) | 0/20 (0%); 0/60 (0.0%) |
| ST-F | 0/20 (0%); 0/160 (0.0%) | 18/20 (90%); 115/156 (73.7%) | 6/20 (30%); 22/149 (14.8%) | 18/20 (90%); 52/78 (66.7%) |
| ST-P | 0/20 (0%); 0/160 (0.0%) | 1/20 (5%); 1/148 (0.7%) | 0/20 (0%); 0/144 (0.0%) | 1/20 (5%); 1/64 (1.6%) |
| PRE-F | 0/20 (0%); 0/160 (0.0%) | 17/20 (85%); 94/156 (60.3%) | 1/20 (5%); 2/148 (1.4%) | 17/20 (85%); 33/77 (42.9%) |
| PRE-P | 0/20 (0%); 0/160 (0.0%) | 0/20 (0%); 0/160 (0.0%) | 0/20 (0%); 0/148 (0.0%) | 0/20 (0%); 0/60 (0.0%) |

Overall: B3 has invalid calls in **110/220 episodes, 50.0%**, accounting for **610/1568 failure steps, 38.9%**. B4: 7/220 episodes and 24/1017 failures. B5: 36/220 episodes and 86/572 failures. B2: 0/220 executed episodes, despite cached replans containing omitted arguments that are not necessarily reached.

A2's concrete trace `qwen2.5:7b|B3|t01|TR-T1|0` recovers the pick at attempt 3, then repeatedly executes `place(..., loc=None, ...)`, ending at the eighth episode failure. The schema issue therefore undermines B3's transient baseline as well as fixable state/precondition recovery.

**UNVERIFIED:** the success rate after schema repair. Valid arguments do not guarantee valid ordering, necessary prerequisites or goal completion. It is too strong to attribute all autonomous ST-F/PRE-F failures solely to the omission; 2/20 B5 ST-F and 3/20 B5 PRE-F episodes have no executed invalid calls, and B2 has no invalid calls in either cell.

## E2. Human-assisted success and autonomous definitions

**VERIFIED:** A1 computes the following success split. Each entry is **autonomous successes / human-assisted successes**, with 20 total episodes per entry. These are counts, not ratios between the two kinds of success:

| Cell | B0 | B1 | B2 | B3 | B4 | B5 |
|---|---:|---:|---:|---:|---:|---:|
| NONE | 20/0 | 20/0 | 20/0 | 20/0 | 20/0 | 20/0 |
| TR-T1 | 20/0 | 20/0 | 20/0 | 0/0 | 20/0 | 20/0 |
| TR-T2 | 20/0 | 20/0 | 20/0 | 0/0 | 20/0 | 20/0 |
| TR-T3 | 20/0 | 0/0 | 20/0 | 0/0 | 20/0 | 20/0 |
| TR-P | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| PAR-F | 0/0 | 0/0 | 20/0 | 0/0 | 20/0 | 20/0 |
| PAR-P | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| ST-F | 0/0 | 0/0 | 0/0 | 0/0 | 0/7 | 0/0 |
| ST-P | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| PRE-F | 0/0 | 0/0 | 0/0 | 0/0 | 0/7 | 0/0 |
| PRE-P | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |

B4's **7/20 ST-F successes are all human-assisted**. No method has autonomous ST-F success in this dataset. B4 also has seven human-assisted PRE-F successes. B2, B4 and B5 tie at **100/140 autonomous successes on solvable cells**.

**FAILED: consistent meaning of “autonomous correctness.”** A1/A3 show three different useful quantities:

| Definition, denominator 220 | B4 | B5 |
|---|---:|---:|
| Autonomous task success, successful solvable episodes with zero human queries | 100/220 = 45.5% | 100/220 = 45.5% |
| Correct termination with zero human queries, including permanent abstention | 100/220 = 45.5% | 159/220 = 72.3% |
| Autonomous solvable success plus any correct permanent termination, including human escalation | 136/220 = 61.8% | 179/220 = 81.4% |

The updated paper's **+19.5 percentage points** and CI `[0.132,0.264]` reproduce under the third definition. A3's unrounded bootstrap output is `(0.19545454545454546, 0.1318181818181818, 0.2636363636363636, 220)`. But that definition retains permanent human escalation; it is not “purely autonomous correctness.” The later discussion uses the second definition, approximately 0.45 and 0.72, without reconciling them. Both formulas must be explicitly named. The additional bootstrap is not among the preregistered primary CSV rows.

## E3. Can B3/B5 solve ST-F with valid replanning?

**VERIFIED: structurally possible. UNVERIFIED: actual Qwen performance after repair.** A2 constructs legal recovery suffixes for all 20 ST-F tasks and, more broadly, all 140 solvable task-cell pairs:

```text
CORRECTED_WITNESSES solvable_cases 140 bad []
```

For ST-F, the construction executes the initial failing pick, visits the observed true location, picks the target, returns to the original anchor location when needed, and completes the original suffix. Returning matters for drawer tasks, whose suffix closes the drawer before transport. This corrects an overly naive witness construction whose failures were due to attempting to close the drawer while at the hidden location. The final verified witnesses contain no such failure.

B3 always requests a new plan. B5 requests replanning on the first STATE_MISMATCH, with `state_replan_cap: 2`. A valid complete suffix can therefore succeed after one failure and one replan for either method. The policy does not prohibit ST-F success. A1 additionally finds the target already held before the first invalid call in **18 B3**, **18 B5** and **6 B4** ST-F episodes. These traces provide evidence that many failures occur after finding and picking the object, not evidence that every remaining planning issue disappears with a schema change.

## E4. Replay checking across the full dataset

**VERIFIED:** A1 calls `reconstruct` on all 1,320 rows, then independently checks detail text, attempt numbering, solvability/group labels, failures, decisions, human queries, correctness, loop flag and saved attempts/regret against the existing implementation. Key output:

```text
REPLAY rows 1320 code_mismatches 0 detail_mismatches 0 metric_mismatches 0 success_iff_goal_mismatches 0
```

Thus every saved success is a final reconstructed goal state, and no non-success reconstructs to a satisfied goal. This is a state-layer check, not a 1,320-episode physical or rendered replay.

**FAILED: raises on any mismatch.** A1 mutates copies in memory:

```text
MUTATION wrong code DETECTED
MUTATION wrong outcome/correct/detail NOT DETECTED final_goal True
```

`src/pfr/viz/state.py` checks only result codes. It does not enforce detail, final outcome, correctness, metric or attempt-index agreement. Current logs passed those broader checks through the independent auditor, but the replay API itself does not provide that guarantee.

**VERIFIED: Day 8 headless scene checkpoint.** Command:

```bash
PYTHONPATH='' PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/pfr-audit-mpl  /home/abhi_pop/pfr/.venv/bin/python scripts/replay.py  --jsonl results/raw/qwen.jsonl --check
```

Output: `max IK position error over the replay: 0.01 cm`; 60 episodes are listed in `scene-check.out`. The script truncates to 60 even in check mode. All 1,320 3D scene/IK trajectories and the live GUI are **UNVERIFIED**, because neither was run. The 1,320 state checks are complete.

A2 checks 12 PNG files and decodes/counts the three videos:

```text
PNG integrity verified 12
VIDEO reel.mp4 frames 3721 fps 30.0 size (640, 360)
VIDEO t06_PAR-F_B0.mp4 frames 735 fps 30.0 size (640, 360)
VIDEO t06_PAR-F_B5.mp4 frames 532 fps 30.0 size (640, 360)
```

Existing `figures/replay_contrast.png` was inspected with `view_image`; the task, method, failure and outcome HUD text is readable. Full clip visual quality, provenance of every rendered frame and failure-marker readability across the clips remain **UNVERIFIED**. No videos were regenerated.

## E5. Faults, tasks and oracle consistency

**VERIFIED for the configured seed 0:** A1/A2 check all 220 task-cell initial states. None starts with the complete goal satisfied; all 20 clean plans reach their goals; all 140 solvable cases have legal constructive solutions. Fixable/permanent pairs have identical first-pick error code/detail. No additional unsolvable case was found among cells labeled solvable.

Permanent unsolvability is supported by the model's transition rules: TR-P and PAR-P intercept every target pick; PRE-P never permits its required visit; ST-P leaves the target at `gone`, a location outside the selectable location set. Every task requires moving the anchor object from its initial location. Human clearing is restricted to solvable faults. This conclusion is about the symbolic model and the configured tasks, not physical feasibility or all possible future seeds.

**FAILED: literal oracle minimum claim.** A3 demonstrates that an informed agent can choose the right grasp/location/prerequisite before its first pick:

```text
CLAIRVOYANT_FIRST_PICK ST-F OK hardcoded_oracle 2
CLAIRVOYANT_FIRST_PICK PRE-F OK hardcoded_oracle 2
CLAIRVOYANT_FIRST_PICK PAR-F OK hardcoded_oracle 2
```

The hardcoded F baseline of 2 is defensible as an oracle that is forced to attempt the original anchor and only then recover. It is not the minimum anchor count for an all-knowing agent allowed to change the initial plan. The paper should state the forced-initial-attempt convention, or change the baseline and recompute metrics.

**FAILED: history is the only information that can distinguish all fixable/permanent faults.** Direct observation check:

```text
ST-F OBSERVABLE apple sink
ST-P OBSERVABLE apple gone
```

Both produce the same initial STATE_MISMATCH, but replanning receives this true observation. ST regimes are distinguishable from world state without accumulated history. The claim in `paper/claim.md` needs narrowing to identical initial failure messages, not universal information-theoretic indistinguishability.

## E6. Additional bugs and risks

### Attempts/regret count the wrong events

**FAILED: literal faulted-step attempt metric.** `nl -ba src/pfr/runner.py` shows global `n_fail += 1` at line 63 and `attempts = n_fail + (1 if anchor_ok else 0)` at line 115. A1 counts actual calls matching the anchor:

```text
ANCHOR COUNT mismatch episodes 215 excess 904
by_method {'B3': 133, 'B5': 56, 'B2': 17, 'B4': 9}
```

The current metrics correctly match this implementation, but include non-anchor failures. Example: B3/t01/TR-T1 reports nine attempts on the faulted step, although only two target picks occurred. Seven malformed places inflated it. There are no episodes with multiple successful anchor picks in this dataset, so the single `anchor_ok` flag does not currently hide repeated successful picks; it remains a possible future issue.

A6's independent scratch calculation counts literal matching anchor calls and holds the existing oracle convention fixed:

| Method | Current mean regret | Literal-anchor mean regret |
|---|---:|---:|
| B0 | 4.181818 | 4.181818 |
| B1 | 1.000000 | 1.000000 |
| B2 | 3.695455 | 3.468182 |
| B3 | 5.890909 | 2.636364 |
| B4 | 3.354545 | 3.227273 |
| B5 | 1.395455 | 0.900000 |

The cost ranking changes. Hypothetical H2 permanent-cell literal-anchor regret CIs still favor B5, but are different: B5-B0 `[-5.1875,-4.8]`, B5-B4 `[-4.375,-3.675]`, B5-B3 `[-4.15,-3.3875]`. These are sensitivity calculations, not amended results. Retaining total failures as a separate recovery-cost metric is useful; naming it anchor attempts is misleading. A low anchor regret also does not mean task completion.

### Paper notes contain stale numbers

**FAILED:** `cat results/tables/overall.csv; rg -n ... paper/notes/results.md paper/notes/hypothesis.md` gives discrepancies:

| Quantity | Paper notes | Current saved/reproduced table |
|---|---:|---:|
| B3 regret | 5.868 | 5.891 |
| B3 loop rate | 0.891 | 0.895 |
| B3 tokens | 2903.645 | 2915.259 |
| B3 latency | 11.741 | 11.860 |
| B4 tokens | 2024.227 | 2024.977 |
| B4 latency | 4.780 | 4.788 |
| B5 regret | 1.391 | 1.395 |
| B5 loop rate | 0.345 | 0.350 |
| B5 tokens | 480.768 | 481.859 |
| B5 latency | 2.020 | 2.084 |

A3 verifies **478/857 B4 modify decisions** were no-ops, not the paper's 479/857. For non-PARAM failures with a recorded recovery decision, **718/790 = 90.9%** chose modify. The paper's sentence about “91% of modify decisions ... classified as modify” uses a circular denominator; it should state this denominator. Its “85-90% of B5 replan attempts” phrase actually corresponds to 17/20 and 18/20 episodes having invalid calls, not a measured fraction of replans.

### History comparison is confounded by added context

**VERIFIED risk:** `src/pfr/prompts.py:78-97` and B2/B4 method code show that B4 adds failure history, the current failure count, remaining budget and untried parameter values. B2 omits all of these. The raw +22.7-point correctness comparison is reproducible, but attributing it solely to history is not isolated by this design. A matched-budget/untried-values ablation would require a new experiment; its result is **UNVERIFIED**.

### Cache, seed and latency semantics

**VERIFIED:** A4 gives identical ST-F locations for `PYTHONHASHSEED=0,1,42`. ST-F uses a dedicated `random.Random` keyed by task/cell/seed; stub mode uses SHA256. No hash-randomization problem was found in these checks.

**VERIFIED:** A5 reconstructs prompts, schema, call-index seeds, cached outputs and plan evolution without invoking `LLMClient.call` or Ollama:

```text
CACHE_AUDIT model_requests 4504 unique_cache_keys 2336 missing 0 mismatches 0
```

Plans and mode decisions match logs; token and latency sums match. Identical requests across episodes reuse cache entries. This is deliberate reuse, not 4,504 independent model samples.

**VERIFIED risks from `src/pfr/llm.py`:** cache identity contains the model tag, messages, schema, seed and temperature, but not model digest, Ollama version or `num_ctx=4096`. An updated model under the same tag or changed context setting could reuse stale entries. `LLMClient` resets call-index seeds per episode, so task/method seeds are not independent. Cached latency is the original request latency, not cache-hit time or end-to-end episode duration. Internal parse retries are not separately costed or counted unless every retry fails. A4 confirms zero saved parse failures, but cannot establish zero internal retried parses. Actual inference determinism across hardware/Ollama versions is **UNVERIFIED**, because no new calls were allowed.

### Broken partial-line resume

**FAILED:** A4 creates a scratch JSONL with a half-written tail, invokes `load_done_ids` and appends a valid row with `log_episode`:

```text
RESUME resulting_lines ['{"episode_id":"broken"{"episode_id": "recovered"}']
RESUME parses False; appended record merged with partial tail
```

The loader ignores the partial row, but appending without repairing the final newline merges the next record into the corrupt line. Main logs are currently valid, so this reproduction does not imply they are damaged. Resume IDs also exclude configuration, prompt version and code hash; rerunning an existing output path after changing these silently skips matching IDs.

### Additional latent validation/termination risks

**VERIFIED code behavior:** A4 sends a malformed target pick under TR-T1; the fault layer returns EXEC_TRANSIENT and increments its counter before Env validates the call. That consumes a transient attempt despite an invalid call. Current observed invalid calls are all places, so this specific masking case was not found in the main data. Validate skill calls before fault interception if this behavior is unintended.

**VERIFIED code behavior:** REPLAN_SCHEMA has no `minItems`, and the runner replaces the remaining plan with an empty list when output is empty or parsing fails. Outcome then becomes `incomplete` unless the goal happens to be satisfied. A4 finds **zero main episodes ending immediately on a replan decision**, so this is latent rather than an observed empty-plan bug. Malformed non-list output is also not independently validated after parsing.

**VERIFIED boundary behavior:** the runner terminates at `n_fail >= 8`, before asking the policy for an eighth-failure response. An already successful anchor can make the global-failure-based “attempts” equal 9. This is not an execution-loop off-by-one against the configured maximum of eight failures. `loop` is a composite of cap termination or three identical failed calls; it is not a measure of endless execution.

**VERIFIED statistical implementation; UNVERIFIED robustness:** paired bootstrap matches `(task,cell,seed)` and uses 10,000 resamples with alpha `0.05/3`. It resamples task-cell rows, not task clusters, despite cells sharing tasks and model requests sharing cached outputs. Conditional inference under that resampling scheme reproduces; task-cluster intervals and model-seed uncertainty were not evaluated. Supplying no input paths to either analysis script mixes all raw JSONL files, including pilot and pre-fix rows. Explicit current-log paths were used here, avoiding that issue. Multiple models would also be pooled because model is absent from the pairing index. These are risks for future analysis, not mismatches in this explicit single-model audit.

## F. Ranked findings, proposed fixes and result impact

Every evidence ID below refers to commands and output quoted above. Severity ranks research impact, not security risk.

| Rank | Severity | Finding and evidence | Proposed fix | Changes results? |
|---|---|---|---|---|
| 1 | High | Schema-valid omitted locations yield 720 executed invalid calls; A1/A3/A5 | Skill-specific required arguments, validation before execution, explicit parse/validation-failure policy | Yes, new behavioral experiment; preserve original data |
| 2 | High | Literal anchor attempts disagree in 215 episodes; A1/A6 | Separate anchor attempts from total recovery failures; retain both with explicit oracle convention | Changes cost tables/CIs; existing traces suffice for current-data correction |
| 3 | High | “Purely autonomous” metric includes human escalation, and zero-success causal claims overreach; A1/A3 | Name formulas explicitly; report autonomous vs assisted success; narrow claims about repaired-schema behavior | Presentation/derived metrics change; no inference rerun needed |
| 4 | High | B4/B2 adds budget/untried context along with history; prompt source | Narrow history claim or add a matched-context ablation | Text-only correction needs no rerun; causal ablation requires new runs |
| 5 | Medium | Oracle F=2 is not an unrestricted clairvoyant minimum; A3 | Define forced initial attempt, or adopt a different baseline transparently | Wording only, or derived regret values; no current-data inference needed |
| 6 | Medium | Stale paper numbers and empty bibliography; A3/source comparison | Refresh prose from current tables; resolve bibliography and complete manuscript | No model-result change |
| 7 | Medium | Partial-tail resume corrupts appended record; A4 | Detect/truncate or quarantine incomplete tail before resume, in a new output stream | No change to presently valid results |
| 8 | Medium | Replay guards only codes; A1 mutation check | Check result detail, attempt order, final goal/outcome and relevant metrics | No experiment change; stronger validation |
| 9 | Medium | Model/cache identity and provenance incomplete; llm source/A5 | Include model digest and inference options, record run/config/code identities and cache hits | Prevents stale reuse; a changed model/options needs new comparable runs |
| 10 | Medium | Dependency declarations and pilot config do not describe a standalone/current reproduction; fresh install/A6 | Declare dependencies; distinguish pilot stages and save exact config/environment | No behavioral results change |
| 11 | Medium | Row bootstrap dependence and one seed limit conclusions; analysis source/A5 | Add task-cluster sensitivity and future independent seeds | New CIs may change; added seeds require new experiments |
| 12 | Low to medium | Fault masks malformed calls, empty replans are accepted, implicit raw-file glob pools datasets; A4/source | Validate calls and replans; require explicit dataset selection | Latent behavior fixes require separate runs if evaluated; current table path was safe |

### What is solid

**VERIFIED, commands A1/A2/A5 and test commands:** all 1320 expected IDs exist once; all saved result codes/details and reconstructed final goals agree with current code; saved metric fields agree with that implementation; all recorded cached request plans and costs reconcile; both current and archived hypothesis tables independently reproduce; no stored interval changed across the ST-F fix; every current CSV and main figure reproduces byte-for-byte; both working-tree and fresh-clone suites pass 384 tests; the configured tasks have no remaining goal-at-t=0 cases and all labeled-solvable task-cell pairs have constructive solutions.

### What would need rerunning after approved fixes

The following counts are derived from existing traces, not forecasts of repaired behavior. No reruns were started.

1. **Replan-schema-only repair:** the minimum trace-exposed set is **342 episodes**: B3 200, B5 80, B2 40, B4 22. These are all episodes containing a replan decision, not only the 153 episodes with executed invalid calls. A validation change can affect outputs that were never reached in the old trace. Preserve the other 978 old rows only if all other prompts, config and behavior are held fixed and the new dataset's provenance explicitly marks reused rows. For a simpler complete LLM-method comparison, run **800 faulted episodes** across B2-B5 (20 tasks x 10 non-NONE cells x 4 methods), with the 80 clean LLM-method episodes and 440 B0/B1 episodes reused or separately executed without inference. A complete six-method dataset is **1320 rows**.
2. **ST-F/PRE-F-focused schema sensitivity:** **160 episodes** (20 tasks x 2 cells x 4 LLM methods). This diagnoses these cells but does not repair the main B3 comparison, since malformed calls also occur in transient and parameter cells.
3. **Literal anchor-count metric and oracle wording:** **0 inference episodes**. Recompute from existing steps into a new derived directory, with an amendment explaining the metric. This changes cost outputs, not saved task outcomes.
4. **Autonomous split, stale prose, replay guard, packaging and resume fixes:** **0 current-data inference episodes**, unless another behavior change is included.
5. **Matched-context B2 history ablation:** a new B2 variant over **220 episodes**, or 200 faulted episodes plus 20 clean rows. If B4 is also changed, **440 total episodes**. Do not present the existing B4/B2 difference as an isolated history effect.
6. **Different model/version or new independent seed:** rerun the full comparison under that setting. **1320 rows per seed**, including **800 potentially LLM-using fault episodes** under the existing method design.

Timing evidence: A1 sums saved historical request latencies. The 342 replan-exposed episodes total **3889.25 seconds, 64.8 minutes**; the 160 ST-F/PRE-F episodes total **1331.39 seconds, 22.2 minutes**; the 800 non-NONE LLM-method episodes total **5442.43 seconds, 90.7 minutes** (the 80 NONE episodes have zero calls). A new B2 variant has the current B2 historical reference of **1321.35 seconds, 22.0 minutes** for 220 episodes.

**UNVERIFIED estimates:** repaired behavior can change call counts, token lengths and parsing retries; cached latency is not actual rerun wall time. Suggested planning allowances are about **1-2 hours** for the 342-episode schema set, **25-60 minutes** for the focused 160, **1.5-3 hours** for the complete 800 faulted LLM set, and **25-60 minutes** for a 220-row B2 ablation. These ranges are judgment-based allowances anchored to the recorded totals, not measured runtimes. Before any inference, confirm the exact approved scope and time budget as requested.

Stop point: Phase 1 is complete. No proposed fix has been applied.

## Appendix A. Complete tracked-file inventory plus checked runbook/timing candidates

Command A1, using `git ls-files` and filesystem existence checks. EXISTS is VERIFIED existence; MISSING is FAILED existence at that path. For unspecified timing filenames and optional docs fallback paths, MISSING means only that the checked candidate is absent.

```text
EXISTS README.md
MISSING RUNBOOK_7DAY.md
MISSING RUNBOOK_DAY8.md
EXISTS analysis/make_figures.py
EXISTS analysis/summarize.py
EXISTS configs/main.yaml
EXISTS configs/pilot.yaml
EXISTS configs/policy.yaml
MISSING configs/timing.yaml
MISSING docs/RUNBOOK_7DAY.md
MISSING docs/RUNBOOK_DAY8.md
EXISTS figures/fig1_correct_heatmap.png
EXISTS figures/fig2_regret_by_regime.png
EXISTS figures/fig3_decisions.png
EXISTS figures/fig4_tokens_vs_correct.png
EXISTS figures/replay_150.png
EXISTS figures/replay_400.png
EXISTS figures/replay_700.png
EXISTS figures/replay_contrast.png
EXISTS figures/t06_PAR-F_B0_fail.png
EXISTS figures/t06_PAR-F_B0_final.png
EXISTS figures/t06_PAR-F_B5_fail.png
EXISTS figures/t06_PAR-F_B5_final.png
EXISTS paper/claim.md
MISSING paper/competitors.md
MISSING paper/course.md
MISSING paper/notes/CAPE.md
MISSING paper/notes/FRAMES.md
MISSING paper/notes/Graph_Harness.md
MISSING paper/notes/Reflective_Test_Time_Planning.md
MISSING paper/notes/Retry_Switch_Abstain.md
MISSING paper/notes/Self_Healing_Orchestrators.md
MISSING paper/notes/TOOL_MAZE.md
MISSING paper/notes/YALE.md
MISSING paper/notes/_template.md
MISSING paper/notes/faults.md
EXISTS paper/notes/hypothesis.md
EXISTS paper/notes/method.md
EXISTS paper/notes/results.md
EXISTS paper/notes/setup.md
EXISTS paper/outline.md
EXISTS paper/prereg.md
EXISTS paper/refs.bib
EXISTS pyproject.toml
EXISTS requirements-viz.txt
EXISTS requirements.txt
EXISTS results/demo/reel.mp4
EXISTS results/demo/t06_PAR-F_B0.mp4
EXISTS results/demo/t06_PAR-F_B5.mp4
EXISTS results/meta.txt
EXISTS results/raw/pilot.jsonl
EXISTS results/raw/qwen.jsonl
EXISTS results/raw/qwen_pre_fix.jsonl
EXISTS results/tables/by_group.csv
EXISTS results/tables/correct_by_cell.csv
EXISTS results/tables/hypotheses.csv
EXISTS results/tables/overall.csv
EXISTS results/tables/st_f_sensitivity.csv
EXISTS scripts/bench.py
EXISTS scripts/check_llm.py
EXISTS scripts/estimate_hours.py
EXISTS scripts/make_reel.py
EXISTS scripts/replay.py
EXISTS scripts/rerun_st_f.py
EXISTS scripts/run_main.sh
EXISTS src/pfr/__init__.py
EXISTS src/pfr/core.py
EXISTS src/pfr/env.py
EXISTS src/pfr/faults.py
EXISTS src/pfr/llm.py
EXISTS src/pfr/logging_utils.py
EXISTS src/pfr/methods/__init__.py
EXISTS src/pfr/methods/b0_retry.py
EXISTS src/pfr/methods/b1_maxretry.py
EXISTS src/pfr/methods/b2_nohistory.py
EXISTS src/pfr/methods/b3_replan.py
EXISTS src/pfr/methods/b4_llm_history.py
EXISTS src/pfr/methods/b5_policy.py
EXISTS src/pfr/prompts.py
EXISTS src/pfr/runner.py
EXISTS src/pfr/stub_llm.py
EXISTS src/pfr/tasks.py
EXISTS src/pfr/viz/__init__.py
EXISTS src/pfr/viz/play.py
EXISTS src/pfr/viz/scene.py
EXISTS src/pfr/viz/state.py
EXISTS tests/test_env.py
EXISTS tests/test_faults.py
EXISTS tests/test_methods.py
EXISTS tests/test_runner.py
EXISTS tests/test_viz_scene.py
EXISTS tests/test_viz_state.py
```

Additional untracked files verified by `rg --files`: `run_tests.sh`, `paper/Closest_papers.md`, and these files under `paper/notes/Related work_Literature survey/`: CAPE.md, FRAMES.md, Graph_Harness.md, Reflective_Test_Time_Planning.md, Retry_Switch_Abstain.md, Self_Healing_Orchestrators.md, TOOL_MAZE.md, YALE.md, _template.md, faults.md. A checkout of HEAD does not contain these untracked additions.

## Appendix B. Data preservation checks

Command: `sha256sum results/raw/qwen.jsonl results/raw/qwen_pre_fix.jsonl results/tables/hypotheses.csv`. A3 and the end-of-audit shell command produced identical hashes:

```text
a0a60376c6b3f1cb707387fd72f97836b7b65622c7292ea2d41670973d6e7fe7  results/raw/qwen.jsonl
4e78851fe8a8b70c1611e21dd276f1b8e3f448433cf78cf7e48fd4de5f350e56  results/raw/qwen_pre_fix.jsonl
4e7ca3ee520764f61b6f4e48b894d14778c6ad2f5c6000c01ff49bfe58d4bcf3  results/tables/hypotheses.csv
```

Working-tree status at the end matches the initial status. Scratch products remain separate from the repository. The complete evidence scripts are available beside this report for inspection and repeat execution.
