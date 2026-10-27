"""bld_map_room_2x2: where raccoons pore over maps and plan their raids (Sniffing / research).

A rug-covered nook with a low table spread with a big map (weighted with a mug and a stone), a candle on it, rolled
maps in a barrel, a pin-board of charts with string between the pins, a bookshelf, a lantern. Two raccoons can read
the map from either side (spot_work_1 at the back facing the front, spot_work_2 at the front facing the back), both
with work_read: crouched over the map, paws holding it flat, one paw tracing a route.

Clips (24 fps)
  idle  48 fr  the candle flickers, the map's loose corner and the charts on the board flutter, the hanging map sways
  work  48 fr  as idle; a pin on the board jiggles as plans are made (the readers' paws trace the route)

Run:  python3 tools/build_map_room.py   (--no-renders)
Out:  map_room.blend, export/bld_map_room_2x2.glb, renders/bld_map_room_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_map_room_2x2"
FRAMES = 48
FLOOR = 0.008
TABLE_C = V((-0.08, 0.0, 0.0))
GAP = 0.105                                       # from each reader's spot to the table edge (clears the toes)
DEPTH = 0.28                                      # the table, front to back
RUG_TOP = FLOOR + 0.0025
SPOTS = [(V((TABLE_C.x, TABLE_C.y + DEPTH / 2 + GAP, RUG_TOP + 0.0015)), (0, -1, 0)),     # at the back, facing front
         (V((TABLE_C.x + 0.05, TABLE_C.y - DEPTH / 2 - GAP, RUG_TOP + 0.0015)), (0, 1, 0))]  # at the front, facing back
MAP_TOP = RUG_TOP + 0.0015 + J.READ_C.z - 0.025   # the map top: the paws (2.5 cm deep under the hand slot) rest on it
TABLE_W = 0.62


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "wood_mid")
    m.obox(V((TABLE_C.x, TABLE_C.y, FLOOR + 0.001)), (1.1, 0.95, 0.002), "cloth_red")              # rug
    m.obox(V((TABLE_C.x, TABLE_C.y, FLOOR + 0.0015)), (1.0, 0.85, 0.002), "cloth_mustard")
    # ---- the low table: top, four legs
    tz = MAP_TOP - 0.003
    m.obox(V((TABLE_C.x, TABLE_C.y, tz - 0.01)), (TABLE_W, DEPTH, 0.02), "wood_dark", top="wood_mid")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.obox(V((TABLE_C.x + sx * (TABLE_W / 2 - 0.04), TABLE_C.y + sy * (DEPTH / 2 - 0.04), (tz - 0.02 + FLOOR) / 2)),
                   (0.03, 0.03, tz - 0.02 - FLOOR), "wood_dark")
    # ---- round the room: barrel of rolled maps, pin-board, bookshelf, lantern post, a globe
    bc = V((-0.75, -0.6, FLOOR))
    m.cyl(bc + V((0, 0, 0.1)), 0.09, 0.2, "wood_mid", cap="wood_dark", segs=8)
    for k in range(5):
        a = k * 1.25
        m.cyl(bc + V((0.04 * math.cos(a), 0.04 * math.sin(a), 0.22)), 0.015, 0.14, ["cloth_cream", "bone", "cloth_cream", "rope", "bone"][k],
              axis=(0.15 * math.cos(a), 0.15 * math.sin(a), 1), segs=5)
    pb = V((0.0, 0.88, FLOOR))
    for x in (-0.4, 0.4):
        m.obox(pb + V((x, 0, 0.3)), (0.03, 0.03, 0.6), "wood_dark")
    m.obox(pb + V((0, 0, 0.42)), (0.78, 0.025, 0.32), "leather")                                    # the board
    for k, (x, z, w, h, sw) in enumerate(((-0.25, 0.47, 0.18, 0.14, "cloth_cream"), (0.05, 0.4, 0.2, 0.16, "bone"),
                                          (0.28, 0.48, 0.14, 0.12, "cloth_cream"))):
        m.obox(pb + V((x, -0.016, z)), (w, 0.004, h), sw)
        m.obox(pb + V((x - w * 0.2, -0.019, z + h * 0.1)), (0.02, 0.003, 0.012), "cloth_red")
    pins = [pb + V((x, -0.022, z)) for x, z in ((-0.28, 0.5), (0.02, 0.44), (0.26, 0.5), (0.1, 0.36))]
    for a, b in zip(pins, pins[1:]):
        m.beam(a, b, 0.003, "cloth_red")                                                          # string between pins
    for p in pins:
        m.blob(p + V((0, -0.004, 0)), V((0.008, 0.008, 0.008)), "ruby", 5, 3)
    bs = V((0.78, 0.25, FLOOR))
    m.obox(bs + V((0.05, 0, 0.25)), (0.02, 0.42, 0.5), "wood_dark")                                     # back panel
    for y in (-0.2, 0.2):
        m.obox(bs + V((0, y, 0.25)), (0.12, 0.02, 0.5), "wood_dark")                                     # sides
    m.obox(bs + V((0, 0, 0.495)), (0.12, 0.42, 0.02), "wood_dark")
    for z in (0.08, 0.24, 0.4):
        m.obox(bs + V((-0.005, 0, z)), (0.1, 0.38, 0.015), "wood_light")
        for k in range(6):
            y = -0.15 + 0.06 * k
            h = rnd.uniform(0.07, 0.11)
            m.obox(bs + V((-0.01, y, z + 0.008 + h / 2)), (0.07, 0.04, h), rnd.choice(["cloth_red", "cloth_blue", "leather", "teal", "cloth_mustard"]))
    gl = V((0.72, -0.62, FLOOR))
    m.cyl(gl + V((0, 0, 0.03)), 0.04, 0.06, "wood_dark", segs=6)
    m.blob(gl + V((0, 0, 0.14)), V((0.075, 0.075, 0.075)), "water", 10, 6)                          # a globe
    m.blob(gl + V((0.02, -0.02, 0.17)), V((0.04, 0.03, 0.03)), "moss_light", 6, 3)
    m.obox(gl + V((0, 0, 0.14)), (0.004, 0.17, 0.004), "gold_dark", rot=(0.3, 0, 0))
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- the map (still): the paws hold it flat
    mm = B.M()
    mm.obox(V((TABLE_C.x, TABLE_C.y, MAP_TOP - 0.0015)), (TABLE_W - 0.04, DEPTH + 0.004, 0.003), "cloth_cream")  # over the edges
    for k in range(5):                                                                            # rivers, woods, an X
        p = V((TABLE_C.x + rnd.uniform(-0.22, 0.22), TABLE_C.y + rnd.uniform(-0.09, 0.09), MAP_TOP + 0.0005))
        mm.obox(p, (rnd.uniform(0.05, 0.1), 0.01, 0.001), "water" if k < 2 else "moss", rot=(0, 0, rnd.uniform(0, 3)))
    xx = V((TABLE_C.x + 0.18, TABLE_C.y + 0.04, MAP_TOP + 0.0006))
    for a in (0.78, -0.78):
        mm.obox(xx, (0.04, 0.008, 0.001), "cloth_red", rot=(0, 0, a))
    mm.cyl(V((TABLE_C.x - 0.25, TABLE_C.y - 0.07, MAP_TOP + 0.022)), 0.02, 0.044, "wood_light", segs=7, cap="cloth_cream")   # mug weight
    mm.blob(V((TABLE_C.x + 0.25, TABLE_C.y + 0.08, MAP_TOP + 0.01)), V((0.022, 0.018, 0.014)), "stone_light", 6, 3)  # stone
    mm.cyl(V((TABLE_C.x + 0.24, TABLE_C.y - 0.08, MAP_TOP + 0.006)), 0.02, 0.012, "gold_dark", segs=8, cap="soot")   # candle dish
    mm.cyl(V((TABLE_C.x + 0.24, TABLE_C.y - 0.08, MAP_TOP + 0.03)), 0.008, 0.036, "cloth_cream", segs=6)
    mapo = mm.obj("pr_map", coll)
    mapo.parent = root
    parts = {}
    mm = B.M()
    fl = V((TABLE_C.x + 0.24, TABLE_C.y - 0.08, MAP_TOP + 0.048))
    mm.cyl(fl + V((0, 0, 0.012)), 0.007, 0.024, "flame_yellow", segs=5, r2=0.0)
    parts["pr_candle"] = A.part(mm.obj("pr_candle", coll), root, fl)
    mm = B.M()                                                                           # the map's loose corner
    cn = V((TABLE_C.x - TABLE_W / 2 + 0.03, TABLE_C.y + 0.06, MAP_TOP))
    mm.obox(cn + V((-0.025, 0, 0.0005)), (0.05, 0.06, 0.002), "cloth_cream")
    parts["pr_map_corner"] = A.part(mm.obj("pr_map_corner", coll), root, cn + V((0, 0, 0.0015)))
    for i, (x, z, w, h) in enumerate(((-0.25, 0.47, 0.18, 0.14), (0.28, 0.48, 0.14, 0.12))):     # loose chart corners
        mm = B.M()
        top = pb + V((x + w / 2 - 0.035, -0.02, z - h / 2 + 0.04))
        mm.obox(top + V((0, 0, -0.025)), (0.06, 0.003, 0.05), "cloth_cream")
        parts[f"pr_chart_{i + 1}"] = A.part(mm.obj(f"pr_chart_{i + 1}", coll), root, top)
    mm = B.M()
    pin = pins[1] + V((0, -0.006, 0))
    mm.blob(pin, V((0.009, 0.009, 0.009)), "sapphire", 5, 3)
    parts["pr_pin"] = A.part(mm.obj("pr_pin", coll), root, pin + V((0, 0.006, 0)))
    return root, mapo, parts


def clips(parts):
    def common(p):
        return {"pr_candle": (None, A.q((0, 0, 1), 20 * math.sin(TAU * 4 * p)), (1, 1, 1 + 0.2 * math.sin(TAU * 5 * p))),
                "pr_map_corner": (None, A.q((0, 1, 0), 8 + 8 * max(0.0, math.sin(TAU * 2 * p))), None),
                "pr_chart_1": (None, A.q((1, 0, 0), -6 * max(0.0, math.sin(TAU * (p + 0.2)))), None),
                "pr_chart_2": (None, A.q((1, 0, 0), -6 * max(0.0, math.sin(TAU * (p + 0.6)))), None)}

    def idle(p):
        pose = common(p)
        pose["pr_pin"] = (None, None, None)
        return pose

    def work(p):
        pose = common(p)
        j = math.exp(-((((p - 0.45) + 0.5) % 1.0 - 0.5) ** 2) / 0.002)
        pose["pr_pin"] = (None, A.q((1, 0, 0), 15 * j * math.sin(TAU * 8 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, mapo, parts = build(coll, random.Random(131))
    for i, (p, face) in enumerate(SPOTS):
        A.spot(root, f"spot_work_{i + 1}", p, face)
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(mapo) + sum(K.tris(o) for o in parts.values())} tris (moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "map_room.blend"), relative_remap=True)
    A.export()
    crew, objs = [], []
    for i in range(len(SPOTS)):
        rig, mesh, _ = A.raccoon_at(bpy.data.objects[f"spot_work_{i + 1}"], clip="work_read")
        crew.append((rig, mesh, None, "work", {"pr_map": None, "pr_map_corner": None}))
        objs += [rig, mesh]
    allow = [("pr_candle", "pr_map"), ("pr_map_corner", "pr_map"), ("pr_map_corner", NAME), ("pr_chart_1", NAME),
             ("pr_chart_2", NAME), ("pr_pin", NAME)]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_map_room_loops.gif",
                       target=(0.0, 0.05, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
