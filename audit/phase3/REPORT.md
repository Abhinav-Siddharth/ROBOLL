# Phase 3 steps 1–2: execution report

Both steps completed locally, without inference or Ollama calls. The user's later “finish full prompt” instruction superseded the pauses between steps. Tests and scratch reproduction ran with `PYTHONPATH=""` and the venv Python. Raw logs, frozen tables, all existing figures, primary analysis, tasks and policy were preserved. New analyses are exploratory and do not amend H1–H4.

## Step 1: freeze, reproduction and backup

### 1a–b: clean starting checkout and tags — VERIFIED

Commands:

```bash
git status --porcelain=v1
git tag -a v2-primary -m 'v2 primary dataset, 425 tests, all gates complete' HEAD
git rev-parse v2-primary 'v2-primary^{commit}' pre-phase2 'pre-phase2^{commit}'
```

Starting status output: empty (clean). Tag output, in that order:

```text
0eb9fc62cf253fac761157e057fe12b98b17eeda
8cfd7daedafc4d6a4558befe588bd2e927f99c6c
1eb8c3c5b3f355e41ae0e5fff17a7f17bab618a1
0f6cd408c40cc13d6effb386672e28736726d71b
```

The first/third hashes are annotated tag objects; the second/fourth are commits. The required message describes the completed Phase 2 snapshot with 425 tests; Phase 3 tools live in later commits.

### 1c: SHA256 inventory — VERIFIED

`results/MANIFEST.sha256` has **43 lines**, covering every file in raw, tables, derived_v1 and v2. It excludes the new exploratory directory by design. The verifier detects changed, missing and extra files; fixture tests also reject duplicate manifest entries.

Command: `PYTHONPATH="" .venv/bin/python scripts/verify_manifest.py`

```text
MANIFEST OK: 43 files; no missing, extra, or changed files
```

Targeted command: `PYTHONPATH="" .venv/bin/python -m pytest tests/test_manifest.py -q -p no:cacheprovider`

```text
6 passed in 0.05s
```

### 1d: exact environment lock and metadata — VERIFIED within the recorded scope

Command: `PYTHONPATH="" .venv/bin/python -m pip freeze > requirements.lock`

The file retains the exact editable source path emitted by pip. REPRODUCE.md filters that one line before installing dependencies, then installs the clean clone itself. The lock is not rewritten to pretend it was portable originally.

Local Python/OS collection produced:

```text
Python: 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]
OS: Linux-7.1.5-76070105-generic-x86_64-with-glibc2.39
Recorded Ollama: 0.40.0
Model: qwen2.5:7b
Digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
```

Ollama version/name/digest are retained from the timestamped Phase 2 snapshot. **Current Ollama state is unknown**, explicitly recorded; no server or binary was called. The JSON metadata remains parseable and its original options stay intact. Targeted provenance/environment tests: `2 passed in 0.01s` (one preexisting, one new).

### 1e: clean-clone installation, tests, complete artifact rebuild and replay — VERIFIED

Exact runnable commands are in [REPRODUCE.md](../../REPRODUCE.md). They were run in `/tmp/pfr-phase3-clean`, bootstrapping a fresh venv, installing the locked third-party packages and then the clone editable. `install.txt` and `editable_install.txt` preserve pip output. Final dependency check:

```text
No broken requirements found.
```

At the freeze-tools commit, the clean clone reported:

```text
436 passed in 3.26s
```

One premature test attempt started before editable installation completed and failed with `14 errors in 0.27s` (missing pfr imports). It is not counted as verification. Installation finished, then the ordered rerun above passed. The final clone, updated to the exploratory commits, reported:

```text
460 passed in 3.98s
```

Command:

```bash
PYTHONPATH="" .venv/bin/python scripts/rebuild_artifacts.py --scratch /tmp/pfr-phase3-rebuilt
```

Final output:

```text
ARTIFACT DIFF: 50 files compared; 0 different
```

This rebuilt every archived table, derived-v1 file, v2 table/derived/comparison/caption file and all 18 PNGs, including eight replay stills from freshly rendered videos. Statistical plots and video-frame stills are byte-identical to committed artifacts on this locked local environment. The raw logs were read only. Video frame counts were 3721, 735 and 532; videos themselves were scratch intermediates, not substituted for committed demos. Full stdout is in `rebuild.txt`.

Single-episode command:

```bash
PYTHONPATH="" .venv/bin/python scripts/replay.py --jsonl results/raw/qwen_v2.jsonl --task t06 --cell PAR-F --method B5 --check
```

Output:

```text
replaying qwen2.5:7b|B5|t06|PAR-F|0 (8 steps)
max IK position error over the replay: 0.01 cm
```

The clean clone's `git status --porcelain=v1` output is empty. Replay is symbolic/kinematic verification, not proof of contact-physics execution.

### 1f: complete local git bundle — VERIFIED

Commands actually run:

```bash
git bundle create /tmp/pfr-v2-primary.bundle --all
git bundle verify /tmp/pfr-v2-primary.bundle
```

