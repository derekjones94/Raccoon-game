"""bld_fishing_spot_1x2: a little plank deck on a stone-rimmed pond, where a raccoon fishes (Dabbling).

The pond fills the right half of the lot (+X), the deck the left half. The raccoon sits at the deck's edge at
spot_work FACING THE WATER (+X), legs out over the edge, rod held still out over the pond (work_fish + prop_fishing_rod
in handslot.r). The line and float belong to the building: they hang from where the adult's rod tip is in work_fish
(it never moves) down to the water.

Clips (24 fps)
  idle  96 fr  ripples spread, reeds sway, lily pads bob, a fish jumps once
  work  96 fr  as idle, plus the line and float (hidden in idle): the float bobs, dips twice (on frames 29 and 69,
               when the raccoon's ears perk up in work_fish if both start together) with a ring of ripples each time;
               a fish flips in the bucket

Run:  python3 tools/build_fishing_spot.py   (--no-renders)
Out:  fishing_spot.blend, export/bld_fishing_spot_1x2.glb, renders/bld_fishing_spot_loops.gif, renders/qa_buildings.txt
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

ROOT = A.ROOT
V = Vector
NAME = "bld_fishing_spot_1x2"
DECK_Z = 0.1                     # deck top
WATER_Z = 0.05                   # water surface (inside a 0.07 rim)
RIM_Z = 0.07
POND = (-0.03, 0.435, -0.88, 0.88)           # pond outer rim: x0, x1, y0, y1
SPOT = V((-0.07, 0.12, DECK_Z + 0.002))      # the raccoon sits here, facing +X (the water)
FRAMES = 96


def rod_tip():
    """Where the adult's rod tip is in work_fish (it doesn't move), in the raccoon's own space (facing -Y)."""
    import build_raccoon_jobs as J
    import build_tools as T
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_animated.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rig = dst.objects[0]
    bpy.context.scene.collection.objects.link(rig)
    rig.location = (0, 0, 0)
    for t in rig.animation_data.nla_tracks:
        t.mute = True
    rig.animation_data.action = next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name == "work_fish")
    tips = []
    for f in (0, 24, 48, 72):
        bpy.context.scene.frame_set(f)
        tips.append(rig.pose.bones["handslot.r"].matrix @ T.ROD_TIP)
    bpy.data.objects.remove(rig)
    spread = max((a - tips[0]).length for a in tips)
    print(f"STAT rod tip (raccoon space) {tuple(round(c, 3) for c in tips[0])}, moves {spread * 1000:.2f} mm over the clip")
    return tips[0], J


def to_world(p):
    """Raccoon space (facing -Y) -> building space with the raccoon at SPOT facing +X."""
    return SPOT + Matrix.Rotation(math.radians(90), 3, "Z") @ p


