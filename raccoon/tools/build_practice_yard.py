"""bld_practice_yard_3x2: where young thieves practise picking locks and lifting purses.

A sanded yard with a low fence. On the left a lock board: a plank wall on posts with practice padlocks on hasps; a
raccoon picks one (spot_pick: work_picklock + prop_lockpick, side-on to the camera). On the right a straw dummy in a
coat with a purse on its belt; a raccoon lifts the purse off and hangs it back (spot_lift: work_lift). Round about:
straw bales, a rack of picks, a basket of practice purses, a chalk board of scores, bunting.

Clips (24 fps)
  idle  48 fr  the bunting and the dummy's coat-tail stir, the hanging locks rock a little
  work  48 fr  the padlock being picked springs open (build_raccoon_jobs.LOCK_POP) and is snapped shut; the purse
               follows the thief's paw (build_raccoon_jobs.lift_purse). Start both raccoons' clips with work.

Run:  python3 tools/build_practice_yard.py   (--no-renders)
Out:  practice_yard.blend, export/bld_practice_yard_3x2.glb, renders/bld_practice_yard_loops.gif
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_practice_yard_3x2"
FRAMES = 48
FLOOR = 0.006
PICK_SPOT = V((-0.62, -0.1, FLOOR + 0.0015))     # facing -X: the lock board is to its front
PICK_FACE = V((-1, 0, 0))
LIFT_SPOT = V((0.42, -0.1, FLOOR + 0.0015))      # facing +X: the dummy in front of it
LIFT_FACE = V((1, 0, 0))


def frame_of(face):
    """Spot frame: (forward, left, up) in the building, for a spot facing `face`."""
    f = face.normalized()
    up = V((0, 0, 1))
    return f, up.cross(f), up


def to_world(spot, face, v):
    """A point in a raccoon's own space (build_raccoon_jobs.loc: x = left, y = back, z = up) to the building."""
    f, l, u = frame_of(face)
    return spot + f * (-v.y) + l * v.x + u * v.z


