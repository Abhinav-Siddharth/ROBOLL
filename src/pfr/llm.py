"""Ollama wrapper: schema-constrained JSON output, on-disk cache, token and latency accounting."""
from __future__ import annotations

import hashlib
import json
import os
import time

from jsonschema import ValidationError, validate

from . import stub_llm

CACHE_DIR = os.environ.get("PFR_CACHE", "results/cache")


def _ollama_chat(model, messages, schema, seed, temp):
    import ollama  # imported here so tests and --model stub work without it

    t0 = time.time()
    r = ollama.chat(
        model=model, messages=messages, format=schema,
        options={"temperature": temp, "seed": seed, "num_ctx": 4096},
    )
    return {
        "content": json.loads(r.message.content),
        "tokens": (r.prompt_eval_count or 0) + (r.eval_count or 0),
        "latency_s": time.time() - t0,
    }


def call(model, messages, schema, seed, temp=0.7):
    """Returns {"content": dict|None, "tokens": int, "latency_s": float}. Cached on disk."""
    if model == "stub":
        return stub_llm.respond(messages, schema, seed)
    key = hashlib.sha256(json.dumps([model, messages, schema, seed, temp], sort_keys=True).encode()).hexdigest()
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    out = None
    for attempt in range(3):  # a parse failure gets 2 more tries with a different seed
        try:
            out = _ollama_chat(model, messages, schema, seed + 100003 * attempt, temp)
            validate(out["content"], schema)
            break
        except (json.JSONDecodeError, KeyError, AttributeError, ValidationError):
            out = None
            continue
    if out is None:
        return {"content": None, "tokens": 0, "latency_s": 0.0}
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f)
    os.replace(tmp, path)
    return out


class LLMClient:
    """One per episode. Derives a fresh seed for every call and totals tokens and latency."""

    def __init__(self, model: str, base_seed: int = 0, temp: float = 0.7):
        self.model, self.base_seed, self.temp = model, base_seed, temp
        self.n_calls = 0
        self.tokens = 0
        self.latency = 0.0
        self.parse_failures = 0

    def call(self, messages, schema):
        seed = self.base_seed * 1000 + self.n_calls
        self.n_calls += 1
        out = call(self.model, messages, schema, seed, self.temp)
        self.tokens += out["tokens"]
        self.latency += out["latency_s"]
        if out["content"] is None:
            self.parse_failures += 1
        return out["content"]
