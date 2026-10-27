"""bld_farm_2x2: a fenced vegetable patch where raccoons plant and tend crops (Tending).

Rows run left to right: cabbages at the front, then carrots, then a row of new seedlings. The raccoon stands behind
the seedling row (spot_work, facing the front) and waters it from a can (work_water, prop_watering_can). Behind it: a
wheat patch, a scarecrow, sunflowers, a water barrel. A low wattle fence on all sides with a gap at the front.

Clips (24 fps)
  idle  64 fr  the wheat and sunflowers sway, the scarecrow's rags flap, a butterfly flits over the cabbages
  work  64 fr  as idle, plus the water: a stream from the can's spout while it pours (it sweeps along the row with
               the raccoon's arm), a splash ring where it lands, and the two seedlings beside it perk up

The stream hangs from where the adult's spout is in work_water (measured from the clip, like the fishing line), so
the building's work and the raccoon's work_water must start together (both 64 frames).

Run:  python3 tools/build_farm.py   (--no-renders)
Out:  farm.blend, export/bld_farm_2x2.glb, renders/bld_farm_loops.gif, renders/qa_buildings.txt
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
import build_tools as T  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_farm_2x2"
FRAMES = 64
SOIL = 0.008                                   # top of the soil plate: the raccoon stands on it
SPOT = V((0.32, 0.12, SOIL + 0.0015))          # behind the seedling row, facing the front (-Y), feet just on the soil
ROW_H = 0.026                                  # height of the row mounds above the soil
FENCE = 0.93


def spout_path():
    """The can's rose (where the water leaves it) over work_water, raccoon space: [(rose, direction)] per frame."""
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_animated.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rig = dst.objects[0]
    bpy.context.scene.collection.objects.link(rig)
    rig.location = (0, 0, 0)
    for t in rig.animation_data.nla_tracks:
        t.mute = True
    rig.animation_data.action = next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name == "work_water")
    out = []
    for f in range(FRAMES + 1):
        bpy.context.scene.frame_set(f)
        M = rig.pose.bones["handslot.r"].matrix
        out.append((M @ T.CAN_SPOUT, (M.to_3x3() @ T.CAN_SPOUT_DIR).normalized()))
    bpy.data.objects.remove(rig)
    return out


def mound(m, x0, x1, y, w=0.06, sw="wood_dark"):
    """A row of heaped soil along X (a flattened half-ellipsoid)."""
    m.blob(V(((x0 + x1) / 2, y, SOIL)), V(((x1 - x0) / 2, w, ROW_H)), sw, 10, 3)


def seedling(m, c, h=0.03):
    m.cyl(c + V((0, 0, h / 2)), 0.003, h, "moss", segs=3)
    for s in (-1, 1):
        m.obox(c + V((s * 0.009, 0, h)), (0.016, 0.008, 0.003), "moss_light", rot=(0, s * 0.35, 0))


