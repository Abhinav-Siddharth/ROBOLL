#!/usr/bin/env python
"""Replay logged episodes in 3D.   Examples:
  python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --method B5 --gui
  python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --method B0 --video results/demo/b0.mp4
  python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --list
  python scripts/replay.py --jsonl results/raw/qwen.jsonl --check          # headless IK sanity over many episodes
"""
import argparse
import json
import sys
from pathlib import Path


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def select(rows, a):
    out = rows
    for key, val in [("task", a.task), ("cell", a.cell), ("method", a.method), ("model", a.model)]:
        if val:
            out = [r for r in out if r[key] == val]
    if a.seed is not None:
        out = [r for r in out if r["seed"] == a.seed]
    if a.episode_id:
        out = [r for r in out if r["episode_id"] == a.episode_id]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--task"), ap.add_argument("--cell"), ap.add_argument("--method"), ap.add_argument("--model")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--episode-id")
    ap.add_argument("--all", action="store_true", help="play every match (default: first)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--gui", action="store_true", help="live window (needs a display)")
    ap.add_argument("--video", help="write an mp4 here (no display needed)")
    ap.add_argument("--check", action="store_true", help="headless: replay many episodes, report max IK error")
    ap.add_argument("--speed", type=float, default=1.5)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--res", default="960x540")
    a = ap.parse_args()

    from pfr.viz.state import reconstruct
    rows = select(load(a.jsonl), a)
    if not rows:
        sys.exit("no episode matches those filters (try --list with fewer filters)")
    if a.list:
        for r in rows:
            print(r["episode_id"], r["outcome"], "correct" if r["correct"] else "WRONG", f"regret={r['regret']}")
        return
    if not (a.gui or a.video or a.check):
        sys.exit("choose one of --gui, --video PATH, --check (or --list)")

    from pfr.viz.play import play_episode
    from pfr.viz.scene import Scene
    todo = rows if (a.all or a.check) else rows[:1]
    if a.check:
        todo = todo[:60]
    if len(rows) > 1 and not (a.all or a.check):
        print(f"{len(rows)} episodes match; playing the first ({rows[0]['episode_id']}). Use --all or narrow the filters.")

    w, h = (int(x) for x in a.res.lower().split("x"))
    writer = None
    if a.video:
        import imageio
        Path(a.video).parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(a.video, fps=a.fps, codec="libx264", quality=8, macro_block_size=None)
    sc = Scene(gui=a.gui, render=not a.check, size=(w, h), fps=a.fps, speed=a.speed, writer=writer)
    try:
        for r in todo:
            ep = reconstruct(r)
            print("replaying", r["episode_id"], f"({len(ep.frames)} steps)")
            play_episode(sc, ep)
    finally:
        if writer:
            writer.close()
            print(f"wrote {a.video} ({sc.n_frames} frames, {sc.n_frames / a.fps:.0f}s)")
        print(f"max IK position error over the replay: {sc.max_ik_err * 100:.2f} cm")
        sc.close()


if __name__ == "__main__":
    main()
