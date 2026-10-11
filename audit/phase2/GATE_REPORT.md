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

