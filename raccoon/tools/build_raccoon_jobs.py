"""Job clips: the raccoon doing a building's work, with its tool held right.

  work_chop     one-handed hatchet at the woodpile, swung out on the right: the EDGE comes down onto the log
  work_fish     sitting at the end of the pier, rod held still out over the water (the building owns line + bobber)
  work_scrub    wading ankle-deep in the washing pool's shallows, crouched, paws rubbing food in the water
  work_rummage  crouched at the junk heap, paws taking turns digging at it
  work_water    standing at a seedling row, watering can at the right hip: lifts and tips it, pours with a slow sweep
  work_tend     crouched at a low bed, the paws taking turns patting the soil round a plant (two pats each)
  work_stash    crouched at a low open crate: both paws reach in and settle the goods, come back up, rub clean
  work_pump     crouched at the smelter's bellows, both paws on its handle: two strong pumps a loop
  work_stir     standing at a cauldron, ladle in the right paw: slow circles through the brew
  work_hammer   crouched at a low bench, a small hammer in the right paw: tap, tap on the piece the left paw holds
  work_haggle   standing on a stool behind a counter: rubs its paws, taps the coins twice, wags a claw "no"
  work_drink    sitting on a cushion, a mug in the right paw: sips, rests it on the knee, laughs (patio bar)
  work_chat     sitting on a cushion, no mug: talks with its paws, slaps its knee laughing (patio bar)
  work_grind    crouched by a mortar on a stand at its right foot, grinding medicine with a pestle
  work_read     crouched over a map on a low table, paws holding it flat, the right paw tracing a route
  work_guard    on watch with a spear held upright in the right paw: scans slowly left and right, peering
  work_ring     hauling on the alarm bell's rope with both paws: two big pulls a loop
  work_mourn    standing at a grave, head bowed, paws clasped, ears and tail low
  work_sweep    crouched, sweeping the floor into a dustpan with a hand brush, the left paw holding the pan
  work_teach    THE ELDER: leaning on his cane (right paw), points at a slate with his left, turns to the class
  work_listen   A KIT: sitting on the floor listening, nods, ears up, now and then puts a paw up to ask
  work_swing    A KIT: on the tyre swing's rim, holding the ropes, pumping with its legs (the swing follows swing_angle)

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
import build_kit_blockout as KB  # noqa: E402
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
    w_pole = 0.05 if pole is None else 0.5             # an explicit pole steers a tool arm's elbow harder
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
                score = abs(fore.dot(hd)) + w_pole * (1 - math.cos(ph))
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


def leg_rots(rig, side, ankle, pole, toe_dir):
    """Rotations that put the ankle (foot.<side>'s head) at `ankle` (armature space), the knee bending toward `pole`,
    the foot pointing along `toe_dir`. The rig must already be posed for the body. Returns (rots, reach_miss)."""
    sd = side
    _, hu, tu = _rest(rig, f"upperleg.{sd}")
    _, hl, tl = _rest(rig, f"lowerleg.{sd}")
    a, b = (tu - hu).length, (tl - hl).length
    S = rig.pose.bones[f"upperleg.{sd}"].head.copy()
    d = ankle - S
    L = d.length
    di = d.normalized()
    Lc = min(max(L, abs(a - b) + 1e-4), a + b - 1e-4)
    x = (a * a - b * b + Lc * Lc) / (2 * Lc)
    h = math.sqrt(max(a * a - x * x, 0.0))
    pv = V(pole) - di * V(pole).dot(di)
    pv = pv.normalized() if pv.length > 1e-6 else -FWD
    E = S + di * x + pv * h
    W = S + di * Lc
    rots = {f"upperleg.{sd}": [("AIM", tuple(E - S))], f"lowerleg.{sd}": [("AIM", tuple(W - E))],
            f"foot.{sd}": [("AIM", tuple(toe_dir))]}
    return rots, (ankle - W).length


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


WATER_GRIP = loc(f=0.058, u=0.118, l=-0.128)            # the can at rest: carried by its top handle at the right hip
WATER_POUR = loc(f=0.085, u=0.15, l=-0.114)            # pouring: lifted out front on the right
WATER_TILT = 34.0                                    # degrees the can tips forward to pour (the spout then points down)
WATER_SWEEP = 0.016                                  # side to side along the row while pouring (m)


def water_can(a):
    """Watering can frame (hand slot) tipped forward by a degrees: handle level and pointing ahead, can below."""
    th = math.radians(a)
    y = FWD * math.cos(th) - UP * math.sin(th)
    z = UP * math.cos(th) + FWD * math.sin(th)
    return frame_yz(y, z)


def water_phase(p):
    """(tilt 0..1, sweep offset along l) of the can at loop phase p; shared with the farm (its water stream)."""
    if p < 0.18:
        t = smooth(p / 0.18)
    elif p < 0.72:
        t = 1.0
    elif p < 0.88:
        t = 1 - smooth((p - 0.72) / 0.16)
    else:
        t = 0.0
    sweep = WATER_SWEEP * math.sin(TAU * (p - 0.18) / 0.54) if 0.18 <= p < 0.72 else 0.0
    return t, sweep


def water(p):
    """Standing at the end of a seedling row, the can carried by its top handle at the right hip. Lift it out front
    and tip it, pour while sweeping slowly along the row, tip it back and lower it, a moment's rest. The left paw
    hangs loose for balance."""
    t, sweep = water_phase(p)
    Ts = water_can(WATER_TILT * t)
    grip = WATER_GRIP.lerp(WATER_POUR, t) + loc(l=sweep - 0.008 * t - 0.012 * math.sin(math.pi * t))   # out past the thigh
    breath = AN.s(p, 2)
    rots = act({
        "upperleg.l": [(Y, -8), (X, -12)], "upperleg.r": [(Y, 8), (X, -4)],               # easy stance, left foot ahead
        "lowerleg.l": [(X, 16)], "lowerleg.r": [(X, 8)], "foot.l": [(X, -4)], "foot.r": [(X, -4)],
        "spine": [(X, 6 + 6 * t + breath)], "chest": [(X, 3 + 4 * t)],
        "head": [(X, 4 + 4 * t), (Z, 6 - 120 * sweep)],                              # watching the water land
        "ear.l": [(Y, 8)], "ear.r": [(Y, -8)],
    }, tail_sway(p, 6, 1))
    bal = loc(f=0.04, u=0.12, l=0.1)
    arms = {"r": (grip, Ts, None), "l": (bal, None, LEFT * 1.0 - UP * 0.4 + V((0, 0.3, 0)))}
    return rots, -0.004 * t, "legs", arms


TEND_C = loc(f=0.104, u=0.05)                         # the plant being tended: the paws pat the soil either side of it
TEND_PATS = (0.3, 0.6)                                # when (in each paw's half of the loop) a pat lands


def tend(p):
    """Crouched at a low bed; the right paw pats the soil round the plant twice, then the left; the resting paw
    hovers by the knee. The building wiggles the plant on each pat (see tend_pats)."""
    def paw(side, ph):
        t = (p - ph) % 1.0 * 2                                           # 0..1 in this paw's half, >1 resting
        spot = TEND_C + loc(l=0.034 * (1 if side == "l" else -1))
        home = loc(f=0.088, u=0.085, l=0.042 * (1 if side == "l" else -1))
        if t >= 1:
            return home
        out = ramp(t, 0.0, 0.18) * (1 - ramp(t, 0.78, 1.0))
        lift = 0.022 * (1 - max(math.exp(-((t - c) ** 2) / 0.003) for c in TEND_PATS))
        return home.lerp(spot + loc(u=lift), out)
    pr, pl = paw("r", 0.0), paw("l", 0.5)
    side = math.sin(TAU * p)                                               # leans toward the busy paw
    rots = act({
        "upperleg.l": [(Y, -18), (X, -70)], "upperleg.r": [(Y, 18), (X, -70)],             # deep crouch, knees apart
        "lowerleg.l": [(X, 96)], "lowerleg.r": [(X, 96)], "foot.l": [(X, -26)], "foot.r": [(X, -26)],
        "spine": [(X, 28)], "chest": [(X, 14), (Z, 4 * side)], "head": [(X, -12), (Z, 8 * side)],
        "ear.l": [(Y, 10 + 4 * side)], "ear.r": [(Y, -10 + 4 * side)],
        "tail_1": [(X, -30)],
    }, tail_sway(p, 6, 1))
    return rots, 0.0, "legs", {"r": (pr, None, None), "l": (pl, None, None)}


def tend_pats():
    """Loop phases where a paw pats the soil (the building's plant wiggles then)."""
    return sorted(((ph + c / 2) % 1.0) for ph in (0.0, 0.5) for c in TEND_PATS)


STASH_C = loc(f=0.124, u=0.09)                       # top of the goods in the crate: both paws settle them here


def stash(p):
    """Crouched at a low open crate: both paws reach in together and settle the goods (a little shove each), come
    back up over the rim and rub each other clean, then rest a beat."""
    reach = ramp(p, 0.04, 0.24) * (1 - ramp(p, 0.52, 0.68))
    shove = sum(math.exp(-((p - c) ** 2) / 0.0016) for c in (0.3, 0.42))
    rub = ramp(p, 0.66, 0.72) * (1 - ramp(p, 0.9, 0.96))
    a = TAU * p * 6
    out = {}
    for sd, sgn in (("l", 1), ("r", -1)):
        home = loc(f=0.135, u=0.112, l=0.032 * sgn)
        rubbing = loc(f=0.135 + 0.005 * math.cos(a) * sgn, u=0.108 + 0.005 * math.sin(a), l=0.024 * sgn)
        spot = STASH_C + loc(l=0.032 * sgn, f=0.008 * shove * (1 if (sd == "r") == (p < 0.36) else 0), u=-0.008 * shove)
        out[sd] = (home.lerp(rubbing, rub).lerp(spot, reach), None, None)
    rots = act({
        "upperleg.l": [(Y, -16), (X, -62 - 8 * reach)], "upperleg.r": [(Y, 16), (X, -62 - 8 * reach)],   # crouched low
        "lowerleg.l": [(X, 86 + 10 * reach)], "lowerleg.r": [(X, 86 + 10 * reach)],
        "foot.l": [(X, -24 - 2 * reach)], "foot.r": [(X, -24 - 2 * reach)],
        "tail_1": [(X, -25)],
        "spine": [(X, 28 + 4 * reach)], "chest": [(X, 15 + 3 * reach)], "head": [(X, -6 - 8 * reach + 10 * rub)],
        "ear.l": [(Y, 10)], "ear.r": [(Y, -10)],
    }, tail_sway(p, 7, 1, 0.1))
    return rots, 0.0, "legs", out


PUMP = loc(f=0.122, u=0.098)                          # the bellows handle (a bar across), raised; both paws on it
PUMP_DEPTH = 0.026                                   # how far a pump presses it down


def pump_press(p):
    """0 (handle up) .. 1 (pressed down): two pumps a loop, a firm press and an easier rise. Shared with the smelter."""
    u = (2 * p) % 1.0
    return smooth(u / 0.35) if u < 0.35 else 1 - smooth((u - 0.35) / 0.65)


def pump(p):
    """Crouched at the bellows, leaning in: both paws on the handle push it down, let it rise, twice a loop."""
    d = pump_press(p)
    bar = PUMP + loc(u=-PUMP_DEPTH * d)
    rots = act({
        "upperleg.l": [(Y, -16), (X, -62)], "upperleg.r": [(Y, 16), (X, -62)],
        "lowerleg.l": [(X, 86)], "lowerleg.r": [(X, 86)], "foot.l": [(X, -24)], "foot.r": [(X, -24)],
        "spine": [(X, 26 + 6 * d)], "chest": [(X, 14 + 4 * d)], "head": [(X, -10 - 4 * d), (Z, 6)],
        "ear.l": [(Y, 10 - 8 * d)], "ear.r": [(Y, -10 + 8 * d)],
        "tail_1": [(X, -25)],
    }, tail_sway(p, 5, 2))
    return rots, -0.004 * d, "legs", {"r": (bar + loc(l=-0.03), None, None), "l": (bar + loc(l=0.03), None, None)}


STIR_C = loc(f=0.11, u=0.162, l=-0.07)               # middle of the circle the ladle's grip makes
POT_C = loc(f=0.2, u=0.062, l=-0.02)                         # where the ladle's bowl circles, in the brew
STIR_R = (0.012, 0.03)                                # radius of the grip's circle, of the bowl's circle


def stir(p):
    """Standing at the cauldron, ladle in the right paw: two slow circles a loop through the brew; the left paw rests
    on the hip; the head follows the ladle."""
    a = TAU * 2 * p
    ca, sa = math.cos(a), math.sin(a)
    grip = STIR_C + loc(f=STIR_R[0] * ca, l=STIR_R[0] * sa)
    bowl = POT_C + loc(f=STIR_R[1] * ca, l=STIR_R[1] * sa)
    Ts = frame_yz(bowl - grip, FWD - UP)
    rots = act({
        "upperleg.l": [(Y, -8), (X, -8)], "upperleg.r": [(Y, 8), (X, -8)],
        "lowerleg.l": [(X, 12)], "lowerleg.r": [(X, 12)], "foot.l": [(X, -4)], "foot.r": [(X, -4)],
        "spine": [(X, 10 + 1.5 * ca)], "chest": [(X, 6), (Z, -3 * sa)], "head": [(X, 16), (Z, -6 * sa)],
        "ear.l": [(Y, 6)], "ear.r": [(Y, -6)],
    }, tail_sway(p, 6, 1))
    arms = {"r": (grip, Ts, None), "l": (loc(f=0.05, u=0.12, l=0.1), None, LEFT * 1.0 - UP * 0.4 + V((0, 0.3, 0)))}
    return rots, 0.0, "legs", arms


HAM_X = -0.085                                        # the hammer swings in this plane: out on the right, clear of the snout
HAM_HIT = loc(f=0.162, u=0.084, l=HAM_X)              # where its face meets the piece on the anvil (past the toes)
HAM_KEYS = [(0.0, -34, None), (1.0, -8, loc(f=0.1, u=0.17, l=HAM_X - 0.016))]   # a short, wristy lift


def _hammer_at(t):
    """Hammer frame and grip for t: 0 = face on the piece, 1 = raised."""
    deg = HAM_KEYS[0][1] + (HAM_KEYS[1][1] - HAM_KEYS[0][1]) * t
    Tm = _sagittal(deg)                                 # face (+X) points the way a downward swing travels
    g0 = HAM_HIT - _sagittal(HAM_KEYS[0][1]) @ T.HAMMER_FACE
    return Tm, g0.lerp(HAM_KEYS[1][2], smooth(t))


def hammer(p):
    """Crouched at a low bench; quick light taps (two a loop, on frames 0 and 16), the left paw holding the piece."""
    q = (2 * p) % 1.0
    if q < 0.12:
        t = 0.06 * math.sin(math.pi * q / 0.12)
    elif q < 0.6:
        t = smooth((q - 0.12) / 0.48)
    elif q < 0.78:
        t = 1.0
    else:
        u = (q - 0.78) / 0.22
        t = 1 - u * u
    Ts, grip = _hammer_at(t)
    hit = math.exp(-((q if q < 0.5 else q - 1) ** 2) / 0.003)
    rots = act({
        "upperleg.l": [(Y, -16), (X, -62)], "upperleg.r": [(Y, 16), (X, -62)],
        "lowerleg.l": [(X, 86)], "lowerleg.r": [(X, 86)], "foot.l": [(X, -24)], "foot.r": [(X, -24)],
        "spine": [(X, 26 + 2 * hit)], "chest": [(X, 14), (Z, -4 * t)], "head": [(X, -8 + 3 * hit), (Z, 4)],
        "ear.l": [(Y, 10 - 10 * hit)], "ear.r": [(Y, -10 + 10 * hit)],
        "tail_1": [(X, -25)],
    }, tail_sway(p, 5, 1))
    arms = {"r": (grip, Ts, None), "l": (loc(f=0.135, u=0.096, l=0.015), None, None)}   # holds the near end of the piece
    return rots, 0.0, "legs", arms


HAGGLE_TAPS = (0.36, 0.46)                           # when the right paw taps the coins on the counter
HAGGLE_TAP = loc(f=0.124, u=0.1, l=-0.035)           # the coins, on the counter top


def haggle(p):
    """Standing on the stool behind the counter: rubs its paws together (scheming), leans in and taps the coins twice,
    straightens and wags a claw: no, not enough. Back to rubbing."""
    a = TAU * 5 * p
    rub_r = loc(f=0.1 + 0.005 * math.cos(a), u=0.152 + 0.004 * math.sin(a), l=-0.02)
    rub_l = loc(f=0.1 - 0.005 * math.cos(a), u=0.152 - 0.004 * math.sin(a), l=0.02)
    lean = ramp(p, 0.26, 0.34) * (1 - ramp(p, 0.5, 0.58))
    tap = sum(math.exp(-((p - c) ** 2) / 0.0006) for c in HAGGLE_TAPS)
    wag = ramp(p, 0.56, 0.64) * (1 - ramp(p, 0.84, 0.92))
    over = HAGGLE_TAP + loc(u=0.022 * (1 - tap))
    up = loc(f=0.075, u=0.205, l=-0.075 + 0.012 * math.sin(TAU * 6 * p) * wag)
    pr = rub_r.lerp(over, lean).lerp(up, wag)
    pl = rub_l.lerp(loc(f=0.1, u=0.125, l=0.045), lean)
    rots = act({
        "upperleg.l": [(Y, -6), (X, -6)], "upperleg.r": [(Y, 6), (X, -6)],
        "lowerleg.l": [(X, 10)], "lowerleg.r": [(X, 10)], "foot.l": [(X, -4)], "foot.r": [(X, -4)],
        "spine": [(X, 6 + 20 * lean)], "chest": [(X, 3 + 8 * lean)],
        "head": [(X, 4 + 10 * lean), (Z, 9 * math.sin(TAU * 3 * p) * wag)],
        "ear.l": [(Y, 14 - 10 * wag)], "ear.r": [(Y, -14 + 10 * wag)],
    }, tail_sway(p, 8, 1))
    return rots, 0.0, "legs", {"r": (pr, None, None), "l": (pl, None, None)}


SEAT_LEGS = {"upperleg.l": [(Y, -30), (X, -72)], "upperleg.r": [(Y, 30), (X, -72)],      # sitting, legs out in front
             "lowerleg.l": [(X, 40)], "lowerleg.r": [(X, 40)], "foot.l": [(X, 10)], "foot.r": [(X, 10)]}
KNEE_L, KNEE_R = loc(f=0.09, u=0.085, l=0.038), loc(f=0.09, u=0.085, l=-0.038)
DRINK_REST = loc(f=0.08, u=0.12, l=-0.07)               # the mug resting on top of the right knee (grip)
SIP_RIM = loc(f=0.112, u=0.148, l=-0.034)             # the mug's rim at a sip: just under the chin
SIP_TILT = 15.0


def mug_frame(tilt):
    """Mug held by its handle, body ahead of the paw, tipped toward the mouth by `tilt` degrees."""
    th = math.radians(tilt)
    y = UP * math.cos(th) - FWD * math.sin(th)
    x = FWD * math.cos(th) + UP * math.sin(th)
    return frame_yx(y, x)


def _sip_grip():
    Tm = mug_frame(SIP_TILT)
    return SIP_RIM - Tm @ (T.MUG_C + V((0, T.MUG_H / 2, 0)))


DRINK_SIP = _sip_grip()

def drink(p):
    """Sitting at the patio bar: a long sip, the mug down on the knee, a chat and a laugh (the free paw gestures),
    another sip. 96 frames."""
    sip = ramp(p, 0.04, 0.14) * (1 - ramp(p, 0.3, 0.4)) + ramp(p, 0.68, 0.78) * (1 - ramp(p, 0.9, 0.98))
    laugh = ramp(p, 0.45, 0.5) * (1 - ramp(p, 0.58, 0.64))
    shake = laugh * math.sin(TAU * 10 * p)
    grip = DRINK_REST.lerp(DRINK_SIP, sip)
    Ts = mug_frame(SIP_TILT * sip)
    gest = ramp(p, 0.4, 0.46) * (1 - ramp(p, 0.6, 0.66))
    pl = KNEE_L.lerp(loc(f=0.1, u=0.16, l=0.085) + loc(u=0.01 * shake), gest)
    rots = act(SEAT_LEGS, {
        "spine": [(X, 4 - 5 * laugh)], "chest": [(X, 3 - 4 * laugh)],
        "head": [(X, 8 - 4 * sip - 14 * laugh + 3 * shake), (Z, 6 * math.sin(TAU * p) * (1 - sip))],
        "ear.l": [(Y, 14 + 10 * laugh)], "ear.r": [(Y, -14 - 10 * laugh)],
        "tail_1": [(X, -40)], "tail_2": [(X, -15)],
    }, tail_sway(p, 7, 2, 0.12))
    return rots, -0.05, "seat", {"r": (grip, Ts, None), "l": (pl, None, None)}


def chat(p):
    """Sitting at the patio bar without a mug: talks with its paws (one, then the other, then both: 'and THEN...'),
    a big laugh with a slap of the knee. 96 frames."""
    a = ramp(p, 0.05, 0.12) * (1 - ramp(p, 0.26, 0.32))
    b = ramp(p, 0.3, 0.36) * (1 - ramp(p, 0.5, 0.56))
    both = ramp(p, 0.55, 0.6) * (1 - ramp(p, 0.68, 0.72))
    laugh = ramp(p, 0.74, 0.78) * (1 - ramp(p, 0.92, 0.98))
    slap = sum(math.exp(-((p - c) ** 2) / 0.0004) for c in (0.8, 0.86))
    wob = 0.008 * math.sin(TAU * 6 * p)
    pr = KNEE_R.lerp(loc(f=0.11, u=0.165 + wob, l=-0.075), max(a, both)) + loc(u=0.03 * (1 - slap) * laugh)
    pl = KNEE_L.lerp(loc(f=0.11, u=0.165 - wob, l=0.075), max(b, both))
    rots = act(SEAT_LEGS, {
        "spine": [(X, 6 - 10 * laugh)], "chest": [(X, 4 - 6 * laugh), (Z, 6 * (a - b))],
        "head": [(X, 6 - 16 * laugh + 4 * slap), (Z, 10 * (a - b) + 4 * math.sin(TAU * 2 * p))],
        "ear.l": [(Y, 14 + 8 * laugh)], "ear.r": [(Y, -14 - 8 * laugh)],
        "tail_1": [(X, -40)], "tail_2": [(X, -15)],
    }, tail_sway(p, 8, 2, 0.12))
    return rots, -0.05, "seat", {"r": (pr, None, None), "l": (pl, None, None)}


MORTAR_C = loc(f=0.124, u=0.074, l=-0.098)             # the bottom of the mortar bowl: on a stone stand by the right foot
GRIND_R = 0.012


def grind(p):
    """Crouched by a mortar on a little stand beside its right foot: the pestle grinds round it (two turns a loop), the
    left paw on the knee."""
    a = TAU * 2 * p
    tip = MORTAR_C + loc(f=GRIND_R * math.cos(a), l=GRIND_R * math.sin(a))
    up = (UP * 1.0 - FWD * 0.15 - LEFT * 0.25).normalized()              # handle leans back and out, off the face
    grip = tip + up * T.PESTLE_TIP.y
    Ts = frame_yz(tip - grip, FWD)
    rots = act({
        "upperleg.l": [(Y, -16), (X, -62)], "upperleg.r": [(Y, 16), (X, -62)],
        "lowerleg.l": [(X, 86)], "lowerleg.r": [(X, 86)], "foot.l": [(X, -24)], "foot.r": [(X, -24)],
        "spine": [(X, 32), (Y, 6)], "chest": [(X, 14), (Z, -3 * math.sin(a))], "head": [(X, -10), (Z, 4 * math.sin(a))],
        "ear.l": [(Y, 10)], "ear.r": [(Y, -10)],
        "tail_1": [(X, -25)],
    }, tail_sway(p, 5, 1))
    return rots, 0.0, "legs", {"r": (grip, Ts, -LEFT * 1.0 - UP * 0.2), "l": (loc(f=0.085, u=0.11, l=0.055), None, None)}


READ_C = loc(f=0.112, u=0.094)                         # the map, on a low table


def read(p):
    """Crouched over a map: the left paw holds it flat, the right paw traces a route out and back; the head follows,
    a pause to think (ear flick)."""
    t = ramp(p, 0.05, 0.4) * (1 - ramp(p, 0.6, 0.95))
    route = [loc(l=-0.05, f=0.0), loc(l=-0.035, f=0.018), loc(l=-0.018, f=0.006), loc(l=-0.006, f=0.02)]
    k = t * (len(route) - 1)
    i = min(int(k), len(route) - 2)
    pr = READ_C + route[i].lerp(route[i + 1], k - i)
    think = ramp(p, 0.42, 0.47) * (1 - ramp(p, 0.55, 0.6))
    rots = act({
        "upperleg.l": [(Y, -16), (X, -62)], "upperleg.r": [(Y, 16), (X, -62)],
        "lowerleg.l": [(X, 86)], "lowerleg.r": [(X, 86)], "foot.l": [(X, -24)], "foot.r": [(X, -24)],
        "spine": [(X, 26)], "chest": [(X, 14)], "head": [(X, -4 + 6 * think), (Z, -10 + 30 * t)],
        "ear.l": [(Y, 12 - 16 * think)], "ear.r": [(Y, -12)],
        "tail_1": [(X, -25)],
    }, tail_sway(p, 5, 1))
    return rots, 0.0, "legs", {"r": (pr + loc(u=0.004 * (1 - think)), None, None),
                               "l": (READ_C + loc(l=0.045, f=0.0), None, None)}


TEACH_BOARD = loc(f=0.07, u=0.2, l=0.135)              # where the elder's claw taps the slate (to his left)


def teach(p):
    """The elder, leaning on his cane (right paw, left as it hangs): turns to the slate on his left and points at it,
    taps it twice, turns back to the class with an open paw, a wagging claw for emphasis. 96 frames."""
    board = ramp(p, 0.04, 0.14) * (1 - ramp(p, 0.42, 0.5))
    taps = sum(math.exp(-((p - c) ** 2) / 0.0005) for c in (0.24, 0.31))
    talk = ramp(p, 0.5, 0.58) * (1 - ramp(p, 0.9, 0.98))
    home = loc(f=0.06, u=0.105, l=0.085)
    point = TEACH_BOARD + loc(l=-0.02 * (1 - taps), f=-0.012 * (1 - taps))
    open_ = loc(f=0.11, u=0.17, l=0.06) + loc(l=0.01 * math.sin(TAU * 5 * p) * talk)
    pl = home.lerp(point, board).lerp(open_, talk)
    rots = act({                                       # legs as in his idle: the cane was fitted to that stance
        "chest": [(Z, 14 * board)], "head": [(Z, 22 * board - 10 * talk), (X, -6 * board + 4 * taps)],
        "upperarm.r": [(Y, 5)],                         # the cane arm a touch out from the side, as in his idle
        "ear.l": [(Y, 10 + 8 * talk)], "ear.r": [(Y, -10 - 8 * talk)],
    }, tail_sway(p, 5, 1))
    return rots, 0.0, "legs", {"l": (pl, None, None)}


def listen(p):
    """A kit sitting on the floor, listening: paws on its knees, slow nods, ears up; halfway through it shoots a paw
    up to ask a question, then settles. 96 frames."""
    nod = math.sin(TAU * 3 * p) * (1 - ramp(p, 0.5, 0.55)) * 1.0
    ask = ramp(p, 0.55, 0.6) * (1 - ramp(p, 0.76, 0.82))
    wave = 0.008 * math.sin(TAU * 8 * p) * ask
    pr = KNEE_R.lerp(loc(f=0.05, u=0.29, l=-0.11 + wave), ask)
    rots = act(SEAT_LEGS, {
        "spine": [(X, 2 - 4 * ask)], "chest": [(X, 2 - 3 * ask), (Z, -5 * ask)],
        "head": [(X, -6 + 5 * nod - 6 * ask), (Z, 5 * math.sin(TAU * p))],
        "ear.l": [(Y, 22)], "ear.r": [(Y, -22)],
        "tail_1": [(X, -40)], "tail_2": [(X, -15)],
    }, tail_sway(p, 6, 1, 0.12))
    return rots, -0.05, "seat", {"r": (pr, None, None), "l": (KNEE_L, None, None)}


GUARD_GRIP = loc(f=0.058, u=0.135, l=-0.118)          # the spear upright beside the right leg (its butt near the floor)


def guard(p):
    """On watch, spear upright in the right paw: the head turns slowly to one side and the other, a pause to peer at
    each end; ears swivel; the left paw hangs easy. 96 frames."""
    scan = math.sin(TAU * p)
    shade = ramp(p, 0.15, 0.22) * (1 - ramp(p, 0.36, 0.43))            # a long peer at the far left
    Ts = frame_yz((UP - LEFT * 0.1 + FWD * 0.08).normalized(), FWD * -1)   # the shaft leans a touch out, clear of the forearm
    pl = loc(f=0.05, u=0.11, l=0.095)
    rots = act({
        "spine": [(X, -2)], "chest": [(Z, 5 * scan)],
        "head": [(Z, 26 * scan), (X, -4 + 6 * shade)],
        "ear.l": [(Y, 18 + 8 * scan)], "ear.r": [(Y, -18 + 8 * scan)],
        "upperleg.l": [(Y, -4)], "upperleg.r": [(Y, 4)],
    }, tail_sway(p, 6, 1))
    return rots, 0.0, "legs", {"r": (GUARD_GRIP, Ts, -LEFT * 1.0 + V((0, 0.4, 0))), "l": (pl, None, LEFT * 1.0 - UP * 0.4 + V((0, 0.3, 0)))}


ROPE = loc(f=0.112, l=0.0)                             # where the bell rope hangs in front of the ringer (u = 0)
RING_TOP, RING_PULL = 0.225, 0.07                      # the upper paw's height before a pull, how far a pull brings it down


def ring_pull(p):
    """0 (paws up) .. 1 (rope hauled down): two big pulls a loop, a hard haul and a quicker rise."""
    u = (2 * p) % 1.0
    return smooth(u / 0.4) if u < 0.4 else 1 - smooth((u - 0.4) / 0.6)


def ring(p):
    """Hauling on the alarm bell's rope with both paws, one above the other: down hard, let it lift them, again.
    The building's rope and bell follow ring_pull."""
    d = ring_pull(p)
    top = ROPE + loc(u=RING_TOP - RING_PULL * d)
    rots = act({
        "upperleg.l": [(Y, -8), (X, -10 - 28 * d)], "upperleg.r": [(Y, 8), (X, -10 - 28 * d)],
        "lowerleg.l": [(X, 16 + 46 * d)], "lowerleg.r": [(X, 16 + 46 * d)],
        "foot.l": [(X, -6 - 18 * d)], "foot.r": [(X, -6 - 18 * d)],
        "spine": [(X, 2 + 14 * d)], "chest": [(X, 2 + 4 * d)], "head": [(X, -14 + 8 * d)],
        "ear.l": [(Y, 4 - 20 * d)], "ear.r": [(Y, -4 + 20 * d)],
    }, tail_sway(p, 8, 2))
    return rots, 0.0, "legs", {"r": (top + loc(l=-0.006), None, None), "l": (top + loc(u=-0.028, l=0.004), None, None)}


def mourn(p):
    """Standing at a grave: head bowed, paws clasped in front, ears and tail low; slow breaths, a little sniffle."""
    breath = AN.s(p, 1)
    sniff = math.exp(-((p - 0.55) ** 2) / 0.002)
    clasp = loc(f=0.106, u=0.148, l=0.0)
    rots = act({
        "spine": [(X, 6 + 1.5 * breath)], "chest": [(X, 4 + 1.5 * breath + 3 * sniff)],
        "head": [(X, 13 + 3 * sniff), (Z, 3 * breath)],
        "ear.l": [(Y, 40)], "ear.r": [(Y, -40)],
        "tail_1": [(X, -30)], "tail_2": [(X, -12)],
    }, tail_sway(p, 3, 1))
    return rots, 0.0, "legs", {"r": (clasp + loc(l=-0.013, u=0.003 * sniff), None, None),
                               "l": (clasp + loc(l=0.013, u=0.003 * sniff), None, None)}


SWEEP_C = loc(f=0.17, u=0.018, l=-0.045)               # the middle of the brush's sweep: the bristle block, on the floor
PAN = loc(f=0.13, l=0.055)                             # the dustpan, on the floor at its left


def sweep(p):
    """Crouched, sweeping toward the dustpan: two strokes a loop (brush across, lift back), the left paw on the
    pan's handle."""
    u = (2 * p) % 1.0
    k = smooth(u / 0.55) if u < 0.55 else 1 - smooth((u - 0.55) / 0.45)
    lift = 0.0 if u < 0.55 else 0.018 * math.sin(math.pi * (u - 0.55) / 0.45)
    bristle = SWEEP_C + loc(l=-0.035 + 0.065 * k, u=lift)
    yd = (FWD * 0.8 - UP * 0.45 + LEFT * 0.35).normalized()             # the handle points from the paw down to the brush
    Ts = frame_yx(yd, UP)                                                # +X up: the bristles (-X) face the floor
    grip = bristle - Ts @ T.BRUSH_C
    rots = act({
        "upperleg.l": [(Y, -18), (X, -70)], "upperleg.r": [(Y, 18), (X, -70)],
        "lowerleg.l": [(X, 96)], "lowerleg.r": [(X, 96)], "foot.l": [(X, -26)], "foot.r": [(X, -26)],
        "spine": [(X, 30)], "chest": [(X, 16), (Z, 5 * (k - 0.5))], "head": [(X, -14), (Z, 8 * (k - 0.5))],
        "ear.l": [(Y, 10)], "ear.r": [(Y, -10)],
        "tail_1": [(X, -30)],
    }, tail_sway(p, 6, 2))
    return rots, 0.0, "legs", {"r": (grip, Ts, -LEFT * 1.0 - FWD * 0.3 + UP * 0.3), "l": (PAN + loc(f=-0.03, u=0.06), None, None)}


SWING_GRIP = loc(f=0.03, u=0.2, l=0.117)               # the kit's paws on the swing's side ropes (adult metres, scaled to
                                                       # the kit when baked); l is mirrored for the right paw


def swing_angle(p):
    """The tyre swing's swing, in degrees forward (the building's work follows this): one swing a loop."""
    return 10.0 * math.sin(TAU * p)


def swing(p):
    """A KIT on the tyre swing, sitting on its back rim, holding the two side ropes: it pumps, legs kicked out going
    forward and tucked going back, leaning back with its head up at the top of each swing; ears blown back. 48 frames."""
    ext = (1 + math.sin(TAU * p + 0.7)) / 2                              # legs out as it swings forward
    joy = max(0.0, math.sin(TAU * p)) ** 2
    rots = act({
        "upperleg.l": [(Y, -28), (X, -64 - 10 * ext)], "upperleg.r": [(Y, 28), (X, -64 - 10 * ext)],
        "lowerleg.l": [(X, 75 - 65 * ext)], "lowerleg.r": [(X, 75 - 65 * ext)],
        "foot.l": [(X, 10 - 20 * ext)], "foot.r": [(X, 10 - 20 * ext)],
        "spine": [(X, 4 - 12 * ext)], "chest": [(X, 2 - 6 * ext)],
        "head": [(X, -4 - 12 * joy), (Z, 4 * math.sin(TAU * 2 * p))],
        "ear.l": [(Y, 30 + 15 * ext)], "ear.r": [(Y, -30 - 15 * ext)],
        "tail_1": [(X, -20)], "tail_2": [(X, -10 + 10 * math.sin(TAU * p))],
    }, tail_sway(p, 6, 2, 0.12))
    g = SWING_GRIP
    return rots, -0.05, "seat", {"r": (V((-g.x, g.y, g.z)), None, None), "l": (g, None, None)}


ELBOW_OUT_R = -LEFT * 1.0 - UP * 0.5 + FWD * 0.1        # IK poles: elbows out to the side, clear of the chest
ELBOW_OUT_L = LEFT * 1.0 - UP * 0.5 + FWD * 0.1
LOCK_C = loc(f=0.19, u=0.17, l=-0.02)                  # the practice padlock's keyhole (the pick's tip goes in)
LOCK_POP = 0.62                                        # when the lock springs open (the building pops its shackle)


def picklock(p):
    """At the practice yard's lock board: ear to the lock, the left paw steadying it, the right working a pick in
    the keyhole -- tiny jiggles and twists, a pause to listen, then the lock springs (LOCK_POP) and a pleased
    straighten-up; it snaps the lock shut again for another go. 48 frames."""
    work = 1 - ramp(p, LOCK_POP - 0.04, LOCK_POP) * (1 - ramp(p, 0.9, 0.97))
    jig = work * (0.003 * math.sin(TAU * 9 * p) + 0.002 * math.sin(TAU * 13 * p + 1))
    twist = work * 25 * math.sin(TAU * 6 * p)
    pleased = ramp(p, LOCK_POP, LOCK_POP + 0.06) * (1 - ramp(p, 0.86, 0.94))
    tip = LOCK_C + loc(u=jig, f=-0.004 * (1 - work))
    d = (FWD * 0.9 + LEFT * 0.4).normalized()                         # the pick comes in from the right paw's side
    Ts = Quaternion(d, math.radians(twist)).to_matrix() @ frame_yz(d, UP)
    grip = tip - Ts @ T.PICK_TIP
    rots = act({
        "upperleg.l": [(Y, -6), (X, -14)], "upperleg.r": [(Y, 6), (X, -14)], "lowerleg.l": [(X, 22)], "lowerleg.r": [(X, 22)],
        "foot.l": [(X, -8)], "foot.r": [(X, -8)],
        "spine": [(X, 10 - 6 * pleased)], "chest": [(X, 4)],
        "head": [(Z, 18 * (1 - pleased)), (Y, -10 * (1 - pleased)), (X, 6 - 10 * pleased)],    # ear to the lock
        "ear.l": [(Y, 30)], "ear.r": [(Y, -10 - 20 * pleased)],
    }, tail_sway(p, 6 + 6 * pleased, 2))
    return rots, 0.0, "legs", {"r": (grip, Ts, ELBOW_OUT_R), "l": (loc(f=0.09, u=0.145, l=0.085), None, ELBOW_OUT_L)}


PURSE_HOOK = loc(f=0.1, u=0.16, l=-0.115)              # where the practice purse hangs on the dummy's belt (right of centre)
COAT_PAW = loc(f=0.11, u=0.15, l=0.06)                 # the left paw steadies the dummy's coat here


def lift_purse(p):
    """The purse's offset from its hook as the thief lifts it (both the clip and the building follow this)."""
    up = ramp(p, 0.22, 0.34) * (1 - ramp(p, 0.62, 0.74))
    out = ramp(p, 0.3, 0.42) * (1 - ramp(p, 0.56, 0.66))
    return loc(u=0.04 * up, l=-0.02 * out, f=-0.02 * out)


def lift(p):
    """Pickpocket practice at the straw dummy: the left paw flat on its coat to steady it, the right paw takes the
    purse off its hook, lifts it out to the side, a quick look round, then hangs it back and eases off. 48 frames."""
    hold = ramp(p, 0.1, 0.2) * (1 - ramp(p, 0.8, 0.9))
    look = math.exp(-((p - 0.47) ** 2) / 0.003) - math.exp(-((p - 0.53) ** 2) / 0.003)
    rest_r = loc(f=0.055, u=0.101, l=-0.086)                        # where the hanging paw is (not solved at rest)
    purse_top = PURSE_HOOK + lift_purse(p) + loc(u=-0.012)               # the paw pinches the purse's neck
    pr = rest_r.lerp(purse_top, hold) + loc(f=0.02 * math.sin(math.pi * hold))
    steady = ramp(p, 0.04, 0.12) * (1 - ramp(p, 0.9, 0.98))
    pl = loc(f=0.1, u=0.12, l=0.08).lerp(COAT_PAW, steady)
    rots = act({
        "upperleg.l": [(Y, -4)], "upperleg.r": [(Y, 4)],
        "spine": [(X, 2)], "head": [(Z, 35 * look), (X, -4)],
        "ear.l": [(Y, 34)], "ear.r": [(Y, -34)],
        "tail_1": [(X, -20)],
    }, tail_sway(p, 4, 1))
    hang_pole = -UP * 1.0 - LEFT * 0.15 + FWD * 0.15                  # the hanging arm's elbow: straight below
    pole = hang_pole.lerp(-LEFT * 1.0 + V((0, 0.4, 0)), hold)
    arms = {"l": (pl, None, ELBOW_OUT_L)}
    if hold > 0.0:                                                     # at rest the right arm just hangs
        arms["r"] = (pr, None, pole)
    return rots, 0.0, "legs", arms


SPAR_GAP = 0.48                                        # between the two sparring partners' spots


GUARD_GRIP, GUARD_DIR = loc(f=0.12, u=0.15, l=-0.09), (FWD * 0.6 + UP * 0.75 + LEFT * 0.2).normalized()


def _spar_half(t):
    """One fighter's attack half (t 0..1): wind up, thrust (the pad stops at the partner's stick), recover.
    Returns (grip, stick direction, how far into the thrust)."""
    wind = ramp(t, 0.1, 0.3) * (1 - ramp(t, 0.3, 0.4))
    thrust = ramp(t, 0.3, 0.42) * (1 - ramp(t, 0.6, 0.85))
    grip = GUARD_GRIP + loc(f=-0.02 * wind + 0.03 * thrust, u=0.03 * wind, l=0.02 * thrust)
    d = GUARD_DIR.lerp((FWD * 0.95 + UP * 0.14 + LEFT * 0.3).normalized(), thrust).lerp(
        (FWD * 0.3 + UP * 0.8 - LEFT * 0.4).normalized(), wind).normalized()          # wound back over its shoulder
    return grip, d, thrust


def _block_half(t):
    """The other half: the stick held across in front of the chest to take the partner's thrust."""
    up = ramp(t, 0.15, 0.32) * (1 - ramp(t, 0.7, 0.9))
    grip = GUARD_GRIP.lerp(loc(f=0.12, u=0.19, l=-0.08), up)
    d = GUARD_DIR.lerp((LEFT * 0.8 + FWD * 0.4 + UP * 0.2).normalized(), up).normalized()
    return grip, d, up


def spar(p):
    """Sparring with padded sticks, facing a partner SPAR_GAP away playing the same clip half a loop later: the
    first half it thrusts (the pad stops on the partner's raised stick), the second half it blocks. Bouncing on its
    toes in between, the free paw up in guard. 48 frames."""
    if p < 0.5:
        grip, d, a = _spar_half(p * 2)
        lunge, block = a, 0.0
    else:
        grip, d, b = _block_half((p - 0.5) * 2)
        lunge, block = 0.0, b
    Ts = frame_yz(d, (UP * 0.6 - FWD * 0.8).normalized())          # one steady roll hint: no flips mid-swing
    bounce = abs(math.sin(TAU * 4 * p)) * (1 - max(lunge, block))
    rots = act({
        "upperleg.l": [(Y, -10), (X, -20 - 12 * lunge)], "upperleg.r": [(Y, 10), (X, -14 + 8 * lunge)],
        "lowerleg.l": [(X, 30 + 8 * lunge)], "lowerleg.r": [(X, 26)],
        "foot.l": [(X, -10)], "foot.r": [(X, -12)],
        "spine": [(X, 6 + 8 * lunge - 4 * block)], "chest": [(Z, -8 * lunge)],
        "head": [(X, -4), (Z, 4 * lunge)],
        "ear.l": [(Y, 20 + 10 * block)], "ear.r": [(Y, -20 - 10 * block)],
    }, tail_sway(p, 8, 2))
    return rots, 0.006 * bounce, "legs", {"r": (grip, Ts, -LEFT * 0.6 - UP * 1.0), "l": (loc(f=0.1, u=0.2, l=0.07), None, ELBOW_OUT_L)}


# ---------------------------------------------------------------- the shadow course: a clip that travels a route
# Building coordinates of bld_shadow_course_2x2 (its spot_course sits at COURSE_SPOT, facing -Y with no turn, so the
# clip's own space is the building's, shifted). Each waypoint starts a segment of that kind; the route is closed.
COURSE_SPOT = V((0.5, -0.52, 0.0))
BEAM_H = 0.1                                    # the balance log's walking height
HURDLE_H = 0.1
COURSE = [((0.5, -0.52), "run"), ((0.1, -0.56), "sneak"), ((-0.42, -0.56), "run"), ((-0.62, -0.42), "hopup"),
          ((-0.64, -0.2), "beam"), ((-0.64, 0.36), "hopdown"), ((-0.58, 0.6), "run"), ((-0.3, 0.66), "sneak"),
          ((0.22, 0.64), "run"), ((0.56, 0.44), "hop"), ((0.6, 0.06), "run"), ((0.62, -0.2), "run")]
SPEED = {"run": 0.5, "sneak": 0.26, "beam": 0.3}
STRIDE = {"run": 0.26, "sneak": 0.12, "beam": 0.15}   # metres per gait cycle (two steps)
HOP_S = 0.45                                    # seconds a hop takes
BLEND = 0.06                                    # seconds either side of a change of gait to blend over


def _cr(p0, p1, p2, p3, t):
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def _course_table():
    """Sample the closed route: per segment its samples (point, cumulative length), kind, time and gait cycles."""
    pts = [V((x, y, 0)) for (x, y), _ in COURSE]
    n = len(pts)
    segs = []
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        smp, L, prev = [], 0.0, p1
        for k in range(41):
            q = _cr(p0, p1, p2, p3, k / 40)
            L += (q - prev).length
            smp.append((q, L))
            prev = q
        kind = COURSE[i][1]
        t = HOP_S if kind.startswith("hop") else L / SPEED[kind]
        cyc = 0.5 if kind.startswith("hop") else L / STRIDE[kind]
        segs.append({"smp": smp, "L": L, "kind": kind, "t": t, "cyc": cyc})
    total_t = sum(sg["t"] for sg in segs)
    gait = sum(sg["cyc"] for sg in segs if not sg["kind"].startswith("hop"))
    k = round(gait) / gait                                     # whole gait cycles round the loop: it closes
    for sg in segs:
        if not sg["kind"].startswith("hop"):
            sg["cyc"] *= k
    return segs, total_t


COURSE_SEGS, COURSE_T = _course_table()
COURSE_FRAMES = int(round(COURSE_T * 24 / 8)) * 8          # a multiple of 8 frames


def _seg_at(p):
    """(segment index, local fraction) at loop phase p."""
    t = (p % 1.0) * COURSE_T
    for i, sg in enumerate(COURSE_SEGS):
        if t < sg["t"] or i == len(COURSE_SEGS) - 1:
            return i, min(1.0, t / sg["t"])
        t -= sg["t"]


def _point(sg, u):
    """Point and tangent at fraction u of a segment's length."""
    target = u * sg["L"]
    smp = sg["smp"]
    for (a, la), (b, lb) in zip(smp, smp[1:]):
        if lb >= target:
            w = 0.0 if lb == la else (target - la) / (lb - la)
            return a.lerp(b, w), (b - a).normalized()
    return smp[-1][0], (smp[-1][0] - smp[-2][0]).normalized()


def course_pos(p):
    """Where the runner is (building coords, z = the floor under it) and its heading, at loop phase p."""
    i, u = _seg_at(p)
    sg = COURSE_SEGS[i]
    q, tng = _point(sg, u)
    floor = {"beam": BEAM_H, "hopdown": BEAM_H * (1 - smooth(u)), "hopup": BEAM_H * smooth(u)}.get(sg["kind"], 0.0)
    return V((q.x, q.y, floor)), tng


def _gait_phase(p):
    i, u = _seg_at(p)
    return sum(sg["cyc"] for sg in COURSE_SEGS[:i]) + COURSE_SEGS[i]["cyc"] * u


def _gait_pose(kind, ph, u):
    """Rotations and hips offset for one kind of movement at gait phase ph (u: fraction through a hop)."""
    if kind == "run":
        rots, bob = AN.walk(ph % 1.0, stride=34, arms=False)
        sw = 0.5 * 34 * AN.s(ph % 1.0)          # arms held a little out, pumping forward from a forward rest: never
        fl, fr = max(0.0, sw), max(0.0, -sw)    # swung back past the side (that puts the elbow in the belly)
        return merge(rots, {"spine": [(X, 5)], "head": [(X, -6)], "ear.l": [(Y, 18)], "ear.r": [(Y, -18)],
                            "upperarm.l": [(Y, -30), (X, -12 - fl)], "upperarm.r": [(Y, 30), (X, -12 - fr)],
                            "lowerarm.l": [(X, -18 - 0.4 * fl)], "lowerarm.r": [(X, -18 - 0.4 * fr)]}), bob, 0.0
    if kind == "sneak":
        rots, dz = AN.sneak(ph % 1.0)
        return rots, dz, 0.0
    if kind == "beam":
        rots, bob = AN.walk(ph % 1.0, stride=16, arms=False)
        return merge(rots, {"upperarm.l": [(Y, -68), (X, -10)], "upperarm.r": [(Y, 68), (X, -10)],
                            "lowerarm.l": [(X, -12)], "lowerarm.r": [(X, -12)], "ear.l": [(Y, 24)], "ear.r": [(Y, -24)]}), \
            bob * 0.5, 0.0
    tuck = math.sin(math.pi * u)                                       # a hop: legs tuck, arms reach, an arc
    rots = act({
        "upperleg.l": [(Y, -8), (X, -20 - 40 * tuck)], "upperleg.r": [(Y, 8), (X, -20 - 40 * tuck)],
        "lowerleg.l": [(X, 30 + 50 * tuck)], "lowerleg.r": [(X, 30 + 50 * tuck)],
        "foot.l": [(X, -10 - 20 * tuck)], "foot.r": [(X, -10 - 20 * tuck)],
        "upperarm.l": [(Y, -20), (X, -30 - 30 * tuck)], "upperarm.r": [(Y, 20), (X, -30 - 30 * tuck)],
        "lowerarm.l": [(X, -30)], "lowerarm.r": [(X, -30)],
        "spine": [(X, 10 + 6 * tuck)], "head": [(X, -10)], "ear.l": [(Y, 30)], "ear.r": [(Y, -30)],
        "tail_1": [(X, 10 * tuck)],
    }, tail_sway(u, 8, 1))
    arc = (0.16 if kind == "hop" else 0.08) * math.sin(math.pi * u)
    return rots, -0.01, arc


def course(p):
    """Running the shadow course: dash along the front, sneak under the bell rope, hop up onto the log and balance
    along it, hop down, sneak past the lantern, dash, hop the hurdle and run back to the start. One lap a loop; the
    route is COURSE (building coordinates). Returns a fifth item: (x, y, heading, floor) for the baker."""
    i, u = _seg_at(p)
    sg = COURSE_SEGS[i]
    ph = _gait_phase(p)
    rots, dz, arc = _gait_pose(sg["kind"], ph, u)
    tleft, tright = u * sg["t"], (1 - u) * sg["t"]                     # blend into the next / from the previous gait
    blend = None
    if tright < BLEND:
        nk = COURSE_SEGS[(i + 1) % len(COURSE_SEGS)]["kind"]
        if nk != sg["kind"]:
            blend = (nk, 0.5 * (1 - tright / BLEND), 0.0)
    elif tleft < BLEND:
        pk = COURSE_SEGS[i - 1]["kind"]
        if pk != sg["kind"]:
            blend = (pk, 0.5 * (1 - tleft / BLEND), 1.0)
    if blend:
        k2, w, u2 = blend
        r2, dz2, arc2 = _gait_pose(k2, ph, u2)
        rots = ("BLEND", rots, r2, w)
        dz = dz * (1 - w) + dz2 * w
    pos, tng = course_pos(p)
    yaw = math.degrees(math.atan2(tng.x, -tng.y))
    return rots, dz, "legs", {}, (pos.x - COURSE_SPOT.x, pos.y - COURSE_SPOT.y, yaw, pos.z + arc)


# ---------------------------------------------------------------- the stone stairs: hop up, hop down (one-way clips)
# kit_stairs_stone: 6 steps, each 1/6 m high and 0.157 m deep, the first tread from y -0.47. The climber starts in
# the cell in front (STAIRS_START, facing +Y up the stairs) and ends standing on the floor above, beyond the top step.
STAIR_RISE, STAIR_RUN, STAIR_N = 1.0 / 6, 0.94 / 6, 6
STAIRS_START = V((0.0, -0.62, 0.0))            # building coords (the stair piece's own), facing +Y
STAIR_TAIL = {"tail_1": (0, 0.2, 0.98), "tail_2": (0, 0.55, 0.83), "tail_3": (0, 0.85, 0.53)}   # going down: the
                                               # tail carried up and back (rig space: +Y is back), over the steps
STAIR_FOOT_DOWN = 0.035                        # going down: nearer the step's nose, the tail clear of the riser
STAIR_FOOT = 0.055                             # where the feet stand on a tread, from its nose (the belly clears the riser)
HOP_T, REST_T = 0.42, 0.18                     # seconds per hop, and the breath between hops


def _stair_stops(foot=None):
    """Where the climber stands, in order: the floor in front, each tread, the floor above (y, z)."""
    a = -0.47
    stops = [(STAIRS_START.y, 0.0)]
    for k in range(STAIR_N):
        stops.append((a + k * STAIR_RUN + (foot or STAIR_FOOT), (k + 1) * STAIR_RISE))
    stops.append((0.47 + 0.09, 1.0))
    return stops


STAIR_STOPS = _stair_stops()
STAIR_OFF = 0.3                                # going down, a last hop on: the resting tail clear of the bottom step
STAIR_STOPS_DOWN = _stair_stops(STAIR_FOOT_DOWN)[::-1]     # going down: near each tread's front (its riser behind)
STAIR_STOPS_DOWN.append((STAIRS_START.y - STAIR_OFF, 0.0))
STAIRS_T = len(STAIR_STOPS) * REST_T + (len(STAIR_STOPS) - 1) * HOP_T
STAIRS_FRAMES = int(round(STAIRS_T * 24 / 4)) * 4
STAIRS_DOWN_T = len(STAIR_STOPS_DOWN) * REST_T + (len(STAIR_STOPS_DOWN) - 1) * HOP_T
STAIRS_DOWN_FRAMES = int(round(STAIRS_DOWN_T * 24 / 4)) * 4


def _stairs_state(p, down):
    """(y, floor z, hop fraction or None) at phase p of the climb (down: the same stops, the other way)."""
    stops = STAIR_STOPS_DOWN if down else STAIR_STOPS
    t = p * (STAIRS_DOWN_T if down else STAIRS_T)
    for i in range(len(stops) - 1):
        if t < REST_T:
            return stops[i][0], stops[i][1], None
        t -= REST_T
        if t < HOP_T:
            return None, None, (i, t / HOP_T)
        t -= HOP_T
    return stops[-1][0], stops[-1][1], None


def stairs_path(p, down=False):
    """The feet's (y, z) and the hop fraction (None standing) at phase p: up, a hop lifts first (the toes clear the
    step's nose) then moves forward; down, it moves forward off the nose then drops."""
    stops = STAIR_STOPS_DOWN if down else STAIR_STOPS
    y, z, hop = _stairs_state(p, down)
    if hop is None:
        return y, z, None
    i, u = hop
    (y0, z0), (y1, z1) = stops[i], stops[i + 1]
    if not down:
        lift = smooth(min(1.0, u / 0.38))                # up past the step's nose first,
        fwd = smooth(max(0.0, (u - 0.34) / 0.58))        # then forward onto the tread
        z = z0 + (z1 - z0) * lift + 0.035 * math.sin(math.pi * min(1.0, u / 0.9))
    else:
        fwd = smooth(min(1.0, u / 0.55))
        drop = smooth(max(0.0, (u - 0.35) / 0.55))
        z = z0 + (z1 - z0) * drop + 0.03 * math.sin(math.pi * min(1.0, u / 0.5))
    return y0 + (y1 - y0) * fwd, z, u


def _stairs(p, down):
    y, z, hop = stairs_path(p, down)
    if hop is None:
        rots, dz = AN.idle((p * 4) % 1.0)
        rots = merge(rots, {"upperleg.l": [(X, -8)], "upperleg.r": [(X, -8)], "lowerleg.l": [(X, 14)], "lowerleg.r": [(X, 14)],
                            "foot.l": [(X, -6)], "foot.r": [(X, -6)], "head": [(X, 8 if down else -8)]})
    else:
        rots, dz, _ = _gait_pose("hop", 0.0, hop)
        swing = math.sin(math.pi * hop)                  # arms swing back and out: clear of the step ahead
        rots = merge(rots, {"upperarm.l": [(X, 60 + 25 * swing), (Y, -25)], "upperarm.r": [(X, 60 + 25 * swing), (Y, 25)],
                            "lowerarm.l": [(X, 20)], "lowerarm.r": [(X, 20)],
                            "upperleg.l": [(Y, -12 * swing)], "upperleg.r": [(Y, 12 * swing)]})   # knees apart: the
                                                                                       # tucked feet beside the belly
    # each clip has its own spot facing the way it goes (up: at the bottom facing +Y; down: at the top facing -Y),
    # so the body only travels straight ahead: d metres forward (the rig's forward is its own -Y)
    if down:                                             # the steps behind are higher: the tail up, clear of them,
        up = {**rots, **{n: [("AIM", v)] for n, v in STAIR_TAIL.items()}}
        up = merge(up, {"spine": [(X, 24)], "head": [(X, -14)]})   # and leaning on, the head clear of the tail
        t = p * STAIRS_DOWN_T                            # raised on the first hop (still on the top floor), lowered
        w = smooth(min(1.0, max(0.0, (t - REST_T) / HOP_T)))   # once off the stairs, on the last stop
        w *= 1.0 - smooth(min(1.0, max(0.0, (t - (STAIRS_DOWN_T - REST_T - HOP_T * 0.5)) / (REST_T + HOP_T * 0.5))))
        rots = ("BLEND", rots, up, w) if w < 0.999 else up
    d = (y - STAIR_STOPS[0][0]) if not down else (STAIR_STOPS[-1][0] - y)
    floor = z - (STAIR_STOPS[-1][1] if down else 0.0)    # from the spot's own floor (down: the floor above)
    return rots, dz, "legs", {}, (0.0, -d, 0.0, floor)


def climb_stairs_up(p):
    """Hopping up kit_stairs_stone: from the floor in front, a hop onto each step (a breath on each), and a last hop
    onto the floor above. One way: it ends where it stops, the game moves the raccoon on from there."""
    return _stairs(p, False)


def climb_stairs_down(p):
    """The same stairs going down: from the floor above, a hop down each step to the floor in front."""
    return _stairs(p, True)


# ---------------------------------------------------------------- the chicken ladder: scramble up, back down
# kit_ladder_wood (build_kit_climbs.py): a cleated plank from the floor at the front of the cell up to a plank deck
# laid on the back wall's top. Building coordinates of the piece; the climber's spots face +Y (up the plank).
LAD_FOOT, LAD_TOP = V((0.0, *KB.LAD_FOOT)), V((0.0, *KB.LAD_TOP))  # the plank's walking surface, bottom and top edge
LAD_DIR = (LAD_TOP - LAD_FOOT).normalized()
LAD_N = V((0.0, -LAD_DIR.z, LAD_DIR.y))                            # out of the plank, toward the climber
LAD_LEN = (LAD_TOP - LAD_FOOT).length
LAD_PITCH = math.degrees(math.atan2(LAD_DIR.y, LAD_DIR.z))         # the body leans this far forward on the plank
DECK_Z = KB.DECK_Z                                                 # the top deck's surface
LAD_STRIDE = KB.LAD_STRIDE                                         # a cleat every stride: a foot fits between
LAD_HIPS_OUT = 0.104                                               # the hips' distance off the plank while scrambling
# the belly is deeper than the legs are long: the legs keep (almost) their standing pose against the body, and the
# toes reach forward to the plank, resting just above a cleat
LAD_ANKLE = (0.022, -0.047)                                        # an ankle from the hips: (forward, up) in the body
LAD_TOE = 10                                                       # the feet point at the plank, toes this far down
STAND_ANKLE = 0.0458                                               # an ankle's height over a floor, standing
LAD_SPOT_UP = V((0.0, -0.52, 0.0015))                                  # standing at the foot (climb up starts here)
LAD_SPOT_DOWN = V((0.0, 0.3, DECK_Z + 0.0015))                              # standing on the deck (climb down starts here)
HANG = V((0.148, -0.0646, 0.0565))                                 # a hanging paw's slot from the hips (rig rest, left)
REST_H = 0.086                                                     # the hips' rest height over the feet


def lad_p(s):
    return LAD_FOOT + LAD_DIR * s


def _stance(s_h):
    """Scrambling on the plank with the hips at s_h: hips position, feet ankles (l, r) (building)."""
    H = lad_p(s_h) + LAD_N * LAD_HIPS_OUT
    a = H - LAD_N * LAD_ANKLE[0] + LAD_DIR * LAD_ANKLE[1]          # the body's forward is -LAD_N, its up LAD_DIR
    feet = [a + V((sx * 0.053, 0, 0)) for sx in (-1, 1)]           # l = -x (faces +Y)
    return H, feet


def _paws_at(s_p):
    return [lad_p(s_p) + LAD_N * 0.026 + V((sx * 0.07, 0, 0)) for sx in (-1, 1)]


def _ladder_keys():
    """The climb as key poses: (seconds, hips, tilt, feet [l, r], paws [l, r] or None = hanging, kind of move)."""
    keys = []
    H0 = LAD_SPOT_UP + V((0, 0, REST_H))
    feet0 = [LAD_SPOT_UP + V((sx * 0.053, 0.009, STAND_ANKLE)) for sx in (-1, 1)]
    s_h = 0.14                                                     # the first foothold: the toes clear the floor
    s_p = s_h + 0.06                                               # paws between two cleats
    keys.append((0.0, H0, 0.0, feet0, None, "stand"))
    keys.append((0.45, H0 + V((0, 0.025, 0.0)), 18.0, feet0, _paws_at(s_p), "reach"))   # lean, paws on the plank
    H, feet = _stance(s_h)
    keys.append((0.45, H, LAD_PITCH, feet, _paws_at(s_p), "hop"))  # hop the feet up onto the plank
    while s_h + LAD_STRIDE < LAD_LEN - 0.07:                        # up to the top: the shoulders over the deck
        s_p += LAD_STRIDE
        keys.append((0.26, H, LAD_PITCH, feet, _paws_at(s_p), "reach"))
        s_h += LAD_STRIDE
        H, feet = _stance(s_h)
        keys.append((0.32, H, LAD_PITCH, feet, _paws_at(s_p), "pull"))
    deck_paws = [V((sx * 0.07, LAD_TOP.y + 0.035, DECK_Z + 0.026)) for sx in (-1, 1)]
    keys.append((0.3, H, LAD_PITCH, feet, deck_paws, "reach"))    # paws over the top onto the deck
    Hs = LAD_SPOT_DOWN + V((0, 0, REST_H))
    feet_s = [LAD_SPOT_DOWN + V((sx * 0.053, 0.009, STAND_ANKLE)) for sx in (-1, 1)]
    keys.append((0.55, Hs, 0.0, feet_s, None, "vault"))            # pull up and hop onto the deck, over its edge
    keys.append((0.35, Hs, 0.0, feet_s, None, "stand"))
    return keys


LAD_KEYS = _ladder_keys()
LAD_T = sum(k[0] for k in LAD_KEYS)
LAD_FRAMES = int(round(LAD_T * 24 / 4)) * 4


def _hang(H, pitch):
    """Where a hanging paw is, for hips at H tilted `pitch` (building, left and right)."""
    R = Quaternion(V((1, 0, 0)), math.radians(-pitch))            # building: faces +Y, so a forward lean turns about -X
    out = []
    for sx in (-1, 1):                                             # rig left = building -x
        rel = V((sx * HANG.x, -HANG.y, HANG.z))
        out.append(H + R @ rel)
    return out


def _ladder_state(t):
    """Interpolated (hips, tilt, feet, paws, kind, u) at time t of the climb up."""
    acc = 0.0
    prev = LAD_KEYS[0]
    for key in LAD_KEYS[1:]:
        dt = key[0]
        if t <= acc + dt or key is LAD_KEYS[-1]:
            u = 0.0 if dt == 0 else min(1.0, max(0.0, (t - acc) / dt))
            return prev, key, u
        acc += dt
        prev = key
    return prev, LAD_KEYS[-1], 1.0


def ladder_up_frame(p):
    """Building-space targets at phase p of the climb up: hips, tilt, feet [l, r], paws [l, r], move kind, u."""
    a, b, u = _ladder_state(p * LAD_T)
    w = smooth(u)
    kind = b[5]
    H = a[1].lerp(b[1], w)
    if kind == "vault":                                            # an arc: the belly clears the deck's edge
        H = H + V((0, 0, 0.13 * math.sin(math.pi * u)))
    pitch = a[2] + (b[2] - a[2]) * w
    feet = []
    Ra, Rb, R = (Quaternion(V((1, 0, 0)), math.radians(-t)) for t in (a[2], b[2], pitch))
    for fa, fb in zip(a[3], b[3]):
        if fa == fb:                                               # planted: stays put
            f = fa.copy()
        else:                                                      # moving: with the body (it tilts as they go)
            wf = smooth(max(0.0, (u - 0.4) / 0.6)) if kind == "vault" else w   # vault: the body goes up, then the feet
            f = H + R @ (Ra.inverted() @ (fa - a[1])).lerp(Rb.inverted() @ (fb - b[1]), wf)
            f.z = max(f.z, LAD_SPOT_UP.z + STAND_ANKLE)               # never down through the floor as it tilts
        if kind == "pull" and fa != fb:                            # the feet hop off the plank as the paws pull
            f = f + LAD_N * (0.012 * math.sin(math.pi * u))
        feet.append(f)
    pa = a[4] if a[4] is not None else _hang(a[1], a[2])
    pb = b[4] if b[4] is not None else _hang(b[1], b[2])
    paws = []
    for qa, qb in zip(pa, pb):
        if (a[4] is None) != (b[4] is None):                       # to / from hanging: move with the body
            q = H + R @ (Ra.inverted() @ (qa - a[1])).lerp(Rb.inverted() @ (qb - b[1]), w)
        else:
            q = qa.lerp(qb, w)
        if kind == "reach" and qa != qb:                           # a paw lifts off as it reaches
            up = V((0, 0, 0.05)) if qb.z >= DECK_Z else LAD_N * 0.035                # over the cleat / the deck's edge
            q = q + up * min(1.0, 2.0 * math.sin(math.pi * u))
        paws.append(q)
    return H, pitch, feet, paws, kind, u


def _b2r(v, spot, point=True):
    """Building -> the clip's own space for a spot facing +Y at `spot` (rig forward is its -Y, its left is +X)."""
    d = v - spot if point else v
    return V((-d.x, -d.y, d.z))


def _ladder_clip(p, down):
    H, pitch, feet, paws, kind, u = ladder_up_frame(1.0 - p if down else p)
    spot = LAD_SPOT_DOWN if down else LAD_SPOT_UP
    rots = act({
        "spine": [(X, 4)], "head": [(X, -12 - 1.4 * pitch)],      # looks up the plank (the snout clears it)
        "ear.l": [(Y, 24)], "ear.r": [(Y, -24)],
        "tail_1": [(X, -10)],
    }, tail_sway(p * 6 % 1.0, 6, 1))
    toe = _b2r(-LAD_N * math.cos(math.radians(LAD_TOE)) - LAD_DIR * math.sin(math.radians(LAD_TOE)), spot, point=False)
    flat = _b2r(V((0, 1, -0.27)).normalized(), spot, point=False)
    feet_t = {}
    for side, f in zip("lr", feet):                                # a foot on a floor stands flat; off it, it turns
        lvl = (DECK_Z + 0.0015 if f.y > LAD_TOP.y else LAD_SPOT_UP.z) + STAND_ANKLE   # to point at the plank
        t = min(1.0, max(0.0, (f.z - lvl) / 0.04))
        kpole = _b2r(-LAD_N, spot, point=False).lerp(FWD, 1 - t)   # knees toward the plank, not up into the belly
        feet_t[side] = (_b2r(f, spot), kpole, flat.lerp(toe, t).normalized())
    out_r, out_l = -LEFT - _b2r(LAD_DIR, spot, point=False) * 0.4, LEFT - _b2r(LAD_DIR, spot, point=False) * 0.4
    arms = {"l": (_b2r(paws[0], spot), None, out_l), "r": (_b2r(paws[1], spot), None, out_r)}
    h = _b2r(H, spot)
    ground = DECK_Z if H.y > LAD_TOP.y else 0.0                    # the tail rests on the floor / the deck, never through
    return rots, 0.0, "free", arms, (h.x, h.y, 0.0, h.z - REST_H, pitch, ground - spot.z), feet_t


def climb_ladder_up(p):
    """Scrambling up the chicken ladder (kit_ladder_wood): lean onto the plank, hop the feet up onto it, then reach
    up a cleat with both paws and pull up (the feet tuck and land under the hips) over and over; at the top, paws
    over onto the deck, pull up and stand. One way: ends standing on the deck (LAD_SPOT_DOWN)."""
    return _ladder_clip(p, False)


def climb_ladder_down(p):
    """The climb up played backwards, from the deck: backing down the plank, facing it, as you go down a ladder."""
    return _ladder_clip(p, True)


KIT = False          # set while baking the kit (its own proportions: see rummage)

JOBS = {   # clip: (fn, frames, tool)
    "work_chop": (chop, 32, "prop_axe"),
    "work_fish": (fish, 96, "prop_fishing_rod"),
    "work_scrub": (scrub, 48, None),
    "work_rummage": (rummage, 48, None),
    "work_water": (water, 64, "prop_watering_can"),
    "work_tend": (tend, 48, None),
    "work_stash": (stash, 48, None),
    "work_pump": (pump, 48, None),
    "work_stir": (stir, 48, "prop_ladle"),
    "work_hammer": (hammer, 32, "prop_hammer"),
    "work_haggle": (haggle, 48, None),
    "work_drink": (drink, 96, "prop_mug"),
    "work_chat": (chat, 96, None),
    "work_grind": (grind, 48, "prop_pestle"),
    "work_read": (read, 48, None),
    "work_teach": (teach, 96, None),
    "work_listen": (listen, 96, None),
    "work_guard": (guard, 96, "prop_spear"),
    "work_ring": (ring, 48, None),
    "work_mourn": (mourn, 96, None),
    "work_sweep": (sweep, 48, "prop_brush"),
    "work_swing": (swing, 48, None),
    "work_course": (course, COURSE_FRAMES, None),
    "work_picklock": (picklock, 48, "prop_lockpick"),
    "work_lift": (lift, 48, None),
    "work_spar": (spar, 48, "prop_stick"),
    "climb_stairs_up": (climb_stairs_up, STAIRS_FRAMES, None),
    "climb_stairs_down": (climb_stairs_down, STAIRS_DOWN_FRAMES, None),
    "climb_ladder_up": (climb_ladder_up, LAD_FRAMES, None),
    "climb_ladder_down": (climb_ladder_down, LAD_FRAMES, None),
}
JOB_RIG = {"work_teach": "chr_raccoon_elder", "work_listen": "chr_raccoon_kit", "work_swing": "chr_raccoon_kit"}   # everything else: the adult


def rig_of(name):
    return JOB_RIG.get(name, "chr_raccoon")


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


def blend_quats(rig, ra, rb, w):
    """Pose quaternions part-way (w) from one rotation set to another (each bone's pose rotation slerped), so a change
    of gait (run to sneak) eases over a few frames instead of snapping."""
    qa, qb = pose_quats(rig, ra), pose_quats(rig, rb)
    return {n: qa[n].slerp(qb[n], w) for n in qa}


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

    hips_inv = hips.matrix_local.to_3x3().inverted()
    travel = [V(), 0.0, 0.0]                               # a clip that travels: the hips' offset, heading, forward tilt
    hm = hips.matrix_local.to_3x3().normalized()

    def pose(rots, z):
        yq = None
        if travel[1] or travel[2]:                          # heading and tilt turn the whole posed body as one, about
            yq = Quaternion(V((0, 0, 1)), math.radians(travel[1])) @ Quaternion(V((1, 0, 0)), math.radians(travel[2]))
            Ri = yq.to_matrix().inverted()                  # aims (IK) are where they end up: aim before the turn
            rots = {n: [("AIM", tuple(Ri @ V(e[1]))) if e[0] == "AIM" else ("MAT", Ri @ e[1]) if e[0] == "MAT" else e
                        for e in lst] for n, lst in rots.items()}
        qs = pose_quats(rig, rots)
        if yq is not None:
            qs["hips"] = (hm.inverted() @ yq.to_matrix() @ hm).to_quaternion() @ qs["hips"]   # the hips: the root only
        for pb in rig.pose.bones:
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = qs[pb.name]
            pb.location = (0, 0, 0)
        rig.pose.bones["hips"].location = up_local * z + hips_inv @ travel[0]
        bpy.context.view_layer.update()
    worst = 0.0
    fverts = _forearm_verts(rig, ob)
    pushes = {"l": V(), "r": V()}                          # carried frame to frame: smooth, no popping
    for f in range(frames + 1):
        out = fn((f / frames) % 1.0)
        rots, dz, support, arms = out[:4]
        floor = 0.0
        if len(out) > 4:                                    # a travelling clip: where it is, its heading, the floor
            tx, ty, yaw, floor = out[4][:4]                 # ("free" support: floor = the hips' own height offset)
            travel[0] = V((tx, ty, 0)) * ratio
            travel[1] = yaw
            travel[2] = out[4][4] if len(out[4]) > 4 else 0.0
            floor *= ratio
        feet = out[5] if len(out) > 5 else {}
        if isinstance(rots, tuple):                         # a change of gait: resolve the blend to plain rotations
            rots = {n: [("LOCALQ", q)] for n, q in blend_quats(rig, rots[1], rots[2], rots[3]).items()}
        z = dz * k
        pose(rots, z)
        if support == "free":                               # the clip places the hips itself (climbing)
            z = floor
        else:
            z -= AN._lowest(ob, legs if support == "legs" else seat) - floor
        pose(rots, z)
        if feet:                                            # feet on given spots (a ladder's plank): leg IK
            lr = {}
            for side, (ankle, kpole, toe) in feet.items():
                r_, miss = leg_rots(rig, side, ankle * ratio, kpole, toe)
                lr.update(r_)
                if report is not None and miss > 0.002:
                    report.setdefault(name + "_feet", []).append((f, side, round(miss, 4)))
            rots = merge(rots, lr)
            pose(rots, z)
        ground = min(floor, 0.0)                            # the tail lies on the ground, not through it (going
                                                            # down stairs: the step it stands on)
        if support == "free":                               # climbing: the clip says where the ground is (or none)
            ground = out[4][5] * ratio if len(out[4]) > 5 and out[4][5] is not None else None
        if tail and ground is not None and AN._lowest(ob, tail) < ground - 0.001:
            lo, hi = 0.0, 70.0
            for _ in range(7):
                mid = (lo + hi) / 2
                pose(merge(rots, {"tail_1": [(tuple(lift_ax), mid)]}), z)
                lo, hi = (lo, mid) if AN._lowest(ob, tail) >= ground - 0.001 else (mid, hi)
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
