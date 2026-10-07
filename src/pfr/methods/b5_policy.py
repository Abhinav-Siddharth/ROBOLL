from ..core import Decision


class B5Policy:
    """Explicit history-aware recovery policy. Uses the failure CODE (given by the oracle monitor)
    plus how often each code has failed so far. Thresholds come from configs/policy.yaml.

      EXEC_TRANSIENT  retry while count <= transient_retry_cap, then `exhausted_action`
      PARAM_MISMATCH  modify while untried parameter values remain; none left -> abstain
      STATE_MISMATCH  replan while count <= state_replan_cap; then abstain
      PRECOND_UNMET   replan while count <= precond_replan_cap; then abstain
      any code        escalate once total failures reach total_failure_budget
    """
    name = "B5"

    def __init__(self, policy: dict):
        self.p = policy

    def on_failure(self, ctx):
        p, code = self.p, ctx.result.code
        n_code = ctx.count_code(code)
        if ctx.n_fail >= p["total_failure_budget"]:
            return Decision("escalate", "total failure budget reached")
        if code == "EXEC_TRANSIENT":
            if n_code <= p["transient_retry_cap"]:
                return Decision("retry", f"transient failure {n_code} <= cap")
            return Decision(p["exhausted_action"], "transient retries exhausted")
        if code == "PARAM_MISMATCH":
            if ctx.untried:
                return Decision("modify", "untried parameter values remain")
            return Decision("abstain", "every parameter value failed")
        if code == "STATE_MISMATCH":
            if n_code <= p["state_replan_cap"]:
                return Decision("replan", f"state mismatch {n_code} <= cap")
            return Decision("abstain", "replans did not fix the state mismatch")
        if code == "PRECOND_UNMET":
            if n_code <= p["precond_replan_cap"]:
                return Decision("replan", f"precondition failure {n_code} <= cap")
            return Decision("abstain", "replans did not fix the precondition")
        return Decision("abstain", "unknown code")
