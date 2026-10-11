# Phase 2 gate report

Gate 0 VERIFIED: clean status and pre-phase2 resolves to 0f6cd408c40cc13d6effb386672e28736726d71b.

The user authorized completing all gates on 2026-10-11, including inference after the committed amendment and validation gate. Original datasets, tables and figures are protected by protected_sha256.json. Test transcripts record commands, output and exit status for each item.
## Gate 1a VERIFIED

Before: 2 failed (missing derived metrics). After: 386 passed. Literal anchor calls, total failure cost and legacy regret are separate. Outputs: results/derived_v1/; runner.py is unchanged. No inference. See gate1a-before.txt, gate1a-after.txt, gate1a-derived.txt.

## Gate 1b VERIFIED

Before: 2 failed, 2 passed. After: 388 passed. Success and three correct-termination definitions are explicitly named, including the definition retaining permanent human escalation. No inference. See gate1b transcripts and results/derived_v1/outcomes_*.csv.

## Gate 1c VERIFIED

Before: 2 failed, 4 passed. After: 390 passed. Task-cluster bootstrap pairs first and keeps every task cell together, using the original hypothesis masks and CSV layout. Primary analysis/make_figures.py is unchanged. See hypotheses_task_cluster.csv and gate1c transcripts.

## Gate 1d VERIFIED

Before: 2 failed. After: 392 passed. Appending quarantines an interrupted final record, or inserts a newline after a complete JSON record lacking one. No archived log was repaired or overwritten. See gate1d transcripts.

## Gate 1e VERIFIED

Before: 5 failed mutation tests. After: 397 passed. Codes, details, attempt order, final goal/outcome and correctness are enforced. All 1320 v1 rows replay with 0 mismatches. No inference.

## Gate 1f VERIFIED

Before: 2 failed. After: 399 passed. Runtime dependencies and test/viewer extras are declared. README names the 165-episode stage-1 config versus the 330-episode archived pilot. Installation is verified again in the final clean-clone check. No inference.

## Gate 1g VERIFIED

Before: 1 failed. After: 400 passed. scripts/record_metadata.py read /api/tags, /api/show and /api/version without generation. Model digest 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e; server/client 0.40.0. Existing metadata retained; old cache keys remain unchanged. Namespace results/cache_v2 is reserved for new runs. Historical v1 server identity remains UNVERIFIED.

## Gate 1h VERIFIED

Before: 4 failed. After: 404 passed. CSV-generated notes use current v1 values, explicit correct-termination formulas and context-bundle/observable-ST limitations. Oracle convention and genuinely unknown registration metadata are disclosed. Seven bibliography entries were checked against official arXiv abstract metadata, linked in bibliography_sources.json. Full comparative literature review and an assembled manuscript remain outside this gate and UNVERIFIED.

## Gate 2 VERIFIED

Prospective amendment written before inference; diff in gate2-amendment.diff. All protected v1 hashes match; v2 file did not yet exist. User authorization to finish all gates supersedes the earlier wait-for-OK instruction. Scope: validity repair, 160 structural gate then 640 remaining faulted episodes, B2C 200, no new benchmark seeds or model. Primary hypotheses and analysis hash are frozen in prereg_manifest.json.

## Gate 3 schema repair VERIFIED (unit checks)

Before: 6 failed. After: 410 passed. Skill-specific required arguments and allowed values are enforced by the shared replan schema for B2-B5. Parsed schema-invalid output follows the existing three parse attempts and is never cached. Prompt text is unchanged; version v2-format denotes the schema. No inference yet.

## Gate 3 pre-interception validation VERIFIED

Before: 4 failed. After: 414 passed. Malformed anchor calls do not consume transient counters or prerequisites; valid calls preserve their behavior. All 1320 v1 rows still replay with 0 mismatches. No inference yet.

## Gate 3 cache versioning VERIFIED

Before: 2 failed. After: 416 passed. Legacy keys are identical and cache entries remain readable without mutation. New namespaces include digest, server version and context option. New cache-hit and internal retry counts are recorded without altering legacy runner metrics. No inference yet.

## Gate 3 batch instrumentation VERIFIED

418 tests passed, including protected-path and exact-ID guards. New rows record model/options/code/cache provenance and actual episode wall time. Batch completion enforces the preregistered structural gate.

## Gate 3 smoke VERIFIED

Command: PYTHONPATH="" PYTHONDONTWRITEBYTECODE=1 PFR_CACHE=results/cache_v2 PFR_CACHE_NAMESPACE=v2-format PFR_MODEL_DIGEST=845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e PFR_OLLAMA_VERSION=0.40.0 .venv/bin/python scripts/check_llm.py qwen2.5:7b. Output is gate3-smoke.txt; exit 0. Frozen prompt text, tasks, policy and primary analysis hash also verified in gate3-frozen-design.txt.

## Gate 3 completed VERIFIED

160 exact unique IDs; zero invalid calls, zero exhausted parse/schema failures, zero replay mismatches. Actual wall time 736.65 seconds (12.28 minutes). See gate3-run.json, gate3-inference.txt, gate3-validation.txt and gate3-cell-results.csv. Gate continuation is structural and did not depend on success rates. The fixed B2C ablation and exact no-inference reuse tools were prepared while this batch ran; tests passed with 422 total.

## Gate 4 main batch VERIFIED

640 additional exact unique episodes passed the strongest current ID-coordinate, format, parse and replay checks. Zero invalid calls, exhausted parse/schema failures and replay mismatches. Wall time 1988.04 seconds (33.13 minutes); together with Gate 3, all 800 new main faulted episodes are complete. Experimental prompts/policies remained frozen. Metadata-repeat and ID-coordinate guards added with failing-before/passing-after tests; full suite 424 passed.

## Gate 4 completed VERIFIED

All 200 B2C faulted episodes are exact, unique and valid; wall time 632.35 seconds (10.54 minutes). V2 main has 800 new rows plus 520 controls verified by exact no-inference execution and explicit source hashes. All 5278 recorded model requests across main and ablation reconcile with 2752 unique cache keys, with zero missing keys, mode/plan/token/latency mismatches or missing place.loc fields. Saved cost/group/failure/decision metrics independently match all 1320 v1, 1320 v2 and 200 ablation rows.

On 200 faulted cases, raw correctness is B2=0.400, B2C=0.440, B4=0.680. Zero-human correctness is 0.400, 0.410, 0.415. B2C-B4 zero-human difference -0.005 has paired-row and task-cluster CI [-0.025, 0.015]. This does not prove equivalence. The raw difference -0.240 favors B4 under the secondary comparisons, while autonomous differences are small and uncertain. All primary analysis code, task and policy hashes remain frozen and all 19 protected v1 artifacts match. See gate4-integrity.txt, gate4-all-cache-verification.txt and results/v2/ablation_comparisons.csv.

V2 notes are generated directly from CSVs and retain v1 alongside v2. Their added consistency test failed before regeneration and passed afterward; full suite 425 passed. Figures 1-4 retain the primary code; companion figures label literal costs and zero-human correctness explicitly. The heatmap and literal-cost panel were visually inspected.


## FINAL VERIFIED

Clean clone of d0a954092e6e41a7aea285dd1fc8557af42ef12d: editable install succeeds with declared dependencies; imports exclude the dev checkout; 425 passed in 2.80s, zero skips/failures. The clean-clone integrity check repeats every preservation, ID, saved-metric and replay check successfully. No independent model regeneration was done. See final-clone-* transcripts and FINAL_REPORT.md for outcomes and explicit remaining limitations.
