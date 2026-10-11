import copy
import pytest
from pfr.llm import LLMClient
from pfr.methods import make_method
from pfr.runner import run_episode
from pfr.tasks import TASKS
from pfr.viz.state import reconstruct, ReplayMismatch


@pytest.mark.parametrize('mutation', ['detail', 'attempt', 'outcome', 'correct'])
def test_replay_rejects_metadata_mutations(mutation):
    row = run_episode(TASKS[0], 'NONE', 0, make_method('B0'), LLMClient('stub', 0))
    if mutation == 'detail':
        row['steps'][0]['detail'] = 'fabricated'
    elif mutation == 'attempt':
        row['steps'][0]['attempt'] = 4
    elif mutation == 'outcome':
        row['outcome'] = 'incomplete'
    else:
        row['correct'] = False
    with pytest.raises(ReplayMismatch):
        reconstruct(row)


def test_replay_rejects_success_with_unsatisfied_goal():
    row = run_episode(TASKS[0], 'TR-P', 0, make_method('B0'), LLMClient('stub', 0))
    row['outcome'] = 'success'
    row['correct'] = True
    with pytest.raises(ReplayMismatch):
        reconstruct(row)
