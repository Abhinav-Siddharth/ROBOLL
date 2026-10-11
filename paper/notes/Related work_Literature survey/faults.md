NONE   OK              ok
TR-T1  EXEC_TRANSIENT  execution error: motion timeout
TR-T2  EXEC_TRANSIENT  execution error: motion timeout
TR-T3  EXEC_TRANSIENT  execution error: motion timeout
TR-P   EXEC_TRANSIENT  execution error: motion timeout
PAR-F  PARAM_MISMATCH  grasp invalid for apple
PAR-P  PARAM_MISMATCH  grasp invalid for apple
ST-F   STATE_MISMATCH  object not found at current location
ST-P   STATE_MISMATCH  object not found at current location
PRE-F  PRECOND_UNMET   precondition: prior visit to sink required
PRE-P  PRECOND_UNMET   precondition: prior visit to sink required

## Oracle attempts

The recovery oracle uses the forced initial attempt convention: execute the original
anchor once before reacting with knowledge of the fault. This is not an unrestricted
clairvoyant minimum:

- NONE = 1
- TR-T1 = 2
- TR-T2 = 3
- TR-T3 = 4
- Permanent (P) = 1
- Fixable non-transient (F) = 2

## Regret

Regret measures extra attempts beyond the oracle:

regret = max(0, attempts_on_faulted_step - oracle_attempts)

Literal anchor regret and total failure cost are separately derived from traces. The
archived runner field uses episode-wide failures and is labeled legacy regret.
