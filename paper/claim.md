# Knowing when to stop under persistent robot skill failures

RQ: In a symbolic robot benchmark, how do recovery policies balance autonomous completion,
correct termination, total failure cost and literal anchor regret?

The benchmark compares B0-B5 across 20 tasks and 11 fault cells. Fixable and permanent
variants share initial failure messages. ST regimes are observable in the true state
supplied to replanning, so history is not the only signal.

B4 vs B2 compares a context bundle: history, failure counts, remaining budget and
untried parameter values. It does not isolate history. The matched-context B2 ablation
will retain budget/untried hints and remove prior failure history.

Contributions: a controlled fault taxonomy; comparisons of retry, modify, replan,
escalate and abstain; explicit autonomous and human-assisted outcome definitions;
and an analysis of omitted required arguments in small-model replanning.

V1 is preserved alongside the planned format-validity replication. Its headline is
correct termination and knowing when to stop, qualified by baseline schema defects.
No claim is made that all ST-F/PRE-F zeros measure recovery ability or that schema
repair guarantees completion. See paper/notes/results.md for current numbers and formulas.

Oracle regret uses a forced initial attempt convention. We assume oracle initial plans,
structured failure codes, a fixed skill menu, a symbolic simulator, one model and one seed.
We do not claim priority over retry/switch/abstain research, an isolated history effect,
physical executability, sim-to-real performance or superiority to a state-of-the-art system.

Related-work metadata is verified in paper/refs.bib and audit/phase2/bibliography_sources.json.
A full comparative literature review remains unfinished.
