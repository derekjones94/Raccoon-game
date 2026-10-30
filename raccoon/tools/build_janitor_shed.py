"""bld_janitor_shed_2x1: the colony's cleaner's shed, and the patch of yard they keep spotless.

A little plank shed on the left with its door open: mops in a bucket, brooms on a rack, rags on a shelf, a pail.
Outside it, a broom leaning on the wall, a laundry line of rags, a trash sack. On the right a swept flagstone yard:
the janitor crouches there (spot_work, facing the front) sweeping dirt toward a dustpan with a hand brush
(work_sweep + prop_brush), the left paw on the pan's handle.

Clips (24 fps)
  idle  48 fr  the leaning broom slips, wobbles and settles back; the rags on the line stir
  work  48 fr  as idle, plus a little drift of dirt is pushed toward the pan on each brush stroke (two a loop) and
               tips in, a dust puff at the pan's lip; start it with the raccoon's work_sweep (both 48 frames)

Run:  python3 tools/build_janitor_shed.py   (--no-renders)
Out:  janitor_shed.blend, export/bld_janitor_shed_2x1.glb, renders/bld_janitor_shed_loops.gif, renders/qa_buildings.txt
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
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_janitor_shed_2x1"
FRAMES = 48
FLOOR = 0.008                                    # top of the flagstones
SPOT = V((0.3, 0.14, FLOOR + 0.0015))            # the janitor, crouched, facing the front (-Y)
PAN = SPOT + J.PAN                               # the dustpan's middle, on the floor
SWEEP = SPOT + J.SWEEP_C                         # the middle of the brush's stroke
SHED = (-0.94, -0.3, -0.12, 0.42)                # x0 x1 y0 y1 of the shed
SHED_H = (0.5, 0.38)                             # wall height at the front and the back (a single-slope roof)
BROOM_FOOT = V((-0.22, -0.02, 0.032))            # the leaning broom: its foot on the ground by the shed's right wall


def broom(m, foot, top, head_sw="rope"):
    d = (top - foot).normalized()
    m.beam(foot + d * 0.05, top, 0.012, "wood_light")
    m.cyl(foot + d * 0.03, 0.03, 0.07, head_sw, axis=tuple(d), segs=6, r2=0.012)
    m.cyl(foot + d * 0.066, 0.016, 0.014, "rope_dark", axis=tuple(d), segs=6)


def build(coll, rnd):
    m = B.M()
    # ---- ground: packed earth, the shed's sill
    m.obox(V((0, 0, 0.002)), (1.94, 0.94, 0.004), "wood_weathered")
    x0, x1, y0, y1 = SHED
    # ---- the shed: plank walls (the front has an open doorway), a single-slope plank roof
    fz, bz = SHED_H
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, 0.01)), (x1 - x0, y1 - y0, 0.02), "wood_dark", top="wood_mid")
    for k in range(7):                                                                        # back wall
        x = x0 + (x1 - x0) * (k + 0.5) / 7
        m.obox(V((x, y1 - 0.01, bz / 2)), ((x1 - x0) / 7 - 0.004, 0.018, bz), "wood_mid" if k % 2 else "wood_light")
    for x in (x0 + 0.01, x1 - 0.01):                                                          # side walls
        for k in range(5):
            y = y0 + (y1 - y0) * (k + 0.5) / 5
            h = fz + (bz - fz) * (y - y0) / (y1 - y0)
            m.obox(V((x, y, h / 2)), (0.018, (y1 - y0) / 5 - 0.004, h), "wood_light" if k % 2 else "wood_mid")
    door = (-0.72, -0.48)                                                                     # front wall, either side of the door
    for a, b in ((x0, door[0]), (door[1], x1)):
        n = max(1, round((b - a) / 0.09))
        for k in range(n):
            x = a + (b - a) * (k + 0.5) / n
            m.obox(V((x, y0 + 0.01, fz / 2)), ((b - a) / n - 0.004, 0.018, fz), "wood_mid" if k % 2 else "wood_light")
    m.obox(V(((door[0] + door[1]) / 2, y0 + 0.01, fz - 0.04)), (door[1] - door[0], 0.02, 0.08), "wood_dark")   # lintel
    for x in door:
        m.obox(V((x, y0 + 0.01, fz / 2)), (0.03, 0.03, fz), "wood_dark")
    ang = math.atan2(bz - fz, y1 - y0)
    for k in range(5):                                                                        # roof planks
        x = x0 - 0.02 + (x1 - x0 + 0.05) * (k + 0.5) / 5
        m.obox(V((x, (y0 + y1) / 2, (fz + bz) / 2 + 0.02)), ((x1 - x0 + 0.05) / 5 - 0.004, (y1 - y0) / math.cos(ang) + 0.08, 0.016),
               "wood_bark" if k % 2 else "wood_dark", rot=(ang, 0, 0))
    m.obox(V((x0 - 0.002, (y0 + y1) / 2, 0.3)), (0.004, 0.14, 0.09), "teal")                 # a sign: a broom on teal
    m.beam(V((x0 - 0.005, (y0 + y1) / 2 - 0.05, 0.27)), V((x0 - 0.005, (y0 + y1) / 2 + 0.04, 0.33)), 0.006, "cloth_cream")
    # the door leaf, swung open against the front wall
    for k in range(3):
        m.obox(V((door[1] + 0.02 + 0.075 * k + 0.035, y0 - 0.018, fz / 2 - 0.02)), (0.07, 0.014, fz - 0.06),
               "wood_light" if k % 2 else "wood_mid")
    m.obox(V((door[1] + 0.13, y0 - 0.028, fz * 0.3)), (0.22, 0.008, 0.02), "wood_dark")
    m.obox(V((door[1] + 0.13, y0 - 0.028, fz * 0.75)), (0.22, 0.008, 0.02), "wood_dark")
    # ---- inside: a mop bucket, brooms in a rack, a shelf of rags and soap
    bc = V((-0.6, 0.12, 0.02))
    m.cyl(bc + V((0, 0, 0.05)), 0.06, 0.1, "iron_light", segs=8, r2=0.052, cap="water")
    for a in (0.3, 2.5):
        top = bc + V((0.05 * math.cos(a), 0.05 * math.sin(a), 0.42))
        m.beam(bc + V((0, 0, 0.04)), top, 0.01, "wood_mid")
    m.blob(bc + V((0, 0, 0.1)), V((0.05, 0.05, 0.03)), "cloth_cream", 6, 3)
    m.obox(V((-0.82, 0.36, 0.3)), (0.14, 0.04, 0.02), "wood_dark")                           # broom rack
    for k in range(3):
        x = -0.87 + 0.05 * k
        broom(m, V((x, 0.33, 0.03)), V((x, 0.37, 0.36)), "rope" if k % 2 else "burlap")
    for z in (0.18, 0.3):                                                                     # shelf on the back wall
        m.obox(V((-0.45, 0.37, z)), (0.24, 0.07, 0.014), "wood_light")
    m.blob(V((-0.5, 0.37, 0.205)), V((0.04, 0.03, 0.02)), "cloth_blue", 6, 3)
    m.blob(V((-0.4, 0.37, 0.205)), V((0.04, 0.03, 0.02)), "cloth_red", 6, 3)
    m.obox(V((-0.46, 0.37, 0.32)), (0.04, 0.03, 0.025), "cloth_cream")                       # soap
    m.cyl(V((-0.38, 0.37, 0.33)), 0.018, 0.04, "pewter", segs=6, cap="iron")
    # ---- outside: a pail and a scrubbing brush, a trash sack, a rag line between the shed and a post
    m.cyl(V((-0.14, -0.3, 0.04)), 0.045, 0.07, "wood_mid", segs=8, r2=0.038, cap="water_deep")
    m.obox(V((-0.06, -0.33, 0.012)), (0.05, 0.03, 0.016), "wood_mid", top="burlap")
    B.sack(m, V((0.78, 0.3, 0.004)), 0.075, sw="soot")
    m.obox(V((0.86, -0.3, 0.2)), (0.03, 0.03, 0.4), "wood_dark")                              # line post
    m.beam(V((x1 + 0.005, y0 + 0.05, 0.42)), V((0.86, -0.3, 0.38)), 0.005, "rope")
    # ---- flagstones where the janitor works
    flags = []
    for i in range(4):
        for j in range(3):
            c = V((-0.05 + 0.2 * i + rnd.uniform(-0.003, 0.003), -0.32 + 0.24 * j + rnd.uniform(-0.003, 0.003), 0.0))
            flags.append((c, rnd.choice(["pewter", "fur_light", "fur_mid"])))                 # warm grey stone, not blue
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    # the yard's flagstones: their own still object (the brush and paws touch them)
    m = B.M()
    for k, (c, sw) in enumerate(flags):                                    # laid square, even joints, never touching
        h = FLOOR - 0.00012 * k                                                # (and no two tops at the same height)
        m.obox(c + V((0, 0, h / 2)), (0.18, 0.22, h), sw, rot=(0, 0, rnd.uniform(-0.012, 0.012)))
    floor = m.obj("pr_floor", coll)
    floor.parent = root
    parts = {}
    # the dustpan, its handle up to the left paw (still)
    m = B.M()
    grip = SPOT + J.PAN + J.loc(f=-0.03, u=0.06)
    pc = V((PAN.x, PAN.y - 0.025, FLOOR))                    # its lip faces the brush (-X), its back toward +X; its
                                                             # near side clears the crouched janitor's toes
    m.obox(pc + V((0, 0, 0.002)), (0.07, 0.09, 0.004), "iron_light")
    for dy in (-0.045, 0.045):
        m.obox(pc + V((0.005, dy, 0.01)), (0.06, 0.004, 0.016), "iron")
    m.obox(pc + V((0.035, 0, 0.012)), (0.004, 0.09, 0.02), "iron")
    m.beam(pc + V((0.035, 0, 0.02)), grip, 0.009, "wood_mid")
    m.blob(pc + V((0.012, 0, 0.004)), V((0.02, 0.03, 0.006)), "wood_weathered", 6, 3)       # dirt already in it
    pan = m.obj("pr_pan", coll)
    pan.parent = root
    # the leaning broom (slips and settles back)
    m = B.M()
    top = V((BROOM_FOOT.x - 0.06, 0.16, 0.42))
    broom(m, BROOM_FOOT, top, "burlap")
    parts["pr_broom"] = A.part(m.obj("pr_broom", coll), root, BROOM_FOOT)
    # rags on the line
    line_a, line_b = V((x1 + 0.005, y0 + 0.05, 0.42)), V((0.86, -0.3, 0.38))
    for i, (t, sw) in enumerate(((0.3, "cloth_blue"), (0.55, "cloth_cream"), (0.8, "cloth_red"))):
        m = B.M()
        c = line_a.lerp(line_b, t) - V((0, 0, 0.004))
        m.obox(c + V((0, 0, -0.04)), (0.07, 0.006, 0.08), sw, rot=(0, 0, math.atan2(line_b.y - line_a.y, line_b.x - line_a.x)))
        parts[f"pr_rag_{i + 1}"] = A.part(m.obj(f"pr_rag_{i + 1}", coll), root, c)
    # the drift of dirt the brush pushes, and a dust puff at the pan's lip
    m = B.M()
    for k, (dl, df) in enumerate(((0.0, 0.0), (0.012, 0.01), (-0.01, -0.008), (0.006, -0.012))):
        m.blob(V((0, 0, 0)) + J.loc(f=df, l=dl) + V((0, 0, FLOOR + 0.004)), V((0.008, 0.008, 0.005)),
               "wood_weathered" if k % 2 else "wood_dark", 4, 3)
    dirt0 = V((SWEEP.x - 0.005, SWEEP.y + 0.02, 0.0))          # just ahead of the brush at the stroke's start
    ob = m.obj("pr_dirt", coll)
    ob.data.transform(__import__("mathutils").Matrix.Translation(dirt0))
    parts["pr_dirt"] = A.part(ob, root, dirt0 + V((0, 0, FLOOR)))
    m = B.M()
    pc = V((PAN.x - 0.03, PAN.y - 0.025, FLOOR + 0.02))        # over the pan's lip
    m.blob(pc, V((0.018, 0.014, 0.014)), "stone_pale", 6, 3)
    m.blob(pc + V((0.014, 0.004, 0.008)), V((0.012, 0.01, 0.01)), "stone_light", 5, 3)
    parts["pr_puff"] = A.part(m.obj("pr_puff", coll), root, pc)
    return root, floor, pan, parts


def clips(parts):
    def common(p):
        pose = {}
        for i in (1, 2, 3):
            pose[f"pr_rag_{i}"] = (None, A.q((1, 0.2, 0), 10 * math.sin(TAU * (p + 0.15 * i)) + 4 * math.sin(TAU * (3 * p + i))), None)
        # the broom: leaning on the wall; it slips a little (its foot slides out), wobbles, is nudged back
        slip = math.exp(-((p - 0.35) ** 2) / 0.004)
        settle = math.exp(-((p - 0.45) ** 2) / 0.01) * math.sin(TAU * 6 * (p - 0.35))
        pose["pr_broom"] = (V((0.012 * slip, 0.0, 0.0)), A.q((0, 1, 0), 3 * slip + 2.5 * settle), None)
        return pose

    def idle(p):
        pose = common(p)
        pose["pr_dirt"] = A.hidden()
        pose["pr_puff"] = A.hidden()
        return pose

    def work(p):
        pose = common(p)
        u = (2 * p) % 1.0
        k = J.smooth(u / 0.55) if u < 0.55 else 1.0
        # the drift rides ahead of the brush across the stroke, tips into the pan at the stroke's end, and a new
        # drift shows (grows) as the brush lifts back for the next stroke
        if u < 0.55:
            s, off = 1.0, 0.065 * k
        elif u < 0.65:
            s, off = 1 - (u - 0.55) / 0.1, 0.065 + 0.03 * (u - 0.55) / 0.1
        else:
            s, off = max(0.001, (u - 0.65) / 0.35), 0.0
        pose["pr_dirt"] = (J.loc(l=off), None, max(0.001, s))
        puff = math.exp(-((u - 0.6) ** 2) / 0.004)
        pose["pr_puff"] = (V((0, 0, 0.02 * (u - 0.5) if u > 0.5 else 0)), None, max(0.001, 1.6 * puff))
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, floor, pan, parts = build(coll, random.Random(31))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(floor) + K.tris(pan) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(floor) + K.tris(pan)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "janitor_shed.blend"), relative_remap=True)
    A.export()
    rig, mesh, brush = A.raccoon_at(bpy.data.objects["spot_work"], clip="work_sweep", tool="prop_brush")
    allow = [("pr_floor", NAME), ("pr_pan", "pr_floor"), ("pr_pan", NAME), ("pr_broom", NAME), ("pr_dirt", "pr_floor"),
             ("pr_dirt", "pr_pan"), ("pr_puff", "pr_pan"), ("pr_puff", "pr_floor"),
             ("pr_puff", "pr_dirt")] + [(f"pr_rag_{i}", NAME) for i in (1, 2, 3)]
    probs = A.check(root, 2, 1, crew=[(rig, mesh, brush, "work", {"pr_floor": None, "pr_pan": None, "pr_dirt": None,
                                                                 "pr_puff": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, brush], ROOT / "renders" / "bld_janitor_shed_loops.gif",
                       target=(-0.05, 0.0, 0.12), dist=3.4, pitch=42, idle_frames=48, grid_n=4)


if __name__ == "__main__":
    main()
