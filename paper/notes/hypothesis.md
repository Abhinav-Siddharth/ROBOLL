# Hypothesis results

H1-H4 and the three primary all-cell correctness comparisons retain their original definitions and analysis. The B4/B2 side comparison is a context-bundle comparison. No CI including zero proves equivalence or a tie. Secondary comparisons are descriptive, not confirmatory.

## V1 original paired-row bootstrap

| hypothesis | comparison | subset_metric | n_pairs | diff | ci_lo | ci_hi | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | B5 - B1 | T1/T2 correctness | 40 | 0.000 | 0.000 | 0.000 | CI includes 0 (no clear difference) |
| H1 | B5 - B3 | T1/T2 correctness | 40 | 1.000 | 1.000 | 1.000 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell regret | 80 | -4.700 | -4.850 | -4.550 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell regret | 80 | -3.788 | -4.112 | -3.425 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell regret | 80 | -4.550 | -4.763 | -4.275 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell loop rate | 80 | -0.512 | -0.646 | -0.388 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell loop rate | 80 | -0.512 | -0.637 | -0.388 | CI excludes 0 (A better) |
| H3 | B5 - B4 | F-cell correctness | 60 | -0.233 | -0.367 | -0.117 | CI excludes 0 (A worse) |
| H3 | B5 - B3 | F-cell correctness | 60 | 0.333 | 0.200 | 0.483 | CI excludes 0 (A better) |
| H4 | B1 - B5 | P-cell correctness | 80 | 0.013 | 0.000 | 0.050 | CI includes 0 (no clear difference) |
| H4 | B1 - B5 | P-cell regret | 80 | -0.300 | -0.450 | -0.150 | CI excludes 0 (A better) |
| H4 | B1 - B5 | F + T3 correctness | 80 | -0.500 | -0.637 | -0.362 | CI excludes 0 (A worse) |
| MAIN | B5 - B1 | all-cell correctness | 220 | 0.177 | 0.114 | 0.241 | CI excludes 0 (A better) |
| MAIN | B5 - B4 | all-cell correctness | 220 | 0.132 | 0.050 | 0.214 | CI excludes 0 (A better) |
| MAIN | B5 - B3 | all-cell correctness | 220 | 0.723 | 0.650 | 0.791 | CI excludes 0 (A better) |
| MAIN | B4 - B2 | does history help the LLM? (B4 vs B2) | 220 | 0.227 | 0.164 | 0.295 | CI excludes 0 (A better) |

## V1 task-cluster sensitivity

| hypothesis | comparison | subset_metric | n_pairs | diff | ci_lo | ci_hi | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | B5 - B1 | T1/T2 correctness | 40 | 0.000 | 0.000 | 0.000 | CI includes 0 (no clear difference) |
| H1 | B5 - B3 | T1/T2 correctness | 40 | 1.000 | 1.000 | 1.000 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell regret | 80 | -4.700 | -4.812 | -4.588 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell regret | 80 | -3.788 | -4.071 | -3.513 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell regret | 80 | -4.550 | -4.725 | -4.312 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell loop rate | 80 | -0.512 | -0.575 | -0.450 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell loop rate | 80 | -0.512 | -0.575 | -0.450 | CI excludes 0 (A better) |
| H3 | B5 - B4 | F-cell correctness | 60 | -0.233 | -0.367 | -0.117 | CI excludes 0 (A worse) |
| H3 | B5 - B3 | F-cell correctness | 60 | 0.333 | 0.333 | 0.333 | CI excludes 0 (A better) |
| H4 | B1 - B5 | P-cell correctness | 80 | 0.013 | 0.000 | 0.050 | CI includes 0 (no clear difference) |
| H4 | B1 - B5 | P-cell regret | 80 | -0.300 | -0.412 | -0.188 | CI excludes 0 (A better) |
| H4 | B1 - B5 | F + T3 correctness | 80 | -0.500 | -0.500 | -0.500 | CI excludes 0 (A worse) |
| MAIN | B5 - B1 | all-cell correctness | 220 | 0.177 | 0.164 | 0.182 | CI excludes 0 (A better) |
| MAIN | B5 - B4 | all-cell correctness | 220 | 0.132 | 0.032 | 0.227 | CI excludes 0 (A better) |
| MAIN | B5 - B3 | all-cell correctness | 220 | 0.723 | 0.709 | 0.727 | CI excludes 0 (A better) |
| MAIN | B4 - B2 | does history help the LLM? (B4 vs B2) | 220 | 0.227 | 0.136 | 0.318 | CI excludes 0 (A better) |

## V1 H2 cost-definition sensitivity

