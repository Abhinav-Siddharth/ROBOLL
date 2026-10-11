import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify_manifest', ROOT/'scripts/verify_manifest.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(root):
    path = root/'results/raw/example.jsonl'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'example\n')
    manifest = root/'results/MANIFEST.sha256'
    manifest.write_text(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  results/raw/example.jsonl\n')
    return path, manifest


def test_committed_manifest_cli():
    result = subprocess.run([sys.executable, str(ROOT/'scripts/verify_manifest.py')],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'MANIFEST OK:' in result.stdout


def test_known_manifest(tmp_path):
    fixture(tmp_path)
    assert module.verify(tmp_path) == 1


@pytest.mark.parametrize('mutation', ['change', 'remove', 'extra'])
def test_manifest_detects_mutations(tmp_path, mutation):
    path, _ = fixture(tmp_path)
    if mutation == 'change':
        path.write_bytes(b'changed')
    elif mutation == 'remove':
        path.unlink()
    else:
        path.with_name('extra.jsonl').write_bytes(b'extra')
    with pytest.raises(ValueError, match='missing, extra, or changed'):
        module.verify(tmp_path)


def test_manifest_rejects_duplicate(tmp_path):
    _, manifest = fixture(tmp_path)
    manifest.write_text(manifest.read_text()*2)
    with pytest.raises(ValueError, match='Duplicate'):
        module.verify(tmp_path)
