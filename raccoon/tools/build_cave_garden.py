"""bld_cave_garden_2x2: a damp cave nook where raccoons grow glowing mushrooms (Tending).

A dark stone floor under a ring of mossy boulders (the cave's back wall and left side). A low bed of black soil full
of glowing mushrooms in the middle; the raccoon crouches behind it (spot_work, facing the front) and pats the soil
round the young mushroom in front of it (work_tend). A fallen log with shelf mushrooms, a drip from a ledge into a
little pool, a basket of picked caps and a glow-crystal lantern.

Clips (24 fps)
  idle  48 fr  the glowing caps swell and fade in turn, spores drift up, water drips from the ledge into the pool
  work  48 fr  as idle, plus the young mushroom by the paws wobbles on every pat and lets off a puff of spores

The young mushroom wobbles on the beats of work_tend's pats (build_raccoon_jobs.tend_pats), so start the building's
work and the raccoon's work_tend together (both 48 frames).

Run:  python3 tools/build_cave_garden.py   (--no-renders)
Out:  cave_garden.blend, export/bld_cave_garden_2x2.glb, renders/bld_cave_garden_loops.gif, renders/qa_buildings.txt
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
TAU = 2 * math.pi
NAME = "bld_cave_garden_2x2"
FRAMES = 48
FLOOR = 0.008
SPOT = V((0.04, 0.2, FLOOR + 0.0015))           # behind the bed, facing the front (-Y)
TENDED = SPOT + J.TEND_C                         # the young mushroom between the paws (raccoon space == building space)
BED = (-0.42, 0.42, TENDED.y - 0.26, SPOT.y - 0.108)   # raised planter, x0 x1 y0 y1: its back board just clears
BED_H = 0.04                                             # the crouching raccoon's toes; soil top, over the floor
DRIP = V((0.6, 0.72, 0.34))                      # the ledge's drip point; the pool is right under it
POOL_Z = FLOOR + 0.004


def bed_z(x, y):
    """Height of the planter's soil at (x, y)."""
    return FLOOR + BED_H


def mushroom(m, base, h, r, cap="mushroom_glow", stem="bone", tilt=(0, 0, 1), segs=7):
    d = V(tilt).normalized()
    m.cyl(base + d * (h / 2), r * 0.32, h, stem, axis=tuple(d), segs=4 if segs < 7 else 5)
    m.cyl(base + d * (h + r * 0.18), r, r * 0.45, cap, axis=tuple(d), segs=segs, r2=r * 0.35)


