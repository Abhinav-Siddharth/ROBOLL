"""One JSONL row per episode. Append-only so a crashed run can resume."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def log_episode(row: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    _repair_tail(path)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()


def load_done_ids(path: str) -> set:
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        done.add(json.loads(line)["episode_id"])
                    except (json.JSONDecodeError, KeyError):
                        pass  # a half-written last line after a crash: ignore, it will be re-run
    return done


def _repair_tail(path):
    """Preserve an interrupted final record separately before an append."""
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return
    with p.open('r+b') as f:
        # Inspect only the final record; normal appends do not read the whole log.
        end = f.seek(0, os.SEEK_END)
        f.seek(end-1)
        if f.read(1) == b'\n':
            return
        position = end
        start = 0
        chunks = []
        while position:
            size = min(position, 4096)
            position -= size
            f.seek(position)
            chunk = f.read(size)
            split = chunk.rfind(b'\n')
            if split >= 0:
                chunks.insert(0, chunk[split+1:])
                start = position+split+1
                break
            chunks.insert(0, chunk)
        tail = b''.join(chunks)
        try:
            record = json.loads(tail)
            valid = isinstance(record, dict) and isinstance(record.get('episode_id'), str)
        except (json.JSONDecodeError, UnicodeDecodeError):
            valid = False
        if valid:
            f.seek(end)
            f.write(b'\n')
        else:
            quarantine = p.with_name(p.name+'.partial-'+hashlib.sha256(tail).hexdigest()[:16])
            if not quarantine.exists():
                with quarantine.open('xb') as q:
                    q.write(tail)
                    q.flush()
                    os.fsync(q.fileno())
            elif quarantine.read_bytes() != tail:
                raise RuntimeError('Quarantine path collision; refusing to discard tail')
            f.truncate(start)
        f.flush()
        os.fsync(f.fileno())