def build(coll, rnd, tip_w):
    m = B.M()
    x0, x1, y0, y1 = POND
    # ---- pond: stone rim of chunky blocks, dark floor, water
    t = 0.05
    for (a, b, horiz) in (((x0, y0), (x1, y0), True), ((x0, y1), (x1, y1), True), ((x0, y0), (x0, y1), False),
                          ((x1, y0), (x1, y1), False)):
        L = (b[0] - a[0]) if horiz else (b[1] - a[1])
        n = max(2, int(L / 0.17))
        for k in range(n):
            u0, u1 = k / n, (k + 1) / n
            h = RIM_Z + rnd.uniform(-0.006, 0.006)
            if horiz:
                c = V(((a[0] + (b[0] - a[0]) * (u0 + u1) / 2), a[1], h / 2))
                size = (L / n - 0.004, t, h)
            else:
                c = V((a[0], a[1] + (b[1] - a[1]) * (u0 + u1) / 2, h / 2))
                size = (t, L / n - 0.004, h)
            m.obox(c, size, rnd.choice(["stone_mid", "stone_light", "stone_mid"]), top="stone_light")
    m.obox(V(((x0 + x1) / 2, 0, 0.004)), (x1 - x0 - t, y1 - y0 - t, 0.008), "stone_deep")          # pond floor
    m.obox(V(((x0 + x1) / 2, 0, WATER_Z - 0.003)), (x1 - x0 - t, y1 - y0 - t, 0.006), "water")     # water surface
    for c, s_ in ((V((x1 - 0.04, y1 - 0.04, RIM_Z)), 0.045), (V((x1 - 0.035, -0.25, RIM_Z)), 0.04),
                  (V((x0 + 0.02, y1 - 0.04, RIM_Z)), 0.04)):                                     # boulders on the rim
        m.blob(c, V((s_ * 1.1, s_, s_ * 0.75)), "stone_light", 6, 4)
    # ---- deck: planks on posts, the end over the rim; a plank ramp down to the ground at the front
    dx0, dx1, dy0, dy1 = -0.44, x0 + 0.03, -0.42, 0.62
    n = 7
    w = (dy1 - dy0) / n
    for k in range(n):
        y = dy0 + (k + 0.5) * w
        L = dx1 - dx0 - rnd.uniform(0, 0.03)
        m.obox(V((dx0 + L / 2, y, DECK_Z - 0.012)), (L, w - 0.006, 0.024),
               rnd.choice(["wood_mid", "wood_mid", "wood_light", "wood_weathered"]))
    for x in (dx0 + 0.04, dx1 - 0.05):
        for y in (dy0 + 0.04, (dy0 + dy1) / 2, dy1 - 0.04):
            m.obox(V((x, y, (DECK_Z - 0.024) / 2)), (0.04, 0.04, DECK_Z - 0.024), "wood_dark")
    for x in (dx0 + 0.02, dx1 - 0.02):                                                              # stringers
        m.obox(V((x, (dy0 + dy1) / 2, DECK_Z - 0.034)), (0.03, dy1 - dy0, 0.02), "wood_dark")
    for k in range(3):                                                                              # front steps
        m.obox(V(((dx0 + dx1) / 2 - 0.06, dy0 - 0.05 - k * 0.07, (DECK_Z - 0.03) * (2 - k) / 3 + 0.01)),
               (0.26, 0.065, 0.02), "wood_light" if k % 2 else "wood_mid")
    # ---- on the deck: bucket (its fish is a moving part), tackle box, coiled rope, lantern post at the back
    bk = V((-0.3, -0.25, DECK_Z))
    m.cyl(bk + V((0, 0, 0.004)), 0.058, 0.008, "wood_dark", segs=10)                                # bucket floor
    _tube(m, bk, 0.058, 0.064, 0.09, "wood_mid", 10)                                               # open bucket
    m.cyl(bk + V((0, 0, 0.03)), 0.067, 0.012, "iron", segs=10)
    m.cyl(bk + V((0, 0, 0.075)), 0.068, 0.012, "iron", segs=10)
    m.obox(V((-0.32, 0.42, DECK_Z + 0.04)), (0.13, 0.09, 0.08), "teal_dark", top="teal", rot=(0, 0, 0.2))   # tackle box
    m.obox(V((-0.32, 0.42, DECK_Z + 0.085)), (0.05, 0.012, 0.012), "iron_light", rot=(0, 0, 0.2))
    for k in range(3):
        m.cyl(V((-0.13, 0.5, DECK_Z + 0.006 + k * 0.009)), 0.045 - k * 0.008, 0.008, "rope", segs=8)
    lp = V((-0.4, 0.56, DECK_Z))
    m.obox(lp + V((0, 0, 0.17)), (0.03, 0.03, 0.34), "wood_dark")
    m.obox(lp + V((0.05, 0, 0.33)), (0.12, 0.022, 0.02), "wood_dark")
    m.obox(lp + V((0.09, 0, 0.27)), (0.05, 0.05, 0.065), "flame_yellow")
    m.obox(lp + V((0.09, 0, 0.31)), (0.064, 0.064, 0.016), "iron_dark")
    # ---- bank life: stones and moss by the steps, mushrooms by the lantern
    for p, s in (((-0.42, -0.62), 0.05), ((0.2, -0.94 + 0.05), 0.0), ((-0.1, -0.6), 0.035)):
        if s:
            m.blob(V((p[0], p[1], s * 0.4)), V((s * 1.3, s, s * 0.8)), "stone_light", 6, 3)
    m.blob(V((-0.25, -0.75, 0.0)), V((0.08, 0.05, 0.025)), "moss", 6, 3)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = _parts(coll, root, rnd, tip_w)
    return root, parts


def _tube(m, c, r_in, r_out, h, sw, segs):
    """An open-topped tube wall (bucket): outer + inner faces + rim, so you can see into it."""
    import bmesh
    rings = []
    for z, r in ((0, r_out), (h, r_out), (h, r_in), (0.008, r_in)):
        rings.append([m.bm.verts.new(c + V((math.cos(2 * math.pi * k / segs) * r, math.sin(2 * math.pi * k / segs) * r, z)))
                      for k in range(segs)])
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(segs):
            j = (k + 1) % segs
            faces.append(m.bm.faces.new((a[k], a[j], b[j], b[k])))
    bmesh.ops.recalc_face_normals(m.bm, faces=faces)
    m.tag(faces, sw)