def build(coll, rnd):
    m = B.M()
    # ---- floor: dark stone, a few loose pebbles
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "stone_deep")
    for c, caps in ((V((0.28, -0.58, FLOOR)), ("fur_tan", "cloth_red", "fur_tan", "cloth_red")),     # wild clumps
                    (V((-0.6, 0.02, FLOOR)), ("mushroom_glow",) * 3)):
        for k, cap in enumerate(caps):
            a = k * 2.3 + 0.5
            mushroom(m, c + V((0.04 * math.cos(a) * min(k, 1), 0.035 * math.sin(a) * min(k, 1), 0)),
                     0.05 - 0.008 * k, 0.026 - 0.003 * k, cap=cap, segs=5)
    # ---- the cave: rounded boulders along the back and the left side, a few stalagmites, moss on top
    rocks = [(-0.78, 0.8, 0.17, 0.42), (-0.5, 0.82, 0.16, 0.36), (-0.22, 0.8, 0.18, 0.44), (0.08, 0.82, 0.15, 0.3),
             (0.33, 0.8, 0.16, 0.38), (0.6, 0.82, 0.15, 0.4), (0.82, 0.8, 0.12, 0.26),
             (-0.82, 0.48, 0.13, 0.32), (-0.84, 0.18, 0.12, 0.24), (-0.85, -0.12, 0.11, 0.17), (-0.86, -0.4, 0.1, 0.11)]
    for k, (x, y, r, h) in enumerate(rocks):
        m.blob(V((x, y, 0.4 * h)), V((r, r * 0.75 if k < 7 else r * 1.3, 0.6 * h)),
               rnd.choice(["stone_dark", "stone_mid", "stone_dark"]), 7, 4)
        if h > 0.25 and k != 5:
            m.blob(V((x + rnd.uniform(-0.04, 0.04), y - 0.03, 0.97 * h)), V((r * 0.5, r * 0.35, 0.02)), "moss", 5, 3)
    for c, h in ((V((-0.6, 0.58, 0)), 0.2), (V((-0.68, 0.36, 0)), 0.13), (V((0.4, 0.64, 0)), 0.15)):
        m.cyl(c + V((0, 0, h / 2)), 0.04, h, "stone_mid", segs=6, r2=0.008)              # stalagmites
    # the ledge the water drips from (a flat rock jutting from the boulder behind), and its pool
    m.blob(DRIP + V((0, 0.07, 0.022)), V((0.07, 0.1, 0.024)), "stone_mid", 7, 3)
    m.cyl(V((DRIP.x, DRIP.y - 0.02, FLOOR + 0.002)), 0.15, 0.004, "stone_dark", segs=10)          # pool rim
    m.cyl(V((DRIP.x, DRIP.y - 0.02, POOL_Z)), 0.12, 0.004, "water_deep", segs=10)
    # ---- the soil bed and its mushrooms (the one by the paws is a part)
    # a fallen log with shelf mushrooms (front left), a basket of picked caps and a crystal lantern (right)
    lc = V((-0.52, -0.6, 0.05))
    B.log(m, lc, 0.05, 0.5, axis=(1, 0.35, 0))
    for k, t in enumerate((-0.15, 0.0, 0.14)):
        p = lc + V((1, 0.35, 0)).normalized() * t + V((0, -0.05, 0.01 + 0.012 * k))
        m.cyl(p, 0.032, 0.008, "fur_tan" if k % 2 else "cloth_red", segs=7)
    bk = V((0.64, -0.5, 0))
    m.cyl(bk + V((0, 0, 0.04)), 0.07, 0.08, "rope", segs=8, r2=0.08, cap="rope_dark")
    for k in range(4):
        a = k * 1.6
        m.cyl(bk + V((0.035 * math.cos(a), 0.035 * math.sin(a), 0.088)), 0.024, 0.012, "mushroom_glow", segs=6,
              axis=(math.cos(a) * 0.4, math.sin(a) * 0.4, 1))
    ln = V((0.78, 0.18, 0))
    m.obox(ln + V((0, 0, 0.06)), (0.06, 0.06, 0.12), "iron_dark")
    m.obox(ln + V((0, 0, 0.17)), (0.045, 0.045, 0.1), "teal_light")
    m.cyl(ln + V((0, 0, 0.23)), 0.04, 0.03, "iron_dark", segs=4, r2=0.0)
    m.beam(V((0.5, -0.2, FLOOR + 0.006)), V((0.62, -0.26, FLOOR + 0.006)), 0.01, "wood_light")    # trowel
    m.obox(V((0.47, -0.185, FLOOR + 0.004)), (0.05, 0.03, 0.006), "iron_light", rot=(0, 0, -0.45))
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # the bed (a still child object: the paws may press into it)
    m = B.M()
    x0, x1, y0, y1 = BED
    t = 0.016
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, FLOOR + (BED_H - 0.002) / 2)), (x1 - x0 - 0.01, y1 - y0 - 0.01, BED_H - 0.002),
           "wood_bark")                                                   # the soil
    for (a, b, horiz) in (((x0, y0), (x1, y0), True), ((x0, y1), (x1, y1), True), ((x0, y0), (x0, y1), False),
                          ((x1, y0), (x1, y1), False)):                   # plank sides, a touch below the soil
        c = V(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, FLOOR + (BED_H - 0.006) / 2))
        size = ((x1 - x0 + t), t, BED_H - 0.006) if horiz else (t, (y1 - y0 + t), BED_H - 0.006)
        m.obox(c, size, "wood_dark")
    for k in range(12):                                                   # glowing mushrooms, away from the paws
        x = rnd.uniform(x0 + 0.05, x1 - 0.05)
        y = rnd.uniform(y0 + 0.04, y1 - 0.04)
        if abs(x - TENDED.x) < 0.14 and y > TENDED.y - 0.08:
            continue
        mushroom(m, V((x, y, bed_z(x, y) - 0.004)), rnd.uniform(0.025, 0.045), rnd.uniform(0.014, 0.022),
                 tilt=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 1))
    bed = m.obj("pr_bed", coll)
    PR.trim_below_floor(bed)
    bed.parent = root
    parts = {}
    # glowing caps that pulse (big ones on the bed, two on the rocks)
    yc = (BED[2] + BED[3]) / 2
    glows = [V((-0.3, yc - 0.01, 0)), V((0.3, yc + 0.03, 0)), V((-0.08, BED[2] + 0.06, 0)),
             V((-0.72, 0.5, 0)), V((0.2, 0.72, 0))]
    for i, g in enumerate(glows):
        z = bed_z(g.x, g.y) - 0.004 if i < 3 else (0.0 if i == 4 else 0.0)
        m = B.M()
        base = V((g.x, g.y, max(z, FLOOR)))
        mushroom(m, base, 0.06 if i < 3 else 0.05, 0.034 if i < 3 else 0.028)
        parts[f"pr_glow_{i + 1}"] = A.part(m.obj(f"pr_glow_{i + 1}", coll), root, base)
    # the young mushroom the raccoon tends, and its puff of spores
    m = B.M()
    tb = V((TENDED.x, TENDED.y, bed_z(TENDED.x, TENDED.y) - 0.003))
    mushroom(m, tb, 0.022, 0.014)
    parts["pr_tended"] = A.part(m.obj("pr_tended", coll), root, tb)
    for i in range(3):
        m = B.M()
        c = tb + V((0.006 * (i - 1), 0.0, 0.04))
        m.obox(c, (0.006, 0.006, 0.006), "mushroom_glow", rot=(0.6, 0.4 * i, 0.3))
        parts[f"pr_puff_{i + 1}"] = A.part(m.obj(f"pr_puff_{i + 1}", coll), root, c)
    # drifting spores over the bed
    for i in range(4):
        m = B.M()
        c = V((-0.36 + 0.24 * i, yc - 0.06 + 0.09 * (i % 2), 0.15))
        m.obox(c, (0.007, 0.007, 0.007), "mushroom_glow", rot=(0.5, 0.5, 0))
        parts[f"pr_spore_{i + 1}"] = A.part(m.obj(f"pr_spore_{i + 1}", coll), root, c)
    # the drip and its ring
    m = B.M()
    m.blob(DRIP, V((0.006, 0.006, 0.009)), "water", 5, 3)
    parts["pr_drip"] = A.part(m.obj("pr_drip", coll), root, DRIP)
    m = B.M()
    rc = V((DRIP.x, DRIP.y, POOL_Z + 0.0025))
    FS._ring(m, rc, 0.03, 0.022, "stone_frost", 12)
    parts["pr_drip_ring"] = A.part(m.obj("pr_drip_ring", coll), root, rc)
    return root, bed, parts