| hypothesis | comparison | subset_metric | n_pairs | diff | ci_lo | ci_hi | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | B5 - B0 | P-cell anchor_regret | 80 | -4.987 | -5.188 | -4.800 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell anchor_regret | 80 | -4.025 | -4.375 | -3.675 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell anchor_regret | 80 | -3.788 | -4.150 | -3.388 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell total_failure_cost | 80 | -4.700 | -4.850 | -4.550 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell total_failure_cost | 80 | -3.788 | -4.112 | -3.425 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell total_failure_cost | 80 | -4.550 | -4.763 | -4.275 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell legacy_regret | 80 | -4.700 | -4.850 | -4.550 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell legacy_regret | 80 | -3.788 | -4.112 | -3.425 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell legacy_regret | 80 | -4.550 | -4.763 | -4.275 | CI excludes 0 (A better) |

V1 H1 and H3 are not uniformly supported; H2 favors B5 on the tested permanent-cell costs and loops. H4 has no clear permanent-correctness difference and favors B5 on F+T3 correctness. B3 validity defects and human assistance qualify these readings.

## V2 primary paired-row bootstrap

| hypothesis | comparison | subset_metric | n_pairs | diff | ci_lo | ci_hi | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | B5 - B1 | T1/T2 correctness | 40 | 0.000 | 0.000 | 0.000 | CI includes 0 (no clear difference) |
| H1 | B5 - B3 | T1/T2 correctness | 40 | 0.150 | 0.025 | 0.300 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell regret | 80 | -4.787 | -4.975 | -4.625 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell regret | 80 | -3.913 | -4.213 | -3.625 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell regret | 80 | -4.463 | -4.725 | -4.125 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell loop rate | 80 | -0.512 | -0.637 | -0.388 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell loop rate | 80 | -0.475 | -0.613 | -0.350 | CI excludes 0 (A better) |
| H3 | B5 - B4 | F-cell correctness | 60 | 0.250 | 0.117 | 0.400 | CI excludes 0 (A better) |
| H3 | B5 - B3 | F-cell correctness | 60 | 0.133 | 0.033 | 0.250 | CI excludes 0 (A better) |
| H4 | B1 - B5 | P-cell correctness | 80 | 0.037 | 0.000 | 0.100 | CI includes 0 (no clear difference) |
| H4 | B1 - B5 | P-cell regret | 80 | -0.212 | -0.375 | -0.025 | CI excludes 0 (A better) |
| H4 | B1 - B5 | F + T3 correctness | 80 | -0.912 | -0.975 | -0.825 | CI excludes 0 (A worse) |
| MAIN | B5 - B1 | all-cell correctness | 220 | 0.318 | 0.241 | 0.395 | CI excludes 0 (A better) |
| MAIN | B5 - B4 | all-cell correctness | 220 | 0.245 | 0.173 | 0.323 | CI excludes 0 (A better) |
| MAIN | B5 - B3 | all-cell correctness | 220 | 0.427 | 0.350 | 0.509 | CI excludes 0 (A better) |
| MAIN | B4 - B2 | does history help the LLM? (B4 vs B2) | 220 | 0.255 | 0.186 | 0.327 | CI excludes 0 (A better) |

## V2 task-cluster sensitivity

| hypothesis | comparison | subset_metric | n_pairs | diff | ci_lo | ci_hi | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | B5 - B1 | T1/T2 correctness | 40 | 0.000 | 0.000 | 0.000 | CI includes 0 (no clear difference) |
| H1 | B5 - B3 | T1/T2 correctness | 40 | 0.150 | 0.000 | 0.350 | CI includes 0 (no clear difference) |
| H2 | B5 - B0 | P-cell regret | 80 | -4.787 | -4.925 | -4.675 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell regret | 80 | -3.913 | -4.213 | -3.612 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell regret | 80 | -4.463 | -4.688 | -4.175 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell loop rate | 80 | -0.512 | -0.575 | -0.450 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell loop rate | 80 | -0.475 | -0.500 | -0.425 | CI excludes 0 (A better) |
| H3 | B5 - B4 | F-cell correctness | 60 | 0.250 | 0.133 | 0.350 | CI excludes 0 (A better) |
| H3 | B5 - B3 | F-cell correctness | 60 | 0.133 | 0.050 | 0.217 | CI excludes 0 (A better) |
| H4 | B1 - B5 | P-cell correctness | 80 | 0.037 | 0.000 | 0.087 | CI includes 0 (no clear difference) |
| H4 | B1 - B5 | P-cell regret | 80 | -0.212 | -0.325 | -0.075 | CI excludes 0 (A better) |
| H4 | B1 - B5 | F + T3 correctness | 80 | -0.912 | -0.975 | -0.825 | CI excludes 0 (A worse) |
| MAIN | B5 - B1 | all-cell correctness | 220 | 0.318 | 0.286 | 0.345 | CI excludes 0 (A better) |
| MAIN | B5 - B4 | all-cell correctness | 220 | 0.245 | 0.155 | 0.332 | CI excludes 0 (A better) |
| MAIN | B5 - B3 | all-cell correctness | 220 | 0.427 | 0.373 | 0.500 | CI excludes 0 (A better) |
| MAIN | B4 - B2 | does history help the LLM? (B4 vs B2) | 220 | 0.255 | 0.159 | 0.350 | CI excludes 0 (A better) |

