import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_freeze_records_environment_and_snapshot_scope():
    meta = json.loads((ROOT/'results/meta.txt').read_text().split('\nPFR_PHASE2_PROVENANCE_JSON\n', 1)[1])
    assert meta['python_version'].startswith('3.12.3')
    assert meta['os'].startswith('Linux-')
    assert 'not queried in Phase 3' in meta['phase3_metadata_note']
    lock = (ROOT/'requirements.lock').read_text().splitlines()
    assert 'pytest==9.1.1' in lock
    assert 'numpy==2.5.3' in lock
    assert '-e /home/abhi_pop/pfr' in lock
