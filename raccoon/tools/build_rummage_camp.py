"""bld_rummage_camp_2x2: a scavengers' camp round a heap of junk, where raccoons rummage for berries and scraps.

A heap of scavenged junk (a burlap mound with leaves, tin cans, a bottle, a boot, a teacup, a broken plank) in the
middle; the raccoon digs at it from behind (spot_work, facing the front: from the game camera its face peeks over
the pile). Round it: a tarp lean-to with a bedroll, sorting baskets (berries, shiny caps), a sack of finds that
wiggles, a crate with a lantern, a small campfire.

Clips (24 fps)
  idle  48 fr  the fire flickers, the sack twitches now and then (something alive in there?), a leaf flutters
  work  48 fr  as idle, plus the junk on the heap jostles while the raccoon digs (work_rummage, 48 frames)

Run:  python3 tools/build_rummage_camp.py   (--no-renders)
Out:  rummage_camp.blend, export/bld_rummage_camp_2x2.glb, renders/bld_rummage_camp_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_rummage_camp_2x2"
SPOT = V((0.05, 0.27, 0.006))                    # behind the heap, facing the front (-Y), on the dirt patch
HEAP_C = V((0.05, 0.27 - 0.217, 0.0))            # heap: an ellipsoid; the side facing the raccoon (its back, +Y)
HEAP_R = V((0.25, 0.13, 0.12))                   # meets the paws' reach (~0.145 out at 0.1 up) and clears its knees
FRAMES = 48
BIG_C = V((HEAP_C.x - 0.02, HEAP_C.y - 0.17, 0.0))   # the bulk of the pile, further to the front (out of reach)
BIG_R = V((0.27, 0.2, 0.22))


def heap_point(ang, hf, C=None, R=None):
    """A point on a heap ellipsoid's surface and its normal: ang = angle round it (0 = +X, -90 = front), hf = 0..1
    height fraction. Default: the big front part of the pile."""
    C = BIG_C if C is None else C
    R = BIG_R if R is None else R
    z = R.z * hf
    k = math.sqrt(max(1 - hf * hf, 0.0))
    p = V((C.x + R.x * k * math.cos(ang), C.y + R.y * k * math.sin(ang), z))
    n = V(((p.x - C.x) / R.x ** 2, (p.y - C.y) / R.y ** 2, p.z / R.z ** 2)).normalized()
    return p, n


def on_heap(m, ang, hf, fn, lift=0.0):
    """Build something sitting on the heap surface: fn(m, point, normal); the point is lifted along the normal."""
    p, n = heap_point(ang, hf)
    fn(m, p + n * lift, n)


def build(coll, rnd):
    m = B.M()
    # ---- ground: a trampled, irregular dirt patch
    pts = []
    for k in range(14):
        a = math.tau * k / 14
        r = 0.72 + 0.12 * math.sin(3 * a + 0.4) + rnd.uniform(-0.05, 0.05)
        pts.append(V((0.02 + r * math.cos(a) * 1.05, -0.02 + r * math.sin(a), 0.004)))
    vs = [m.bm.verts.new(p) for p in pts]
    f = m.bm.faces.new(vs)
    m.tag([f], "burlap")
    # ---- tarp lean-to at the back left with a bedroll under it
    lt = V((-0.55, 0.62, 0))
    for dx in (-0.28, 0.28):
        m.obox(lt + V((dx, -0.18, 0.21)), (0.03, 0.03, 0.42), "wood_dark")
    m.obox(lt + V((0, 0.02, 0.29)), (0.66, 0.46, 0.014), "cloth_mustard", rot=(-0.55, 0, 0))     # tarp: posts -> ground
    m.beam(lt + V((-0.3, -0.18, 0.42)), lt + V((0.3, -0.18, 0.42)), 0.022, "wood_dark")
    m.blob(lt + V((0.0, 0.1, 0.03)), V((0.2, 0.08, 0.03)), "cloth_blue", 8, 3)                   # bedroll
    m.cyl(lt + V((0.18, 0.1, 0.035)), 0.03, 0.12, "cloth_cream", axis=(1, 0, 0), segs=6)
    # ---- sorting baskets at the front left: berries, shiny caps
    for c, fill in ((V((-0.62, -0.55, 0)), "berries"), (V((-0.38, -0.7, 0)), "caps")):
        m.cyl(c + V((0, 0, 0.04)), 0.075, 0.08, "rope", segs=8, r2=0.085, cap="rope_dark")
        for k in range(5):
            a = k * 1.3 + 0.3
            p = c + V((0.04 * math.cos(a), 0.04 * math.sin(a), 0.085))
            if fill == "berries":
                m.blob(p, V((0.016, 0.016, 0.014)), "cloth_red" if k % 2 else "amethyst", 6, 3)
            else:
                m.cyl(p, 0.015, 0.006, "silver" if k % 2 else "gold", segs=6)
    # ---- crate with a lantern at the back right; campfire at the front right
    B.crate(m, V((0.62, 0.6, 0)), 0.16, rot=0.4)
    m.obox(V((0.62, 0.6, 0.2)), (0.06, 0.06, 0.07), "flame_yellow")
    m.obox(V((0.62, 0.6, 0.24)), (0.075, 0.075, 0.016), "iron_dark")
    fc = V((0.55, -0.48, 0))
    for k in range(8):
        a = k * math.tau / 8
        m.blob(fc + V((0.13 * math.cos(a), 0.13 * math.sin(a), 0.02)), V((0.04, 0.035, 0.03)), "stone_mid", 6, 3)
    for a in (0.3, 1.9, 3.6):
        d = V((math.cos(a), math.sin(a), 0))
        B.log(m, fc + d * 0.03 + V((0, 0, 0.025)), 0.018, 0.13, axis=tuple(d + V((0, 0, 0.35))))
    m.cyl(fc + V((0, 0, 0.004)), 0.09, 0.008, "soot", segs=8)
    # ---- the heap's static junk, on the front and the sides: the raccoon digs at the back (ang +90)
    on_heap(m, math.radians(15), 0.45, lambda m, p, n: m.cyl(p + n * 0.012, 0.018, 0.045, "iron_light", cap="rust",
                                                            axis=tuple(n + V((0.6, 0, 0))), segs=6))           # can
    on_heap(m, math.radians(-120), 0.3, lambda m, p, n: m.obox(p + n * 0.012, (0.11, 0.03, 0.012), "wood_weathered",
                                                               rot=(0.3, -0.5, 0.4)))                           # plank
    on_heap(m, math.radians(-60), 0.45, lambda m, p, n: m.blob(p + n * 0.01, V((0.012, 0.012, 0.016)), "fur_cream", 6, 3))  # core
    on_heap(m, math.radians(-175), 0.3, lambda m, p, n: m.obox(p + n * 0.02, (0.06, 0.035, 0.04), "leather_dark",
                                                               rot=(0, 0, 0.6)))                                 # boot
    # ---- big junk on the front of the pile: a cart wheel leaning on it, an old pot, a broken crate
    wc = V((HEAP_C.x - 0.24, HEAP_C.y - 0.3, 0.13))
    m.cyl(wc, 0.13, 0.025, "wood_mid", axis=(0.9, -0.3, 0.35), segs=10, cap="wood_dark")
    m.cyl(wc + V((0.01, 0, 0.002)), 0.03, 0.04, "iron_dark", axis=(0.9, -0.3, 0.35), segs=6)
    m.cyl(V((HEAP_C.x + 0.2, HEAP_C.y - 0.3, 0.17)), 0.055, 0.07, "iron", axis=(0.3, -0.5, 1), segs=8, cap="soot")
    m.obox(V((HEAP_C.x + 0.02, HEAP_C.y - 0.36, 0.06)), (0.14, 0.1, 0.1), "wood_weathered", rot=(0.2, 0.4, 0.5))
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- the heap mound itself: its own (still) object, the paws may dig into it, nothing else
    m = B.M()
    m.blob(HEAP_C, HEAP_R, "burlap", 12, 6)
    for k in range(10):                                                                    # leaves stuck on it
        ang = math.radians(rnd.uniform(-190, 10))
        hf = rnd.uniform(0.2, 0.9)
        sw = rnd.choice(["moss", "torch_orange", "moss_light", "rust"])
        on_heap(m, ang, hf, lambda m, p, n, sw=sw: m.obox(p + n * 0.002, (0.035, 0.022, 0.004), sw,
                                                          rot=n.to_track_quat("Z", "Y").to_euler()))
    # the bulk of the pile rises further toward the front, out of the raccoon's reach
    m.blob(BIG_C, BIG_R, "rope_dark", 12, 6)
    m.blob(BIG_C + V((0.16, 0.05, 0)), V((0.14, 0.13, 0.15)), "burlap", 10, 5)
    heap = m.obj("pr_heap", coll)
    PR.trim_below_floor(heap)
    heap.parent = root
    parts = {}
    # junk that jostles while the raccoon digs: a tin can, a bottle, a teacup (on the heap, off the dig spot)
    for nm, ang, hf, fn in (("pr_can", -5, 0.6, "can"), ("pr_bottle", 150, 0.55, "bottle"),
                            ("pr_cup", -95, 0.82, "cup")):
        p, n = heap_point(math.radians(ang), hf)
        m = B.M()
        if fn == "can":
            m.cyl(p + n * 0.024, 0.017, 0.042, "iron_light", cap="rust", axis=tuple(n), segs=6)
        elif fn == "bottle":
            m.cyl(p + n * 0.02, 0.016, 0.07, "verdigris", axis=tuple(n + V((0.0, 0.0, -0.3))), segs=6, r2=0.008)
        else:
            m.cyl(p + n * 0.018, 0.02, 0.03, "cloth_cream", cap="cloth_blue", axis=tuple(n), segs=7, r2=0.026)
        parts[nm] = A.part(m.obj(nm, coll), root, p)
    # the sack of finds that twitches, beside the heap (left)
    sk = V((-0.42, 0.1, 0))
    m = B.M()
    m.blob(sk + V((0, 0, 0.085)), V((0.075, 0.07, 0.08)), "burlap", 8, 5)
    m.cyl(sk + V((0, 0, 0.17)), 0.018, 0.035, "rope", segs=6)
    parts["pr_sack"] = A.part(m.obj("pr_sack", coll), root, sk)
    # campfire flames
    for i, (d, h, sw) in enumerate(((V((0, 0, 0)), 0.11, "torch_orange"), (V((0.025, 0.015, 0)), 0.075, "flame_yellow"),
                                    (V((-0.02, -0.018, 0)), 0.065, "torch_orange"))):
        m = B.M()
        c = fc + d + V((0, 0, 0.012))
        m.cyl(c + V((0, 0, h / 2)), 0.028 if i == 0 else 0.018, h, sw, segs=5, r2=0.0)
        parts[f"pr_flame_{i + 1}"] = A.part(m.obj(f"pr_flame_{i + 1}", coll), root, c)
    # a leaf that flutters on the heap's top
    p, n = heap_point(math.radians(-60), 0.95)
    m = B.M()
    m.obox(p + V((0.015, 0, 0.004)), (0.035, 0.022, 0.003), "torch_orange")
    parts["pr_leaf"] = A.part(m.obj("pr_leaf", coll), root, p + V((0, 0, 0.002)))
    return root, heap, parts


def clips(parts):
    TAU = 2 * math.pi

    def common(p):
        pose = {}
        for i, (k, ph) in enumerate(((3, 0.0), (5, 0.3), (4, 0.6))):
            fl = 1 + 0.12 * math.sin(TAU * (k * p + ph)) + 0.06 * math.sin(TAU * (2 * k * p + ph))
            pose[f"pr_flame_{i + 1}"] = (None, A.q((0, 0, 1), 25 * math.sin(TAU * (k * p + ph))), (1, 1, fl))
        tw = math.exp(-((p - 0.35) ** 2) / 0.0015) - 0.6 * math.exp(-((p - 0.42) ** 2) / 0.001)
        pose["pr_sack"] = (None, A.q((1, 0.3, 0), 6 * tw), (1, 1, 1 + 0.04 * abs(tw)))
        pose["pr_leaf"] = (None, A.q((1, 0, 0.2), 25 * max(0.0, math.sin(TAU * 2 * p)) ** 2), None)
        return pose

    def idle(p):
        return common(p)

    def work(p):
        pose = common(p)
        for i, (nm, ph) in enumerate((("pr_can", 0.1), ("pr_bottle", 0.45), ("pr_cup", 0.7))):
            j = math.exp(-((((p - ph) + 0.5) % 1.0 - 0.5) ** 2) / 0.003)            # a jolt when a paw digs nearby
            pose[nm] = (V((0, 0, 0.006 * j)), A.q((1, 0.5 * i, 0.2), 9 * j * math.sin(TAU * 6 * p)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, heap, parts = build(coll, random.Random(9))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(heap) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(heap)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "rummage_camp.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_rummage")
    allow = [(n, "pr_heap") for n in ("pr_can", "pr_bottle", "pr_cup", "pr_leaf")] + \
            [(f"pr_flame_{i}", NAME) for i in (1, 2, 3)] + [("pr_sack", NAME)] + \
            [("pr_flame_1", "pr_flame_2"), ("pr_flame_1", "pr_flame_3"), ("pr_flame_2", "pr_flame_3")]
    probs = A.check(root, 2, 2, crew=[(rig, mesh, None, "work", {"pr_heap": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_rummage_camp_loops.gif",
                       target=(0.0, 0.0, 0.15), dist=3.4, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
