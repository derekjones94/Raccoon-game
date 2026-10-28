"""bld_hammock_1x2: a hammock slung between two crates. A decoration, and a resting spot.

Two stacked crates, one at each end, each with a stout post lashed to it. Ropes run from the post tops to spreader
bars at the hammock's ends; the hammock is a striped cloth, flat in the middle where a raccoon curls up and rising to
the bars. A blanket hangs over its side, a tassel fringe; under it a mug and a dropped book.

A raccoon can sleep in it: spot_sleep (play the base sleep clip there). The spot is a child of the hammock's moving
node, `pr_hammock`, so it rocks with it: parent the sleeping raccoon to the spot (or to `pr_hammock`) and it rocks
too.

Clips (24 fps)
  idle  72 fr  the empty hammock rocks gently, the tassels swing
  work  72 fr  someone asleep: it rocks more slowly and less (72 frames, like the sleep loop)

Run:  python3 tools/build_hammock.py   (--no-renders)
Out:  hammock.blend, export/bld_hammock_1x2.glb, renders/bld_hammock_loops.gif
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
NAME = "bld_hammock_1x2"
FRAMES = 72
POST_Y, POST_TOP = 0.78, 0.46                    # the posts on the crates, and where the ropes tie on
BAR_Y, BAR_Z = 0.42, 0.25                        # the spreader bars
BED_Z = 0.2                                      # the cloth's flat middle
FLAT = 0.2                                       # half-length of the flat middle (the sleeper lies there)
HALF_W = 0.26
PIVOT = V((0, 0, POST_TOP))                      # the hammock rocks about the line between the post tops


def bed_z(y):
    a = abs(y)
    if a <= FLAT:
        return BED_Z
    t = (a - FLAT) / (BAR_Y - FLAT)
    return BED_Z + (BAR_Z - BED_Z) * t * t


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 1.94, 0.004), "wood_weathered")
    for sy in (-1, 1):
        y = sy * POST_Y
        m.obox(V((0, y, 0.09)), (0.3, 0.26, 0.18), "wood_mid", top="wood_light")                     # crates
        m.obox(V((0.03, y + sy * 0.02, 0.24)), (0.22, 0.2, 0.12), "wood_light", top="wood_mid")
        for z in (0.09, 0.24):
            m.obox(V((0, y - sy * 0.131, z)), (0.3, 0.004, 0.02), "wood_dark")
        m.obox(V((0, y + sy * 0.09, (POST_TOP + 0.05) / 2)), (0.05, 0.05, POST_TOP + 0.05), "wood_dark")   # post
        for z in (0.16, 0.28):
            m.obox(V((0, y + sy * 0.09, z)), (0.06, 0.06, 0.02), "rope")                               # lashings
    # under it: a mug and a dropped book
    m.cyl(V((0.2, -0.1, 0.03)), 0.025, 0.05, "wood_mid", segs=8, cap="wood_dark")
    m.obox(V((-0.18, 0.12, 0.012)), (0.1, 0.08, 0.02), "cloth_red", top="cloth_cream", rot=(0, 0, 0.4))
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    mm = DEN.DenMesh()
    n = 16
    ys = [-BAR_Y + 2 * BAR_Y * k / n for k in range(n + 1)]
    xs = [-HALF_W + 2 * HALF_W * j / 4 for j in range(5)]
    for side, want in ((0.0, V((0, 0, 1))), (-0.004, V((0, 0, -1)))):                             # both faces
        grid = [[mm.bm.verts.new(V((x, y, bed_z(y) + side + 0.012 * (abs(x) / HALF_W) ** 4))) for x in xs] for y in ys]
        for k in range(n):
            for j in range(4):
                sw = ["cloth_red", "cloth_cream", "teal", "cloth_cream"][j]
                mm.face([grid[k][j], grid[k][j + 1], grid[k + 1][j + 1], grid[k + 1][j]], want, sw)
    hm = B.M()
    for sy in (-1, 1):
        by = sy * BAR_Y
        hm.beam(V((-HALF_W - 0.03, by, BAR_Z)), V((HALF_W + 0.03, by, BAR_Z)), 0.02, "wood_mid")      # spreader bar
        for x in (-HALF_W, -HALF_W / 2, 0.0, HALF_W / 2, HALF_W):                                    # suspension ropes
            hm.beam(V((x, by, BAR_Z)), V((0, sy * (POST_Y - 0.09 + 0.09), POST_TOP)), 0.005, "rope")
    for k in range(5):                                                                                 # the blanket over
        y = -0.16 + 0.08 * k                                                                           # its side
        hm.obox(V((HALF_W + 0.012, y, BED_Z - 0.05)), (0.008, 0.075, 0.11), "cloth_blue" if k % 2 else "sapphire")
    hm.obox(V((HALF_W - 0.02, 0.0, BED_Z + 0.006)), (0.06, 0.4, 0.006), "cloth_blue")
    cloth = mm.obj("pr_hammock_cloth", coll)
    hamm = hm.obj("pr_hammock", coll)
    cloth.parent = hamm
    parts["pr_hammock"] = A.part(hamm, root, PIVOT)
    cloth.location = -PIVOT                                                                           # stays put in its parent
    for i, y in enumerate((-0.3, -0.1, 0.1, 0.3)):                                                    # tassels on the
        tm = B.M()                                                                                    # other side
        top = V((-HALF_W - 0.004, y, bed_z(y) - 0.004))
        tm.beam(top, top + V((0, 0, -0.05)), 0.004, "gold_dark")
        tm.blob(top + V((0, 0, -0.06)), V((0.008, 0.008, 0.014)), "gold", 5, 3)
        parts[f"pr_tassel_{i + 1}"] = A.part(tm.obj(f"pr_tassel_{i + 1}", coll), root, top)
    return root, parts


def rock(p, amp):
    return amp * math.sin(TAU * p)


def clips(parts):
    tassels = {n: o.location.copy() for n, o in parts.items() if n.startswith("pr_tassel")}

    def make(amp):
        def pose(p):
            a = rock(p, amp)
            r = A.q((0, 1, 0), a)
            out = {"pr_hammock": (None, r, None)}
            for n, loc in tassels.items():                       # ride with the hammock, and swing a little behind it
                rel = loc - PIVOT
                lag = A.q((0, 1, 0), 1.5 * amp * math.sin(TAU * p - 0.8))
                out[n] = ((r @ rel) - rel, r @ lag, None)
            return out
        return pose

    A.animate(parts, {"idle": (FRAMES, make(4.0)), "work": (FRAMES, make(2.0))})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(4))
    off, half = DEN.SLEEP_BOX["chr_raccoon"]
    sp = A.spot(root, "spot_sleep", V((-off.x, -off.y, BED_Z + 0.0015)), (0, -1, 0))
    ham = parts["pr_hammock"]
    bpy.context.view_layer.update()                                     # the hammock's new origin, before parenting
    mw = sp.matrix_world.copy()
    sp.parent = ham                                                     # it rocks with the hammock
    sp.matrix_world = mw
    clips(parts)
    cloth = bpy.data.objects["pr_hammock_cloth"]
    print(f"STAT {NAME}: {K.tris(root) + K.tris(cloth) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "hammock.blend"), relative_remap=True)
    A.export()
    bpy.context.view_layer.update()
    rig, mesh, _ = A.raccoon_at(sp, clip="sleep")
    mw = rig.matrix_world.copy()
    rig.parent = sp                                                     # the sleeper rocks too
    rig.matrix_world = mw
    allow = [("pr_hammock", NAME), ("pr_hammock", "pr_hammock_cloth"), ("pr_hammock_cloth", NAME)] + \
            [(f"pr_tassel_{i + 1}", o) for i in range(4) for o in ("pr_hammock_cloth", "pr_hammock", NAME)]
    probs = A.check(root, 1, 2, crew=[(rig, mesh, None, "work", {})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_hammock_loops.gif",
                       target=(0.0, 0.0, 0.2), dist=2.4, pitch=40, idle_frames=36, grid_n=3, step=3)


if __name__ == "__main__":
    main()
