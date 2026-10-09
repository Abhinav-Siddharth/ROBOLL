"""Play one reconstructed episode in a Scene: HUD text + step animations."""
from __future__ import annotations

OK_COL, BAD_COL, WHITE = (90, 230, 130), (255, 90, 90), (255, 255, 255)


def _args(params: dict) -> str:
    return ", ".join(str(v) for v in params.values())


def play_episode(sc, ep) -> None:
    row = ep.row
    head = [f"{row['task']}: {ep.task['goal_text']}",
            f"{row['method']} | cell {row['cell']} | hidden truth: {ep.hidden}"]
    sc.load_state(ep.initial)
    sc.set_hud(head + ["start"], WHITE)
    sc.hold(1.2)
    for fr in ep.frames:
        call = f"#{fr.attempt} {fr.skill}({_args(fr.params)})"
        if fr.code == "OK":
            sc.set_hud(head + [f"{call}  ->  OK"], OK_COL)
        else:
            dec = f"{row['method']} decides: {fr.decision}" if fr.decision else ""
            sc.set_hud(head + [f"{call}  ->  {fr.code}", f"{fr.detail}   |   {dec}"], BAD_COL, n_colored=2)
        sc.run_step(fr)
        if fr.decision == "escalate":
            msg = "human intervenes: problem fixed" if fr.human_fixed else "human says: impossible"
            sc.set_hud(head + [msg], WHITE)
            sc.hold(1.0)
        elif fr.code != "OK":
            sc.hold(0.5)
    ok = row["correct"]
    verdict = (f"OUTCOME: {row['outcome']}  |  {'CORRECT' if ok else 'WRONG'}  |  "
               f"attempts on faulted step {row['attempts_on_faulted_step']} (oracle {row['oracle_attempts']}), "
               f"regret {row['regret']}")
    sc.set_hud(head + [verdict], OK_COL if ok else BAD_COL)
    sc.hold(2.5)
