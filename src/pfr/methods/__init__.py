"""Method registry. Modules are imported lazily so you can build one at a time."""
import importlib

import yaml

_MODULES = {
    "B0": ("b0_retry", "B0Retry"),
    "B1": ("b1_maxretry", "B1MaxRetry"),
    "B2": ("b2_nohistory", "B2NoHistory"),
    "B3": ("b3_replan", "B3Replan"),
    "B4": ("b4_llm_history", "B4LLMHistory"),
    "B5": ("b5_policy", "B5Policy"),
}


def make_method(name: str, policy_path: str = "configs/policy.yaml"):
    mod, cls = _MODULES[name]
    klass = getattr(importlib.import_module(f"pfr.methods.{mod}"), cls)
    if name == "B5":
        with open(policy_path) as f:
            return klass(yaml.safe_load(f))
    return klass()
