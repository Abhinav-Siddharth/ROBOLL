import hashlib
import json
from pfr import llm


def test_legacy_cache_keys_and_entries_stay_readable(tmp_path, monkeypatch):
    model, messages, schema, seed, temp = 'test-double', [], {'type': 'object'}, 0, 0.7
    old = hashlib.sha256(json.dumps([model, messages, schema, seed, temp], sort_keys=True).encode()).hexdigest()
    assert llm.cache_key(model, messages, schema, seed, temp) == old
    record = {'content': {}, 'tokens': 5, 'latency_s': 0.2}
    path = tmp_path/f'{old}.json'
    path.write_text(json.dumps(record))
    original = path.read_bytes()
    monkeypatch.setattr(llm, 'CACHE_DIR', str(tmp_path))
    monkeypatch.setattr(llm, '_ollama_chat', lambda *a: (_ for _ in ()).throw(AssertionError('inference')))
    assert llm.call(model, messages, schema, seed)['content'] == {}
    assert path.read_bytes() == original


def test_new_cache_identity_includes_digest_server_and_options():
    base = {'model_digest': 'a'*64, 'ollama_version': '0.40.0', 'num_ctx': 4096}
    key = llm.cache_key('qwen2.5:7b', [], {}, 0, 0.7, 'v2-format', base)
    assert key != llm.cache_key('qwen2.5:7b', [], {}, 0, 0.7)
    for field, value in [('model_digest', 'b'*64), ('ollama_version', 'different'), ('num_ctx', 8192)]:
        changed = {**base, field: value}
        assert key != llm.cache_key('qwen2.5:7b', [], {}, 0, 0.7, 'v2-format', changed)
