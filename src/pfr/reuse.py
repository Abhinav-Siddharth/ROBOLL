"""Prove selected v1 rows are unaffected before explicitly reusing them."""
import copy
from .llm import LLMClient
from .methods import make_method
from .runner import run_episode
from .tasks import get_task


class NoInferenceClient(LLMClient):
    def call(self, *args, **kwargs):
        raise AssertionError('Reused rows must never request a model')


def verified_reuse(row, source_hash, verification_commit):
    if (row['method'] not in ('B0', 'B1') and row['cell'] != 'NONE') or row['llm_calls'] != 0:
        raise ValueError('Only deterministic B0/B1 or clean NONE rows may be reused')
    fresh = run_episode(get_task(row['task']), row['cell'], row['seed'],
                        make_method(row['method']), NoInferenceClient(row['model'], row['seed']))
    differences = [key for key in fresh if key != 'prompt_version' and fresh[key] != row.get(key)]
    if differences:
        raise ValueError('Deterministic reuse disagrees on: '+', '.join(differences))
    reused = copy.deepcopy(row)
    reused.update(reused=True, dataset_version='v2-format',
                  reuse_source_file='results/raw/qwen.jsonl',
                  reuse_source_episode_id=row['episode_id'],
                  reuse_source_sha256=source_hash, reuse_source_git_ref='pre-phase2',
                  reuse_verification_commit=verification_commit,
                  reuse_verification='Exact row-field comparison except prompt-version label; model calls forbidden')
    return reused
