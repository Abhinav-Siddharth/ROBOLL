import pytest

from pfr.core import Ctx
from pfr.env import Call, Result
from pfr.methods import make_method

POLICY = "configs/policy.yaml"
CALL = Call("pick", {"obj": "apple", "grasp": "top"})


def ctx(code, past_codes=(), untried=(), detail="x", max_failures=8):
    hist = [{"call": CALL.to_flat(), "code": c, "detail": "x", "decision": "retry"} for c in past_codes]
    res = Result(ok=False, code=code, detail=detail, param_field="grasp" if code == "PARAM_MISMATCH" else None)
    return Ctx(task={"goal_text": "t"}, call=CALL, result=res, history=hist, n_fail=len(hist) + 1,
               max_failures=max_failures, param_field="grasp", untried=list(untried))


def test_b0_always_retries():
    m = make_method("B0")
    assert m.on_failure(ctx("PARAM_MISMATCH")).mode == "retry"
    assert m.on_failure(ctx("EXEC_TRANSIENT", ["EXEC_TRANSIENT"] * 6)).mode == "retry"


def test_b1_aborts_at_exactly_three():
    m = make_method("B1")
    modes = [m.on_failure(ctx("EXEC_TRANSIENT", ["EXEC_TRANSIENT"] * k)).mode for k in range(5)]
    assert modes == ["retry", "retry", "abstain", "abstain", "abstain"]


def test_b3_always_replans():
    assert make_method("B3").on_failure(ctx("EXEC_TRANSIENT")).mode == "replan"


# ---- B5, every branch
def b5():
    return make_method("B5", POLICY)


def test_b5_transient_retries_then_escalates():
    m = b5()
    T = "EXEC_TRANSIENT"
    assert [m.on_failure(ctx(T, [T] * k)).mode for k in range(3)] == ["retry"] * 3   # failures 1..3
    assert m.on_failure(ctx(T, [T] * 3)).mode == "escalate"                          # failure 4: cap exceeded


def test_b5_param_modifies_while_untried_then_abstains():
    m = b5()
    P = "PARAM_MISMATCH"
    assert m.on_failure(ctx(P, [], untried=["side", "pinch"])).mode == "modify"
    assert m.on_failure(ctx(P, [P], untried=["pinch"])).mode == "modify"
    assert m.on_failure(ctx(P, [P, P], untried=[])).mode == "abstain"


def test_b5_state_replans_twice_then_abstains():
    m = b5()
    S = "STATE_MISMATCH"
    assert m.on_failure(ctx(S, [])).mode == "replan"
    assert m.on_failure(ctx(S, [S])).mode == "replan"
    assert m.on_failure(ctx(S, [S, S])).mode == "abstain"


def test_b5_precondition_replans_twice_then_abstains():
    m = b5()
    C = "PRECOND_UNMET"
    assert m.on_failure(ctx(C, [])).mode == "replan"
    assert m.on_failure(ctx(C, [C])).mode == "replan"
    assert m.on_failure(ctx(C, [C, C])).mode == "abstain"


def test_b5_total_budget_escalates():
    m = b5()
    mixed = ["EXEC_TRANSIENT", "STATE_MISMATCH", "PRECOND_UNMET", "EXEC_TRANSIENT", "STATE_MISMATCH"]
    assert m.on_failure(ctx("PRECOND_UNMET", mixed)).mode == "escalate"   # n_fail = 6


def test_b5_exhausted_action_is_configurable():
    m = b5()
    m.p = dict(m.p, exhausted_action="abstain")
    T = "EXEC_TRANSIENT"
    assert m.on_failure(ctx(T, [T] * 3)).mode == "abstain"


def test_b5_counts_codes_not_just_steps():
    """History matters: the same current failure gets a different decision after a longer history."""
    m = b5()
    S = "STATE_MISMATCH"
    assert m.on_failure(ctx(S, [])).mode != m.on_failure(ctx(S, [S, S])).mode


def test_registry_names():
    for n in ["B0", "B1", "B2", "B3", "B4", "B5"]:
        assert make_method(n, POLICY).name == n
