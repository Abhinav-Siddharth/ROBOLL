from pfr.core import Ctx
from pfr.env import Call, Result
from pfr.methods import make_method
from pfr import prompts


class Capture:
    def call(self, messages, schema):
        self.messages = messages
        return {'mode': 'replan', 'why': 'test'}


def test_b2c_gets_budget_and_untried_values_but_no_prior_history():
    client = Capture()
    ctx = Ctx(task={'goal_text': 'put apple on table'}, call=Call('pick', {'obj':'apple','grasp':'top'}),
              result=Result(ok=False, code='STATE_MISMATCH', detail='current error'),
              history=[{'call': {'skill':'pick'}, 'code':'STATE_MISMATCH',
                        'detail':'SECRET PRIOR EVENT', 'decision':'retry'}],
              n_fail=2, max_failures=8, param_field='grasp', untried=['side','pinch'], llm=client)
    assert make_method('B2C').on_failure(ctx).mode == 'replan'
    text = client.messages[-1]['content']
    assert 'Failures so far in this episode (including this one): 2' in text
    assert '6 remain.' in text
    assert "['side', 'pinch']" in text
    assert 'SECRET PRIOR EVENT' not in text
    assert 'Earlier failures' not in text
    assert 'first failure' not in text


def test_default_b2_and_b4_prompt_text_stays_unchanged():
    import subprocess
    import types
    old = types.ModuleType('pfr._old_prompts')
    old.__package__ = 'pfr'
    exec(subprocess.check_output(['git','show','pre-phase2:src/pfr/prompts.py'], text=True), old.__dict__)
    task = {'goal_text': 'put apple on table'}
    call = Call('pick', {'obj':'apple','grasp':'top'})
    res = Result(ok=False, code='STATE_MISMATCH', detail='current error')
    for kwargs in [{}, {'history': [], 'remaining': 7, 'untried': ['side'], 'n_fail': 1}]:
        assert prompts.mode_messages(task,call,res,**kwargs) == old.mode_messages(task,call,res,**kwargs)
