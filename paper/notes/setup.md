Experimental setup. We use a discrete tabletop kitchen simulator with five skills:
goto, pick, place, open, and close. Each skill has explicit preconditions (e.g. pick
requires the robot at the object's location and an empty gripper). There are 20
scripted tasks with plans of 4–8 steps (fetch, open drawer, place object, etc.).
State is fully observable via observe(). Failed skills return structured codes
(STATE_MISMATCH, PRECOND_UNMET, PARAM_MISMATCH, EXEC_TRANSIENT). No continuous
control or vision — this isolates recovery decisions from perception noise.

