# Reproduce the frozen results without inference

The annotated `v2-primary` tag freezes the primary dataset at
`8cfd7daedafc4d6a4558befe588bd2e927f99c6c`. The Phase 3 reproduction tools
are in subsequent commits. Use the latest checkout for these commands; the
tag itself predates those tools. No command below contacts Ollama.

These are the exact local clean-clone commands used for the freeze check.
Python 3.12.3 is required for the exact environment lock. The first command
uses the existing venv solely to bootstrap a new venv. On another computer,
substitute your Python 3.12 interpreter and repository location for those
two absolute paths. Choose unused scratch/clone paths for repeat runs.

```bash
git clone --no-hardlinks /home/abhi_pop/pfr /tmp/pfr-phase3-clean
cd /tmp/pfr-phase3-clean
PYTHONPATH="" /home/abhi_pop/pfr/.venv/bin/python -m venv .venv
PYTHONPATH="" .venv/bin/python -c 'from pathlib import Path; lines=Path("requirements.lock").read_text().splitlines(); Path("/tmp/pfr-phase3-dependencies.lock").write_text("\n".join(line for line in lines if not line.startswith("-e "))+"\n")'
PYTHONPATH="" .venv/bin/python -m pip install --cache-dir /tmp/pfr-phase3-pip-cache --find-links /home/abhi_pop/.cache/pip/wheels/72/95/1d/b336e5ee612ae9a019bfff4dc0bedd100ee6f0570db205fdf8 -r /tmp/pfr-phase3-dependencies.lock
PYTHONPATH="" .venv/bin/python -m pip install --no-deps --cache-dir /tmp/pfr-phase3-pip-cache -e .
PYTHONPATH="" .venv/bin/python -m pip check
PYTHONPATH="" .venv/bin/python -m pytest -q -p no:cacheprovider
PYTHONPATH="" .venv/bin/python scripts/verify_manifest.py
PYTHONPATH="" .venv/bin/python scripts/rebuild_artifacts.py --scratch /tmp/pfr-phase3-rebuilt
PYTHONPATH="" .venv/bin/python scripts/replay.py --jsonl results/raw/qwen_v2.jsonl --task t06 --cell PAR-F --method B5 --check
git status --porcelain=v1
```

`requirements.lock` is the exact original `pip freeze`, including its editable
absolute source path. The filter prevents installation from the original
checkout; the subsequent editable install points at the clean clone. The
`--find-links` directory is a local cached PyBullet wheel used in this run;
omit that option on a machine without that cache (pip can build/download it).
Installing the Ollama Python package does not contact the server.

The rebuild script passes explicit dataset paths, rebuilds all five archived
tables, all ten derived-v1 files, all v2 tables/derived files/comparisons/captions,
and all eighteen PNG figures. It regenerates the three original demo videos
from the v1 logs to extract the eight original replay stills. Recorded extraction
indices are reel 150/400/700, B0 245/734, and B5 177/531. The contrast joins
B0's failure and B5's final still with a ten-pixel `(30,30,35)` separator.
It writes only outside the checkout, byte-compares the complete artifact
inventory, writes `diff.json`, and exits nonzero on any mismatch. Encoding and
rendering may vary across OS/graphics/font/FFmpeg versions; a mismatch is a
failed exact reproduction and must be reported, not silently accepted.

The replay command reconstructs and checks one logged episode, then runs a
headless kinematic replay. It verifies symbolic trace consistency and reports
IK error. This does not establish physical executability.

The model name, digest and Ollama version in `results/meta.txt` come from the
earlier recorded Phase 2 snapshot. Phase 3 collects Python/OS locally and
records current Ollama state as unknown. No new model runs or current server
verification are needed to rebuild the artifacts.

For a private remote that you have created, run these yourself, replacing
`OWNER/PRIVATE-REPO` with the real private repository:

```bash
git remote add private git@github.com:OWNER/PRIVATE-REPO.git
git push private HEAD:refs/heads/main
git push private refs/tags/pre-phase2 refs/tags/v2-primary
```

No push is performed by this workflow. A local backup is created and checked by:

```bash
git bundle create /tmp/pfr-v2-primary.bundle --all
git bundle verify /tmp/pfr-v2-primary.bundle
```

## Reproduce the exploratory additions

After updating the clean clone to the Phase 3 commits, run these exact commands.
They rebuild into a second scratch directory and leave committed derived outputs intact.

```bash
git -C /tmp/pfr-phase3-clean pull --ff-only
cd /tmp/pfr-phase3-clean
PYTHONPATH="" .venv/bin/python -m pytest -q -p no:cacheprovider
PYTHONPATH="" .venv/bin/python analysis/human_utility.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --out /tmp/pfr-phase3-exploratory
PYTHONPATH="" .venv/bin/python analysis/human_pareto.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --out /tmp/pfr-phase3-exploratory
PYTHONPATH="" .venv/bin/python analysis/human_terminations.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --out /tmp/pfr-phase3-exploratory
PYTHONPATH="" .venv/bin/python analysis/claims_evidence.py --v1 results/raw/qwen.jsonl --v2 results/raw/qwen_v2.jsonl --ablation results/raw/qwen_v2_ablation.jsonl --out /tmp/pfr-phase3-exploratory --paper /tmp/pfr-phase3-exploratory/claims_evidence.md
PYTHONPATH="" .venv/bin/python -c 'from pathlib import Path; root=Path.cwd(); scratch=Path("/tmp/pfr-phase3-exploratory"); files=sorted((root/"results/derived_v2").iterdir()); changed=[p.name for p in files if p.read_bytes()!=(scratch/p.name).read_bytes()]; changed += ["claims_evidence.md"] if (root/"paper/claims_evidence.md").read_bytes()!=(scratch/"claims_evidence.md").read_bytes() else []; print(f"EXPLORATORY DIFF: {len(files)+1} files compared; {len(changed)} different",changed); raise SystemExit(bool(changed))'
```

Every number in `results/derived_v2/` is **exploratory, defined after seeing the
data**. Its intervals retain the primary marginal alpha but do not provide
familywise control across the full set of exploratory comparisons. Read
`paper/claims_evidence.md` for the exact permitted scope of each claim.
