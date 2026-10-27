"""bld_stockpile_2x2: the colony's store yard, where haulers drop off and fetch goods.

A plank yard. At the back, a tarp lean-to over stacked crates, barrels and sacks; a lantern hangs from its front beam.
At the front, an open crate being packed: the raccoon crouches behind it (spot_work, facing the front) and settles
the goods with both paws (work_stash). A hand-cart of sacks, a tally board and a coil of rope round it.

Clips (24 fps)
  idle  48 fr  the tarp's loose corner flaps, the lantern and a rope end sway (the open crate's lid leans open)
  work  48 fr  as idle, plus the goods on top settle each time the paws shove them down, and the lid rattles

The goods settle on work_stash's shoves, so start the building's work and the raccoon's work_stash together (both
48 frames).

Run:  python3 tools/build_stockpile.py   (--no-renders)
Out:  stockpile.blend, export/bld_stockpile_2x2.glb, renders/bld_stockpile_loops.gif, renders/qa_buildings.txt
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
import build_fishing_spot as FS  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_stockpile_2x2"
FRAMES = 48
DECK = 0.03                                      # top of the plank yard
SPOT = V((0.02, -0.2, DECK + 0.0015))            # behind the open crate, facing the front (-Y)
CRATE = (SPOT.x - 0.16, SPOT.x + 0.16, SPOT.y - 0.31, SPOT.y - 0.1)   # x0 x1 y0 y1, outer; the near wall clears the toes
CRATE_H = 0.08
WALL = 0.012
LIP = 0.045                                      # height of the crate's near side (the raccoon's)
SHOVES = (0.3, 0.42)                             # work_stash's shoves (build_raccoon_jobs.stash)
TARP_FRONT = (0.5, 0.62)                         # y and height of the lean-to's front beam (it slopes down to the
TARP_BACK = (0.9, 0.46)                          # back, so the game camera sees the goods under it)


def packing_crate(m, box, floor, sw="wood_mid"):
    """An open crate (x0, x1, y0, y1 outer) standing on `floor`. The side toward +Y (where the raccoon crouches) is a
    low lip, so the paws reach over it into the goods: a full-height wall there would sit in the wrists."""
    x0, x1, y0, y1 = box
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, floor + 0.005)), (x1 - x0, y1 - y0, 0.01), "wood_dark")
    m.obox(V(((x0 + x1) / 2, y0 + WALL / 2, floor + CRATE_H / 2)), (x1 - x0, WALL, CRATE_H), sw, top="wood_light")
    m.obox(V(((x0 + x1) / 2, y1 - WALL / 2, floor + LIP / 2)), (x1 - x0, WALL, LIP), sw, top="wood_light")
    for x in (x0 + WALL / 2, x1 - WALL / 2):
        m.obox(V((x, (y0 + y1) / 2, floor + CRATE_H / 2)), (WALL, y1 - y0 - 2 * WALL, CRATE_H), sw, top="wood_light")


def build(coll, rnd):
    m = B.M()
    # ---- plank yard
    a = 0.97
    n = 9
    for k in range(n):
        x = -a + 2 * a * (k + 0.5) / n
        m.obox(V((x, 0, DECK / 2)), (2 * a / n - 0.012, 2 * a, DECK), "wood_light" if k % 2 else "wood_mid")
    for y in (-0.8, 0.0, 0.8):
        m.obox(V((0, y, DECK + 0.002)), (2 * a - 0.02, 0.03, 0.004), "wood_dark")                 # cross battens
    # ---- lean-to: posts, beams, the tarp
    for x in (-0.86, 0.86):
        for (y, h) in (TARP_FRONT, TARP_BACK):
            m.obox(V((x, y, h / 2)), (0.04, 0.04, h), "wood_dark")
    m.beam(V((-0.86, TARP_FRONT[0], TARP_FRONT[1])), V((0.86, TARP_FRONT[0], TARP_FRONT[1])), 0.03, "wood_dark")
    m.beam(V((-0.86, TARP_BACK[0], TARP_BACK[1])), V((0.86, TARP_BACK[0], TARP_BACK[1])), 0.03, "wood_dark")
    fy, fz = TARP_FRONT
    by, bz = TARP_BACK
    ang = math.atan2(bz - fz, by - fy)
    L = math.hypot(by - fy, bz - fz)
    m.obox(V((0, (fy + by) / 2, (fz + bz) / 2 + 0.022)), (1.8, L + 0.04, 0.012), "cloth_blue", rot=(ang, 0, 0))
    # ---- under the tarp: crates (left), barrels (right), sacks between
    B.crate(m, V((-0.62, 0.66, DECK)), 0.24, 0.08)
    B.crate(m, V((-0.62, 0.66, DECK + 0.24)), 0.2, -0.15)
    B.crate(m, V((-0.36, 0.7, DECK)), 0.2, -0.05)
    B.crate(m, V((-0.62, 0.36, DECK)), 0.18, 0.2)
    for c in ((0.62, 0.7), (0.4, 0.74)):
        m.cyl(V((*c, DECK + 0.13)), 0.1, 0.26, "wood_mid", cap="wood_dark", segs=8)
        for z in (0.05, 0.21):
            m.cyl(V((*c, DECK + z)), 0.105, 0.018, "iron", segs=8)
    for c in ((0.05, 0.72), (0.18, 0.62), (-0.06, 0.58)):
        B.sack(m, V((*c, DECK)), 0.07)
    # ---- the open crate (front): walls; the goods inside are their own object
    packing_crate(m, CRATE, DECK)
    # ---- front left: hand-cart with sacks; front right: tally board, rope coil, a loose sack
    hc = V((-0.62, -0.55, DECK))
    m.obox(hc + V((0, 0, 0.09)), (0.3, 0.22, 0.02), "wood_light", rot=(0, 0.12, 0))
    for s in (-1, 1):
        m.cyl(hc + V((0.06, s * 0.125, 0.06)), 0.06, 0.02, "wood_dark", axis=(0, 1, 0), segs=8, cap="wood_mid")
        m.beam(hc + V((-0.14, s * 0.09, 0.08)), hc + V((-0.3, s * 0.09, 0.04)), 0.018, "wood_dark")   # handles
    B.sack(m, hc + V((-0.04, -0.04, 0.1)), 0.06)
    B.sack(m, hc + V((0.06, 0.05, 0.1)), 0.055, sw="cloth_cream")
    tb = V((0.66, -0.62, DECK))
    m.obox(tb + V((0, 0, 0.2)), (0.035, 0.035, 0.4), "wood_dark")
    m.obox(tb + V((0, -0.025, 0.3)), (0.2, 0.012, 0.16), "soot")
    for k in range(4):                                                                       # chalk tallies
        m.obox(tb + V((-0.06 + 0.022 * k, -0.032, 0.3)), (0.006, 0.004, 0.08), "cloth_cream")
    m.obox(tb + V((0.0, -0.032, 0.3)), (0.11, 0.004, 0.006), "cloth_cream", rot=(0, 0.5, 0))
    m.cyl(V((0.4, -0.75, DECK + 0.015)), 0.07, 0.03, "rope", segs=10, cap="rope_dark")                 # rope coil
    B.sack(m, V((0.42, -0.42, DECK)), 0.065)
    root = m.obj(NAME, coll)
    # the crate's goods (still): the paws may press into them
    m = B.M()
    x0, x1, y0, y1 = CRATE
    gi = (x0 + WALL, x1 - WALL, y0 + WALL, y1 - WALL)
    m.obox(V(((gi[0] + gi[1]) / 2, (gi[2] + gi[3]) / 2, DECK + 0.035)), (gi[1] - gi[0] - 0.004, gi[3] - gi[2] - 0.004, 0.05),
           "burlap")
    for k in range(9):
        p = V((rnd.uniform(gi[0] + 0.03, gi[1] - 0.03), rnd.uniform(gi[2] + 0.03, gi[3] - 0.03), DECK + 0.06))
        m.blob(p, V((0.022, 0.022, 0.018)), rnd.choice(["cloth_red", "cloth_red", "moss_light", "cloth_cream"]), 6, 3)
    goods = m.obj("pr_goods", coll)
    goods.parent = root
    parts = {}
    # the lid, hinged on the far wall's top edge
    m = B.M()
    hinge = V(((x0 + x1) / 2, y0, DECK + CRATE_H))
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, DECK + CRATE_H + 0.007)), (x1 - x0 + 0.01, y1 - y0 + 0.004, 0.012), "wood_light")
    for x in (x0 + 0.05, x1 - 0.05):
        m.obox(V((x, (y0 + y1) / 2, DECK + CRATE_H + 0.015)), (0.03, y1 - y0, 0.006), "wood_dark")   # battens
    parts["pr_lid"] = A.part(m.obj("pr_lid", coll), root, hinge + V((0, 0, 0.001)))
    # goods on top that settle: an apple, a turnip, a bundle
    for i, (dx, dy, kind) in enumerate(((-0.07, 0.05, "apple"), (0.08, 0.06, "turnip"), (0.0, -0.04, "bundle"))):
        c = V(((x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy, DECK + 0.078))
        m = B.M()
        if kind == "apple":
            m.blob(c, V((0.024, 0.024, 0.021)), "cloth_red", 7, 4)
        elif kind == "turnip":
            m.blob(c, V((0.022, 0.022, 0.02)), "cloth_cream", 7, 4)
            m.cyl(c + V((0, 0, 0.026)), 0.006, 0.02, "moss", segs=4, r2=0.012)
        else:
            m.obox(c + V((0, 0, -0.004)), (0.07, 0.04, 0.026), "burlap", rot=(0, 0, 0.3))
            m.obox(c + V((0, 0, -0.004)), (0.012, 0.042, 0.028), "rope", rot=(0, 0, 0.3))
        parts[f"pr_good_{i + 1}"] = A.part(m.obj(f"pr_good_{i + 1}", coll), root, c)
    # the tarp's loose corner (front left) and a rope end; a lantern on the front beam
    m = B.M()
    corner = V((-0.6, fy, fz + 0.012))
    m.obox(corner + V((0, -0.05, -0.006)), (0.3, 0.1, 0.01), "cloth_blue")
    parts["pr_tarp_flap"] = A.part(m.obj("pr_tarp_flap", coll), root, corner)
    m = B.M()
    rt = V((0.45, fy, fz - 0.016))
    m.cyl(rt + V((0, 0, -0.05)), 0.006, 0.1, "rope", segs=4)
    parts["pr_rope_end"] = A.part(m.obj("pr_rope_end", coll), root, rt)
    m = B.M()
    lt = V((0.15, fy, fz - 0.016))
    m.cyl(lt + V((0, 0, -0.03)), 0.003, 0.06, "iron_dark", segs=4)
    m.obox(lt + V((0, 0, -0.085)), (0.045, 0.045, 0.06), "flame_yellow")
    m.obox(lt + V((0, 0, -0.052)), (0.055, 0.055, 0.012), "iron_dark")
    m.obox(lt + V((0, 0, -0.118)), (0.055, 0.055, 0.01), "iron_dark")
    parts["pr_lantern"] = A.part(m.obj("pr_lantern", coll), root, lt)
    return root, goods, parts


def clips(parts):
    def common(p):
        pose = {}
        flap = math.sin(TAU * 2 * p) + 0.4 * math.sin(TAU * 6 * p + 1)
        pose["pr_tarp_flap"] = (None, A.q((1, 0, 0), 14 + 12 * flap), None)
        pose["pr_rope_end"] = (None, A.q((1, 0.3, 0), 10 * math.sin(TAU * (p + 0.2))), None)
        pose["pr_lantern"] = (None, A.q((1, 0, 0), 6 * math.sin(TAU * p)) @ A.q((0, 1, 0), 3 * math.sin(TAU * 2 * p)), None)
        return pose

    def idle(p):
        pose = common(p)
        pose["pr_lid"] = (None, A.q((1, 0, 0), 112), None)          # propped open, leaning out
        return pose

    def work(p):
        pose = common(p)
        hit = sum(math.exp(-((p - c) ** 2) / 0.0012) for c in SHOVES)
        pose["pr_lid"] = (None, A.q((1, 0, 0), 112 - 2 * hit), None)  # open, leaning out; it rattles on the shoves
        for i, ph in ((1, 0.0), (2, 0.04), (3, 0.02)):
            h = sum(math.exp(-((p - c - ph) ** 2) / 0.0015) for c in SHOVES)
            pose[f"pr_good_{i}"] = (V((0, 0, -0.007 * h)), A.q((1, 0.5 * i, 0), 8 * h * math.sin(TAU * 4 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, goods, parts = build(coll, random.Random(41))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(goods) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(goods)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "stockpile.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_stash")
    allow = [("pr_lid", NAME), ("pr_tarp_flap", NAME), ("pr_rope_end", NAME), ("pr_lantern", NAME)] + \
            [(f"pr_good_{i}", "pr_goods") for i in (1, 2, 3)] + [("pr_goods", "pr_lid")]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, None, "work", {"pr_goods": None, "pr_good_1": None, "pr_good_2": None,
                                                               "pr_good_3": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_stockpile_loops.gif",
                       target=(0.0, 0.05, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