def clips(parts):
    pats = J.tend_pats()

    def common(p):
        pose = {}
        for i in range(1, 6):                                              # caps swell and fade in turn
            g = 0.5 + 0.5 * math.sin(TAU * (p - 0.2 * i))
            pose[f"pr_glow_{i}"] = (None, None, (1 + 0.1 * g, 1 + 0.1 * g, 1 + 0.06 * g))
        for i in range(1, 5):                                              # spores rise and vanish
            u = (p + 0.25 * i) % 1.0
            s = math.sin(math.pi * u)
            pose[f"pr_spore_{i}"] = (V((0.02 * math.sin(TAU * (u + i * 0.3)), 0.01 * math.cos(TAU * u), 0.16 * u)),
                                     A.q((0, 0, 1), 360 * u), max(s, 0.001))
        u = p * 2 % 1.0                                                    # a drip every 24 frames
        if u < 0.4:
            pose["pr_drip"] = (None, None, 0.3 + 1.7 * u)                  # gathering on the ledge
        elif u < 0.6:
            fall = ((u - 0.4) / 0.2) ** 2
            pose["pr_drip"] = (V((0, 0, -(DRIP.z - POOL_Z - 0.006) * fall)), None, (1, 1, 1.3))
        else:
            pose["pr_drip"] = A.hidden()
        ring = (u - 0.6) / 0.4
        pose["pr_drip_ring"] = (None, None, 0.3 + 1.6 * ring) if u >= 0.6 else A.hidden()
        return pose

    def idle(p):
        pose = common(p)
        for i in (1, 2, 3):
            pose[f"pr_puff_{i}"] = A.hidden()
        return pose

    def work(p):
        pose = common(p)
        hit = 0.0
        since = 1.0
        for c in pats:                                                     # the latest pat and how long ago
            d = (p - c) % 1.0
            if d < since:
                since = d
        hit = math.exp(-since / 0.04)
        pose["pr_tended"] = (None, A.q((1, 0.4, 0), 10 * hit * math.sin(TAU * since * 12)), (1, 1, 1 - 0.12 * hit))
        for i in (1, 2, 3):                                                # spores puff up off it after each pat
            u = since / 0.2
            if u < 1:
                pose[f"pr_puff_{i}"] = (V((0.012 * (i - 2) * u, 0.006 * u, 0.05 * u)), None, max(1 - u, 0.001))
            else:
                pose[f"pr_puff_{i}"] = A.hidden()
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, bed, parts = build(coll, random.Random(31))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(bed) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(bed)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "cave_garden.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_tend")
    allow = [(f"pr_glow_{i}", n) for i in range(1, 6) for n in (NAME, "pr_bed")] + \
            [("pr_tended", "pr_bed"), ("pr_drip_ring", NAME), ("pr_drip", NAME)] + \
            [(f"pr_puff_{i}", f"pr_puff_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j] + \
            [(f"pr_puff_{i}", "pr_tended") for i in (1, 2, 3)]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, None, "work", {"pr_bed": None, "pr_tended": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_cave_garden_loops.gif",
                       target=(0.0, 0.05, 0.12), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
