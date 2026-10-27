"""Job clips: the raccoon doing a building's work, with its tool held right.

  work_chop     one-handed hatchet at the woodpile, swung out on the right: the EDGE comes down onto the log
  work_fish     sitting at the end of the pier, rod held still out over the water (the building owns line + bobber)
  work_scrub    wading ankle-deep in the washing pool's shallows, crouched, paws rubbing food in the water
  work_rummage  crouched at the junk heap, paws taking turns digging at it

How they are made: every frame the body is posed (rotations like the other actions), the feet (or the seat) are
planted on the floor, then each arm is solved with a two-bone IK so the hand slot lands exactly on its target:
  * a tool hand gets a position AND an orientation: its hand slot frame IS the tool's frame (see build_tools.py), so
    the tool's edge / tip are exactly where the clip wants them;
  * a free hand (or the second hand on a handle) gets a position; the paw keeps the forearm's line.
Every frame is keyed (not every other), so the paws stay on the handle between keys too. Targets are written for
the adult in its own space (feet at z 0, facing -Y, +X = its left) and scaled for the kit and the elder.

Used by build_raccoon_anims.py (bakes these after the six base actions) and by the building scripts (which place a
raccoon at the building's spot_work marker and check it for clipping).
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_raccoon_anims as AN  # noqa: E402
from build_raccoon_anims import X, Y, Z, act, merge, pose_quats, tail_sway  # noqa: E402
import build_tools as T  # noqa: E402

V = Vector
TAU = 2 * math.pi
FWD, UP, LEFT = V((0, -1, 0)), V((0, 0, 1)), V((1, 0, 0))
ADULT_K = 1.06                      # the adult's build scale (spec scale 1.0 x 1.06): targets are written for it


def loc(f=0.0, u=0.0, l=0.0):
    """A point in the raccoon's own space: f forward, u up, l to its left (adult metres)."""
    return FWD * f + UP * u + LEFT * l


def frame_yz(y_dir, z_hint):
    """Orthonormal frame (as a 3x3 with X, Y, Z columns) with Y along y_dir and Z as close to z_hint as possible."""
    y = V(y_dir).normalized()
    z = (V(z_hint) - y * V(z_hint).dot(y)).normalized()
    return Matrix((y.cross(z), y, z)).transposed()


def frame_yx(y_dir, x_hint):
    y = V(y_dir).normalized()
    x = (V(x_hint) - y * V(x_hint).dot(y)).normalized()
    return Matrix((x, y, x.cross(y))).transposed()


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ramp(p, a, b):
    return smooth((p - a) / (b - a))


# ---------------------------------------------------------------- arm IK
def _rest(rig, name):
    b = rig.data.bones[name]
    return b.matrix_local.to_3x3().normalized(), b.head_local.copy(), b.tail_local.copy()


