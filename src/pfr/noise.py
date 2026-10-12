"""Preregistered diagnostic corruption, separate from execution truth."""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

from .env import Call, Result


VERSION = "phase3b-code-noise-v1"
FAILURE_CODES = ("EXEC_TRANSIENT", "PARAM_MISMATCH", "STATE_MISMATCH", "PRECOND_UNMET")
CANONICAL_DETAILS = {
    "EXEC_TRANSIENT": "execution error: motion timeout",
    "PARAM_MISMATCH": "parameter invalid for this skill execution",
    "STATE_MISMATCH": "observed state does not match the expected state",
    "PRECOND_UNMET": "precondition for this skill execution is not satisfied",
}


@dataclass(frozen=True)
class CodeNoise:
    task_id: str
    cell: str
    environment_seed: int
    p: float

    def __post_init__(self):
        if not 0 <= self.p <= 1 or abs(self.p * 100 - round(self.p * 100)) > 1e-9:
            raise ValueError("Noise probability must be an integer percentage in [0, 1]")
        if not isinstance(self.environment_seed, int):
            raise ValueError("Environment seed must be an integer")

    def __call__(self, result: Result, call: Call, attempt_no: int):
        # Neither the action nor hidden environment state enters the random key.
        if self.p == 0 or result.ok:
            return result, {}
        if result.code not in FAILURE_CODES or attempt_no < 1:
            raise ValueError("Expected a known failed result and one-based attempt")
        percentage = round(self.p * 100)
        identity = [VERSION, self.task_id, self.cell, self.environment_seed, attempt_no, percentage]
        encoded = json.dumps(identity, separators=(",", ":"), ensure_ascii=True)
        key = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        rng = random.Random(int(key, 16))
        draw = rng.random()
        corrupted = draw < self.p
        observed = result
        if corrupted:
            candidates = [code for code in FAILURE_CODES if code != result.code]
            code = candidates[rng.randrange(len(candidates))]
            # Parameter hints remain derived from the action in the runner, not
            # from the true diagnosis. Do not carry diagnostic param_field data.
            observed = Result(ok=False, code=code, detail=CANONICAL_DETAILS[code])
        return observed, {
            "observed_code": observed.code,
            "observed_detail": observed.detail,
            "noise_corrupted": corrupted,
            "noise_draw": draw,
            "noise_key": key,
            "noise_key_version": VERSION,
        }


def make_observer(task, cell, environment_seed, p):
    """Return the runner callback; a zero-probability callback is a strict no-op."""
    task_id = task["id"] if isinstance(task, dict) else task
    return CodeNoise(task_id, cell, environment_seed, p)
