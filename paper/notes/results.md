# Results

## Experimental Overview

The final evaluation contains 1,320 episodes covering 20 tasks, 11 fault cells, and six recovery methods (B0–B5). The evaluation measures episode correctness, attempts and regret at the faulted step, loop rate, human queries, LLM token usage, and latency.

All reported values in this section are taken from the generated analysis tables.

---

## Overall Performance

The overall correctness, recovery cost, and loop behavior of the six methods are summarized below.

| Method | Correctness | Regret | Loop rate | Human queries | Tokens/episode | Latency (s) |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 0.364 | 4.182 | 0.727 | 0.000 | 0.0 | 0.00 |
| B1 | 0.636 | 1.000 | 0.727 | 0.000 | 0.0 | 0.00 |
| B2 | 0.455 | 3.695 | 0.545 | 0.000 | 1628.968 | 6.006 |
| B3 | 0.091 | 5.868 | 0.891 | 0.000 | 2903.645 | 11.741 |
| B4 | 0.682 | 3.355 | 0.541 | 0.227 | 2024.227 | 4.780 |
| B5 | **0.814** | **1.391** | **0.345** | **0.091** | **480.768** | **2.020** |

B5 achieves the highest overall correctness at **81.4%**, exceeding B4 (68.2%), B1 (63.6%), B2 (45.5%), B0 (36.4%), and B3 (9.1%). B5 also has a substantially lower average regret than the LLM-based methods B2, B3, and B4.

B1 has the lowest average regret (1.000), but this result should not be interpreted as superior recovery. B1 terminates after three attempts and therefore avoids accumulating additional failed attempts, including on episodes where further recovery could have been possible. Its loop rate remains high at 72.7%.

B5 combines high correctness with a substantially lower loop rate of **34.5%**, compared with 54.1% for B4, 54.5% for B2, 72.7% for B0 and B1, and 89.1% for B3.

B5 also has the lowest LLM token usage and latency among the LLM-based recovery methods. It uses approximately **481 tokens per episode** and has mean latency of **2.02 s**, compared with 2,024 tokens and 4.78 s for B4, 1,629 tokens and 6.01 s for B2, and 2,904 tokens and 11.74 s for B3.

Human-assisted outcomes critically qualify raw correctness figures. Across the entire benchmark:
- **Autonomous Success on Solvable Cells:** B2, B4, and B5 are exactly tied at **100/140 (71.4%)** (or 45.5% across all 220 episodes).
- **Human Escalation:** B4 obtains 14 additional successes (7 in `ST-F` and 7 in `PRE-F`) via human intervention (`human_queries = 1`), raising its solvable success to 114/140 (81.4%) and overall correctness to 68.2%. B4 achieves 0/20 autonomous success on both `ST-F` and `PRE-F`.
- When evaluated strictly on **Autonomous Correctness** (solvable success without human intervention, permanent correctly terminating), B5 achieves **81.4%** versus B4's **61.8%**, expanding B5's advantage from +13.2% to **+19.5%** (98.3% CI: [+0.132, +0.264]).
- **Schema Argument Omission:** The 0/20 autonomous success on `ST-F` and `PRE-F` stems from a structural schema omission in the 7B planner rather than failure of spatial reasoning. When replanning, Qwen2.5-7B accurately identifies the object's true location from observations and navigates to pick it, but frequently omits the required `loc` parameter in `place` calls (emitting `place(obj, orient)` without `loc`). This produces `PRECOND_UNMET: invalid call` in 50.0% of all B3 episodes and 85–90% of B5's replan attempts on state/precondition faults.


## Hypothesis Results

### H1 — Similar behavior at low persistence

The preregistered hypothesis predicted that methods would behave similarly at low-persistence transient faults.

For B5 versus B1 on T1/T2 correctness, the paired difference was **0.000**, with a 98.3% CI of **[0.000, 0.000]**, so there is no clear difference.

However, B5 versus B3 on the same subset produced a difference of **+1.000**, with a 98.3% CI of **[1.000, 1.000]**, clearly favoring B5.

**Conclusion: H1 is not supported.**

The results show that B5 and B1 behave similarly on T1/T2, but B3 behaves substantially differently and performs poorly on these transient conditions.

### H2 — B5 reduces regret and loops on persistent failures

B5 shows a substantial reduction in P-cell regret relative to every comparison method tested.

- B5 vs B0: difference **-4.700**, CI **[-4.850, -4.550]**
- B5 vs B4: difference **-3.788**, CI **[-4.112, -3.425]**
- B5 vs B3: difference **-4.550**, CI **[-4.763, -4.275]**

The loop-rate comparisons also favor B5:

- B5 vs B4: difference **-0.512**, CI **[-0.646, -0.388]**
- B5 vs B3: difference **-0.512**, CI **[-0.637, -0.388]**