def arm_rots(rig, side, grip, Ts=None, pole=None):
    """Rotations (pose_quats entries) that put handslot.<side> at `grip` (armature space). With Ts (a 3x3) the hand
    slot also takes that orientation; without, the paw keeps the forearm's line. The rig must already be posed
    for the body (the shoulder is read from the pose). Returns (rots, reach_miss)."""
    sd = side
    Mu, hu, tu = _rest(rig, f"upperarm.{sd}")
    Ml, hl, tl = _rest(rig, f"lowerarm.{sd}")
    Mw, hw, _ = _rest(rig, f"wrist.{sd}")
    Mh, _, _ = _rest(rig, f"hand.{sd}")
    Ms, hs, _ = _rest(rig, f"handslot.{sd}")
    a, b = (tu - hu).length, (tl - hl).length
    S = rig.pose.bones[f"upperarm.{sd}"].head.copy()
    out = LEFT if sd == "l" else -LEFT
    pole = V(pole) if pole is not None else (out * 0.6 - UP * 1.0 + V((0, 0.4, 0)))
    W = grip.copy()
    D = None
    for _ in range(4 if Ts is None else 1):
        if Ts is not None:
            D = Ts @ Ms.inverted()                          # the wrist-hand-slot group turns rigidly by D
        elif D is None:
            D = Matrix.Identity(3)
        W = grip - D @ (hs - hw)
        d = W - S
        L = d.length
        di = d.normalized()
        Lc = min(max(L, abs(a - b) + 1e-4), a + b - 1e-4)
        x = (a * a - b * b + Lc * Lc) / (2 * Lc)
        h = math.sqrt(max(a * a - x * x, 0.0))
        pv = pole - di * pole.dot(di)
        pv = pv.normalized() if pv.length > 1e-6 else out
        E = S + di * x + pv * h
        if Ts is not None and h > 1e-5:
            # a held tool: of all elbow positions on the circle that keep the paw on the grip, take the one where the
            # forearm crosses the handle nearest a right angle (a fist round a handle), leaning toward the pole
            hd = Ts @ V((0, 1, 0))
            u_ = pv
            v_ = di.cross(u_).normalized()
            C = S + di * x
            best = None
            for k in range(72):
                ph = TAU * k / 72
                Ek = C + (u_ * math.cos(ph) + v_ * math.sin(ph)) * h
                fore = (S + di * Lc - Ek).normalized()
                score = abs(fore.dot(hd)) + 0.05 * (1 - math.cos(ph))
                if best is None or score < best[0]:
                    best = (score, Ek)
            E = best[1]
        Wr = S + di * Lc
        if Ts is None:                                      # free paw: follows the forearm, so D depends on it
            fore_rest = (tl - hl).normalized()
            D = fore_rest.rotation_difference((Wr - E).normalized()).to_matrix()   # approx.; bake_job corrects
    rots = {f"upperarm.{sd}": [("AIM", tuple(E - S))], f"lowerarm.{sd}": [("AIM", tuple(Wr - E))]}
    if Ts is not None:
        rots[f"wrist.{sd}"] = [("MAT", D @ Mw)]
        rots[f"hand.{sd}"] = [("MAT", D @ Mh)]
    return rots, (W - Wr).length


# ---------------------------------------------------------------- the jobs
# Each returns: body rotations (with HANG), hips offset, support ("legs" / "seat"), arms {side: (grip, Ts, pole)}.
CHOP_X = -0.095                                     # the swing plane: out on the right, clear of belly and cheek
CHOP_HIT = loc(f=0.25, u=0.08, l=CHOP_X)            # where the edge meets the log (top of the upright log on the block)


def _sagittal(deg):
    """Axe frame with the handle `deg` above level, pointing straight ahead, the edge facing the way a downward swing
    travels (so the swing always leads with the edge)."""
    th = math.radians(deg)
    d = FWD * math.cos(th) + UP * math.sin(th)
    x = FWD * math.sin(th) - UP * math.cos(th)
    return Matrix((x, d, x.cross(d))).transposed()


# A one-handed hatchet chop in a vertical plane out to the raccoon's right: the arms are short and the belly round,
# so two paws on one handle in front of the belly can't happen without the forearms sinking into it. Key frames of the
# hatchet (handle angle above level, grip point); everything stays in the plane l = CHOP_X, edge leading on the way down.
CHOP_KEYS = [(0.0, -6, loc(f=0.25, u=0.08, l=CHOP_X)), (0.5, 55, loc(f=0.08, u=0.2, l=CHOP_X - 0.012)),
             (1.0, 120, loc(f=0.005, u=0.24, l=CHOP_X - 0.02))]


AXE_EDGE_SLOT = T.AXE_EDGE


