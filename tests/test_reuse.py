import pytest
from pfr.llm import LLMClient
from pfr.runner import run_episode
from pfr.methods import make_method
from pfr.tasks import TASKS


def test_reuse_requires_exact_deterministic_trace():
    from pfr.reuse import verified_reuse
    row = run_episode(TASKS[0], 'TR-T1', 0, make_method('B0'), LLMClient('qwen2.5:7b'))
    row['prompt_version'] = 'v1'
    reused = verified_reuse(row, 'a'*64, 'test-commit')
    assert reused['reused'] is True
    assert reused['steps'] == row['steps']
    assert reused['prompt_version'] == 'v1'
    assert reused['reuse_source_sha256'] == 'a'*64
    bad = {**row, 'regret': 99}
    with pytest.raises(ValueError):
        verified_reuse(bad, 'a'*64, 'test-commit')


def test_faulted_llm_method_cannot_be_marked_reused():
    from pfr.reuse import verified_reuse
    row = {'method': 'B2', 'cell': 'ST-F', 'llm_calls': 0}
    with pytest.raises(ValueError):
        verified_reuse(row, 'a'*64, 'test-commit')
