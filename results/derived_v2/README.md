# Exploratory human-help analysis

Every number here is "exploratory, defined after seeing the data".

U(c) = raw_correct - c * human_queries; c = 0.25, 0.5, 1.0. Correctness includes permanent abstain/escalate and solvable success. Every query is penalized, including queries in incorrect episodes. Overall means give equal weight to each logged task/cell/seed unit. v1 means qwen.jsonl, the corrected archived dataset; qwen_pre_fix.jsonl is only the earlier ST-F archive.

Paired row and task-cluster percentile CIs use 10000 draws, seed 0, confidence 0.983333333 (matching the primary 0.05/3 alpha). The same resampled units are used across methods; comparison intervals bootstrap paired differences. Whole-task resampling preserves the row-mean estimand even with unequal task sizes. These marginal intervals do not control all post-data comparisons as a family. Degenerate empirical bootstrap CIs are not proof of zero population uncertainty.

c_star solves delta_correct - c * delta_queries = 0. An outside-range root is reported, but is not a break-even in [0,1]. Equal intercept and slope means equality throughout the interval. Costs are chosen after seeing the data and do not estimate real human burden.
