"""bld_junk_throne_1x1: a throne of crates, a pot lid and a saddle, for the colony's best thief. A decoration.

A big crate for the seat with a stolen saddle strapped on as the cushion; two stacked crates for the arms; two posts
behind carrying a dented copper pot lid as the backrest, with a teal pennant flying from a spoon on top. There's a gap
under the backrest: a seated raccoon's tail goes back through it and lies along the seat. A red rug in front, coins
and a gold goblet at the foot.

The best thief sits there (spot_seat: work_drink with prop_mug, a king with his drink).

Clips (24 fps)
  idle  48 fr  the pennant flutters
  work  48 fr  the same, a little livelier (someone's on the throne)

Run:  python3 tools/build_junk_throne.py   (--no-renders)
Out:  junk_throne.blend, export/bld_junk_throne_1x1.glb, renders/bld_junk_throne_loops.gif
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
NAME = "bld_junk_throne_1x1"
FRAMES = 48
SEAT_Z = 0.14                                    # the saddle's flat top
SPOT = V((0.0, -0.02, SEAT_Z + 0.0015))          # the sitter, facing the front (-Y)
SEAT = (-0.15, 0.15, SPOT.y - 0.08, SPOT.y + 0.36)   # the seat crate: x0 x1 y0 y1 (deep enough for the tail)
BACK_Y = SPOT.y + 0.13                           # the backrest posts, just behind the sitter's back
GAP = 0.2                                        # the backrest starts this far over the seat: the tail goes under it
LID_C = V((0.0, BACK_Y + 0.01, SEAT_Z + GAP + 0.13))
POLE_TOP = LID_C + V((0.0, 0.0, 0.33))


def crate(m, x0, x1, y0, y1, z0, z1, sw="wood_mid"):
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)), (x1 - x0, y1 - y0, z1 - z0), sw, top="wood_light")
    for z in (z0 + 0.02, z1 - 0.02):                                                   # dark battens round it
        m.obox(V(((x0 + x1) / 2, y0 - 0.002, z)), (x1 - x0 + 0.004, 0.006, 0.018), "wood_dark")
    m.obox(V(((x0 + x1) / 2, y0 - 0.003, (z0 + z1) / 2)), ((x1 - x0) * 1.1, 0.004, 0.016), "wood_dark",
           rot=(0, math.atan2(z1 - z0, x1 - x0), 0))


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "stone_mid")
    m.obox(V((0, SEAT[2] - 0.17, 0.005)), (0.34, 0.34, 0.004), "cloth_red")                       # the rug
    m.obox(V((0, SEAT[2] - 0.17, 0.0055)), (0.3, 0.3, 0.004), "cloth_red", top="gold_dark")
    m.obox(V((0, SEAT[2] - 0.17, 0.006)), (0.26, 0.26, 0.004), "cloth_red")
    x0, x1, y0, y1 = SEAT
    crate(m, x0, x1, y0, y1, 0.0, SEAT_Z - 0.03)
    # the saddle: leather pad, raised pommel at the front edge (below the legs), stirrups hanging off the sides
    m.obox(V((0, (y0 + y1) / 2, SEAT_Z - 0.015)), (0.26, y1 - y0 - 0.02, 0.03), "leather", top="leather")
    m.obox(V((0, y0 + 0.015, SEAT_Z - 0.02)), (0.12, 0.03, 0.03), "leather_dark")
    for sx in (-1, 1):
        m.beam(V((sx * 0.13, SPOT.y + 0.05, SEAT_Z - 0.01)), V((sx * 0.155, SPOT.y + 0.05, SEAT_Z - 0.09)), 0.006, "leather_dark")
        m.obox(V((sx * 0.157, SPOT.y + 0.05, SEAT_Z - 0.1)), (0.008, 0.04, 0.02), "iron")             # stirrups
    # the arms: stacked crates either side
    for sx in (-1, 1):
        ax0 = 0.15 if sx > 0 else -0.27
        crate(m, ax0 + 0.005, ax0 + 0.115, y0 + 0.02, BACK_Y + 0.05, 0.0, SEAT_Z + 0.06, "wood_light")
        m.cyl(V((sx * 0.21, y0 + 0.06, SEAT_Z + 0.07)), 0.025, 0.02, "gold", segs=8, cap="gold_light")   # gold knobs
    # the backrest: two posts, a crossbar, the pot lid; a spoon pole with the pennant
    for sx in (-1, 1):
        m.obox(V((sx * 0.13, BACK_Y + 0.02, (SEAT_Z + POLE_TOP.z - 0.25) / 2)), (0.035, 0.035, POLE_TOP.z - 0.25 - SEAT_Z + 0.14),
               "wood_dark")
    m.obox(V((0, BACK_Y + 0.025, SEAT_Z + GAP)), (0.3, 0.03, 0.03), "wood_dark")
    m.cyl(LID_C, 0.13, 0.02, "copper", segs=14, axis=(0, 1, 0), cap="copper")
    m.cyl(LID_C + V((0, -0.012, 0)), 0.1, 0.006, "rust", segs=14, axis=(0, 1, 0))                 # a darker ring
    m.cyl(LID_C + V((0, -0.018, 0)), 0.03, 0.02, "iron_dark", segs=8, axis=(0, 1, 0))           # its knob
    m.obox(LID_C + V((0.05, -0.013, 0.06)), (0.04, 0.004, 0.012), "copper", rot=(0, 0.6, 0))    # a dent
    m.blob(LID_C + V((0, -0.03, 0.0)), V((0.02, 0.01, 0.02)), "gold_light", 6, 3)               # a crown nailed on
    for k in range(3):
        m.cyl(LID_C + V((-0.02 + 0.02 * k, -0.034, 0.02 + 0.006 * (k == 1))), 0.005, 0.02, "gold", segs=4, r2=0.0)
    m.beam(LID_C + V((0, 0.012, 0.1)), POLE_TOP, 0.012, "silver")                               # a long spoon
    m.blob(POLE_TOP + V((0, 0, 0.015)), V((0.018, 0.008, 0.025)), "silver", 6, 3)
    # at its foot: coins, a goblet, a sack of loot
    for k in range(7):
        a = rnd.uniform(-2.6, -0.5)
        r = rnd.uniform(0.28, 0.4)
        m.cyl(V((r * math.cos(a), r * math.sin(a) + 0.05, 0.006 + 0.004 * (k % 3))), 0.016, 0.005, "gold", segs=6)
    m.cyl(V((0.3, -0.3, 0.05)), 0.03, 0.04, "gold", segs=8, r2=0.022, cap="cloth_red")         # goblet
    m.cyl(V((0.3, -0.3, 0.015)), 0.01, 0.03, "gold", segs=6)
    m.cyl(V((0.3, -0.3, 0.003)), 0.025, 0.006, "gold", segs=8)
    B.sack(m, V((-0.32, 0.3, 0.0)), 0.07)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    mm = B.M()
    pole = POLE_TOP + V((0, 0, -0.03))
    mm.obox(pole + V((0.07, 0, -0.03)), (0.14, 0.004, 0.06), "teal", rot=(0, 0.1, 0))
    mm.obox(pole + V((0.07, -0.003, -0.03)), (0.03, 0.002, 0.02), "gold")                       # a paw on it
    parts["pr_pennant_1"] = A.part(mm.obj("pr_pennant_1", coll), root, pole)
    mm = B.M()
    tip = pole + V((0.14, 0, -0.03))
    mm.obox(tip + V((0.045, 0, 0.0)), (0.09, 0.004, 0.045), "teal_light")
    parts["pr_pennant_2"] = A.part(mm.obj("pr_pennant_2", coll), root, tip)
    return root, parts


def clips(parts):
    rel = parts["pr_pennant_2"].location - parts["pr_pennant_1"].location

    def make(wind):
        def pose(p):
            a1 = (12 + 6 * wind) * math.sin(TAU * 2 * p)
            a2 = (20 + 10 * wind) * math.sin(TAU * (2 * p - 0.15)) + 6 * math.sin(TAU * 6 * p)
            r1 = A.q((0, 0, 1), a1)
            return {"pr_pennant_1": (None, r1, None), "pr_pennant_2": ((r1 @ rel) - rel, A.q((0, 0, 1), a1 + a2), None)}
        return pose

    A.animate(parts, {"idle": (FRAMES, make(0.0)), "work": (FRAMES, make(1.0))})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(12))
    A.spot(root, "spot_seat", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "junk_throne.blend"), relative_remap=True)
    A.export()
    rig, mesh, mug = A.raccoon_at(bpy.data.objects["spot_seat"], clip="work_drink", tool="prop_mug")
    allow = [("pr_pennant_1", NAME), ("pr_pennant_2", NAME), ("pr_pennant_1", "pr_pennant_2")]
    probs = A.check(root, 1, 1, crew=[(rig, mesh, mug, "work", {})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, mug], ROOT / "renders" / "bld_junk_throne_loops.gif",
                       target=(0.0, 0.0, 0.3), dist=1.9, pitch=30, idle_frames=24, grid_n=3, step=2)


if __name__ == "__main__":
    main()
