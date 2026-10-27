"""bld_washing_pool_2x1: a shallow stone-rimmed pool where raccoons wash their food (Grubbing).

A low pool with a pebble floor and a hand's depth of water. The raccoon WADES into the shallows (spot_work, inside
the rim, facing the front) and crouches to rub its food in the water (work_scrub). Washed finds dry on a plank on
the rim; laundry hangs on a line along the back; an apple and a carrot bob on the water; a washboard leans on the
rim; a bucket and a basket stand outside.

Clips (24 fps)
  idle  48 fr  the cloths stir on the line, the floating apple and carrot bob, a slow ring of ripples
  work  48 fr  as idle, plus rings of ripples spreading from the raccoon's paws (it scrubs twice a loop)

Run:  python3 tools/build_washing_pool.py   (--no-renders)
Out:  washing_pool.blend, export/bld_washing_pool_2x1.glb, renders/bld_washing_pool_loops.gif, renders/qa_buildings.txt
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
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
NAME = "bld_washing_pool_2x1"
FLOOR = 0.006                                     # pebble floor plate top: the raccoon stands on it
WATER = FLOOR + 0.002 + J.SCRUB_WATER             # water surface: a hand's depth over the raccoon's feet
RIM = 0.075
POOL = (-0.74, 0.74, -0.38, 0.31)                 # rim, outer edge: x0, x1, y0, y1
SPOT = V((-0.22, -0.02, FLOOR + 0.002))           # wading, facing the front (-Y); tail clear of the back rim
PAWS = V((SPOT.x, SPOT.y + J.SCRUB_C.y, WATER))      # where the paws rub (raccoon space == building space here)
FRAMES = 48
LINE_Y = 0.405


def build(coll, rnd):
    m = B.M()
    x0, x1, y0, y1 = POOL
    t = 0.06
    # ---- rim of chunky stones, slightly uneven
    for (a, b, horiz) in (((x0, y0), (x1, y0), True), ((x0, y1), (x1, y1), True), ((x0, y0), (x0, y1), False),
                          ((x1, y0), (x1, y1), False)):
        L = (b[0] - a[0]) if horiz else (b[1] - a[1])
        n = max(2, int(L / 0.2))
        for k in range(n):
            u0, u1 = k / n, (k + 1) / n
            h = RIM + rnd.uniform(-0.008, 0.008)
            if horiz:
                c = V((a[0] + (b[0] - a[0]) * (u0 + u1) / 2, a[1], h / 2))
                size = (L / n - 0.005, t, h)
            else:
                c = V((a[0], a[1] + (b[1] - a[1]) * (u0 + u1) / 2, h / 2))
                size = (t, L / n - 0.005, h)
            m.obox(c, size, rnd.choice(["stone_mid", "stone_light", "stone_mid", "stone_pale"]), top="stone_light")
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, FLOOR / 2)), (x1 - x0 - t, y1 - y0 - t, FLOOR), "stone_dark")   # pebble floor
    for k in range(9):                                                                   # pebbles under the water
        p = V((rnd.uniform(x0 + 0.1, x1 - 0.1), rnd.uniform(y0 + 0.1, y1 - 0.1), FLOOR))
        if (p.xy - SPOT.xy).length < 0.2 or (p.xy - PAWS.xy).length < 0.12:
            continue
        m.blob(p, V((0.02, 0.016, 0.01)), rnd.choice(["stone_light", "stone_pale"]), 6, 3)
    for c, s_ in ((V((0.42, 0.12, FLOOR)), 0.06), (V((0.52, 0.05, FLOOR)), 0.04)):          # boulders breaking the surface
        m.blob(c + V((0, 0, s_ * 0.55)), V((s_ * 1.2, s_, s_ * 1.15)), "stone_light", 6, 4)
    for k, (dx, dy, h) in enumerate(((0, 0, 0.17), (0.025, 0.012, 0.14), (-0.02, 0.018, 0.12))):     # reeds, back left
        c = V((x0 + 0.08 + dx, y1 - 0.08 + dy, FLOOR))
        m.cyl(c + V((0, 0, h / 2)), 0.006, h, "moss", segs=4, r2=0.0015)
        m.cyl(c + V((0, 0, h * 0.82)), 0.009, 0.045, "wood_mid", segs=5)
    # ---- drying plank on the front rim with washed finds; washboard leaning on the right inner rim
    m.obox(V((0.35, y0, RIM + 0.012)), (0.42, 0.09, 0.016), "wood_light")
    for k, (dx, sw, r) in enumerate(((0.2, "cloth_red", 0.018), (0.28, "moss_light", 0.015), (0.36, "cloth_red", 0.017),
                                     (0.44, "torch_orange", 0.016), (0.5, "moss_light", 0.014))):
        m.blob(V((dx, y0, RIM + 0.02 + r * 0.8)), V((r, r, r * 0.9)), sw, 6, 4)
    wb = V((0.7, -0.12, FLOOR))
    m.obox(wb + V((0, 0.0, 0.07)), (0.16, 0.018, 0.15), "wood_weathered", rot=(-0.35, 0, 0))
    for k in range(4):
        m.obox(wb + V((0, -0.028 + 0.0, 0.03 + k * 0.03)), (0.14, 0.008, 0.008), "wood_dark", rot=(-0.35, 0, 0))
    # ---- outside: a bucket and a basket at the front corners, laundry posts at the back
    m.cyl(V((0.86, -0.28, 0.05)), 0.055, 0.1, "wood_mid", segs=8, cap="water")                   # bucket of water
    m.cyl(V((0.86, -0.28, 0.03)), 0.058, 0.012, "iron", segs=8)
    m.cyl(V((0.86, -0.28, 0.08)), 0.058, 0.012, "iron", segs=8)
    m.cyl(V((-0.86, -0.28, 0.035)), 0.06, 0.07, "rope", segs=8, r2=0.07, cap="rope_dark")         # basket of berries
    for k in range(4):
        a = k * 1.6
        m.blob(V((-0.86 + 0.03 * math.cos(a), -0.28 + 0.03 * math.sin(a), 0.075)), V((0.015, 0.015, 0.013)), "cloth_red", 6, 3)
    for x in (-0.9, 0.9):
        m.obox(V((x, LINE_Y, 0.33)), (0.035, 0.035, 0.66), "wood_dark")
        m.cyl(V((x, LINE_Y, 0.665)), 0.02, 0.012, "wood_dark", segs=5, r2=0.0)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- the water: its own (still) child object, so the QA can let the raccoon wade in it and nothing else
    m = B.M()
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, (FLOOR + WATER) / 2)), (x1 - x0 - t - 0.002, y1 - y0 - t - 0.002, WATER - FLOOR), "water")
    water = m.obj("pr_water", coll)
    water.parent = root
    m = B.M()                                             # the washing line: its own object, the cloths hang on it
    m.beam(V((-0.9, LINE_Y, 0.62)), V((0.9, LINE_Y, 0.62)), 0.01, "rope")
    line = m.obj("pr_washing_line", coll)
    line.parent = root
    parts = {}
    # cloths on the line: each hangs from its peg on the rope and stirs about the rope
    for i, (x, sw, w, h) in enumerate(((-0.55, "cloth_cream", 0.22, 0.24), (-0.12, "cloth_red", 0.18, 0.2),
                                       (0.3, "cloth_blue", 0.24, 0.26), (0.66, "cloth_mustard", 0.14, 0.16))):
        m = B.M()
        top = V((x, LINE_Y, 0.615))
        m.obox(top + V((0, 0, -h / 2)), (w, 0.012, h), sw)
        m.obox(top + V((0, 0, 0.004)), (0.012, 0.02, 0.025), "wood_light")                           # peg
        parts[f"pr_cloth_{i + 1}"] = A.part(m.obj(f"pr_cloth_{i + 1}", coll), root, top)
    # floating apple and carrot
    for nm, c, kind in (("pr_apple", V((0.25, -0.12, WATER)), "apple"), ("pr_carrot", V((0.12, 0.16, WATER)), "carrot")):
        m = B.M()
        if kind == "apple":
            m.blob(c + V((0, 0, 0.004)), V((0.02, 0.02, 0.018)), "cloth_red", 7, 4)
            m.cyl(c + V((0, 0, 0.024)), 0.003, 0.01, "wood_dark", segs=4)
        else:
            m.cyl(c + V((0, 0, 0.002)), 0.012, 0.07, "torch_orange", axis=(1, 0.3, 0), segs=6, r2=0.002)
            m.cyl(c + V((-0.04, -0.012, 0.004)), 0.008, 0.018, "moss", axis=(1, 0.3, 0.4), segs=4, r2=0.0)
        parts[nm] = A.part(m.obj(nm, coll), root, c)
    # ripple rings: two at the raccoon's paws, one round the apple
    for i, c in enumerate((PAWS, PAWS, V((0.25, -0.12, WATER)))):
        m = B.M()
        FS._ring(m, c + V((0, 0, 0.0035)), 0.06, 0.052, "stone_frost", 14)
        parts[f"pr_ripple_{i + 1}"] = A.part(m.obj(f"pr_ripple_{i + 1}", coll), root, c + V((0, 0, 0.0035)))
    return root, water, parts


def clips(parts):
    TAU = 2 * math.pi

    def common(p):
        pose = {}
        for i in range(1, 5):                                 # cloths stir about the rope, out of step
            pose[f"pr_cloth_{i}"] = (None, A.q((1, 0, 0), 5 * math.sin(TAU * (p + i * 0.23)) + 1.5), None)
        pose["pr_apple"] = (V((0.006 * math.sin(TAU * p), 0, 0.002 * math.sin(TAU * 2 * p))),
                            A.q((0, 0, 1), 20 * math.sin(TAU * p)), None)
        pose["pr_carrot"] = (V((0, 0.005 * math.sin(TAU * (p + 0.4)), 0.0015 * math.sin(TAU * 2 * (p + 0.2)))),
                             A.q((0, 0, 1), 10 * math.sin(TAU * (p + 0.3))), None)
        u = p                                                 # a slow ring round the apple
        pose["pr_ripple_3"] = (V((0.006 * math.sin(TAU * p), 0, 0)), None, (0.3 + 0.9 * u) if u < 0.95 else 0.001)
        return pose

    def idle(p):
        pose = common(p)
        pose["pr_ripple_1"] = A.hidden()
        pose["pr_ripple_2"] = A.hidden()
        return pose

    def work(p):
        pose = common(p)
        for i, ph in ((1, 0.0), (2, 0.5)):                    # a ring from the paws every half loop (each scrub)
            u = (p + ph) % 1.0 / 0.5
            pose[f"pr_ripple_{i}"] = (None, None, (0.35 + 1.4 * u) if u < 1 else 0.001)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, water, parts = build(coll, random.Random(12))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(water) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(water)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "washing_pool.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_scrub")
    allow = [(f"pr_cloth_{i}", "pr_washing_line") for i in (1, 2, 3, 4)] + \
            [("pr_apple", "pr_water"), ("pr_carrot", "pr_water"), ("pr_ripple_3", "pr_apple"),
             ("pr_ripple_1", "pr_ripple_2")] + [(f"pr_ripple_{i}", "pr_water") for i in (1, 2, 3)]
    probs = A.check(root, 2, 1, crew=[(rig, mesh, None, "work", {"pr_water": "wade", "pr_ripple_1": "wade",
                                                               "pr_ripple_2": "wade"})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_washing_pool_loops.gif",
                       target=(0.0, 0.06, 0.18), dist=3.3, pitch=40, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