def build(coll, rnd):
    m = B.M()
    # ---- the yard: sand, a low fence round the back and sides, bunting on poles
    m.obox(V((0, 0, FLOOR / 2)), (2.94, 1.94, FLOOR), "gold_light", top="cloth_mustard")
    for k in range(15):
        x = -1.4 + 2.8 * k / 14
        m.obox(V((x, 0.9, 0.08)), (0.03, 0.03, 0.16), "wood_dark")
    for z in (0.06, 0.13):
        m.obox(V((0, 0.9, z)), (2.84, 0.014, 0.02), "wood_mid")
    for sx in (-1, 1):
        for k in range(6):
            y = -0.85 + 1.75 * k / 5
            m.obox(V((sx * 1.4, y, 0.08)), (0.03, 0.03, 0.16), "wood_dark")
        for z in (0.06, 0.13):
            m.obox(V((sx * 1.4, 0.03, z)), (0.014, 1.74, 0.02), "wood_mid")
    for x in (-1.38, 1.38):
        m.cyl(V((x, 0.88, 0.3)), 0.012, 0.6, "wood_dark", segs=6)
    prev = None
    for k in range(17):
        t = k / 16
        q = V((-1.38 + 2.76 * t, 0.88, 0.58 - 0.09 * math.sin(math.pi * t)))
        if prev is not None:
            m.beam(prev, q, 0.004, "rope")
        prev = q
    # ---- the lock board: plank wall on two posts, hasps with practice locks (the one being picked is a part)
    kh = to_world(PICK_SPOT, PICK_FACE, J.LOCK_C)                       # the keyhole
    bx = kh.x - 0.03                                                    # the board's face (behind the lock)
    for y in (-0.36, 0.2):
        m.obox(V((bx - 0.03, y, 0.22)), (0.04, 0.04, 0.44), "wood_dark")
    for k in range(5):
        m.obox(V((bx - 0.01, -0.08, 0.08 + 0.065 * k)), (0.02, 0.6, 0.06), "wood_light" if k % 2 else "wood_mid")
    for k, (y, z, sw) in enumerate(((-0.28, 0.3, "iron"), (0.1, 0.3, "copper"), (-0.27, 0.15, "gold_dark"), (0.12, 0.13, "iron"))):
        m.obox(V((bx + 0.004, y, z + 0.02)), (0.008, 0.012, 0.03), "iron_dark")                    # hasp
        m.obox(V((bx + 0.014, y, z - 0.012)), (0.018, 0.04, 0.045), sw)                           # a lock
    m.obox(V((bx + 0.004, kh.y, kh.z + 0.045)), (0.008, 0.012, 0.03), "iron_dark")                 # its hasp
    for k in range(5):                                                                              # a rack of picks
        m.beam(V((bx + 0.01, 0.3 + 0.012 * k, 0.4)), V((bx + 0.01, 0.3 + 0.012 * k, 0.33)), 0.003, "iron_light")
    m.obox(V((bx + 0.004, 0.32, 0.41)), (0.006, 0.08, 0.012), "wood_dark")
    # ---- the straw dummy on a post, wearing a coat
    dc = to_world(LIFT_SPOT, LIFT_FACE, J.loc(f=0.2, l=0.0))
    m.cyl(V((dc.x, dc.y, 0.12)), 0.012, 0.24, "wood_dark", segs=6)
    m.cyl(V((dc.x, dc.y, 0.012)), 0.07, 0.024, "wood_mid", segs=8)
    m.blob(V((dc.x, dc.y, 0.2)), V((0.075, 0.09, 0.1)), "cloth_blue", 8, 5)                       # coat body
    m.blob(V((dc.x, dc.y, 0.33)), V((0.06, 0.06, 0.06)), "burlap", 8, 4)                          # straw head
    m.cyl(V((dc.x, dc.y, 0.385)), 0.06, 0.012, "soot", segs=10)                                   # hat brim
    m.cyl(V((dc.x, dc.y, 0.41)), 0.035, 0.04, "soot", segs=8)
    m.obox(V((dc.x, dc.y, 0.15)), (0.155, 0.185, 0.014), "leather_dark")                          # belt
    for sy in (-1, 1):                                                                             # straw arms
        m.beam(V((dc.x, dc.y + sy * 0.08, 0.26)), V((dc.x - 0.02, dc.y + sy * 0.15, 0.18)), 0.025, "cloth_blue")
        m.blob(V((dc.x - 0.025, dc.y + sy * 0.16, 0.17)), V((0.02, 0.02, 0.02)), "burlap", 5, 3)
    hook = to_world(LIFT_SPOT, LIFT_FACE, J.PURSE_HOOK)
    m.beam(hook + V((0.03, 0, 0.0)), hook, 0.005, "iron_dark")                                      # the purse hook
    # ---- round about: straw bales, a basket of purses, a chalk score board
    for k, (x, y) in enumerate(((-1.15, 0.65), (-0.95, 0.68), (1.12, 0.62))):
        m.obox(V((x, y, 0.06)), (0.18, 0.12, 0.12), "fur_tan", top="burlap", rot=(0, 0, 0.2 * k))   # darker straw
        for dx in (-0.045, 0.045):                                                    # than the sand, two twine bands
            off = V((dx * math.cos(0.2 * k), dx * math.sin(0.2 * k), 0))
            m.obox(V((x, y, 0.06)) + off, (0.012, 0.126, 0.126), "rope_dark", rot=(0, 0, 0.2 * k))
    bk = V((0.98, -0.62, 0.0))
    m.cyl(bk + V((0, 0, 0.05)), 0.08, 0.1, "burlap", segs=8, r2=0.09, cap="wood_dark")
    for k in range(4):
        a = TAU * k / 4
        m.blob(bk + V((0.045 * math.cos(a), 0.045 * math.sin(a), 0.11)), V((0.025, 0.025, 0.02)),
               ["leather", "cloth_red", "leather_dark", "cloth_blue"][k], 6, 3)
    sb = V((0.0, 0.84, 0.0))
    m.obox(sb + V((0, 0, 0.22)), (0.26, 0.016, 0.16), "soot")
    for k in range(5):
        m.obox(sb + V((-0.09 + 0.045 * k, -0.01, 0.22 + 0.02 * (k % 2))), (0.006, 0.003, 0.06), "cloth_cream")
    for x in (-0.12, 0.12):
        m.obox(sb + V((x, 0, 0.12)), (0.02, 0.02, 0.24), "wood_dark")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # the padlock being picked: body (the pick's tip goes into its keyhole) and its shackle
    mm = B.M()
    body_c = kh + V((-0.012, 0, -0.006))
    mm.obox(body_c, (0.024, 0.044, 0.05), "iron", top="iron_light")
    mm.obox(kh + V((0.0005, 0, 0.0)), (0.002, 0.008, 0.012), "soot")                                  # keyhole
    parts["pr_lock"] = A.part(mm.obj("pr_lock", coll), root, kh + V((-0.012, 0, 0.045)))
    mm = B.M()
    sc = kh + V((-0.012, 0, 0.03))
    for sy in (-1, 1):
        mm.beam(sc + V((0, sy * 0.014, 0)), sc + V((0, sy * 0.014, 0.022)), 0.005, "iron_light")
    mm.beam(sc + V((0, -0.014, 0.022)), sc + V((0, 0.014, 0.022)), 0.005, "iron_light")
    parts["pr_shackle"] = A.part(mm.obj("pr_shackle", coll), root, sc + V((0, 0.014, 0)))
    # the purse on its string
    mm = B.M()
    neck = hook + V((0, 0, -0.012))
    mm.beam(hook, neck, 0.003, "rope")
    mm.blob(neck + V((0, 0, -0.03)), V((0.026, 0.022, 0.028)), "leather", 7, 4)
    mm.cyl(neck + V((0, 0, -0.004)), 0.01, 0.01, "leather_dark", segs=6)
    mm.blob(neck + V((0.0, 0.0, -0.055)), V((0.012, 0.012, 0.008)), "gold", 5, 3)                 # a coin peeking out
    parts["pr_purse"] = A.part(mm.obj("pr_purse", coll), root, hook)
    # the dummy's coat-tail, and a bunting flag
    mm = B.M()
    ct = V((dc.x + 0.06, dc.y, 0.12))
    mm.obox(ct + V((0.0, 0, -0.04)), (0.012, 0.12, 0.08), "cloth_blue")
    parts["pr_coattail"] = A.part(mm.obj("pr_coattail", coll), root, ct)
    for i, t in enumerate((0.25, 0.5, 0.75)):
        mm = B.M()
        q = V((-1.38 + 2.76 * t, 0.88, 0.58 - 0.09 * math.sin(math.pi * t) - 0.004))
        mm.obox(q + V((0, 0, -0.035)), (0.06, 0.004, 0.06), ["cloth_red", "teal", "gold_light"][i], rot=(0, math.pi / 4, 0))
        parts[f"pr_bunting_{i + 1}"] = A.part(mm.obj(f"pr_bunting_{i + 1}", coll), root, q)
    return root, parts


