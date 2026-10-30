"""bld_mirror_mosaic_1x1: a standing panel of mirror shards and bottle glass. A decoration.

An arched plank panel on two feet, propped from behind, its face set with broken mirror and bits of bottle glass
(green, blue, amber, violet) in a rough sunburst round a round mirror in the middle. A twisted wire frame edges it; a
string of beads and a silver spoon hang from one shoulder.

Clips (24 fps)
  idle  96 fr  glints catch the light: little stars flash on the shards one after another; the spoon charm swings
  work  96 fr  the same (decorations have no work of their own)

Run:  python3 tools/build_mirror_mosaic.py   (--no-renders)
Out:  mirror_mosaic.blend, export/bld_mirror_mosaic_1x1.glb, renders/bld_mirror_mosaic_loops.gif
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
NAME = "bld_mirror_mosaic_1x1"
FRAMES = 96
PY = 0.04                                        # the panel's front face (it faces -Y, the game camera)
HALF_W, Z0, Z1 = 0.25, 0.1, 0.5                  # the panel: half width, bottom, where the arch starts
ARCH = 0.25                                      # the arch's radius (a half circle on top)
CENTRE = V((0.0, 0.0, 0.42))                     # the round mirror in the middle of the sunburst
GLASS = ["emerald", "sapphire", "gold_light", "amethyst", "teal_light", "ruby"]
MIRROR = ["silver", "stone_frost", "pewter", "silver"]


def outline(inset=0.0):
    """The panel's outline in XZ, counter-clockwise seen from the front."""
    w = HALF_W - inset
    pts = [(-w, Z0 + inset), (w, Z0 + inset)]
    for k in range(13):
        a = math.pi * k / 12
        pts.append((w * math.cos(a), Z1 + w * math.sin(a)))
    return pts[:2] + pts[3:-1] + [(-w, Z1)]


def inside(x, z, inset):
    w = HALF_W - inset
    if z < Z0 + inset or abs(x) > w:
        return False
    return z <= Z1 or x * x + (z - Z1) ** 2 <= w * w


def shard(m, c, r, n, sw, rnd, y):
    """A flat broken piece on the panel's face: an irregular polygon round c (XZ)."""
    a0 = rnd.uniform(0, TAU)
    vs = []
    for k in range(n):
        a = a0 + TAU * k / n + rnd.uniform(-0.3, 0.3)
        rr = r * rnd.uniform(0.6, 1.0)
        vs.append(m.bm.verts.new(V((c[0] + rr * math.cos(a), y, c[1] + rr * math.sin(a)))))
    m.face(vs, V((0, -1, 0)), sw)


