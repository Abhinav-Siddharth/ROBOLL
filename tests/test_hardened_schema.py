import copy
import json
import pytest
from pfr import prompts, llm
from pfr.env import SKILL_ARGS

EXAMPLES = [
    {'skill': 'goto', 'loc': 'table'},
    {'skill': 'pick', 'obj': 'apple', 'grasp': 'top'},
    {'skill': 'place', 'obj': 'apple', 'loc': 'table', 'orient': 'upright'},
    {'skill': 'open', 'container': 'drawer', 'force': 'med'},
    {'skill': 'close', 'container': 'drawer'},
]


@pytest.mark.parametrize('example', EXAMPLES)
def test_schema_rejects_each_missing_skill_argument(example):
    from jsonschema import Draft202012Validator
    validator = Draft202012Validator(prompts.REPLAN_SCHEMA)
    assert validator.is_valid({'steps': [example]})
    for required in SKILL_ARGS[example['skill']]:
        missing = {k: v for k, v in example.items() if k != required}
        assert not validator.is_valid({'steps': [missing]}), required


def test_parsed_invalid_model_output_is_rejected_before_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, 'CACHE_DIR', str(tmp_path))
    monkeypatch.setattr(llm, '_ollama_chat', lambda *a: {
        'content': {'steps': [{'skill': 'place', 'obj': 'apple', 'orient': 'upright'}]},
        'tokens': 10, 'latency_s': 0.1})
    client = llm.LLMClient('test-double')
    assert client.call([], prompts.REPLAN_SCHEMA) is None
    assert client.parse_failures == 1
    assert not list(tmp_path.glob('*.json'))
