"""bld_hammock_1x2: a hammock slung between two crates. A decoration, and a resting spot.

Two stacked, banded crates at each end, and a stout post standing against their outer side, lashed where the ropes
tie on. The ropes fan from there to spreader bars at the hammock's ends; the hammock is a striped cloth, flat in the
middle where a raccoon curls up and rising to the bars. A blanket lies along one edge and drapes over the side (one
piece, clear of the sleeper), tassels hang from the other edge; under it a mug and a dropped book.

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
POST_Y, POST_TOP = 0.78, 0.46                    # the crates' centres, and the height where the ropes tie on
CRATE = (0.3, 0.26, 0.18)                        # the lower crate (x, y, z sizes) ...
CRATE2 = (0.22, 0.2, 0.12, 0.03, 0.03)           # ... and the one stacked on it, its offset (x, outward): back faces flush
POST_W = 0.05
POST_OFF = CRATE[1] / 2 + POST_W / 2             # the post stands against the crates' outer faces
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


def crate(m, c, size, body, top):
    """A crate: a box with a dark band round it at two heights and corner battens, all flush on its faces."""
    sx_, sy_, sz_ = size
    m.obox(c, size, body, top=top)
    for f in (0.3, 0.75):                                                            # bands, on all four sides
        z = c.z - sz_ / 2 + sz_ * f
        m.obox(V((c.x, c.y, z)), (sx_ + 0.006, sy_ + 0.006, 0.018), "wood_dark")
    for dx in (-1, 1):                                                               # corner battens
        for dy in (-1, 1):
            m.obox(V((c.x + dx * (sx_ / 2 - 0.008), c.y + dy * (sy_ / 2 - 0.008), c.z)), (0.02, 0.02, sz_ + 0.002), "wood_dark")


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 1.94, 0.004), "wood_weathered")
    for sy in (-1, 1):
        y = sy * POST_Y
        crate(m, V((0, y, CRATE[2] / 2)), CRATE, "wood_mid", "wood_light")
        w2, d2, h2, ox, oy = CRATE2
        crate(m, V((ox, y + sy * oy, CRATE[2] + h2 / 2)), (w2, d2, h2), "wood_light", "wood_mid")
        py = y + sy * POST_OFF                                                       # the post: on the ground, against
        top_z = POST_TOP + 0.05                                                      # the crates' outer faces
        m.obox(V((0, py, top_z / 2)), (POST_W, POST_W, top_z), "wood_dark")
        for z in (CRATE[2] + 0.04, POST_TOP):                                        # lashed above the crates, and
            m.obox(V((0, py, z)), (POST_W + 0.012, POST_W + 0.012, 0.022), "rope")   # where the ropes tie on
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
    tie = POST_Y + POST_OFF - POST_W / 2 - 0.006                                      # the ropes' knot, on the post's
    for sy in (-1, 1):                                                               # inner face, in its lashing
        by = sy * BAR_Y
        hm.beam(V((-HALF_W - 0.03, by, BAR_Z)), V((HALF_W + 0.03, by, BAR_Z)), 0.02, "wood_mid")      # spreader bar
        for x in (-HALF_W, -HALF_W / 2, 0.0, HALF_W / 2, HALF_W):                                    # suspension ropes
            hm.beam(V((x, by, BAR_Z)), V((0, sy * tie, POST_TOP)), 0.005, "rope")
    blanket(mm)
    cloth = mm.obj("pr_hammock_cloth", coll)
    hamm = hm.obj("pr_hammock", coll)
    cloth.parent = hamm
    parts["pr_hammock"] = A.part(hamm, root, PIVOT)
    cloth.location = -PIVOT                                                                           # stays put in its parent
    for i, y in enumerate((-0.3, -0.1, 0.1, 0.3)):                                                    # tassels on the
        tm = B.M()                                                                                    # other side
        top = V((-HALF_W - 0.001, y, bed_z(y) + 0.008))                               # on the cloth's edge
        tm.beam(top, top + V((0, 0, -0.05)), 0.004, "gold_dark")
        tm.blob(top + V((0, 0, -0.06)), V((0.008, 0.008, 0.014)), "gold", 5, 3)
        parts[f"pr_tassel_{i + 1}"] = A.part(tm.obj(f"pr_tassel_{i + 1}", coll), root, top)
    return root, parts


def cloth_z(x, y):
    """The cloth's top surface (it curls up a little at the long edges)."""
    return bed_z(y) + 0.012 * (abs(x) / HALF_W) ** 4


def blanket(mm):
    """A blanket over the hammock's +X edge: lying along the edge on top (clear of the sleeper), over the edge and
    hanging down the side, one piece, in bands, with a darker hem."""
    ys = [-0.18 + 0.36 * k / 8 for k in range(9)]
    path = [(0.215, 0.003), (0.245, 0.003), (HALF_W + 0.006, 0.0), (HALF_W + 0.012, -0.018), (HALF_W + 0.014, -0.06),
            (HALF_W + 0.013, -0.1), (HALF_W + 0.012, -0.115)]
    bands = ["cloth_blue", "cloth_blue", "cloth_blue", "cloth_blue", "cloth_cream", "cloth_blue", "sapphire"]
    for layer in (0.0, 1.0):                                                        # top face, then the underside
        rows = []
        for y in ys:
            row = []
            for i, (x, dz) in enumerate(path):
                z = cloth_z(min(x, HALF_W), y) + dz
                a, b = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
                t = V((b[0] - a[0], 0, b[1] - a[1])).normalized()
                nrm = V((-t.z, 0, t.x))                                              # out of the blanket
                wave = 0.004 * math.sin(y * 40) * (i >= 4)                          # the hanging part ripples
                row.append(mm.bm.verts.new(V((x + wave, y, z)) - nrm * 0.004 * layer))
            rows.append(row)
        for k in range(len(ys) - 1):
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                t = V((b[0] - a[0], 0, b[1] - a[1])).normalized()
                out = V((-t.z, 0, t.x)) * (1 if layer == 0 else -1)
                mm.face([rows[k][i], rows[k][i + 1], rows[k + 1][i + 1], rows[k + 1][i]], out, bands[i])


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
