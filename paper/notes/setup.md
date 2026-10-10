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

## Limitations & Disclosures
The 3D replay is a kinematic visualisation without contact physics; it does not constitute evidence of physical executability.
A generator bug (ST-F hidden location equal to the goal in 6/20 tasks) was found after the main run; candidate location sampling was fixed to exclude the target goal, affected episodes (72 total) were re-run, and pre-fix data was archived (`results/raw/qwen_pre_fix.jsonl`). Method rankings on correctness and regret were completely unchanged (`results/tables/st_f_sensitivity.csv`).


