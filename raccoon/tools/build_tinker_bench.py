"""bld_tinker_bench_1x1: a low tinker's bench where lockpicks and gear are made (Tinkering).

Rebuilt at raccoon size (the first blockout's bench top was 0.38 m up, as tall as a raccoon): a low plank bench with a
bar of metal being worked, a vise, gears and a lamp. The raccoon crouches at it (spot_work,
facing the front), taps the bar with a small hammer (work_hammer, prop_hammer) and holds its end with the left paw.
A grindstone on a frame beside it, a rack of picks and wrenches on the other side.

Clips (24 fps)
  idle  32 fr  the lamp flickers, the grindstone turns slowly to a stop and on again
  work  32 fr  sparks jump from the bar on each hammer tap (frames 0 and 16), the grindstone spins

Start the building's work and the raccoon's work_hammer together (both 32 frames): the sparks fly on the taps.

Run:  python3 tools/build_tinker_bench.py   (--no-renders)
Out:  tinker_bench.blend, export/bld_tinker_bench_1x1.glb, renders/bld_tinker_bench_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_tinker_bench_1x1"
FRAMES = 32
FLOOR = 0.006
SPOT = V((0.07, 0.17, FLOOR + 0.0015))           # crouched at the bench, facing the front (-Y)
HIT = SPOT + J.HAM_HIT                           # where the hammer's face meets the bar
TOP = HIT.z - 0.018                              # the bench top; the bar (18 mm thick) sits on it
BENCH = (-0.24, 0.3, SPOT.y - 0.3, SPOT.y - 0.105)   # x0 x1 y0 y1: its back edge clears the crouching toes


def build(coll, rnd):
    m = B.M()
    # ---- floor boards
    for k in range(5):
        x = -0.47 + 0.94 * (k + 0.5) / 5
        m.obox(V((x, 0, FLOOR / 2)), (0.94 / 5 - 0.008, 0.94, FLOOR), "wood_mid" if k % 2 else "wood_light")
    # ---- the bench: plank top on four stubby legs, a shelf of scrap below
    x0, x1, y0, y1 = BENCH
    m.obox(V(((x0 + x1) / 2, (y0 + y1) / 2, TOP - 0.008)), (x1 - x0, y1 - y0, 0.016), "wood_light", top="wood_cut")
    for x in (x0 + 0.03, x1 - 0.03):
        for y in (y0 + 0.03, y1 - 0.03):
            m.obox(V((x, y, (TOP - 0.016) / 2)), (0.03, 0.03, TOP - 0.016), "wood_dark")
    m.cyl(V((0.2, y0 + 0.06, TOP + 0.012)), 0.028, 0.008, "rust", segs=8)                         # gears
    m.cyl(V((0.15, y0 + 0.1, TOP + 0.01)), 0.018, 0.006, "copper", segs=7)
    m.obox(V((-0.17, y0 + 0.06, TOP + 0.02)), (0.05, 0.05, 0.04), "iron", top="iron_light")      # vise
    m.obox(V((-0.17, y0 + 0.03, TOP + 0.022)), (0.06, 0.01, 0.03), "iron_dark")
    m.obox(V((0.0, y0 + 0.05, TOP + 0.008)), (0.08, 0.04, 0.016), "wood_dark")                   # box of picks
    for k in range(4):
        m.obox(V((-0.026 + 0.017 * k, y0 + 0.05, TOP + 0.02)), (0.004, 0.03, 0.006), "silver")
    # ---- grindstone on a frame (right), rack of tools (left)
    gs = V((0.36, -0.06, FLOOR))
    for y in (-0.035, 0.035):
        m.obox(gs + V((0, y, 0.07)), (0.03, 0.012, 0.14), "wood_dark")
    m.obox(gs + V((0, 0, 0.012)), (0.12, 0.1, 0.024), "wood_dark")
    rk = V((-0.38, 0.0, FLOOR))
    m.obox(rk + V((0, 0, 0.09)), (0.025, 0.26, 0.18), "wood_weathered")                         # a low tool board
    for side in (-1, 1):                                                                       # tools on both faces
        for k, (y, h, sw) in enumerate(((-0.09, 0.08, "iron_light"), (-0.03, 0.06, "silver"), (0.03, 0.09, "iron"),
                                        (0.09, 0.06, "copper"))):
            m.obox(rk + V((side * 0.017, y, 0.11)), (0.008, 0.012, h), sw)
    m.cyl(rk + V((0.03, 0.0, 0.035)), 0.05, 0.05, "wood_mid", segs=8, cap="iron_dark")          # bucket of scrap
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # the bar being worked (still): the hammer and the left paw touch it
    m = B.M()
    m.obox(V((HIT.x + 0.05, HIT.y + 0.007, TOP + 0.009)), (0.16, 0.05, 0.018), "iron_light")       # a bar, on the bench
    piece = m.obj("pr_piece", coll)
    piece.parent = root
    parts = {}
    m = B.M()                                                                         # grindstone wheel
    m.cyl(gs + V((0, 0, 0.15)), 0.1, 0.03, "stone_pale", axis=(0, 1, 0), segs=12, cap="stone_light")
    m.cyl(gs + V((0, 0, 0.15)), 0.012, 0.09, "iron_dark", axis=(0, 1, 0), segs=5)
    m.obox(gs + V((0, -0.05, 0.15)), (0.012, 0.012, 0.06), "iron_dark")                          # crank
    parts["pr_grindstone"] = A.part(m.obj("pr_grindstone", coll), root, gs + V((0, 0, 0.15)))
    m = B.M()                                                                         # the lamp's flame
    lc = V((0.24, y0 + 0.16, TOP))
    m.obox(lc + V((0, 0, 0.012)), (0.03, 0.03, 0.024), "iron_dark")
    root_lamp = lc + V((0, 0, 0.026))
    m.cyl(root_lamp + V((0, 0, 0.016)), 0.009, 0.032, "flame_yellow", segs=5, r2=0.0)
    parts["pr_lamp"] = A.part(m.obj("pr_lamp", coll), root, root_lamp)
    for i in range(3):                                                                 # sparks off the bar
        m = B.M()
        c = HIT + V((0, -0.01, 0.006))
        m.obox(c, (0.008, 0.008, 0.008), "flame_yellow" if i else "gold_glint", rot=(0.5, 0.5 * i, 0.3))
        parts[f"pr_spark_{i + 1}"] = A.part(m.obj(f"pr_spark_{i + 1}", coll), root, c)
    return root, piece, parts


def clips(parts):
    def idle(p):
        pose = {"pr_lamp": (None, A.q((0, 0, 1), 15 * math.sin(TAU * 3 * p)), (1, 1, 1 + 0.15 * math.sin(TAU * 4 * p)))}
        spin = 360 * (p - math.sin(TAU * p) / TAU)                     # turns once a loop, easing to a stop
        pose["pr_grindstone"] = (None, A.q((0, 1, 0), spin), None)
        for i in range(1, 4):
            pose[f"pr_spark_{i}"] = A.hidden()
        return pose

    def work(p):
        pose = idle(p)
        pose["pr_grindstone"] = (None, A.q((0, 1, 0), 720 * p), None)
        for i in range(1, 4):                                          # a burst on each tap (frames 0 and 16)
            u = (2 * p) % 1.0 / 0.3
            if u < 1:
                a = TAU * i / 3 + 0.4
                pose[f"pr_spark_{i}"] = (V((0.05 * math.cos(a) * u, -0.03 * u - 0.02 * math.sin(a) * u,
                                            0.06 * u - 0.07 * u * u)), A.q((1, 0, 0), 400 * u), max(1 - u, 0.001))
            else:
                pose[f"pr_spark_{i}"] = A.hidden()
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, piece, parts = build(coll, random.Random(91))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(piece) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(piece)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "tinker_bench.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, ham = A.raccoon_at(sp, clip="work_hammer", tool="prop_hammer")
    allow = [("pr_grindstone", NAME), ("pr_lamp", NAME)] + [(f"pr_spark_{i}", n) for i in (1, 2, 3)
                                                              for n in (NAME, "pr_piece")] + \
            [(f"pr_spark_{i}", f"pr_spark_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j]
    probs = A.check(root, 1, 1, crew=[(rig, mesh, ham, "work", {"pr_piece": None,
                                                              **{f"pr_spark_{i}": None for i in (1, 2, 3)}})],
                    allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, ham], ROOT / "renders" / "bld_tinker_bench_loops.gif",
                       target=(0.0, 0.0, 0.1), dist=2.2, pitch=42, idle_frames=16, grid_n=3)


if __name__ == "__main__":
    main()
