"""bld_mushroom_lamp_1x1: a tall glowing cave mushroom, the cave's own lantern. A decoration for the deep layers.

A thick pale stalk with a ring, leaning a little, rises from a mossy mound to a broad cap glowing from its gills,
its top freckled with glowing spots. Little glowing caps cluster round its foot; a flat stone, some pebbles.

Clips (24 fps)
  idle  96 fr  the glow swells and fades (the gills, the spots and the little caps breathe in turn), spores drift up
  work  96 fr  the same (decorations have no work of their own)

Run:  python3 tools/build_mushroom_lamp.py   (--no-renders)
Out:  mushroom_lamp.blend, export/bld_mushroom_lamp_1x1.glb, renders/bld_mushroom_lamp_loops.gif
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
NAME = "bld_mushroom_lamp_1x1"
FRAMES = 96
CAP = V((0.04, 0.03, 0.66))                      # the cap's underside centre
CAP_R = 0.24
SMALL = [(V((-0.2, -0.16, 0.0)), 0.06), (V((-0.27, 0.02, 0.0)), 0.045), (V((0.22, -0.2, 0.0)), 0.05),
         (V((0.25, 0.14, 0.0)), 0.035), (V((-0.1, 0.25, 0.0)), 0.04)]
SPOTS = [(0.0, 0.0), (0.6, 1.2), (0.65, 2.9), (0.55, 4.6), (0.38, 0.4), (0.4, 2.1), (0.42, 3.8), (0.68, 5.6), (0.66, 0.2),
         (0.36, 5.2)]


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "stone_deep")
    m.blob(V((0, 0, 0.0)), V((0.3, 0.28, 0.06)), "moss", 10, 4)
    m.cyl(V((0.28, -0.32, 0.012)), 0.08, 0.024, "stone_mid", segs=7, cap="stone_light")               # a flat stone
    for k in range(6):
        a = rnd.uniform(0, TAU)
        r = rnd.uniform(0.32, 0.42)
        m.blob(V((r * math.cos(a), r * math.sin(a), 0.01)), V((0.02, 0.018, 0.014)), "stone_light", 5, 3)
    # the stalk: three tapering pieces, leaning a little, with a skirt ring
    pts = [V((0, 0, 0.02)), V((0.01, 0.01, 0.25)), V((0.03, 0.02, 0.47)), CAP + V((0, 0, 0.01))]
    for a, b, r0, r1 in zip(pts, pts[1:], (0.07, 0.058, 0.05), (0.06, 0.05, 0.045)):
        m.cyl((a + b) / 2, r0, (b - a).length + 0.01, "bone", segs=8, axis=tuple(b - a), r2=r1)
    m.cyl(V((0.03, 0.02, 0.5)), 0.075, 0.02, "cloth_cream", segs=10, r2=0.055)                       # the ring
    m.blob(V((0, 0, 0.04)), V((0.09, 0.09, 0.05)), "bone", 8, 4)                                      # bulb at its foot
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # the cap (top) and the glowing gills under it: the gills swell, the cap barely breathes
    mm = B.M()
    mm.cyl(CAP + V((0, 0, 0.04)), CAP_R, 0.08, "teal_dark", segs=14, r2=CAP_R * 0.55)
    mm.blob(CAP + V((0, 0, 0.08)), V((CAP_R * 0.55, CAP_R * 0.55, 0.06)), "teal_dark", 12, 4)
    mm.cyl(CAP + V((0, 0, 0.002)), CAP_R + 0.004, 0.016, "amethyst", segs=14)                        # rim
    parts["pr_cap"] = A.part(mm.obj("pr_cap", coll), root, CAP)
    mm = B.M()
    mm.cyl(CAP + V((0, 0, -0.006)), CAP_R - 0.02, 0.012, "mushroom_glow", segs=14)
    mm.cyl(CAP + V((0, 0, 0.022)), CAP_R - 0.01, 0.026, "mushroom_glow", segs=14, r2=CAP_R * 0.86)   # the glowing band
    for k in range(14):                                                                                # gill lines
        a = TAU * k / 14
        mm.beam(CAP + V((0.06 * math.cos(a), 0.06 * math.sin(a), -0.014)),
                CAP + V(((CAP_R - 0.03) * math.cos(a), (CAP_R - 0.03) * math.sin(a), -0.014)), 0.006, "teal_light")
    parts["pr_gills"] = A.part(mm.obj("pr_gills", coll), root, CAP)
    # glowing spots on the cap
    for i, (rf, a) in enumerate(SPOTS):
        mm = B.M()
        r = rf * CAP_R * 0.85
        h = 0.08 + 0.06 * (1 - rf) ** 0.5 if rf < 0.5 else 0.08 - 0.06 * (rf - 0.5)
        c = CAP + V((r * math.cos(a), r * math.sin(a), h + 0.01))
        mm.blob(c, V((0.03, 0.03, 0.014)), "mushroom_glow", 6, 3)
        parts[f"pr_spot_{i + 1}"] = A.part(mm.obj(f"pr_spot_{i + 1}", coll), root, c)
    # the little glowing caps round the foot
    for i, (c, s) in enumerate(SMALL):
        mm = B.M()
        mm.cyl(c + V((0, 0, s * 0.7)), s * 0.22, s * 1.4, "bone", segs=6, r2=s * 0.18)
        mm.cyl(c + V((0, 0, s * 1.45)), s, s * 0.35, "mushroom_glow", segs=8, r2=s * 0.45, cap="mushroom_glow")
        parts[f"pr_small_{i + 1}"] = A.part(mm.obj(f"pr_small_{i + 1}", coll), root, c)
    # spores drifting up round the cap
    for i in range(SPORES):
        mm = B.M()
        a = TAU * i / SPORES + 0.3
        c = CAP + V((0.18 * math.cos(a), 0.18 * math.sin(a), -0.08))
        mm.obox(c, (0.008, 0.008, 0.008), "mushroom_glow", rot=(0.5, 0.3 * i, 0.2))
        parts[f"pr_spore_{i + 1}"] = A.part(mm.obj(f"pr_spore_{i + 1}", coll), root, c)
    return root, parts


SPORES = 6


def clips(parts):
    def pose(p):
        out = {}
        g = math.sin(TAU * p)                                                     # one slow breath a loop
        out["pr_gills"] = (None, None, (1 + 0.04 * g, 1 + 0.04 * g, 1 + 0.8 * (g + 1) / 2))
        out["pr_cap"] = (None, A.q((1, 0.4, 0), 1.2 * math.sin(TAU * p + 0.6)), (1 + 0.015 * g, 1 + 0.015 * g, 1))
        for i in range(len(SPOTS)):
            s = 0.75 + 0.35 * (math.sin(TAU * (p - 0.12 * i)) + 1) / 2
            out[f"pr_spot_{i + 1}"] = (None, None, s)
        for i in range(len(SMALL)):
            s = 0.92 + 0.1 * math.sin(TAU * (p - 0.5 - 0.15 * i))
            out[f"pr_small_{i + 1}"] = (None, None, (1, 1, s))
        for i in range(SPORES):
            t = (2 * p + i / SPORES) % 1.0                                         # rise and fade, two a loop each
            a = TAU * i / SPORES + 0.3
            out[f"pr_spore_{i + 1}"] = (V((0.06 * t * math.cos(a), 0.06 * t * math.sin(a), 0.45 * t + 0.02 * math.sin(TAU * 3 * t))),
                                        A.q((0, 0, 1), 200 * t), max(0.001, math.sin(math.pi * t)))
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(41))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "mushroom_lamp.blend"), relative_remap=True)
    A.export()
    allow = [(n, NAME) for n in parts] + [("pr_cap", "pr_gills")] + [(f"pr_spot_{i + 1}", "pr_cap") for i in range(len(SPOTS))] + \
            [(f"pr_spore_{i + 1}", o) for i in range(SPORES) for o in ["pr_cap", "pr_gills"] + [f"pr_spot_{j + 1}" for j in range(len(SPOTS))]]
    probs = A.check(root, 1, 1, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [], ROOT / "renders" / "bld_mushroom_lamp_loops.gif",
                       target=(0.0, 0.0, 0.4), dist=1.9, pitch=32, grid_n=3, step=3, idle_only=True)


if __name__ == "__main__":
    main()
