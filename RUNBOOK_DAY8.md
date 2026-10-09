# DAY 8 RUNBOOK: 3D replay (the visual layer)

Same rules as the 7-day plan: run the commands in order, do not skip a checkpoint, do not "improve" anything on the way.

## Where it fits
- Do it **after Day 6** (the main run is finished and `results/raw/qwen.jsonl` exists), and **before the Day 7 submit step** if your deadline allows.
- If the deadline is fixed at 7 days, do Day 8 **after submitting** and use it as the README / GitHub / viva demo. Nothing in the paper depends on it.
- Do **not** run it while the overnight main run is still going: rendering uses the CPU, and Ollama will slow down.

## What this is, and what it is not
- It **replays logged episodes** (`results/raw/*.jsonl`) in PyBullet: a mobile Franka Panda drives between five stations, opens the drawer, grasps, places. Failures are shown (stall, slipped grasp, closing on air, refusal shake, blocked path) with a red marker and a HUD line saying the failure code, the hidden truth, and what the method decided.
- It is a **kinematic visualisation**: joints come from IK, held objects follow the gripper. There is **no contact physics and no grasp dynamics**. Do not call it "physics simulation" anywhere.
- The experiment is **unchanged and symbolic**. No result, config, prompt, cache or seed is touched. All new code lives in `src/pfr/viz/` plus two scripts, and nothing in the experiment imports it.
- The replay is **verified against the logs**: it re-runs the same deterministic env + fault on every logged call and raises `ReplayMismatch` if any result code differs from the log. A replay can never show something the experiment did not do.

