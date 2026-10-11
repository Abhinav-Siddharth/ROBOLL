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
