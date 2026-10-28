"""bld_shadow_course_2x2: an obstacle course for sneaking practice, run as a lap.

Raccoons start at the flag (spot_course) and run the lap in work_course, which carries them round the route (it
travels: the raccoon's root stays on the spot, its body goes round): dash along the front, sneak under a rope hung
with bells, hop up onto a plank and balance along it, hop down, sneak past the sentry lantern, dash, hop the hurdle
and run back to the flag. A cardboard weasel "guard" on a pivot turns its back while they sneak past it.

Everything on the route is placed from build_raccoon_jobs.COURSE, the same route the clip runs, so the plank is under
the feet and the rope over the heads. Two runners can share the lap half a lap apart.

Clips (24 fps)
  idle  96 fr                 the bells and the lantern sway a little, the flag flutters, the weasel slowly scans
  work  COURSE_FRAMES (264)   a lap: the weasel turns away while each runner sneaks under the bells, the bells jingle
                              as they pass, the lantern swings; start it with work_course (and the second runner half
                              a lap later)

Run:  python3 tools/build_shadow_course.py   (--no-renders)
Out:  shadow_course.blend, export/bld_shadow_course_2x2.glb, renders/bld_shadow_course_loops.gif
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
NAME = "bld_shadow_course_2x2"
FRAMES = J.COURSE_FRAMES
IDLE_FRAMES = 96
FLOOR = 0.006
SPOT = V((J.COURSE_SPOT.x, J.COURSE_SPOT.y, FLOOR + 0.0015))
ROPE_X = -0.16                                   # the bell rope crosses the first sneak here
ROPE_H = 0.42
HALF = 0.5


def seg_window(kind_index):
    """(start, end) loop phase of segment i."""
    t0 = sum(sg["t"] for sg in J.COURSE_SEGS[:kind_index])
    return t0 / J.COURSE_T, (t0 + J.COURSE_SEGS[kind_index]["t"]) / J.COURSE_T


def seg_points(i, n=20):
    sg = J.COURSE_SEGS[i]
    return [J._point(sg, k / n)[0] for k in range(n + 1)]


def build(coll, rnd):
    m = B.M()
    # ---- ground: dark trodden earth; chalk dots mark both edges of the route (well clear of the runners' tails)
    m.obox(V((0, 0, FLOOR / 2)), (1.94, 1.94, FLOOR), "stone_deep")
    for i, sg in enumerate(J.COURSE_SEGS):
        for k in range(0, 8, 2):
            q, t = J._point(sg, k / 8)
            side = V((-t.y, t.x, 0)).normalized()
            for sgn in (-1, 1):
                d = q + side * (0.19 * sgn)
                if abs(d.x) < 0.9 and abs(d.y) < 0.9:
                    m.cyl(V((d.x, d.y, FLOOR + 0.0003)), 0.012, 0.0012, "cloth_cream", segs=6)
    # ---- start: a chalk line and a flag pole by the spot
    m.obox(V((SPOT.x - 0.02, SPOT.y, FLOOR + 0.0002)), (0.012, 0.24, 0.0012), "cloth_cream")     # the runners step on it:
                                                                                                    # under their 1.5 mm
    fp = V((SPOT.x + 0.2, SPOT.y - 0.16, 0.0))
    m.cyl(fp + V((0, 0, 0.25)), 0.01, 0.5, "wood_dark", segs=6)
    m.cyl(fp + V((0, 0, 0.01)), 0.04, 0.02, "stone_mid", segs=7)
    # ---- the bell rope over the first sneak: two posts, the rope sagging a little
    s0 = seg_points(1)
    ry = min(s0, key=lambda q: abs(q.x - ROPE_X)).y
    for dy in (-0.22, 0.22):
        m.cyl(V((ROPE_X, ry + dy, (ROPE_H + 0.04) / 2)), 0.018, ROPE_H + 0.04, "wood_bark", segs=6, cap="wood_cut")
        m.blob(V((ROPE_X, ry + dy, 0.01)), V((0.04, 0.04, 0.02)), "stone_mid", 5, 3)
    prev = None
    for k in range(9):
        t = k / 8
        q = V((ROPE_X, ry - 0.22 + 0.44 * t, ROPE_H + 0.02 - 0.02 * math.sin(math.pi * t)))
        if prev is not None:
            m.beam(prev, q, 0.005, "rope")
        prev = q
    # ---- the balance plank on two stumps, under the beam section (and a bit beyond, for the hops)
    bp = seg_points(4)
    xs = [q.x for q in bp]
    ys = [q.y for q in bp]
    px = sum(xs) / len(xs)
    half_w = max(0.06, (max(xs) - min(xs)) / 2 + 0.06)
    y0, y1 = min(ys) - 0.03, max(ys) + 0.03
    top = FLOOR + J.BEAM_H
    m.obox(V((px, (y0 + y1) / 2, top - 0.01)), (2 * half_w, y1 - y0, 0.02), "wood_light", top="wood_mid")
    for y in (y0 + 0.08, y1 - 0.08):
        m.cyl(V((px, y, (top - 0.02) / 2)), 0.045, top - 0.02, "wood_bark", segs=7, cap="wood_cut")
    # ---- the sentry lantern post beside the second sneak
    sp2 = seg_points(7)
    mid = sp2[len(sp2) // 2]
    lp = V((mid.x, min(0.9, mid.y + 0.25), 0.0))
    m.cyl(lp + V((0, 0, 0.27)), 0.02, 0.54, "wood_dark", segs=6)
    m.beam(lp + V((0, 0, 0.52)), lp + V((0, -0.1, 0.52)), 0.014, "wood_dark")
    m.blob(lp + V((0, 0, 0.01)), V((0.05, 0.05, 0.02)), "stone_mid", 5, 3)
    # ---- the hurdle across the middle of the hop
    hq, ht = J._point(J.COURSE_SEGS[9], 0.5)
    side = V((-ht.y, ht.x, 0)).normalized()
    for sgn in (-1, 1):
        c = hq + side * (0.17 * sgn)
        m.obox(V((c.x, c.y, (FLOOR + J.HURDLE_H + 0.02) / 2)), (0.025, 0.025, J.HURDLE_H + 0.02), "wood_dark")
        m.obox(V((c.x, c.y, 0.01)), (0.08, 0.025, 0.02), "wood_dark", rot=(0, 0, math.atan2(side.y, side.x)))
    a, b = hq - side * 0.18, hq + side * 0.18
    m.beam(V((a.x, a.y, FLOOR + J.HURDLE_H - 0.008)), V((b.x, b.y, FLOOR + J.HURDLE_H - 0.008)), 0.014, "cloth_red")
    # ---- round the edge: a bench, a water bucket, a chalk tally board
    m.obox(V((0.05, 0.1, 0.05)), (0.3, 0.08, 0.02), "wood_mid", top="wood_light")
    for x in (-0.07, 0.17):
        m.obox(V((x, 0.1, 0.02)), (0.03, 0.07, 0.04), "wood_dark")
    m.cyl(V((-0.15, 0.08, 0.04)), 0.04, 0.07, "wood_mid", segs=8, r2=0.035, cap="water")
    m.obox(V((0.08, 0.14, 0.12)), (0.14, 0.012, 0.1), "soot")
    for k in range(4):
        m.obox(V((0.03 + 0.02 * k, 0.133, 0.12)), (0.004, 0.003, 0.05), "cloth_cream")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # the flag at the start
    mm = B.M()
    fz = 0.48
    mm.obox(fp + V((0.06, 0, fz - 0.03)), (0.11, 0.004, 0.06), "teal")
    mm.obox(fp + V((0.06, -0.003, fz - 0.03)), (0.025, 0.002, 0.02), "cloth_cream")
    parts["pr_flag"] = A.part(mm.obj("pr_flag", coll), root, fp + V((0, 0, fz)))
    # bells on the rope
    for i in range(3):
        mm = B.M()
        y = ry - 0.12 + 0.12 * i
        hook = V((ROPE_X, y, ROPE_H + 0.02 - 0.02 * math.sin(math.pi * (y - ry + 0.22) / 0.44) - 0.004))
        mm.beam(hook, hook + V((0, 0, -0.012)), 0.003, "rope")
        mm.cyl(hook + V((0, 0, -0.02)), 0.012, 0.018, "gold", segs=6, r2=0.016)
        parts[f"pr_bell_{i + 1}"] = A.part(mm.obj(f"pr_bell_{i + 1}", coll), root, hook)
    # the sentry lantern
    mm = B.M()
    lh = lp + V((0, -0.1, 0.51))
    mm.beam(lh, lh + V((0, 0, -0.03)), 0.003, "iron_dark")
    mm.cyl(lh + V((0, 0, -0.06)), 0.025, 0.05, "flame_yellow", segs=6, cap="iron_dark")
    mm.cyl(lh + V((0, 0, -0.03)), 0.028, 0.01, "iron_dark", segs=6)
    parts["pr_lantern"] = A.part(mm.obj("pr_lantern", coll), root, lh)
    # the cardboard weasel guard on its pivot, by the rope (it turns its back while the runner sneaks under)
    mm = B.M()
    wc = V((ROPE_X + 0.02, ry - 0.3, 0.0))
    mm.cyl(wc + V((0, 0, 0.01)), 0.05, 0.02, "wood_dark", segs=8)
    mm.cyl(wc + V((0, 0, 0.1)), 0.008, 0.16, "wood_dark", segs=5)
    mm.obox(wc + V((0, 0, 0.2)), (0.1, 0.008, 0.2), "fur_brown")                                    # body board
    mm.obox(wc + V((0, -0.005, 0.32)), (0.07, 0.008, 0.06), "fur_tan")                              # head
    mm.obox(wc + V((0, -0.009, 0.325)), (0.05, 0.002, 0.012), "soot")                                # eyes band
    mm.cyl(wc + V((0.03, -0.005, 0.36)), 0.012, 0.02, "fur_brown", segs=4, r2=0.0)                   # ears
    mm.cyl(wc + V((-0.03, -0.005, 0.36)), 0.012, 0.02, "fur_brown", segs=4, r2=0.0)
    mm.obox(wc + V((0, -0.006, 0.2)), (0.06, 0.004, 0.06), "cloth_red")                              # a painted tabard
    parts["pr_guard"] = A.part(mm.obj("pr_guard", coll), root, wc)
    return root, parts


def clips(parts):
    s1 = seg_window(1)                                   # the first sneak: under the bells, past the weasel
    rope_u = None
    sg = J.COURSE_SEGS[1]
    for k in range(41):
        if J._point(sg, k / 40)[0].x <= ROPE_X:
            rope_u = k / 40
            break
    pass_at = s1[0] + (s1[1] - s1[0]) * (rope_u or 0.5)  # when a runner is under the rope

    def bells(p, jingle):
        out = {}
        for i in range(3):
            j = sum(math.exp(-((((p - c) + 0.5) % 1.0 - 0.5) ** 2) / 0.0004) for c in jingle)
            out[f"pr_bell_{i + 1}"] = (None, A.q((0, 1, 0), (5 + 20 * j) * math.sin(TAU * (7 * p + 0.3 * i))), None)
        return out

    def idle(p):
        out = bells(p, [])
        out["pr_flag"] = (None, A.q((0, 0, 1), 15 * math.sin(TAU * 2 * p)), None)
        out["pr_lantern"] = (None, A.q((1, 0, 0), 4 * math.sin(TAU * p)), None)
        out["pr_guard"] = (None, A.q((0, 0, 1), 25 * math.sin(TAU * p)), None)
        return out

    def work(p):
        out = bells(p, [pass_at, (pass_at + HALF) % 1.0])
        out["pr_flag"] = (None, A.q((0, 0, 1), 20 * math.sin(TAU * 8 * p)), None)
        out["pr_lantern"] = (None, A.q((1, 0, 0), 8 * math.sin(TAU * 4 * p)), None)
        turn = 0.0                                        # back turned while either runner sneaks past
        for off in (0.0, HALF):
            a, b = (s1[0] + off) % 1.0, (s1[1] + off) % 1.0
            q = (p - a) % 1.0
            span = (b - a) % 1.0
            if q < span:
                turn = max(turn, min(1.0, q / 0.03, (span - q) / 0.03))
        out["pr_guard"] = (None, A.q((0, 0, 1), 160 * turn + 10 * math.sin(TAU * 3 * p)), None)
        return out

    A.animate(parts, {"idle": (IDLE_FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(30))
    A.spot(root, "spot_course", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "shadow_course.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_course"]
    crew, objs = [], []
    for i in range(2):
        rig, mesh, _ = A.raccoon_at(sp, clip="work_course")
        if i:
            A.offset_clip(rig, FRAMES // 2)                 # the second runner, half a lap on
        crew.append((rig, mesh, None, "work", {}))
        objs += [rig, mesh]
    allow = [(n, NAME) for n in parts]
    probs = A.check(root, 2, 2, crew=crew, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_shadow_course_loops.gif",
                       target=(0.0, 0.0, 0.1), dist=3.7, pitch=48, idle_frames=24, grid_n=4, step=4)


if __name__ == "__main__":
    main()
