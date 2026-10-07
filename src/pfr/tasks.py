"""20 hand-written tasks. Each task is data:
    id, goal_text, goal, init_state, plan (the oracle plan = the initial plan).

Default world (unless a task overrides it):
    apple@counter  cup@shelf  plate@sink  knob_key@drawer (drawer closed)  bowl@table
    robot@table
"""
from __future__ import annotations

BASE_OBJECTS = {"apple": "counter", "cup": "shelf", "plate": "sink", "knob_key": "drawer", "bowl": "table"}


def goto(loc): return {"skill": "goto", "loc": loc}
def pick(obj, grasp): return {"skill": "pick", "obj": obj, "grasp": grasp}
def place(obj, loc, orient): return {"skill": "place", "obj": obj, "loc": loc, "orient": orient}
def open_drawer(force): return {"skill": "open", "container": "drawer", "force": force}
def close_drawer(): return {"skill": "close", "container": "drawer"}


def task(tid, goal_text, goal_at, plan, robot="table", goal_drawer_open=None):
    return {
        "id": tid,
        "goal_text": goal_text,
        "goal": {"at": goal_at, "drawer_open": goal_drawer_open},
        "init_state": {
            "robot_loc": robot,
            "holding": None,
            "drawer_open": False,
            "objects": dict(BASE_OBJECTS),
        },
        "plan": plan,
    }


TASKS = [
    task("t01", "put the apple on the table", {"apple": "table"},
         [goto("counter"), pick("apple", "top"), goto("table"), place("apple", "table", "upright")]),
    task("t02", "move the cup to the counter", {"cup": "counter"},
         [goto("shelf"), pick("cup", "side"), goto("counter"), place("cup", "counter", "upright")]),
    task("t03", "put the plate on the shelf", {"plate": "shelf"},
         [goto("sink"), pick("plate", "pinch"), goto("shelf"), place("plate", "shelf", "flat")]),
    task("t04", "get the knob_key from the drawer and put it on the table", {"knob_key": "table"},
         [goto("drawer"), open_drawer("med"), pick("knob_key", "pinch"), close_drawer(),
          goto("table"), place("knob_key", "table", "upright")], goal_drawer_open=False),
    task("t05", "put the bowl on the counter", {"bowl": "counter"},
         [goto("table"), pick("bowl", "side"), goto("counter"), place("bowl", "counter", "flat")]),
    task("t06", "put the apple in the drawer", {"apple": "drawer"},
         [goto("counter"), pick("apple", "top"), goto("drawer"), open_drawer("low"),
          place("apple", "drawer", "upright"), close_drawer()], goal_drawer_open=False),
    task("t07", "move the cup from the shelf to the sink", {"cup": "sink"},
         [goto("shelf"), pick("cup", "side"), goto("sink"), place("cup", "sink", "upright")]),
    task("t08", "move the cup to the table, then put the apple on the shelf",
         {"cup": "table", "apple": "shelf"},
         [goto("shelf"), pick("cup", "side"), goto("table"), place("cup", "table", "upright"),
          goto("counter"), pick("apple", "top"), goto("shelf"), place("apple", "shelf", "upright")]),
    task("t09", "put the plate on the counter", {"plate": "counter"},
         [goto("sink"), pick("plate", "pinch"), goto("counter"), place("plate", "counter", "flat")],
         robot="shelf"),
    task("t10", "get the knob_key from the drawer and put it on the shelf", {"knob_key": "shelf"},
         [goto("drawer"), open_drawer("high"), pick("knob_key", "pinch"), close_drawer(),
          goto("shelf"), place("knob_key", "shelf", "upright")], goal_drawer_open=False),
    task("t11", "put the bowl in the sink", {"bowl": "sink"},
         [goto("table"), pick("bowl", "top"), goto("sink"), place("bowl", "sink", "flat")]),
    task("t12", "put the plate on the counter and the bowl in the sink",
         {"plate": "counter", "bowl": "sink"},
         [goto("sink"), pick("plate", "pinch"), goto("counter"), place("plate", "counter", "flat"),
          goto("table"), pick("bowl", "side"), goto("sink"), place("bowl", "sink", "flat")]),
    task("t13", "put the apple on the shelf", {"apple": "shelf"},
         [goto("counter"), pick("apple", "side"), goto("shelf"), place("apple", "shelf", "upright")],
         robot="sink"),
    task("t14", "move the plate from the sink to the table", {"plate": "table"},
         [goto("sink"), pick("plate", "pinch"), goto("table"), place("plate", "table", "flat")],
         robot="counter"),
    task("t15", "put the cup in the drawer", {"cup": "drawer"},
         [goto("shelf"), pick("cup", "side"), goto("drawer"), open_drawer("med"),
          place("cup", "drawer", "upright"), close_drawer()], goal_drawer_open=False),
    task("t16", "put the bowl on the shelf and the apple on the table",
         {"bowl": "shelf", "apple": "table"},
         [goto("table"), pick("bowl", "top"), goto("shelf"), place("bowl", "shelf", "flat"),
          goto("counter"), pick("apple", "side"), goto("table"), place("apple", "table", "upright")]),
    task("t17", "move the apple to the sink", {"apple": "sink"},
         [goto("counter"), pick("apple", "top"), goto("sink"), place("apple", "sink", "flat")],
         robot="shelf"),
    task("t18", "take the knob_key from the drawer to the counter", {"knob_key": "counter"},
         [goto("drawer"), open_drawer("low"), pick("knob_key", "pinch"), close_drawer(),
          goto("counter"), place("knob_key", "counter", "upright")], goal_drawer_open=False),
    task("t19", "put the cup on the table", {"cup": "table"},
         [goto("shelf"), pick("cup", "top"), goto("table"), place("cup", "table", "upright")]),
    task("t20", "move the plate to the counter, then the apple to the sink",
         {"plate": "counter", "apple": "sink"},
         [goto("sink"), pick("plate", "pinch"), goto("counter"), place("plate", "counter", "flat"),
          pick("apple", "side"), goto("sink"), place("apple", "sink", "upright")]),
]


def get_task(task_id: str) -> dict:
    for t in TASKS:
        if t["id"] == task_id:
            return t
    raise KeyError(task_id)
