"""bld_rubble_heap_2x2: where diggers dump what they bring up: stone, ore, wood and scrap, roughly sorted.

The main heap of broken stone in the middle; the raccoon sorts through it from behind (spot_work, facing the front:
from the game camera its face shows over the heap) with work_rummage. Round it: a bay of ore (copper and rust
chunks, a glint of gold), a stack of planks and props, a barrel of scrap iron, a wheelbarrow of stones and a pick.

Clips (24 fps)
  idle  48 fr  pebbles trickle down the heap's front now and then, roll a little and settle
  work  48 fr  as idle, plus stones near the raccoon's paws jostle as it digs, and a puff of dust rises

Run:  python3 tools/build_rubble_heap.py   (--no-renders)
Out:  rubble_heap.blend, export/bld_rubble_heap_2x2.glb, renders/bld_rubble_heap_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_rubble_heap_2x2"
FRAMES = 48
FLOOR = 0.006
SPOT = V((0.12, 0.36, FLOOR + 0.0015))           # behind the heap, facing the front (-Y)
# the same heap shape the rummage camp proved against work_rummage: a near part the paws reach, the bulk beyond
HEAP_C = V((SPOT.x, SPOT.y - 0.217, 0.0))
HEAP_R = RC.HEAP_R
BIG_C = V((HEAP_C.x - 0.02, HEAP_C.y - 0.17, 0.0))
BIG_R = V((0.3, 0.22, 0.24))


def hp(ang, hf, big=True):
    return RC.heap_point(math.radians(ang), hf, BIG_C if big else HEAP_C, BIG_R if big else HEAP_R)


def chunk(m, p, n, s, sw, rnd):
    """An angular stone chunk sitting on a surface point p with normal n."""
    m.obox(p + n * s * 0.35, (s, s * rnd.uniform(0.6, 0.9), s * rnd.uniform(0.5, 0.8)), sw,
           rot=(rnd.uniform(0, 1), rnd.uniform(0, 1), rnd.uniform(0, 3)))


def build(coll, rnd):
    m = B.M()
    # ---- trampled ground
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "wood_weathered")                         # dusty earth
    for k in range(6):
        p = V((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.85, 0.85), FLOOR))
        if (p.xy - HEAP_C.xy).length < 0.5 or (p.xy - SPOT.xy).length < 0.25:
            continue
        chunk(m, p, V((0, 0, 1)), rnd.uniform(0.025, 0.04), rnd.choice(["stone_mid", "stone_light"]), rnd)
    # ---- ore bay (front right): three low stone walls, copper and rust chunks, a glint of gold
    oc = V((0.62, -0.5, FLOOR))
    for (c, size) in (((0.0, 0.2), (0.44, 0.06)), ((-0.2, 0.0), (0.06, 0.38)), ((0.2, 0.0), (0.06, 0.38))):
        m.obox(oc + V((c[0], c[1], 0.05)), (size[0], size[1], 0.1), "stone_mid", top="stone_light")
    m.blob(oc + V((0, -0.02, 0)), V((0.15, 0.15, 0.07)), "rust_dark", 8, 3)
    for k in range(6):
        a = k * 1.1
        p, n = oc + V((0.08 * math.cos(a), -0.02 + 0.08 * math.sin(a), 0.05)), V((math.cos(a) * 0.3, math.sin(a) * 0.3, 1))
        chunk(m, p, n.normalized(), 0.04, ["copper", "rust", "copper", "gold"][k % 4] if k != 5 else "gold_light", rnd)
    # ---- planks and props (left): a stack on bearers, two posts holding it
    wc = V((-0.62, 0.3, FLOOR))
    for y in (-0.16, 0.16):
        m.obox(wc + V((0, y, 0.015)), (0.42, 0.04, 0.03), "wood_dark")
    for k in range(4):
        m.obox(wc + V((rnd.uniform(-0.01, 0.01), 0, 0.04 + 0.022 * k)), (0.5, 0.11 - 0.012 * k, 0.018),
               ["wood_light", "wood_mid", "wood_weathered", "wood_light"][k], rot=(0, 0, rnd.uniform(-0.05, 0.05)))
    for k in range(3):
        B.log(m, wc + V((0, 0.24 + 0.0 * k, 0.04 + 0.075 * k)) + V((0.0, -0.01 * k, 0)), 0.035, 0.46)
    for x in (-0.27, 0.27):
        m.obox(wc + V((x, 0.24, 0.13)), (0.03, 0.03, 0.26), "wood_dark")
    m.beam(wc + V((0.3, -0.25, 0.005)), wc + V((0.22, -0.16, 0.28)), 0.012, "wood_light")             # pick handle
    m.obox(wc + V((0.25, -0.19, 0.27)), (0.11, 0.02, 0.022), "iron", rot=(0.0, 0.25, 0.85))            # pick head
    # ---- scrap barrel (back right) and a wheelbarrow of stones (front left)
    bc = V((0.68, 0.6, FLOOR))
    m.cyl(bc + V((0, 0, 0.11)), 0.1, 0.22, "iron", cap="iron_dark", segs=8)
    m.cyl(bc + V((0, 0, 0.2)), 0.105, 0.016, "rust", segs=8)
    for k in range(3):
        m.obox(bc + V((-0.03 + 0.03 * k, 0.01 * k, 0.24)), (0.03, 0.06, 0.01), ["iron_light", "rust", "copper"][k],
               rot=(0.5 * k, 0.3, 0.4 * k))
    m.cyl(bc + V((0.02, -0.02, 0.25)), 0.012, 0.09, "iron_dark", axis=(0.3, 0.2, 1), segs=4)
    wb = V((-0.6, -0.55, FLOOR))
    m.obox(wb + V((0.02, 0, 0.1)), (0.24, 0.17, 0.07), "wood_mid", top="stone_mid")                  # tray (full)
    m.cyl(wb + V((0.17, 0, 0.055)), 0.05, 0.02, "iron_dark", axis=(0, 1, 0), segs=8)                   # wheel
    for s in (-1, 1):
        m.beam(wb + V((-0.1, s * 0.07, 0.08)), wb + V((-0.28, s * 0.09, 0.1)), 0.016, "wood_dark")      # handles
        m.obox(wb + V((-0.08, s * 0.06, 0.03)), (0.02, 0.02, 0.06), "wood_dark")                     # legs
    for k in range(4):
        chunk(m, wb + V((-0.06 + 0.05 * k, 0.03 * (k % 2) - 0.015, 0.14)), V((0, 0, 1)), 0.04, "stone_light", rnd)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- the heap (still): the paws may dig into it, nothing else
    m = B.M()
    m.blob(HEAP_C, HEAP_R, "stone_light", 12, 6)
    m.blob(BIG_C, BIG_R, "stone_mid", 12, 6)
    m.blob(BIG_C + V((0.18, 0.04, 0)), V((0.15, 0.14, 0.16)), "stone_light", 10, 5)
    for k in range(16):                                                 # chunks on it, off the dig spot (the back)
        ang = rnd.uniform(-200, 20)
        hf = rnd.uniform(0.15, 0.85)
        p, n = hp(ang, hf)
        chunk(m, p, n, rnd.uniform(0.035, 0.06), rnd.choice(["stone_light", "stone_mid", "stone_pale", "stone_light"]), rnd)
    for ang, hf, sw in ((-40, 0.5, "copper"), (-140, 0.35, "rust"), (-95, 0.75, "wood_light")):        # strays
        p, n = hp(ang, hf)
        chunk(m, p, n, 0.04, sw, rnd)
    heap = m.obj("pr_heap", coll)
    PR.trim_below_floor(heap)
    heap.parent = root
    parts = {}
    # pebbles that trickle down the front of the heap
    for i, ang in enumerate((-100, -70, -125)):
        m = B.M()
        p, n = hp(ang, 0.97)
        c = p + n * 0.014
        m.blob(c, V((0.014, 0.012, 0.011)), "stone_light" if i % 2 else "stone_pale", 5, 3)
        parts[f"pr_pebble_{i + 1}"] = A.part(m.obj(f"pr_pebble_{i + 1}", coll), root, c)
    # stones by the dig spot that jostle while the raccoon digs (either side of its reach)
    for i, (ang, hf) in enumerate(((55, 0.62), (128, 0.6))):
        m = B.M()
        p, n = hp(ang, hf, big=False)
        c = p + n * 0.016
        m.obox(c, (0.03, 0.024, 0.02), "stone_light", rot=(0.3, 0.2, 0.5 * i))
        parts[f"pr_stone_{i + 1}"] = A.part(m.obj(f"pr_stone_{i + 1}", coll), root, c)
    # a puff of dust over the dig spot
    m = B.M()
    dc = V((SPOT.x, SPOT.y - 0.23, 0.1))                    # just beyond the paws, below the snout
    m.blob(dc, V((0.035, 0.03, 0.025)), "stone_pale", 7, 3)
    parts["pr_dust"] = A.part(m.obj("pr_dust", coll), root, dc)
    return root, heap, parts


def pebble_path(ang, u):
    """Offset of a trickling pebble from its start at loop fraction u: rolls down the heap's front, a short roll on
    the ground, settles, then sinks out of sight before the next."""
    start = hp(ang, 0.97)
    start = start[0] + start[1] * 0.014
    if u < 0.55:
        hf = 0.97 * (1 - (u / 0.55) ** 1.6)
        p, n = hp(ang, hf)
        pos = p + n * 0.014
    else:
        p, n = hp(ang, 0.0)
        out = V((n.x, n.y, 0)).normalized()
        pos = p + out * (0.014 + 0.05 * min((u - 0.55) / 0.15, 1.0) ** 0.5) + V((0, 0, 0.011))
    pos.z = max(pos.z, FLOOR + 0.0115)                   # never below the ground
    return pos - start


def clips(parts):
    def common(p):
        pose = {}
        for i, (ang, ph) in enumerate(((-100, 0.0), (-70, 0.37), (-125, 0.7))):
            u = (p + ph) % 1.0
            off = pebble_path(ang, u)
            roll = 900 * min(u / 0.7, 1.0)
            sc = 1.0 if u < 0.85 else max(1 - (u - 0.85) / 0.1, 0.001) if u < 0.95 else 0.001
            if u >= 0.95:                                         # grows back at the top of the heap
                sc = max((u - 0.95) / 0.05, 0.001)
                off = V()
                roll = 0
            pose[f"pr_pebble_{i + 1}"] = (off, A.q((1, 0.3, 0), roll), sc)
        return pose

    def idle(p):
        pose = common(p)
        pose["pr_dust"] = A.hidden()
        return pose

    def work(p):
        pose = common(p)
        for i, ph in ((1, 0.85), (2, 0.35)):                     # each paw's dig (work_rummage: right .2-.5, left .7-1)
            j = math.exp(-((((p - ph) + 0.5) % 1.0 - 0.5) ** 2) / 0.003)
            pose[f"pr_stone_{i}"] = (V((0, 0, 0.005 * j)), A.q((1, 0.4 * i, 0.2), 10 * j * math.sin(TAU * 6 * p)), None)
        u = ((p - 0.3) * 2) % 1.0                                # a puff on each dig
        pose["pr_dust"] = (V((0, -0.05 * u, 0.04 * u)), None, max(1.6 * math.sin(math.pi * u) * (1 - u), 0.001))
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, heap, parts = build(coll, random.Random(61))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(heap) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(heap)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "rubble_heap.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_rummage")
    allow = [(f"pr_pebble_{i}", n) for i in (1, 2, 3) for n in ("pr_heap", NAME)] + \
            [(f"pr_stone_{i}", "pr_heap") for i in (1, 2)] + [("pr_dust", "pr_heap")]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, None, "work", {"pr_heap": None, "pr_stone_1": None,
                                                               "pr_stone_2": None, "pr_dust": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_rubble_heap_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
