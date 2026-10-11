# pfr: persistent failure recovery for LLM-based robot agents

Controlled simulator study: when a skill keeps failing, should the agent retry, modify, replan, escalate or abstain?
Methods B0-B5, 20 tasks, 11 fault cells (transient / fixable / permanent), regret against an oracle attempt count.

## Setup
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt && pip install -e .
    ollama pull qwen2.5:7b

## Tests (no model needed)
    pytest -q

## Dry run with the fake model (seconds, no Ollama)
    python -m pfr.runner --config configs/pilot.yaml --model stub --out /tmp/stub.jsonl
    python analysis/summarize.py /tmp/stub.jsonl

## Reproduce the results
    python -m pfr.runner --config configs/pilot.yaml --model qwen2.5:7b --out results/raw/pilot.jsonl
    python analysis/summarize.py results/raw/pilot.jsonl          # go / no-go
    bash scripts/run_main.sh                                       # 1320 episodes, resumable
    python analysis/make_figures.py results/raw/qwen.jsonl         # figures/ and results/tables/

## Layout
    src/pfr/env.py        simulator (5 skills, structured results)
    src/pfr/tasks.py      20 tasks
    src/pfr/faults.py     11 fault cells, oracle attempts
    src/pfr/prompts.py    frozen prompts (v1)
    src/pfr/llm.py        Ollama wrapper + cache
    src/pfr/runner.py     episode loop + CLI
    src/pfr/methods/      B0-B5
    configs/              pilot, main, timing, policy thresholds
    analysis/             summarize.py (go/no-go), make_figures.py
    paper/                claim, prereg, notes, outline

## Pilot stages

`configs/pilot.yaml` is stage 1 only: 5 tasks x 11 cells x B0/B3/B4 = 165 episodes.
The archived `results/raw/pilot.jsonl` contains a later six-method pilot of 330 episodes.
To reproduce that design explicitly use `--methods B0,B1,B2,B3,B4,B5`; do not append to
or overwrite the archive. Use a new output path and record the exact config.

An editable install declares runtime and analysis dependencies. Test and viewer tools
are available through `pip install -e '.[test,viz]'`. Viewer dependencies are optional.
