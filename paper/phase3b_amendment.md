# Phase 3b prospective amendment: seeds, second model, and diagnostic noise

Prepared at 2026-10-12T07:53:02Z (2026-10-12 13:23:02 Asia/Kolkata), after observing the archived v1/v2 results and before any Phase 3b inference. Baseline repository commit: `107434e18fa5cfff6bf270165854a972c8a9bf37`. This timestamp documents preparation, not approval or external registration. The amendment commit and its hash will be recorded before inference. No Phase 3b outcomes were used to select this design.

## Execution authorization

The user ended the Phase 3b instruction with "finish it all off and report." This direct authorization is interpreted as permission to complete the stated gate sequence without additional routine approval pauses. Gate diffs, checks and results will still be reported before dependent work. Failed stop rules, an incompatible second-model candidate, missing prerequisites or a methodological change still stop the affected work; this authorization does not waive those conditions. No inference has occurred before this amendment.

## Scope, prerequisites, and immutable artifacts

Phase 3b adds replication and diagnostic-code robustness measurements. It does not adopt the larger research roadmap. The private remote must contain the existing repository snapshot, and restoration into a fresh checkout must succeed before this amendment is committed. Document the remote visibility check, pushed commit/tag hashes, restored commit, and manifest verification. Do not publish the repository publicly.

Keep every existing `results/raw/*`, `results/v2/*`, table, and figure byte-for-byte unchanged. Existing raw logs are sources, never destinations. The new raw destinations are `results/raw/qwen_v3_seed1.jsonl`, `results/raw/qwen_v3_seed2.jsonl`, `results/raw/llama_v3_seed0.jsonl`, and separate `results/raw/qwen_v3_noise_p01.jsonl`, `qwen_v3_noise_p02.jsonl`, `qwen_v3_noise_p03.jsonl`. New derived outputs go only to `results/derived_v3/`; smoke and audit artifacts go under `audit/phase3b/`. Reject any destination that is an already-existing protected raw artifact. A resumed new batch must validate its own prior provenance before appending.

Do not retune or change `configs/policy.yaml`, `src/pfr/prompts.py` (including all schemas), `src/pfr/tasks.py`, fault-generation/transition semantics, temperature, context limit, maximum failures, or the archived primary analysis in `analysis/make_figures.py`. The frozen options are temperature 0.7, `num_ctx=4096`, maximum eight execution failures, and the existing schema-validation retry policy. New instrumentation and noise/seed/model plumbing may not add hints, alter plans, supply oracle corrections, or silently change fallbacks.

H1–H4 and all v1/v2 results retain their existing status. S1, M1, and N1 below are registered prospectively for Phase 3b, after inspection of v2. They are not independently conceived before the original experiment.

## A. Replication with seeds 1 and 2

Run the same 20 tasks, 11 cells and B0–B5: 1,320 episodes per seed, 2,640 new episodes in total. Execute B0/B1 and every NONE row through the harness; do not copy these for the new environment seeds.

Use the experimental seed for both `build_fault(task, cell, seed)` and `LLMClient(base_seed=seed)`. Preserve the existing logical-request seed rule `base_seed * 1000 + call_index`; backend parse/schema retries use `seed + 100003 * retry_index` as before. Record the environment seed and base LLM seed separately even when equal.

The existing generator uses the seed only to sample the ST-F alternate location. PAR, PRE, permanent conditions and transient duration are fixed by their existing definitions. Do not introduce new random parameters. Read-only construction before this amendment found that seed 1 changes the ST-F location for 13/20 tasks versus seed 0 and seed 2 changes 11/20; every other cell's fault definition is unchanged. Repeated parameter values across seeds are expected in a finite candidate set. This is joint fault-location/sampling-seed replication, not a factorial separation of those effects or three independently sampled task sets.

Before new inference, reproduce seed 0 using archived caches only. The backend must raise on any cache miss; no silent inference fallback is allowed. Compare all pre-existing episode payload fields with the archived v2 reference. New provenance, observed-evidence audit fields, wall-clock timestamps and cache-hit counters are not part of legacy payload equality. For the 520 reused controls, preserve their archived prompt-version label in the comparison. Clearly report any excluded provenance-only fields. Required p=0 regression coverage uses the exact 20 coordinates of the seed-smoke recipe below with seed replaced by 0; all are among the 800 newly generated v2 rows. The seed-0 reproduction check covers all 1,320 reference rows.

