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

We record task correctness, number of attempts on the faulted step, regret, loop occurrence, human escalation, token usage, and latency.

The faulted-step attempt count is the number of failed executions plus one when the anchor eventually succeeds. Oracle attempts represent the minimum number of attempts required when the fault condition is known in advance. Regret is defined as:

`regret = max(0, attempts_on_faulted_step - oracle_attempts)`

An episode is considered correct when a solvable task reaches its goal, or when an unsolvable permanent case ends in abstention or escalation.