def _axe_at(t):
    """Hatchet frame and grip for t: 0 = edge on the log, 1 = raised up past the shoulder."""
    for (t0, a0, g0), (t1, a1, g1) in zip(CHOP_KEYS, CHOP_KEYS[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            Tm = _sagittal(a0 + (a1 - a0) * u)
            if t0 == 0.0:                                   # first leg: grip follows from the edge on the log
                g_imp = CHOP_HIT - _sagittal(a0) @ AXE_EDGE_SLOT
                return Tm, g_imp.lerp(g1, smooth(u))
            return Tm, g0.lerp(g1, smooth(u))
    return _sagittal(CHOP_KEYS[-1][1]), CHOP_KEYS[-1][2]


def chop(p):
    # t: 0 = edge in the log, 1 = raised. Hit on frame 0: stuck a moment, lift, hold, a fast swing down to p = 1
    if p < 0.1:
        t = 0.04 * math.sin(math.pi * p / 0.1)                      # small rebound off the log
    elif p < 0.6:
        t = smooth((p - 0.1) / 0.5)
    elif p < 0.8:
        t = 1.0
    else:
        u = (p - 0.8) / 0.2
        t = 1 - u * u                                               # accelerating down
    Ts, grip = _axe_at(t)
    hold = smooth((p - 0.6) / 0.2) * (1 - smooth((p - 0.8) / 0.05)) if p >= 0.6 else 0.0   # anticipation, body only
    lean = 14 * (1 - t) - 3 * t - 4 * hold
    hit = math.exp(-((p if p < 0.5 else p - 1) ** 2) / 0.004)
    rots = act({
        "upperleg.l": [(Y, -14), (X, -18)], "upperleg.r": [(Y, 14), (X, -8)],          # wide stance, left foot forward
        "lowerleg.l": [(X, 24)], "lowerleg.r": [(X, 16)], "foot.l": [(X, -6)], "foot.r": [(X, -8)],
        "spine": [(X, 6 + lean * 0.55), (Z, -6 * t)], "chest": [(X, lean * 0.45), (Z, -8 * t)],
        "head": [(X, 6 * (1 - t) - 3 * hit), (Z, 10 * t)],          # eyes stay on the log
        "ear.l": [(Y, -14 * hit)], "ear.r": [(Y, 14 * hit)],
    }, tail_sway(p, 6, 1))
    bal = loc(f=0.06 - 0.02 * t, u=0.115 + 0.02 * t, l=0.105)           # left paw out to the side, for balance
    arms = {"r": (grip, Ts, None), "l": (bal, None, LEFT * 1.0 - UP * 0.4 + V((0, 0.3, 0)))}   # balance elbow well out
    return rots, -0.006 * (1 - t), "legs", arms


FISH_GRIP = loc(f=0.075, u=0.105, l=-0.08)             # beside the right hip, butt clear of the belly
FISH_DIR = (FWD * math.cos(math.radians(30)) + UP * math.sin(math.radians(30)) - LEFT * 0.12).normalized()


def fish(p):
    """Sitting at the pier's end, legs out over the edge. The rod NEVER moves (its tip is where the building hangs
    the line from); breathing, a slow look about, ear twitches when the float dips (twice a loop), the tail."""
    breath = AN.s(p, 2)
    dip = sum(math.exp(-((p - c) ** 2) / 0.0012) for c in (0.3, 0.72))
    rots = act({
        "upperleg.l": [(Y, -30), (X, -72)], "upperleg.r": [(Y, 30), (X, -72)],             # legs out over the edge, apart
        "lowerleg.l": [(X, 40)], "lowerleg.r": [(X, 40)], "foot.l": [(X, 10)], "foot.r": [(X, 10)],
        "spine": [(X, 4 + 1.2 * breath)], "chest": [(X, 3 + 1.2 * breath)],
        "head": [(X, 10 + 4 * dip), (Z, 7 * math.sin(TAU * p) * (1 - min(dip, 1)))],
        "ear.l": [(Y, 18 - 22 * min(dip, 1))], "ear.r": [(Y, -18 + 22 * min(dip, 1))],
        "tail_1": [(X, -40)], "tail_2": [(X, -15)],
    }, tail_sway(p, 6, 1, 0.12))
    Ts = frame_yz(FISH_DIR, UP)                                     # reel underneath, rod out over the water
    arms = {"r": (FISH_GRIP, Ts, None), "l": (loc(f=0.09, u=0.085, l=0.036), None, None)}    # left paw rests on its knee
    return rots, -0.05, "seat", arms


SCRUB_C = loc(f=0.108, u=0.056)                      # middle of the two paws: just in the water
SCRUB_WATER = 0.052                                  # water surface over the raccoon's feet: it WADES in the shallows


def scrub(p):
    """Crouched ankle-deep in the shallows, leaning over; the paws rub small circles in the water, opposite each other
    (raccoons 'wash' their food). Nothing solid between the raccoon and the water: with this round body and these
    short arms, any rim in front of it would sit in its wrists or belly."""
    a = TAU * p * 2
    r = 0.009
    pr = SCRUB_C + loc(l=-0.024) + loc(f=r * math.cos(a), l=r * math.sin(a))
    pl = SCRUB_C + loc(l=0.024) + loc(f=-r * math.cos(a), l=-r * math.sin(a))
    bob = AN.s(p, 2)
    rots = act({
        "upperleg.l": [(Y, -18), (X, -70)], "upperleg.r": [(Y, 18), (X, -70)],             # deep crouch, knees apart
        "lowerleg.l": [(X, 96)], "lowerleg.r": [(X, 96)], "foot.l": [(X, -26)], "foot.r": [(X, -26)],
        "spine": [(X, 30 + 1.5 * bob)], "chest": [(X, 16 + 1.5 * bob)], "head": [(X, -16), (Z, 4 * AN.s(p, 1))],
        "ear.l": [(Y, 10)], "ear.r": [(Y, -10)],
        "tail_1": [(X, -30)],
    }, tail_sway(p, 5, 1))
    return rots, 0.0, "legs", {"r": (pr, None, None), "l": (pl, None, None)}


RUMMAGE_REACH = [loc(f=0.135, u=0.105, l=-0.03), loc(f=0.14, u=0.095, l=0.035)]     # right, left: on the heap


def rummage(p):
    """Crouched at the heap; the paws take turns: reach in, scrabble, pull back up to the chest."""
    def paw(ph, reach, home):
        t = (p + ph) % 1.0
        out = ramp(t, 0.0, 0.22) * (1 - ramp(t, 0.5, 0.72))
        scr = 0.008 * math.sin(TAU * t * 6) * ramp(t, 0.2, 0.25) * (1 - ramp(t, 0.45, 0.5))
        return home.lerp(reach, out) + loc(l=scr, u=abs(scr) * 0.5)
    hf, hu = (0.15, 0.13) if KIT else (0.13, 0.145)                # the kit's head is big for its body: paws further out
    pr = paw(0.0, RUMMAGE_REACH[0], loc(f=hf, u=hu, l=-0.065))
    pl = paw(0.5, RUMMAGE_REACH[1], loc(f=hf, u=hu, l=0.065))
    side = AN.s(p, 1)
    rots = act({
        "upperleg.l": [(Y, -10), (X, -46)], "upperleg.r": [(Y, 10), (X, -46)],
        "lowerleg.l": [(X, 64)], "lowerleg.r": [(X, 64)], "foot.l": [(X, -18)], "foot.r": [(X, -18)],
        "spine": [(X, 30)], "chest": [(X, 16), (Z, 5 * side)], "head": [(X, -12), (Z, 8 * side)],
        "ear.l": [(Y, 12 + 6 * side)], "ear.r": [(Y, -12 + 6 * side)],
    }, tail_sway(p, 8, 2, 0.1))
    return rots, 0.0, "legs", {"r": (pr, None, None), "l": (pl, None, None)}


KIT = False          # set while baking the kit (its own proportions: see rummage)

JOBS = {   # clip: (fn, frames, tool)
    "work_chop": (chop, 32, "prop_axe"),
    "work_fish": (fish, 96, "prop_fishing_rod"),
    "work_scrub": (scrub, 48, None),
    "work_rummage": (rummage, 48, None),
}


# ---------------------------------------------------------------- keeping paws out of the body
import os  # noqa: E402
NOPUSH = bool(os.environ.get("JOB_NOPUSH"))
RAYS = [V(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.62, 0.55, -0.2), (0.12, -0.9, 0.35))]


def _forearm_verts(rig, ob):
    """Per side: the vertices that the forearm / wrist / paw move (dominant weight), which must stay out of the body.
    Vertices already tucked inside the body in the arms-down look (the inner side of the arm tube where it meets the
    flank) are left out, the same way check_character.py does: they are hidden by design."""
    names = {i: g.name for i, g in enumerate(ob.vertex_groups)}
    out = {"l": [], "r": []}
    for v in ob.data.vertices:
        if v.groups:
            g = names[max(v.groups, key=lambda e: e.weight).group]
            if g.startswith(("lowerarm.", "wrist.", "hand.")):
                out[g[-1]].append(v.index)
    qs = pose_quats(rig, AN.HANG)
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = qs[pb.name]
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    trees = _skins(me, ob)
    for sd in out:
        out[sd] = [i for i in out[sd] if _inside(trees, me.vertices[i].co)[0] == 0.0]
    ev.to_mesh_clear()
    return out


def _skins(me, ob):
    """BVHs of the body and of the head (outer skins), from the deformed mesh."""
    import build_raccoon_blockout as RB
    from mathutils.bvhtree import BVHTree
    grp = ob.data.attributes["grp"].data
    co = [v.co.copy() for v in me.vertices]
    trees = []
    for part in ("body", "head"):
        polys = [list(p.vertices) for p in me.polygons if RB.GROUPS[grp[p.index].value] == part]
        trees.append(BVHTree.FromPolygons(co, polys))
    return trees


def _inside(trees, p):
    """(depth, outward direction) of p inside the body or head, or (0, None)."""
    best = (0.0, None)
    for t in trees:
        votes = 0
        for d in RAYS:
            n, o = 0, p.copy()
            for _ in range(24):
                hit = t.ray_cast(o, d)
                if hit[0] is None:
                    break
                n += 1
                o = hit[0] + d * 1e-6
            votes += n % 2
        if votes >= 2:
            near = t.find_nearest(p)
            if near[3] > best[0]:
                best = (near[3], (near[0] - p).normalized())
    return best


def arm_intrusion(rig, ob, fverts):
    """Per side: (deepest forearm/paw vertex depth inside body or head, the way out)."""
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    trees = _skins(me, ob)
    res = {}
    for side, idx in fverts.items():
        best = (0.0, None)
        for i in idx:
            d = _inside(trees, me.vertices[i].co)
            if d[0] > best[0]:
                best = d
        res[side] = best
    ev.to_mesh_clear()
    return res


# ---------------------------------------------------------------- baking
def bake_job(rig, ob, name, k, report=None):
    """Key a job clip on every frame, ground-locked, arms solved onto their targets."""
    global KIT
    fn, frames, tool = JOBS[name]
    ratio = k / ADULT_K
    KIT = ratio < 0.8
    act_ = bpy.data.actions.new(name)
    rig.animation_data_create()
    rig.animation_data.action = act_
    hips = rig.data.bones["hips"]
    up_local = hips.matrix_local.to_3x3().inverted() @ V((0, 0, 1))
    vg = AN._groups(ob)
    legs = [i for i, g in vg.items() if g.startswith(("thigh_", "foot_"))]
    seat = [i for i, g in vg.items() if not g.startswith(("tail", "arm_", "shoulder_"))]
    tail = [i for i, g in vg.items() if g == "tail"]
    t1 = rig.data.bones["tail_1"]
    lift_ax = (t1.tail_local - t1.head_local).normalized().cross(V((0, 0, 1))).normalized()

    def pose(rots, z):
        qs = pose_quats(rig, rots)
        for pb in rig.pose.bones:
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = qs[pb.name]
            pb.location = (0, 0, 0)
        rig.pose.bones["hips"].location = up_local * z
        bpy.context.view_layer.update()
    worst = 0.0
    fverts = _forearm_verts(rig, ob)
    pushes = {"l": V(), "r": V()}                          # carried frame to frame: smooth, no popping
    for f in range(frames + 1):
        rots, dz, support, arms = fn((f / frames) % 1.0)
        z = dz * k
        pose(rots, z)
        z -= AN._lowest(ob, legs if support == "legs" else seat)
        pose(rots, z)
        if tail and AN._lowest(ob, tail) < -0.001:
            lo, hi = 0.0, 70.0
            for _ in range(7):
                mid = (lo + hi) / 2
                pose(merge(rots, {"tail_1": [(tuple(lift_ax), mid)]}), z)
                lo, hi = (lo, mid) if AN._lowest(ob, tail) >= -0.001 else (mid, hi)
            rots = merge(rots, {"tail_1": [(tuple(lift_ax), hi)]})
            pose(rots, z)
        push = {side: pushes[side] * 0.6 for side in arms}   # last frame's push, relaxed: lets the paw drift back
        for rnd in range(10):                               # solve; if a forearm / paw is inside the body, move out
            corr = {side: V() for side in arms}
            for _ in range(4):                              # re-aim by the measured miss: exact paws on every frame
                full = dict(rots)
                for side, (grip, Ts, pole) in arms.items():
                    ar, _miss = arm_rots(rig, side, grip * ratio + push[side] + corr[side], Ts, pole)
                    full.update(ar)
                pose(full, z)
                for side, (grip, Ts, pole) in arms.items():
                    corr[side] += grip * ratio + push[side] - rig.pose.bones[f"handslot.{side}"].head
                    if corr[side].length > 0.03:            # out of reach: don't chase it; QA reports the miss
                        corr[side] = corr[side].normalized() * 0.03
            hits = arm_intrusion(rig, ob, {sd: fverts[sd] for sd in arms})
            if report is not None and rnd == 0:
                for sd, (depth, way) in hits.items():
                    if depth > 0.003:
                        report.setdefault(name + "_intrude", []).append((f, sd, round(depth, 3)))
            if NOPUSH:
                break
            moved = False
            for side, (depth, way) in hits.items():
                if depth > 0.003 and arms[side][1] is None:  # free paws only: a tool hand is never moved
                    push[side] = push[side] + way * (depth + 0.004)
                    if push[side].length > 0.035:            # a nudge, not a new pose: QA reports anything bigger
                        push[side] = push[side].normalized() * 0.035
                    moved = True
            if not moved:
                break
        if report is not None:                              # what is left after the nudges
            for sd, (depth, way) in arm_intrusion(rig, ob, {sd: fverts[sd] for sd in arms}).items():
                if depth > 0.003:
                    report.setdefault(name + "_left", []).append((f, sd, round(depth, 3)))
        pushes.update(push)
        for side, (grip, Ts, pole) in arms.items():
            if push[side].length > 0.001 and report is not None:
                report.setdefault(name + "_pushed", []).append((f, side, round(push[side].length, 4)))
            miss = (rig.pose.bones[f"handslot.{side}"].head - grip * ratio - push[side]).length
            if report is not None and miss > 0.002:
                report.setdefault(name + "_frames", []).append((f, side, round(miss, 4)))
            worst = max(worst, miss)
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=f)
        rig.pose.bones["hips"].keyframe_insert("location", frame=f)
    act_.use_frame_range = True
    act_.frame_range = (0, frames)
    act_.use_cyclic = True
    tr = rig.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act_)
    tr.mute = True
    rig.animation_data.action = None
    if report is not None:
        report[name] = worst
    return act_