## B. Second model

Candidate: `llama3.1:8b`, seed 0. Before use, record the exact local model name, digest, quantization, manifest/download size, Ollama server/client versions, template hash and options. Verify download size from the provider and actual installed metadata, and verify that the chosen quantization/configuration can run on the available 8 GB GPU. Model name alone is not a frozen identity. Do not claim measured VRAM use, download size, or parse reliability before checking it.

Use the frozen prompts, schema, policy, task/fault definitions and options. Run `scripts/check_llm.py` in its own fresh namespace: 20 inputs per schema, 60 logical calls total. Require zero bad outputs and zero JSON/schema failures, including any recovered retry, before proceeding. Existing script output reports only exhausted failures, so expose request-level diagnostics alongside its unchanged prompt/schema checks. If this candidate fails compatibility or capacity checks, propose a specific alternative and stop for approval; do not try successive models until one produces favorable task scores.

Run B2–B5 on 20 tasks × 10 faulted cells = 800 new episodes. Assemble a 1,320-row second-model dataset only after proving all 520 B0/B1/NONE source rows model-independent by fresh deterministic execution with a client that raises if invoked. Change destination model/episode identifiers explicitly; preserve source model, episode ID, path, SHA256 and verification commit as provenance. Mark reused rows and never count them as new model inference. Do not copy any row with model calls.

## C. Consistent wrong-code evidence

Run Qwen seed 0 on all 200 faulted task/cell pairs for B2, B4 and B5 at p ∈ {0.1, 0.2, 0.3}: 600 episodes per p and 1,800 total. B0/B1 are excluded because their decisions do not read the code. B3 is outside this specified noise comparison. The p=0 reference uses the matching B2/B4/B5 faulted rows already in v2, not a newly sampled baseline.

On each real failed execution, independently determine whether to corrupt the evidence with probability p. The four eligible failure codes, in this fixed order, are:

1. `EXEC_TRANSIENT`
2. `PARAM_MISMATCH`
3. `STATE_MISMATCH`
4. `PRECOND_UNMET`

`OK` is never a candidate. When corrupted, draw uniformly from the other three codes and pair it with this fixed canonical detail table:

| Observed code | Exact canonical detail |
| --- | --- |
| `EXEC_TRANSIENT` | `execution error: motion timeout` |
| `PARAM_MISMATCH` | `parameter invalid for this skill execution` |
| `STATE_MISMATCH` | `observed state does not match the expected state` |
| `PRECOND_UNMET` | `precondition for this skill execution is not satisfied` |

These generic details depend only on the observed code. They may not contain the true fault kind, hidden fix, required prerequisite location, or original detail. On uncorrupted failures, preserve the original code, detail and result exactly. In particular, p=0 is a strict no-op; it does not canonicalize normal evidence. The manipulation is consistent wrong diagnosis text, not a wrong code paired with the true detail. The latter conflicting-evidence variant is out of scope.

Define `step_index` as the one-based executed-attempt index already logged in `steps[].attempt`, counting successful and failed executions. Construct an event RNG with a stable, explicitly serialized key `(task_id, cell, environment_seed, step_index, p)`, with p represented as the integer percentage 10/20/30. Use a versioned SHA256 key encoding rather than Python's process-dependent `hash()`. Draw one Bernoulli uniform and, if needed, a uniform index into the fixed code list with the true code removed. The key excludes the method, model sampling seed, time, request count and cache state. Test determinism across separate processes. The inclusion of p means the three noise levels have separate rather than nested corruption realizations. Methods share the random event key at equal task/cell/attempt coordinates; after their actions diverge, equal attempt indices need not describe identical physical events.

