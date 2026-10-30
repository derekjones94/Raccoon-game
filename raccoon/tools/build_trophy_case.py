"""bld_trophy_case_1x1: a glass case on legs, for showing off one stolen relic. A decoration.

A little dark-wood stand on turned legs, a brass plaque on its front; on it a glass case with brass edges and a
pointed lid (the glass itself isn't modelled: it would hide the relic). Inside, a red velvet cushion on a turning plinth, and
the relic on the cushion.

There is one child node per relic: `pr_relic_caravan_bell` (a brass caravan bell on a red ribbon) and
`pr_relic_duke_signet` (the Duke's gold signet ring with its ruby). Both are in the file and both play the same
motion; the game shows the one the colony owns and hides the other(s). More relics can be added the same way.

Clips (24 fps)
  idle  96 fr  a slow sparkle: the cushion and relic turn slowly round, sparkles wink on and off round the relic
  work  96 fr  the same (decorations have no work of their own)

Run:  python3 tools/build_trophy_case.py   (--no-renders)
Out:  trophy_case.blend, export/bld_trophy_case_1x1.glb, renders/bld_trophy_case_loops.gif
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
NAME = "bld_trophy_case_1x1"
FRAMES = 96
TOP = 0.3                                        # the stand's top
RELIC_SCALE = 1.8
CASE = (0.17, 0.14, 0.3)                         # the case: half width, half depth, height
CUSHION = V((0.0, 0.0, TOP + 0.11))              # the cushion's top centre: the relic sits here


def grow(ob, k=RELIC_SCALE):
    """Relics are modelled at true size, then shown bigger: scaled about their pivot (the cushion top)."""
    from mathutils import Matrix
    ob.data.transform(Matrix.Scale(k, 4))
    return ob


def build(coll, rnd):
    m = B.M()
    hw, hd, h = CASE
    # ---- the stand: top, apron, turned legs, a shelf, the plaque
    m.obox(V((0, 0, TOP - 0.012)), (2 * hw + 0.08, 2 * hd + 0.08, 0.024), "wood_dark", top="wood_mid")
    m.obox(V((0, 0, TOP - 0.045)), (2 * hw + 0.03, 2 * hd + 0.03, 0.045), "wood_dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = V((sx * hw, sy * hd, 0))
            m.cyl(c + V((0, 0, 0.13)), 0.018, 0.2, "wood_dark", segs=6, r2=0.013)
            m.blob(c + V((0, 0, 0.235)), V((0.024, 0.024, 0.02)), "wood_mid", 6, 3)
            m.blob(c + V((0, 0, 0.03)), V((0.022, 0.022, 0.02)), "wood_mid", 6, 3)
            m.cyl(c + V((0, 0, 0.006)), 0.022, 0.012, "gold_dark", segs=6)                       # brass feet
    m.obox(V((0, 0, 0.08)), (2 * hw, 2 * hd, 0.014), "wood_mid")                                 # low shelf
    m.obox(V((0, -hd - 0.026, TOP - 0.045)), (0.12, 0.004, 0.032), "gold")                       # the plaque
    m.obox(V((0, -hd - 0.029, TOP - 0.045)), (0.08, 0.003, 0.006), "gold_dark")
    # on the shelf: a folded cloth and a polishing tin
    m.obox(V((-0.06, 0.02, 0.095)), (0.12, 0.08, 0.016), "cloth_red")
    m.cyl(V((0.08, 0.0, 0.098)), 0.03, 0.02, "pewter", segs=8, cap="iron")
    # ---- the case: brass edges, a base plate, a pointed lid with a finial; glass shown as light streaks
    z0, z1 = TOP, TOP + h
    m.obox(V((0, 0, z0 + 0.01)), (2 * hw + 0.02, 2 * hd + 0.02, 0.02), "gold_dark", top="wood_dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.obox(V((sx * hw, sy * hd, (z0 + z1) / 2)), (0.01, 0.01, h), "gold_dark")
    for z in (z0 + 0.02, z1):
        for sy in (-1, 1):
            m.obox(V((0, sy * hd, z)), (2 * hw, 0.01, 0.01), "gold_dark")
        for sx in (-1, 1):
            m.obox(V((sx * hw, 0, z)), (0.01, 2 * hd, 0.01), "gold_dark")
    apex = V((0, 0, z1 + 0.09))
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.beam(V((sx * hw, sy * hd, z1)), apex, 0.009, "gold_dark")
    m.blob(apex + V((0, 0, 0.018)), V((0.02, 0.02, 0.022)), "gold_light", 6, 4)                 # finial
    m.blob(apex + V((0, 0, 0.045)), V((0.01, 0.01, 0.012)), "ruby", 5, 3)
    # ---- a velvet rope on two brass posts in front
    for x in (-0.3, 0.3):
        m.cyl(V((x, -0.32, 0.11)), 0.012, 0.22, "gold", segs=6)
        m.cyl(V((x, -0.32, 0.01)), 0.04, 0.02, "gold_dark", segs=8)
        m.blob(V((x, -0.32, 0.23)), V((0.018, 0.018, 0.018)), "gold_light", 6, 3)
    prev = None
    for k in range(9):
        t = k / 8
        pt = V((-0.3 + 0.6 * t, -0.32, 0.2 - 0.07 * math.sin(math.pi * t)))
        if prev is not None:
            m.beam(prev, pt, 0.012, "cloth_red")
        prev = pt
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # the turning plinth and cushion
    mm = B.M()
    mm.cyl(V((0, 0, TOP + 0.028)), 0.06, 0.016, "gold_dark", segs=10, cap="gold")
    mm.cyl(V((0, 0, TOP + 0.06)), 0.03, 0.05, "wood_dark", segs=8, r2=0.022)                        # the pedestal
    mm.cyl(V((0, 0, CUSHION.z - 0.024)), 0.05, 0.012, "gold_dark", segs=10)
    mm.obox(CUSHION + V((0, 0, -0.008)), (0.15, 0.15, 0.022), "cloth_red", top="cloth_red")
    for sx in (-1, 1):
        for sy in (-1, 1):
            mm.blob(CUSHION + V((sx * 0.075, sy * 0.075, -0.008)), V((0.01, 0.01, 0.01)), "gold", 4, 3)   # tassels
    parts["pr_cushion"] = A.part(mm.obj("pr_cushion", coll), root, V((0, 0, TOP + 0.02)))
    # relic 1: the Caravan Bell, on a ribbon, mouth down
    mm = B.M()
    c = CUSHION + V((0, 0, 0.002))
    mm.cyl(c + V((0, 0, 0.03)), 0.04, 0.05, "gold", segs=10, r2=0.026, cap="gold_dark")
    mm.cyl(c + V((0, 0, 0.004)), 0.043, 0.008, "gold_light", segs=10)
    mm.cyl(c + V((0, 0, 0.002)), 0.034, 0.004, "soot", segs=10)
    mm.cyl(c + V((0, 0, 0.065)), 0.012, 0.022, "gold_dark", segs=6, axis=(1, 0, 0))             # its loop
    mm.cyl(c + V((0, 0, 0.032)), 0.039, 0.01, "gold_dark", segs=10)
    for s in (-1, 1):                                                                           # the red ribbon
        mm.obox(c + V((0.0, s * 0.03, 0.07)), (0.012, 0.05, 0.004), "cloth_red", rot=(s * 0.5, 0, 0))
        mm.obox(c + V((s * 0.02, -0.03, 0.03)), (0.01, 0.004, 0.05), "cloth_red", rot=(0, s * 0.3, 0))
    parts["pr_relic_caravan_bell"] = grow(A.part(mm.obj("pr_relic_caravan_bell", coll), root, c))
    # relic 2: the Duke's Signet, standing in a slot in the cushion
    mm = B.M()
    rc = CUSHION + V((0, 0, 0.034))
    n = 12
    for k in range(n):                                                                          # the band
        a0, a1 = TAU * k / n, TAU * (k + 1) / n
        mm.beam(rc + V((0.032 * math.cos(a0), 0, 0.032 * math.sin(a0))), rc + V((0.032 * math.cos(a1), 0, 0.032 * math.sin(a1))),
                0.011, "gold")
    mm.obox(rc + V((0, 0, 0.036)), (0.03, 0.026, 0.014), "gold_light")                           # the bezel
    mm.blob(rc + V((0, 0, 0.047)), V((0.012, 0.011, 0.009)), "ruby", 6, 3)
    mm.obox(rc + V((0, -0.0135, 0.036)), (0.016, 0.002, 0.008), "gold_dark")                     # the duke's crest
    parts["pr_relic_duke_signet"] = grow(A.part(mm.obj("pr_relic_duke_signet", coll), root, CUSHION))
    # sparkles: four-point stars winking on the brass edges and the finial (not loose in the air)
    for i, d in enumerate(SPARKLES):
        mm = B.M()
        c = V(d)
        mm.obox(c, (0.03, 0.002, 0.004), "flame_white")
        mm.obox(c, (0.004, 0.002, 0.03), "flame_white")
        parts[f"pr_sparkle_{i + 1}"] = A.part(mm.obj(f"pr_sparkle_{i + 1}", coll), root, c)
    return root, parts


SPARKLES = [(-CASE[0], -CASE[1] - 0.008, TOP + CASE[2]), (CASE[0], -CASE[1] - 0.008, TOP + 0.02),   # on the brass edges,
            (0.0, -0.026, TOP + CASE[2] + 0.108), (CASE[0], -CASE[1] - 0.008, TOP + CASE[2])]      # and the finial


def clips(parts):
    def pose(p):
        out = {}
        turn = A.q((0, 0, 1), 360 * p)
        out["pr_cushion"] = (None, turn, None)
        bob = V((0, 0, 0.004 * math.sin(TAU * 2 * p)))
        for n in ("pr_relic_caravan_bell", "pr_relic_duke_signet"):
            out[n] = (bob, turn, None)
        k = len(SPARKLES)
        for i in range(k):
            t = ((p - i / k - 0.1) % 1.0) * k
            g = math.sin(math.pi * t / 0.7) if t < 0.7 else 0.0
            out[f"pr_sparkle_{i + 1}"] = (None, A.q((0, 1, 0), 45 * t), max(0.001, g))        # spins in its own plane
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(5))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "trophy_case.blend"), relative_remap=True)
    A.export()
    allow = [(n, NAME) for n in parts if n.startswith("pr_sparkle")] + \
            [("pr_relic_caravan_bell", "pr_relic_duke_signet"), ("pr_relic_caravan_bell", "pr_cushion"),
             ("pr_relic_duke_signet", "pr_cushion"), ("pr_cushion", NAME)] + \
            [(f"pr_sparkle_{i + 1}", r) for i in range(len(SPARKLES)) for r in ("pr_relic_caravan_bell", "pr_relic_duke_signet", "pr_cushion")]
    probs = A.check(root, 1, 1, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        bpy.data.objects["pr_relic_duke_signet"].hide_render = True          # the GIF shows one relic, as the game does
        A.render_loops(root, [], ROOT / "renders" / "bld_trophy_case_loops.gif",
                       target=(0.0, 0.0, 0.35), dist=1.6, pitch=30, grid_n=3, step=3, idle_only=True)


if __name__ == "__main__":
    main()
