#!/usr/bin/env python
"""One demo video: for each (cell, weak, strong) pair, find a task where `weak` got it wrong and `strong`
got it right, then play both back to back with title cards.
  python scripts/make_reel.py --jsonl results/raw/qwen.jsonl --out results/demo/reel.mp4
  python scripts/make_reel.py --jsonl results/raw/qwen.jsonl --pairs TR-P:B0:B5,PAR-F:B0:B5 --out results/demo/reel.mp4
"""
import argparse
import json
from pathlib import Path

DEFAULT_PAIRS = "TR-P:B0:B5,PAR-F:B0:B5,ST-P:B3:B5"
WHY = {"TR-P": "permanent timeout: stop retrying", "PAR-F": "wrong grasp: change the parameter",
       "ST-F": "object is elsewhere: replan", "ST-P": "object is gone: give up", "PRE-F": "missing prerequisite",
       "PRE-P": "prerequisite blocked", "PAR-P": "no grasp works", "TR-T2": "transient: retrying is right"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", default=DEFAULT_PAIRS)
    ap.add_argument("--model")
    ap.add_argument("--speed", type=float, default=1.8)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--res", default="960x540")
    a = ap.parse_args()

    import imageio
    from pfr.viz.play import play_episode
    from pfr.viz.scene import Scene
    from pfr.viz.state import reconstruct

    rows = [json.loads(l) for l in open(a.jsonl) if l.strip()]
    if a.model:
        rows = [r for r in rows if r["model"] == a.model]
    by = {(r["task"], r["cell"], r["method"]): r for r in rows}
    plan = []
    for spec in a.pairs.split(","):
        cell, weak, strong = spec.split(":")
        tasks = sorted({t for (t, c, m) in by if c == cell})
        hit = next((t for t in tasks if (t, cell, weak) in by and (t, cell, strong) in by
                    and not by[(t, cell, weak)]["correct"] and by[(t, cell, strong)]["correct"]), None)
        if hit is None:
            print(f"[skip] {spec}: no task where {weak} is wrong and {strong} is right")
            continue
        plan.append((cell, weak, strong, hit))
    if not plan:
        raise SystemExit("nothing to render")

    w, h = (int(x) for x in a.res.lower().split("x"))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(a.out, fps=a.fps, codec="libx264", quality=8, macro_block_size=None)
    sc = Scene(gui=False, size=(w, h), fps=a.fps, speed=a.speed, writer=writer)
    try:
        sc.card(["Persistent failure recovery", "same task, same hidden fault,", "different recovery policy"], 3.0)
        for cell, weak, strong, task in plan:
            for m in (weak, strong):
                row = by[(task, cell, m)]
                sc.card([f"{task}  |  {cell}", WHY.get(cell, ""), f"method {m}"], 2.0)
                print("rendering", row["episode_id"])
                play_episode(sc, reconstruct(row))
    finally:
        writer.close()
        sc.close()
    print(f"wrote {a.out}  ({sc.n_frames} frames, {sc.n_frames / a.fps:.0f}s)")


if __name__ == "__main__":
    main()
