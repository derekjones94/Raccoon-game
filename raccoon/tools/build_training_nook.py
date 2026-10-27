"""bld_training_nook_2x2: where an elder teaches the kits the trade (Mentoring).

A swept floor with a rug. At the back the elder stands beside a slate on an easel (at his left, side-on to the class),
chalk drawings of a lock and a key on it (spot_elder, facing the class: work_teach on chr_raccoon_elder, with his cane prop_cane in his right paw as always).
Three kits sit on cushions in a row facing him (spot_kit_1..3: work_listen on chr_raccoon_kit). A straw practice dummy
with a purse on its belt, a low shelf of books, a box of practice locks.

Clips (24 fps)
  idle  96 fr  the dummy rocks a little, the purse swings, a lantern sways
  work  96 fr  (class is on) as idle, plus the slate rattles on its easel when the elder taps it (frames 23 and 30)

Start the building's work with the elder's work_teach (both 96 frames): the slate rattles on his taps. The kits'
work_listen can start whenever (offset them).

Run:  python3 tools/build_training_nook.py   (--no-renders)
Out:  training_nook.blend, export/bld_training_nook_2x2.glb, renders/bld_training_nook_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_training_nook_2x2"
FRAMES = 96
FLOOR = 0.008
RUG_TOP = FLOOR + 0.0025
ELDER = V((-0.12, 0.38, RUG_TOP + 0.0015))        # the elder at the back, facing the class (-Y)
TAP = ELDER + J.TEACH_BOARD                       # where his claw taps the slate (raccoon space == building space)
SLATE_X = TAP.x + 0.02                            # the slate stands at his left, its face toward him (-X), side-on
KITS = [V((x, -0.12, RUG_TOP + 0.0015)) for x in (-0.42, -0.12, 0.18)]


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "wood_light")
    m.obox(V((-0.12, 0.05, FLOOR + 0.001)), (1.0, 0.9, 0.002), "cloth_blue")                         # rug, top RUG_TOP
    m.obox(V((-0.12, 0.05, FLOOR + 0.0015)), (0.9, 0.8, 0.002), "teal_dark")
    # ---- the easel, to the elder's left: two legs behind the slate, a ledge with chalk at its foot
    sy0, sy1 = TAP.y - 0.17, TAP.y + 0.05            # the slate runs from beside him toward the class
    sz0, sz1 = 0.12, 0.3
    for y in (sy0 + 0.02, sy1 - 0.02):
        m.beam(V((SLATE_X + 0.07, y, FLOOR)), V((SLATE_X + 0.012, y, sz1 + 0.04)), 0.012, "wood_dark")
    m.beam(V((SLATE_X + 0.12, (sy0 + sy1) / 2, FLOOR)), V((SLATE_X + 0.02, (sy0 + sy1) / 2, sz1 + 0.02)), 0.012, "wood_dark")
    m.obox(V((SLATE_X + 0.006, (sy0 + sy1) / 2, sz0 - 0.01)), (0.03, sy1 - sy0 + 0.03, 0.012), "wood_mid")
    m.cyl(V((SLATE_X - 0.004, (sy0 + sy1) / 2 - 0.06, sz0)), 0.004, 0.03, "cloth_cream", axis=(0, 1, 0), segs=4)
    # ---- cushions for the kits, facing the elder
    for k, c in enumerate(KITS):
        m.cyl(V((c.x, c.y + 0.03, FLOOR + 0.0005)), 0.11, 0.001, ["cloth_red", "cloth_mustard", "cloth_red"][k], segs=10)
    # ---- the practice dummy (right), a shelf of books (left), a box of practice locks (front)
    bs = V((-0.82, 0.3, FLOOR))
    m.obox(bs + V((-0.05, 0, 0.15)), (0.02, 0.42, 0.3), "wood_dark")                                    # back panel
    for y in (-0.2, 0.2):
        m.obox(bs + V((0, y, 0.15)), (0.12, 0.02, 0.3), "wood_dark")
    m.obox(bs + V((0, 0, 0.295)), (0.12, 0.42, 0.02), "wood_dark")
    for z in (0.06, 0.2):
        m.obox(bs + V((0.005, 0, z)), (0.1, 0.38, 0.014), "wood_light")
        for k in range(6):
            h = rnd.uniform(0.06, 0.1)
            m.obox(bs + V((0.01, -0.16 + 0.065 * k, z + 0.007 + h / 2)), (0.07, 0.045, h), rnd.choice(["cloth_red", "cloth_blue", "leather", "moss", "cloth_mustard"]))
    lb = V((0.3, -0.7, FLOOR))
    m.obox(lb + V((0, 0, 0.04)), (0.26, 0.16, 0.08), "wood_mid", top="wood_dark")
    for k in range(3):
        c = lb + V((-0.08 + 0.08 * k, 0, 0.09))
        m.obox(c, (0.04, 0.025, 0.035), ["iron", "gold_dark", "copper"][k])                        # padlocks
        m.cyl(c + V((0, 0, 0.025)), 0.014, 0.006, "iron_light", axis=(0, 1, 0), segs=6)
    pole = V((0.78, 0.68, FLOOR))
    m.obox(pole + V((0, 0, 0.3)), (0.03, 0.03, 0.6), "wood_dark")                                   # lantern pole
    m.beam(pole + V((0, 0, 0.58)), pole + V((-0.14, 0, 0.58)), 0.015, "wood_dark")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    # the slate: its own moving part (rattles when tapped); chalk drawings of a lock and a key on its face (-X)
    mm = B.M()
    mm.obox(V((SLATE_X + 0.008, (sy0 + sy1) / 2, (sz0 + sz1) / 2)), (0.016, sy1 - sy0, sz1 - sz0), "wood_mid")
    mm.obox(V((SLATE_X + 0.003, (sy0 + sy1) / 2, (sz0 + sz1) / 2)), (0.008, sy1 - sy0 - 0.03, sz1 - sz0 - 0.03), "soot")
    lc = V((SLATE_X - 0.0015, TAP.y - 0.1, 0.21))
    mm.obox(lc, (0.002, 0.05, 0.04), "cloth_cream")                                                    # lock body
    mm.obox(lc + V((0, 0, 0.034)), (0.002, 0.04, 0.03), "cloth_cream")
    mm.obox(lc + V((-0.0005, 0, 0.032)), (0.0025, 0.028, 0.022), "soot")
    kc = V((SLATE_X - 0.0015, TAP.y + 0.0, 0.25))
    mm.obox(kc, (0.002, 0.06, 0.008), "cloth_cream")                                                   # key
    mm.obox(kc + V((0, -0.035, 0)), (0.002, 0.02, 0.02), "cloth_cream")
    mm.obox(kc + V((0, 0.02, -0.01)), (0.002, 0.008, 0.012), "cloth_cream")
    parts["pr_slate"] = A.part(mm.obj("pr_slate", coll), root, V((SLATE_X + 0.02, (sy0 + sy1) / 2, sz0 - 0.004)))
    # the dummy: a post with a straw body and a sack head, rocking on its base; a purse on its belt
    dp = V((0.62, 0.15, FLOOR))
    mm = B.M()
    mm.cyl(dp + V((0, 0, 0.02)), 0.07, 0.04, "wood_dark", segs=8)
    mm.obox(dp + V((0, 0, 0.15)), (0.025, 0.025, 0.24), "wood_mid")
    mm.blob(dp + V((0, 0, 0.2)), V((0.06, 0.05, 0.08)), "burlap", 8, 4)
    mm.blob(dp + V((0, 0, 0.31)), V((0.045, 0.045, 0.045)), "burlap", 8, 4)
    mm.beam(dp + V((-0.12, 0, 0.24)), dp + V((0.12, 0, 0.24)), 0.012, "wood_mid")
    mm.cyl(dp + V((0, 0, 0.165)), 0.062, 0.012, "leather_dark", segs=8)                               # belt
    dummy = A.part(mm.obj("pr_dummy", coll), root, dp)
    parts["pr_dummy"] = dummy
    mm = B.M()
    pt = dp + V((0.0, -0.062, 0.162))
    mm.beam(pt, pt + V((0, -0.006, -0.025)), 0.003, "leather_dark")
    mm.blob(pt + V((0, -0.008, -0.045)), V((0.02, 0.014, 0.024)), "gold_dark", 6, 4)
    parts["pr_purse"] = A.part(mm.obj("pr_purse", coll), root, pt)
    mm = B.M()
    lt = pole + V((-0.14, 0, 0.57))
    mm.cyl(lt + V((0, 0, -0.02)), 0.003, 0.04, "iron_dark", segs=4)
    mm.obox(lt + V((0, 0, -0.065)), (0.05, 0.05, 0.06), "flame_yellow")
    mm.obox(lt + V((0, 0, -0.035)), (0.06, 0.06, 0.012), "iron_dark")
    parts["pr_lantern"] = A.part(mm.obj("pr_lantern", coll), root, lt)
    return root, parts


def clips(parts):
    def common(p):
        rock = 3 * math.sin(TAU * p)
        return {"pr_dummy": (None, A.q((1, 0.2, 0), rock), None),
                "pr_purse": (None, A.q((1, 0, 0), 12 * math.sin(TAU * (2 * p - 0.15)) + rock), None),
                "pr_lantern": (None, A.q((1, 0.3, 0), 4 * math.sin(TAU * (2 * p + 0.2))), None)}

    def idle(p):
        pose = common(p)
        pose["pr_slate"] = (None, None, None)
        return pose

    def work(p):
        pose = common(p)
        hit = sum(math.exp(-((p - c - 0.004) ** 2) / 0.0004) for c in (0.24, 0.31))
        pose["pr_slate"] = (None, A.q((0, 1, 0), 2.5 * hit * math.sin(TAU * 12 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(141))
    A.spot(root, "spot_elder", ELDER, (0, -1, 0))
    for i, c in enumerate(KITS):
        A.spot(root, f"spot_kit_{i + 1}", c, (ELDER.x - c.x, ELDER.y - c.y, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris (moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "training_nook.blend"), relative_remap=True)
    A.export()
    rig, mesh, cane = A.raccoon_at(bpy.data.objects["spot_elder"], variant="chr_raccoon_elder", clip="work_teach",
                                   tool="prop_cane", tool_blend="prop_cane.blend")
    crew, objs = [(rig, mesh, cane, "work", {"pr_slate": None})], [rig, mesh, cane]
    for i in range(len(KITS)):
        r2, m2, _ = A.raccoon_at(bpy.data.objects[f"spot_kit_{i + 1}"], variant="chr_raccoon_kit", clip="work_listen")
        crew.append((r2, m2, None, "work", {}))
        objs += [r2, m2]
    allow = [("pr_slate", NAME), ("pr_dummy", NAME), ("pr_purse", "pr_dummy"), ("pr_lantern", NAME)]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_training_nook_loops.gif",
                       target=(0.0, 0.05, 0.15), dist=3.6, pitch=42, idle_frames=24, grid_n=4, step=3)


if __name__ == "__main__":
    main()