All of these confidence intervals exclude zero.

**Conclusion: H2 is supported for the tested P-cell measures.**

B5 substantially reduces wasted attempts and repeated-loop behavior on persistent failures.

### H3 — B5 does not reduce success on fixable faults

The hypothesis predicted that B5 would preserve success on fixable faults.

Against B4, B5 is significantly worse on F-cell correctness:

- B5 vs B4: difference **-0.233**
- 98.3% CI: **[-0.367, -0.117]**

Against B3, B5 is significantly better:

- B5 vs B3: difference **+0.333**
- 98.3% CI: **[0.200, 0.483]**

Thus, B5 does not uniformly preserve fixable-fault performance. In particular, B4 achieves significantly higher F-cell correctness than B5.

**Conclusion: H3 is not supported.**

The result suggests a trade-off: B5's explicit fault-specific rules improve efficiency and robustness overall, while the more flexible history-aware LLM policy in B4 can recover some fixable faults that B5 fails to recover.

### H4 — B1 versus B5

The hypothesis predicted that B1 could perform similarly to B5 on permanent faults but would underperform on fixable faults.

For P-cell correctness:

- B1 vs B5: difference **+0.013**
- 98.3% CI: **[0.000, 0.050]**
- CI includes zero.

Thus, there is no clear difference in P-cell correctness.

For P-cell regret:

- B1 vs B5: difference **-0.300**
- 98.3% CI: **[-0.450, -0.150]**

B1 therefore has lower P-cell regret, largely because it terminates after three attempts rather than continuing recovery.

For the combined F + T3 correctness subset:

- B1 vs B5: difference **-0.500**
- 98.3% CI: **[-0.637, -0.362]**

This strongly favors B5.

**Conclusion: H4 is supported with nuance.**

B1 and B5 show no clear difference in P-cell correctness, while B5 substantially outperforms B1 on conditions where continued recovery can be useful. However, B1 achieves lower regret on permanent cells through early termination rather than successful recovery.

---

## Recovery Behavior

The results show a clear separation between the six recovery strategies.

### B0: persistent retry

B0 performs blind retries without changing strategy. It achieves **36.4% correctness**, with a **72.7% loop rate** and **4.182 regret**. Its strongest behavior is on transient faults where repeated execution is actually sufficient, but it performs poorly on permanent and non-transient faults.

### B1: bounded retry

B1 improves correctness to **63.6%** while reducing average regret to **1.000**, but its loop rate remains **72.7%**. The low regret is partly a consequence of its fixed three-attempt termination rule rather than superior recovery reasoning.

### B2: current-error-only LLM recovery

B2 achieves **45.5% correctness**. It uses the current error but does not retain failure history. Its performance is substantially below B4, suggesting that the additional context supplied by failure history is important for recovery decisions.

### B3: always replan

B3 performs worst overall, with only **9.1% correctness**, **5.868 regret**, and an **89.1% loop rate**. Replanning after every failure does not guarantee useful recovery and introduces substantial LLM overhead.

### B4: history-aware LLM recovery

B4 reaches **68.2% correctness**, demonstrating that providing full failure history, remaining budget, and untried values substantially improves over B2. The direct B4-versus-B2 comparison gives a correctness difference of **+0.227**, with a 98.3% CI of **[0.164, 0.295]**.

However, B4 frequently selects `modify` even when the observed failure is not a parameter mismatch. Across the analyzed execution decisions, **91% of B4 modify decisions on non-PARAM errors were still classified as `modify`**, and **479 of 857 modify decisions were no-op modifications**. This indicates that B4 can convert parameter modification into repeated attempts when the available parameter values have already been exhausted.

### B5: explicit failure-specific policy

B5 obtains the strongest overall result: **81.4% correctness**, **1.391 regret**, and **34.5% loop rate**. Unlike B4, its recovery mode is selected according to explicit rules tied to the observed failure code and failure counts. This prevents repeated modification of parameters for failures where parameter changes cannot resolve the underlying problem.

B5 also uses substantially fewer LLM tokens and lower latency than B4, while achieving higher overall correctness.

---

# Discussion

## Why B5 performs well

The main advantage of B5 is that it explicitly conditions recovery behavior on the failure class and accumulated failure count.

Instead of treating every failure as a generic reason to continue experimenting, B5 distinguishes between transient execution failures, parameter mismatches, state mismatches, and unmet preconditions. This allows it to stop investing attempts in strategies that have already demonstrated that they are ineffective.

This behavior explains the strong reduction in regret and loop rate on persistent failures. The P-cell analysis shows that B5 uses substantially fewer unnecessary attempts than B0, B3, and B4.