def build(coll, rnd, path):
    m = B.M()
    # ---- soil plate and the fence
    m.obox(V((0, 0, SOIL / 2)), (2 * FENCE, 2 * FENCE, SOIL), "leather_dark")
    a = FENCE
    sides = [((-a, a), (a, a)), ((-a, -a), (-a, a)), ((a, -a), (a, a)), ((-a, -a), (-0.16, -a)), ((0.16, -a), (a, -a))]
    for (x0, y0), (x1, y1) in sides:
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(L / 0.6))
        for k in range(n + 1):
            u = k / n
            p = V((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, 0))
            h = 0.15 + rnd.uniform(-0.012, 0.012)
            m.obox(p + V((0, 0, h / 2)), (0.03, 0.03, h), "wood_dark")
        m.beam(V((x0, y0, 0.1)), V((x1, y1, 0.1)), 0.02, "wood_weathered")                         # woven rail
    # ---- rows: cabbages (front), carrots, seedlings (the raccoon waters these)
    rows = {"cabbage": -0.62, "carrot": -0.37, "seedling": SPOT.y - 0.21}
    mound(m, -0.78, 0.78, rows["cabbage"], 0.08)
    mound(m, -0.78, 0.78, rows["carrot"], 0.06)
    mound(m, -0.4, 0.66, rows["seedling"], 0.055)
    for k, x in enumerate((-0.62, -0.31, 0.0, 0.31, 0.62)):
        if k == 2:
            continue                                                 # one picked already (it's in the basket)
        c = V((x + rnd.uniform(-0.02, 0.02), rows["cabbage"], SOIL + ROW_H * 0.6))
        m.blob(c + V((0, 0, 0.01)), V((0.075, 0.07, 0.03)), "moss", 7, 2)                           # outer leaves
        m.blob(c + V((0, 0, 0.038)), V((0.05, 0.048, 0.04)), "moss_light", 7, 3)                   # the head
    for x in [-0.65 + 0.26 * k for k in range(6)]:
        c = V((x + rnd.uniform(-0.015, 0.015), rows["carrot"], SOIL + ROW_H * 0.8))
        m.cyl(c + V((0, 0, 0.006)), 0.011, 0.014, "torch_orange", segs=4, r2=0.008)
        for j in range(2):                                              # feathery tops
            ang = j * math.pi + rnd.uniform(0, 1)
            d = V((math.cos(ang), math.sin(ang), 2.2)).normalized()
            m.cyl(c + V((0, 0, 0.012)) + d * 0.026, 0.012, 0.052, "moss_light" if j else "moss", axis=tuple(d),
                  segs=3, r2=0.0)
    # seedlings: the two beside where the water lands are moving parts (they perk up); the rest are still
    land_x = SPOT.x + path[20][0].x
    seed_xs = [-0.3, -0.06, land_x - 0.075, land_x + 0.075, 0.54]
    for x in seed_xs[:2] + seed_xs[4:]:
        seedling(m, V((x, rows["seedling"], SOIL + ROW_H * 0.85)))
    # ---- back: wheat patch (left), scarecrow, sunflowers (right), water barrel, a hoe on the fence
    m.obox(V((-0.45, 0.52, SOIL + 0.004)), (0.78, 0.6, 0.008), "wood_dark")                         # tilled patch
    sc = V((0.08, 0.66, 0))
    m.obox(sc + V((0, 0, 0.21)), (0.025, 0.025, 0.42), "wood_dark")                                  # post
    m.beam(sc + V((-0.15, 0, 0.32)), sc + V((0.15, 0, 0.32)), 0.022, "wood_dark")                    # arms
    m.blob(sc + V((0, 0, 0.28)), V((0.06, 0.045, 0.08)), "cloth_blue", 8, 4)                         # coat
    m.blob(sc + V((0, -0.005, 0.4)), V((0.042, 0.04, 0.045)), "burlap", 8, 4)                        # head
    m.cyl(sc + V((0, -0.005, 0.44)), 0.075, 0.008, "cloth_mustard", segs=8)                          # hat brim
    m.cyl(sc + V((0, -0.005, 0.47)), 0.04, 0.05, "cloth_mustard", segs=6, r2=0.03)                  # hat crown
    for s in (-1, 1):
        m.obox(sc + V((s * 0.015, -0.042, 0.41)), (0.012, 0.004, 0.012), "soot")                     # button eyes
        m.cyl(sc + V((s * 0.15, 0, 0.32)), 0.018, 0.02, "rope", axis=(1, 0, 0), segs=5)              # straw cuffs
    m.obox(sc + V((0, -0.044, 0.385)), (0.03, 0.004, 0.004), "soot")                                 # stitched mouth
    bc = V((0.78, 0.22, 0))
    m.cyl(bc + V((0, 0, 0.1)), 0.085, 0.2, "wood_mid", cap="wood_dark", segs=8)
    for z in (0.045, 0.155):
        m.cyl(bc + V((0, 0, z)), 0.09, 0.016, "iron", segs=8)
    m.cyl(bc + V((0, 0, 0.198)), 0.078, 0.006, "water", segs=8)
    m.beam(bc + V((0.02, 0.0, 0.2)), bc + V((0.11, -0.02, 0.27)), 0.01, "wood_light")               # dipper handle
    m.beam(V((FENCE - 0.03, -0.5, 0.005)), V((FENCE - 0.05, -0.32, 0.2)), 0.012, "wood_light")      # hoe handle
    m.obox(V((FENCE - 0.03, -0.52, 0.025)), (0.03, 0.05, 0.045), "iron", rot=(0.0, 0.0, 0.0))         # hoe blade
    bk = V((-0.72, -0.8, 0))                                                                          # basket of veg
    m.cyl(bk + V((0, 0, 0.045)), 0.07, 0.08, "rope", segs=8, r2=0.08, cap="rope_dark")
    m.blob(bk + V((0.0, 0.0, 0.09)), V((0.045, 0.043, 0.035)), "moss_light", 8, 4)                   # the picked cabbage
    for j in range(3):
        ang = j * 2.1 + 0.5
        m.cyl(bk + V((0.05 * math.cos(ang), 0.05 * math.sin(ang), 0.1)), 0.009, 0.06, "torch_orange", segs=5,
              axis=(math.cos(ang), math.sin(ang), 0.8), r2=0.003)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # wheat clumps
    for i, c in enumerate((V((-0.72, 0.36, 0)), V((-0.5, 0.62, 0)), V((-0.3, 0.38, 0)), V((-0.66, 0.7, 0)),
                           V((-0.2, 0.68, 0)))):
        m = B.M()
        base = c + V((0, 0, SOIL + 0.004))
        h = rnd.uniform(0.15, 0.18)
        m.cyl(base + V((0, 0, h / 2)), 0.016, h, "gold", segs=5, r2=0.032, cap="gold_dark")         # the sheaf of stalks
        for j in range(5):                                                                        # ears of grain
            ang = j * TAU / 5 + rnd.uniform(0, 0.4)
            d = V((math.cos(ang), math.sin(ang), 2.6)).normalized()
            m.cyl(base + V((0.022 * math.cos(ang), 0.022 * math.sin(ang), h + 0.016)) + d * 0.024, 0.012, 0.064,
                  "gold_light", axis=tuple(d), segs=4, r2=0.003)
        parts[f"pr_wheat_{i + 1}"] = A.part(m.obj(f"pr_wheat_{i + 1}", coll), root, base)
    # sunflowers
    for i, (c, h) in enumerate(((V((0.56, 0.72, 0)), 0.36), (0.7 * V((1.0, 0.0, 0)) + V((0.0, 0.58, 0)), 0.3),
                                (V((0.82, 0.74, 0)), 0.33))):
        m = B.M()
        base = c + V((0, 0, SOIL))
        m.cyl(base + V((0, 0, h / 2)), 0.007, h, "moss", segs=4)
        m.obox(base + V((0.02, 0, h * 0.5)), (0.04, 0.02, 0.005), "moss_light", rot=(0, -0.4, 0))
        hd = base + V((0, -0.012, h + 0.01))
        m.cyl(hd, 0.045, 0.012, "gold_light", axis=(0, -1, 0.35), segs=7)
        m.cyl(hd + V((0, -0.006, 0.002)), 0.022, 0.012, "wood_dark", axis=(0, -1, 0.35), segs=5)
        parts[f"pr_sunflower_{i + 1}"] = A.part(m.obj(f"pr_sunflower_{i + 1}", coll), root, base)
    # the scarecrow's rags: hang from its arms and flap
    for i, s in enumerate((-1, 1)):
        m = B.M()
        top = sc + V((s * 0.11, 0, 0.31))
        m.obox(top + V((0, 0, -0.045)), (0.035, 0.006, 0.09), "cloth_red" if s < 0 else "cloth_cream")
        parts[f"pr_rag_{i + 1}"] = A.part(m.obj(f"pr_rag_{i + 1}", coll), root, top)
    # a butterfly over the cabbages
    m = B.M()
    bf = V((-0.3, -0.6, 0.2))
    for s in (-1, 1):
        m.obox(bf + V((s * 0.012, 0, 0)), (0.022, 0.018, 0.002), "cloth_mustard")
    m.obox(bf, (0.004, 0.02, 0.004), "soot")
    parts["pr_butterfly"] = A.part(m.obj("pr_butterfly", coll), root, bf)
    # the two seedlings beside the landing water
    for i, x in enumerate(seed_xs[2:4]):
        m = B.M()
        c = V((x, rows["seedling"], SOIL + ROW_H * 0.85))
        seedling(m, c)
        parts[f"pr_seedling_{i + 1}"] = A.part(m.obj(f"pr_seedling_{i + 1}", coll), root, c)
    # the water stream: a curved fall from the spout to the soil, hanging at the spout (frame 20 of the pour)
    rose, d = path[20]
    rose_w = SPOT + rose
    land_z = SOIL + ROW_H * 0.9
    m = B.M()
    _stream(m, rose_w, d, land_z)
    parts["pr_water_stream"] = A.part(m.obj("pr_water_stream", coll), root, rose_w)
    m = B.M()
    land = _stream_end(rose_w, d, land_z)
    FS._ring(m, land + V((0, 0, 0.002)), 0.022, 0.015, "water", 12)
    parts["pr_splash"] = A.part(m.obj("pr_splash", coll), root, land + V((0, 0, 0.002)))
    return root, parts, rows