Keep execution truth and observed evidence separate. The environment, fault counters, skill validation, actual results, outcomes, human intervention behavior and metric labels use execution truth. Logged legacy `steps[].code` and `detail` remain true values for state reconstruction. Log the displayed code/detail, corruption flag and RNG identity separately. Feed the displayed result into mode choice, modify and replan calls. Save the displayed error in method-visible history, so B4 and B5 cannot recover the true diagnosis from past entries. B5 counts displayed codes through the unchanged `Ctx.count_code` behavior. Record evidence even for cutoff failures, while making no additional method call after cutoff.

The unchanged replan prompt still receives the true visible world observation; action identities, untried parameter hints and failure budgets also retain their original definitions. Thus this tests diagnostic code/detail robustness with the existing observation channel, not unreliable perception in every modality. Wrong diagnoses may change decisions and resulting trajectories. The causal environment invariance test holds the scripted actions and human interventions fixed and compares environment/fault states with and without the observation transformation.

## Diagnosis withheld: explicitly excluded

No unknown/withheld code is generated in Phase 3b. Do not edit policy.yaml or the B5 implementation. The current B5 implementation already escalates at the total failure budget and otherwise abstains on an unrecognized code; the typed Result currently permits only the four known failure codes and OK. A future withheld-diagnosis experiment would explicitly expose an UNKNOWN representation and preregister the existing effective fallback: escalate when the unchanged total failure budget is reached, otherwise abstain immediately. That experiment could strongly disadvantage B5 and would need its own amendment; it is not run here.

## Prospective hypotheses and decision criteria

`no_human_correct = bool(correct) and human_queries == 0`, matching the existing derived definition. It includes autonomous completion of solvable tasks and correct abstention on permanent faults; it is not a task-completion rate. Always report autonomous success and permanent abstention separately as descriptive decompositions.

- **S1:** B5's no-human correctness is strictly above B2, B3 and B4 in each of seeds 0, 1 and 2. Evaluate all 220 task/cell rows per method per seed. “Holds” means each of the nine paired point differences is >0; a tie or negative value does not satisfy the statement. This point-order criterion does not require CI exclusion of zero and does not establish all-seed population superiority.
- **M1:** B5 minus B4 no-human correctness is >0 on the second model, seed 0, using its assembled 220 rows/method. Report the point difference and both confidence intervals. Positive point difference with an interval including zero supports only the observed directional statement, not a significant positive population difference.
- **N1:** Report B5 and B4 faulted-only no-human correctness at p=0,0.1,0.2,0.3, their paired difference d(p)=B5−B4, and whether a sampled crossover occurs. There is no directional prediction about a crossover. Include B2 as the preregistered comparison curve.

For N1, publish every sampled d(p). A strictly opposite sign at adjacent tested p values defines a crossover bracket; report all such brackets. An exact zero at a sampled p is an observed tie, identified separately, and a positive-to-negative sign change across a tie is reported as such. If no sign reversal occurs, write “No crossover was observed at the tested noise levels in [0,0.3]”; do not claim none exists between measurements. Optional linear interpolation within a bracket is explicitly exploratory and not an observed p*. Do not select only the most favorable crossing or extend the p grid after seeing results under this amendment.

Per-seed and per-model summaries are prespecified. Pooled Qwen summaries weight all three seeds equally, with balanced task/cell counts. Do not pool the second model into a single model-generalization score. Post-hoc cell choices, utility costs, subgroup findings or alternative crossover definitions remain labeled exploratory.

## Uncertainty and analysis freeze

Use the current numerical convention: two-sided percentile bootstrap confidence `1 - 0.05/3 = 0.9833333333333333` (98.3333%), 10,000 resamples, NumPy RNG seed 0. This continues the prior interval level but does not claim simultaneous familywise coverage across every new seed/model/cell/p comparison. The S1 decision remains the explicitly frozen point-order rule.

For paired-row resampling, assemble complete matched task/cell vectors across methods and, for noise, across all four p levels. Draw the same row indices for every method and p in a replicate. For a single seed there are 220 all-cell units or 200 faulted units, as specified. Pooled seed analysis has 660 matched task/cell/seed units. Missing matches or duplicate units are structural errors, not grounds for silently dropping rows.

