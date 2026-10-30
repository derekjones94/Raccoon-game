"""bld_goblet_planter_1x1: a stolen silver goblet, big as a raccoon, with a fern growing out of it. A decoration.

A chased silver goblet (foot, knopped stem, a wide cup with a gold band and a few gems set in it) stands on a low
stone plinth. The cup is full of dark soil, and a fern spills out of it; ivy trails over one side. A few coins and a
silver spoon lie round the plinth.

Clips (24 fps)
  idle  96 fr  the fern's fronds sway, each a little behind the one before, like a breeze passing
  work  96 fr  the same (decorations have no work of their own; both clips exist so every building plays alike)

Run:  python3 tools/build_goblet_planter.py   (--no-renders)
Out:  goblet_planter.blend, export/bld_goblet_planter_1x1.glb, renders/bld_goblet_planter_loops.gif
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

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_goblet_planter_1x1"
FRAMES = 96
PLINTH = 0.06                                    # top of the plinth
CUP_Z, CUP_R = PLINTH + 0.38, 0.14               # the cup's rim height and radius
SOIL = CUP_Z - 0.02


def frond(m, base, ang, length, lift, rnd):
    """A fern frond from `base`, heading out at `ang` (radians round Z), arching up then over: a blade of leaflets,
    one flat triangle each side per step, wide near the base and narrowing to the tip (both faces, so no back-face
    holes from below)."""
    d = V((math.cos(ang), math.sin(ang), 0))
    side = V((-d.y, d.x, 0))
    n = 8
    spine = [base + d * (length * k / n) + V((0, 0, lift * math.sin(math.pi * 0.85 * k / n) - 0.07 * (k / n) ** 2))
             for k in range(n + 1)]
    for k in range(n):
        a, b = spine[k], spine[k + 1]
        w = 0.05 * (1 - k / n) ** 0.7 + 0.008
        for s in (-1, 1):
            tip = (a + b) / 2 + side * (s * w) + (b - a) * 0.6 + V((0, 0, -0.012))
            sw = "moss_light" if (k + (s > 0)) % 2 else "moss"
            for want in (V((0, 0, 1)), V((0, 0, -1))):
                m.face([m.bm.verts.new(v) for v in (a, tip, b)], want, sw)


def build(coll, rnd):
    m = B.M()
    # ---- plinth and the scatter round it
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "moss")                                         # grass
    m.cyl(V((0, 0, PLINTH / 2)), 0.22, PLINTH, "stone_mid", segs=8, cap="stone_light")
    m.cyl(V((0, 0, 0.006)), 0.25, 0.012, "stone_dark", segs=8)
    for k, (x, y) in enumerate(((-0.3, -0.18), (-0.26, -0.24), (0.28, -0.26), (0.31, 0.2), (-0.12, -0.33))):
        m.cyl(V((x, y, 0.0072 + 0.0062 * (k == 1))), 0.022, 0.006, "gold", segs=8, cap="gold_light")
    m.beam(V((0.18, -0.3, 0.0072)), V((0.3, -0.36, 0.0072)), 0.006, "silver")                     # a spoon
    m.blob(V((0.33, -0.375, 0.0092)), V((0.022, 0.016, 0.005)), "silver", 8, 3)
    # ---- the goblet: foot, stem with a knop, a tall bowl flaring to the rim
    m.cyl(V((0, 0, PLINTH + 0.012)), 0.12, 0.024, "silver", segs=12, r2=0.09)
    m.cyl(V((0, 0, PLINTH + 0.032)), 0.06, 0.016, "pewter", segs=10, r2=0.03)
    m.cyl(V((0, 0, PLINTH + 0.075)), 0.024, 0.07, "silver", segs=8, r2=0.02)
    m.blob(V((0, 0, PLINTH + 0.115)), V((0.04, 0.04, 0.026)), "silver", 10, 4)                    # knop
    m.cyl(V((0, 0, PLINTH + 0.145)), 0.02, 0.04, "silver", segs=8, r2=0.035)
    z0 = PLINTH + 0.165
    for r0, r1, za, zb in ((0.035, 0.1, z0, z0 + 0.06), (0.1, 0.128, z0 + 0.06, z0 + 0.14), (0.128, CUP_R, z0 + 0.14, CUP_Z)):
        m.cyl(V((0, 0, (za + zb) / 2)), r0, zb - za, "silver", segs=12, r2=r1)
    m.cyl(V((0, 0, CUP_Z - 0.004)), CUP_R + 0.006, 0.012, "pewter", segs=12)                      # rim
    m.cyl(V((0, 0, CUP_Z - 0.05)), 0.138, 0.024, "gold", segs=12)                                # gold band
    for k in range(4):                                                                              # gems in the band
        a = TAU * k / 4 + 0.4
        m.blob(V((0.141 * math.cos(a), 0.141 * math.sin(a), CUP_Z - 0.05)), V((0.014, 0.014, 0.012)),
               ["ruby", "sapphire", "emerald", "amethyst"][k], 6, 3)
    m.cyl(V((0, 0, SOIL - 0.005)), CUP_R - 0.006, 0.014, "fur_dark", segs=12)                     # soil
    # ---- ivy trailing over the front-right of the rim and down the cup
    a = -0.6
    p0 = V((CUP_R * math.cos(a), CUP_R * math.sin(a), CUP_Z))
    pts = [p0, p0 + V((0.03 * math.cos(a), 0.03 * math.sin(a), -0.06)), p0 + V((0.025 * math.cos(a), 0.02 * math.sin(a), -0.16)),
           p0 + V((0.0, -0.01, -0.22))]
    side = 1
    for q0, q1 in zip(pts, pts[1:]):
        m.beam(q0, q1, 0.004, "moss")
        for t in (0.3, 0.65, 1.0):                                  # leaves along the vine, alternating sides: flat
            c = q0.lerp(q1, t)                                      # diamonds facing out, not beads
            tang = V((-math.sin(a), math.cos(a), 0)) * side * 0.012
            m.obox(c + tang, (0.024, 0.004, 0.024), "moss_light" if side > 0 else "moss",
                   rot=(0, math.radians(45), a + math.pi / 2))
            side = -side
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    base = V((0, 0, SOIL))
    for i in range(FRONDS):
        mm = DEN.DenMesh()
        ang = TAU * i / FRONDS + rnd.uniform(-0.2, 0.2)
        frond(mm, base + V((0.02 * math.cos(ang), 0.02 * math.sin(ang), 0)), ang, rnd.uniform(0.24, 0.32),
              rnd.uniform(0.1, 0.2) if i % 2 else rnd.uniform(0.2, 0.26), rnd)
        parts[f"pr_frond_{i + 1}"] = A.part(mm.obj(f"pr_frond_{i + 1}", coll), root, base)
    mm = B.M()                                                                                     # the fern's heart:
    for k in range(3):                                                                             # young fiddleheads
        a = TAU * k / 3
        c = base + V((0.012 * math.cos(a), 0.012 * math.sin(a), 0.05))
        mm.beam(base, c, 0.005, "moss_light")
        mm.blob(c + V((0, 0, 0.008)), V((0.01, 0.01, 0.01)), "moss_light", 5, 3)
    parts["pr_frond_heart"] = A.part(mm.obj("pr_frond_heart", coll), root, base)
    return root, parts


FRONDS = 9


def clips(parts):
    def pose(p):
        out = {}
        for i in range(FRONDS):
            ang = TAU * i / FRONDS
            axis = (-math.sin(ang), math.cos(ang), 0)                    # tip the frond up and down along its length
            nod = 5 * math.sin(TAU * (p - 0.06 * i)) + 2 * math.sin(TAU * (3 * p + 0.3 * i))
            out[f"pr_frond_{i + 1}"] = (None, A.q(axis, nod) @ A.q((0, 0, 1), 3 * math.sin(TAU * (2 * p + 0.15 * i))), None)
        out["pr_frond_heart"] = (None, A.q((1, 0.3, 0), 3 * math.sin(TAU * p)), None)
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(3))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "goblet_planter.blend"), relative_remap=True)
    A.export()
    allow = [(n, NAME) for n in parts] + [(a, b) for a in parts for b in parts if a < b]   # fronds overlap at the heart
    probs = A.check(root, 1, 1, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [], ROOT / "renders" / "bld_goblet_planter_loops.gif",
                       target=(0.0, 0.0, 0.25), dist=1.7, pitch=36, grid_n=3, step=3, idle_only=True)


if __name__ == "__main__":
    main()
