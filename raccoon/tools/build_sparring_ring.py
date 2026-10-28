"""bld_sparring_ring_2x2: a roped ring of sand where two raccoons spar with padded sticks.

Four corner posts with two ropes round, a sand floor, a bench and a rack of practice sticks outside the ropes, a
dented shield hung on one post, a water bucket. Two raccoons face each other across the middle (spot_spar_1 faces
+X, spot_spar_2 faces -X) and play work_spar with prop_stick, the second HALF A LOOP after the first: one thrusts
while the other blocks, then they swap. They never touch: only the sticks meet.

Clips (24 fps)
  idle  48 fr  the shield wobbles on its nail, the ropes sway
  work  48 fr  dust puffs where each lunging foot lands (twice a loop, one per fighter), the ropes shake

Run:  python3 tools/build_sparring_ring.py   (--no-renders)
Out:  sparring_ring.blend, export/bld_sparring_ring_2x2.glb, renders/bld_sparring_ring_loops.gif
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
NAME = "bld_sparring_ring_2x2"
FRAMES = 48
FLOOR = 0.012
GAP = J.SPAR_GAP
SPOTS = [(V((-GAP / 2, -0.05, FLOOR + 0.0015)), (1, 0, 0)), (V((GAP / 2, -0.05, FLOOR + 0.0015)), (-1, 0, 0))]
RING = 0.72                                      # the corner posts
LUNGE = 0.21                                     # when a fighter's thrust lands (its own clip phase)


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (1.94, 1.94, 0.004), "moss")
    m.obox(V((0, 0, FLOOR / 2)), (2 * RING + 0.1, 2 * RING + 0.1, FLOOR), "gold_light", top="cloth_mustard")   # sand
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = V((sx * RING, sy * RING, 0))
            m.cyl(c + V((0, 0, 0.18)), 0.025, 0.36, "wood_bark", segs=7, cap="wood_cut")
            m.cyl(c + V((0, 0, 0.36)), 0.03, 0.02, "cloth_red", segs=7)
    root = m.obj(NAME, coll)
    # outside the ropes: a bench, a rack of sticks, a water bucket, a towel
    m = B.M()
    m.obox(V((0, 0.86, 0.05)), (0.5, 0.08, 0.02), "wood_mid", top="wood_light")
    for x in (-0.2, 0.2):
        m.obox(V((x, 0.86, 0.02)), (0.03, 0.07, 0.04), "wood_dark")
    m.obox(V((0.1, 0.86, 0.065)), (0.08, 0.06, 0.01), "cloth_cream")
    for x in (-0.86, -0.8):
        m.obox(V((x, 0.2, 0.15)), (0.025, 0.025, 0.3), "wood_dark")
    m.obox(V((-0.83, 0.2, 0.27)), (0.1, 0.02, 0.02), "wood_dark")
    for k in range(3):
        m.beam(V((-0.86 + 0.03 * k, 0.15, 0.0)), V((-0.86 + 0.03 * k, 0.21, 0.3)), 0.008, "wood_mid")
        m.blob(V((-0.86 + 0.03 * k, 0.21, 0.3)), V((0.012, 0.014, 0.016)), "cloth_cream", 5, 3)
    m.cyl(V((0.86, -0.4, 0.04)), 0.05, 0.08, "wood_mid", segs=8, r2=0.042, cap="water")
    extra = m.obj("pr_extras", coll)
    extra.parent = root
    PR.trim_below_floor(root)

    parts = {}
    # the ropes: two rings of four sides each, a part per side so they can shake
    for z in (0.16, 0.3):
        for k, (a, b) in enumerate((((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1)))):
            mm = B.M()
            pa, pb = V((a[0] * RING, a[1] * RING, z)), V((b[0] * RING, b[1] * RING, z))
            prev = pa
            for j in range(1, 9):
                t = j / 8
                q = pa.lerp(pb, t) + V((0, 0, -0.02 * math.sin(math.pi * t)))
                mm.beam(prev, q, 0.007, "rope")
                prev = q
            parts[f"pr_rope_{int(z * 100)}_{k + 1}"] = A.part(mm.obj(f"pr_rope_{int(z * 100)}_{k + 1}", coll), root, (pa + pb) / 2)
    # the dented shield on the front-right post
    mm = B.M()
    nail = V((RING, -RING - 0.03, 0.3))
    mm.cyl(nail + V((0, -0.006, -0.08)), 0.07, 0.012, "copper", segs=10, axis=(0, 1, 0), cap="rust")
    mm.cyl(nail + V((0, -0.013, -0.08)), 0.02, 0.012, "iron", segs=8, axis=(0, 1, 0))
    mm.beam(nail, nail + V((0, -0.006, -0.012)), 0.004, "rope")
    parts["pr_shield"] = A.part(mm.obj("pr_shield", coll), root, nail)
    # dust puffs at each fighter's lunging foot (its left, the front foot)
    for i, (sp, face) in enumerate(SPOTS):
        mm = B.M()
        fdir = V(face)
        left = V((0, 0, 1)).cross(fdir)
        c = sp + fdir * 0.15 + left * 0.06 + V((0, 0, 0.012))           # just ahead of the lunging (left) foot
        mm.blob(c, V((0.03, 0.03, 0.015)), "cloth_mustard", 6, 3)
        mm.blob(c + V((0.02, 0.015, 0.008)), V((0.018, 0.018, 0.012)), "gold_light", 5, 3)
        mm.blob(c + V((-0.02, -0.012, 0.006)), V((0.016, 0.016, 0.01)), "gold_light", 5, 3)
        parts[f"pr_dust_{i + 1}"] = A.part(mm.obj(f"pr_dust_{i + 1}", coll), root, c)
    return root, parts


def clips(parts):
    def ropes(p, shake):
        out = {}
        for n in parts:
            if n.startswith("pr_rope"):
                k = int(n[-1])
                out[n] = (V((0, 0, -0.004 * shake * math.sin(TAU * (6 * p + 0.25 * k)))), A.q((1 if k % 2 else 0, 0 if k % 2 else 1, 0),
                          (2 + 4 * shake) * math.sin(TAU * (p + 0.25 * k))), None)
        return out

    def idle(p):
        out = ropes(p, 0.0)
        out["pr_shield"] = (None, A.q((0, 1, 0), 4 * math.sin(TAU * p)), None)
        for i in (1, 2):
            out[f"pr_dust_{i}"] = A.hidden()
        return out

    def work(p):
        out = ropes(p, 1.0)
        out["pr_shield"] = (None, A.q((0, 1, 0), 6 * math.sin(TAU * 2 * p)), None)
        for i, off in ((1, 0.0), (2, 0.5)):
            t = (p - LUNGE * 0.5 - off) % 1.0                    # each fighter's thrust lands in its first half
            g = math.sin(math.pi * t / 0.18) if t < 0.18 else 0.0
            out[f"pr_dust_{i}"] = (V((0, 0, 0.02 * t)), None, max(0.001, 1.4 * g))
        return out

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(16))
    for i, (sp, face) in enumerate(SPOTS):
        A.spot(root, f"spot_spar_{i + 1}", sp, face)
    clips(parts)
    ex = bpy.data.objects["pr_extras"]
    print(f"STAT {NAME}: {K.tris(root) + K.tris(ex) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(ex)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "sparring_ring.blend"), relative_remap=True)
    A.export()
    crew, objs = [], []
    for i in range(2):
        rig, mesh, stick = A.raccoon_at(bpy.data.objects[f"spot_spar_{i + 1}"], clip="work_spar", tool="prop_stick")
        if i:
            A.offset_clip(rig, FRAMES // 2)                 # half a loop on: it blocks while the first thrusts
        crew.append((rig, mesh, stick, "work", {}))
        objs += [rig, mesh, stick]
    allow = [(n, NAME) for n in parts] + [(n, "pr_extras") for n in parts] + [("pr_extras", NAME)] + \
            [(a, b) for a in parts for b in parts if a < b and a.startswith("pr_rope") and b.startswith("pr_rope")]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_sparring_ring_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.2, pitch=38, idle_frames=24, grid_n=4, step=2)


if __name__ == "__main__":
    main()
