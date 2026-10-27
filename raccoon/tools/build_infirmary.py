"""bld_infirmary_2x2: where the injured are patched up (Patching).

A tidy corner of the colony on a plank floor: two low cots with blankets where patients rest (spot_patient_1, _2:
the base `sleep` clip, sitting propped up and dozing), and the healer's corner at the front right: the healer
crouches by a stone mortar on the floor and grinds medicine (spot_work, work_grind with prop_pestle). A kettle on a
little brazier, a shelf of jars and rolled bandages, bandages drying on a line, a basket of herbs.

Clips (24 fps)
  idle  48 fr  the bandages on the line sway, the brazier glows, the kettle steams gently
  work  48 fr  the kettle boils (its lid rattles, more steam), the medicine in the mortar swirls with the pestle

Patients use the base `sleep` clip on the cots; the healer uses work_grind (start the building's work with it).

Run:  python3 tools/build_infirmary.py   (--no-renders)
Out:  infirmary.blend, export/bld_infirmary_2x2.glb, renders/bld_infirmary_loops.gif, renders/qa_buildings.txt
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
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_infirmary_2x2"
FRAMES = 48
FLOOR = 0.016
COT_TOP = FLOOR + 0.07
SPOT = V((0.45, -0.28, FLOOR + 0.0015))          # the healer, crouched by the mortar, facing the front (-Y)
MORTAR = SPOT + J.MORTAR_C                       # bottom of the mortar's bowl (raccoon space == building space)
SLEEP_C, SLEEP_H = DEN.SLEEP_BOX["chr_raccoon"]  # a sleeping adult's footprint (own space): centre, half-sizes
COTS = [V((-0.52, 0.42, 0)), V((0.08, 0.5, 0))]  # where each patient sits (cot centred under its footprint)


def build(coll, rnd):
    m = B.M()
    # ---- plank floor
    for k in range(9):
        x = -0.97 + 1.94 * (k + 0.5) / 9
        m.obox(V((x, 0, FLOOR / 2)), (1.94 / 9 - 0.008, 1.94, FLOOR), "wood_light" if k % 2 else "wood_cut")
    # ---- cots: a frame on short legs, a straw mattress, a folded blanket at the foot, a pillow at the back
    for i, c in enumerate(COTS):
        cc = c + V((SLEEP_C.x, SLEEP_C.y, 0))
        hx, hy = SLEEP_H.x + 0.03, SLEEP_H.y + 0.03
        m.obox(V((cc.x, cc.y, COT_TOP - 0.025)), (2 * hx + 0.02, 2 * hy + 0.02, 0.02), "wood_mid")
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.obox(V((cc.x + sx * hx, cc.y + sy * hy, (COT_TOP - 0.03) / 2 + FLOOR / 2)), (0.025, 0.025, COT_TOP - 0.03 - FLOOR + 0.002), "wood_dark")
        m.obox(V((cc.x, cc.y, COT_TOP - 0.008)), (2 * hx, 2 * hy, 0.016), "cloth_blue" if i else "cloth_red")   # blanketed mattress
        hz = COT_TOP + 0.07
        m.obox(V((cc.x, cc.y + hy + 0.022, (FLOOR + hz) / 2)), (2 * hx + 0.02, 0.016, hz - FLOOR), "wood_dark")    # headboard
    # ---- the healer's corner: brazier with a kettle, shelf of jars and bandages
    br = V((0.75, 0.15, FLOOR))
    m.cyl(br + V((0, 0, 0.05)), 0.06, 0.1, "iron_dark", segs=8, r2=0.075, cap="torch_orange")
    for k in range(3):
        a = TAU * k / 3
        m.beam(br + V((0.06 * math.cos(a), 0.06 * math.sin(a), 0)), br + V((0.05 * math.cos(a), 0.05 * math.sin(a), 0.06)), 0.008, "iron")
    m.cyl(br + V((0, 0, 0.13)), 0.05, 0.06, "copper", segs=8, r2=0.04)                                 # kettle
    m.cyl(br + V((0.055, 0, 0.14)), 0.008, 0.06, "copper", axis=(1, 0, 0.8), segs=5)                    # spout
    sh = V((0.72, 0.68, FLOOR))
    for x in (-0.18, 0.18):
        m.obox(sh + V((x, 0, 0.2)), (0.025, 0.1, 0.4), "wood_dark")
    for z in (0.12, 0.27, 0.39):
        m.obox(sh + V((0, 0, z)), (0.4, 0.11, 0.018), "wood_light")
        for k in range(4):
            x = -0.13 + 0.085 * k
            if (k + int(z * 10)) % 3 == 0:
                m.cyl(sh + V((x, 0, z + 0.03)), 0.022, 0.035, "cloth_cream", axis=(1, 0, 0), segs=6)    # rolled bandage
            else:
                m.cyl(sh + V((x, 0, z + 0.035)), 0.02, 0.05, rnd.choice(["verdigris", "teal_light", "amethyst", "moss_light"]),
                      segs=6, cap="cloth_cream")
    # bandage line: two posts (left)
    for y in (-0.62, 0.05):
        m.obox(V((-0.88, y, 0.25)), (0.03, 0.03, 0.5), "wood_dark")
    m.beam(V((-0.88, -0.62, 0.48)), V((-0.88, 0.05, 0.48)), 0.006, "rope")
    hb = V((-0.4, -0.7, FLOOR))                                                                       # basket of herbs
    m.cyl(hb + V((0, 0, 0.045)), 0.08, 0.09, "rope", segs=8, r2=0.09, cap="rope_dark")
    for k in range(4):
        a = k * 1.6
        m.cyl(hb + V((0.03 * math.cos(a), 0.03 * math.sin(a), 0.12)), 0.02, 0.06, "moss" if k % 2 else "moss_light", segs=4, r2=0.006)
    m.obox(V((0.1, -0.72, FLOOR + 0.004)), (0.36, 0.22, 0.008), "cloth_red")                           # a rug
    m.obox(V((0.1, -0.72, FLOOR + 0.006)), (0.08, 0.025, 0.006), "cloth_cream")                        # stitched cross
    m.obox(V((0.1, -0.72, FLOOR + 0.006)), (0.025, 0.08, 0.006), "cloth_cream")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # the mortar (on the floor by the healer's right foot) with its medicine: its own still object, the pestle
    # grinds in it
    import build_fishing_spot as FS
    mm = B.M()
    stand_top = MORTAR.z - 0.026
    mm.cyl(V((MORTAR.x, MORTAR.y, (FLOOR + stand_top) / 2)), 0.018, stand_top - FLOOR, "stone_mid", segs=6, r2=0.014)   # narrow stand
    FS._tube(mm, V((MORTAR.x, MORTAR.y, stand_top)), 0.028, 0.036, MORTAR.z - stand_top + 0.012, "stone_light", 8)
    mm.cyl(V((MORTAR.x, MORTAR.y, MORTAR.z - 0.004)), 0.027, 0.01, "moss", segs=8)
    med = mm.obj("pr_mortar", coll)
    med.parent = root
    parts = {}
    for i, (y, sw, h) in enumerate(((-0.5, "cloth_cream", 0.12), (-0.32, "cloth_cream", 0.09), (-0.12, "cloth_red", 0.1))):
        mm = B.M()
        top = V((-0.88, y, 0.475))
        mm.obox(top + V((0, 0, -h / 2)), (0.008, 0.04, h), sw)
        parts[f"pr_bandage_{i + 1}"] = A.part(mm.obj(f"pr_bandage_{i + 1}", coll), root, top)
    mm = B.M()
    lid = br + V((0, 0, 0.162))
    mm.cyl(lid, 0.04, 0.008, "copper", segs=8, cap="rust")
    mm.cyl(lid + V((0, 0, 0.008)), 0.008, 0.01, "iron_dark", segs=5)
    parts["pr_kettle_lid"] = A.part(mm.obj("pr_kettle_lid", coll), root, lid)
    for i in range(2):
        mm = B.M()
        c = br + V((0.09 + 0.01 * i, 0, 0.19))
        mm.blob(c, V((0.025, 0.025, 0.02)), "stone_frost", 7, 3)
        parts[f"pr_steam_{i + 1}"] = A.part(mm.obj(f"pr_steam_{i + 1}", coll), root, c)
    mm = B.M()
    sc = V((MORTAR.x, MORTAR.y, MORTAR.z + 0.002))
    mm.beam(sc + V((-0.012, 0, 0)), sc + V((0.012, 0, 0)), 0.004, "moss_light")
    parts["pr_swirl"] = A.part(mm.obj("pr_swirl", coll), root, sc)
    return root, med, parts


def clips(parts):
    def common(p, boil):
        pose = {}
        for i in range(1, 4):
            pose[f"pr_bandage_{i}"] = (None, A.q((0, 1, 0), 6 * math.sin(TAU * (p + 0.3 * i))), None)
        for i in (1, 2):
            u = (p * (1 + boil) + i / 2) % 1.0
            s = math.sin(math.pi * u)
            pose[f"pr_steam_{i}"] = (V((0.04 * u, 0.01 * math.sin(TAU * u), 0.15 * u)), None, max((0.5 + 0.8 * u) * s * (0.7 + 0.5 * boil), 0.001))
        return pose

    def idle(p):
        pose = common(p, 0.0)
        pose["pr_kettle_lid"] = (None, None, None)
        pose["pr_swirl"] = (None, A.q((0, 0, 1), 30 * math.sin(TAU * p)), None)
        return pose

    def work(p):
        pose = common(p, 1.0)
        r = math.sin(TAU * 8 * p) * (0.5 + 0.5 * math.sin(TAU * 2 * p))
        pose["pr_kettle_lid"] = (V((0, 0, 0.003 * abs(r))), A.q((1, 0.3, 0), 6 * r), None)
        pose["pr_swirl"] = (None, A.q((0, 0, 1), 720 * p), None)         # with the pestle (two turns a loop)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, med, parts = build(coll, random.Random(121))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    for i, c in enumerate(COTS):
        A.spot(root, f"spot_patient_{i + 1}", V((c.x, c.y, COT_TOP + 0.0015)), (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(med) + sum(K.tris(o) for o in parts.values())} tris (moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "infirmary.blend"), relative_remap=True)
    A.export()
    rig, mesh, pestle = A.raccoon_at(bpy.data.objects["spot_work"], clip="work_grind", tool="prop_pestle")
    crew, objs = [(rig, mesh, pestle, "work", {"pr_mortar": None, "pr_swirl": None})], [rig, mesh, pestle]
    for i in range(len(COTS)):
        r2, m2, _ = A.raccoon_at(bpy.data.objects[f"spot_patient_{i + 1}"], clip="sleep")
        crew.append((r2, m2, None, "work", {}))
        objs += [r2, m2]
    allow = [(f"pr_bandage_{i}", NAME) for i in (1, 2, 3)] + [("pr_kettle_lid", NAME), ("pr_steam_1", "pr_steam_2"),
                                                               ("pr_swirl", "pr_mortar")] + \
            [(f"pr_steam_{i}", "pr_kettle_lid") for i in (1, 2)]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_infirmary_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
