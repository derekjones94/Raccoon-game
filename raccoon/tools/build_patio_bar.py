"""bld_patio_bar_2x2: an open-air patio bar where raccoons hang out, drink and chat. Room for five.

A round deck of planks with a stone fire pit in the middle. Five seats round the fire (spot_seat_1..5, each on a
flat rug, facing the fire): raccoons sit there and play work_drink (with prop_mug) or work_chat. In the back corner, a
bar of kegs and a plank counter with mugs on it; a string of lanterns between four corner posts.

Clips (24 fps)
  idle  96 fr  the fire flickers, the lanterns sway on their strings
  work  96 fr  (someone's here) the fire burns up brighter with sparks, the lanterns sway, the mugs on the counter
               clink together now and then

The seats are independent: start each raccoon's clip whenever it sits down (offsetting them looks livelier); mix
work_drink and work_chat. Nothing in the building waits on a particular raccoon.

Run:  python3 tools/build_patio_bar.py   (--no-renders)
Out:  patio_bar.blend, export/bld_patio_bar_2x2.glb, renders/bld_patio_bar_loops.gif, renders/qa_buildings.txt
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

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_patio_bar_2x2"
FRAMES = 96
DECK = 0.02
PIT = V((-0.06, -0.06, DECK))                      # the fire pit, in the middle of the seats
SEAT_R = 0.45                                       # seats sit this far from the pit's centre
SEAT_ANGLES = (10, 82, 160, 232, 304)               # degrees round the pit (0 = +X); the bar is in the gap at the back right
POSTS = [V((x, y, 0)) for x, y in ((-0.88, -0.88), (0.88, -0.88), (0.88, 0.88), (-0.88, 0.88))]
POST_H = 0.62


def seats():
    out = []
    for a in SEAT_ANGLES:
        r = math.radians(a)
        p = PIT + V((math.cos(r), math.sin(r), 0)) * SEAT_R
        out.append((V((p.x, p.y, DECK + 0.0015)), (PIT - p).normalized()))
    return out


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (1.94, 1.94, 0.004), "moss")                       # grass round the deck (and its posts)
    # ---- deck: a disc of planks on a stone ring, flush to the ground
    n = 10
    for k in range(n):                                       # each plank's ends cut on the circle: a clean round edge
        xl, xr = -0.95 + 1.9 * k / n + 0.005, -0.95 + 1.9 * (k + 1) / n - 0.005
        hl, hr = (math.sqrt(max(0.95 ** 2 - x * x, 0.04)) for x in (xl, xr))
        outline = [(xl, -hl), (xr, -hr), (xr, hr), (xl, hl)]
        bot = [m.bm.verts.new((x, y, 0.0)) for x, y in outline]
        top = [m.bm.verts.new((x, y, DECK)) for x, y in outline]
        fs = [m.bm.faces.new(top), m.bm.faces.new(list(reversed(bot)))]
        for i in range(4):
            j = (i + 1) % 4
            fs.append(m.bm.faces.new((bot[i], bot[j], top[j], top[i])))
        m.tag(fs, "wood_light" if k % 2 else "wood_mid")
    # ---- fire pit: a ring of stones, logs, coals
    for k in range(9):
        a = TAU * k / 9
        m.blob(PIT + V((0.13 * math.cos(a), 0.13 * math.sin(a), 0.0)), V((0.045, 0.04, 0.04)), rnd.choice(["stone_mid", "stone_light"]), 6, 3)
    m.cyl(PIT + V((0, 0, 0.003)), 0.1, 0.006, "soot", segs=10)
    for a in (0.3, 2.4, 4.4):
        d = V((math.cos(a), math.sin(a), 0))
        B.log(m, PIT + d * 0.03 + V((0, 0, 0.022)), 0.017, 0.12, axis=tuple(d + V((0, 0, 0.3))))
    m.blob(PIT + V((0, 0, 0.012)), V((0.06, 0.06, 0.015)), "torch_orange", 7, 3)
    # ---- a rug under each seat (flush, so the sitter sits on it)
    for (p, face), sw in zip(seats(), ("cloth_red", "cloth_blue", "cloth_mustard", "teal", "cloth_red")):
        c = p - face * 0.03
        m.cyl(V((c.x, c.y, DECK + 0.0005)), 0.13, 0.001, sw, segs=10)
    # ---- the bar in the back right corner: three kegs on their sides, a plank counter on two kegs, a tap
    bc = V((0.62, 0.62, DECK))
    for k, (dx, dy) in enumerate(((0.0, 0.18), (0.16, 0.06))):                                    # counter kegs
        m.cyl(bc + V((dx - 0.12, dy - 0.2, 0.09)), 0.07, 0.18, "wood_mid", cap="wood_dark", segs=8)
        m.cyl(bc + V((dx - 0.12, dy - 0.2, 0.09)), 0.074, 0.014, "iron", segs=8)
    m.obox(bc + V((-0.06, -0.08, 0.19)), (0.36, 0.1, 0.02), "wood_light", rot=(0, 0, -0.78))       # the counter plank
    for k in range(2):                                                                            # kegs on a rack
        c = bc + V((0.14 - 0.02 * k, 0.16 + 0.0 * k, 0.07 + 0.14 * k))
        m.cyl(c, 0.065, 0.16, "wood_mid", axis=(1, -1, 0), segs=8, cap="wood_dark")
        m.cyl(c + V((-0.07, 0.07, 0)), 0.008, 0.03, "copper", axis=(1, -1, 0), segs=5)            # taps
    m.obox(bc + V((0.14, 0.16, 0.03)), (0.24, 0.2, 0.06), "wood_dark", rot=(0, 0, -0.78))           # rack
    # ---- posts with lantern strings along the front and back edges
    for p in POSTS:
        m.obox(p + V((0, 0, POST_H / 2)), (0.04, 0.04, POST_H), "wood_dark")
    for a, b in ((0, 1), (3, 2), (0, 3)):
        p0, p1 = POSTS[a] + V((0, 0, POST_H - 0.02)), POSTS[b] + V((0, 0, POST_H - 0.02))
        mid = (p0 + p1) / 2 + V((0, 0, -0.08))
        m.beam(p0, mid, 0.008, "rope")
        m.beam(mid, p1, 0.008, "rope")
    # ---- a crate with a board game on it (front right)
    gb = V((0.7, -0.7, DECK))
    B.crate(m, gb, 0.14, 0.3)
    m.obox(gb + V((0, 0, 0.146)), (0.1, 0.1, 0.008), "cloth_cream", rot=(0, 0, 0.3))
    for k in range(3):
        m.cyl(gb + V((-0.02 + 0.02 * k, 0.01 * k, 0.153)), 0.009, 0.006, "soot" if k % 2 else "ruby", segs=6)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    # lanterns hanging on the strings (they swing), fire flames, sparks, two mugs on the counter
    k = 0
    for a, b in ((0, 1), (3, 2), (0, 3)):
        p0, p1 = POSTS[a] + V((0, 0, POST_H - 0.02)), POSTS[b] + V((0, 0, POST_H - 0.02))
        for t in (0.3, 0.7):
            top = p0.lerp(p1, t) + V((0, 0, -0.08 * (1 - abs(2 * t - 1)) * 1.0 - 0.006))
            mm = B.M()
            mm.cyl(top + V((0, 0, -0.02)), 0.003, 0.04, "iron_dark", segs=4)
            mm.obox(top + V((0, 0, -0.06)), (0.035, 0.035, 0.045), "flame_yellow" if k % 2 else "torch_orange")
            mm.obox(top + V((0, 0, -0.035)), (0.045, 0.045, 0.01), "iron_dark")
            k += 1
            parts[f"pr_lantern_{k}"] = A.part(mm.obj(f"pr_lantern_{k}", coll), root, top)
    for i, (d, h, sw) in enumerate(((V((0, 0, 0)), 0.13, "torch_orange"), (V((0.03, 0.02, 0)), 0.09, "flame_yellow"),
                                    (V((-0.025, -0.02, 0)), 0.085, "flame_yellow"))):
        mm = B.M()
        c = PIT + d + V((0, 0, 0.015))
        mm.cyl(c + V((0, 0, h / 2)), 0.032 if i == 0 else 0.02, h, sw, segs=5, r2=0.0)
        parts[f"pr_flame_{i + 1}"] = A.part(mm.obj(f"pr_flame_{i + 1}", coll), root, c)
    for i in range(3):
        mm = B.M()
        c = PIT + V((0.01 * (i - 1), 0, 0.16))
        mm.obox(c, (0.01, 0.01, 0.01), "flame_yellow", rot=(0.6, 0.3, i))
        parts[f"pr_spark_{i + 1}"] = A.part(mm.obj(f"pr_spark_{i + 1}", coll), root, c)
    for i, dx in enumerate((-0.03, 0.03)):
        mm = B.M()
        c = bc + V((-0.06 + dx, -0.08 - dx, 0.2))
        mm.cyl(c + V((0, 0, 0.022)), 0.02, 0.044, "wood_light", segs=8, cap="cloth_cream")
        mm.cyl(c + V((0, 0, 0.012)), 0.0225, 0.005, "iron", segs=8)
        parts[f"pr_mug_{i + 1}"] = A.part(mm.obj(f"pr_mug_{i + 1}", coll), root, c)
    return root, parts


def clips(parts):
    nl = len([n for n in parts if n.startswith("pr_lantern")])

    def common(p, heat):
        pose = {}
        for i in range(1, nl + 1):
            pose[f"pr_lantern_{i}"] = (None, A.q((1, 0.4 * i, 0), (3 + 2 * heat) * math.sin(TAU * (2 * p + 0.17 * i))), None)
        for i, (f, ph) in enumerate(((5, 0.0), (7, 0.33), (6, 0.66))):
            fl = (1 + 0.15 * math.sin(TAU * (f * p + ph))) * (0.8 + 0.3 * heat)
            pose[f"pr_flame_{i + 1}"] = (None, A.q((0, 0, 1), 25 * math.sin(TAU * (f * p + ph))), (0.9 + 0.2 * heat, 0.9 + 0.2 * heat, fl))
        return pose

    def idle(p):
        pose = common(p, 0.0)
        for i in range(1, 4):
            pose[f"pr_spark_{i}"] = A.hidden()
        return pose

    def work(p):
        pose = common(p, 1.0)
        for i in range(1, 4):
            u = (p * 4 + i / 3) % 1.0
            pose[f"pr_spark_{i}"] = (V((0.03 * math.sin(TAU * (u + i)), 0.02 * math.cos(TAU * u), 0.2 * u)),
                                     A.q((1, 0, 0), 300 * u), max(1 - u, 0.001))
        for i, ph in ((1, 0.0), (2, 0.5)):                          # the mugs clink together now and then
            c = sum(math.exp(-((((p - c0) + 0.5) % 1.0 - 0.5) ** 2) / 0.0006) for c0 in (0.25, 0.7))
            sgn = 1 if i == 1 else -1
            pose[f"pr_mug_{i}"] = (V((0.006 * sgn * c, -0.006 * sgn * c, 0.004 * c)), A.q((1, 1, 0), 8 * sgn * c), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(111))
    for i, (p, face) in enumerate(seats()):
        A.spot(root, f"spot_seat_{i + 1}", p, face)
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris (moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "patio_bar.blend"), relative_remap=True)
    A.export()
    crew, objs = [], []
    for i in range(5):
        sp = bpy.data.objects[f"spot_seat_{i + 1}"]
        drink = i % 2 == 0
        rig, mesh, mug = A.raccoon_at(sp, clip="work_drink" if drink else "work_chat", tool="prop_mug" if drink else None)
        crew.append((rig, mesh, mug, "work", {}))
        objs += [rig, mesh] + ([mug] if mug else [])
    allow = [(f"pr_lantern_{i}", NAME) for i in range(1, 7)] + [(f"pr_flame_{i}", NAME) for i in (1, 2, 3)] + \
            [("pr_flame_1", "pr_flame_2"), ("pr_flame_1", "pr_flame_3"), ("pr_flame_2", "pr_flame_3")] + \
            [(f"pr_spark_{i}", n) for i in (1, 2, 3) for n in (NAME, "pr_flame_1", "pr_flame_2", "pr_flame_3")] + \
            [(f"pr_spark_{i}", f"pr_spark_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j] + \
            [("pr_mug_1", NAME), ("pr_mug_2", NAME), ("pr_mug_1", "pr_mug_2")]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_patio_bar_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.7, pitch=42, idle_frames=24, grid_n=4, step=3)


if __name__ == "__main__":
    main()