def _stream_pts(rose, d, land_z, n=5):
    """A falling arc: leaves along the spout's direction, curves down to the soil."""
    v = V((d.x, d.y, 0)) * 0.6
    h = rose.z - land_z
    return [rose + v * (h * (k / n)) * 0.9 + V((0, 0, -h * (k / n) ** 1.6)) for k in range(n + 1)]


def _stream_end(rose, d, land_z):
    return _stream_pts(rose, d, land_z)[-1]


def _stream(m, rose, d, land_z):
    pts = _stream_pts(rose, d, land_z)
    for a, b in zip(pts, pts[1:]):
        m.cyl((a + b) / 2, 0.0065, (b - a).length + 0.002, "water", axis=tuple(b - a), segs=4)


def clips(parts, path):
    rest_rose = path[20][0]

    def common(p):
        pose = {}
        for i in range(1, 6):                                            # wheat sways in a slow wave, left to right
            w = math.sin(TAU * (p - 0.12 * i))
            pose[f"pr_wheat_{i}"] = (None, A.q((0.3, 1, 0), 5 * w), None)
        for i in range(1, 4):
            w = math.sin(TAU * (p - 0.2 * i - 0.3))
            pose[f"pr_sunflower_{i}"] = (None, A.q((1, 0.2, 0), 3 * w) @ A.q((0, 0, 1), 6 * math.sin(TAU * p + i)), None)
        for i in (1, 2):                                                 # rags flap about the arm
            pose[f"pr_rag_{i}"] = (None, A.q((1, 0, 0), 14 * math.sin(TAU * (2 * p + 0.3 * i)) + 6), None)
        # butterfly: a lazy loop over the cabbages, wings beating
        a = TAU * p
        off = V((0.28 * math.sin(a), 0.07 * math.sin(2 * a), 0.03 * math.sin(3 * a)))
        flap = 0.25 + 0.75 * abs(math.cos(TAU * 8 * p))
        heading = math.degrees(math.atan2(0.14 * math.cos(2 * a), 0.28 * math.cos(a)))
        pose["pr_butterfly"] = (off, A.q((0, 0, 1), heading - 90), (flap, 1, 1))
        return pose

    def idle(p):
        pose = common(p)
        for n in ("pr_water_stream", "pr_splash"):
            pose[n] = A.hidden()
        return pose

    def work(p):
        pose = common(p)
        f = round(p * FRAMES) % FRAMES
        t, _sw = J.water_phase(p)
        rose = path[f][0]
        on = ramp_stream(p)
        if on > 0:
            # hangs from the spout (the stream's shape is the pour's; only the sweep moves it), grows out as it starts
            pose["pr_water_stream"] = (V((rose.x - rest_rose.x, 0, 0)), None, (1, 1, 1) if on >= 1 else (on, on, on))
            ring = (p - 0.2) % (1 / 6) * 6                               # a ring spreads every ~10 frames
            pose["pr_splash"] = (V((rose.x - rest_rose.x, 0, 0)), None, (0.4 + 1.1 * ring) * min(on, 1))
        else:
            pose["pr_water_stream"] = A.hidden()
            pose["pr_splash"] = A.hidden()
        for i, x_off in ((1, -1), (2, 1)):                               # the seedlings perk up as water reaches them
            near = max(0.0, 1 - abs((rose.x - rest_rose.x) * x_off - 0.016) / 0.03) if on > 0 else 0.0
            perk = 0.6 * near * (0.5 + 0.5 * math.sin(TAU * 6 * p))
            pose[f"pr_seedling_{i}"] = (None, A.q((1, 0, 0), 8 * perk), (1, 1, 1 + 0.25 * perk))
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def ramp_stream(p):
    """How much water flows (0 none, 1 full): only while the can is fully tipped (work_water's pour)."""
    t, _ = J.water_phase(p)
    return max(0.0, (t - 0.92) / 0.08) if t < 1 else 1.0


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    path = spout_path()
    root, parts, rows = build(coll, random.Random(21), path)
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts, path)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "farm.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, can = A.raccoon_at(sp, clip="work_water", tool="prop_watering_can")
    allow = [("pr_water_stream", NAME), ("pr_splash", NAME), ("pr_water_stream", "pr_splash")] + \
            [(f"pr_seedling_{i}", NAME) for i in (1, 2)] + [(f"pr_wheat_{i}", NAME) for i in range(1, 6)] + \
            [(f"pr_sunflower_{i}", NAME) for i in (1, 2, 3)] + [(f"pr_rag_{i}", NAME) for i in (1, 2)]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, can, "work", {"pr_water_stream": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, can], ROOT / "renders" / "bld_farm_loops.gif",
                       target=(0.0, 0.0, 0.12), dist=3.7, pitch=42, idle_frames=32, grid_n=4)


if __name__ == "__main__":
    main()
