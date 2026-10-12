import json
from pathlib import Path

import pytest

from pfr.phase3b_runtime import (BatchHealth, BatchStopped, CacheMismatch,
    Phase3bLLMClient, assert_hashes, check_model_metadata, episode_namespace,
    file_hash, protected_output, run_coordinates, safe_run_id)

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = dict(model_digest='test-digest', ollama_version='0.40.0', num_ctx=4096)
SCHEMA = {'type':'object','properties':{'x':{'type':'integer'}},'required':['x']}


def client(tmp_path, backend, **kwargs):
    return Phase3bLLMClient('test', cache_dir=tmp_path, namespace='unique-test-run',
                            identity=IDENTITY, backend=backend, **kwargs)


def good(*args):
    return dict(content={'x':1}, tokens=2, latency_s=.25)


def test_cold_response_and_offline_replay_have_matching_payload(tmp_path):
    a = client(tmp_path, good, cold=True)
    assert a.call([], SCHEMA) == {'x':1}
    assert a.health.completed_responses == 1 and a.cache_hits == 0
    def prohibited(*args):
        raise AssertionError('backend must not be invoked')
    b = client(tmp_path, prohibited, offline=True)
    assert b.call([], SCHEMA) == {'x':1}
    assert b.cache_hits == b.n_calls == 1
    assert b.health.backend_attempts == 0
    assert b.tokens == a.tokens and b.latency == a.latency
    with pytest.raises(CacheMismatch, match='Cold'):
        client(tmp_path, good, cold=True).call([], SCHEMA)


def test_missing_offline_cache_never_calls_backend(tmp_path):
    def prohibited(*args):
        raise AssertionError('backend must not be invoked')
    with pytest.raises(CacheMismatch, match='Offline cache miss'):
        client(tmp_path, prohibited, offline=True).call([], SCHEMA)


@pytest.mark.parametrize('mutation', ['identity','content','tokens','latency'])
def test_cache_mutations_fail_closed(tmp_path, mutation):
    a = client(tmp_path, good); a.call([], SCHEMA)
    path = tmp_path/(a.cache_keys[0]+'.json'); saved=json.loads(path.read_text())
    if mutation == 'identity': saved['request_identity']['seed']=7
    if mutation == 'content': saved['content']={'x':'not an integer'}
    if mutation == 'tokens': saved['tokens']=-1
    if mutation == 'latency': saved['latency_s']=-1
    path.write_text(json.dumps(saved))
    with pytest.raises(CacheMismatch):
        client(tmp_path, good, offline=True).call([], SCHEMA)


def test_strict_one_percent_boundary():
    h=BatchHealth(completed_responses=99)
    h.completed(invalid=True)
    assert h.json_schema_failures == 1 and h.completed_responses == 100
    with pytest.raises(BatchStopped, match='exceeds 1%'):
        h.completed(invalid=True)


def test_early_malformed_response_aborts_and_is_retained(tmp_path):
    def invalid(*args): return dict(content={'x':'wrong'},tokens=1,latency_s=.1)
    a=client(tmp_path, invalid)
    with pytest.raises(BatchStopped, match='1/1'):
        a.call([], SCHEMA)
    assert a.health.backend_attempts == a.health.json_schema_failures == 1
    assert a.health.events[0]['invalid_response'] == {'x':'wrong'}
    assert not list(tmp_path.glob('*.json'))


def test_permitted_retry_preserves_frozen_seed_progression(tmp_path):
    seeds=[]
    def backend(model,messages,schema,seed,temp):
        seeds.append(seed)
        return dict(content={'x':'invalid'} if len(seeds)==1 else {'x':1},tokens=2,latency_s=.1)
    h=BatchHealth(completed_responses=199)
    a=client(tmp_path, backend, base_seed=2, health=h)
    assert a.call([], SCHEMA) == {'x':1}
    assert seeds == [2000,102003]
    assert a.parse_retries == 1 and h.json_schema_failures == 1
    assert h.completed_responses == 201


def test_transport_failure_is_distinct_and_stops(tmp_path):
    def backend(*args): raise ConnectionError('server unavailable')
    a=client(tmp_path, backend)
    with pytest.raises(BatchStopped,match='Transport'):
        a.call([],SCHEMA)
    assert a.health.transport_failures==1 and a.health.completed_responses==0


def test_grid_sizes_and_noise_coordinates_are_frozen():
    spec=json.loads((ROOT/'configs/phase3b_hypotheses.json').read_text())
    for design,n in [('seed1',1320),('seed2',1320),('second_model',800),
                     ('noise_p01',600),('noise_p02',600),('noise_p03',600)]:
        coords=run_coordinates(spec,design)
        assert len(coords)==n
        if design.startswith('noise'):
            assert {c['noise_p'] for c in coords} == {int(design[-2:])/10}
    assert len(run_coordinates(spec,'second_model',smoke=True))==50
    assert len(run_coordinates(spec,'seed1',smoke=True))==20


def test_episode_namespaces_are_isolated():
    a=dict(task='t01',cell='ST-F',method='B5',seed=0,noise_p=.2)
    b={**a,'method':'B4'}
    assert episode_namespace('run-a','model',a)!=episode_namespace('run-a','model',b)
    assert episode_namespace('run-a','model',a)!=episode_namespace('run-b','model',a)


def test_original_output_and_existing_new_output_are_protected(tmp_path):
    allowed=['results/raw/new.jsonl']
    with pytest.raises(BatchStopped): protected_output(tmp_path,'results/raw/qwen_v2.jsonl',allowed)
    path=protected_output(tmp_path,allowed[0],allowed)
    path.parent.mkdir(parents=True);path.write_text('{}\n')
    with pytest.raises(BatchStopped): protected_output(tmp_path,allowed[0],allowed)
    with pytest.raises(BatchStopped): protected_output(tmp_path,'../new.jsonl',allowed)


def test_frozen_input_mutation_is_rejected(tmp_path):
    p=tmp_path/'amendment.md';p.write_text('frozen')
    expected={'amendment.md':file_hash(p)}
    assert_hashes(tmp_path,expected)
    p.write_text('changed')
    with pytest.raises(BatchStopped):assert_hashes(tmp_path,expected)


def test_changed_model_identity_is_rejected():
    spec={'ollama_version':'0.40.0','qwen_model':'qwen','qwen_digest':'old','second_model':'llama'}
    tags={'models':[{'name':'qwen','digest':'changed','size':123}]}
    with pytest.raises(BatchStopped,match='digest'):
        check_model_metadata('qwen',spec,tags,{'version':'0.40.0'}, {})


@pytest.mark.parametrize('value',['../escape','bad id','', 'x'*101])
def test_run_id_rejects_unsafe_names(value):
    with pytest.raises(ValueError):safe_run_id(value)
