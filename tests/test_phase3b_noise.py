import copy
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys

import pytest

from pfr.core import Decision
from pfr.env import Call, Env, Result
from pfr.faults import CELLS, FaultyEnv, build_fault
from pfr.llm import LLMClient
from pfr.noise import CANONICAL_DETAILS, FAILURE_CODES, CodeNoise, make_observer
from pfr.runner import run_episode
from pfr.tasks import TASKS
from pfr.viz.state import reconstruct

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('code', FAILURE_CODES)
def test_corruption_is_wrong_and_consistent(code):
    original = Result(ok=False, code=code, detail='hidden true explanation', param_field='grasp')
    observed, audit = CodeNoise('t01', 'TR-P', 0, 1)(original, Call('pick'), 2)
    assert observed.code != code
    assert observed.detail == CANONICAL_DETAILS[observed.code]
    assert observed.param_field is None
    assert original.detail == 'hidden true explanation'
    assert audit['noise_corrupted']


def test_zero_probability_preserves_original_object_and_payload():
    r = Result(ok=False, code='PRECOND_UNMET', detail='actual prerequisite')
    observed, audit = CodeNoise('t01', 'PRE-F', 0, 0)(r, Call('pick'), 1)
    assert observed is r and audit == {}


def test_noise_does_not_corrupt_success():
    r = Result(ok=True, code='OK', detail='ok')
    assert CodeNoise('t01', 'NONE', 0, 1)(r, Call('goto'), 1) == (r, {})


def test_determinism_across_process_and_action_identity():
    result = Result(ok=False, code='EXEC_TRANSIENT', detail='truth')
    expected = CodeNoise('t01', 'TR-P', 0, .2)(result, Call('pick'), 7)[1]
    assert CodeNoise('t01', 'TR-P', 0, .2)(result, Call('open'), 7)[1] == expected
    code = "from pfr.noise import CodeNoise; from pfr.env import Result,Call; import json; print(json.dumps(CodeNoise('t01','TR-P',0,.2)(Result(ok=False,code='EXEC_TRANSIENT',detail='truth'),Call('pick'),7)[1],sort_keys=True))"
    actual = json.loads(subprocess.check_output([sys.executable, '-c', code], text=True))
    assert actual == expected
    # The constructor has no LLM seed or method input; changing either cannot change a draw.
    assert set(CodeNoise.__dataclass_fields__) == {'task_id', 'cell', 'environment_seed', 'p'}


@pytest.mark.parametrize('cell', CELLS)
def test_noise_never_changes_scripted_environment_or_fault_state(cell):
    task = TASKS[0]
    left = FaultyEnv(Env(task['init_state']), build_fault(task, cell, 0))
    right = FaultyEnv(Env(task['init_state']), build_fault(task, cell, 0))
    observer = make_observer(task, cell, 0, .3)
    sequence = [Call.from_flat(s) for s in task['plan']]*3
    for attempt, action in enumerate(sequence, 1):
        a, b = left.execute(action), right.execute(action)
        if not b.ok:
            observer(b, action, attempt)
        assert a == b
        assert left.observe() == right.observe()
        assert asdict(left.fault) == asdict(right.fault)
        if attempt == 5:
            left.fault.clear(left.env)
            right.fault.clear(right.env)


def test_seeded_fault_parameters_only_change_where_expected():
    for seed, expected in ((1, 13), (2, 11)):
        for cell in CELLS:
            changed = sum(asdict(build_fault(t, cell, seed)) != asdict(build_fault(t, cell, 0))
                          for t in TASKS)
            assert changed == (expected if cell == 'ST-F' else 0)


def test_displayed_history_and_true_replay_are_separate():
    contexts = []
    class Method:
        name = 'test'
        def on_failure(self, ctx):
            contexts.append(copy.deepcopy((ctx.result.model_dump(), ctx.history)))
            return Decision('retry' if len(contexts) < 3 else 'abstain')
    row = run_episode(TASKS[0], 'TR-P', 0, Method(), LLMClient('stub'),
                      observation_transform=make_observer(TASKS[0], 'TR-P', 0, 1))
    for current, history in contexts:
        assert current['code'] != 'EXEC_TRANSIENT'
        assert current['detail'] == CANONICAL_DETAILS[current['code']]
        assert all(h['code'] != 'EXEC_TRANSIENT' for h in history)
    assert all(s['code'] == 'EXEC_TRANSIENT' for s in row['steps'] if s['code'] != 'OK')
    reconstruct(row)


def test_cutoff_failure_still_records_noise():
    class Method:
        name = 'test'
        def on_failure(self, ctx):
            return Decision('retry')
    row = run_episode(TASKS[0], 'TR-P', 0, Method(), LLMClient('stub'),
                      observation_transform=make_observer(TASKS[0], 'TR-P', 0, 1))
    assert row['steps'][-1]['decision'] == 'cutoff'
    assert row['steps'][-1]['noise_corrupted']


@pytest.mark.parametrize('mode, cell', [('modify','PAR-P'),('replan','ST-F')])
def test_modify_and_replan_receive_only_observed_diagnostics(monkeypatch, mode, cell):
    from pfr import prompts
    captured=[]
    name=mode+'_messages'; original=getattr(prompts,name)
    def spy(task, call, result, *args, **kwargs):
        captured.append((result.code,result.detail))
        return original(task,call,result,*args,**kwargs)
    monkeypatch.setattr(prompts,name,spy)
    class Method:
        name='test'
        def on_failure(self,ctx):return Decision(mode if not captured else 'abstain')
    row=run_episode(TASKS[0],cell,0,Method(),LLMClient('stub'),
                    observation_transform=make_observer(TASKS[0],cell,0,1))
    assert captured
    code,detail=captured[0]
    assert detail==CANONICAL_DETAILS[code]
    failed=next(s for s in row['steps'] if s['code']!='OK')
    assert code!=failed['code'] and detail!=failed['detail']


def test_predetermined_twenty_v2_rows_are_cache_only_exact():
    import importlib.util
    spec = importlib.util.spec_from_file_location('offline_phase3b', ROOT/'scripts/check_phase3b_offline.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    if not (ROOT/'results/cache_v2').is_dir():
        pytest.skip('Archived cache restoration is exercised separately in the clean clone')
    result = module.check(full=False)
    assert result['rows'] == 20
    assert result['execution_field_mismatches'] == result['server_requests'] == 0
    assert result['cache_hits'] == result['llm_calls']
