#!/usr/bin/env python
"""Verify the frozen result inventory without writing or running models."""
import argparse
import hashlib
from pathlib import Path

DIRECTORIES = ('results/raw', 'results/tables', 'results/derived_v1', 'results/v2')


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for directory in DIRECTORIES for p in (root / directory).rglob('*') if p.is_file()}


def verify(root, manifest=None):
    root = Path(root).resolve()
    manifest = Path(manifest) if manifest else root / 'results/MANIFEST.sha256'
    expected = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split('  ', 1)
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid SHA256')
        if name in expected or name.startswith('/') or '..' in Path(name).parts:
            raise ValueError('Duplicate or unsafe manifest path')
        expected[name] = digest
    actual = inventory(root)
    problems = [f'{name}: missing, extra, or changed' for name in sorted(expected.keys() | actual.keys())
                if expected.get(name) != actual.get(name)]
    if problems:
        raise ValueError('\n'.join(problems))
    return len(expected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    try:
        count = verify(args.root, args.manifest)
    except (OSError, ValueError) as error:
        parser.exit(1, f'MANIFEST FAIL: {error}\n')
    print(f'MANIFEST OK: {count} files; no missing, extra, or changed files')
