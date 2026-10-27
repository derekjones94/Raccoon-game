"""bld_cold_cellar_2x2: an earth-covered root cellar where the colony keeps its food cold.

A grassy mound with snow on it fills the back of the lot; its stone doorway (frosted, icicles on the lintel) has a
plank door. In front of the mound: an ice bin packed with snow, fish and apples. The raccoon crouches behind the bin
(spot_work, facing the front, the cellar door behind it on its right) and packs the food down (work_stash). A
barrel of salted fish, a string of drying fish, a sled.

Clips (24 fps)
  idle  48 fr  wisps of frosty breath curl out under the shut door, the string of fish sways
  work  48 fr  the door stands open and cold mist rolls out along the ground; the food in the bin settles each time
               the paws shove it down (work_stash's shoves)

Start the building's work and the raccoon's work_stash together (both 48 frames).

Run:  python3 tools/build_cold_cellar.py   (--no-renders)
Out:  cold_cellar.blend, export/bld_cold_cellar_2x2.glb, renders/bld_cold_cellar_loops.gif, renders/qa_buildings.txt
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
import build_stockpile as SP  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_cold_cellar_2x2"
FRAMES = 48
FLOOR = 0.006                                    # packed-earth yard
SPOT = V((0.28, -0.12, FLOOR + 0.0015))          # behind the ice bin, facing the front (-Y)
BIN = (SPOT.x - 0.16, SPOT.x + 0.16, SPOT.y - 0.31, SPOT.y - 0.1)
FACE_Y = 0.22                                    # front face of the doorway's stonework
DOOR = (-0.44, -0.18, 0.3)                       # doorway x0, x1, height
MOUND_C, MOUND_R = V((0.0, 0.62, 0.0)), V((0.9, 0.36, 0.5))
SHOVES = SP.SHOVES


def build(coll, rnd):
    m = B.M()
    # ---- yard: packed earth with patches of snow
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "rope_dark")
    for c, r in ((V((-0.7, -0.65)), (0.16, 0.1)), (V((0.72, -0.72)), (0.14, 0.12)), (V((-0.15, -0.8)), (0.12, 0.07)),
                 (V((0.75, 0.05)), (0.12, 0.16))):
        m.blob(V((c.x, c.y, FLOOR)), V((r[0], r[1], 0.008)), "stone_frost", 8, 2)
    # ---- the mound: earth, a grass cap, snow on top
    m.blob(MOUND_C, MOUND_R, "wood_dark", 12, 5)
    m.blob(MOUND_C + V((0, 0.02, 0.06)), V((0.82, 0.3, 0.46)), "moss", 12, 4)
    m.blob(MOUND_C + V((0.05, 0.04, 0.3)), V((0.55, 0.2, 0.21)), "stone_frost", 10, 4)
    # ---- the doorway: stone jambs and lintel in a stone face set into the mound, a dark way down behind
    x0, x1, h = DOOR
    fd = 0.1
    yc = FACE_Y + fd / 2
    for x, w in ((x0 - 0.07, 0.14), (x1 + 0.07, 0.14)):
        for k in range(3):
            m.obox(V((x + (0.01 if k % 2 else -0.01), yc, 0.05 + 0.1 * k)), (w, fd, 0.1), "stone_light" if k % 2 else "stone_pale",
                   top="stone_frost")
    m.obox(V(((x0 + x1) / 2, yc, h + 0.04)), (x1 - x0 + 0.3, fd + 0.01, 0.08), "stone_pale", top="stone_frost")
    m.obox(V(((x0 + x1) / 2, FACE_Y + fd, h / 2)), (x1 - x0, 0.01, h), "soot")                       # the dark inside
    m.obox(V(((x0 + x1) / 2, FACE_Y + 0.05, FLOOR + 0.006)), (x1 - x0, fd, 0.012), "stone_mid")       # threshold
    for k in range(5):                                                                                # icicles
        x = x0 - 0.1 + k * (x1 - x0 + 0.2) / 4
        L = 0.03 + 0.02 * (k % 2)
        m.cyl(V((x, FACE_Y - 0.002, h - L / 2)), 0.007, L, "stone_frost", segs=4, r2=0.0, rot=0.4)
    # ---- beside the door: a barrel of salted fish, a post with the drying line; a sled at the front
    bc = V((-0.72, 0.1, FLOOR))
    m.cyl(bc + V((0, 0, 0.11)), 0.09, 0.22, "wood_mid", cap="stone_frost", segs=8)
    for z in (0.04, 0.18):
        m.cyl(bc + V((0, 0, z)), 0.095, 0.016, "iron", segs=8)
    for k in range(3):
        m.cyl(bc + V((-0.03 + 0.03 * k, 0.0, 0.235)), 0.012, 0.05, "silver", axis=(0.3 * (k - 1), 0.2, 1), segs=4, r2=0.004)
    m.obox(V((0.0, 0.14, 0.2)), (0.035, 0.035, 0.4), "wood_dark")                                   # drying post
    sl = V((-0.48, -0.55, FLOOR))
    for s in (-1, 1):
        m.beam(sl + V((-0.18, s * 0.08, 0.012)), sl + V((0.16, s * 0.08, 0.012)), 0.014, "wood_dark")   # runners
        m.beam(sl + V((0.16, s * 0.08, 0.012)), sl + V((0.21, s * 0.08, 0.05)), 0.014, "wood_dark")
    m.obox(sl + V((0, 0, 0.04)), (0.3, 0.2, 0.014), "wood_light")
    B.sack(m, sl + V((-0.04, 0.0, 0.047)), 0.055, sw="cloth_cream")
    m.cyl(sl + V((0.08, 0.02, 0.07)), 0.035, 0.05, "cloth_mustard", segs=8, cap="cloth_cream")         # cheese wheel
    # ---- the ice bin
    SP.packing_crate(m, BIN, FLOOR, sw="wood_weathered")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # the bin's contents (still): snow, fish, apples; the paws may press into them
    m = B.M()
    bx0, bx1, by0, by1 = BIN
    W = SP.WALL
    m.obox(V(((bx0 + bx1) / 2, (by0 + by1) / 2, FLOOR + 0.035)), (bx1 - bx0 - 2 * W - 0.004, by1 - by0 - 2 * W - 0.004, 0.05),
           "stone_frost")
    for k in range(7):
        p = V((rnd.uniform(bx0 + 0.04, bx1 - 0.04), rnd.uniform(by0 + 0.04, by1 - 0.04), FLOOR + 0.062))
        if k < 4:
            m.blob(p, V((0.04, 0.012, 0.01)), "silver" if k % 2 else "iron_light", 6, 3)        # fish on the snow
        else:
            m.blob(p, V((0.02, 0.02, 0.017)), "cloth_red", 6, 3)
    goods = m.obj("pr_ice", coll)
    goods.parent = root
    parts = {}
    # the door, hinged on its left
    m = B.M()
    m.obox(V(((x0 + x1) / 2, FACE_Y - 0.012, h / 2 + 0.003)), (x1 - x0 - 0.008, 0.02, h - 0.006), "wood_mid")
    for z in (0.07, 0.23):
        m.obox(V(((x0 + x1) / 2, FACE_Y - 0.024, z)), (x1 - x0 - 0.02, 0.006, 0.022), "iron_dark")
    m.cyl(V((x1 - 0.04, FACE_Y - 0.03, h * 0.5)), 0.01, 0.012, "iron_light", axis=(0, 1, 0), segs=6)    # pull ring
    parts["pr_door"] = A.part(m.obj("pr_door", coll), root, V((x0 + 0.004, FACE_Y - 0.012, 0)))
    # frost: wisps that curl out from under the shut door (idle), mist rolling out of the open door (work)
    for i in range(3):
        m = B.M()
        c = V((x0 + 0.06 + 0.07 * i, FACE_Y - 0.03, FLOOR + 0.025))
        m.blob(c, V((0.05, 0.035, 0.022)), "stone_frost", 7, 3)
        parts[f"pr_mist_{i + 1}"] = A.part(m.obj(f"pr_mist_{i + 1}", coll), root, c)
    # food on top of the bin that settles
    for i, (dx, dy, kind) in enumerate(((-0.06, 0.05, "fish"), (0.07, 0.07, "apple"), (0.01, -0.05, "fish"))):
        c = V(((bx0 + bx1) / 2 + dx, (by0 + by1) / 2 + dy, FLOOR + 0.072))
        m = B.M()
        if kind == "fish":
            m.blob(c, V((0.045, 0.014, 0.012)), "silver", 7, 3)
            m.obox(c + V((0.05, 0, 0)), (0.018, 0.004, 0.02), "iron_light")                         # tail fin
        else:
            m.blob(c, V((0.022, 0.022, 0.02)), "cloth_red", 7, 4)
        parts[f"pr_food_{i + 1}"] = A.part(m.obj(f"pr_food_{i + 1}", coll), root, c)
    # the string of drying fish, from the post to the mound
    m = B.M()
    top = V((0.0, 0.14, 0.4))
    m.beam(top, top + V((0.0, -0.0, -0.02)), 0.006, "rope")
    for k in range(3):
        c = top + V((0, 0, -0.045 - 0.065 * k))
        m.blob(c, V((0.014, 0.008, 0.028)), "pewter" if k % 2 else "silver", 6, 3)
        m.cyl(c + V((0, 0, 0.025)), 0.003, 0.03, "rope", segs=3)
    parts["pr_fish_string"] = A.part(m.obj("pr_fish_string", coll), root, top)
    return root, goods, parts


def clips(parts):
    def common(p):
        pose = {}
        pose["pr_fish_string"] = (None, A.q((1, 0.2, 0), 7 * math.sin(TAU * p)) @ A.q((0, 0, 1), 12 * math.sin(TAU * p + 1)), None)
        return pose

    def idle(p):
        pose = common(p)
        pose["pr_door"] = (None, None, None)
        for i in range(1, 4):                              # thin wisps from under the door: out, up, gone
            u = (p + i / 3) % 1.0
            s = math.sin(math.pi * u)
            pose[f"pr_mist_{i}"] = (V((0.02 * math.sin(TAU * u + i), -0.07 * u, 0.012 * u)), None,
                                    (max(0.5 * s, 0.001), max(0.5 * s, 0.001), max(0.4 * s, 0.001)))
        return pose

    def work(p):
        pose = common(p)
        pose["pr_door"] = (None, A.q((0, 0, 1), -100 + 2 * math.sin(TAU * p)), None)     # swung wide open, creaking
        for i in range(1, 4):                              # big cold puffs roll out along the ground and thin away
            u = (p + i / 3) % 1.0
            s = math.sin(math.pi * u)
            pose[f"pr_mist_{i}"] = (V((0.03 * math.sin(TAU * u + i) - 0.04 * u, -0.2 * u, 0.008 * u)), None,
                                    (max(1.4 * s, 0.001), max(1.2 * s, 0.001), max(0.9 * s, 0.001)))
        for i, ph in ((1, 0.0), (2, 0.03), (3, 0.015)):
            hh = sum(math.exp(-((p - c - ph) ** 2) / 0.0015) for c in SHOVES)
            pose[f"pr_food_{i}"] = (V((0, 0, -0.006 * hh)), A.q((1, 0.5 * i, 0), 7 * hh * math.sin(TAU * 4 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, goods, parts = build(coll, random.Random(51))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(goods) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(goods)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "cold_cellar.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_stash")
    allow = [("pr_door", NAME), ("pr_fish_string", NAME)] + [(f"pr_mist_{i}", NAME) for i in (1, 2, 3)] + \
            [(f"pr_mist_{i}", f"pr_mist_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j] + \
            [(f"pr_mist_{i}", "pr_door") for i in (1, 2, 3)] + [(f"pr_food_{i}", "pr_ice") for i in (1, 2, 3)]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, None, "work", {"pr_ice": None, "pr_food_1": None, "pr_food_2": None,
                                                               "pr_food_3": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_cold_cellar_loops.gif",
                       target=(0.0, 0.05, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
