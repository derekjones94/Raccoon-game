"""bld_coin_fountain_2x2: a little fountain whose basin is lined with stolen coins. A decoration, and the colony's
big loot sink.

An octagonal stone basin on a flagstone pad, a ring of gold coins set into its inner wall and more coins shining in
the shallow water; a heap of coins round the foot of the fountain breaks the surface. Two stone bowls on a column,
and on top a fat gold money bag spouting water. Water spills from bowl to bowl to the basin. Flower bushes between
the seats.

Raccoons can sit on the rim (spot_seat_1 to _4, on the four diagonals, facing the water: their tails hang off the
back of the rim, their toes over the water) and play work_drink (with prop_mug) or work_chat, as at the patio bar.

Clips (24 fps)
  idle  48 fr  water spouts and trickles down (drops run down each stream), ripples spread where it lands, coins glint
  work  48 fr  the same: nothing in it waits on a raccoon; play work while anyone's sitting there

Run:  python3 tools/build_coin_fountain.py   (--no-renders)
Out:  coin_fountain.blend, export/bld_coin_fountain_2x2.glb, renders/bld_coin_fountain_loops.gif
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
NAME = "bld_coin_fountain_2x2"
FRAMES = 48
PAD = 0.01                                       # top of the flagstone pad
RO, RI, RIM = 0.76, 0.58, 0.1                    # the basin rim: outer and inner radius, top
WATER = 0.07
SEAT_R = 0.65                                    # the seats: on the rim, facing in; the seated body reaches 0.1 back
SEAT_ANGLES = (45, 135, 225, 315)                # diagonals: the tails hang off the rim toward the lot's corners
BOWL1 = (0.34, 0.24)                             # lower bowl: lip height, radius
BOWL2 = (0.52, 0.13)                             # upper bowl
BAG = V((0, 0, BOWL2[0] + 0.01))                 # the money bag's foot


def ring(m, r0, r1, z0, z1, n, sw, top):
    """A solid ring wall (an n-sided annulus) between radii r0 and r1: one closed shell, so no overlapping faces."""
    pts = [(math.cos(TAU * k / n), math.sin(TAU * k / n)) for k in range(n)]
    vs = {key: [m.bm.verts.new(V((r * c, r * s_, z))) for c, s_ in pts] for key, (r, z) in
          {"ib": (r0, z0), "ob": (r1, z0), "it": (r0, z1), "ot": (r1, z1)}.items()}
    fs_top, fs_side = [], []
    for k in range(n):
        j = (k + 1) % n
        fs_top.append(m.bm.faces.new((vs["it"][k], vs["ot"][k], vs["ot"][j], vs["it"][j])))
        fs_side.append(m.bm.faces.new((vs["ib"][k], vs["ib"][j], vs["ob"][j], vs["ob"][k])))
        fs_side.append(m.bm.faces.new((vs["ob"][k], vs["ob"][j], vs["ot"][j], vs["ot"][k])))
        fs_side.append(m.bm.faces.new((vs["ib"][k], vs["it"][k], vs["it"][j], vs["ib"][j])))
    m.tag(fs_top, top)
    m.tag(fs_side, sw)
    for k in range(n):                                                    # joints between the stones, on the outside
        a = TAU * (k + 0.5) / n
        m.obox(V(((r1 + 0.001) * math.cos(a), (r1 + 0.001) * math.sin(a), (z0 + z1) / 2)), (0.004, 0.006, z1 - z0 - 0.004),
               "stone_dark", rot=(0, 0, a))


def coin(m, c, r=0.02, sw="gold", axis=(0, 0, 1)):
    m.cyl(c, r, 0.005, sw, segs=6, axis=axis, cap="gold_light")


def build(coll, rnd):
    m = B.M()
    # ---- ground: grass, a round flagstone pad
    m.obox(V((0, 0, 0.002)), (1.94, 1.94, 0.004), "moss")
    m.cyl(V((0, 0, PAD / 2)), 0.94, PAD, "stone_mid", segs=16, cap="stone_light")
    for k in range(16):                                                                              # joints
        a = TAU * k / 16
        m.beam(V((RO * math.cos(a), RO * math.sin(a), PAD + 0.0005)), V((0.93 * math.cos(a), 0.93 * math.sin(a), PAD + 0.0005)),
               0.006, "stone_dark")
    # ---- the basin: rim wall with a coping, the water, coins set round the inner wall
    ring(m, RI, RO, PAD, RIM - 0.02, 16, "stone_mid", "stone_mid")
    ring(m, RI - 0.01, RO + 0.015, RIM - 0.02, RIM, 16, "stone_light", "stone_pale")
    m.cyl(V((0, 0, (PAD + WATER) / 2)), RI + 0.002, WATER - PAD, "water_deep", segs=16, cap="water")
    for k in range(20):
        a = TAU * (k + 0.5) / 20
        r = RI - 0.004
        coin(m, V((r * math.cos(a), r * math.sin(a), WATER + 0.016)), 0.013, axis=(math.cos(a), math.sin(a), 0))
    for _ in range(18):                                                                              # in the shallows
        a, r = rnd.uniform(0, TAU), rnd.uniform(0.3, RI - 0.05)
        m.cyl(V((r * math.cos(a), r * math.sin(a), WATER + 0.001)), rnd.uniform(0.014, 0.02), 0.002,
              rnd.choice(["gold", "gold", "gold_light", "silver"]), segs=6)
    # ---- the heap of coins round the column's foot
    for k in range(10):
        a, r = TAU * k / 10 + rnd.uniform(-0.1, 0.1), rnd.uniform(0.11, 0.22)
        m.blob(V((r * math.cos(a), r * math.sin(a), WATER - 0.01)), V((0.05, 0.05, 0.03 + 0.02 * (r < 0.16))), "gold_dark", 6, 3)
    for k in range(14):
        a, r = rnd.uniform(0, TAU), rnd.uniform(0.1, 0.24)
        h = WATER + 0.02 + 0.03 * (0.24 - r) / 0.14
        coin(m, V((r * math.cos(a), r * math.sin(a), h)), 0.02, rnd.choice(["gold", "gold_light"]),
             axis=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 1))
    m.blob(V((0.17, -0.08, WATER + 0.05)), V((0.025, 0.025, 0.02)), "ruby", 6, 3)                 # gems in it
    m.blob(V((-0.14, 0.12, WATER + 0.045)), V((0.022, 0.022, 0.02)), "sapphire", 6, 3)
    m.cyl(V((-0.05, -0.19, WATER + 0.05)), 0.03, 0.03, "silver", segs=8, axis=(0.3, -1, 0.3), r2=0.02)   # a cup
    # ---- the fountain: column, two bowls with water in them
    m.cyl(V((0, 0, (WATER + BOWL1[0]) / 2)), 0.07, BOWL1[0] - WATER, "stone_light", segs=8)
    m.cyl(V((0, 0, BOWL1[0] - 0.05)), 0.08, 0.04, "stone_mid", segs=8, r2=BOWL1[1])
    m.cyl(V((0, 0, BOWL1[0] - 0.012)), BOWL1[1], 0.024, "stone_pale", segs=12, cap="water")
    m.cyl(V((0, 0, (BOWL1[0] + BOWL2[0]) / 2)), 0.045, BOWL2[0] - BOWL1[0], "stone_light", segs=8)
    m.cyl(V((0, 0, BOWL2[0] - 0.04)), 0.05, 0.03, "stone_mid", segs=8, r2=BOWL2[1])
    m.cyl(V((0, 0, BOWL2[0] - 0.01)), BOWL2[1], 0.02, "stone_pale", segs=12, cap="water")
    for k in range(8):                                                                               # coins in bowl 1
        a = TAU * k / 8
        coin(m, V((0.15 * math.cos(a), 0.15 * math.sin(a), BOWL1[0] + 0.001)), 0.018)
    # ---- the money bag on top, spouting from its neck
    m.blob(BAG + V((0, 0, 0.06)), V((0.07, 0.07, 0.065)), "gold", 10, 5)
    m.cyl(BAG + V((0, 0, 0.125)), 0.03, 0.02, "gold_dark", segs=8)                                 # its tie
    m.cyl(BAG + V((0, 0, 0.145)), 0.024, 0.03, "gold", segs=8, r2=0.04)                            # the open neck
    m.obox(BAG + V((0, -0.07, 0.065)), (0.012, 0.004, 0.06), "gold_dark")                         # a coin sign on it
    m.obox(BAG + V((0, -0.07, 0.065)), (0.04, 0.004, 0.01), "gold_dark")
    # ---- flower bushes between the seats, and a "throw a coin" bucket
    for k in range(4):
        a = TAU * k / 4
        c = V((0.86 * math.cos(a), 0.86 * math.sin(a), 0.0))
        m.blob(c + V((0, 0, 0.06)), V((0.08, 0.08, 0.07)), "moss", 7, 4)
        for j in range(4):
            b = TAU * j / 4 + k
            m.blob(c + V((0.05 * math.cos(b), 0.05 * math.sin(b), 0.11)), V((0.016, 0.016, 0.014)),
                   ["cloth_red", "gold_light", "amethyst", "cloth_cream"][(j + k) % 4], 5, 3)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # water: the spout's jet, then streams from the bowls' lips: flat sheets of water spilling over the lip and
    # widening as they fall (never thin rods: those read as legs holding the bowls up), drops running down them
    for i, (top, bot, n) in enumerate(STREAMS):
        mm = B.M()
        top, bot = V(top), V(bot)
        if i == 0:                                                     # the jet: two crossed sheets, seen from all round
            sheet(mm, top, bot, 0.03, 0.05, V((1, 0, 0)), "stone_frost")
            sheet(mm, top, bot, 0.03, 0.05, V((0, 1, 0)), "stone_frost")
        else:                                                          # an arc pouring off the lip, out and down
            pts = arc(top, bot)
            for k in range(len(pts) - 1):
                sheet(mm, pts[k], pts[k + 1], 0.04 + 0.012 * k / len(pts), 0.04 + 0.012 * (k + 1) / len(pts), None,
                      "stone_frost" if k % 2 else "water")
        parts[f"pr_stream_{i + 1}"] = A.part(mm.obj(f"pr_stream_{i + 1}", coll), root, top)
        mm = B.M()
        pts = arc(top, bot) if i else [top + (bot - top) * t / n for t in range(n + 1)]
        for k in range(n):                                             # drops: highlights along the stream
            c = pts[int((k + 0.5) / n * (len(pts) - 1))]
            mm.blob(c, V((0.006, 0.006, 0.018)), "stone_frost", 8, 4)
        parts[f"pr_drops_{i + 1}"] = A.part(mm.obj(f"pr_drops_{i + 1}", coll), root, top)
    # ripples where the water lands
    for i, c in enumerate(RIPPLES):
        mm = B.M()
        c = V(c)
        for k in range(6):
            a0, a1 = TAU * k / 6, TAU * (k + 0.6) / 6
            mm.beam(c + V((0.05 * math.cos(a0), 0.05 * math.sin(a0), 0)), c + V((0.05 * math.cos(a1), 0.05 * math.sin(a1), 0)),
                    0.006, "stone_frost")
        parts[f"pr_ripple_{i + 1}"] = A.part(mm.obj(f"pr_ripple_{i + 1}", coll), root, c)
    # glints on the coins
    for i, c in enumerate(GLINTS):
        mm = B.M()
        c = V(c)
        mm.obox(c, (0.04, 0.003, 0.005), "flame_white")
        mm.obox(c, (0.005, 0.003, 0.04), "flame_white")
        mm.obox(c, (0.005, 0.04, 0.005), "flame_white")
        parts[f"pr_glint_{i + 1}"] = A.part(mm.obj(f"pr_glint_{i + 1}", coll), root, c)
    return root, parts


def arc(top, bot, n=6):
    """Points of water pouring off a lip at top and landing at bot: it leaves sideways and falls ever steeper."""
    return [V((top.x + (bot.x - top.x) * t, top.y + (bot.y - top.y) * t, top.z + (bot.z - top.z) * t * t))
            for t in (k / n for k in range(n + 1))]


def sheet(m, top, bot, w0, w1, side=None, swatch="water"):
    """A thin sheet of falling water from top to bot, w0 wide at the top and w1 at the bottom, both faces."""
    d = bot - top
    if side is None:
        side = V((0, 0, 1)).cross(V((d.x, d.y, 0))).normalized()
    n = side.cross(d).normalized() * 0.0015                            # a thin closed slab: seen from both sides
    q = [top - side * w0 / 2, top + side * w0 / 2, bot + side * w1 / 2, bot - side * w1 / 2]
    f = [m.bm.verts.new(v + n) for v in q]
    k = [m.bm.verts.new(v - n) for v in q]
    faces = [m.bm.faces.new(f), m.bm.faces.new(list(reversed(k)))]
    for i in range(4):
        j = (i + 1) % 4
        faces.append(m.bm.faces.new((f[i], k[i], k[j], f[j])))
    m.tag(faces, swatch)


def _streams():
    out = [((0, 0, BAG.z + 0.16), (0, 0, BAG.z + 0.24), 3)]                  # the jet, straight up out of the bag
    for k in range(4):                                                         # upper bowl to lower bowl
        a = TAU * k / 4 + TAU / 8
        out.append(((BOWL2[1] * math.cos(a), BOWL2[1] * math.sin(a), BOWL2[0]),
                    ((BOWL2[1] + 0.04) * math.cos(a), (BOWL2[1] + 0.04) * math.sin(a), BOWL1[0] + 0.002), 4))
    for k in range(6):                                                         # lower bowl to the basin
        a = TAU * k / 6
        out.append(((BOWL1[1] * math.cos(a), BOWL1[1] * math.sin(a), BOWL1[0]),
                    ((BOWL1[1] + 0.06) * math.cos(a), (BOWL1[1] + 0.06) * math.sin(a), WATER + 0.004), 5))
    return out


STREAMS = _streams()
RIPPLES = [tuple(V(s[1]) + V((0, 0, 0.002))) for s in STREAMS[5:]]
GLINTS = [(0.35, -0.3, WATER + 0.02), (-0.4, -0.2, WATER + 0.02), (0.1, -0.2, WATER + 0.08), (-0.2, 0.42, WATER + 0.02),
          (0.0, -RI + 0.02, WATER + 0.03), (0.0, -0.075, BAG.z + 0.1)]


def clips(parts):
    def pose(p):
        out = {}
        for i, (top, bot, n) in enumerate(STREAMS):
            d = (V(bot) - V(top)) / n
            k = (4 * p) % 1.0                                       # four drop-steps a loop: a steady flow
            out[f"pr_drops_{i + 1}"] = (None, None, 0.6 + 0.6 * abs(math.sin(TAU * (4 * p + 0.29 * i))))   # glitter
            out[f"pr_stream_{i + 1}"] = (None, None, (1 + 0.15 * math.sin(TAU * (6 * p + 0.3 * i)), 1, 1))
        for i in range(len(RIPPLES)):
            t = (2 * p + 0.37 * i) % 1.0
            s = 0.5 + 1.1 * t
            out[f"pr_ripple_{i + 1}"] = (None, None, (s, s, 1) if t < 0.85 else 0.001)
        k = len(GLINTS)
        for i in range(k):
            t = ((p - i / k) % 1.0) * k
            g = math.sin(math.pi * t / 0.7) if t < 0.7 else 0.0
            out[f"pr_glint_{i + 1}"] = (None, A.q((0, 0, 1), 40 * t), max(0.001, g))
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(77))
    for i, a in enumerate(SEAT_ANGLES):
        r = math.radians(a)
        A.spot(root, f"spot_seat_{i + 1}", V((SEAT_R * math.cos(r), SEAT_R * math.sin(r), RIM + 0.0015)),
               (-math.cos(r), -math.sin(r), 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "coin_fountain.blend"), relative_remap=True)
    A.export()
    crew, objs = [], []
    for i in range(len(SEAT_ANGLES)):
        drink = i % 2 == 0
        rig, mesh, mug = A.raccoon_at(bpy.data.objects[f"spot_seat_{i + 1}"], clip="work_drink" if drink else "work_chat",
                                      tool="prop_mug" if drink else None)
        crew.append((rig, mesh, mug, "work", {}))
        objs += [o for o in (rig, mesh, mug) if o]
    allow = [(n, NAME) for n in parts] + [(f"pr_drops_{i + 1}", f"pr_stream_{i + 1}") for i in range(len(STREAMS))] + \
            [(f"pr_ripple_{i + 1}", f"pr_stream_{i + 6}") for i in range(len(RIPPLES))]      # the water lands in its ripple
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_coin_fountain_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.6, pitch=40, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
