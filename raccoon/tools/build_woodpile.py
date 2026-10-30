"""bld_woodpile_1x1: the woodpile, where a raccoon chops firewood (Timbering).

A chopping stump at the front with a hatchet stuck in it, a neat stack of rounds behind between two stakes, a
basket of kindling, a few chips on the ground. The raccoon stands at spot_work facing the front (toward the game
camera) and swings prop_axe one-handed on its right; the edge lands on the upright log on the stump.

Clips (24 fps)
  idle  48 fr  still: the hatchet rests in the stump
  work  64 fr  the hatchet is in the raccoon's paw (hidden here), a log stands on the stump; every 32 frames the
               edge lands (raccoon work_chop frame 0) and chips fly off the log, settle, and shrink away.
               Start the building's work and the raccoon's work_chop together: 64 = 2 x 32, hits on 0 and 32.

Run:  python3 tools/build_woodpile.py   (--no-renders)
Out:  woodpile.blend, export/bld_woodpile_1x1.glb, renders/bld_woodpile_*.png/gif, renders/qa_buildings.txt
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
import build_tools as T  # noqa: E402

ROOT = A.ROOT
V = Vector
NAME = "bld_woodpile_1x1"
SPOT = V((0.06, 0.03, 0.002))                         # raccoon stands here, facing the front (-Y)
HIT = SPOT + V((J.CHOP_HIT.x, J.CHOP_HIT.y, J.CHOP_HIT.z))     # raccoon space == building space (facing -Y)
STUMP_R, STUMP_H = 0.085, 0.042
LOG_R = 0.034
WORK, IDLE, CHOP = 64, 48, 32


def build(coll, rnd):
    m = B.M()
    # ---- chopping stump: bark sides, cut top with rings, a couple of roots
    c = V((HIT.x, HIT.y, 0))
    m.cyl(c + V((0, 0, STUMP_H / 2)), STUMP_R, STUMP_H, "wood_bark", cap="wood_cut", segs=9, rot=0.2)
    m.cyl(c + V((0, 0, STUMP_H + 0.001)), STUMP_R * 0.55, 0.002, "wood_light", segs=9, rot=0.2)        # growth ring
    for a in (0.6, 2.4, 4.3):
        d = V((math.cos(a), math.sin(a), 0))
        m.beam(c + d * (STUMP_R * 0.7) + V((0, 0, 0.012)), c + d * (STUMP_R + 0.045) + V((0, 0, 0.004)), 0.022, "wood_bark")
    # ---- the stack: a 3-2-1 pyramid of rounds lying along X between two pairs of stakes, at the back, clear of the
    #      raccoon's tail; ends cut (pale rings)
    r, gap = 0.036, 0.003
    y0 = 0.31
    rows = [(0, 3), (1, 2), (2, 1)]
    for lvl, cnt in rows:
        z = r + lvl * math.sqrt(3) * (r + gap / 2)
        for i in range(cnt):
            y = y0 + (i + lvl * 0.5 - 1) * (2 * r + gap) + r + gap / 2
            L = 0.46 - 0.03 * ((i + lvl) % 2)
            B.log(m, V((0.02 * ((i + lvl) % 2) - 0.01, y, z)), r, L, axis=(1, 0, 0))
    for x in (-0.27, 0.27):
        for dy in (-1, 1):
            yy = y0 + r + dy * (2.2 * r + 0.01)
            m.obox(V((x, yy, 0.105)), (0.024, 0.024, 0.21), "wood_dark", rot=(dy * 0.08, 0, 0))
    # ---- split halves in a little heap left of the stump (the morning's work)
    hp = V((-0.3, -0.2, 0))
    for k, (dx, dy, rz, lvl) in enumerate(((0, 0, 0.2, 0), (0.0, 0.06, -0.1, 0), (0.01, 0.03, 0.1, 1))):
        a0 = rz
        y = hp.y + dy
        x0 = hp.x + dx - 0.09
        prof = [(y - 0.034, 0.0), (y + 0.034, 0.0), (y + 0.024, 0.024), (y, 0.034), (y - 0.024, 0.024)]
        zz = 0.034 * lvl
        m.prism_x([(py, pz + zz) for py, pz in prof], x0, x0 + 0.18, "wood_bark", ends="wood_cut")
    # ---- old chips lying round the stump (static), moss
    for k in range(6):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(STUMP_R + 0.03, STUMP_R + 0.12)
        p = c + V((math.cos(a) * d, math.sin(a) * d, 0.003))
        if p.y > SPOT.y - 0.12:                               # not under the raccoon's feet
            continue
        m.obox(p, (0.03, 0.016, 0.006), "wood_cut", rot=(0, 0, rnd.uniform(0, 3)))
    m.blob(V((0.33, -0.33, 0.0)), V((0.06, 0.05, 0.03)), "moss", 6, 3)
    m.obox(V((0, 0, 0.0005)), (0.94, 0.94, 0.001), "moss")                     # the ground (thin: the chopper's feet
    m.blob(V((0.02, -0.05, -0.012)), V((0.3, 0.26, 0.0135)), "wood_weathered", 10, 3)   # stand just on it), trodden earth
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- moving parts
    parts = {}
    # the hatchet resting in the stump (idle), edge down into the cut top, handle leaning back over the right
    ax = T.prop_axe(coll)
    ax.name = "pr_hatchet_rest"
    edge_world = V((HIT.x + 0.01, HIT.y - 0.02, STUMP_H - 0.01))   # edge bitten 1 cm into the stump top
    Tm = J._sagittal(-38)                                     # head down in the wood, handle rising up and back
    Tm = J.Matrix.Rotation(math.radians(200), 3, "Z") @ Tm    # handle leaning back and to the side, off the log spot
    grip = edge_world - Tm @ T.AXE_EDGE
    ax.data.transform(J.Matrix.Translation(grip) @ Tm.to_4x4())
    parts["pr_hatchet_rest"] = A.part(ax, root, grip)
    # the log to split: upright on the stump, top exactly at the hit point
    m = B.M()
    lc = V((HIT.x, HIT.y, STUMP_H + 0.001))
    m.cyl(lc + V((0, 0, (HIT.z - lc.z) / 2)), LOG_R, HIT.z - lc.z, "wood_bark", cap="wood_cut", segs=7)
    parts["pr_log"] = A.part(m.obj("pr_log", coll), root, lc)
    # chips that fly on each hit
    chips = []
    for k in range(4):
        m = B.M()
        m.obox(HIT + V((0, 0, 0.01)), (0.024, 0.014, 0.006), "wood_cut")          # built where it flies from
        o = m.obj(f"pr_chip_{k + 1}", coll)
        parts[o.name] = A.part(o, root, HIT + V((0, 0, 0.01)))
        chips.append(o.name)
    return root, parts, chips


CHIP_PATHS = [  # (direction in plane, distance, peak height, spin axis): away from the raccoon (it stands at +Y)
    (V((-0.8, -0.6, 0)), 0.15, 0.09, (1, 0, 0.3)), (V((0.7, -0.7, 0)), 0.14, 0.11, (0, 1, 0.2)),
    (V((1.0, -0.05, 0)), 0.13, 0.07, (0.3, 1, 0)), (V((0.15, -1.0, 0)), 0.17, 0.08, (1, 0.2, 0)),
]


def smooth_land(u):
    """Spin progress that finishes a little before touchdown, so the chip comes down flat."""
    return min(u / 0.85, 1.0)


def clips(parts, chips):
    def idle(p):
        pose = {n: A.hidden() for n in chips}
        pose["pr_log"] = A.hidden()
        return pose

    def work(p):
        f = p * WORK
        tau = f % CHOP                                        # frames since the last hit (0 = the edge lands)
        pose = {"pr_hatchet_rest": A.hidden()}
        squash = 1 - 0.05 * math.exp(-tau / 1.2)              # the log takes the blow
        pose["pr_log"] = (None, None, (1 + 0.02 * math.exp(-tau / 1.2), 1 + 0.02 * math.exp(-tau / 1.2), squash))
        for name, (d, dist, peak, spin) in zip(chips, CHIP_PATHS):
            if tau < 1:
                pose[name] = A.hidden()
                continue
            u = min((tau - 1) / 9, 1.0)                       # 9 frames of flight
            ground = -(HIT.z + 0.01) + 0.0052                 # chip's centre when it lies flat on the ground
            z = 4 * peak * u * (1 - u) + ground * u * u       # up, over, down onto the floor
            off = d.normalized() * dist * (1 - (1 - u) ** 1.6) + V((0, 0, z))
            rot = A.q(spin, 360 * smooth_land(u))             # one whole tumble: it lands flat
            fade = 1.0 if tau < 22 else max(0.001, 1 - (tau - 22) / 8)
            pose[name] = (off, rot, fade if tau < 30 else 0.001)
        return pose

    A.animate(parts, {"idle": (IDLE, idle), "work": (WORK, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts, chips = build(coll, random.Random(4))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts, chips)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "woodpile.blend"), relative_remap=True)
    A.export()
    # ---- QA with a raccoon chopping at the spot
    sp = bpy.data.objects["spot_work"]
    rig, mesh, axe = A.raccoon_at(sp, clip="work_chop", tool="prop_axe")
    hits = (0, 1, 2, 3, 4, 5)                                 # raccoon frames the edge sits in the log (hit + rebound)
    contacts = {"pr_log": hits, **{c: hits for c in chips}}
    probs = A.check(root, 1, 1, crew=[(rig, mesh, axe, "work", contacts)],
                    allow=[("pr_hatchet_rest", NAME), ("pr_log", NAME)])
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh, axe], ROOT / "renders" / "bld_woodpile_loops.gif",
                       target=(0.0, 0.0, 0.12), dist=1.9, pitch=38, idle_frames=24, work_repeat=1)


if __name__ == "__main__":
    main()
