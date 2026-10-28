"""bld_guard_post_2x2: the colony's lookout, a raised watch platform where a guard keeps an eye on the woods.

A plank platform on four log posts, railed on three sides, with a ladder up the back. The guard stands at its front
rail (spot_work, raised, facing the front) with a spear (work_guard + prop_spear) and scans the woods. A teal flag on
a tall pole at the back corner, a lantern hanging from a bracket at the front corner. Round the foot of the tower:
a palisade of sharpened stakes, a rack of spare spears, a fire basket, a pile of sling stones, a barrel and sacks.

Clips (24 fps)
  idle  96 fr  the flag waves, the lantern sways on its hook, the fire flickers (nobody on watch)
  work  96 fr  a guard on watch: the flag snaps harder, the lantern turns slowly on its hook to light the woods

work_guard is 96 frames too, so the guard's scan and the lantern's turn line up if they start together.

Run:  python3 tools/build_guard_post.py   (--no-renders)
Out:  guard_post.blend, export/bld_guard_post_2x2.glb, renders/bld_guard_post_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_guard_post_2x2"
FRAMES = 96
FLOOR = 0.006
PLAT = 0.34                                      # top of the watch platform's planks
DECK = (-0.24, 0.44, -0.26, 0.34)                # x0 x1 y0 y1
SPOT = V((0.1, -0.06, PLAT + 0.0015))            # the guard, at the front rail, facing the front (-Y)
RAIL_H = 0.13                                    # the rail's top above the planks (below the guard's chest)
POLE = V((-0.2, 0.3, PLAT))                      # the flag pole's foot (back-left corner of the platform)
FLAG_Z = 0.95
HOOK = V((0.53, -0.22, PLAT + 0.26))             # the lantern's hook, on a bracket off the front-right post


def stake(m, x, y, h, lean, sw="wood_bark"):
    a = V((x, y, 0.0))
    b = V((x + lean[0], y + lean[1], h))
    m.cyl((a + b) / 2, 0.022, h, sw, segs=6, axis=tuple(b - a))
    m.cyl(b + (b - a).normalized() * 0.02, 0.022, 0.04, "wood_cut", segs=6, r2=0.0, axis=tuple(b - a))   # sharpened tip


def spear(m, foot, top, sw_shaft="wood_mid"):
    m.beam(foot, top, 0.012, sw_shaft)
    d = (top - foot).normalized()
    m.cyl(top + d * 0.03, 0.014, 0.06, "iron_light", segs=4, r2=0.0, axis=tuple(d))


def build(coll, rnd):
    m = B.M()
    # ---- ground: trodden earth in grass, flagstones to the ladder
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "moss")
    m.blob(V((0.1, 0.05, FLOOR - 0.02)), V((0.62, 0.55, 0.024)), "wood_weathered", 12, 3)
    for k, (x, y) in enumerate(((0.12, 0.55), (0.02, 0.7), (0.14, 0.84))):
        m.cyl(V((x, y, FLOOR + 0.004)), 0.06 + 0.01 * (k % 2), 0.008, "stone_mid", segs=7, cap="stone_light")
    # ---- the tower: four log posts, cross braces, the plank platform
    x0, x1, y0, y1 = DECK
    for x in (x0 + 0.03, x1 - 0.03):
        for y in (y0 + 0.03, y1 - 0.03):
            m.cyl(V((x, y, (PLAT + RAIL_H + 0.03) / 2)), 0.026, PLAT + RAIL_H + 0.03, "wood_bark", segs=7, cap="wood_cut")
    for x in (x0 + 0.03, x1 - 0.03):                                                      # X braces on the sides
        m.beam(V((x, y0 + 0.05, 0.03)), V((x, y1 - 0.05, PLAT - 0.06)), 0.014, "wood_dark")
        m.beam(V((x, y1 - 0.05, 0.03)), V((x, y0 + 0.05, PLAT - 0.06)), 0.014, "wood_dark")
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, PLAT - 0.035)), (x1 - x0 - 0.02, y1 - y0 - 0.02, 0.02), "wood_dark")  # joists
    n = 8
    for k in range(n):                                                                    # planks along X
        y = y0 + (y1 - y0) * (k + 0.5) / n
        m.obox(V(((x0 + x1) / 2 + rnd.uniform(-0.01, 0.01), y, PLAT - 0.012)), (x1 - x0 + 0.02, (y1 - y0) / n - 0.006, 0.024),
               "wood_light" if k % 2 else "wood_mid")
    # ---- rails: front and both sides; the back is open over the ladder
    rz = PLAT + RAIL_H
    for a, b in (((x0 + 0.03, y0 + 0.03), (x1 - 0.03, y0 + 0.03)), ((x0 + 0.03, y0 + 0.03), (x0 + 0.03, y1 - 0.03)),
                 ((x1 - 0.03, y0 + 0.03), (x1 - 0.03, y1 - 0.03))):
        m.beam(V((a[0], a[1], rz)), V((b[0], b[1], rz)), 0.02, "wood_mid")
        m.beam(V((a[0], a[1], PLAT + 0.055)), V((b[0], b[1], PLAT + 0.055)), 0.014, "wood_dark")
    for x in (-0.12, 0.32):                                                               # front balusters
        m.obox(V((x, y0 + 0.03, PLAT + RAIL_H / 2)), (0.018, 0.018, RAIL_H), "wood_dark")
    m.obox(V((0.1, y0 + 0.022, PLAT + 0.09)), (0.16, 0.006, 0.05), "teal_dark")             # a little teal plaque
    m.obox(V((0.1, y0 + 0.018, PLAT + 0.09)), (0.04, 0.004, 0.03), "gold")                 # with a gold paw badge
    # ---- the ladder up the back
    lx = 0.1
    for dx in (-0.07, 0.07):
        m.beam(V((lx + dx, y1 + 0.2, 0.0)), V((lx + dx, y1 - 0.015, PLAT + 0.05)), 0.016, "wood_mid")
    for k in range(5):
        t = (k + 0.7) / 6
        y = y1 + 0.2 + (y1 - 0.015 - y1 - 0.2) * t
        m.beam(V((lx - 0.07, y, PLAT * t)), V((lx + 0.07, y, PLAT * t)), 0.011, "wood_light")
    # ---- the flag pole and the lantern bracket
    m.cyl(V((POLE.x, POLE.y, (PLAT + FLAG_Z) / 2)), 0.012, FLAG_Z - PLAT + 0.02, "wood_dark", segs=6)
    m.cyl(V((POLE.x, POLE.y, FLAG_Z + 0.02)), 0.018, 0.02, "gold", segs=6)
    m.beam(V((x1 - 0.03, y0 + 0.03, HOOK.z + 0.03)), V((HOOK.x, HOOK.y, HOOK.z + 0.03)), 0.014, "wood_dark")
    m.cyl(V((x1 - 0.03, y0 + 0.03, (rz + HOOK.z + 0.06) / 2)), 0.018, HOOK.z + 0.06 - rz, "wood_bark", segs=6)
    # ---- on the platform: a horn on a peg, a water skin, a stool at the side
    m.cyl(V((x0 + 0.07, 0.14, PLAT + 0.02)), 0.025, 0.04, "leather", segs=6, cap="leather_dark")
    m.cyl(V((x1 - 0.09, 0.2, PLAT + 0.035)), 0.04, 0.07, "wood_mid", segs=7, cap="wood_light")
    m.cyl(V((x1 - 0.03 - 0.03, y0 + 0.03, rz - 0.03)), 0.014, 0.07, "bone", axis=(1, 0, 0.6), segs=5, r2=0.006)  # horn
    # ---- the foot of the tower: palisade, spear rack, fire basket, sling stones, barrel, sacks
    for k in range(9):
        x = -0.92 + k * 0.105
        if -0.05 < x < 0.15:
            continue
        stake(m, x, -0.86 + 0.02 * (k % 2), 0.2 + 0.04 * ((k * 7) % 3), (0, -0.04))
    for k in range(3):
        stake(m, 0.62 + k * 0.1, -0.86 + 0.02 * (k % 2), 0.22 + 0.03 * k, (0, -0.04))
    m.beam(V((-0.94, -0.84, 0.1)), V((-0.08, -0.84, 0.1)), 0.012, "rope_dark")
    rx, ry = -0.62, 0.15                                                                  # spear rack
    for dy in (-0.14, 0.14):
        m.obox(V((rx, ry + dy, 0.13)), (0.03, 0.03, 0.26), "wood_dark")
    m.beam(V((rx, ry - 0.16, 0.22)), V((rx, ry + 0.16, 0.22)), 0.016, "wood_mid")
    m.beam(V((rx, ry - 0.16, 0.06)), V((rx, ry + 0.16, 0.06)), 0.016, "wood_mid")
    for k, dy in enumerate((-0.08, 0.0, 0.08)):
        spear(m, V((rx + 0.03, ry + dy, 0.0)), V((rx - 0.03, ry + dy + 0.01, 0.42 + 0.02 * k)))
    fb = V((-0.5, -0.45, 0.0))                                                            # fire basket on legs
    for a in range(3):
        an = TAU * a / 3
        m.beam(fb + V((0.07 * math.cos(an), 0.07 * math.sin(an), 0.0)), fb + V((0.04 * math.cos(an), 0.04 * math.sin(an), 0.14)),
               0.01, "iron_dark")
    m.cyl(fb + V((0, 0, 0.16)), 0.065, 0.05, "iron", segs=8, r2=0.05, cap="soot")
    m.blob(fb + V((0, 0, 0.18)), V((0.045, 0.045, 0.015)), "wood_dark", 6, 3)
    sp = V((0.6, -0.5, 0.0))                                                              # sling stones
    for k in range(9):
        a = TAU * k / 6
        r = 0.05 if k < 6 else 0.015
        m.blob(sp + V((r * math.cos(a), r * math.sin(a), 0.02 + (0.025 if k >= 6 else 0.0))), V((0.025, 0.025, 0.02)),
               "stone_light" if k % 2 else "stone_mid", 5, 3)
    m.cyl(V((0.72, 0.5, 0.1)), 0.08, 0.2, "wood_mid", cap="wood_dark", segs=8)          # barrel
    for z in (0.04, 0.16):
        m.cyl(V((0.72, 0.5, z)), 0.084, 0.012, "iron_dark", segs=8)
    for k, (x, y) in enumerate(((0.58, 0.68), (0.74, 0.72), (0.66, 0.78))):           # sacks
        m.blob(V((x, y, 0.05 + 0.03 * (k == 2))), V((0.06, 0.05, 0.055)), "burlap", 7, 4)
    m.cyl(V((-0.55, 0.62, 0.02)), 0.07, 0.035, "rope", segs=8, cap="rope_dark")           # coil of rope
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # flag: two strips that wave in a chain off the pole
    for i, (x0f, x1f, sw) in enumerate(((0.0, 0.13, "teal"), (0.13, 0.24, "teal_light"))):
        mm = B.M()
        piv = V((POLE.x + x0f, POLE.y, FLAG_Z - 0.06))
        mm.obox(V((POLE.x + (x0f + x1f) / 2, POLE.y, FLAG_Z - 0.06)), (x1f - x0f - 0.004, 0.006, 0.1 - 0.02 * i), sw)
        if i == 0:
            mm.obox(V((POLE.x + 0.06, POLE.y - 0.0035, FLAG_Z - 0.06)), (0.04, 0.002, 0.04), "gold")       # paw badge
        parts[f"pr_flag_{i + 1}"] = A.part(mm.obj(f"pr_flag_{i + 1}", coll), root, piv)
    # lantern on its hook
    mm = B.M()
    c = HOOK + V((0, 0, -0.07))
    mm.beam(HOOK, c + V((0, 0, 0.035)), 0.004, "iron_dark")
    mm.cyl(c, 0.03, 0.06, "iron_dark", segs=6, cap="iron")
    mm.cyl(c + V((0, -0.012, 0)), 0.024, 0.045, "flame_yellow", segs=6)                 # the lit glass (front half)
    mm.cyl(c + V((0, 0, 0.04)), 0.032, 0.02, "iron", segs=6, r2=0.01)
    parts["pr_lantern"] = A.part(mm.obj("pr_lantern", coll), root, HOOK)
    # fire in the basket
    mm = B.M()
    fc = fb + V((0, 0, 0.19))
    for k, (dx, h, sw) in enumerate(((0.0, 0.11, "torch_orange"), (0.025, 0.07, "flame_yellow"), (-0.025, 0.075, "flame_yellow"))):
        mm.cyl(fc + V((dx, 0.01 * k, h / 2)), 0.03 - 0.006 * k, h, sw, segs=5, r2=0.0)
    parts["pr_fire"] = A.part(mm.obj("pr_fire", coll), root, fc)
    return root, parts


def clips(parts):
    def common(p, wind):
        a1 = (14 + 10 * wind) * math.sin(TAU * 2 * p) + 6 * wind * math.sin(TAU * 6 * p)
        a2 = (22 + 14 * wind) * math.sin(TAU * (2 * p - 0.18)) + 8 * wind * math.sin(TAU * (6 * p - 0.3))
        r1 = A.q((0, 0, 1), a1)
        rel = V((0.13, 0.0, 0.0))
        off2 = (r1 @ rel) - rel                                                          # strip 2 rides strip 1's edge
        pose = {"pr_flag_1": (None, r1, None), "pr_flag_2": (off2, A.q((0, 0, 1), a1 + a2), None)}
        fl = math.sin(TAU * 8 * p) + 0.5 * math.sin(TAU * 13 * p + 1)
        pose["pr_fire"] = (None, A.q((0, 0, 1), 20 * fl), (1, 1, 1 + 0.15 * math.sin(TAU * 11 * p)))
        return pose

    def idle(p):
        pose = common(p, 0.0)
        pose["pr_lantern"] = (None, A.q((1, 0, 0), 5 * math.sin(TAU * 2 * p)), None)
        return pose

    def work(p):
        pose = common(p, 1.0)
        turn = A.q((0, 0, 1), 60 * math.sin(TAU * p))                                   # sweeps the woods with the guard
        pose["pr_lantern"] = (None, A.q((1, 0, 0), 4 * math.sin(TAU * 4 * p)) @ turn, None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(55))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "guard_post.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, spear_ob = A.raccoon_at(sp, clip="work_guard", tool="prop_spear")
    allow = [("pr_flag_1", NAME), ("pr_flag_2", NAME), ("pr_flag_1", "pr_flag_2"), ("pr_lantern", NAME), ("pr_fire", NAME)]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, spear_ob, "work", {})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, spear_ob], ROOT / "renders" / "bld_guard_post_loops.gif",
                       target=(0.0, 0.0, 0.3), dist=3.9, pitch=40, idle_frames=48, grid_n=4, step=3)


if __name__ == "__main__":
    main()