def _parts(coll, root, rnd, tip_w):
    parts = {}
    x0, x1, y0, y1 = POND
    # float + line: the float rests on the water just under the rod tip (a touch toward the raccoon)
    bob = V((tip_w.x - 0.015, tip_w.y, WATER_Z + 0.004))
    m = B.M()
    m.blob(bob + V((0, 0, 0.008)), V((0.011, 0.011, 0.012)), "cloth_red", 6, 4)
    m.blob(bob + V((0, 0, 0.022)), V((0.007, 0.007, 0.006)), "cloth_cream", 6, 3)
    parts["pr_float"] = A.part(m.obj("pr_float", coll), root, bob)
    top = bob + V((0, 0, 0.026))
    m = B.M()
    m.beam(tip_w, top, 0.0025, "cloth_cream")
    parts["pr_line"] = A.part(m.obj("pr_line", coll), root, tip_w)
    # ripple rings (thin flat annuli on the water): two at the float, two out in the pond
    for i, c in enumerate((bob, bob, V((0.25, 0.55, WATER_Z)), V((0.15, -0.6, WATER_Z)))):
        m = B.M()
        _ring(m, c + V((0, 0, 0.0035)), 0.05, 0.042, "stone_frost", 12)
        parts[f"pr_ripple_{i + 1}"] = A.part(m.obj(f"pr_ripple_{i + 1}", coll), root, c + V((0, 0, 0.0035)))
    # lily pads
    for i, (c, r) in enumerate(((V((0.33, 0.35, WATER_Z)), 0.05), (V((0.08, 0.66, WATER_Z)), 0.04),
                                (V((0.3, -0.72, WATER_Z)), 0.045))):
        m = B.M()
        m.cyl(c + V((0, 0, 0.003)), r, 0.004, "moss", segs=8, cap="moss_light", rot=rnd.uniform(0, 3))
        if i == 0:
            m.blob(c + V((0.012, 0.01, 0.012)), V((0.012, 0.012, 0.01)), "cloth_cream", 6, 3)   # a flower
        parts[f"pr_lily_{i + 1}"] = A.part(m.obj(f"pr_lily_{i + 1}", coll), root, c)
    # reeds: clumps in the far corners, each blade swaying from its foot
    for i, (c, h) in enumerate(((V((0.4, 0.83, WATER_Z)), 0.2), (V((0.37, 0.8, WATER_Z)), 0.16),
                                (V((0.41, -0.83, WATER_Z)), 0.18), (V((0.0, 0.84, WATER_Z)), 0.14))):
        m = B.M()
        m.cyl(c + V((0, 0, h / 2)), 0.006, h, "moss", segs=4, r2=0.0015)
        m.cyl(c + V((0, 0, h * 0.82)), 0.009, 0.05, "wood_mid", segs=5)                    # bulrush head
        parts[f"pr_reed_{i + 1}"] = A.part(m.obj(f"pr_reed_{i + 1}", coll), root, c)
    # a fish that jumps in the pond (idle and work) and one that flips in the bucket (work)
    for nm, c, scale in (("pr_fish_jump", V((0.2, -0.15, WATER_Z - 0.03)), 1.0), ("pr_fish_bucket", V((-0.3, -0.25, DECK_Z + 0.03)), 0.8)):
        m = B.M()
        m.blob(c, V((0.032 * scale, 0.011 * scale, 0.014 * scale)), "silver", 7, 4)
        m.cyl(c + V((-0.038 * scale, 0, 0)), 0.014 * scale, 0.004, "teal", axis=(0, 1, 0), segs=3)
        parts[nm] = A.part(m.obj(nm, coll), root, c)
    return parts


def _ring(m, c, r_out, r_in, sw, segs):
    vo = [m.bm.verts.new(c + V((math.cos(2 * math.pi * k / segs) * r_out, math.sin(2 * math.pi * k / segs) * r_out, 0)))
          for k in range(segs)]
    vi = [m.bm.verts.new(c + V((math.cos(2 * math.pi * k / segs) * r_in, math.sin(2 * math.pi * k / segs) * r_in, 0)))
          for k in range(segs)]
    faces = [m.bm.faces.new((vo[k], vo[(k + 1) % segs], vi[(k + 1) % segs], vi[k])) for k in range(segs)]
    for f in faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    m.tag(faces, sw)


def dips(p):
    """Float dip strength (0..1): two bites a loop, on the raccoon's ear-perk beats."""
    return sum(math.exp(-((p - c) ** 2) / 0.0006) for c in (0.3, 0.72))