## V2 H2 cost-definition sensitivity

| hypothesis | comparison | subset_metric | n_pairs | diff | ci_lo | ci_hi | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | B5 - B0 | P-cell anchor_regret | 80 | -5.062 | -5.275 | -4.850 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell anchor_regret | 80 | -4.138 | -4.487 | -3.800 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell anchor_regret | 80 | -3.737 | -4.125 | -3.312 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell total_failure_cost | 80 | -4.787 | -4.975 | -4.625 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell total_failure_cost | 80 | -3.913 | -4.213 | -3.625 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell total_failure_cost | 80 | -4.463 | -4.725 | -4.125 | CI excludes 0 (A better) |
| H2 | B5 - B0 | P-cell legacy_regret | 80 | -4.787 | -4.975 | -4.625 | CI excludes 0 (A better) |
| H2 | B5 - B4 | P-cell legacy_regret | 80 | -3.913 | -4.213 | -3.625 | CI excludes 0 (A better) |
| H2 | B5 - B3 | P-cell legacy_regret | 80 | -4.463 | -4.725 | -4.125 | CI excludes 0 (A better) |

V2 H1 B5-B3: paired-row CI [0.025, 0.3], task-cluster CI [0.0, 0.35]. The sampling unit matters; neither comparison is an equivalence test. V2 H3 B5-B4 difference 0.25, CI [0.117, 0.4], CI excludes 0 (A better). This contrasts with the v1 F-cell reading above.

## Secondary matched-context comparisons

| comparison | metric | bootstrap | n_pairs | diff | ci_lo | ci_hi | reading | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2C - B2 | raw_correct | paired_row | 200 | 0.040 | 0.010 | 0.075 | CI excludes 0 (A better) | secondary post-audit ablation |
| B2C - B2 | raw_correct | task_cluster | 200 | 0.040 | 0.005 | 0.085 | CI excludes 0 (A better) | secondary post-audit ablation |
| B2C - B2 | no_human_correct | paired_row | 200 | 0.010 | 0.000 | 0.030 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B2 | no_human_correct | task_cluster | 200 | 0.010 | 0.000 | 0.030 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B2 | autonomous_success | paired_row | 200 | 0.010 | 0.000 | 0.030 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B2 | autonomous_success | task_cluster | 200 | 0.010 | 0.000 | 0.030 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B2 | anchor_regret | paired_row | 200 | 0.075 | -0.020 | 0.170 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B2 | anchor_regret | task_cluster | 200 | 0.075 | -0.035 | 0.150 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B2 | total_failure_cost | paired_row | 200 | -0.110 | -0.225 | -0.030 | CI excludes 0 (A better) | secondary post-audit ablation |
| B2C - B2 | total_failure_cost | task_cluster | 200 | -0.110 | -0.260 | -0.010 | CI excludes 0 (A better) | secondary post-audit ablation |
| B2C - B4 | raw_correct | paired_row | 200 | -0.240 | -0.325 | -0.160 | CI excludes 0 (A worse) | secondary post-audit ablation |
| B2C - B4 | raw_correct | task_cluster | 200 | -0.240 | -0.343 | -0.140 | CI excludes 0 (A worse) | secondary post-audit ablation |
| B2C - B4 | no_human_correct | paired_row | 200 | -0.005 | -0.025 | 0.015 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B4 | no_human_correct | task_cluster | 200 | -0.005 | -0.025 | 0.015 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B4 | autonomous_success | paired_row | 200 | -0.005 | -0.025 | 0.015 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B4 | autonomous_success | task_cluster | 200 | -0.005 | -0.025 | 0.015 | CI includes 0 (no clear difference) | secondary post-audit ablation |
| B2C - B4 | anchor_regret | paired_row | 200 | 0.295 | 0.125 | 0.465 | CI excludes 0 (A worse) | secondary post-audit ablation |
| B2C - B4 | anchor_regret | task_cluster | 200 | 0.295 | 0.130 | 0.460 | CI excludes 0 (A worse) | secondary post-audit ablation |
| B2C - B4 | total_failure_cost | paired_row | 200 | 0.425 | 0.245 | 0.610 | CI excludes 0 (A worse) | secondary post-audit ablation |
| B2C - B4 | total_failure_cost | task_cluster | 200 | 0.425 | 0.215 | 0.630 | CI excludes 0 (A worse) | secondary post-audit ablation |

These 200-pair comparisons are post-audit secondary analyses. B2C retains current failure count, remaining budget and untried values but removes prior failure history. Compare with B2 for the hint bundle and B4 for history conditional on those hints. The intervals do not establish familywise control over every exploratory comparison.
