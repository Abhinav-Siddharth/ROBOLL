import pytest
from pfr.experiment import protect_output, validate_rows


def test_new_runs_refuse_archived_output_paths():
    with pytest.raises(ValueError):
        protect_output('results/raw/qwen.jsonl')
    with pytest.raises(ValueError):
        protect_output('results/raw/qwen_pre_fix.jsonl')


def test_validation_rejects_duplicate_and_missing_ids():
    row = {'episode_id': 'a', 'parse_failures': 0, 'steps': []}
    with pytest.raises(ValueError):
        validate_rows([row, row], {'a'})
    with pytest.raises(ValueError):
        validate_rows([row], {'a', 'b'})


def test_repeated_batch_summary_preserves_original_wall_time(tmp_path):
    import json
    from pfr.experiment import save_run_summary
    path = tmp_path/'gate-run.json'
    first = save_run_summary(path, {'wall_time_s': 700, 'newly_executed': 160})
    second = save_run_summary(path, {'wall_time_s': 0.01, 'newly_executed': 0})
    assert first == path
    assert second != path
    assert json.loads(path.read_text())['wall_time_s'] == 700
    assert json.loads(second.read_text())['newly_executed'] == 0


def test_validation_rejects_id_coordinate_disagreement_even_if_replay_matches():
    from pfr.runner import run_episode
    from pfr.llm import LLMClient
    from pfr.methods import make_method
    from pfr.tasks import TASKS
    row = run_episode(TASKS[0], 'TR-P', 0, make_method('B0'), LLMClient('qwen2.5:7b'))
    original_id = row['episode_id']
    row['task'] = 't13'  # Same anchor and initial prefix; permanent-failure replay still matches.
    with pytest.raises(ValueError):
        validate_rows([row], {original_id})
