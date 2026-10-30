"""bld_brewery_2x2: where tonics, sleep powder and smoke bombs are brewed (Brewing).

A fat iron cauldron of violet brew on a ring of hearth stones, a small fire under it. The raccoon stands behind it
(spot_work, facing the front) and stirs with a long ladle (work_stir, prop_ladle). Round it: a shelf of potion
bottles, bundles of herbs drying on a rack, a table with a mortar and pestle, a crate of smoke bombs, sacks of
sleep powder, a water barrel.

Clips (24 fps)
  idle  48 fr  the brew bubbles and steams, the fire flickers, the herbs on the rack sway
  work  48 fr  as idle, plus a swirl in the brew turns with the ladle (two turns a loop) and it bubbles harder

The swirl follows the ladle (build_raccoon_jobs.stir), so start the building's work and the raccoon's work_stir
together (both 48 frames).

Run:  python3 tools/build_brewery.py   (--no-renders)
Out:  brewery.blend, export/bld_brewery_2x2.glb, renders/bld_brewery_loops.gif, renders/qa_buildings.txt
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
import build_fishing_spot as FS  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_brewery_2x2"
FRAMES = 48
FLOOR = 0.008
SPOT = V((0.05, 0.12, FLOOR + 0.0015))           # behind the cauldron, facing the front (-Y)
POT = V((SPOT.x + J.POT_C.x, SPOT.y + J.POT_C.y, FLOOR))   # under the ladle's circle (raccoon space == building)
POT_R, RIM_Z, BREW_Z = 0.078, FLOOR + 0.093, FLOOR + 0.077
BASE_Z = FLOOR + 0.03                            # the cauldron's belly sits this high, over the fire


def build(coll, rnd):
    m = B.M()
    # ---- floor: dark stone, a round hearth of paler flags under the cauldron and where the brewer stands
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "stone_dark")
    m.cyl(V(((POT.x + SPOT.x) / 2, (POT.y + SPOT.y) / 2, FLOOR + 0.0005)), 0.36, 0.001, "stone_mid", segs=12)
    # ---- the cauldron: a fat pot open at the top (outer wall, inner wall, rim), on hearth stones, three legs
    import bmesh
    segs = 12
    prof = [(POT_R * 0.55, BASE_Z - 0.012), (POT_R * 0.95, BASE_Z + 0.008), (POT_R * 1.04, BASE_Z + 0.04),
            (POT_R * 0.96, RIM_Z - 0.008), (POT_R, RIM_Z), (POT_R - 0.008, RIM_Z), (POT_R - 0.012, RIM_Z - 0.03)]
    rings = [[m.bm.verts.new(POT + V((r * math.cos(TAU * k / segs), r * math.sin(TAU * k / segs), z - FLOOR)))
              for k in range(segs)] for r, z in prof]
    fs = []
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            j = (k + 1) % segs
            fs.append(m.bm.faces.new((a[k], a[j], b[j], b[k])))
    fs.append(m.bm.faces.new(list(reversed(rings[0]))))
    bmesh.ops.recalc_face_normals(m.bm, faces=fs)
    m.tag(fs, "iron_dark")
    m.tag(fs[segs * 3: segs * 5], "iron")                                                     # the rim
    for k in range(3):
        a = TAU * k / 3 + 0.5
        d = V((math.cos(a), math.sin(a), 0))
        m.cyl(POT + d * POT_R * 0.6 + V((0, 0, (BASE_Z - FLOOR) / 2)), 0.008, BASE_Z - FLOOR, "iron_dark", segs=4)
    for k in range(9):                                                                         # hearth ring
        a = TAU * k / 9
        if abs(math.sin(a)) > 0.9 and math.sin(a) > 0:                                         # a gap on the raccoon's side
            continue
        d = V((math.cos(a), math.sin(a), 0))
        m.blob(POT + d * (POT_R + 0.035) + V((0, 0, 0.0)), V((0.03, 0.026, 0.026)), rnd.choice(["stone_mid", "stone_light"]), 6, 3)
    m.cyl(POT + V((0, 0, 0.002)), 0.07, 0.004, "soot", segs=8)
    for a in (0.4, 2.5, 4.4):                                                                  # logs under the pot
        d = V((math.cos(a), math.sin(a), 0))
        m.cyl(POT + d * 0.035 + V((0, 0, 0.012)), 0.011, 0.08, "wood_bark", axis=tuple(d), segs=5, cap="wood_cut")
    # ---- shelf of bottles (back left), herb rack (back right), table with mortar (left), smoke bombs (front right)
    sh = V((-0.5, 0.66, FLOOR))
    for x in (-0.3, 0.3):
        m.obox(sh + V((x, 0, 0.25)), (0.03, 0.1, 0.5), "wood_dark")
    for z in (0.12, 0.3, 0.48):
        m.obox(sh + V((0, 0, z)), (0.66, 0.12, 0.02), "wood_light")
        for k in range(5):
            if rnd.random() < 0.2:
                continue
            x = -0.25 + 0.125 * k + rnd.uniform(-0.02, 0.02)
            sw = rnd.choice(["teal_light", "amethyst", "ruby", "verdigris", "cloth_cream"])
            h = rnd.uniform(0.05, 0.08)
            m.cyl(sh + V((x, 0, z + 0.01 + h / 2)), 0.022, h, sw, segs=6, r2=0.018)
            m.cyl(sh + V((x, 0, z + 0.01 + h + 0.012)), 0.007, 0.024, "cloth_cream", segs=4)
    rk = V((0.5, 0.62, FLOOR))
    for x in (-0.3, 0.3):
        m.obox(rk + V((x, 0, 0.27)), (0.03, 0.03, 0.54), "wood_dark")
    m.beam(rk + V((-0.3, 0, 0.52)), rk + V((0.3, 0, 0.52)), 0.02, "wood_mid")
    tb = V((-0.48, -0.14, FLOOR))
    m.obox(tb + V((0, 0, 0.13)), (0.3, 0.22, 0.02), "wood_light")
    for dx in (-0.12, 0.12):
        for dy in (-0.08, 0.08):
            m.obox(tb + V((dx, dy, 0.06)), (0.025, 0.025, 0.12), "wood_dark")
    m.cyl(tb + V((0.04, 0.0, 0.17)), 0.045, 0.06, "stone_light", segs=8, r2=0.035, cap="moss")         # mortar of herbs
    m.cyl(tb + V((0.07, 0.01, 0.22)), 0.009, 0.08, "wood_cut", axis=(0.4, 0.1, 1), segs=5)            # pestle
    m.blob(tb + V((-0.08, 0.04, 0.155)), V((0.04, 0.03, 0.015)), "amethyst", 6, 3)                    # sleep powder
    bx = V((0.46, -0.42, FLOOR))
    m.obox(bx + V((0, 0, 0.05)), (0.24, 0.18, 0.1), "wood_mid", top="wood_dark")
    for k in range(4):                                                                         # smoke bombs
        c = bx + V((-0.06 + 0.08 * (k % 2), -0.03 + 0.06 * (k // 2), 0.12))
        m.blob(c, V((0.03, 0.03, 0.03)), "iron_dark", 7, 4)
        m.cyl(c + V((0, 0, 0.035)), 0.004, 0.02, "rope", segs=3)
    for c, sw in ((V((-0.32, -0.5)), "amethyst"), (V((-0.17, -0.6)), "cloth_cream")):         # sacks of powder
        B.sack(m, V((c.x, c.y, FLOOR)), 0.07, sw=sw if sw != "amethyst" else "burlap")
        if sw == "amethyst":
            m.blob(V((c.x, c.y, FLOOR + 0.13)), V((0.04, 0.035, 0.015)), "amethyst", 6, 3)
    bc = V((0.58, 0.16, FLOOR))
    m.cyl(bc + V((0, 0, 0.11)), 0.09, 0.22, "wood_mid", cap="water", segs=8)
    for z in (0.04, 0.18):
        m.cyl(bc + V((0, 0, z)), 0.095, 0.016, "iron", segs=8)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    m = B.M()
    m.cyl(V((POT.x, POT.y, BREW_Z - 0.003)), POT_R - 0.008, 0.006, "amethyst", segs=12)
    brew = m.obj("pr_brew", coll)
    brew.parent = root
    parts = {}
    # the swirl on the brew (turns with the ladle) and bubbles
    m = B.M()
    sc = V((POT.x, POT.y, BREW_Z + 0.0015))
    for k in range(3):
        a = TAU * k / 3
        p0 = sc + V((0.018 * math.cos(a), 0.018 * math.sin(a), 0))
        p1 = sc + V((0.05 * math.cos(a + 1.1), 0.05 * math.sin(a + 1.1), 0))
        m.beam(p0, p1, 0.006, "cloth_cream")
    parts["pr_swirl"] = A.part(m.obj("pr_swirl", coll), root, sc)
    for i, (dx, dy) in enumerate(((0.03, 0.02), (-0.035, -0.01), (0.0, -0.04), (-0.01, 0.04))):
        m = B.M()
        c = V((POT.x + dx, POT.y + dy, BREW_Z))
        m.blob(c, V((0.01, 0.01, 0.007)), "amethyst" if i % 2 else "cloth_cream", 6, 3)
        parts[f"pr_bubble_{i + 1}"] = A.part(m.obj(f"pr_bubble_{i + 1}", coll), root, c)
    for i in range(2):
        m = B.M()
        c = V((POT.x + 0.025 * (i - 0.5), POT.y - 0.035, RIM_Z + 0.02))          # the far side, off the face
        A.puff(m, c, 0.024)
        parts[f"pr_steam_{i + 1}"] = A.part(m.obj(f"pr_steam_{i + 1}", coll), root, c)
    for i, a in enumerate((0.9, 3.0, 5.0)):                                                     # flames under the pot
        m = B.M()
        c = POT + V((0.045 * math.cos(a), 0.045 * math.sin(a), 0.004))
        m.cyl(c + V((0, 0, 0.016)), 0.014, 0.032, "torch_orange" if i % 2 else "flame_yellow", segs=5, r2=0.0)
        parts[f"pr_flame_{i + 1}"] = A.part(m.obj(f"pr_flame_{i + 1}", coll), root, c)
    for i, (x, sw) in enumerate(((-0.18, "moss"), (0.0, "moss_light"), (0.18, "gold_dark"))):        # herb bundles
        m = B.M()
        top = rk + V((x, 0, 0.51))
        m.beam(top, top + V((0, 0, -0.04)), 0.005, "rope")
        m.cyl(top + V((0, 0, -0.085)), 0.03, 0.09, sw, segs=6, r2=0.01)
        parts[f"pr_herbs_{i + 1}"] = A.part(m.obj(f"pr_herbs_{i + 1}", coll), root, top)
    return root, brew, parts


def clips(parts):
    def common(p, boil):
        pose = {}
        for i in range(1, 5):                                          # bubbles swell and pop
            u = (p * (2 + boil) + i * 0.27) % 1.0
            pose[f"pr_bubble_{i}"] = (None, None, max(0.3 + 1.2 * u, 0.001) if u < 0.85 else 0.001)
        for i in (1, 2):                                               # steam rises and thins
            u = (p + i / 2) % 1.0
            pose[f"pr_steam_{i}"] = (V((0.02 * math.sin(TAU * u + i), -0.05 * u, 0.18 * u)), None,
                                     A.puff_size(u) * (0.8 + 0.3 * boil))
        for i, (f, ph) in enumerate(((3, 0.0), (4, 0.4), (5, 0.7))):
            pose[f"pr_flame_{i + 1}"] = (None, None, (1, 1, 1 + 0.25 * math.sin(TAU * (f * p + ph))))
        for i in range(1, 4):
            pose[f"pr_herbs_{i}"] = (None, A.q((1, 0.2, 0), 5 * math.sin(TAU * (p + 0.3 * i))), None)
        return pose

    def idle(p):
        pose = common(p, 0.0)
        pose["pr_swirl"] = (None, A.q((0, 0, 1), 60 * p), None)    # drifts slowly round
        return pose

    def work(p):
        pose = common(p, 1.0)
        pose["pr_swirl"] = (None, A.q((0, 0, 1), 720 * p), None)    # two turns a loop, with the ladle
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, brew, parts = build(coll, random.Random(81))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(brew) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(brew)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "brewery.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, ladle = A.raccoon_at(sp, clip="work_stir", tool="prop_ladle")
    allow = [("pr_swirl", "pr_brew")] + [(f"pr_bubble_{i}", "pr_brew") for i in range(1, 5)] + \
            [(f"pr_bubble_{i}", "pr_swirl") for i in range(1, 5)] + \
            [("pr_steam_1", NAME), ("pr_steam_2", NAME), ("pr_steam_1", "pr_steam_2")] + \
            [(f"pr_flame_{i}", NAME) for i in (1, 2, 3)] + [(f"pr_herbs_{i}", NAME) for i in (1, 2, 3)]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, ladle, "work", {"pr_brew": None, "pr_swirl": None,
                                                                **{f"pr_bubble_{i}": None for i in range(1, 5)}})],
                    allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, ladle], ROOT / "renders" / "bld_brewery_loops.gif",
                       target=(0.0, 0.05, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
