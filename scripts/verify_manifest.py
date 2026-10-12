#!/usr/bin/env python
"""Verify the frozen result inventory without writing or running models."""
import argparse
import hashlib
from pathlib import Path

DIRECTORIES = ('results/raw', 'results/tables', 'results/derived_v1', 'results/v2',
               'results/derived_v3')


def safe_path(root, name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Unsafe manifest path')
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('Unsafe manifest symlink')
    return resolved


def inventoried(name):
    return any(name == d or name.startswith(d + '/') for d in DIRECTORIES)


def inventory(root, extra_files=()):
    root = Path(root).resolve()
    paths = [p for directory in DIRECTORIES for p in (root / directory).rglob('*')
             if p.is_file()]
    paths += [safe_path(root, name) for name in extra_files
              if safe_path(root, name).is_file()]
    return {p.relative_to(root).as_posix(): hashlib.sha256(safe_path(
                root, p.relative_to(root).as_posix()).read_bytes()).hexdigest() for p in paths}


def verify(root, manifest=None, *, allow_new=()):
    root = Path(root).resolve()
    manifest = Path(manifest) if manifest else root / 'results/MANIFEST.sha256'
    expected = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split('  ', 1)
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid SHA256')
        if name in expected or name.startswith('/') or '..' in Path(name).parts:
            raise ValueError('Duplicate or unsafe manifest path')
        safe_path(root, name)
        expected[name] = digest
    permitted = set(allow_new)
    if permitted & expected.keys():
        raise ValueError('Cannot exempt a frozen manifest entry')
    for name in permitted:
        safe_path(root, name)
        if not inventoried(name):
            raise ValueError('New artifact exemption must be in an inventoried directory')
    actual = inventory(root, [name for name in expected if not inventoried(name)])
    actual = {name: digest for name, digest in actual.items() if name not in permitted}
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
