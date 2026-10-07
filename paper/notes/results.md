# Results

## Overall performance
Report B0–B5 correctness, regret, loops, human queries.

## Hypothesis results
Summarize H1–H4 from hypotheses.md.

## Recovery behavior
Discuss B5 vs B4/B2/B3 and the main differences.

# Discussion

## Why B5 performs well
Explicit failure-specific policy reduces futile retries/modifications.

## History-aware LLM behavior
B4 benefits from history but frequently overuses modify.

## B4 vs B5 case study
Use t02 TR-P:
B4 → cutoff/wrong
B5 → retry then escalate/correct.

## Trade-offs
B5 has higher overall correctness and lower loops, while B4 retains advantages on some fixable faults.

## Limitations
Mention:
- symbolic simulator
- fixed skill menu
- hand-built fault taxonomy
- one model / one seed
- B5 designed around this taxonomy
- human-assisted outcomes can inflate raw correctness
