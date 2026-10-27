"""bld_smelter_2x2: a squat stone furnace where ore is smelted into bars (Smelting).

A round stone furnace with a glowing fire-mouth toward the front and a tall chimney. A pair of bellows lies on the
floor beside it, its nozzle in the furnace's side; the raccoon crouches at the bellows' handle (spot_work, facing the
furnace: +X) and pumps (work_pump). Round it: an ore bin, a coal heap, a slab of ingot moulds with fresh bars, stacked
bars, tongs on a bucket.

Clips (24 fps)
  idle  48 fr  the fire flickers low, smoke drifts from the chimney
  work  48 fr  the bellows pump (its top board follows the raccoon's paws), the fire flares on each pump, sparks
               fly up the chimney, the smoke comes thicker

The bellows' handle moves with the paws (build_raccoon_jobs.pump_press), so start the building's work and the
raccoon's work_pump together (both 48 frames).

Run:  python3 tools/build_smelter.py   (--no-renders)
Out:  smelter.blend, export/bld_smelter_2x2.glb, renders/bld_smelter_loops.gif, renders/qa_buildings.txt
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_smelter_2x2"
FRAMES = 48
FLOOR = 0.008
SPOT = V((-0.36, 0.02, FLOOR + 0.0015))          # facing the furnace (+X), the bellows' handle in front of it
FURN = V((0.42, 0.18, FLOOR))                    # furnace: centre of its base
FURN_R, FURN_H = 0.27, 0.46
HANDLE = SPOT + Matrix.Rotation(math.radians(90), 3, "Z") @ J.PUMP    # the handle bar's middle, raised
HINGE = V((FURN.x - FURN_R - 0.02, SPOT.y, FLOOR + 0.05))           # the top board's hinge, at the nozzle end
BOARD_W = 0.11


def to_world(p):
    """Raccoon space (facing -Y) -> building space, the raccoon at SPOT facing +X."""
    return SPOT + Matrix.Rotation(math.radians(90), 3, "Z") @ p


def build(coll, rnd):
    m = B.M()
    # ---- floor: packed earth with a scorched patch by the furnace
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "rope_dark")
    m.cyl(FURN + V((0, -0.2, 0.001)), 0.36, 0.002, "soot", segs=12)
    # ---- furnace: courses of stone, a domed top, the chimney
    n = 4
    for k in range(n):
        z = FLOOR + FURN_H * k / n
        r = FURN_R * (1 - 0.06 * k)
        m.cyl(FURN + V((0, 0, z + FURN_H / n / 2)), r, FURN_H / n, ["stone_mid", "stone_light"][k % 2], segs=12,
              r2=r * 0.97, rot=0.26 * k)
    m.blob(FURN + V((0, 0, FLOOR + FURN_H)), V((FURN_R * 0.8, FURN_R * 0.8, 0.1)), "stone_mid", 12, 3)
    ch = FURN + V((0.06, 0.06, 0))
    m.cyl(ch + V((0, 0, 0.78)), 0.08, 0.6, "stone_dark", segs=8, r2=0.065, cap="soot")
    m.cyl(ch + V((0, 0, 1.06)), 0.085, 0.04, "stone_light", segs=8)
    # fire-mouth facing the front (-Y): a dark arch with a stone lintel; the coals and flames are parts
    mo = FURN + V((0, -FURN_R + 0.01, FLOOR))
    m.obox(mo + V((0, -0.005, 0.1)), (0.22, 0.03, 0.18), "soot")
    m.obox(mo + V((0, -0.02, 0.205)), (0.28, 0.05, 0.045), "stone_pale")
    m.blob(mo + V((0, -0.012, 0.02)), V((0.095, 0.03, 0.025)), "torch_orange", 7, 3)               # coals
    m.blob(mo + V((0.02, -0.02, 0.03)), V((0.04, 0.02, 0.015)), "flame_yellow", 6, 3)
    # the bellows: bottom board, the nozzle into the furnace's side
    x1 = HINGE.x
    x0 = HANDLE.x - 0.012
    m.obox(V(((x0 + x1) / 2, SPOT.y, FLOOR + 0.01)), (x1 - x0, BOARD_W, 0.02), "wood_dark")
    m.cyl(V((x1 + 0.04, SPOT.y, FLOOR + 0.04)), 0.02, 0.1, "iron_dark", axis=(1, 0, 0.15), segs=6, r2=0.012)
    for x in (x0 + 0.03, x1 - 0.03):
        m.obox(V((x, SPOT.y, FLOOR + 0.005)), (0.03, BOARD_W + 0.03, 0.01), "wood_mid")                # feet
    # ---- round it: ore bin (front left), coal heap, ingot moulds with bars (front right), stacked bars, tongs
    ob = V((-0.62, -0.55, FLOOR))
    for (c, size) in (((0.0, -0.14), (0.34, 0.04)), ((-0.15, 0.0), (0.04, 0.28)), ((0.15, 0.0), (0.04, 0.28)),
                      ((0.0, 0.14), (0.34, 0.04))):
        m.obox(ob + V((c[0], c[1], 0.05)), (size[0], size[1], 0.1), "wood_mid", top="wood_light")
    m.blob(ob + V((0, 0, 0.07)), V((0.13, 0.11, 0.06)), "rust_dark", 8, 3)
    for k in range(5):
        a = k * 1.3
        m.obox(ob + V((0.06 * math.cos(a), 0.05 * math.sin(a), 0.11)), (0.035, 0.03, 0.025),
               ["rust", "copper", "iron", "rust", "gold"][k], rot=(0.4, 0.3 * k, k))
    m.blob(V((-0.7, 0.55, FLOOR)), V((0.18, 0.16, 0.11)), "soot", 8, 4)                          # coal heap
    for k in range(5):
        m.blob(V((-0.7 + 0.06 * math.cos(k * 1.5), 0.55 + 0.05 * math.sin(k * 1.5), 0.085 + 0.01 * k)),
               V((0.025, 0.022, 0.02)), "fur_mask", 5, 3)
    sl = V((0.48, -0.6, FLOOR))
    m.obox(sl + V((0, 0, 0.03)), (0.42, 0.22, 0.06), "stone_light", top="stone_pale")             # mould slab
    for k in range(3):
        c = sl + V((-0.13 + 0.13 * k, 0, 0.062))
        m.obox(c, (0.09, 0.05, 0.006), "soot")
        m.obox(c + V((0, 0, 0.006)), (0.075, 0.038, 0.012), ["gold_light", "iron_light", "copper"][k])
    for k in range(4):                                                                            # stacked bars
        y = 0.62 + 0.025 * (k % 2)
        m.obox(V((0.0 + 0.05 * (k // 2), y - 0.02 * k, FLOOR + 0.012 + 0.024 * (k // 2))), (0.1, 0.04, 0.024),
               ["iron", "gold", "iron_light", "copper"][k], rot=(0, 0, 1.4 * (k // 2)))
    bu = V((0.82, 0.62, FLOOR))
    m.cyl(bu + V((0, 0, 0.06)), 0.06, 0.12, "iron", segs=8, cap="water")                          # quench bucket
    m.beam(bu + V((-0.02, 0, 0.12)), bu + V((-0.1, -0.02, 0.24)), 0.008, "iron_dark")             # tongs
    m.beam(bu + V((0.0, 0.015, 0.12)), bu + V((-0.08, 0.0, 0.25)), 0.008, "iron_dark")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    # bellows top board (hinged at the nozzle end) with the handle bar across its free end
    m = B.M()
    L = HINGE.x - x0
    ang = math.atan2(HANDLE.z - 0.01 - HINGE.z, HINGE.x - HANDLE.x)
    mid = HINGE + V((-L / 2 * math.cos(ang), 0, L / 2 * math.sin(ang)))
    m.obox(mid, (L, BOARD_W, 0.014), "wood_mid", rot=(0, ang, 0))
    m.beam(V((HANDLE.x, HANDLE.y - 0.06, HANDLE.z)), V((HANDLE.x, HANDLE.y + 0.06, HANDLE.z)), 0.014, "wood_light")
    parts["pr_bellows_top"] = A.part(m.obj("pr_bellows_top", coll), root, HINGE)
    # the leather between the boards: a wedge, pinned at the hinge, that squashes with the board
    m = B.M()
    prof = [(x1 - 0.01, FLOOR + 0.02), (x0 + 0.03, FLOOR + 0.02), (x0 + 0.03, HANDLE.z - 0.05)]   # under the paws
    vs0 = [m.bm.verts.new((x, SPOT.y - BOARD_W / 2 + 0.008, z)) for x, z in prof]
    vs1 = [m.bm.verts.new((x, SPOT.y + BOARD_W / 2 - 0.008, z)) for x, z in prof]
    fs = [m.bm.faces.new(vs0), m.bm.faces.new(list(reversed(vs1)))]
    for i in range(3):
        j = (i + 1) % 3
        fs.append(m.bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i])))
    import bmesh
    bmesh.ops.recalc_face_normals(m.bm, faces=fs)
    m.tag(fs, "leather")
    parts["pr_bellows_skin"] = A.part(m.obj("pr_bellows_skin", coll), root, V((x1 - 0.01, SPOT.y, FLOOR + 0.02)))
    # flames in the fire-mouth
    for i, (dx, h, sw) in enumerate(((0.0, 0.14, "torch_orange"), (0.055, 0.1, "flame_yellow"), (-0.055, 0.1, "flame_yellow"))):
        m = B.M()
        c = mo + V((dx, -0.012, 0.03))
        m.cyl(c + V((0, 0, h / 2)), 0.032 if i == 0 else 0.022, h, sw, segs=5, r2=0.0)
        parts[f"pr_flame_{i + 1}"] = A.part(m.obj(f"pr_flame_{i + 1}", coll), root, c)
    # smoke from the chimney, sparks (work)
    top = ch + V((0, 0, 1.09))
    for i in range(3):
        m = B.M()
        m.blob(top, V((0.05, 0.05, 0.04)), "stone_pale", 7, 3)
        parts[f"pr_smoke_{i + 1}"] = A.part(m.obj(f"pr_smoke_{i + 1}", coll), root, top)
    for i in range(3):
        m = B.M()
        c = top + V((0.01 * (i - 1), 0, -0.01))
        m.obox(c, (0.012, 0.012, 0.012), "flame_yellow", rot=(0.7, 0.3, i))
        parts[f"pr_spark_{i + 1}"] = A.part(m.obj(f"pr_spark_{i + 1}", coll), root, c)
    return root, parts


def board_angle(d):
    """Rotation (deg, about +Y at the hinge) that lowers the handle by d * PUMP_DEPTH."""
    L = HINGE.x - HANDLE.x
    return -math.degrees(math.atan2(J.PUMP_DEPTH * d, L))


def clips(parts):
    def fire(p, k):
        pose = {}
        for i, (f, ph) in enumerate(((3, 0.0), (4, 0.33), (5, 0.66))):
            fl = 1 + 0.12 * math.sin(TAU * (f * p + ph))
            pose[f"pr_flame_{i + 1}"] = (None, A.q((0, 0, 1), 20 * math.sin(TAU * (f * p + ph))), (k, k, fl * k))
        return pose

    def smoke(p, speed):
        pose = {}
        for i in range(3):
            u = (p * speed + i / 3) % 1.0
            s = math.sin(math.pi * u)
            pose[f"pr_smoke_{i + 1}"] = (V((0.06 * u, 0.03 * math.sin(TAU * u), 0.34 * u)), None,
                                         max((0.6 + 1.1 * u) * s, 0.001))
        return pose

    def idle(p):
        pose = {**fire(p, 0.8), **smoke(p, 1)}
        pose["pr_bellows_top"] = (None, None, None)
        pose["pr_bellows_skin"] = (None, None, None)
        for i in range(1, 4):
            pose[f"pr_spark_{i}"] = A.hidden()
        return pose

    def work(p):
        d = J.pump_press(p)
        flare = sum(math.exp(-((((p - c) + 0.5) % 1.0 - 0.5) ** 2) / 0.004) for c in (0.2, 0.7))
        pose = {**fire(p, 1.0 + 0.45 * flare), **smoke(p, 2)}
        pose["pr_bellows_top"] = (None, A.q((0, 1, 0), board_angle(d)), None)
        pose["pr_bellows_skin"] = (None, None, (1, 1, 1 - 0.32 * d))
        for i in range(1, 4):                                        # sparks shoot up after each pump
            u = ((p - 0.2 - 0.04 * i) * 2) % 1.0
            if u < 0.5:
                pose[f"pr_spark_{i}"] = (V((0.03 * (i - 2) * u, 0.02 * math.sin(i + u * 4), 0.3 * u)),
                                         A.q((1, 0, 0), 300 * u), max(1 - 2 * u, 0.001))
            else:
                pose[f"pr_spark_{i}"] = A.hidden()
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(71))
    A.spot(root, "spot_work", SPOT, (1, 0, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "smelter.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_pump")
    allow = [("pr_bellows_top", "pr_bellows_skin"), ("pr_bellows_top", NAME), ("pr_bellows_skin", NAME)] + \
            [(f"pr_flame_{i}", NAME) for i in (1, 2, 3)] + [("pr_flame_1", "pr_flame_2"), ("pr_flame_1", "pr_flame_3"),
                                                            ("pr_flame_2", "pr_flame_3")] + \
            [(f"pr_smoke_{i}", NAME) for i in (1, 2, 3)] + [(f"pr_spark_{i}", NAME) for i in (1, 2, 3)] + \
            [(f"pr_smoke_{i}", f"pr_smoke_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j] + \
            [(f"pr_spark_{i}", f"pr_smoke_{j}") for i in (1, 2, 3) for j in (1, 2, 3)] + \
            [(f"pr_spark_{i}", f"pr_spark_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, None, "work", {"pr_bellows_top": None})], allow=allow,
                    sky=[f"pr_smoke_{i}" for i in (1, 2, 3)] + [f"pr_spark_{i}" for i in (1, 2, 3)])
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_smelter_loops.gif",
                       target=(0.0, 0.05, 0.25), dist=4.0, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
