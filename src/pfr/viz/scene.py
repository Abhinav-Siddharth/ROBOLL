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