## PRE-FLIGHT FINDING (read this, decide, do not act yet)
While building the replay I found something in the experiment itself. For **6 of the 20 tasks** (t01, t04, t07, t13, t17, t19) the **ST-F hidden location equals the goal location**, so the goal is already satisfied at t=0 after the fault is applied. In those 6 episodes the object is "elsewhere" but elsewhere is where the task wants it.
- It is pinned by `test_known_degenerate_st_f_tasks_are_flagged_by_goal_at_t0`, so it cannot change silently.
- Effect: ST-F results mix 14 genuine episodes with 6 where "do nothing" would already succeed. That muddies the ST-F row, and a reviewer could find it.
- I missed this in the earlier 9/10 review. I checked that tests pass and numbers match, not this edge case.
- Fix is one line in `faults.py` (exclude the target object's goal location from the ST-F candidate locations), but it **changes the episode set**, so the main run and cached results would be regenerated. If the main run is already done, **do not fix it now**: report the 14 clean ST-F episodes as a sensitivity check and state the issue in Limitations. Your call.

## Step 0: baseline (2 min)
```bash
cd ~/pfr_kit && source .venv/bin/activate
pytest -q
```
Expected: `334 passed`. If not, stop; Day 8 builds on a green baseline.

## Step 1: install the viewer dependencies (10-30 min, mostly waiting)
PyBullet has no prebuilt wheel for recent Python versions, so pip compiles it from source.
```bash
sudo apt install -y build-essential python3-dev
pip install -r requirements-viz.txt      # use the file from the kit (Step 2); or run Step 2 first
python -c "import pybullet, imageio; print('viz deps ok')"
```
The compile took a few minutes on a single core in my test. It looks frozen at "Building wheel for pybullet", and that is normal. Do not Ctrl-C it.
Fallback if the build fails: `conda install -c conda-forge pybullet` in a separate conda env, or skip to Fallback A below.

## Step 2: add the files (3 min)
Unzip `day8_kit.zip` into the project root. It only adds files, it overwrites nothing:
```bash
cd ~/pfr_kit
unzip -n ~/Downloads/day8_kit.zip
ls src/pfr/viz scripts/replay.py scripts/make_reel.py tests/test_viz_*.py requirements-viz.txt
pytest -q
```
Expected: `384 passed` (334 original + 36 replay-state + 14 scene).
If pybullet is not installed yet, the scene tests are **skipped, not failed**. Install it and rerun.

## Step 3: headless sanity check on your real data (10 min)
```bash
python scripts/replay.py --jsonl results/raw/qwen.jsonl --check
```
Expected: it replays up to 60 episodes with no rendering and prints `max IK position error over the replay: ... cm`. In my test on the stub run it was 0.01 cm; anything under **3 cm** is fine.
- `ReplayMismatch` means the log and the code have diverged for that episode: do **not** render it, note the episode id, and send it to me.
- List what is available: `python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --list`

## Step 4: watch one live (20-40 min including tuning)
```bash
python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --method B5 --gui
```
You get a PyBullet window (mouse: rotate/zoom). `--speed 1.0` is slow and `2.5` is fast.
**Honest caveat: I tested video/headless mode end to end, but I could not open a GUI window in my sandbox.** If `--gui` fails (Wayland / OpenGL), use Step 5; the video path does not need a display.

## Step 5: render single episodes to mp4 (15 min)
Same task and fault, weak method vs strong method:
```bash
mkdir -p results/demo
python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --method B0 --video results/demo/t06_PAR-F_B0.mp4 --res 640x360
python scripts/replay.py --jsonl results/raw/qwen.jsonl --task t06 --cell PAR-F --method B5 --video results/demo/t06_PAR-F_B5.mp4 --res 640x360
```
Render speed in my 1-core sandbox: about 0.2 s per frame at 640x360 (a 12 s clip took ~80 s). 960x540 is roughly 4x slower. Check at 640x360 first, then re-render finals at `--res 960x540`.

## Step 6: the demo reel (30-60 min of rendering)
Picks, for each (cell, weak, strong) pair, the first task where the weak method is wrong and the strong one is right, then plays both with title cards:
```bash
python scripts/make_reel.py --jsonl results/raw/qwen.jsonl --out results/demo/reel.mp4 --res 640x360
```
Default pairs: `TR-P:B0:B5` (permanent timeout: stop retrying), `PAR-F:B0:B5` (wrong grasp: change the parameter), `ST-P:B3:B5` (object gone: give up). Lines like `[skip] ...: no task where B0 is wrong and B5 is right` mean that pair has no contrast in your data. That is a result worth knowing, not a bug. Choose other pairs: `--pairs PAR-F:B2:B5,ST-F:B3:B5`.
A 3-pair reel is about 3000 frames. Start it, go do something else.

## Step 7: stills for the paper (20 min)
```bash
python - <<'PY'
import imageio.v2 as imageio
r = imageio.get_reader("results/demo/reel.mp4")
n = r.count_frames(); print("frames:", n)
for i in [150, 400, 700]:          # change these after scrubbing the video
    imageio.imwrite(f"figures/replay_{i}.png", r.get_data(i))
PY
```
Pick two stills: one failure frame (red marker + HUD) and one final-banner frame, and use them as one figure.

## Step 8: the three sentences for the paper (10 min)
Add these, and nothing stronger:
- **Method/Setup:** "Episodes are executed in a symbolic simulator; for qualitative inspection we additionally replay logged traces in a PyBullet scene (kinematic visualisation, verified against the logs)."
- **Figure caption:** "Replay of task tNN under fault cell XX: (left) B0 retries a failing grasp until the cap; (right) B5 changes the grasp parameter and succeeds. Visualisation only; execution is symbolic."
- **Limitations:** "The 3D replay is a kinematic visualisation without contact physics; it does not constitute evidence of physical executability."
If you decided not to fix the ST-F issue, add: "For 6 of 20 tasks the ST-F hidden location coincides with the goal location; results are also reported on the remaining 14."

## Day 8 checkpoint
- [ ] `pytest -q` shows `384 passed` (or 370 passed + skipped scene tests if PyBullet is missing)
- [ ] `--check` ran on the real log with IK error < 3 cm and no `ReplayMismatch`
- [ ] At least one B0 and one B5 clip rendered; the failure marker and HUD are readable
- [ ] `results/demo/reel.mp4` exists (or you recorded which pairs had no contrast)
- [ ] Limitations has the "visualisation only" sentence

## Fallbacks
- **A. PyBullet will not build:** skip it. The replay *state* layer (`src/pfr/viz/state.py`, 36 tests) needs no PyBullet, and `ReplayMismatch` checks still run. Present the symbolic traces as before; Day 8 simply does not happen.
- **B. `--gui` fails:** use `--video`.
- **C. Rendering is too slow:** `--res 480x270 --speed 3`, or `--fps 20`.
- **D. `libx264` / ffmpeg error:** `pip install --upgrade imageio-ffmpeg`.
- **E. A replay looks wrong (object in the wrong place, arm stuck):** the scene re-syncs to the true world state after every step, so errors cannot accumulate. Send me the episode id and a screenshot.

## Time budget
| Step | Time |
|---|---|
| 0-3 baseline, install, files, headless check | 0.5-1 h (mostly the PyBullet compile) |
| 4 live view | 0.5 h |
| 5-6 clips and reel (mostly waiting) | 1-1.5 h |
| 7-8 stills and paper text | 0.5 h |
| **Total** | **about 5-6 h** (one day, as estimated) |

## What I verified while building this, and what I did not
Verified in my sandbox: 384 tests pass (334 + 36 + 14); 660 real stub episodes replay against their own logs; all 20 clean tasks end with every object at its goal and IK error under 3 cm; all 11 fault cells replay without error; a 12 s clip and a 68 s two-pair reel rendered, and I looked at the frames.
Not verified: the live `--gui` window; rendering against your real qwen logs (they contain LLM replans I have not seen); real render times on your laptop.

---
# APPENDIX: full source (identical to the files in `day8_kit.zip`)

## `requirements-viz.txt`
```
pybullet>=3.2.6
imageio>=2.34
imageio-ffmpeg>=0.5
pillow>=10.1
```

## `src/pfr/viz/__init__.py`
```python
"""Day-8 add-on: kinematic 3D replay of logged episodes. Nothing here is imported by the experiment code."""
```

## `src/pfr/viz/state.py`
```python
"""Rebuild the true world state of a logged episode, step by step. NO pybullet needed.

The JSONL row stores every executed call and its result code, but not the world.
We re-run the SAME deterministic Env + FaultyEnv on the logged calls and check that
every result code matches the log. A mismatch means the log and the code have
diverged, so a replay would be lying: we raise instead of drawing it.

Only one thing happens outside the logged calls: when a step's decision was
"escalate" on a solvable fault, the runner calls fault.clear(env) (the human fixes
it). We do the same here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..env import Call, Env
from ..faults import FaultyEnv, build_fault
from ..tasks import TASKS

TASK_BY_ID = {t["id"]: t for t in TASKS}


class ReplayMismatch(RuntimeError):
    pass


@dataclass
class Frame:
    attempt: int
    skill: str
    params: dict
    code: str
    detail: str
    decision: str
    before: dict
    after: dict
    human_fixed: bool = False
    note: str = ""


@dataclass
class Episode:
    row: dict
    task: dict
    initial: dict                      # true world at t=0 (ST faults already applied)
    hidden: str                        # one line: what the agent cannot see
    frames: list = field(default_factory=list)
    final_goal_ok: bool = False


def hidden_truth(fault) -> str:
    k = fault.kind
    if k == "NONE":
        return "no fault"
    if k == "TR":
        if fault.regime == "permanent":
            return f"pick({fault.target}) will time out forever (permanent)"
        return f"pick({fault.target}) times out {fault.n_clear}x, then works"
    if k == "PAR":
        if fault.regime == "permanent":
            return f"no grasp works for {fault.target} (permanent)"
        return f"only grasp='{fault.hidden_fix}' works for {fault.target}"
    if k == "ST":
        if fault.regime == "permanent":
            return f"{fault.target} is gone (permanent)"
        return f"{fault.target} is really at '{fault.true_loc}'"
    if k == "PRE":
        if fault.regime == "permanent":
            return f"path to '{fault.prereq_loc}' is blocked (permanent)"
        return f"must visit '{fault.prereq_loc}' before picking {fault.target}"
    return ""


def reconstruct(row: dict, task: Optional[dict] = None) -> Episode:
    task = task or TASK_BY_ID[row["task"]]
    fault = build_fault(task, row["cell"], row["seed"])
    env = Env(task["init_state"])
    fenv = FaultyEnv(env, fault)
    ep = Episode(row=row, task=task, initial=env.observe(), hidden=hidden_truth(fault))
    for s in row["steps"]:
        call = Call(s["skill"], dict(s["params"]))
        before = env.observe()
        res = fenv.execute(call)
        if res.code != s["code"]:
            raise ReplayMismatch(
                f"{row['episode_id']} attempt {s['attempt']}: log says {s['code']}, replay says {res.code}")
        fixed = False
        if s["decision"] == "escalate" and fault.solvable:
            fault.clear(env)
            fixed = True
        ep.frames.append(Frame(s["attempt"], s["skill"], dict(s["params"]), s["code"], s["detail"],
                               s["decision"], before, env.observe(), fixed, s.get("note", "")))
    ep.final_goal_ok = env.goal_satisfied(task["goal"])
    return ep
```

## `src/pfr/viz/scene.py`
```python
"""PyBullet kinematic replay scene: a mobile Franka Panda and five stations.

HONEST SCOPE: this is a *visualisation*. Joints are set by IK each frame and held
objects simply follow the gripper. There is no contact physics and no grasp
dynamics. The experiment is still the symbolic one in pfr.env; this only draws it.
"""
from __future__ import annotations

import math
import time
from typing import Optional

import numpy as np
import pybullet as p
import pybullet_data

# ----------------------------------------------------------------- layout
RS, RB, RB_DRAWER = 1.35, 0.72, 0.62      # station ring radius, robot base ring radius (stands further back at the drawer)
BASE_Z = 0.12                             # robot stands on a small pedestal so the shelf is reachable
STATION_ANGLE = {"sink": -64.0, "table": -32.0, "drawer": 0.0, "counter": 32.0, "shelf": 64.0}
STATION_TOP = {"sink": 0.12, "table": 0.18, "drawer": 0.26, "counter": 0.24, "shelf": 0.34}
STATION_COLOR = {"sink": (0.55, 0.65, 0.80, 1), "table": (0.70, 0.52, 0.34, 1), "drawer": (0.45, 0.45, 0.50, 1),
                 "counter": (0.80, 0.78, 0.72, 1), "shelf": (0.60, 0.42, 0.28, 1)}
HALF_T, HALF_R = 0.32, 0.16               # station half-size: tangent, radial
SLOTS = [0.0, -0.12, 0.12, -0.24, 0.24]   # tangent offsets (first free slot is used)
TRAY_TOP, TRAY_SLIDE = 0.12, 0.18         # drawer tray top height, how far it slides out

# object: (shape, size, rgba, half_height)
OBJ = {
    "apple": (p.GEOM_SPHERE, 0.035, (0.85, 0.12, 0.12, 1), 0.035),
    "cup": (p.GEOM_CYLINDER, (0.030, 0.08), (0.15, 0.40, 0.90, 1), 0.040),
    "plate": (p.GEOM_CYLINDER, (0.060, 0.012), (0.95, 0.95, 0.95, 1), 0.006),
    "knob_key": (p.GEOM_BOX, (0.035, 0.014, 0.010), (1.0, 0.80, 0.0, 1), 0.010),
    "bowl": (p.GEOM_CYLINDER, (0.050, 0.05), (0.20, 0.70, 0.30, 1), 0.025),
}

# ----------------------------------------------------------------- panda
EE = 11                                   # panda_grasptarget link
ARM = list(range(7))
FINGERS = (9, 10)
LOWER = [-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973]
UPPER = [2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973]
RANGES = [u - l for l, u in zip(LOWER, UPPER)]
STOW = [0.0, -0.45, 0.0, -2.35, 0.0, 1.95, 0.78]


def _ease(s: float) -> float:
    return s * s * (3 - 2 * s)


def _u(angle_deg: float) -> np.ndarray:   # outward unit vector
    a = math.radians(angle_deg)
    return np.array([math.cos(a), math.sin(a), 0.0])


def _t(angle_deg: float) -> np.ndarray:   # tangent unit vector
    a = math.radians(angle_deg)
    return np.array([-math.sin(a), math.cos(a), 0.0])


class Scene:
    def __init__(self, gui: bool = False, render: bool = True, size=(960, 540), fps: int = 30,
                 speed: float = 1.0, writer=None):
        self.gui, self.render, self.size, self.fps, self.speed, self.writer = gui, render, size, fps, speed, writer
        self.cid = p.connect(p.GUI if gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        if gui:
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
            p.resetDebugVisualizerCamera(2.4, -62, -40, [0.85, 0.05, 0.12])
        plane = p.loadURDF("plane.urdf")
        p.changeVisualShape(plane, -1, rgbaColor=(0.80, 0.83, 0.86, 1), textureUniqueId=-1)
        self.eye, self.target = [-0.1, -1.55, 1.95], [0.85, 0.20, 0.08]
        self.view = p.computeViewMatrix(self.eye, self.target, [0, 0, 1])
        self.proj = p.computeProjectionMatrixFOV(60, size[0] / size[1], 0.1, 8.0)
        self.hud_lines: list = []
        self.hud_color = (255, 255, 255)
        self.hud_n = 1
        self.max_ik_err = 0.0
        self.n_frames = 0
        self._hud_ids: dict = {}
        self._build_stations()
        self.arm = p.loadURDF("franka_panda/panda.urdf", [0, 0, 0], useFixedBase=True)
        self.base_loc = "table"
        self.base_angle = STATION_ANGLE["table"]
        self.base_r = RB
        self.pedestal = p.createMultiBody(0, -1, p.createVisualShape(p.GEOM_CYLINDER, radius=0.13, length=BASE_Z,
                                          rgbaColor=(0.25, 0.25, 0.28, 1)), [0, 0, BASE_Z / 2])
        self.held: Optional[str] = None
        self.hold_off = np.zeros(3)
        self.slide = 0.0
        self.obj_loc: dict = {}
        self.slot_of: dict = {}
        self.body = {n: self._make_obj(n) for n in OBJ}
        self.marker = p.createMultiBody(0, -1, p.createVisualShape(p.GEOM_SPHERE, radius=0.065,
                                        rgbaColor=(1, 0.1, 0.1, 1)), [0, 0, -5])
        self._place_base(self.base_angle, self.base_r)
        self._set_arm(STOW)
        self._fingers(0.04)

    # ------------------------------------------------------------ building
    def _box(self, half, pos, yaw_deg, rgba):
        v = p.createVisualShape(p.GEOM_BOX, halfExtents=half, rgbaColor=rgba)
        return p.createMultiBody(0, -1, v, list(pos), p.getQuaternionFromEuler([0, 0, math.radians(yaw_deg)]))

    def _build_stations(self):
        self.station_label = {}
        for name, ang in STATION_ANGLE.items():
            c, top = RS * _u(ang), STATION_TOP[name]
            self._box([HALF_R, HALF_T, top / 2], c + [0, 0, top / 2], ang, STATION_COLOR[name])
            if name == "sink":   # a darker basin so it reads as a sink
                self._box([HALF_R * 0.75, HALF_T * 0.8, 0.004], c + [0, 0, top + 0.003], ang, (0.2, 0.25, 0.35, 1))
            if name == "drawer":
                self.tray = self._box([0.14, 0.28, 0.01], c + [0, 0, TRAY_TOP - 0.01], ang, (0.85, 0.85, 0.88, 1))
                self.handle = self._box([0.01, 0.07, 0.03], c - _u(ang) * 0.17 + [0, 0, TRAY_TOP + 0.03], ang,
                                        (0.15, 0.15, 0.15, 1))
            self.station_label[name] = c + [0, 0, top + 0.12]

    def _make_obj(self, name):
        shape, size, rgba, hh = OBJ[name]
        if shape == p.GEOM_SPHERE:
            v = p.createVisualShape(shape, radius=size, rgbaColor=rgba)
        elif shape == p.GEOM_CYLINDER:
            v = p.createVisualShape(shape, radius=size[0], length=size[1], rgbaColor=rgba)
        else:
            v = p.createVisualShape(shape, halfExtents=size, rgbaColor=rgba)
        return p.createMultiBody(0, -1, v, [0, 0, -5])

    # ------------------------------------------------------------ geometry
    def _tray_center(self, s=None):
        s = self.slide if s is None else s
        return RS * _u(STATION_ANGLE["drawer"]) - _u(STATION_ANGLE["drawer"]) * s

    def slot_pos(self, loc: str, obj: str) -> np.ndarray:
        ang, off = STATION_ANGLE[loc], SLOTS[self.slot_of[(loc, obj)]]
        hh = OBJ[obj][3]
        if loc == "drawer":
            base = self._tray_center() - _u(ang) * 0.07
            return base + _t(ang) * off * 0.8 + [0, 0, TRAY_TOP + hh]
        return RS * _u(ang) + _t(ang) * off + [0, 0, STATION_TOP[loc] + hh]

    def _assign_slot(self, loc: str, obj: str):
        used = {self.slot_of[(loc, o)] for o, l in self.obj_loc.items() if l == loc and (loc, o) in self.slot_of}
        self.slot_of[(loc, obj)] = next(i for i in range(len(SLOTS)) if i not in used)

    def _put(self, obj: str, pos):
        p.resetBasePositionAndOrientation(self.body[obj], list(pos), [0, 0, 0, 1])

    def obj_pos(self, obj: str) -> np.ndarray:
        return np.array(p.getBasePositionAndOrientation(self.body[obj])[0])

    def _station_pt(self, loc: str) -> np.ndarray:
        return RS * _u(STATION_ANGLE[loc]) + [0, 0, STATION_TOP[loc]]

    # ------------------------------------------------------------ state sync
    def load_state(self, state: dict):
        """Snap the whole scene to a world state (used at t=0 and as a per-step safety net)."""
        self.held = None
        self.slot_of.clear()
        self.obj_loc = {}
        self.slide = TRAY_SLIDE if state["drawer_open"] else 0.0
        self._set_tray()
        for obj, loc in state["objects"].items():
            self.obj_loc[obj] = loc
        for obj, loc in state["objects"].items():
            if loc in STATION_ANGLE:
                self._assign_slot(loc, obj)
                self._put(obj, self.slot_pos(loc, obj))
            elif loc == "gripper":
                self.held = obj
            else:                                  # "gone": the object does not exist any more
                self._put(obj, [0, 0, -5])
        self.base_loc = state["robot_loc"]
        self._place_base(STATION_ANGLE[self.base_loc], self._r_for(self.base_loc))
        self._set_arm(STOW)
        self._fingers(0.04)
        self._present()

    def sync(self, state: dict):
        """Make the scene match `state` after a step. A no-op if the animation already did the right thing."""
        self.slide = TRAY_SLIDE if state["drawer_open"] else 0.0
        self._set_tray()
        for obj, loc in state["objects"].items():
            if loc == "gripper":
                continue
            if loc in STATION_ANGLE:
                if self.obj_loc.get(obj) != loc or (loc, obj) not in self.slot_of:
                    self.obj_loc[obj] = loc
                    self._assign_slot(loc, obj)
                self._put(obj, self.slot_pos(loc, obj))
            else:
                self.obj_loc[obj] = loc
                self._put(obj, [0, 0, -5])
        if self.held and state["holding"] != self.held:
            self.held = None
        self.show_marker(None)

    def _set_tray(self):
        a = STATION_ANGLE["drawer"]
        yaw = p.getQuaternionFromEuler([0, 0, math.radians(a)])
        c = self._tray_center()
        p.resetBasePositionAndOrientation(self.tray, list(c + [0, 0, TRAY_TOP - 0.01]), yaw)
        p.resetBasePositionAndOrientation(self.handle, list(c - _u(a) * 0.17 + [0, 0, TRAY_TOP + 0.03]), yaw)
        for o, l in self.obj_loc.items():
            if l == "drawer" and o != self.held and (l, o) in self.slot_of:
                self._put(o, self.slot_pos(l, o))

    # ------------------------------------------------------------ arm
    @staticmethod
    def _r_for(loc: str) -> float:
        return RB_DRAWER if loc == "drawer" else RB

    def _place_base(self, angle: float, r: Optional[float] = None):
        r = self.base_r if r is None else r
        pos = r * _u(angle) + [0, 0, BASE_Z]
        q = p.getQuaternionFromEuler([0, 0, math.radians(angle)])
        p.resetBasePositionAndOrientation(self.arm, list(pos), q)
        p.resetBasePositionAndOrientation(self.pedestal, list(r * _u(angle) + [0, 0, BASE_Z / 2]), q)
        self.base_angle, self.base_r = angle, r

    def _set_arm(self, q):
        for j, v in zip(ARM, q):
            p.resetJointState(self.arm, j, v)

    def _fingers(self, w: float):
        for j in FINGERS:
            p.resetJointState(self.arm, j, w)

    def ee(self) -> np.ndarray:
        return np.array(p.getLinkState(self.arm, EE, computeForwardKinematics=True)[4])

    def _ik(self, pos) -> list:
        orn = p.getQuaternionFromEuler([math.pi, 0, math.radians(self.base_angle)])
        q = None
        for _ in range(3):
            q = p.calculateInverseKinematics(self.arm, EE, list(pos), orn, lowerLimits=LOWER, upperLimits=UPPER,
                                             jointRanges=RANGES, restPoses=STOW, maxNumIterations=120,
                                             residualThreshold=1e-4)[:7]
            self._set_arm(q)
            err = float(np.linalg.norm(self.ee() - np.array(pos)))
            if err < 0.01:
                break
        self.max_ik_err = max(self.max_ik_err, err)
        return list(q)

    def move_ee(self, target, n: Optional[int] = None):
        start, target = self.ee(), np.array(target, dtype=float)
        n = n or max(5, int(np.linalg.norm(target - start) / (0.012 * self.speed)))
        for k in range(1, n + 1):
            self._set_arm(self._ik(start + (target - start) * _ease(k / n)))
            self._carry()
            self._present()

    def move_joints(self, q1, n: int = 18):
        q0 = [p.getJointState(self.arm, j)[0] for j in ARM]
        n = max(4, int(n / self.speed))
        for k in range(1, n + 1):
            s = _ease(k / n)
            self._set_arm([a + (b - a) * s for a, b in zip(q0, q1)])
            self._carry()
            self._present()

    def _carry(self):
        if self.held:
            self._put(self.held, self.ee() + self.hold_off)

    def grip(self, w1: float, n: int = 8):
        w0 = p.getJointState(self.arm, FINGERS[0])[0]
        for k in range(1, int(n / self.speed) + 2):
            self._fingers(w0 + (w1 - w0) * k / (int(n / self.speed) + 1))
            self._present()

    def hold(self, seconds: float):
        for _ in range(max(1, int(seconds * self.fps))):
            self._present()

    def show_marker(self, pos):
        p.resetBasePositionAndOrientation(self.marker, [0, 0, -5] if pos is None else list(pos), [0, 0, 0, 1])

    # ------------------------------------------------------------ skills
    def _hover_z(self, loc: str, z: float) -> float:
        return max(z + 0.12, STATION_TOP[loc] + 0.12)

    def goto(self, loc: str, ok: bool = True):
        self.move_joints(STOW, 14)
        a0, a1 = self.base_angle, STATION_ANGLE[loc]
        r0, r1 = self.base_r, self._r_for(loc)
        n = max(10, int(abs(a1 - a0) / (1.1 * self.speed)))
        stop = n if ok else int(n * 0.4)
        for k in range(1, stop + 1):
            self._place_base(a0 + (a1 - a0) * _ease(k / n), r0 + (r1 - r0) * _ease(k / n))
            self._carry()
            self._present()
        if ok:
            self.base_loc = loc
        else:                                  # path blocked: stop short, flash, come back
            self.show_marker(self.ee() + [0, 0, 0.3])
            self.hold(0.5)
            ang, rr = self.base_angle, self.base_r
            for k in range(1, stop + 1):
                self._place_base(ang + (a0 - ang) * k / stop, rr + (r0 - rr) * k / stop)
                self._carry()
                self._present()
            self.show_marker(None)

    def _approach(self, tgt, loc):
        self.move_joints(STOW, 10)
        self.move_ee([tgt[0], tgt[1], self._hover_z(loc, tgt[2])])

    def pick(self, obj: str, ok: bool, code: str):
        loc = self.base_loc
        here = self.obj_loc.get(obj) == loc
        tgt = self.obj_pos(obj) if here else self._station_pt(loc)
        grasp_z = tgt[2] + (OBJ[obj][3] * 0.6 if here else 0.03)
        self._approach(tgt, loc)
        if ok:
            self.grip(0.04)
            self.move_ee([tgt[0], tgt[1], grasp_z])
            self.grip(0.02)
            self.held, self.hold_off = obj, self.obj_pos(obj) - self.ee()
            self.obj_loc[obj] = "gripper"
            self.move_ee([tgt[0], tgt[1], self._hover_z(loc, tgt[2])])
            return
        if code == "EXEC_TRANSIENT":           # motion stalls halfway down, jitters, gives up
            mid = [tgt[0], tgt[1], (grasp_z + self._hover_z(loc, tgt[2])) / 2]
            self.move_ee(mid)
            self.show_marker(self.ee() + [0, 0, 0.16])
            self._jitter(0.015, 14)
        elif code == "PARAM_MISMATCH":         # fingers close, object slips, lift with nothing
            self.move_ee([tgt[0], tgt[1], grasp_z])
            self.grip(0.026)
            self.show_marker(self.ee() + [0, 0, 0.16])
            self.move_ee([tgt[0], tgt[1], grasp_z + 0.09])
            self.hold(0.4)
        elif code == "STATE_MISMATCH":         # reaches the expected spot, closes on air
            self.move_ee([tgt[0], tgt[1], grasp_z])
            self.grip(0.0)
            self.show_marker(self.ee() + [0, 0, 0.16])
            self.hold(0.5)
        else:                                  # PRECOND_UNMET: refuses, shakes
            self.show_marker(self.ee() + [0, 0, 0.16])
            self._jitter(0.04, 16)
        self.show_marker(None)
        self.grip(0.04)
        self.move_ee([tgt[0], tgt[1], self._hover_z(loc, tgt[2])])

    def _jitter(self, amp: float, n: int):
        c = self.ee().copy()
        t = _t(self.base_angle)
        for k in range(n):
            self._set_arm(self._ik(c + t * amp * math.sin(k * 1.6)))
            self._carry()
            self._present()
        self._set_arm(self._ik(c))

    def place(self, obj: str, loc: str, ok: bool, state_after: dict):
        if not ok:
            c = self.ee()
            self.show_marker(c + [0, 0, 0.18])
            self._jitter(0.04, 16)
            self.show_marker(None)
            return
        self.obj_loc[obj] = loc
        self.held = None
        self._assign_slot(loc, obj)
        tgt = self.slot_pos(loc, obj)
        self.held = obj
        self.move_ee([tgt[0], tgt[1], self._hover_z(loc, tgt[2])])
        self.move_ee(tgt + self.hold_off * -1)
        self.held = None
        self._put(obj, tgt)
        self.grip(0.04)
        self.move_ee([tgt[0], tgt[1], self._hover_z(loc, tgt[2])])

    def _handle_pt(self, s: float) -> np.ndarray:
        a = STATION_ANGLE["drawer"]
        return self._tray_center(s) - _u(a) * 0.17 + [0, 0, TRAY_TOP + 0.045]

    def drawer(self, opening: bool, ok: bool):
        if not ok:
            self._approach(self._station_pt(self.base_loc), self.base_loc)
            self.show_marker(self.ee() + [0, 0, 0.16])
            self._jitter(0.04, 16)
            self.show_marker(None)
            return
        s0, s1 = (0.0, TRAY_SLIDE) if opening else (TRAY_SLIDE, 0.0)
        h = self._handle_pt(s0)
        self._approach(h, "drawer")
        self.grip(0.04)
        self.move_ee(h)
        self.grip(0.0)
        n = max(8, int(TRAY_SLIDE / (0.010 * self.speed)))
        for k in range(1, n + 1):
            self.slide = s0 + (s1 - s0) * _ease(k / n)
            self._set_tray()
            self._set_arm(self._ik(self._handle_pt(self.slide)))
            self._present()
        self.grip(0.04)
        self.move_ee(self._handle_pt(s1) + [0, 0, 0.18])

    # ------------------------------------------------------------ one logged step
    def run_step(self, fr):
        ok = fr.code == "OK"
        g = fr.params.get
        if fr.skill == "goto" and g("loc") in STATION_ANGLE:
            self.goto(g("loc"), ok)
        elif fr.skill == "pick" and (g("obj") in OBJ or not ok):
            self.pick(g("obj"), ok, fr.code)
        elif fr.skill == "place" and (ok or g("obj") in OBJ):
            self.place(g("obj"), g("loc"), ok, fr.after)
        elif fr.skill in ("open", "close"):
            self.drawer(fr.skill == "open", ok)
        else:                                  # malformed call (unknown skill / bad argument): refuse
            self.show_marker(self.ee() + [0, 0, 0.18])
            self._jitter(0.04, 14)
        self.sync(fr.after)

    # ------------------------------------------------------------ rendering
    def set_hud(self, lines, color=(255, 255, 255), n_colored: int = 1):
        """Show `lines` top-left. The last `n_colored` lines use `color`, the rest are white."""
        self.hud_lines, self.hud_color, self.hud_n = list(lines), color, n_colored

    def _project(self, pt):
        v = np.array(self.view).reshape(4, 4).T @ np.append(pt, 1.0)
        c = np.array(self.proj).reshape(4, 4).T @ v
        if c[3] <= 0:
            return None
        n = c[:3] / c[3]
        return (n[0] + 1) / 2 * self.size[0], (1 - n[1]) / 2 * self.size[1]

    def frame_array(self) -> np.ndarray:
        w, h = self.size
        img = p.getCameraImage(w, h, self.view, self.proj, renderer=p.ER_TINY_RENDERER,
                               flags=p.ER_NO_SEGMENTATION_MASK)[2]
        arr = np.reshape(np.array(img, dtype=np.uint8), (h, w, 4))[:, :, :3]
        from PIL import Image, ImageDraw, ImageFont
        im = Image.fromarray(arr).convert("RGBA")
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        try:
            f, fs = ImageFont.load_default(size=max(13, h // 30)), ImageFont.load_default(size=max(12, h // 38))
        except TypeError:
            f = fs = ImageFont.load_default()
        for name, pt in self.station_label.items():
            xy = self._project(pt)
            if xy:
                d.text(xy, name, font=fs, fill=(255, 255, 255, 255), anchor="mm", stroke_width=2,
                       stroke_fill=(0, 0, 0, 255))
        if self.hud_lines:
            lh = max(17, h // 26)
            d.rectangle([0, 0, w, lh * len(self.hud_lines) + 10], fill=(0, 0, 0, 150))
            for i, line in enumerate(self.hud_lines):
                col = self.hud_color if i >= len(self.hud_lines) - self.hud_n else (255, 255, 255)
                d.text((10, 6 + i * lh), line, font=f, fill=col + (255,))
        return np.array(Image.alpha_composite(im, lay).convert("RGB"))

    def _present(self):
        if not self.render:
            return
        if self.gui:
            time.sleep(1.0 / self.fps)
            self._gui_hud()
        elif self.writer is not None:
            self.writer.append_data(self.frame_array())
            self.n_frames += 1

    def _gui_hud(self):
        for i, line in enumerate(self.hud_lines):
            kw = dict(textSize=1.4, textColorRGB=[c / 255 for c in self.hud_color] if i >= len(self.hud_lines) - self.hud_n
                      else [1, 1, 1])
            self._hud_ids[i] = p.addUserDebugText(line, [-1.0, 0.0, 1.05 - i * 0.07], **kw,
                                                  replaceItemUniqueId=self._hud_ids.get(i, -1))

    def card(self, lines, seconds: float = 2.5):
        """A plain title card (video mode only)."""
        if not self.render or self.gui or self.writer is None:
            return
        from PIL import Image, ImageDraw, ImageFont
        w, h = self.size
        im = Image.new("RGB", (w, h), (18, 18, 24))
        d = ImageDraw.Draw(im)
        try:
            f = ImageFont.load_default(size=max(18, h // 18))
        except TypeError:
            f = ImageFont.load_default()
        lh = max(26, h // 12)
        y0 = h // 2 - lh * len(lines) // 2
        for i, line in enumerate(lines):
            d.text((w // 2, y0 + i * lh), line, font=f, fill=(255, 255, 255), anchor="mm")
        arr = np.array(im)
        for _ in range(int(seconds * self.fps)):
            self.writer.append_data(arr)
            self.n_frames += 1

    def close(self):
        if p.isConnected(self.cid):
            p.disconnect(self.cid)
```

## `src/pfr/viz/play.py`
```python
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
```

## `scripts/replay.py`
```python
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
```

## `scripts/make_reel.py`
```python
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
```

## `tests/test_viz_state.py`
```python
import pytest

from pfr.faults import CELLS
from pfr.llm import LLMClient
from pfr.methods import make_method
from pfr.runner import run_episode
from pfr.tasks import TASKS
from pfr.viz.state import ReplayMismatch, reconstruct


def row_for(task, cell, method):
    return run_episode(task, cell, 0, make_method(method), LLMClient("stub", 0))


@pytest.mark.parametrize("cell", CELLS)
@pytest.mark.parametrize("method", ["B0", "B3", "B4"])
def test_replay_reproduces_every_logged_code_and_outcome(cell, method):
    # 11 cells x 3 methods x 20 tasks = 660 real episodes replayed against their own logs
    for t in TASKS:
        row = row_for(t, cell, method)
        ep = reconstruct(row)
        assert len(ep.frames) == len(row["steps"])
        if row["outcome"] == "success":
            assert ep.final_goal_ok


def test_mismatch_is_detected():
    row = row_for(TASKS[0], "TR-T1", "B0")
    row["steps"][1]["code"] = "OK"          # the faulted pick actually failed
    with pytest.raises(ReplayMismatch):
        reconstruct(row)


def test_st_fault_object_starts_elsewhere():
    ep = reconstruct(row_for(TASKS[0], "ST-P", "B0"))
    assert ep.initial["objects"]["apple"] == "gone"
    assert "gone" in ep.hidden


def test_known_degenerate_st_f_tasks_are_flagged_by_goal_at_t0():
    """Finding: for 6 of 20 tasks the ST-F hidden location equals the goal location, so the goal is
    already true at t=0. The replay shows it; this test pins the number so a fix is a conscious change."""
    from pfr.env import Env
    from pfr.faults import FaultyEnv, build_fault
    bad = []
    for t in TASKS:
        f = build_fault(t, "ST-F", 0)
        e = Env(t["init_state"]); FaultyEnv(e, f)
        if e.goal_satisfied(t["goal"]):
            bad.append(t["id"])
    assert bad == ["t01", "t04", "t07", "t13", "t17", "t19"]
```

## `tests/test_viz_scene.py`
```python
"""Needs pybullet; skipped (not failed) if it is not installed. Headless, no rendering."""
import numpy as np
import pytest

pytest.importorskip("pybullet")

from pfr.faults import CELLS  # noqa: E402
from pfr.llm import LLMClient  # noqa: E402
from pfr.methods import make_method  # noqa: E402
from pfr.runner import run_episode  # noqa: E402
from pfr.tasks import TASKS  # noqa: E402
from pfr.viz.scene import Scene  # noqa: E402
from pfr.viz.state import reconstruct  # noqa: E402


@pytest.fixture(scope="module")
def sc():
    s = Scene(gui=False, render=False, speed=8.0)
    yield s
    s.close()


def play(sc, task, cell, method):
    row = run_episode(task, cell, 0, make_method(method), LLMClient("stub", 0))
    ep = reconstruct(row)
    sc.load_state(ep.initial)
    for fr in ep.frames:
        sc.run_step(fr)
    return ep


def test_every_clean_task_ends_with_objects_at_their_goal_and_ik_is_accurate(sc):
    for t in TASKS:
        sc.max_ik_err = 0.0
        ep = play(sc, t, "NONE", "B0")
        assert ep.final_goal_ok
        for obj, loc in t["goal"]["at"].items():
            assert np.linalg.norm(sc.obj_pos(obj) - sc.slot_pos(loc, obj)) < 0.01, (t["id"], obj)
        assert sc.held is None
        assert sc.max_ik_err < 0.03, (t["id"], sc.max_ik_err)


@pytest.mark.parametrize("cell", CELLS)
def test_every_fault_cell_replays_without_error_and_scene_matches_world(sc, cell):
    for t in TASKS[:6]:
        ep = play(sc, t, cell, "B3")
        last = ep.frames[-1].after
        for obj, loc in last["objects"].items():
            if loc in ("gone", "gripper"):
                continue
            assert np.linalg.norm(sc.obj_pos(obj) - sc.slot_pos(loc, obj)) < 0.01, (t["id"], cell, obj)
        assert (sc.held is None) == (last["holding"] is None)


def test_drawer_slides_and_returns(sc):
    t4 = next(t for t in TASKS if t["id"] == "t04")
    play(sc, t4, "NONE", "B0")
    assert sc.slide == 0.0                      # the plan closes the drawer again
    t6 = next(t for t in TASKS if t["id"] == "t06")
    play(sc, t6, "NONE", "B0")
    assert sc.slide == 0.0


def test_malformed_calls_are_refused_not_crashed(sc):
    from pfr.viz.state import Frame
    st = {"robot_loc": "table", "holding": None, "drawer_open": False,
          "objects": {"apple": "counter", "cup": "shelf", "plate": "sink", "knob_key": "drawer", "bowl": "table"}}
    sc.load_state(st)
    for skill, params in [("goto", {"loc": "kitchen"}), ("goto", {"loc": None}), ("pick", {"obj": "banana", "grasp": "top"}),
                          ("place", {"obj": None, "loc": "mars", "orient": "flat"}), ("dance", {}), ("open", {})]:
        sc.run_step(Frame(1, skill, params, "PRECOND_UNMET", "invalid call", "", st, st))
```
