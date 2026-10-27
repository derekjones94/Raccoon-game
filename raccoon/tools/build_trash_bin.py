"""bld_trash_bin_1x1: a tipped-over trash can, raccoons' favourite place to rummage for fun.

A dented tin can lies on its side beside the heap, its mouth toward it; a heap of trash spills out of it (apple cores, a fish
skeleton, cans, paper, a banana peel). Its lid lies on the ground beside it. The raccoon digs into the spill from
behind (spot_work, facing the front: its face shows over the can) with work_rummage.

Clips (24 fps)
  idle  48 fr  the lid rocks now and then, two flies buzz round the heap
  work  48 fr  as idle, plus trash on the heap jumps as the paws dig, and the lid rattles hard

Run:  python3 tools/build_trash_bin.py   (--no-renders)
Out:  trash_bin.blend, export/bld_trash_bin_1x1.glb, renders/bld_trash_bin_loops.gif, renders/qa_buildings.txt
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
import build_rummage_camp as RC  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_trash_bin_1x1"
FRAMES = 48
FLOOR = 0.004
SPOT = V((0.02, 0.19, FLOOR + 0.0015))           # behind the spill, facing the front (-Y)
HEAP_C = V((SPOT.x, SPOT.y - 0.217, 0.0))        # the rummage camp's proven near heap (work_rummage reaches it)
HEAP_R = V((0.21, 0.13, 0.12))
CAN_R, CAN_L = 0.11, 0.27
CAN_C = V((HEAP_C.x + 0.3, HEAP_C.y - 0.02, CAN_R))   # the can's axis centre; it lies along X, its mouth toward
                                                         # the heap (-X), so the spill shows from the game camera


def hp(ang, hf):
    return RC.heap_point(math.radians(ang), hf, HEAP_C, HEAP_R)


def build(coll, rnd):
    m = B.M()
    # ---- ground: a patch of cobbles
    m.obox(V((0, 0, FLOOR / 2)), (0.94, 0.94, FLOOR), "stone_mid")
    # ---- the can on its side: ribbed tin, open toward the raccoon, a dent
    import bmesh
    segs = 12
    x1, x0 = CAN_C.x + CAN_L / 2, CAN_C.x - CAN_L / 2           # bottom at x1, the open mouth at x0
    rings = []
    for x, r in ((x1, CAN_R * 0.95), (x0, CAN_R), (x0, CAN_R - 0.008), (x1 - 0.01, CAN_R * 0.95 - 0.008)):
        rings.append([m.bm.verts.new(V((x, CAN_C.y + r * math.cos(TAU * k / segs) * (0.9 if k == 3 else 1.0),
                                        CAN_C.z + r * math.sin(TAU * k / segs)))) for k in range(segs)])
    fs = []
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            j = (k + 1) % segs
            fs.append(m.bm.faces.new((a[k], a[j], b[j], b[k])))
    fs.append(m.bm.faces.new(rings[0]))
    fs.append(m.bm.faces.new(list(reversed(rings[3]))))
    bmesh.ops.recalc_face_normals(m.bm, faces=fs)
    m.tag(fs, "iron_light")
    m.tag(fs[2 * segs: 3 * segs], "iron_dark")                                               # the dark inside
    for x in (x1 - 0.06, CAN_C.x, x0 + 0.06):                                               # ribs
        m.cyl(V((x, CAN_C.y, CAN_C.z)), CAN_R + 0.004, 0.012, "iron", axis=(1, 0, 0), segs=segs)
    m.cyl(V((x0 - 0.002, CAN_C.y, CAN_C.z)), CAN_R + 0.006, 0.01, "iron", axis=(1, 0, 0), segs=segs)  # rolled rim
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- the spill (still): the paws dig into it
    m = B.M()
    m.blob(HEAP_C, HEAP_R, "wood_weathered", 10, 5)
    m.blob(V((x0 + 0.02, CAN_C.y, 0.0)), V((0.08, 0.09, 0.07)), "rope_dark", 8, 4)           # spilling from the mouth
    for ang, hf, kind in ((-20, 0.4, "paper"), (-150, 0.45, "paper"), (-80, 0.75, "core"), (-110, 0.3, "can"),
                          (10, 0.25, "fish"), (-170, 0.2, "core"), (-50, 0.6, "paper")):
        p, n = hp(ang, hf)
        if kind == "paper":
            m.obox(p + n * 0.004, (0.05, 0.04, 0.004), rnd.choice(["cloth_cream", "bone"]),
                   rot=n.to_track_quat("Z", "Y").to_euler())
        elif kind == "core":
            m.cyl(p + n * 0.016, 0.012, 0.03, "cloth_cream", segs=6, r2=0.008, axis=tuple(n))
        elif kind == "can":
            m.cyl(p + n * 0.02, 0.016, 0.04, "iron_light", segs=6, axis=(1, 0.3, 0.2), cap="rust")
        else:
            m.beam(p + n * 0.01, p + n * 0.01 + V((0.07, 0.01, 0.0)), 0.006, "bone")         # fish spine
            for k in range(3):
                q = p + n * 0.01 + V((0.015 + 0.02 * k, 0.01, 0))
                m.beam(q + V((0, -0.015, 0)), q + V((0, 0.015, 0)), 0.003, "bone")
    spill = m.obj("pr_spill", coll)
    PR.trim_below_floor(spill)
    spill.parent = root
    parts = {}
    # the lid on the ground beside the can, a banana peel and a can that jump while the raccoon digs
    m = B.M()
    lc = V((-0.26, -0.3, FLOOR + 0.008))
    m.cyl(lc, 0.115, 0.012, "iron_light", segs=12, cap="iron")
    m.obox(lc + V((0, 0, 0.012)), (0.05, 0.012, 0.012), "iron_dark")                        # handle
    parts["pr_lid"] = A.part(m.obj("pr_lid", coll), root, lc + V((0.115, 0, -0.006)))
    for i, (ang, hf, kind) in enumerate(((-60, 0.55, "peel"), (135, 0.62, "can"))):
        p, n = hp(ang, hf)
        m = B.M()
        c = p + n * 0.016
        if kind == "peel":
            m.cyl(c, 0.012, 0.05, "gold_light", axis=(1, 0.2, 0.3), segs=5, r2=0.004)
            m.obox(c + V((0.012, 0.014, -0.004)), (0.03, 0.012, 0.004), "gold", rot=(0, 0, 0.6))
        else:
            m.cyl(c, 0.015, 0.035, "copper", axis=(0.3, 1, 0.2), segs=6, cap="rust")
        parts[f"pr_trash_{i + 1}"] = A.part(m.obj(f"pr_trash_{i + 1}", coll), root, c)
    for i in range(2):                                                                   # flies
        m = B.M()
        c = HEAP_C + V((0.0, -0.04, 0.3 + 0.03 * i))                                # above the can
        m.obox(c, (0.008, 0.006, 0.006), "soot")
        m.obox(c + V((0, 0, 0.004)), (0.014, 0.004, 0.002), "stone_frost")
        parts[f"pr_fly_{i + 1}"] = A.part(m.obj(f"pr_fly_{i + 1}", coll), root, c)
    return root, spill, parts


def clips(parts):
    def common(p, rattle):
        pose = {}
        for i in (1, 2):                                               # flies: quick loops over the heap
            a = TAU * (3 * p + 0.5 * i) * (1 if i == 1 else -1)
            pose[f"pr_fly_{i}"] = (V((0.08 * math.cos(a), 0.05 * math.sin(2 * a), 0.02 * math.sin(3 * a))),
                                   A.q((0, 0, 1), math.degrees(a)), None)
        k = sum(math.exp(-((((p - c) + 0.5) % 1.0 - 0.5) ** 2) / 0.002) for c in (0.3, 0.8))
        rock = (3 + 7 * rattle) * k * math.sin(TAU * 8 * p)             # the lid rocks on its rim, now and then
        pose["pr_lid"] = (None, A.q((0, 1, 0), abs(rock)), None)           # tips up off the ground
        return pose

    def idle(p):
        pose = common(p, 0.0)
        for i in (1, 2):
            pose[f"pr_trash_{i}"] = (None, None, None)
        return pose

    def work(p):
        pose = common(p, 1.0)
        for i, ph in ((1, 0.85), (2, 0.35)):                          # each paw's dig (work_rummage: right .2-.5, left .7-1)
            j = math.exp(-((((p - ph) + 0.5) % 1.0 - 0.5) ** 2) / 0.003)
            pose[f"pr_trash_{i}"] = (V((0, 0, 0.008 * j)), A.q((1, 0.4 * i, 0.2), 14 * j * math.sin(TAU * 6 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, spill, parts = build(coll, random.Random(101))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(spill) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(spill)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "trash_bin.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_rummage")
    allow = [("pr_lid", NAME), ("pr_trash_1", "pr_spill"), ("pr_trash_2", "pr_spill"), ("pr_spill", NAME)]
    probs = A.check(root, 1, 1, crew=[(rig, mesh, None, "work", {"pr_spill": None, "pr_trash_1": None,
                                                               "pr_trash_2": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_trash_bin_loops.gif",
                       target=(0.0, 0.0, 0.12), dist=2.2, pitch=42, idle_frames=24, grid_n=3)


if __name__ == "__main__":
    main()