# ---------------------------------------------------------------- QA helpers
def paw_faces(ob):
    """Polygons of the raccoon mesh that belong to the paws / wrists (dominant weight): they may touch the tool."""
    names = {i: g.name for i, g in enumerate(ob.vertex_groups)}
    paw_v = set()
    for v in ob.data.vertices:
        if v.groups:
            g = max(v.groups, key=lambda e: e.weight)
            if names[g.group].startswith(("hand.", "wrist.")):
                paw_v.add(v.index)
    return {p.index for p in ob.data.polygons if any(i in paw_v for i in p.vertices)}


def world_bvh(o, skip=()):
    """BVH of an object's evaluated (deformed) mesh in world space, without the polygons in `skip`."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    mw = o.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    polys = [list(p.vertices) for p in me.polygons if p.index not in skip]
    ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


def tool_hits(rig, ob, tool, action, frames):
    """Frames where the tool cuts into the raccoon's own body (paws excluded)."""
    import build_raccoon_blockout as RB
    skip = paw_faces(ob)
    grp = ob.data.attributes["grp"].data
    keep = [p.index for p in ob.data.polygons if p.index not in skip]
    rig.animation_data.action = bpy.data.actions[action]
    bad = []
    for f in range(frames + 1):
        bpy.context.scene.frame_set(f)
        pairs = visible_pairs(ob, skip, world_bvh(ob, skip).overlap(world_bvh(tool)))
        if pairs:
            parts = sorted({RB.GROUPS[grp[keep[a]].value] for a, _ in pairs})
            bad.append((f, len(pairs), parts))
    return bad


def visible_pairs(ob, paws, pairs):
    """Overlap pairs (raccoon face index among the non-paw faces, other) minus those whose raccoon face is buried
    inside the paw (the forearm tube runs into the paw blob: a handle through the fist crosses those hidden faces)."""
    from mathutils.bvhtree import BVHTree
    if not pairs:
        return pairs
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ob.matrix_world
    co = [mw @ v.co for v in me.vertices]
    keep = [p.index for p in me.polygons if p.index not in paws]
    paw_tree = BVHTree.FromPolygons(co, [list(me.polygons[i].vertices) for i in paws])
    d = V((0.3, 0.2, 0.93)).normalized()
    out = []
    for a, b in pairs:
        poly = me.polygons[keep[a]]
        c = sum((co[i] for i in poly.vertices), V()) / len(poly.vertices)
        n, o = 0, c.copy()
        for _ in range(20):
            h = paw_tree.ray_cast(o, d)
            if h[0] is None:
                break
            n += 1
            o = h[0] + d * 1e-6
        if n % 2 == 0:                                    # outside the paw: a real, visible contact
            out.append((a, b))
    ev.to_mesh_clear()
    return out
