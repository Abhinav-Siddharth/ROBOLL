# Derived metric definitions

anchor_attempts counts every call matching the original first pick target.
anchor_regret = max(0, anchor_attempts - oracle_attempts).
total_failure_cost = total_failures = count of non-OK execution steps.
legacy_regret retains the archived runner regret, including non-anchor failures.
The oracle convention forces the original initial attempt before recovery.

autonomous_success: success and human_queries == 0.
human_assisted_success: success and human_queries > 0.
raw_correct: success on solvable cells; abstain/escalate on permanent cells.
no_human_correct: raw_correct and human_queries == 0.
autonomous_solvable_or_permanent_correct: raw_correct and (permanent or human_queries == 0); this retains permanent human escalation.
