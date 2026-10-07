# Hypothesis Results

This section reports the pre-registered hypotheses using the paired bootstrap results in `results/tables/hypotheses.csv`.

Interpretation of the `diff` column follows the comparison shown in the table. A positive value favors the first method in the comparison; a negative value favors the second method. A 98.3% confidence interval that excludes 0 indicates a clear difference.

---

## H1 — Methods behave similarly at low persistence

**Pre-registered hypothesis:** Methods should behave similarly at low persistence, particularly on T1/T2 transient faults.

### B5 vs B1 — T1/T2 correctness

- Paired episodes: 40
- Difference: **0.000**
- 98.3% CI: **[0.000, 0.000]**
- Reading: **CI includes 0**
- Interpretation: No clear difference between B5 and B1.

### B5 vs B3 — T1/T2 correctness

- Paired episodes: 40
- Difference: **+1.000**
- 98.3% CI: **[1.000, 1.000]**
- Reading: **CI excludes 0**
- Interpretation: B5 is clearly better than B3 on T1/T2 correctness.

### H1 conclusion

**NOT SUPPORTED.**

B5 and B1 behave identically on the tested T1/T2 correctness measure, but B5 differs substantially from B3. Therefore the broader hypothesis that methods behave similarly at low persistence is not supported across the tested comparisons.

---

## H2 — B5 reduces regret and loops on persistent and difficult failures

**Pre-registered hypothesis:** B5 should reduce regret and loops on persistent failures and difficult fixable/permanent conditions.

### P-cell regret

#### B5 vs B0

- Paired episodes: 80
- Difference: **-4.700**
- 98.3% CI: **[-4.850, -4.550]**
- Reading: **CI excludes 0**
- Interpretation: B5 has substantially lower P-cell regret than B0.

#### B5 vs B4

- Paired episodes: 80
- Difference: **-3.788**
- 98.3% CI: **[-4.112, -3.425]**
- Reading: **CI excludes 0**
- Interpretation: B5 has substantially lower P-cell regret than B4.

#### B5 vs B3

- Paired episodes: 80
- Difference: **-4.550**
- 98.3% CI: **[-4.763, -4.275]**
- Reading: **CI excludes 0**
- Interpretation: B5 has substantially lower P-cell regret than B3.

### P-cell loop rate

#### B5 vs B4

- Paired episodes: 80
- Difference: **-0.512**
- 98.3% CI: **[-0.646, -0.388]**
- Reading: **CI excludes 0**
- Interpretation: B5 has a substantially lower P-cell loop rate than B4.

#### B5 vs B3

- Paired episodes: 80
- Difference: **-0.512**
- 98.3% CI: **[-0.637, -0.388]**
- Reading: **CI excludes 0**
- Interpretation: B5 has a substantially lower P-cell loop rate than B3.

### H2 conclusion

**SUPPORTED FOR THE TESTED P-CELL MEASURES.**

B5 substantially reduces regret and loop rate on persistent P-cell failures compared with B0, B4, and B3.

The available hypothesis tests directly evaluate P-cell regret and loop rate; they do not provide a separate statistical test for every difficult fixable condition named in the broader hypothesis.

---

## H3 — B5 does not reduce success on fixable faults

**Pre-registered hypothesis:** B5 should preserve success on fixable faults rather than sacrificing recovery success for lower recovery cost.

### B5 vs B4 — F-cell correctness

- Paired episodes: 60
- Difference: **-0.233**
- 98.3% CI: **[-0.367, -0.117]**
- Reading: **CI excludes 0**
- Interpretation: B5 is significantly worse than B4 on F-cell correctness.

### B5 vs B3 — F-cell correctness

- Paired episodes: 60
- Difference: **+0.333**
- 98.3% CI: **[0.200, 0.483]**
- Reading: **CI excludes 0**
- Interpretation: B5 is significantly better than B3 on F-cell correctness.

### H3 conclusion

**NOT SUPPORTED.**

B5 does not uniformly preserve fixable-fault success. It outperforms B3, but it is significantly worse than B4 on F-cell correctness. This indicates a trade-off between the explicit B5 policy and the more flexible history-aware LLM recovery used by B4.

---

## H4 — B1 may match B5 on permanent faults but should lose on fixable faults

**Pre-registered hypothesis:** B1 may perform similarly to B5 on permanent faults, but should underperform on fixable faults because B1 retries without changing strategy.

### P-cell correctness — B1 vs B5

- Paired episodes: 80
- Difference: **+0.013**
- 98.3% CI: **[0.000, 0.050]**
- Reading: **CI includes 0**
- Interpretation: There is no clear difference in P-cell correctness.

### P-cell regret — B1 vs B5

- Paired episodes: 80
- Difference: **-0.300**
- 98.3% CI: **[-0.450, -0.150]**
- Reading: **CI excludes 0**
- Interpretation: B1 has lower P-cell regret than B5.

This occurs because B1 terminates after three total attempts, whereas B5 follows a longer explicit recovery policy.

### F + T3 correctness — B1 vs B5

- Paired episodes: 80
- Difference: **-0.500**
- 98.3% CI: **[-0.637, -0.362]**
- Reading: **CI excludes 0**
- Interpretation: B1 is substantially worse than B5 on the combined F + T3 subset.

### H4 conclusion

**SUPPORTED WITH NUANCE.**

B1 and B5 show no clear difference in P-cell correctness, consistent with the prediction that a simple maximum-retry strategy can perform similarly on permanent failures. B1 performs substantially worse on the F + T3 subset, consistent with the prediction that changing strategy is important when recovery remains possible.

However, B1 has lower P-cell regret because its three-attempt cutoff causes earlier termination.

---

# Main Comparisons

These comparisons are not separate pre-registered hypotheses but summarize the main overall method differences.

## B5 vs B1 — all-cell correctness

- Paired episodes: 220
- Difference: **+0.177**
- 98.3% CI: **[0.114, 0.241]**
- Reading: **CI excludes 0**
- Interpretation: B5 has significantly higher overall correctness than B1.

## B5 vs B4 — all-cell correctness

- Paired episodes: 220
- Difference: **+0.132**
- 98.3% CI: **[0.050, 0.214]**
- Reading: **CI excludes 0**
- Interpretation: B5 has significantly higher overall correctness than B4.

## B5 vs B3 — all-cell correctness

- Paired episodes: 220
- Difference: **+0.723**
- 98.3% CI: **[0.650, 0.791]**
- Reading: **CI excludes 0**
- Interpretation: B5 has substantially higher overall correctness than B3.

## B4 vs B2 — does history help the LLM?

- Paired episodes: 220
- Difference: **+0.227**
- 98.3% CI: **[0.164, 0.295]**
- Reading: **CI excludes 0**
- Interpretation: B4 is significantly more correct than B2, providing evidence that supplying full failure history improves LLM recovery performance.

---

# Summary

| Hypothesis | Result | Main evidence |
|---|---|---|
| H1 | **Not supported** | B5 = B1 on T1/T2, but B5 > B3 |
| H2 | **Supported for tested P-cell measures** | B5 substantially lowers P-cell regret and loops |
| H3 | **Not supported** | B5 > B3 but B5 < B4 on F-cell correctness |
| H4 | **Supported with nuance** | B1 ≈ B5 on P-cell correctness, but B1 < B5 on F + T3 correctness |

The main overall comparison shows that **B5 achieves the highest overall correctness among the six methods (0.814), while also substantially reducing regret and loop rate relative to the more persistent recovery strategies. B4 remains stronger than B5 on some fixable-fault cases, indicating a trade-off between explicit policy rules and flexible history-aware LLM recovery.**
