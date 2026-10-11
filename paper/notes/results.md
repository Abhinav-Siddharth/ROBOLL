# Results: v1 archive and format-validity replication

The v1 archive contains 1320 episodes. The `regret` column below preserves the original global-failure-based metric for comparability. It is labeled legacy regret; literal anchor regret and total failure cost are reported separately. Table values are generated from saved CSV files.

## V1 archived overall table

| method | correct | regret | loop | human_queries | tokens | latency_s |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | 0.364 | 4.182 | 0.727 | 0.000 | 0.000 | 0.000 |
| B1 | 0.636 | 1.000 | 0.727 | 0.000 | 0.000 | 0.000 |
| B2 | 0.455 | 3.695 | 0.545 | 0.000 | 1628.968 | 6.006 |
| B3 | 0.091 | 5.891 | 0.895 | 0.000 | 2915.259 | 11.860 |
| B4 | 0.682 | 3.355 | 0.541 | 0.227 | 2024.977 | 4.788 |
| B5 | 0.814 | 1.395 | 0.350 | 0.091 | 481.859 | 2.084 |

## V1 derived cost definitions

| method | anchor_attempts | total_failures | total_failure_cost | anchor_regret | legacy_regret |
| --- | --- | --- | --- | --- | --- |
| B0 | 6.000 | 5.636 | 5.636 | 4.182 | 4.182 |
| B1 | 2.727 | 2.455 | 2.455 | 1.000 | 1.000 |
| B2 | 5.286 | 5.059 | 5.059 | 3.468 | 3.695 |
| B3 | 4.450 | 7.127 | 7.127 | 2.636 | 5.891 |
| B4 | 5.045 | 4.623 | 4.623 | 3.227 | 3.355 |
| B5 | 2.718 | 2.600 | 2.600 | 0.900 | 1.395 |

`total_failure_cost` is the count of all non-OK execution steps. `anchor_regret` counts only original target-pick calls above the forced-initial-attempt oracle. Neither a low cost nor permanent-fault correctness implies successful task recovery.

## V1 autonomous and assisted outcomes

| method | n | autonomous_success | human_assisted_success | raw_correct | no_human_correct | autonomous_solvable_or_permanent_correct | autonomous_success_rate | human_assisted_success_rate | raw_correct_rate | no_human_correct_rate | autonomous_solvable_or_permanent_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | 220 | 80.000 | 0.000 | 80.000 | 80.000 | 80.000 | 0.364 | 0.000 | 0.364 | 0.364 | 0.364 |
| B1 | 220 | 60.000 | 0.000 | 140.000 | 140.000 | 140.000 | 0.273 | 0.000 | 0.636 | 0.636 | 0.636 |
| B2 | 220 | 100.000 | 0.000 | 100.000 | 100.000 | 100.000 | 0.455 | 0.000 | 0.455 | 0.455 | 0.455 |
| B3 | 220 | 20.000 | 0.000 | 20.000 | 20.000 | 20.000 | 0.091 | 0.000 | 0.091 | 0.091 | 0.091 |
| B4 | 220 | 100.000 | 14.000 | 150.000 | 100.000 | 136.000 | 0.455 | 0.064 | 0.682 | 0.455 | 0.618 |
| B5 | 220 | 100.000 | 0.000 | 179.000 | 159.000 | 179.000 | 0.455 | 0.000 | 0.814 | 0.723 | 0.814 |

`raw_correct` counts solvable success and permanent abstain/escalate. `no_human_correct` additionally requires human_queries == 0. `autonomous_solvable_or_permanent_correct` requires autonomous success on solvable cells but retains permanent human escalation. Its name must not be shortened to purely autonomous correctness.

On solvable cells B2, B4 and B5 each have 100/140 autonomous successes in v1. B4 adds 14 human-assisted successes, seven each in ST-F and PRE-F. No method has autonomous ST-F success in v1. Across all 220 episodes, no_human_correct is 100/220 for B4 and 159/220 for B5. This difference includes correct permanent termination; it is not a permanent-cell-only success rate. The alternative definition retaining permanent escalation is 136/220 versus 179/220.

## V1 validity and interpretation limits

All 720 executed invalid calls omit place.loc: B3 610, B4 24 and B5 86. B3 has invalid calls in 110/220 episodes and 610/1568 failure steps (38.9%). In ST-F, B3 and B5 each hold the target before their first invalid call in 18/20 episodes. These are baseline validity defects; the v1 zeros do not isolate recovery policy capability. B2 also fails ST-F/PRE-F without executed invalid calls, so schema validity alone need not solve every case.

B4 vs B2 compares a context bundle: failure history, counts, remaining budget and untried values. The v1 +22.7-point raw-correct difference cannot isolate history. B4 made 857 modify decisions, 478 no-ops. Among 790 non-PARAM failures with a recovery decision, 718 (90.9%) selected modify.

ST regimes are observable in the state supplied to replanning. The symbolic simulator, oracle failure codes and initial plans, hand-built taxonomy, one model and one seed limit generalization. Latency sums retain original cache-entry timings and are not execution wall time. The kinematic replay has no contact physics.

## V2 primary replication

