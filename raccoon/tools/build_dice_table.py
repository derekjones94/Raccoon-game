"""bld_dice_table_1x1: an upturned crate with dice and coins on it. A decoration, and a game for two.

A crate stood upside down as a table (turned so a flat side faces each player), a scrap of green cloth over it, three
dice, a stack of bets on each side, a cup to throw from and a candle stub. Two cushions on the floor, on the
diagonals, where two raccoons sit and play (spot_seat_1, _2: work_chat). A torn card and a few coins underfoot.

The players sit on the diagonals because a seated raccoon's tail lies about a third of a metre behind it: on a 1x1
lot that's the only way two of them fit.

Clips (24 fps)
  idle  48 fr  a die wobbles now and then, the candle flickers
  work  48 fr  someone's playing: a die tumbles and rolls to a stop each loop, the coin stacks jump, the candle leans

Run:  python3 tools/build_dice_table.py   (--no-renders)
Out:  dice_table.blend, export/bld_dice_table_1x1.glb, renders/bld_dice_table_loops.gif
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_dice_table_1x1"
FRAMES = 48
HALF, TOP = 0.08, 0.13                           # the crate: half size (turned 45 deg), top
CUSHION = 0.008
SEAT_R = HALF + 0.135                            # each player: a flat side of the crate just past the toes
SEAT_ANGLES = (-45, 135)                         # front-right and back-left: the game camera sees both side-on
ROT = math.pi / 4


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "wood_weathered")
    # ---- the upturned crate, a green cloth, dice, bets, the cup, a candle stub
    m.obox(V((0, 0, TOP / 2)), (2 * HALF, 2 * HALF, TOP), "wood_mid", top="wood_light", rot=(0, 0, ROT))
    for z in (0.03, 0.1):
        m.obox(V((0, 0, z)), (2 * HALF + 0.006, 2 * HALF + 0.006, 0.016), "wood_dark", rot=(0, 0, ROT))
    m.obox(V((0, 0, TOP + 0.002)), (2 * HALF - 0.02, 2 * HALF - 0.02, 0.004), "moss", rot=(0, 0, ROT + 0.1))
    for k, (x, y) in enumerate(((-0.05, 0.03), (0.04, -0.05))):                                    # bets
        for j in range(3 + k):
            m.cyl(V((x, y, TOP + 0.007 + 0.006 * j)), 0.014, 0.005, "gold" if j % 2 else "gold_light", segs=6)
    m.cyl(V((0.06, 0.06, TOP + 0.025)), 0.02, 0.04, "leather", segs=8, r2=0.024, cap="leather_dark")   # dice cup
    m.cyl(V((-0.06, -0.06, TOP + 0.014)), 0.009, 0.02, "cloth_cream", segs=6, cap="bone")             # candle stub
    for k in range(4):                                                                                 # underfoot
        a = TAU * k / 4 + 0.6
        m.cyl(V((0.36 * math.cos(a), 0.36 * math.sin(a), 0.006)), 0.014, 0.005, "gold", segs=6)
    m.obox(V((0.25, -0.3, 0.005)), (0.04, 0.055, 0.002), "cloth_cream", rot=(0, 0, 0.5))               # a torn card
    m.obox(V((0.25, -0.3, 0.0065)), (0.012, 0.012, 0.001), "cloth_red", rot=(0, 0, 0.5))
    # ---- the cushions
    for k, a in enumerate(SEAT_ANGLES):
        r = math.radians(a)
        c = V((SEAT_R * math.cos(r), SEAT_R * math.sin(r), CUSHION / 2))
        m.cyl(c + V((0.04 * math.cos(r), 0.04 * math.sin(r), 0)), 0.11,                              # under the seat
              CUSHION, "cloth_red" if k else "cloth_blue", segs=10, cap="cloth_mustard" if k else "teal")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    for i, (x, y, rz) in enumerate(DICE):
        mm = B.M()
        c = V((x, y, TOP + 0.004 + 0.011))
        mm.obox(c, (0.022, 0.022, 0.022), "bone", rot=(0, 0, rz))
        for dx, dy in ((-0.005, -0.005), (0.005, 0.005), (0.0, 0.0)):                                    # pips on top
            mm.obox(c + V((dx, dy, 0.011)), (0.004, 0.004, 0.002), "soot", rot=(0, 0, rz))
        parts[f"pr_die_{i + 1}"] = A.part(mm.obj(f"pr_die_{i + 1}", coll), root, c - V((0, 0, 0.011)))
    mm = B.M()
    fc = V((-0.06, -0.06, TOP + 0.026))                            # the cup and candle sit off the players' line
    mm.cyl(fc + V((0, 0, 0.01)), 0.006, 0.02, "flame_yellow", segs=5, r2=0.0)
    parts["pr_flame"] = A.part(mm.obj("pr_flame", coll), root, fc)
    return root, parts


DICE = [(0.0, 0.0, 0.3), (0.03, -0.035, 1.1), (-0.035, 0.03, 0.7)]


def clips(parts):
    def flame(p, lean):
        fl = math.sin(TAU * 7 * p) + 0.6 * math.sin(TAU * 11 * p + 1)
        return (None, A.q((1, 0.4, 0), 5 * fl + lean), (1, 1, 1 + 0.15 * math.sin(TAU * 9 * p)))

    def idle(p):
        w = math.exp(-((p - 0.6) ** 2) / 0.002)                          # now and then: the first die rocks on an edge
        return {"pr_die_1": (None, A.q((1, 0, 0), 12 * w * math.sin(TAU * 10 * p)), None), "pr_flame": flame(p, 0)}

    def work(p):
        out = {"pr_flame": flame(p, 8 * math.sin(TAU * p))}
        t = min(1.0, max(0.0, (p - 0.2) / 0.4))                          # a die thrown: it tumbles across and settles
        if 0.0 < t < 1.0:
            hop = 0.03 * abs(math.sin(math.pi * 3 * t)) * (1 - t)
            out["pr_die_2"] = (V((-0.035 * math.sin(math.pi * t), 0.03 * math.sin(math.pi * t), hop)),
                               A.q((1, 0, 0), 360 * 2 * (3 * t * t - 2 * t * t * t)), None)
        else:
            out["pr_die_2"] = (None, None, None)
        w = math.exp(-((p - 0.62) ** 2) / 0.001)
        out["pr_die_1"] = (V((0, 0, 0.004 * w)), A.q((0, 1, 0), 10 * w * math.sin(TAU * 12 * p)), None)
        return out

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(6))
    for i, a in enumerate(SEAT_ANGLES):
        r = math.radians(a)
        A.spot(root, f"spot_seat_{i + 1}", V((SEAT_R * math.cos(r), SEAT_R * math.sin(r), CUSHION + 0.0015)),
               (-math.cos(r), -math.sin(r), 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "dice_table.blend"), relative_remap=True)
    A.export()
    crew, objs = [], []
    for i in range(len(SEAT_ANGLES)):
        rig, mesh, _ = A.raccoon_at(bpy.data.objects[f"spot_seat_{i + 1}"], clip="work_chat")
        crew.append((rig, mesh, None, "work", {}))
        objs += [rig, mesh]
    allow = [(n, NAME) for n in parts] + [("pr_die_1", "pr_die_2"), ("pr_die_2", "pr_die_3"), ("pr_die_1", "pr_die_3")]
    probs = A.check(root, 1, 1, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_dice_table_loops.gif",
                       target=(0.0, 0.0, 0.12), dist=1.9, pitch=40, idle_frames=24, grid_n=3, step=2)


if __name__ == "__main__":
    main()
