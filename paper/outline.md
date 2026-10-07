# Paper outline (6-8 pages, adjust to the course template and page limit)

| Section | Pages | Must contain | Source in repo |
|---|---|---|---|
| Abstract | 0.2 | problem, setup, 2 numbers from the results, 1 limitation | results/tables/overall.csv |
| 1 Introduction | 0.8 | the failure -> retry loop problem, gap, 3 contributions, what is NOT claimed | paper/claim.md |
| 2 Related Work | 0.8 | CAPE; FRAMES; Reflective TTP; Retry/Switch/Abstain; Self-Healing Orchestrators; Graph Harness; say how you differ from each | paper/notes/*.md |
| 3 Problem Formulation | 0.6 | state, skill call, failure code, five recovery actions, regret, correctness | src/pfr/env.py docstring |
| 4 Method | 1.0 | B0-B5 definitions, B5 rules + thresholds, prompts (summarised) | src/pfr/methods/, configs/policy.yaml |
| 5 Experimental Setup | 1.0 | simulator, 20 tasks, 11-cell fault table, oracle attempts, model, 1 seed, bootstrap | src/pfr/faults.py |
| 6 Results | 1.5 | Fig 1 heatmap, Fig 2 regret by regime, Fig 3 decisions, hypotheses table | figures/, results/tables/ |
| 7 Discussion + Limitations | 0.6 | what B4 vs B5 shows; oracle code, oracle plan, simulator, fixed menu, one model, one seed, hand-built faults | |
| 8 Conclusion | 0.2 | |  |

Rules: every number in the text comes from results/tables/*.csv; every cited paper was opened; claims match prereg.md.