def build(coll, rnd):
    m = B.M()
    # ---- the panel: a plank board with an arched top, feet and a back prop
    m.poly_prism(outline(), PY, PY + 0.03, "wood_mid")
    for x in (-0.16, 0.16):
        m.obox(V((x, PY + 0.015, 0.035)), (0.06, 0.2, 0.07), "wood_dark", top="wood_mid")             # feet
        m.obox(V((x, PY + 0.015, 0.09)), (0.03, 0.03, 0.05), "wood_dark")
    m.beam(V((0, PY + 0.03, 0.5)), V((0, PY + 0.2, 0.0)), 0.024, "wood_dark")                         # back prop
    m.beam(V((-0.14, PY + 0.1, 0.03)), V((0.14, PY + 0.1, 0.03)), 0.018, "wood_dark")
    pts = outline(0.004)                                                                               # wire frame
    for (xa, za), (xb, zb) in zip(pts, pts[1:] + pts[:1]):
        m.beam(V((xa, PY - 0.006, za)), V((xb, PY - 0.006, zb)), 0.012, "copper")
    m.cyl(V((CENTRE.x, PY - 0.003, CENTRE.z)), 0.085, 0.004, "gold", axis=(0, 1, 0), segs=12)    # the mirror's gilt rim
    # ---- the face (its own flat pieces, built facing the front): a round mirror in the middle, rays of glass, shards
    face = DEN.DenMesh()
    m, solid = face, m
    y = PY - 0.006
    rings = 12
    cv = [m.bm.verts.new(V((CENTRE.x + 0.075 * math.cos(TAU * k / rings), y - 0.002, CENTRE.z + 0.075 * math.sin(TAU * k / rings))))
          for k in range(rings)]
    m.face(cv, V((0, -1, 0)), "silver")
    for k in range(12):                                                                                # sunburst rays
        a = TAU * k / 12 + 0.13
        for j, d in enumerate((0.12, 0.17, 0.22, 0.27)):
            x, z = CENTRE.x + d * math.cos(a), CENTRE.z + d * math.sin(a)
            if inside(x, z, 0.03):
                sw = GLASS[(k + j) % len(GLASS)] if k % 2 == 0 else MIRROR[(k + j) % len(MIRROR)]
                shard(m, (x, z), 0.028 - 0.002 * j, 4 + (j % 2), sw, rnd, y)
    step = 0.034                                                                                       # fill the gaps:
    for i in range(int(2 * HALF_W / step) + 1):                                                        # a jittered grid
        for j in range(int((Z1 + HALF_W - Z0) / step) + 1):
            x = -HALF_W + (i + 0.5) * step + rnd.uniform(-0.007, 0.007)
            z = Z0 + (j + 0.5) * step + rnd.uniform(-0.007, 0.007)
            if inside(x, z, 0.022) and (V((x, 0, z)) - V((CENTRE.x, 0, CENTRE.z))).length > 0.1:
                shard(m, (x, z), rnd.uniform(0.016, 0.021), rnd.choice((3, 4, 4)), rnd.choice(MIRROR + MIRROR + GLASS), rnd,
                      y + 0.0012)
    m = solid
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "fur_mid", top="pewter")                        # a flagstone pad
    # ---- bottles on the ground beside it, the source of the glass; a cracked one
    for k, (x, sw) in enumerate(((0.33, "emerald"), (0.4, "sapphire"), (-0.36, "gold_light"))):
        c = V((x, -0.12 - 0.05 * (k % 2), 0.0))
        m.cyl(c + V((0, 0, 0.05)), 0.03, 0.1, sw, segs=6, cap="iron_dark")
        m.cyl(c + V((0, 0, 0.12)), 0.012, 0.04, sw, segs=6, r2=0.01)
    m.cyl(V((-0.3, -0.25, 0.0285)), 0.028, 0.09, "emerald", segs=6, axis=(1, 0.3, 0))                 # lying down
    for k in range(5):                                                                                 # loose chips
        x, yy = rnd.uniform(-0.35, 0.35), rnd.uniform(-0.38, -0.15)
        m.obox(V((x, yy, 0.0055)), (0.02, 0.015, 0.003), rnd.choice(GLASS + MIRROR), rot=(0, 0, rnd.uniform(0, 3)))
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    mosaic = face.obj("pr_mosaic", coll)
    mosaic.parent = root

    parts = {}
    # glints: four-pointed stars that flash on the shards
    for i, (gx, gz) in enumerate(GLINTS):
        mm = B.M()
        c = V((gx, PY - 0.012, gz))
        mm.obox(c, (0.05, 0.002, 0.006), "flame_white")
        mm.obox(c, (0.006, 0.002, 0.05), "flame_white")
        mm.obox(c, (0.018, 0.003, 0.018), "flame_white", rot=(0, math.pi / 4, 0))
        parts[f"pr_glint_{i + 1}"] = A.part(mm.obj(f"pr_glint_{i + 1}", coll), root, c)
    # a string of beads with a spoon, hanging from the right shoulder
    mm = B.M()
    hook = V((HALF_W - 0.03, PY - 0.035, Z1 + 0.11))                # hung off a nail, clear of the glass
    beads = [hook + V((0.012 * math.sin(k), 0, -0.025 * k)) for k in range(1, 6)]
    for k, b in enumerate(beads):
        mm.blob(b, V((0.008, 0.008, 0.008)), GLASS[k % len(GLASS)], 5, 3)
    mm.beam(hook, beads[-1], 0.002, "rope")
    mm.beam(hook + V((0, 0.03, 0.0)), hook, 0.004, "iron_dark")                                     # the nail
    sp = beads[-1] + V((0, 0, -0.02))
    mm.beam(sp, sp + V((0, 0, -0.06)), 0.005, "silver")
    mm.blob(sp + V((0, 0, -0.075)), V((0.014, 0.006, 0.02)), "silver", 6, 3)
    parts["pr_charm"] = A.part(mm.obj("pr_charm", coll), root, hook)
    return root, parts


GLINTS = [(-0.12, 0.62), (0.14, 0.33), (0.0, 0.42), (-0.17, 0.24), (0.1, 0.6), (0.19, 0.46), (-0.06, 0.16)]


def clips(parts):
    n = len(GLINTS)

    def pose(p):
        out = {}
        for i in range(n):
            t = ((p - i / n) % 1.0) * n                        # each glint gets its own slice of the loop
            g = math.sin(math.pi * t / 0.8) if t < 0.8 else 0.0
            out[f"pr_glint_{i + 1}"] = (None, A.q((0, 1, 0), 40 * t), max(0.001, g))
        out["pr_charm"] = (None, A.q((0, 1, 0), 9 * math.sin(TAU * p)) @ A.q((1, 0, 0), 3 * math.sin(TAU * 2 * p + 0.5)), None)
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(17))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "mirror_mosaic.blend"), relative_remap=True)
    A.export()
    allow = [(n, NAME) for n in parts]
    probs = A.check(root, 1, 1, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [], ROOT / "renders" / "bld_mirror_mosaic_loops.gif",
                       target=(0.0, 0.0, 0.3), dist=1.7, pitch=30, grid_n=3, step=3, idle_only=True)


if __name__ == "__main__":
    main()