The result also demonstrates that **recovery quality is not equivalent to task correctness alone**. A method can eventually produce a correct episode while using many unnecessary attempts or relying on human intervention.

## History-aware LLM behavior

B4 demonstrates the value of providing failure history to the LLM. Its overall correctness of **68.2%** exceeds the **45.5%** achieved by B2, which receives only the current failure information. The paired B4-versus-B2 comparison also shows a statistically clear improvement.

However, history alone does not guarantee appropriate strategy selection. B4 heavily favors `modify`, including for execution, state, and precondition failures where modifying the grasp parameter is not the appropriate recovery mechanism.

Once untried values are exhausted, additional `modify` calls can become effectively equivalent to retries. This behavior contributes to unnecessary attempts and explains why B4 can have higher correctness on some fixable cases while still exhibiting substantially greater regret than B5.

## B4 versus B5 case study

A representative example is task **t02 under TR-P**.

B4 receives repeated `EXEC_TRANSIENT` failures and repeatedly selects `modify`. It tries several grasp values and then continues modifying after the available useful parameter values have effectively been exhausted. It eventually reaches the execution cutoff with **regret 7** and the episode is marked **wrong**.

B5 instead retains the same grasp and follows its explicit transient-failure rule. It retries the same action three times, then escalates when the failure persists. The episode is therefore correctly terminated as a permanent failure, with **regret 3**.

This example illustrates the distinction between **context-rich reasoning** and **strategy discipline**. B4 has more information available to it, but B5 uses its information more conservatively and terminates a clearly unproductive recovery path.

## Raw correctness versus autonomous recovery

Human queries provide an important qualification to the correctness results.

B4 has **0.227 human queries per episode**, and its raw correctness of 0.682 falls to approximately **0.45** when correctness is restricted to autonomous outcomes. B5 has fewer human queries (0.091 per episode), with autonomous correctness remaining approximately **0.72**.

Therefore, raw episode correctness should not be interpreted as a direct measure of autonomous capability. Recovery cost, loop rate, and human intervention provide complementary evidence.

## Trade-offs

B5 provides the strongest overall balance of correctness, recovery cost, and computational efficiency. It outperforms B4 in all-cell correctness by **13.2 percentage points**, while also using substantially fewer tokens and exhibiting lower latency.

However, B4 retains an advantage on some fixable faults. The F-cell comparison shows a significant **23.3 percentage-point disadvantage for B5 relative to B4**. This suggests that an explicit rule policy can be more disciplined but less flexible than a history-aware LLM when a fault requires recovery behavior not perfectly captured by the predefined rules.

The results therefore do not imply that explicit policies universally dominate LLM reasoning. Instead, they indicate that **failure-specific control can substantially improve reliability and efficiency in a controlled fault taxonomy, while flexible LLM reasoning can retain advantages on some recoverable cases.**

---

## Limitations

### Symbolic simulator

The evaluation uses a controlled Python state-based simulator rather than a physics-based simulator or physical robot. It therefore does not model realistic robot dynamics, collisions, grasp forces, sensor noise, or perception uncertainty.

### Fixed skill menu

The experiment uses a fixed set of available robot skills. Recovery behavior is therefore evaluated within a constrained action space and does not represent unrestricted real-world robot action generation.

### Hand-built fault taxonomy

The fault taxonomy is manually constructed around 11 predefined cells. This improves experimental control and reproducibility but does not guarantee coverage of the full space of failures encountered by physical robots.

### B5 is aligned with the tested taxonomy

B5 is an explicit rule-based policy whose recovery rules were designed around the predefined fault classes. Its strong performance should therefore not be interpreted as evidence that explicit rules will generalize equally well to arbitrary unseen failure types.

### Human-assisted correctness

Some episodes are counted as correct after human escalation. Consequently, raw correctness can overstate autonomous recovery ability. Human-query frequency and autonomous correctness should therefore be considered alongside overall correctness.

### Model and sampling scope

The main evaluation uses a single local model and a single experimental seed. The bootstrap analysis is performed over the available tasks and fault cells rather than over multiple independent model-sampling seeds. The results therefore provide evidence for the tested configuration rather than establishing model-independent generalization.

---

## Overall Interpretation

Across the final evaluation, the explicit failure-aware B5 policy achieves the strongest overall combination of task correctness, low regret, low loop rate, low latency, and low token usage.

The history-aware LLM strategy B4 performs substantially better than the current-error-only B2 strategy, demonstrating the importance of retaining failure context. However, B4's tendency to repeatedly select parameter modification leads to inefficient recovery in several non-parameter failure classes.

The results therefore support the central conclusion that **effective failure recovery requires more than simply retrying or replanning: the recovery strategy must be conditioned on the observed failure and the accumulated evidence about whether the current recovery path remains viable.**