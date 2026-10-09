Experimental setup. We use a discrete tabletop kitchen simulator with five skills:
goto, pick, place, open, and close. Each skill has explicit preconditions (e.g. pick
requires the robot at the object's location and an empty gripper). There are 20
scripted tasks with plans of 4–8 steps (fetch, open drawer, place object, etc.).
State is fully observable via observe(). Failed skills return structured codes
(STATE_MISMATCH, PRECOND_UNMET, PARAM_MISMATCH, EXEC_TRANSIENT). No continuous
control or vision — this isolates recovery decisions from perception noise.
Episodes are executed in a symbolic simulator; for qualitative inspection we additionally replay logged traces in a PyBullet scene (kinematic visualisation, verified against the logs).

## Figure 5 Caption (Replay Contrast)
Replay of task t06 under fault cell PAR-F: (left) mid-episode step where B0 encounters PARAM_MISMATCH and retries the same grasp parameter; (right) terminal outcome where B5 modifies the grasp parameter ('side') and succeeds. Visualisation only; execution is symbolic.

## Limitations
The 3D replay is a kinematic visualisation without contact physics; it does not constitute evidence of physical executability.
For 6 of 20 tasks the ST-F hidden location coincides with the goal location; results are also reported on the remaining 14 (`results/tables/st_f_sensitivity.csv`). Across the clean 14 tasks, method rankings remain identical to the full set: B4 is the sole method achieving non-zero correctness (28.6% vs 35.0%), all other methods achieve 0.0%, and regret ordering is unchanged (B1: 1.00 < B5: 2.86 < B0/B2: 6.00 < B4: 6.29 < B3: 6.64).


