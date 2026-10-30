"""bld_alarm_bell_1x1: the colony's alarm, a bronze bell in a little timber frame.

Two posts carry an axle with the bell under it; a lever off the axle reaches back toward the ringer, and the rope runs
from its end down into the ringer's upper paw, then hangs through the lower one. The frame stands across the lot's
diagonal; the ringer stands behind the bell (spot_work, facing it) and hauls on the rope with both paws (work_ring).
The rope comes in at a slant, well out in front of the face: the snout sits just above the paws. A shingled cap keeps the rain off; a sparrow sits on the frame when all is quiet.

Clips (24 fps)
  idle  48 fr  the bell sways a little in the wind, the rope with it; the sparrow pecks and hops on the beam
  work  48 fr  the bell rings: every haul on the rope swings it hard (two a loop), the clapper lags and strikes; the
               sparrow has flown

The rope follows build_raccoon_jobs.ring_pull, the same curve work_ring's paws follow: start the building's work
and the raccoon's work_ring together (both 48 frames).

Run:  python3 tools/build_alarm_bell.py   (--no-renders)
Out:  alarm_bell.blend, export/bld_alarm_bell_1x1.glb, renders/bld_alarm_bell_loops.gif, renders/qa_buildings.txt
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_alarm_bell_1x1"
FRAMES = 48
FLOOR = 0.012                                    # top of the cobbled pad
AX = V((-1, -1, 0)).normalized()                 # the frame stands across the lot's diagonal: the axle runs along AX,
WD = V((1, -1, 0)).normalized()                  # and the ringer stands out along WD (front right), facing -WD: the
                                                 # game camera sees the ringer side-on, the rope and bell behind
Z = V((0, 0, 1))
SPOT = V((0.22, -0.22, FLOOR + 0.0015))
KINK = SPOT - WD * J.ROPE.length + Z * J.RING_TOP           # the upper paw on the rope, before a pull (J.ROPE: straight ahead)
LEVER = 0.16
END = SPOT - WD * 0.40 + Z * (J.RING_TOP + 0.15)            # the lever's end: the rope runs up and out to it, well
AXLE = END - WD * LEVER                                     # clear of the ringer's snout (it sits just above the paws)
ROPE_BOT = SPOT.z + 0.09                         # the rope's tail end, below the lower paw at its lowest
IDLE_DROP = 0.2                                  # with nobody ringing: the rope's span hangs this far below the lever
POST = 0.2                                       # the posts, either side of the bell along the axle
YAW = (0.0, 0.0, -0.75 * math.pi)                  # boxes turned so their X runs along AX and their Y along WD


def at(a, w, z):
    """A point in the frame's own axes: a along the axle, w toward the ringer, z up (from the axle's foot)."""
    return V((AXLE.x, AXLE.y, 0.0)) + AX * a + WD * w + Z * z


def lever_angle(d):
    """The axle's turn (degrees about AX) when the rope is hauled down by d (0..1 of RING_PULL): the lever end drops
    as far as the paws do, so the rope keeps its length."""
    return -math.degrees(math.asin(J.RING_PULL * d / LEVER))


def end_at(ang):
    return AXLE + Quaternion(AX, math.radians(ang)) @ (WD * LEVER)


def build(coll, rnd):
    m = B.M()
    # ---- cobbled pad in the grass
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "moss")
    m.obox(V((0, 0, FLOOR - 0.006)), (0.8, 0.8, 0.004), "stone_mid")                       # grout, below the cobbles' tops
    k = 0                                                       # laid in staggered rows, grout showing between: no
    for row in range(9):                                        # cobble ever on another
        y = -0.352 + 0.088 * row
        for col in range(8):
            x = -0.35 + 0.1 * col + (0.05 if row % 2 else 0.0)
            if abs(x) > 0.36:
                continue
            h = FLOOR - 0.00005 * k                                                           # no two tops coplanar
            m.cyl(V((x + rnd.uniform(-0.004, 0.004), y + rnd.uniform(-0.004, 0.004), h / 2)), rnd.uniform(0.037, 0.042), h,
                  rnd.choice(["stone_mid", "stone_light", "stone_pale"]), segs=6, cap="stone_light", rot=rnd.uniform(0, 1))
            k += 1
    # ---- the frame: two posts on stone feet, raking struts, a beam across the top, the shingled cap
    top = AXLE.z + 0.12
    for sa in (-1, 1):
        a = sa * POST
        m.obox(at(a, 0, FLOOR + 0.02), (0.08, 0.1, 0.04), "stone_mid", top="stone_light", rot=YAW)
        m.obox(at(a, 0, (FLOOR + top) / 2), (0.04, 0.05, top - FLOOR), "wood_dark", rot=YAW)
        m.beam(at(a, -0.1, FLOOR + 0.03), at(a, 0, FLOOR + 0.2), 0.016, "wood_mid")
        m.beam(at(a, 0.1, FLOOR + 0.03), at(a, 0, FLOOR + 0.2), 0.016, "wood_mid")
        m.obox(at(a - sa * 0.03, 0, AXLE.z), (0.02, 0.05, 0.04), "iron_dark", rot=YAW)       # bearing block
        m.beam(at(a, 0, top - 0.08), at(a - sa * 0.1, 0, top), 0.014, "wood_mid")             # knee brace
    m.obox(at(0, 0, top + 0.015), (2 * POST + 0.1, 0.06, 0.03), "wood_mid", top="wood_light", rot=YAW)
    for sw in (-1, 1):                                                                      # cap: two shingle slabs
        ang = -math.radians(32) * sw                                                        # eaves down: a peaked cap
        m.obox(at(0, sw * 0.075, top + 0.07), (2 * POST + 0.07, 0.17, 0.016), "wood_bark", rot=(ang, 0, YAW[2]))
        for k in range(3):
            m.obox(at(0, sw * (0.03 + 0.05 * k), top + 0.105 - 0.032 * k), (2 * POST + 0.075, 0.006, 0.01), "wood_dark",
                   rot=(ang, 0, YAW[2]))
    m.obox(at(0, 0, top + 0.115), (2 * POST + 0.08, 0.03, 0.02), "wood_dark", rot=YAW)       # ridge
    m.obox(at(0, 0.032, top + 0.015), (0.12, 0.004, 0.024), "cloth_red", rot=YAW)            # a red warning band
    # ---- a spare coil of rope on one post, and on the other a little sign: a raccoon face in a red ring
    m.cyl(at(POST + 0.04, 0.03, 0.2), 0.035, 0.025, "rope", segs=8, axis=tuple(AX), cap="rope_dark")
    m.cyl(at(-POST - 0.023, 0, 0.24), 0.045, 0.006, "cloth_red", segs=10, axis=tuple(AX))
    m.cyl(at(-POST - 0.026, 0, 0.24), 0.034, 0.006, "cloth_cream", segs=10, axis=tuple(AX))
    m.obox(at(-POST - 0.03, 0, 0.245), (0.004, 0.05, 0.012), "fur_mask", rot=YAW)
    # ---- a bucket of water and a lantern on the ground, for night alarms
    m.cyl(V((0.3, 0.3, FLOOR + 0.04)), 0.05, 0.08, "wood_mid", segs=8, r2=0.042, cap="water")
    m.cyl(V((-0.32, -0.32, FLOOR + 0.035)), 0.026, 0.05, "iron_dark", segs=6, cap="iron")
    m.cyl(V((-0.32, -0.32, FLOOR + 0.035)), 0.02, 0.035, "flame_yellow", segs=6)
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)

    parts = {}
    # the bell on its axle, with the lever reaching toward the ringer
    mm = B.M()
    mm.cyl(AXLE, 0.016, 2 * POST - 0.08, "iron", axis=tuple(AX), segs=6)
    mm.obox(AXLE + V((0, 0, -0.012)), (0.13, 0.05, 0.03), "wood_dark", rot=YAW)              # headstock
    mm.cyl(AXLE + V((0, 0, -0.035)), 0.02, 0.02, "gold_dark", segs=8)                         # crown
    mm.cyl(AXLE + V((0, 0, -0.08)), 0.048, 0.07, "gold", segs=10, r2=0.058, cap="gold_dark")   # shoulder and waist
    mm.cyl(AXLE + V((0, 0, -0.14)), 0.058, 0.05, "gold", segs=10, r2=0.078)                   # flaring to the lip
    mm.cyl(AXLE + V((0, 0, -0.168)), 0.079, 0.008, "gold_light", segs=10)                     # lip
    mm.cyl(AXLE + V((0, 0, -0.165)), 0.07, 0.004, "soot", segs=10)                            # the dark mouth
    mm.cyl(AXLE + V((0, 0, -0.11)), 0.061, 0.008, "gold_dark", segs=10)                       # a band
    mm.beam(AXLE + WD * 0.01, END, 0.016, "wood_mid")                                         # the lever
    mm.cyl(END, 0.014, 0.03, "iron_dark", axis=tuple(AX), segs=6)                             # its end ring
    parts["pr_bell"] = A.part(mm.obj("pr_bell", coll), root, AXLE)
    # the clapper, hung inside from the crown
    mm = B.M()
    cp = AXLE + V((0, 0, -0.05))
    mm.beam(cp, cp + V((0, 0, -0.09)), 0.008, "iron_dark")
    mm.blob(cp + V((0, 0, -0.1)), V((0.017, 0.017, 0.02)), "iron", 6, 4)
    parts["pr_clapper"] = A.part(mm.obj("pr_clapper", coll), root, cp)
    # the rope: a span from the lever's end down into the upper paw (built along -Z, turned onto the span, so it can
    # stretch along its length), and the tail hanging from the paw, through the lower paw
    mm = B.M()
    span0 = KINK - END
    mm.beam(END, END - Z * (span0.length + 0.006), 0.009, "rope")
    ob = A.part(mm.obj("pr_rope_span", coll), root, END)
    ob.rotation_quaternion = (-Z).rotation_difference(span0.normalized())
    parts["pr_rope_span"] = ob
    mm = B.M()
    mm.beam(KINK + Z * 0.006, V((KINK.x, KINK.y, ROPE_BOT + 0.02)), 0.009, "rope")
    mm.cyl(V((KINK.x, KINK.y, ROPE_BOT + 0.01)), 0.012, 0.025, "rope_dark", segs=6)          # the knotted tail
    for z in (0.16, 0.2):                                                                      # grip wraps
        mm.cyl(V((KINK.x, KINK.y, SPOT.z + z)), 0.0075, 0.012, "cloth_red", segs=6)
    parts["pr_rope"] = A.part(mm.obj("pr_rope", coll), root, KINK)
    # the sparrow on the beam
    mm = B.M()
    bc = at(0.12, 0, top + 0.03 + 0.016)
    mm.blob(bc, V((0.022, 0.014, 0.014)), "fur_tan", 6, 4)
    mm.blob(bc - AX * 0.022 + Z * 0.012, V((0.011, 0.01, 0.01)), "fur_brown", 6, 3)
    mm.cyl(bc - AX * 0.035 + Z * 0.012, 0.003, 0.008, "gold", axis=tuple(-AX), segs=4, r2=0.0)
    mm.obox(bc + AX * 0.025 + Z * 0.004, (0.02, 0.006, 0.003), "fur_brown", rot=(0, -0.4, YAW[2]))
    parts["pr_bird"] = A.part(mm.obj("pr_bird", coll), root, bc - Z * 0.014)
    return root, parts


def clips(parts):
    span0 = KINK - END

    def bell(ang, clap, d, held=True):
        r = Quaternion(AX, math.radians(ang))
        cp_rel = V((0, 0, -0.05))
        e = end_at(ang)
        k = KINK - Z * (J.RING_PULL * d)
        if not held:                                            # nobody on it: the rope hangs straight down
            k = e - Z * IDLE_DROP
        span = k - e
        return {"pr_bell": (None, r, None),
                "pr_clapper": ((r @ cp_rel) - cp_rel, Quaternion(AX, math.radians(ang + clap)), None),
                "pr_rope_span": (e - END, span0.normalized().rotation_difference(span.normalized()),
                                 (1, 1, span.length / span0.length)),
                "pr_rope": (k - KINK, None, None)}

    def idle(p):
        pose = bell(3 * math.sin(TAU * p), -1.5 * math.sin(TAU * p - 0.6), 0.0, held=False)
        hop = max(0.0, math.sin(TAU * 2 * p)) ** 4
        peck = math.exp(-((p - 0.7) ** 2) / 0.002) + math.exp(-((p - 0.8) ** 2) / 0.002)
        pose["pr_bird"] = (AX * (0.02 * math.sin(TAU * p)) + Z * (0.012 * hop),
                           A.q((0, 0, 1), 180 if 0.125 < p < 0.625 else 0) @ Quaternion(WD, math.radians(30 * peck)), None)
        return pose

    def work(p):
        d = J.ring_pull(p)
        u = (2 * p) % 1.0                                       # the clapper lags the swing and strikes at the top
        clap = 14 * math.sin(TAU * (u - 0.12)) * (0.6 + 0.4 * d)
        pose = bell(lever_angle(d), max(-14.0, min(14.0, clap)), d)
        pose["pr_bird"] = A.hidden()
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(7))
    A.spot(root, "spot_work", SPOT, tuple(-WD))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "alarm_bell.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_ring")
    allow = [("pr_bell", NAME), ("pr_clapper", "pr_bell"), ("pr_rope_span", "pr_bell"), ("pr_rope_span", "pr_rope"),
             ("pr_bird", NAME)]
    probs = A.check(root, 1, 1, crew=[(rig, mesh, None, "work", {"pr_rope": None, "pr_rope_span": None})], allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_alarm_bell_loops.gif",
                       target=(0.0, 0.0, 0.22), dist=2.2, pitch=38, idle_frames=48, grid_n=3)


if __name__ == "__main__":
    main()
