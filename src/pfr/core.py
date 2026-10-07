"""Small shared types: what a method sees (Ctx) and what it returns (Decision)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .env import Call, Result

MODES = ["retry", "modify", "replan", "escalate", "abstain"]


@dataclass
class Decision:
    mode: str
    why: str = ""


@dataclass
class Ctx:
    task: dict
    call: Call                      # the call that just failed
    result: Result                  # its failure result
    history: list                   # PAST failure events, oldest first (current one NOT included)
    n_fail: int                     # failures so far in this episode, INCLUDING the current one
    max_failures: int               # episode is cut off when n_fail reaches this
    param_field: Optional[str]      # the modifiable parameter of the failed skill (or None)
    untried: list                   # values of param_field not yet tried for this step
    llm: Any = None                 # LLMClient (methods that need the model use it)

    def count_code(self, code: str) -> int:
        """How many failures with this code so far, INCLUDING the current one."""
        past = sum(1 for e in self.history if e["code"] == code)
        return past + (1 if self.result.code == code else 0)

    @property
    def remaining(self) -> int:
        return self.max_failures - self.n_fail
