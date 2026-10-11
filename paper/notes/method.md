# Method

## 1. Experimental Environment

We evaluate LLM-based failure recovery in a controlled, state-based robot-task simulator implemented in Python. The environment maintains the world state, executes robot skill calls, checks skill preconditions, exposes observations, and determines whether the task goal has been satisfied. The simulator is intentionally discrete and deterministic, allowing recovery behavior to be evaluated independently of physical dynamics and rendering.

The benchmark contains 20 predefined tasks, with each task consisting of a clean initial state, a goal condition, and a plan of 4–8 actions. The experiment uses a fixed skill library and evaluates how different recovery strategies respond when an execution failure occurs.

## 2. Controlled Failure Injection

Failures are injected at the first `pick` action of each task, referred to as the faulted step. We evaluate 11 fault cells covering transient execution failures, permanent execution failures, parameter mismatches, state mismatches, and unmet preconditions.

The fault cells include:
- `NONE`: no injected fault.
- `TR-T1`, `TR-T2`, `TR-T3`: transient execution failures lasting 1, 2, or 3 failed attempts before succeeding.
- `TR-P`: permanent execution failure.
- `PAR-F` / `PAR-P`: fixable or permanent parameter mismatch.
- `ST-F` / `ST-P`: fixable or permanent state mismatch.
- `PRE-F` / `PRE-P`: fixable or permanent precondition failure.

Fixable and permanent variants expose the same initial error code and detail; their difference is determined by whether the failure can ultimately be resolved.

## 3. Recovery Methods

We compare six recovery strategies:

- **B0:** repeatedly retries the failed action until the failure cap is reached.
- **B1:** allows three total attempts and then abstains.
- **B2:** uses the LLM to select a recovery mode using only the current error.
- **B3:** always asks the LLM to generate a new plan after failure, without failure history.
- **B4:** uses the LLM with the full failure history, remaining budget, and untried parameter values to select a recovery mode.
- **B5:** applies explicit recovery rules based on the failure code and counts: retry for transient failures, modify parameters until values are exhausted, replan for state/precondition failures, and escalate after sufficient failures.

For B2, B4, and B5, parameter modifications and replanning are generated using the same underlying LLM prompts; their difference lies in how the recovery mode is selected.

## 4. Episode Execution

Each episode begins from the task's initial state. The agent executes the task plan one action at a time. When the faulted action fails, the selected recovery method determines the next response, such as retrying, modifying parameters, replanning, escalating to a human, or abstaining. The resulting action is executed in the simulator, which updates the world state and returns an execution result. The process continues until the task succeeds, the agent abstains or escalates, or the failure cap is exceeded.

This provides an end-to-end evaluation in which recovery decisions are not judged only as text responses: the selected actions are actually executed and their consequences determine the episode outcome.

## 5. Evaluation Metrics

The forced initial attempt convention fixes the original plan until its first faulted
pick is attempted. A recovery oracle then knows the fault. Its anchor baseline is
NONE 1, TR-Tn n+1, fixable 2, permanent 1. An unrestricted clairvoyant planner could
avoid the first failure on fixable cells; that is not the baseline used here.

Derived anchor_attempts counts all calls matching the original first pick's object.
anchor_regret = max(0, anchor_attempts - oracle_attempts). Total failure cost counts
all non-OK execution steps. The archived runner's regret counts all failures plus an
indicator of anchor success, then subtracts the oracle. It is retained as legacy
regret for the original hypothesis analysis; it is not literal anchor regret.

raw_correct counts success on solvable cells and abstain/escalate on permanent cells.
no_human_correct also requires zero human queries. autonomous_solvable_or_permanent_correct
requires zero human queries only on solvable cells and retains permanent human escalation.
Autonomous success and human-assisted success are also reported separately.

B4 adds a context bundle relative to B2: history, counts, remaining budget and untried
values. This comparison alone does not isolate history. True observations in replanning
distinguish ST-F from ST-P; identical initial messages do not make the states identical.
