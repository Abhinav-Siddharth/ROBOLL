#!/usr/bin/env bash
# Run inside tmux:  tmux new -s run   then   bash scripts/run_main.sh
# Safe to re-run after a crash: finished episodes are skipped.
set -euo pipefail
cd ~/pfr
source .venv/bin/activate
mkdir -p logs results/raw
systemd-inhibit --what=sleep:idle --who=pfr --why="experiment" \
  python -m pfr.runner --config configs/main.yaml --model qwen2.5:7b --out results/raw/qwen.jsonl 2>&1 | tee -a logs/qwen.log
