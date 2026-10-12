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


def test_explicit_frozen_source_is_checked(tmp_path):
    _, manifest = fixture(tmp_path)
    source = tmp_path/'paper/amendment.md'
    source.parent.mkdir()
    source.write_bytes(b'prospective')
    with manifest.open('a') as f:
        f.write(hashlib.sha256(source.read_bytes()).hexdigest()+'  paper/amendment.md\n')
    assert module.verify(tmp_path) == 2
    source.write_bytes(b'changed after inference')
    with pytest.raises(ValueError, match='missing, extra, or changed'):
        module.verify(tmp_path)


def test_new_raw_exemption_cannot_hide_old_mutation(tmp_path):
    original, _ = fixture(tmp_path)
    new = original.with_name('new.jsonl')
    new.write_bytes(b'new')
    assert module.verify(tmp_path, allow_new=('results/raw/new.jsonl',)) == 1
    original.write_bytes(b'changed')
    with pytest.raises(ValueError):
        module.verify(tmp_path, allow_new=('results/raw/new.jsonl',))
    with pytest.raises(ValueError, match='Cannot exempt'):
        module.verify(tmp_path, allow_new=('results/raw/example.jsonl',))


def test_manifest_rejects_source_symlink_escape(tmp_path):
    _, manifest = fixture(tmp_path)
    (tmp_path/'escape').symlink_to('/etc/hostname')
    with manifest.open('a') as f:
        f.write('0'*64+'  escape\n')
    with pytest.raises(ValueError, match='symlink'):
        module.verify(tmp_path)


def test_new_derived_directory_is_exhaustive(tmp_path):
    _, _ = fixture(tmp_path)
    p = tmp_path/'results/derived_v3/new.csv'
    p.parent.mkdir()
    p.write_text('unlisted')
    with pytest.raises(ValueError, match='missing, extra, or changed'):
        module.verify(tmp_path)
