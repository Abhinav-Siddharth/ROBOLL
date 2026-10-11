#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONDONTWRITEBYTECODE=1
exec .venv/bin/python -m pytest tests/ -q -o addopts=