For task-cluster sensitivity, sample the 20 task IDs with replacement and retain all corresponding cells, methods, p levels and, in pooled analyses, all three seeds. Preserve the row-mean estimand by resampling task sums and counts together. For per-cell analyses, the same task IDs remain the clusters. Row and cluster intervals are both reported, with no choice between them based on favorability. They quantify task/unit sampling under this benchmark; three fixed seeds are not enough to claim a well-estimated distribution over possible seeds or models.

Primary H1–H4 analysis code stays unchanged. Implement separate Phase 3b analysis scripts with hand-built fixtures. Before Gate 3, add the frozen amendment, machine-readable S1/M1/N1 specification, Phase 3b analysis scripts and their supporting metric/bootstrap modules to `results/MANIFEST.sha256`; include existing frozen prompt/schema, policy, tasks, fault and primary-analysis files as explicit source entries. Extend manifest verification to support these explicit sources while preserving exact existing artifact hashes and inventory checks. Hash analysis dependencies, not merely a CLI wrapper. Record the manifest hash and frozen-source commit in batch provenance. No outcome-dependent edits to these frozen files; a needed methodological change requires a disclosed amendment and new approval before resuming.

## Gate 1: no inference

Commit this amendment, show its diff and wait for approval before executing any inference. Implement plumbing only within authorized scope, in a subsequent commit, with tests for:

1. Predetermined p=0 reference rows match legacy v2 payloads exactly; archived seed-0 reproduction is cache-only.
2. Fault-seed and LLM-seed wiring preserve seed 0 and change seeded parameters/request seeds where expected.
3. Identical scripted actions and interventions produce identical true environment and fault states with and without noise.
4. Noise draws are deterministic, never show the true code when selected, use canonical matching details, and do not depend on the LLM sampling seed.
5. Method-visible history and modify/replan inputs contain observed evidence only, while replay still checks true code/detail and final outcome.
6. Policy/schema/prompt hashes remain unchanged; unknown diagnosis is never generated.
7. Request-level stop monitoring, output protection, model provenance, unique noise IDs and manifest-source checks fail appropriately on small mutation fixtures.

Report the complete test count with quoted output. Unit tests use synthetic clients and do not contact Ollama. Any cache-only failure is a blocked reproduction result, never permission to infer.

## Gate 2: approved smoke inference

After separate approval, check the model identity, capacity and second-model schema compatibility described above. Smoke runs total 90 episodes: 20 Qwen seed-1 episodes, 50 second-model seed-0 episodes, and 20 Qwen seed-0 p=0.2 episodes. Schema-check requests are additional and separately reported.

Freeze smoke selection by this deterministic coordinate recipe before any output is observed. Let T be t01…t20, C be the ten faulted cells in existing CELLS order, A=[B2,B3,B4,B5], and N=[B2,B4,B5]; indexing starts at zero:

- Seed smoke: for i=0…19, `(T[i], C[i mod 10], A[i mod 4], seed=1)`.
- Model smoke: for r=0…4 and j=0…9, `(T[(j+4r) mod 20], C[j], A[(j+r) mod 4], seed=0)`.
- Noise smoke: for i=0…19, `(T[i], C[i mod 10], N[i mod 3], seed=0, p=0.2)`.

These produce 20/50/20 unique coordinates. Every faulted cell appears 2/5/2 times. Method counts are 5/5/5/5 for seed smoke, 13/13/12/12 for model smoke, and 7/7/6 for noise smoke. Each design covers all 20 tasks. No smoke row is part of the final dataset: rerun those coordinates in the independently namespaced full batches after approval.

Require cold-cache episodes, not merely an empty cache at the beginning of a batch. Use a fresh per-episode smoke namespace or disable cache reads while retaining writes for audit; every episode must record zero cache hits. Do not import v2 caches into smoke namespaces. Time actual wall duration, including retries and model-loading effects; report first-load effects separately without excluding them from total wall time. Record logical calls, backend attempts, JSON/schema failures, retries, invalid calls, cache hits, elapsed seconds and seconds/episode.

