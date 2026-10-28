"""bld_bottlecap_banner_1x1: a string of bottle caps and spoons strung between two sticks. A cheap decoration
(scrap iron).

Two crooked sticks pushed into a heap of stones, a twine strung between them in two sags, and hanging from it bottle
caps (red, gold, silver, blue, crimped edges), a few bent spoons and a fork, and a little tin star in the middle.

Clips (24 fps)
  idle  48 fr  the caps and spoons jingle in a breeze: each swings and spins on its thread, to its own beat
  work  48 fr  the same (decorations have no work of their own)

Run:  python3 tools/build_bottlecap_banner.py   (--no-renders)
Out:  bottlecap_banner.blend, export/bld_bottlecap_banner_1x1.glb, renders/bld_bottlecap_banner_loops.gif
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
NAME = "bld_bottlecap_banner_1x1"
FRAMES = 48
STICK_X, STICK_H = 0.36, 0.56
STRINGS = [(STICK_H - 0.03, 0.09), (STICK_H - 0.2, 0.06)]   # each twine: height at the sticks, sag
CAPS = ["cloth_red", "gold", "silver", "sapphire", "cloth_red", "gold", "teal", "silver"]


def twine_at(x, row):
    h, sag = STRINGS[row]
    t = x / STICK_X
    return h - sag * (1 - t * t)


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "wood_weathered")
    for sx in (-1, 1):
        x = sx * STICK_X
        a, b = V((x - sx * 0.02, 0, 0.0)), V((x, 0.01, STICK_H))
        m.beam(a, (a + b) / 2 + V((sx * 0.01, 0, 0)), 0.024, "wood_bark")
        m.beam((a + b) / 2 + V((sx * 0.01, 0, 0)), b, 0.022, "wood_bark")
        m.beam(b + V((0, 0, -0.08)), b + V((sx * 0.06, 0, 0.0)), 0.012, "wood_bark")         # a twig
        for k in range(5):
            an = TAU * k / 5
            m.blob(V((x + 0.06 * math.cos(an), 0.06 * math.sin(an), 0.02)), V((0.04, 0.035, 0.03)),
                   "stone_mid" if k % 2 else "stone_light", 5, 3)
    for row in range(2):
        prev = None
        for k in range(17):
            x = -STICK_X + 2 * STICK_X * k / 16
            p = V((x, 0.0, twine_at(x, row)))
            if prev is not None:
                m.beam(prev, p, 0.004, "rope")
            prev = p
    m.cyl(V((0.25, -0.22, 0.012)), 0.05, 0.024, "rope", segs=8, cap="rope_dark")                # spare twine
    for k in range(3):                                                                            # loose caps
        m.cyl(V((-0.2 + 0.07 * k, -0.25 - 0.03 * k, 0.006)), 0.022, 0.008, "iron_light", segs=8, cap=CAPS[k])
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    i = 0
    for row, n in ((0, 7), (1, 6)):
        for k in range(n):
            x = -STICK_X + 2 * STICK_X * (k + 1) / (n + 1)
            hook = V((x, 0.0, twine_at(x, row) - 0.003))
            mm = B.M()
            kind = "star" if (row == 0 and k == 3) else ("spoon" if (k + row) % 3 == 2 else "cap")
            L = 0.03 + 0.012 * ((k + row) % 2)
            mm.beam(hook, hook + V((0, 0, -L)), 0.002, "rope")
            c = hook + V((0, 0, -L - 0.02))
            if kind == "cap":
                mm.cyl(c, 0.025, 0.007, "iron_light", segs=10, axis=(0, 1, 0), cap=CAPS[i % len(CAPS)])   # crimped rim, painted face
                mm.cyl(c + V((0, -0.004, 0)), 0.013, 0.002, "cloth_cream" if i % 2 else "gold_light", segs=6, axis=(0, 1, 0))
            elif kind == "spoon":
                mm.beam(c + V((0, 0, 0.02)), c + V((0, 0, -0.04)), 0.005, "silver" if i % 2 else "pewter")
                mm.blob(c + V((0, 0, -0.055)), V((0.013, 0.005, 0.02)), "silver" if i % 2 else "pewter", 6, 3)
            else:
                for a in range(5):
                    an = TAU * a / 5 + math.pi / 2
                    mm.beam(c, c + V((0.03 * math.cos(an), 0, 0.03 * math.sin(an))), 0.012, "gold_light")
            parts[f"pr_charm_{i + 1}"] = A.part(mm.obj(f"pr_charm_{i + 1}", coll), root, hook)
            i += 1
    return root, parts


def clips(parts):
    n = len(parts)

    def pose(p):
        out = {}
        for i in range(n):
            gust = 1 + 0.6 * math.sin(TAU * p)                                    # a breeze that comes and goes
            sw = 14 * gust * math.sin(TAU * (2 * p + 0.11 * i))                   # swings on its thread
            spin = 30 * gust * math.sin(TAU * (3 * p + 0.23 * i))                 # and twists, catching the light
            out[f"pr_charm_{i + 1}"] = (None, A.q((1, 0, 0), sw) @ A.q((0, 0, 1), spin), None)
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(8))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "bottlecap_banner.blend"), relative_remap=True)
    A.export()
    probs = A.check(root, 1, 1, allow=[(n, NAME) for n in parts])
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [], ROOT / "renders" / "bld_bottlecap_banner_loops.gif",
                       target=(0.0, 0.0, 0.3), dist=1.5, pitch=22, grid_n=3, step=2, idle_only=True)


if __name__ == "__main__":
    main()
