import importlib.util
import json
from pathlib import Path
import sys

import pytest

from pfr.phase3b_runtime import BatchHealth, BatchStopped

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
try:
    spec=importlib.util.spec_from_file_location('phase3b_driver',ROOT/'scripts/run_phase3b.py')
    driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
finally:
    sys.path.pop(0)


def setup_fixture(tmp_path,monkeypatch):
    spec=json.loads((ROOT/'configs/phase3b_hypotheses.json').read_text())
    (tmp_path/'paper').mkdir();(tmp_path/spec['amendment']).write_text('frozen amendment')
    (tmp_path/'configs').mkdir();(tmp_path/'configs/phase3b_hypotheses.json').write_text(json.dumps(spec))
    (tmp_path/'results').mkdir();(tmp_path/'results/MANIFEST.sha256').write_text('')
    audit=tmp_path/'audit/phase3b/fixture';audit.mkdir(parents=True)
    meta=dict(model_digest='test',ollama_server_version='0.40.0',options={'temperature':.7,'num_ctx':4096})
    identity=dict(model_digest='test',ollama_version='0.40.0',num_ctx=4096)
    monkeypatch.setattr(driver,'prepare',lambda *a,**kw:
        ('test',{},'fixture-commit',audit,meta,identity,BatchHealth(),'fixture-namespace'))
    coordinates=[dict(task='t01',cell='NONE',method='B0',seed=1,noise_p=0)]
    monkeypatch.setattr(driver,'run_coordinates',lambda *a,**kw:coordinates)
    monkeypatch.setattr(driver.subprocess,'check_output',lambda *a,**kw:'1\n')
    return spec,audit


def test_driver_executes_checks_and_cache_verifies_without_a_backend(tmp_path,monkeypatch):
    spec,audit=setup_fixture(tmp_path,monkeypatch)
    def prohibited(*a,**kw):raise AssertionError('No model request permitted')
    monkeypatch.setattr(driver.legacy_llm,'_ollama_chat',prohibited)
    result=driver.execute(spec,'seed1','fixture',smoke=True,root=tmp_path)
    assert result['status']=='passed' and result['rows']==1
    assert result['backend_attempts']==result['cache_hits']==result['replay_mismatches']==0
    assert len((audit/'episodes.jsonl').read_text().splitlines())==1


def test_driver_retains_partial_row_and_stop_evidence(tmp_path,monkeypatch):
    spec,audit=setup_fixture(tmp_path,monkeypatch)
    def mismatch(row):raise BatchStopped('fixture replay mismatch')
    monkeypatch.setattr(driver,'check_row',mismatch)
    with pytest.raises(BatchStopped,match='replay mismatch'):
        driver.execute(spec,'seed1','fixture',smoke=True,root=tmp_path)
    summary=json.loads((audit/'summary.json').read_text())
    assert summary['status']=='stopped' and summary['completed_rows']==1
    assert len((audit/'episodes.jsonl').read_text().splitlines())==1
