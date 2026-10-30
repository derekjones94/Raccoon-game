"""bld_haulers_lodge_2x2: home base for the colony's haulers, who carry goods between buildings.

A plank yard with an open-fronted shed at the back: two straw bunks where off-shift haulers sleep (spot_rest_1, _2:
sleep), packs on pegs, cargo stacked in the corner, a lantern, and a hanging sign with a cart wheel on it. In front, a
low dray (a crate slung between two wheels, its near side a low lip): a hauler crouches behind it loading goods
(spot_work, facing the front: work_stash). On the right a hoist: a post and jib with a crate on a rope and a winch
wheel; a spare cart wheel on a wheelwright's stand.

Clips (24 fps)
  idle  48 fr  the sign and the lantern sway, the wheel on the stand turns slowly, the hoist's crate rests
  work  48 fr  as idle, plus the hoist lifts its crate and lowers it again (the winch wheel turns with it), and the
               goods in the dray settle on each shove of work_stash (start them together, both 48 frames)

Run:  python3 tools/build_haulers_lodge.py   (--no-renders)
Out:  haulers_lodge.blend, export/bld_haulers_lodge_2x2.glb, renders/bld_haulers_lodge_loops.gif, renders/qa_buildings.txt
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
import build_den as DEN  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_stockpile as SP  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_haulers_lodge_2x2"
FRAMES = 48
DECK = 0.03                                      # top of the plank yard
SPOT = V((-0.42, -0.24, DECK + 0.0015))          # the loader, behind the dray, facing the front (-Y)
CRATE = (SPOT.x - 0.16, SPOT.x + 0.16, SPOT.y - 0.31, SPOT.y - 0.1)   # the dray's body (as the stockpile's crate)
SHOVES = SP.SHOVES
SHED_FRONT = (0.14, 0.64)                        # y and height of the shed's front beam; it slopes down to the back
SHED_BACK = (0.92, 0.46)
BEDS = [V((-0.5, 0.58, DECK)), V((0.0, 0.58, DECK))]
HOIST = V((0.66, -0.3, DECK))                    # the hoist post's foot
JIB = V((0.66, -0.62, DECK + 0.68))              # the jib's end: the rope hangs from here
LOAD = V((0.66, -0.62, DECK))                    # the hoisted crate's resting place (its bottom centre)
LIFT = 0.24
WHEEL = V((0.62, 0.3, DECK + 0.13))              # the spare wheel's hub, on its stand


def wheel(m, c, r, axis, sw="wood_mid", spokes=6):
    """A cart wheel: rim, hub and spokes; axis is X or Y (a tuple)."""
    a = V(axis)
    u = V((0, 0, 1))
    w = a.cross(u)
    m.cyl(c, r, 0.022, sw, axis=axis, segs=12, cap="wood_dark")
    m.cyl(c + a * 0.001, r - 0.016, 0.024, "wood_dark", axis=axis, segs=12)                    # the dark inside of the rim
    m.cyl(c, 0.02, 0.04, "iron_dark", axis=axis, segs=6)
    for k in range(spokes):
        t = math.pi * k / spokes
        d = u * math.cos(t) + w * math.sin(t)
        m.beam(c - d * (r - 0.01), c + d * (r - 0.01), 0.008, sw)


def build(coll, rnd):
    m = DEN.DenMesh()                                # (B.M plus face(), for the den's rounded bed pads)
    # ---- plank yard
    a = 0.97
    n = 9
    for k in range(n):
        x = -a + 2 * a * (k + 0.5) / n
        m.obox(V((x, 0, DECK / 2)), (2 * a / n - 0.012, 2 * a, DECK), "wood_mid" if k % 2 else "wood_weathered")
    for y in (-0.8, -0.05, 0.75):
        m.obox(V((0, y, DECK + 0.002)), (2 * a - 0.02, 0.03, 0.004), "wood_dark")
    # ---- the shed: posts, beams, a plank back wall, a low wall on the left, a plank roof
    fy, fz = SHED_FRONT
    by, bz = SHED_BACK
    for x in (-0.88, 0.0, 0.88):
        for (y, h) in (SHED_FRONT, SHED_BACK):
            m.obox(V((x, y, h / 2)), (0.045, 0.045, h), "wood_dark")
    m.beam(V((-0.9, fy, fz)), V((0.9, fy, fz)), 0.034, "wood_dark")
    m.beam(V((-0.9, by, bz)), V((0.9, by, bz)), 0.034, "wood_dark")
    for k in range(10):                                                                       # back wall planks
        x = -0.88 + 1.76 * (k + 0.5) / 10
        m.obox(V((x, by + 0.02, bz / 2)), (0.17, 0.016, bz - 0.01), "wood_light" if k % 2 else "wood_mid")
    for k in range(4):                                                                        # low wall, left side
        y = fy + (by - fy) * (k + 0.5) / 4
        m.obox(V((-0.905, y, 0.12)), (0.016, (by - fy) / 4 - 0.006, 0.22), "wood_mid" if k % 2 else "wood_light")
    ang = math.atan2(bz - fz, by - fy)
    L = math.hypot(by - fy, bz - fz)
    for k in range(9):                                                                        # roof planks
        x = -0.96 + 1.92 * (k + 0.5) / 9
        m.obox(V((x, (fy + by) / 2, (fz + bz) / 2 + 0.026)), (1.92 / 9 - 0.006, L + 0.1, 0.016),
               "wood_bark" if k % 2 else "wood_dark", rot=(ang, 0, 0))
    # ---- inside: two bunks, packs on pegs, a water barrel, cargo in the right corner
    off, half = DEN.SLEEP_BOX["chr_raccoon"]
    for c, bl in zip(BEDS, ("cloth_mustard", "teal")):                                        # the den's beds, on the deck
        DEN.pad(m, c, half.x + 0.03, half.y + 0.03, DEN.MAT, "rope", z0=DECK, side="rope_dark")
        DEN.pad(m, c, half.x + 0.006, half.y + 0.006, DEN.BLANKET, bl, z0=DECK + DEN.MAT, side=bl, band=False)
    for k, x in enumerate((-0.62, -0.38, -0.12, 0.12)):                                      # pegs and packs
        m.cyl(V((x, by, 0.32)), 0.006, 0.04, "wood_dark", axis=(0, 1, 0), segs=4)
        if k % 2 == 0:
            m.blob(V((x, by - 0.035, 0.25)), V((0.05, 0.03, 0.065)), "leather" if k else "burlap", 7, 4)
            m.beam(V((x - 0.02, by - 0.01, 0.32)), V((x - 0.03, by - 0.05, 0.28)), 0.006, "leather_dark")
        else:
            m.cyl(V((x, by - 0.03, 0.27)), 0.04, 0.012, "rope", axis=(0, 1, 0), segs=8, cap="rope_dark")
    for c in ((0.42, 0.78), (0.62, 0.8), (0.52, 0.6)):
        PR_crate(m, V((c[0], c[1], DECK)), 0.16)
    PR_crate(m, V((0.52, 0.79, DECK + 0.16)), 0.13, sw="wood_light")
    for c in ((0.78, 0.6), (0.8, 0.45)):
        B.sack(m, V((c[0], c[1], DECK)), 0.065)
    # ---- the dray: a crate slung low between two big wheels, shafts out front
    SP.packing_crate(m, CRATE, DECK, sw="wood_light")
    x0, x1, y0, y1 = CRATE
    yc = (y0 + y1) / 2
    for x in (x0 - 0.024, x1 + 0.024):
        wheel(m, V((x, yc, DECK + 0.085)), 0.085, (1, 0, 0))
    m.cyl(V(((x0 + x1) / 2, yc, DECK + 0.085)), 0.01, x1 - x0 + 0.03, "iron_dark", axis=(1, 0, 0), segs=5)
    for x in (x0 + 0.04, x1 - 0.04):                                                          # shafts, resting on the deck
        m.beam(V((x, y0 + 0.01, DECK + 0.06)), V((x + (0.03 if x < SPOT.x else -0.03), y0 - 0.3, DECK + 0.01)), 0.016, "wood_dark")
    m.beam(V((x0 + 0.07, y0 - 0.27, DECK + 0.016)), V((x1 - 0.07, y0 - 0.27, DECK + 0.016)), 0.014, "wood_mid")
    # ---- the hoist: post, jib and brace, winch drum, a pile of loads under it
    m.obox(V((HOIST.x, HOIST.y, DECK + 0.36)), (0.05, 0.05, 0.72), "wood_dark")
    m.obox(V((HOIST.x, HOIST.y, DECK + 0.02)), (0.14, 0.14, 0.04), "stone_mid", top="stone_light")
    m.beam(V((HOIST.x, HOIST.y + 0.02, JIB.z + 0.02)), V((JIB.x, JIB.y - 0.02, JIB.z + 0.02)), 0.034, "wood_mid")
    m.beam(V((HOIST.x, HOIST.y - 0.02, JIB.z - 0.22)), V((HOIST.x, HOIST.y - 0.2, JIB.z + 0.005)), 0.022, "wood_mid")
    m.cyl(V((JIB.x, JIB.y, JIB.z + 0.0)), 0.022, 0.03, "iron", axis=(1, 0, 0), segs=8)       # pulley block
    m.cyl(V((HOIST.x + 0.04, HOIST.y, DECK + 0.3)), 0.03, 0.05, "wood_light", axis=(1, 0, 0), segs=8, cap="wood_dark")
    rx = HOIST.x + 0.02                                                       # the hauling rope: over the pulley,
    pts = [V((rx, JIB.y, JIB.z + 0.022)), V((rx, HOIST.y - 0.031, JIB.z + 0.022)),   # back along the jib and down
           V((rx, HOIST.y - 0.031, DECK + 0.335)), V((rx, HOIST.y, DECK + 0.33))]   # the post to the winch drum
    for q0, q1 in zip(pts, pts[1:]):
        m.beam(q0, q1, 0.006, "rope")
    for c in ((0.86, -0.55), (0.86, -0.75), (0.45, -0.82)):                                 # loads waiting
        PR_crate(m, V((c[0], c[1], DECK)), 0.12)
    m.cyl(V((0.86, -0.3, DECK + 0.015)), 0.06, 0.03, "rope", segs=10, cap="rope_dark")
    # ---- the wheelwright's stand (the spare wheel turns on it), a barrel, a yoke on the front post
    for dx in (-0.03, 0.03):
        m.obox(V((WHEEL.x + dx * 2.2, WHEEL.y, (DECK + WHEEL.z) / 2)), (0.02, 0.05, WHEEL.z - DECK), "wood_dark")
        m.obox(V((WHEEL.x + dx * 2.2, WHEEL.y, DECK + 0.01)), (0.03, 0.14, 0.02), "wood_dark")
    m.cyl(WHEEL, 0.008, 0.15, "iron_dark", axis=(1, 0, 0), segs=5)
    m.cyl(V((0.86, 0.12, DECK + 0.1)), 0.075, 0.2, "wood_mid", cap="water", segs=8)
    for z in (0.04, 0.16):
        m.cyl(V((0.86, 0.12, DECK + z)), 0.079, 0.012, "iron_dark", segs=8)
    m.beam(V((-0.86, fy - 0.03, 0.42)), V((-0.7, fy - 0.03, 0.36)), 0.016, "wood_light")    # a yoke on the post
    m.obox(V((-0.88, fy - 0.03, 0.3)), (0.12, 0.012, 0.09), "soot")                           # job slate: tallies
    for k in range(3):
        m.obox(V((-0.91 + 0.02 * k, fy - 0.038, 0.3)), (0.005, 0.004, 0.05), "cloth_cream")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    # the dray's load (still: the paws press into it)
    m = B.M()
    gi = (x0 + SP.WALL, x1 - SP.WALL, y0 + SP.WALL, y1 - SP.WALL)
    m.obox(V(((gi[0] + gi[1]) / 2, (gi[2] + gi[3]) / 2, DECK + 0.035)), (gi[1] - gi[0] - 0.004, gi[3] - gi[2] - 0.004, 0.05),
           "burlap")
    for k in range(7):
        p = V((rnd.uniform(gi[0] + 0.03, gi[1] - 0.03), rnd.uniform(gi[2] + 0.03, gi[3] - 0.03), DECK + 0.06))
        m.blob(p, V((0.024, 0.022, 0.018)), rnd.choice(["burlap", "cloth_cream", "wood_light"]), 6, 3)
    goods = m.obj("pr_goods", coll)
    goods.parent = root
    parts = {}
    for i, (dx, dy, kind) in enumerate(((-0.07, 0.05, "bundle"), (0.075, 0.05, "jar"))):
        c = V(((x0 + x1) / 2 + dx, yc + dy, DECK + 0.078))
        m = B.M()
        if kind == "bundle":
            m.obox(c + V((0, 0, -0.004)), (0.07, 0.04, 0.026), "burlap", rot=(0, 0, 0.3))
            m.obox(c + V((0, 0, -0.004)), (0.012, 0.042, 0.028), "rope", rot=(0, 0, 0.3))
        else:
            m.cyl(c, 0.02, 0.04, "copper", segs=6, cap="cloth_cream")
        parts[f"pr_good_{i + 1}"] = A.part(m.obj(f"pr_good_{i + 1}", coll), root, c)
    # the hanging sign: a board with a cart wheel on it, on two chains from the front beam
    m = B.M()
    sh = V((0.42, fy, fz - 0.017))
    for dx in (-0.06, 0.06):
        m.beam(sh + V((dx, 0, 0)), sh + V((dx, 0, -0.07)), 0.004, "iron_dark")
    m.obox(sh + V((0, 0, -0.11)), (0.17, 0.014, 0.08), "wood_light")
    m.obox(sh + V((0, -0.008, -0.11)), (0.18, 0.004, 0.088), "wood_dark")
    m.cyl(sh + V((0, -0.011, -0.11)), 0.028, 0.004, "gold", axis=(0, 1, 0), segs=8)
    m.cyl(sh + V((0, -0.013, -0.11)), 0.019, 0.004, "wood_light", axis=(0, 1, 0), segs=8)
    for k in range(3):
        t = math.pi * k / 3
        m.obox(sh + V((0, -0.015, -0.11)), (0.05 * abs(math.cos(t)) + 0.004, 0.003, 0.05 * abs(math.sin(t)) + 0.004),
               "gold")
    parts["pr_sign"] = A.part(m.obj("pr_sign", coll), root, sh)
    # the lantern on the front beam
    m = B.M()
    lt = V((-0.25, fy, fz - 0.017))
    m.cyl(lt + V((0, 0, -0.03)), 0.003, 0.06, "iron_dark", segs=4)
    m.obox(lt + V((0, 0, -0.085)), (0.045, 0.045, 0.06), "flame_yellow")
    m.obox(lt + V((0, 0, -0.052)), (0.055, 0.055, 0.012), "iron_dark")
    m.obox(lt + V((0, 0, -0.118)), (0.055, 0.055, 0.01), "iron_dark")
    parts["pr_lantern"] = A.part(m.obj("pr_lantern", coll), root, lt)
    # the hoist: rope (built along -Z from the pulley, so it stretches), the load, the winch wheel
    m = B.M()
    rest_len = JIB.z - 0.022 - (LOAD.z + 0.13)
    m.beam(JIB + V((0, 0, -0.02)), JIB + V((0, 0, -0.02 - rest_len)), 0.006, "rope")
    parts["pr_hoist_rope"] = A.part(m.obj("pr_hoist_rope", coll), root, JIB + V((0, 0, -0.02)))
    m = B.M()
    PR_crate(m, LOAD, 0.12, sw="wood_light")
    m.beam(LOAD + V((-0.05, 0, 0.12)), LOAD + V((0, 0, 0.135)), 0.005, "rope")
    m.beam(LOAD + V((0.05, 0, 0.12)), LOAD + V((0, 0, 0.135)), 0.005, "rope")
    m.cyl(LOAD + V((0, 0, 0.142)), 0.012, 0.005, "iron", axis=(0, 1, 0), segs=8)            # the hook ring
    parts["pr_load"] = A.part(m.obj("pr_load", coll), root, LOAD)
    m = B.M()
    wc = V((HOIST.x + 0.075, HOIST.y, DECK + 0.3))
    wheel(m, wc, 0.07, (1, 0, 0), sw="wood_light", spokes=4)
    m.beam(wc + V((0.015, 0, 0.0)), wc + V((0.015, 0, -0.06)), 0.01, "wood_dark")
    m.cyl(wc + V((0.03, 0, -0.06)), 0.008, 0.035, "wood_light", axis=(1, 0, 0), segs=5)      # the crank handle
    parts["pr_winch"] = A.part(m.obj("pr_winch", coll), root, wc)
    # the spare wheel on the stand
    m = B.M()
    wheel(m, WHEEL, 0.11, (1, 0, 0), sw="wood_mid")
    parts["pr_wheel"] = A.part(m.obj("pr_wheel", coll), root, WHEEL)
    return root, goods, parts


def PR_crate(m, c, s, sw="wood_mid"):
    """A closed crate (bottom centre c, size s) with dark battens."""
    m.obox(c + V((0, 0, s / 2)), (s, s, s), sw, top="wood_light")
    m.obox(c + V((0, -s / 2 - 0.002, s / 2)), (s * 0.95, 0.004, 0.018), "wood_dark", rot=(0.0, 0.7, 0.0))
    m.obox(c + V((0, -s / 2 - 0.002, s / 2)), (s * 0.95, 0.004, 0.018), "wood_dark", rot=(0.0, -0.7, 0.0))


def hoist_lift(p):
    """0..LIFT: the load goes up, hangs a moment, comes down (once a loop)."""
    if p < 0.4:
        return LIFT * (3 * (p / 0.4) ** 2 - 2 * (p / 0.4) ** 3)
    if p < 0.55:
        return LIFT
    t = (p - 0.55) / 0.4
    return LIFT * (1 - (3 * t ** 2 - 2 * t ** 3)) if t < 1 else 0.0


def clips(parts):
    rest_len = JIB.z - 0.022 - (LOAD.z + 0.13)

    def common(p):
        pose = {}
        pose["pr_sign"] = (None, A.q((1, 0, 0), 9 * math.sin(TAU * p) + 3 * math.sin(TAU * 3 * p)), None)
        pose["pr_lantern"] = (None, A.q((1, 0, 0), 6 * math.sin(TAU * p + 1)) @ A.q((0, 1, 0), 3 * math.sin(TAU * 2 * p)), None)
        pose["pr_wheel"] = (None, A.q((1, 0, 0), -360 * p), None)
        return pose

    def idle(p):
        return common(p)

    def work(p):
        pose = common(p)
        h = hoist_lift(p)
        sway = 2.5 * math.sin(TAU * 2 * p) * (h / LIFT)
        pose["pr_load"] = (V((0, 0, h)), A.q((1, 0, 0), sway), None)
        pose["pr_hoist_rope"] = (None, None, (1, 1, (rest_len - h) / rest_len))
        pose["pr_winch"] = (None, A.q((1, 0, 0), -math.degrees(h / 0.03)), None)
        for i, ph in ((1, 0.0), (2, 0.03)):
            k = sum(math.exp(-((p - c - ph) ** 2) / 0.0015) for c in SHOVES)
            pose[f"pr_good_{i}"] = (V((0, 0, -0.007 * k)), A.q((1, 0.5 * i, 0), 8 * k * math.sin(TAU * 4 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, goods, parts = build(coll, random.Random(23))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    for i, c in enumerate(BEDS):
        A.spot(root, f"spot_rest_{i + 1}", DEN.bed_spot(c, "chr_raccoon") + V((0, 0, DECK)), (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(goods) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(goods)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "haulers_lodge.blend"), relative_remap=True)
    A.export()
    rig, mesh, _ = A.raccoon_at(bpy.data.objects["spot_work"], clip="work_stash")
    crew = [(rig, mesh, None, "work", {"pr_goods": None, "pr_good_1": None, "pr_good_2": None})]
    objs = [rig, mesh]
    for i in range(len(BEDS)):
        r2, m2, _ = A.raccoon_at(bpy.data.objects[f"spot_rest_{i + 1}"], clip="sleep")
        crew.append((r2, m2, None, "work", {}))
        objs += [r2, m2]
    allow = [("pr_goods", NAME), ("pr_good_1", "pr_goods"), ("pr_good_2", "pr_goods"), ("pr_sign", NAME),
             ("pr_lantern", NAME), ("pr_hoist_rope", NAME), ("pr_hoist_rope", "pr_load"), ("pr_load", NAME),
             ("pr_winch", NAME), ("pr_wheel", NAME)]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_haulers_lodge_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.8, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
