"""One JSONL row per episode. Append-only so a crashed run can resume."""
from __future__ import annotations

import json
import os


def log_episode(row: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
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
