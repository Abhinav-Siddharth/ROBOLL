Title (working): Managing Persistent Execution Failures in LLM-Based Robotic Agents: A Controlled Study of History-Aware Recovery Decisions

RQ: Under persistent execution failures, does accumulated failure history improve the choice among retry / modify / replan / escalate / abstain?

Gap: Work on LLM agents already studies retry / switch / abstain decisions and budgeted recovery policies
(Retry, Switch, or Abstain? 2608.11977; Self-Healing Agentic Orchestrators 2606.01416; Graph Harness 2604.11378),
and embodied systems add monitoring, replanning and memory (CAPE, FRAMES 2609.22538, Reflective Test-Time Planning 2602.21198).
What is missing is a controlled study in EMBODIED skill execution where persistent and fixable faults produce
identical failure messages, so only the failure history can tell them apart.

Contributions:
 (1) a fault benchmark of 11 cells (transient T1-T3, fixable, permanent) with identical surface symptoms for F and P faults;
 (2) a training-free explicit history-aware recovery policy (B5) and an LLM-with-history counterpart (B4) given the same information;
 (3) a controlled evaluation with regret against an oracle attempt count, reporting both all-cell correctness (+13.2% for B5) and purely autonomous correctness (+19.5% for B5, as B4's F-cell advantage is human-assisted);
 (4) an empirical characterization of structural argument omission (e.g. invalid calls in replanning) in open-weight 7B planners under JSON schemas.

Assumptions (state them in the paper): an oracle monitor supplies a structured failure code; the initial plan is an oracle plan;
the skill menu is fixed; everything runs in a simulator; one 7B model, one seed.

Not solved: perception-based diagnosis, learned recovery, sim-to-real, safety certification.

Claims we do NOT make: that we are first to study retry/replan/abstain for LLM agents; that B5 beats a state-of-the-art system.