Verification output:

```text
/tmp/pfr-v2-primary.bundle is okay
The bundle records a complete history.
The bundle uses this hash algorithm: sha1
```

`initial_bundle_verify.txt` records verification at code/test commit `cc94e307f3211325e18b4291a2e5ac7391a662d3`. After this evidence commit the bundle is refreshed with `--all` and verified again, so the delivered bundle includes the evidence too. The final verification and SHA256 are printed in the session. No push was performed.

Commands for the user to push to a private repository they create (replace the literal placeholder):

```bash
git remote add private git@github.com:OWNER/PRIVATE-REPO.git
git push private HEAD:refs/heads/main
git push private refs/tags/pre-phase2 refs/tags/v2-primary
```

## Step 2: exploratory cost-aware analysis and claims

**Every number in this section and results/derived_v2/ is exploratory, defined after seeing the data.** V1 means corrected archive `qwen.jsonl`; `qwen_pre_fix.jsonl` remains the separate earlier ST-F archive. All statistics are computed from logs, not copied from paper notes. CIs use the original marginal alpha 0.05/3 (98.3333333% intervals), 10,000 draws and seed 0, without familywise control across this entire exploratory set.

### 2a: utility — VERIFIED as a derived calculation; exploratory

Command:

```bash
PYTHONPATH="" .venv/bin/python analysis/human_utility.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --out results/derived_v2
```

Output:

```text
exploratory, defined after seeing the data: 864 means, 2160 paired comparisons, 24 break-even rows
```

`utility_means.csv` gives each method's per-cell and overall mean with row and task-cluster CIs. `utility_comparisons.csv` gives paired differences and CIs. Every bootstrap resamples aligned task/cell/seed units across methods; whole-task resampling preserves the row-mean estimand. Every query is penalized, including queries in incorrect episodes. Per-episode values are in `utility_episodes.csv`.

Overall means:

| Version | Method | U(0.25) | U(0.5) | U(1.0) |
| --- | --- | --- | --- | --- |
| v1 | B0 | 0.363636 | 0.363636 | 0.363636 |
| v1 | B1 | 0.636364 | 0.636364 | 0.636364 |
| v1 | B2 | 0.454545 | 0.454545 | 0.454545 |
| v1 | B3 | 0.090909 | 0.090909 | 0.090909 |
| v1 | B4 | 0.625000 | 0.568182 | 0.454545 |
| v1 | B5 | 0.790909 | 0.768182 | 0.722727 |
| v2 | B0 | 0.363636 | 0.363636 | 0.363636 |
| v2 | B1 | 0.636364 | 0.636364 | 0.636364 |
| v2 | B2 | 0.454545 | 0.454545 | 0.454545 |
| v2 | B3 | 0.527273 | 0.527273 | 0.527273 |
| v2 | B4 | 0.647727 | 0.586364 | 0.463636 |
| v2 | B5 | 0.931818 | 0.909091 | 0.863636 |

B5-B4 overall difference is `delta_correct - c * delta_queries`. V1 intercept/slope are 0.131818/-0.136364, root -0.966667; v2 0.245455/-0.154545, root -1.588235. **Neither version has an overall break-even in [0,1].** `break_even.csv` separately records each cell, including cells with equality throughout the interval. Utility superiority is an overall statement; it is not true in every cell.

For v2, B5-B4 differences are 0.284091, 0.322727, 0.400000 at the three costs. Paired-row CIs are [0.217045,0.353409], [0.256818,0.388636], [0.318182,0.481818]; task-cluster CIs [0.218182,0.345455], [0.277273,0.363636], [0.363636,0.436364].

### 2b: Pareto data and figure — VERIFIED derived coordinates; exploratory

Command:

```bash
PYTHONPATH="" .venv/bin/python analysis/human_pareto.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --out results/derived_v2
```

Output: `exploratory, defined after seeing the data: 12 Pareto method/version rows; pareto.png written`.

`pareto.csv` and `pareto.png` plot mean total failed executions against correct termination with zero human queries. B1/B5 form the v1 empirical frontier; B5 dominates all other primary methods on these two v2 sample coordinates. These are observed coordinates, not a population dominance guarantee. The figure was opened and visually inspected.

### 2c: human involvement — VERIFIED decomposition; exploratory

Command:

```bash
PYTHONPATH="" .venv/bin/python analysis/human_terminations.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --out results/derived_v2
```

Output: `exploratory, defined after seeing the data: 192 termination/dependence rows; dependence describes observed human involvement, not a counterfactual effect`.

`human_terminations.csv` includes every method/cell/group plus overall, with counts, rates and fractions of raw_correct involving queries. Undefined fractions stay blank. V2 B4 has 156 correct outcomes: 103 zero-human, 15 assisted successes, 38 permanent escalations (53/156 = 33.9744% involve human help). V2 B5 has 210: 133 autonomous successes, 57 permanent abstentions, 20 permanent escalations (20/210 = 9.5238% involve human help). On permanent cells B1 abstains correctly in all 80 cases; B5 is not claimed highest on that permanent-only subset.

