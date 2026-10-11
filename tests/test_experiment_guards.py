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
