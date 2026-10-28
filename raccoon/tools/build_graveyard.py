"""bld_graveyard_3x3: where the colony remembers its own.

A grassy yard inside a low drystone wall, a plank gate at the front and a flagstone path up the middle to an old
memorial stone with candles. Graves lie either side of the path, side-on to it, each headstone at the outer end with
its carved face (a paw print) toward the path. An old crooked tree at the back corner, a crow, flowers, candles.

On the right at the front a fresh grave: a raised bed of dug earth, a plank marker, a basket of flowers. A raccoon
crouches beside it (spot_work, facing the front) and pats the soil round the flowers it is planting (work_tend).
Two mourners stand at the foot of graves facing their headstones, heads bowed (spot_mourn_1, _2: work_mourn).

Clips (24 fps)
  idle  96 fr  candles flicker, grass and the tree's crown sway, the gate creaks in the wind, the crow hops and pecks
  work  96 fr  as idle, plus the flower being planted wiggles on each pat of work_tend (start them together)

Run:  python3 tools/build_graveyard.py   (--no-renders)
Out:  graveyard.blend, export/bld_graveyard_3x3.glb, renders/bld_graveyard_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_graveyard_3x3"
FRAMES = 96
FLOOR = 0.006
WALL = 1.36                                      # the wall's centre line, each side
GATE = 0.2                                       # half the gate's opening
PATH = 0.17                                      # half the path's width
# graves: (x of the headstone, y, facing of the stone's carved face (+1: toward +X)), mounds run from the stone to the path
GRAVES = [(-1.08, -0.72, 1), (-1.08, -0.12, 1), (-1.08, 0.5, 1), (1.08, -0.12, -1), (1.08, 0.5, -1)]
FRESH = (1.08, -0.72)                            # the fresh grave's marker
BED_H = 0.04                                     # the fresh bed's flat soil top, over the floor (as the cave garden's)
SPOT = V((0.86, -0.72 + 0.1 + 0.108, FLOOR + 0.0015))   # the gardener, behind the fresh bed (its back edge just clears
TENDED = SPOT + J.TEND_C                                  # the toes), facing the front; the flower between the paws
MOURN = [(V((-0.42, -0.12, FLOOR + 0.0015)), (-1, 0, 0)), (V((0.42, 0.5, FLOOR + 0.0015)), (1, 0, 0))]


def headstone(m, c, face, kind, rnd):
    """A stone at c (on the ground), its carved face toward +X * face."""
    rot = (0, 0, math.pi / 2)                       # boxes: their X across the stone, Y through it
    lean = rnd.uniform(-0.08, 0.08) if kind == "slab" else 0.0
    sw = rnd.choice(["stone_mid", "stone_light", "stone_pale"])
    if kind == "round":
        h, w, th = 0.17, 0.13, 0.035
        m.obox(c + V((0, 0, h / 2)), (w, 0.035, h), sw, rot=(lean, 0, rot[2]))
        m.cyl(c + V((0, 0, h)), w / 2, 0.035, sw, axis=(1, 0, 0), segs=8)
    elif kind == "cross":
        m.obox(c + V((0, 0, 0.11)), (0.035, 0.03, 0.22), sw, rot=(lean, 0, rot[2]))
        m.obox(c + V((0, 0, 0.16)), (0.12, 0.03, 0.035), sw, rot=(lean, 0, rot[2]))
        h, th = 0.18, 0.03
    else:                                           # a squat slab
        h, w, th = 0.11, 0.15, 0.04
        m.obox(c + V((0, 0, h / 2)), (w, 0.04, h), sw, top="stone_light", rot=(lean, 0, rot[2]))
    m.obox(c + V((0, 0, 0.012)), (0.05, 0.17, 0.024), "stone_dark")                         # plinth
    fx = c.x + face * (th / 2 + 0.001)
    if kind != "cross":                                                                       # a carved paw print
        pz = c.z + h * 0.55
        m.obox(V((fx, c.y, pz)), (0.004, 0.034, 0.026), "stone_deep")
        for k in range(4):
            m.obox(V((fx, c.y - 0.024 + 0.016 * k, pz + 0.026)), (0.004, 0.01, 0.01), "stone_deep")
    if rnd.random() < 0.6:                                                                    # moss on the shoulders
        m.blob(c + V((0, rnd.choice((-0.04, 0.04)), h * 0.85)), V((0.03, 0.04, 0.02)), "moss_light", 5, 3)
    return h


def mound(m, x0, x1, y, rnd):
    m.blob(V(((x0 + x1) / 2, y, FLOOR - 0.012)), V((abs(x1 - x0) / 2 + 0.01, 0.1, 0.035)), "wood_weathered", 8, 4)   # a border
    m.blob(V(((x0 + x1) / 2, y, FLOOR - 0.01)), V((abs(x1 - x0) / 2, 0.09, 0.04)), "moss_light", 8, 4)
    for k in range(3):
        m.blob(V((x0 + (x1 - x0) * (0.25 + 0.25 * k), y + rnd.uniform(-0.04, 0.04), FLOOR + 0.02)),
               V((0.018, 0.018, 0.012)), rnd.choice(["cloth_cream", "gold_light", "amethyst"]), 5, 3)    # wild flowers


def candle(m, c, h=0.04):
    m.cyl(c + V((0, 0, h / 2)), 0.01, h, "cloth_cream", segs=6, cap="bone")


def build(coll, rnd):
    m = B.M()
    # ---- ground: grass, the flagstone path, a worn patch round the memorial
    m.obox(V((0, 0, FLOOR / 2)), (2.94, 2.94, FLOOR), "moss")
    for k in range(13):
        y = -1.32 + k * 0.19
        if y > 0.95:
            break
        x = rnd.uniform(-0.03, 0.03)
        m.obox(V((x, y, FLOOR + 0.002 + 0.0006 * (k % 3))), (2 * PATH - rnd.uniform(0.02, 0.06), 0.16, 0.004),
               rnd.choice(["stone_mid", "stone_light"]), rot=(0, 0, rnd.uniform(-0.08, 0.08)))
    m.blob(V((0, 1.1, FLOOR - 0.014)), V((0.42, 0.26, 0.018)), "wood_weathered", 10, 3)
    # ---- the drystone wall, with the gate gap at the front
    for side in range(4):
        for k in range(10):
            t = -WALL + (k + 0.5) * 2 * WALL / 10
            if side == 0 and abs(t) < GATE + 0.05:
                continue
            x, y = [(t, -WALL), (WALL, t), (t, WALL), (-WALL, t)][side]
            along = (1, 0) if side % 2 == 0 else (0, 1)
            L = 2 * WALL / 10
            for z, hh, w, sw in ((0.035, 0.07, 0.08, rnd.choice(["stone_mid", "stone_light"])),
                                 (0.095 + 0.004 * (k % 3), 0.05, 0.066, rnd.choice(["stone_mid", "stone_pale"]))):
                sz = (L - 0.014, w, hh) if along[0] else (w, L - 0.014, hh)     # blocks never overlap: no shared tops
                m.obox(V((x, y, z)), sz, sw, top="stone_light", rot=(0, 0, rnd.uniform(-0.03, 0.03)))
    for sx in (-1, 1):                                                                         # gate posts with caps
        m.obox(V((sx * (GATE + 0.04), -WALL, 0.1)), (0.08, 0.08, 0.2), "stone_dark", top="stone_light")
        m.cyl(V((sx * (GATE + 0.04), -WALL, 0.215)), 0.035, 0.03, "stone_light", segs=6)
    # ---- graves
    for i, (x, y, face) in enumerate(GRAVES):
        headstone(m, V((x, y, FLOOR)), face, ["round", "slab", "cross", "round", "slab"][i], rnd)
        mound(m, x + face * 0.06, x + face * 0.44, y, rnd)
    for x, y in ((-1.08, 1.05), (1.08, 1.05)):                                               # two old sunken stones
        headstone(m, V((x, y, FLOOR - 0.03)), 1 if x < 0 else -1, "slab", rnd)
    # ---- the fresh grave: a raised bed of dug earth with a plank marker, a basket and a trowel
    x0, x1 = FRESH[0] - 0.42, FRESH[0] + 0.02
    y0, y1 = FRESH[1] - 0.1, SPOT.y - 0.108
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, FLOOR + (BED_H - 0.002) / 2)), (x1 - x0 - 0.04, y1 - y0 - 0.02, BED_H - 0.002),
           "fur_brown", top="fur_brown")
    for sx in (-1, 1):                                                                        # rounded earth ends
        m.blob(V((x0 + 0.02 if sx < 0 else x1 - 0.02, (y0 + y1) / 2, FLOOR)), V((0.04, (y1 - y0) / 2, BED_H - 0.002)),
               "fur_brown", 6, 3)
    m.blob(V(((x0 + x1) / 2 + 0.03, y0 + 0.07, FLOOR + BED_H - 0.012)), V((0.17, 0.065, 0.035)), "fur_brown", 8, 4)
    for k in range(5):                                                                        # clods and pebbles
        m.blob(V((x0 + 0.06 + 0.08 * k, y0 + 0.02 + 0.03 * (k % 2), FLOOR + BED_H - 0.002)), V((0.016, 0.014, 0.01)),
               "wood_dark" if k % 2 else "stone_mid", 5, 3)
    m.blob(V(((x0 + x1) / 2, (y0 + y1) / 2, FLOOR - 0.012)), V(((x1 - x0) / 2 + 0.05, (y1 - y0) / 2 + 0.04, 0.02)),
           "wood_weathered", 8, 3)                                                            # spilt soil round it
    m.obox(V((FRESH[0], FRESH[1], 0.12)), (0.025, 0.02, 0.24), "wood_mid")                   # the marker: a post
    m.obox(V((FRESH[0] - 0.012, FRESH[1], 0.19)), (0.012, 0.1, 0.05), "wood_light")          # and a board, a paw on it
    m.obox(V((FRESH[0] - 0.019, FRESH[1], 0.19)), (0.003, 0.025, 0.02), "soot")
    bk = V((SPOT.x + 0.18, SPOT.y + 0.02, FLOOR))                                            # basket of flowers
    m.cyl(bk + V((0, 0, 0.03)), 0.05, 0.06, "burlap", segs=8, r2=0.06, cap="wood_dark")
    m.beam(bk + V((-0.045, 0, 0.06)), bk + V((0.045, 0, 0.06)), 0.006, "wood_mid")
    for k, sw in enumerate(("cloth_red", "gold_light", "amethyst", "cloth_cream")):
        a = TAU * k / 4
        m.blob(bk + V((0.025 * math.cos(a), 0.025 * math.sin(a), 0.075)), V((0.016, 0.016, 0.012)), sw, 5, 3)
    tr = V((SPOT.x - 0.17, SPOT.y + 0.03, FLOOR + 0.006))                                    # trowel
    m.beam(tr, tr + V((0.05, -0.02, 0.0)), 0.008, "wood_mid")
    m.obox(tr + V((0.075, -0.03, 0.0)), (0.04, 0.025, 0.006), "iron_light", rot=(0, 0, -0.4))
    # ---- the memorial at the back: a stone with a paw, candles and offerings, a bench
    mc = V((0.0, 1.12, FLOOR))
    m.obox(mc + V((0, 0, 0.02)), (0.32, 0.18, 0.04), "stone_dark", top="stone_mid")
    m.obox(mc + V((0, 0.02, 0.2)), (0.18, 0.1, 0.32), "stone_light", top="stone_pale")
    m.cyl(mc + V((0, 0.02, 0.38)), 0.07, 0.06, "stone_pale", segs=6, r2=0.0)
    m.obox(mc + V((0, -0.032, 0.22)), (0.06, 0.004, 0.05), "stone_deep")
    for k in range(4):
        m.obox(mc + V((-0.04 + 0.027 * k, -0.032, 0.265)), (0.016, 0.004, 0.016), "stone_deep")
    m.obox(mc + V((0, -0.07, 0.044)), (0.22, 0.04, 0.008), "stone_light")                      # a ledge for offerings
    m.blob(mc + V((0.07, -0.07, 0.06)), V((0.02, 0.02, 0.016)), "cloth_red", 6, 3)           # an apple
    m.cyl(mc + V((-0.08, -0.07, 0.056)), 0.012, 0.014, "gold", segs=8, cap="gold_light")      # a coin stack
    for x in (-0.48, -0.3):                                                                   # bench
        m.obox(V((x, 1.0, FLOOR + 0.025)), (0.03, 0.08, 0.05), "wood_dark")
    m.obox(V((-0.39, 1.0, FLOOR + 0.055)), (0.26, 0.09, 0.016), "wood_mid", top="wood_light")
    # ---- the old tree in the back corner: a crooked trunk and branches
    tb = V((-1.05, 1.0, 0.0))
    pts = [tb, tb + V((0.03, -0.02, 0.25)), tb + V((0.09, -0.05, 0.45)), tb + V((0.05, -0.04, 0.62))]
    for a, b, r in zip(pts, pts[1:], (0.06, 0.05, 0.04)):
        m.cyl((a + b) / 2, r, (b - a).length + 0.01, "wood_bark", segs=7, axis=tuple(b - a), r2=r * 0.8)
    for d in ((0.25, -0.1, 0.12), (-0.2, 0.05, 0.16), (0.08, 0.2, 0.12)):
        a = pts[2]
        b = a + V(d)
        m.beam(a, b, 0.024, "wood_bark")
    for d in ((-0.12, 0.08, 0.0), (0.1, 0.1, 0.0)):                                          # roots
        m.beam(tb + V((0, 0, 0.03)), tb + V(d) + V((0, 0, 0.0)), 0.025, "wood_bark")
    # ---- candles on the graves (bodies; the flames move) and two lanterns on the gate posts
    for c in CANDLES:
        candle(m, c)
    for sx in (-1, 1):
        lc = V((sx * (GATE + 0.04), -WALL, 0.23))
        m.cyl(lc + V((0, 0, 0.03)), 0.025, 0.05, "iron_dark", segs=6, cap="iron")
        m.cyl(lc + V((0, 0, 0.03)), 0.019, 0.035, "flame_yellow", segs=6)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    # the fresh bed is its own still object: the paws pat it
    parts = {}
    mm = B.M()
    mm.obox(V((TENDED.x, TENDED.y + 0.002, FLOOR + BED_H + 0.001)), (0.15, 0.03, 0.002), "wood_dark")   # the patted strip
    bed = mm.obj("pr_bed", coll)
    bed.parent = root
    # the flower being planted (wiggles on the pats)
    mm = B.M()
    fb = V((TENDED.x, TENDED.y, FLOOR + BED_H))
    mm.beam(fb + V((0, 0, -0.003)), fb + V((0, 0, 0.022)), 0.004, "moss")                   # a low seedling: the paws
    mm.obox(fb + V((0.007, 0, 0.012)), (0.01, 0.004, 0.006), "moss_light", rot=(0, 0.5, 0))   # pat close either side
    mm.blob(fb + V((0, 0, 0.025)), V((0.008, 0.008, 0.006)), "cloth_red", 6, 3)
    mm.blob(fb + V((0, 0, 0.029)), V((0.003, 0.003, 0.003)), "gold", 4, 3)
    parts["pr_flower"] = A.part(mm.obj("pr_flower", coll), root, fb)
    # candle flames
    for i, c in enumerate(CANDLES):
        mm = B.M()
        fc = c + V((0, 0, 0.043))
        mm.cyl(fc + V((0, 0, 0.012)), 0.008, 0.024, "flame_yellow" if i % 2 else "torch_orange", segs=5, r2=0.0)
        parts[f"pr_flame_{i + 1}"] = A.part(mm.obj(f"pr_flame_{i + 1}", coll), root, fc)
    # grass tufts
    for i, c in enumerate(TUFTS):
        mm = B.M()
        for k in range(4):
            a = TAU * k / 4 + 0.4
            tip = c + V((0.025 * math.cos(a), 0.025 * math.sin(a), 0.07 + 0.015 * (k % 2)))
            mm.cyl((c + tip) / 2, 0.008, (tip - c).length, "moss_light" if k % 2 else "moss", segs=3, r2=0.0,
                   axis=tuple(tip - c))
        parts[f"pr_tuft_{i + 1}"] = A.part(mm.obj(f"pr_tuft_{i + 1}", coll), root, c)
    # the tree's crown: three leafy clumps
    for i, d in enumerate(((0.25, -0.1, 0.12), (-0.2, 0.05, 0.16), (0.05, -0.04, 0.2))):
        mm = B.M()
        c = (pts[2] if i < 2 else pts[3]) + V(d) + V((0, 0, 0.04))
        mm.blob(c, V((0.13, 0.12, 0.09)), "moss" if i % 2 else "verdigris", 7, 4)
        mm.blob(c + V((0.05, -0.04, 0.05)), V((0.07, 0.07, 0.05)), "moss_light", 6, 3)
        parts[f"pr_leaves_{i + 1}"] = A.part(mm.obj(f"pr_leaves_{i + 1}", coll), root, c - V((0, 0, 0.08)))
    # the gate: two plank leaves, the left one ajar and creaking
    for i, sx in enumerate((-1, 1)):
        mm = B.M()
        hinge = V((sx * GATE, -WALL, 0.0))
        for k in range(3):
            mm.obox(hinge + V((-sx * (0.03 + 0.065 * k), 0, 0.1)), (0.055, 0.016, 0.16), "wood_mid" if k % 2 else "wood_light")
        for z in (0.05, 0.15):
            mm.obox(hinge + V((-sx * 0.1, -0.012, z)), (0.19, 0.01, 0.022), "wood_dark")
        parts[f"pr_gate_{i + 1}"] = A.part(mm.obj(f"pr_gate_{i + 1}", coll), root, hinge + V((0, 0, 0.01)))
    # the crow
    mm = B.M()
    cc = CROW_HOME + V((0, 0, 0.03))
    mm.blob(cc, V((0.035, 0.018, 0.02)), "soot", 6, 4)
    mm.blob(cc + V((0.03, 0, 0.018)), V((0.016, 0.014, 0.014)), "soot", 6, 3)
    mm.cyl(cc + V((0.05, 0, 0.018)), 0.005, 0.016, "iron_dark", axis=(1, 0, -0.2), segs=4, r2=0.0)
    mm.obox(cc + V((-0.04, 0, 0.004)), (0.03, 0.014, 0.004), "soot", rot=(0, 0.3, 0))
    for dy in (-0.006, 0.006):
        mm.beam(cc + V((0, dy, -0.012)), cc + V((0.004, dy, -0.03)), 0.003, "gold_dark")
    parts["pr_crow"] = A.part(mm.obj("pr_crow", coll), root, CROW_HOME)
    return root, bed, parts


CANDLES = [V((-0.98, -0.62, FLOOR)), V((-0.98, 0.6, FLOOR)), V((0.98, -0.02, FLOOR)), V((0.12, 1.02, FLOOR + 0.048)),
           V((-0.1, 1.03, FLOOR + 0.048)), V((0.95, 0.4, FLOOR))]
TUFTS = [V((-0.55, -1.15, FLOOR)), V((0.6, -1.1, FLOOR)), V((-1.2, -0.42, FLOOR)), V((1.22, 0.2, FLOOR)),
         V((0.42, 0.95, FLOOR)), V((-0.7, 0.85, FLOOR)), V((-0.25, 0.3, FLOOR)), V((0.3, -0.42, FLOOR))]
CROW_HOME = V((-1.08, -0.12, FLOOR + 0.11))                  # on top of the slab of the second grave on the left
CROW_HOP = V((0.0, -0.6, 0.17 + 0.065 - 0.11))               # over to the round stone in front of it, and back


def clips(parts):
    pats = J.tend_pats()

    def common(p):
        pose = {}
        for i in range(len(CANDLES)):
            fl = math.sin(TAU * (7 * p + 0.31 * i)) + 0.5 * math.sin(TAU * (11 * p + 0.17 * i))
            pose[f"pr_flame_{i + 1}"] = (None, A.q((1, 0.3 * i, 0), 9 * fl), (1, 1, 1 + 0.18 * math.sin(TAU * (9 * p + 0.2 * i))))
        for i in range(len(TUFTS)):
            pose[f"pr_tuft_{i + 1}"] = (None, A.q((1, 0.3, 0), 7 * math.sin(TAU * (2 * p + 0.13 * i))), None)
        for i in range(3):
            pose[f"pr_leaves_{i + 1}"] = (None, A.q((1, 0.5 * i, 0), 3 * math.sin(TAU * (p + 0.2 * i))), None)
        creak = 6 + 5 * math.sin(TAU * p) + 2 * math.sin(TAU * 5 * p) * math.exp(-((p - 0.35) ** 2) / 0.004)
        pose["pr_gate_1"] = (None, A.q((0, 0, 1), 18 + creak), None)                       # ajar, opening inward
        # crow: perched; pecks; hops to the next stone and back
        t1 = min(1.0, max(0.0, (p - 0.3) / 0.08))
        t2 = min(1.0, max(0.0, (p - 0.75) / 0.08))
        s = (3 * t1 ** 2 - 2 * t1 ** 3) - (3 * t2 ** 2 - 2 * t2 ** 3)
        arc = 0.08 * (math.sin(math.pi * t1) + math.sin(math.pi * t2))
        peck = sum(math.exp(-((p - c) ** 2) / 0.0008) for c in (0.12, 0.18, 0.55, 0.6))
        turn = 180 if 0.34 < p < 0.79 else 0
        pose["pr_crow"] = (CROW_HOP * s + V((0, 0, arc)), A.q((0, 0, 1), turn - 90) @ A.q((0, 1, 0), 35 * peck), None)
        return pose

    def idle(p):
        return common(p)

    def work(p):
        pose = common(p)
        w = sum(math.exp(-((((p * 2) % 1.0 - c) + 0.5) % 1.0 - 0.5) ** 2 / 0.002) for c in pats)   # tend is 48 fr
        pose["pr_flower"] = (None, A.q((1, 0.4, 0), 14 * w * math.sin(TAU * 12 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, bed, parts = build(coll, random.Random(13))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    for i, (pos, facing) in enumerate(MOURN):
        A.spot(root, f"spot_mourn_{i + 1}", pos, facing)
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(bed) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(bed)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "graveyard.blend"), relative_remap=True)
    A.export()
    rig, mesh, _ = A.raccoon_at(bpy.data.objects["spot_work"], clip="work_tend")
    crew = [(rig, mesh, None, "work", {"pr_bed": None, NAME: None, "pr_flower": None})]
    objs = [rig, mesh]
    for i in range(len(MOURN)):
        r2, m2, _ = A.raccoon_at(bpy.data.objects[f"spot_mourn_{i + 1}"], clip="work_mourn")
        crew.append((r2, m2, None, "work", {}))
        objs += [r2, m2]
    allow = [("pr_flower", NAME), ("pr_flower", "pr_bed"), ("pr_bed", NAME), ("pr_crow", NAME)] + \
            [(f"pr_flame_{i + 1}", NAME) for i in range(len(CANDLES))] + [(f"pr_tuft_{i + 1}", NAME) for i in range(len(TUFTS))] + \
            [(f"pr_leaves_{i + 1}", NAME) for i in range(3)] + [("pr_leaves_1", "pr_leaves_3"), ("pr_leaves_2", "pr_leaves_3"),
                                                               ("pr_leaves_1", "pr_leaves_2")] + \
            [(f"pr_gate_{i}", NAME) for i in (1, 2)]
    probs = A.check(root, 3, 3, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_graveyard_loops.gif",
                       target=(0.0, 0.0, 0.1), dist=5.2, pitch=44, idle_frames=48, grid_n=3, step=3)


if __name__ == "__main__":
    main()