### 2d: claims table — VERIFIED calculations and executable policy checks; exploratory interpretation

Command:

```bash
PYTHONPATH="" .venv/bin/python analysis/claims_evidence.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --ablation results/raw/qwen_v2_ablation.jsonl --out results/derived_v2 --paper paper/claims_evidence.md
```

Output: `exploratory, defined after seeing the data: 11 claims checked; 408 freshly computed statistics; claims_evidence.md written`.

See `paper/claims_evidence.md` for supporting file/row, CIs, status and exact allowed wording for all seven requested claims and four unsupported readings of current notes/outline. `claims_statistics.csv`, `invalid_calls.csv` and `reference_policy_examples.csv` make the checks inspectable; `reviewed_notes.csv` records the reviewed source inventory.

- Claim 1 NOT SUPPORTED as written: v1 B3 invalid-call rate 610/3062 = 19.9216%; omissions are 610/1568 = 38.9031% of failure steps, not most. Exposure is 110/220 episodes and 110/200 incorrect episodes. Raw correctness is 20/220 in v1 and 116/220 in v2. A descriptive before/after change does not identify the number caused by omissions.
- Claim 2 SUPPORTED for observed overall correctness: B5 zero-human correct 190/220 = 86.3636%; row CI [80.4545%,91.8182%], cluster [83.1818%,89.0909%]. All five paired baseline differences have positive marginal lower bounds under both schemes.
- Claim 3 PARTIAL: B4-B2C has 48 additional correct outcomes on 200 faulted units; 47 of the net difference involves human queries (including assisted completion). Only one additional autonomous success; no equivalence or causal claim follows.
- Claim 4 SUPPORTED for preregistered T1/T2: B5-B3 +0.15, row CI [0.025,0.300], cluster [0,0.350].
- Claim 5 SUPPORTED descriptively: F-cell B5-B4 is -0.233333 in v1 versus +0.25 in v2; both schemes exclude zero in opposite directions.
- Claim 6 SUPPORTED for overall v2 and the three chosen costs, with positive paired marginal CIs against every primary baseline; not a universal cost/cell result.
- Claim 7 PARTIAL: deterministic history/count/budget/untried-aware mode selection, with LLM-generated modify/replan actions. Code-only lookup and deterministic end-to-end planning are not supported.

Unsupported readings include a literal “only current error” B2 prompt, history isolation from B4/B2, claiming all papers were fully read/all new analyses preregistered, and requiring all numbers to come from the old results/tables directory.

### 2e: fixture tests and final clean-clone check — VERIFIED

Test additions and counts:

| Item | New tests | Suite count after item |
| --- | --- | --- |
| 1c manifest | 6 | 431 |
| 1d environment | 1 | 432 |
| 1e rebuild helpers | 4 | 436 |
| 2a utility/paired bootstrap | 11 | 447 |
| 2b Pareto | 2 | 449 |
| 2c termination split | 3 | 452 |
| 2d claims/count ratios/policy | 7 | 459 |
| 2e additional output-safety fixture | 1 | 460 |

Fixtures have known answers for U with multiple queries, paired versus unpaired uncertainty, unequal-size task clusters, break-even absence/equality, Pareto dominance, zero-correct denominators, permanent classification, weighted failure ratios, and same-code/different-context decisions. Final source and clean clone both pass 460 tests.

Rebuilding all exploratory files and the claims Markdown in clean-clone scratch directories, with the exact commands in REPRODUCE.md, produced:

```text
EXPLORATORY DIFF: 14 files compared; 0 different []
```

Preservation/replay command: `PYTHONPATH="" .venv/bin/python scripts/verify_phase2.py`.

```text
VERIFIED: 19 protected v1 artifacts unchanged
VERIFIED: primary analysis, policy and tasks remain frozen
V2 {'rows': 1320, 'unique_ids': 1320, 'invalid_calls': 0, 'parse_failures': 0, 'replay_mismatches': 0}
Ablation {'rows': 200, 'unique_ids': 200, 'invalid_calls': 0, 'parse_failures': 0, 'replay_mismatches': 0}
VERIFIED: 800 new main episodes, 520 proven reused controls, 200 new ablation episodes
```

The “new episodes” wording is provenance of Phase 2 records; no new inference occurred in Phase 3.

## Solid, exploratory and unclaimed

Solid: local integrity checks, all logged symbolic replay checks, exact local artifact reproduction, passing source/clean-clone tests, and the arithmetic/decomposition computed from the archived logs. Exploratory: costs, utility comparisons, Pareto summaries and the post-data claims audit. The original primary analysis remains frozen.

I would not claim omissions caused most B3 failures, autonomous equivalence of B4/B2C, a code-only B5 policy, superiority in every cell/cost, proof that all literature was read, physical executability, real human-effort calibration, or generalization beyond this one-model/one-seed scripted benchmark. Current Ollama state and independent inference replication remain unverified.

Each code/data item has its own local commit. No data were silently replaced and no remote was contacted for publication.