def clips(parts, tip_w):
    TAU = 2 * math.pi
    bob = parts["pr_float"].location.copy()
    line_rest = bob + V((0, 0, 0.026)) - tip_w

    def common(p):
        pose = {}
        for i in (1, 2, 3):                                   # lily pads: a slow lift and turn
            pose[f"pr_lily_{i}"] = (V((0, 0, 0.0015 * math.sin(TAU * (p + i * 0.3)))),
                                    A.q((0, 0, 1), 6 * math.sin(TAU * (p + i * 0.21))), None)
        for i in (1, 2, 3, 4):                                # reeds sway from the foot, out of step
            pose[f"pr_reed_{i}"] = (None, A.q((1, 0.4 * i, 0), 5 * math.sin(TAU * (2 * p + i * 0.17))), None)
        for i, ph in ((3, 0.1), (4, 0.6)):                    # pond ripples spread and fade
            u = (p * 2 + ph) % 1.0
            pose[f"pr_ripple_{i}"] = (None, None, (0.25 + 1.0 * u) if u < 0.95 else 0.001)
        # the fish: jumps once, a low arc that stays over the water, then hidden under it
        u = (p - 0.5) / 0.12
        if 0 <= u <= 1:
            arc = V((0.09 * u, 0.02 * u, 0.09 * 4 * u * (1 - u) + 0.02))
            pose["pr_fish_jump"] = (arc, A.q((0, 1, 0), -100 * (u - 0.5)), None)
        else:
            pose["pr_fish_jump"] = A.hidden()
        return pose

    def idle(p):
        pose = common(p)
        for n in ("pr_float", "pr_line", "pr_ripple_1", "pr_ripple_2"):
            pose[n] = A.hidden()
        pose["pr_fish_bucket"] = (None, A.q((1, 0, 0), 90), None)          # lies on its side in the bucket
        return pose

    def work(p):
        pose = common(p)
        d = dips(p)
        dz = 0.0025 * math.sin(TAU * 4 * p) - 0.009 * min(d, 1.0)          # bobbing, and pulled under on a bite
        pose["pr_float"] = (V((0, 0, dz)), None, None)
        new = line_rest + V((0, 0, dz))                                    # line follows the float, from the tip
        rot = line_rest.rotation_difference(new)
        pose["pr_line"] = (None, rot, (1, 1, 1))
        for i, c in ((1, 0.3), (2, 0.72)):                                 # a ring spreads from each bite
            u = (p - c) % 1.0 / 0.35
            pose[f"pr_ripple_{i}"] = (None, None, (0.2 + 1.1 * u) if u < 1 else 0.001)
        flip = math.exp(-((p - 0.55) ** 2) / 0.002) + math.exp(-((p - 0.62) ** 2) / 0.001)
        pose["pr_fish_bucket"] = (V((0, 0, 0.012 * min(flip, 1))), A.q((1, 0, 0), 90 - 70 * min(flip, 1)) @
                                  A.q((0, 0, 1), 25 * math.sin(TAU * p * 3) * min(flip, 1)), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    # the line must stretch with the float: scale it along its own length (it hangs from its pivot at the tip)
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    tip, J = rod_tip()
    tip_w = to_world(tip)
    print(f"STAT rod tip in the building: {tuple(round(c, 3) for c in tip_w)}")
    root, parts = build(coll, random.Random(7), tip_w)
    A.spot(root, "spot_work", SPOT, (1, 0, 0))
    clips(parts, tip_w)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "fishing_spot.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, rod = A.raccoon_at(sp, clip="work_fish", tool="prop_fishing_rod")
    allow = [("pr_fish_bucket", NAME), ("pr_fish_jump", NAME), ("pr_float", NAME), ("pr_line", "pr_float")] + \
            [(f"pr_ripple_{i}", NAME) for i in (1, 2, 3, 4)] + [(f"pr_lily_{i}", NAME) for i in (1, 2, 3)] + \
            [(f"pr_reed_{i}", NAME) for i in (1, 2, 3, 4)] + [("pr_ripple_1", "pr_float"), ("pr_ripple_2", "pr_float"),
                                                             ("pr_ripple_1", "pr_ripple_2")]
    probs = A.check(root, 1, 2, crew=[(rig, mesh, rod, "work", {"pr_line": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, rod], ROOT / "renders" / "bld_fishing_spot_loops.gif",
                       target=(0.0, -0.05, 0.1), dist=3.1, pitch=40, idle_frames=48, grid_n=5)


if __name__ == "__main__":
    main()