| method | correct | regret | loop | human_queries | tokens | latency_s |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | 0.364 | 4.182 | 0.727 | 0.000 | 0.000 | 0.000 |
| B1 | 0.636 | 1.000 | 0.727 | 0.000 | 0.000 | 0.000 |
| B2 | 0.455 | 3.686 | 0.545 | 0.000 | 1604.864 | 5.891 |
| B3 | 0.527 | 2.941 | 0.450 | 0.000 | 1864.932 | 8.274 |
| B4 | 0.709 | 3.282 | 0.536 | 0.245 | 1996.355 | 4.803 |
| B5 | 0.955 | 0.973 | 0.282 | 0.091 | 373.550 | 1.666 |

## V2 costs

| method | anchor_attempts | total_failures | total_failure_cost | anchor_regret | legacy_regret |
| --- | --- | --- | --- | --- | --- |
| B0 | 6.000 | 5.636 | 5.636 | 4.182 | 4.182 |
| B1 | 2.727 | 2.455 | 2.455 | 1.000 | 1.000 |
| B2 | 5.282 | 5.050 | 5.050 | 3.464 | 3.686 |
| B3 | 4.377 | 4.168 | 4.168 | 2.559 | 2.941 |
| B4 | 5.082 | 4.564 | 4.564 | 3.264 | 3.282 |
| B5 | 2.686 | 2.173 | 2.173 | 0.868 | 0.973 |

## V2 solvable success split

| method | n | autonomous_success | human_assisted_success | autonomous_success_rate |
| --- | --- | --- | --- | --- |
| B0 | 140 | 80.000 | 0.000 | 0.571 |
| B1 | 140 | 60.000 | 0.000 | 0.429 |
| B2 | 140 | 100.000 | 0.000 | 0.714 |
| B3 | 140 | 116.000 | 0.000 | 0.829 |
| B4 | 140 | 103.000 | 15.000 | 0.736 |
| B5 | 140 | 133.000 | 0.000 | 0.950 |

## V2 named outcomes

| method | n | autonomous_success | human_assisted_success | raw_correct | no_human_correct | autonomous_solvable_or_permanent_correct | autonomous_success_rate | human_assisted_success_rate | raw_correct_rate | no_human_correct_rate | autonomous_solvable_or_permanent_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | 220 | 80.000 | 0.000 | 80.000 | 80.000 | 80.000 | 0.364 | 0.000 | 0.364 | 0.364 | 0.364 |
| B1 | 220 | 60.000 | 0.000 | 140.000 | 140.000 | 140.000 | 0.273 | 0.000 | 0.636 | 0.636 | 0.636 |
| B2 | 220 | 100.000 | 0.000 | 100.000 | 100.000 | 100.000 | 0.455 | 0.000 | 0.455 | 0.455 | 0.455 |
| B3 | 220 | 116.000 | 0.000 | 116.000 | 116.000 | 116.000 | 0.527 | 0.000 | 0.527 | 0.527 | 0.527 |
| B4 | 220 | 103.000 | 15.000 | 156.000 | 103.000 | 141.000 | 0.468 | 0.068 | 0.709 | 0.468 | 0.641 |
| B5 | 220 | 133.000 | 0.000 | 210.000 | 190.000 | 210.000 | 0.605 | 0.000 | 0.955 | 0.864 | 0.955 |

V2 is the primary H1-H4 dataset under the prospective amendment. The original v1 data and tables remain visible above. The format repair gives no method new state, history or budget information. Consult results/v2/comparison.csv and audit/phase2/GATE_REPORT.md for provenance and validity checks.

Residual format-valid failures include missing drawer closure and failure to visit a required location. Goal text does not explicitly state every drawer-closure predicate, although the original remaining plan includes close actions. The causal contribution of goal-specification clarity is untested. V2 does not add formal goal information. A valid empty replan is classified as incomplete, not permanent-fault abstention; we retain this original outcome convention. Low anchor regret alone is not success.

## Matched-context ablation, faulted cells only

| method | raw_correct | no_human_correct | autonomous_solvable_or_permanent_correct | autonomous_success | human_assisted_success | anchor_regret | total_failure_cost | legacy_regret | loop | human_queries | tokens | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | 0.300 | 0.300 | 0.300 | 0.300 | 0.000 | 4.600 | 6.200 | 4.600 | 0.800 | 0.000 | 0.000 | 0.000 |
| B1 | 0.600 | 0.600 | 0.600 | 0.200 | 0.000 | 1.100 | 2.700 | 1.100 | 0.800 | 0.000 | 0.000 | 0.000 |
| B2 | 0.400 | 0.400 | 0.400 | 0.400 | 0.000 | 3.810 | 5.555 | 4.055 | 0.600 | 0.000 | 1765.350 | 6.480 |
| B2C | 0.440 | 0.410 | 0.425 | 0.410 | 0.015 | 3.885 | 5.445 | 3.970 | 0.590 | 0.030 | 1777.770 | 5.866 |
| B3 | 0.480 | 0.480 | 0.480 | 0.480 | 0.000 | 2.815 | 4.585 | 3.235 | 0.495 | 0.000 | 2051.425 | 9.101 |
| B4 | 0.680 | 0.415 | 0.605 | 0.415 | 0.075 | 3.590 | 5.020 | 3.610 | 0.590 | 0.270 | 2195.990 | 5.284 |
| B5 | 0.950 | 0.850 | 0.950 | 0.565 | 0.000 | 0.955 | 2.390 | 1.070 | 0.310 | 0.100 | 410.905 | 1.833 |