Project each full design from these cold measurements with explicitly disclosed sampling uncertainty. Seed projections separate 800 potentially model-using episodes per seed from 520 deterministic harness executions, whose cost can be measured without inference. Model projection covers 800 new episodes plus deterministic reuse verification. Noise projections use equal method weighting and state that p=0.2 timing is an unverified approximation for p=0.1 and p=0.3. Do not substitute archived cached latencies. Flag Qwen throughput materially slower than the user's approximate 3–5 s/episode expectation; do not treat that expectation as a verified hardware promise.

Report the smoke results and projected totals, then stop for approval before Gate 3. Smoke correctness is diagnostic, not an opportunity to retune prompts, select tasks or change thresholds.

## Stop rules and request accounting

Abort the active batch if any replay mismatch occurs, if any executed skill call is invalid, or if the cumulative backend JSON/schema failure rate exceeds 1%. Numerator: backend responses that fail JSON decoding or the frozen schema. Denominator: completed backend response attempts, including retries; cache reads and deterministic episodes do not enter it. Count failed attempts even when a later retry succeeds. Test the >1% boundary exactly. Under this literal cumulative rule, one early malformed response may stop the batch. Do not add an unregistered grace period.

Existing parse retries remain unchanged when the threshold permits continuation. An exhausted logical request also stops the batch: retain its evidence and do not silently accept fallback benchmark outcomes. Transport/server failures stop the batch separately and are reported without classifying them as task failures. Validate each completed episode's true replay and skill calls before proceeding. Keep every partial batch and error record; fixes or restarts require disclosure and a new run namespace, not erasure of adverse records.

## Gate 3: full batches, sequential checkpoints

After approval run, in order: Qwen seed 1; Qwen seed 2; the second model; noise p=0.1; noise p=0.2; noise p=0.3. Use a distinct namespace for each new batch/run, including distinct smoke and schema-check namespaces. Append a deterministic episode suffix to each batch namespace, including full runs, to prevent responses or timing metadata from being overwritten by coincident requests from different episodes. Schema checks likewise isolate their 20 seed clients. Cold smoke additionally disables cache reads. A resumed run may reuse only its validated own namespace. Archived seed-0 verification is a read-only exception that intentionally reads the old namespaces; it is not a new inference run.

After each batch verify the exact ID grid, absence of duplicates, zero invalid skill calls, request-level failure statistics, full true-state replay, observed-evidence regeneration, and cache-only response replay without contacting the backend. Include noise p/run identity in dataset coordinates or validate it as part of the full key so rows from different p levels cannot collide. Record immutable model identity, server/options, code commit, amendment/source hashes, namespace, seed definitions, reused status, source hashes and actual batch wall time. Report these checks before starting the next batch, and honor the user's gate approval requirements.

There are 5,240 new full-run episode executions: 2,640 seeds + 800 second-model + 1,800 noise. The assembled second-model file includes 520 proven reused rows, making 5,760 rows across the new full-run files. The 90 smoke episodes and 60 second-model compatibility logical calls are additional. No runtime estimate is VERIFIED until measured.

## Gate 4 and final reporting

Without inference, create `results/derived_v3/` outputs for per-seed and equal-seed pooled summaries, model comparisons, noise curves and paired row/task-cluster intervals, crossover brackets/ties, and all prespecified outcome decompositions. Write new figures only inside this new directory. Add S1/M1/N1 evidence rows to `paper/claims_evidence.md`, stating the exact metric, denominator, version, model/seed/noise scope, interval scheme and allowed wording. Preserve historical claims and their existing labels; mark additional unregistered analyses exploratory.

Refresh the manifest without changing the previously frozen source or artifact hashes, include all completed new outputs, and verify it. Run the full suite and a clean-clone reproduction with `PYTHONPATH=""` and the venv Python. Report exact quoted outputs and test counts. Create `v3-primary` only after the stated gates, integrity checks, test suite and clean-clone checks succeed. If work is blocked or a batch stops, report partial status and do not apply a completion tag.

Publish an honest conclusion even if S1/M1 fail or N1 finds no crossover. B5 remaining at or above B4 supports a reference-policy robustness description only over tested conditions. A crossover motivates later belief-based work but does not authorize it here. No physical-robot generalization, broad model-generalization, causal benefit of history alone, or full-range noise guarantee follows from this design.
