import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_snapshot_records_immutable_identity_and_options():
    text = (ROOT/'results/meta.txt').read_text()
    marker = '\nPFR_PHASE2_PROVENANCE_JSON\n'
    assert marker in text
    meta = json.loads(text.split(marker, 1)[1])
    assert len(meta['model_digest']) == 64
    assert meta['ollama_server_version']
    assert meta['model'] == 'qwen2.5:7b'
    assert meta['options'] == {'temperature': 0.7, 'num_ctx': 4096}
    assert meta['seed_rule'] == 'base_seed * 1000 + call_index'