def clips(parts):
    f, l, u = frame_of(LIFT_FACE)

    def common(p):
        out = {}
        for i in range(3):
            out[f"pr_bunting_{i + 1}"] = (None, A.q((1, 0, 0), 12 * math.sin(TAU * (2 * p + 0.2 * i))), None)
        out["pr_coattail"] = (None, A.q((0, 1, 0), 5 * math.sin(TAU * p)), None)
        return out

    def idle(p):
        out = common(p)
        out["pr_lock"] = (None, A.q((0, 1, 0), 3 * math.sin(TAU * p)), None)
        return out

    def work(p):
        out = common(p)
        pop = J.ramp(p, J.LOCK_POP - 0.01, J.LOCK_POP + 0.03) * (1 - J.ramp(p, 0.9, 0.95))
        out["pr_shackle"] = (V((0, 0, 0.014 * pop)), A.q((0, 0, 1), 70 * pop), None)       # springs up and swings open
        out["pr_lock"] = (None, A.q((0, 1, 0), 2 * math.sin(TAU * 9 * p)), None)
        o = J.lift_purse(p)
        out["pr_purse"] = (f * (-o.y) + l * o.x + u * o.z, None, None)
        return out

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(14))
    A.spot(root, "spot_pick", PICK_SPOT, tuple(PICK_FACE))
    A.spot(root, "spot_lift", LIFT_SPOT, tuple(LIFT_FACE))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "practice_yard.blend"), relative_remap=True)
    A.export()
    r1, m1, pick = A.raccoon_at(bpy.data.objects["spot_pick"], clip="work_picklock", tool="prop_lockpick")
    r2, m2, _ = A.raccoon_at(bpy.data.objects["spot_lift"], clip="work_lift")
    crew = [(r1, m1, pick, "work", {"pr_lock": None}), (r2, m2, None, "work", {"pr_purse": None, NAME: None})]
    allow = [("pr_lock", NAME), ("pr_shackle", NAME), ("pr_shackle", "pr_lock"), ("pr_purse", NAME), ("pr_coattail", NAME)] + \
            [(f"pr_bunting_{i + 1}", NAME) for i in range(3)]
    probs = A.check(root, 3, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [r1, m1, pick, r2, m2], ROOT / "renders" / "bld_practice_yard_loops.gif",
                       target=(-0.1, 0.0, 0.15), dist=3.9, pitch=40, idle_frames=24, grid_n=4, step=2)


if __name__ == "__main__":
    main()
