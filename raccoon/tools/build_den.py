"""bld_den_2x2: a raccoon family's den, second pass. Hollow and lived in.

A lopsided, hand-stacked dry-stone wall (each stone its own block, courses offset like real stonework, jittered in
height and depth, a few mossy ones low down) round a dirt-and-straw floor, with a doorway and three window holes cut
cleanly through it. Inside: three straw nests with blankets (two adult-sized, one for a kit), a pot-belly stove, a
crate table with a candle, a shelf of jars, a little stash of stolen coins and a rug. Outside: a plank door swung
open, shutters, a stolen shield hung on the wall, a lantern post, firewood, rocks.

The roof is a CHILD object, bld_den_2x2_roof, inside the same .glb: three stepped tiers of plain brown shingles that
nest cleanly (each tier's top tucked under the next with clearance) and the stovepipe. Hide that node in the game (camera close, or a
raccoon inside) to see into the den; the walls stop at 0.6 m so the inside reads from the game camera.

2x2 cells, 1 m tall, inset 0.03 m, origin bottom-centre, entrance facing -Y like every other building.

Run:  python3 tools/build_den.py           (--no-renders to skip the renders)
Out:  den.blend, export/bld_den_2x2.glb, renders/bld_den_*.png
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_buildings_blockout as B  # noqa: E402

ROOT = P.ROOT
V = Vector
TAU = 2 * math.pi
CY = 0.03                                            # plan centre sits a touch back so the doorstep has room
COURSES = [0.16, 0.15, 0.145, 0.14]                  # wall courses, bottom up: top of wall at 0.595
THICK = 0.13
# openings: (centre angle deg, half-width deg, first course, last course) -- angle 0 = +X, 90 = back (+Y)
DOOR = (-90, 15.5, 0, 2)
WINDOWS = [(-38, 8.5, 2, 2), (158, 8.0, 2, 2), (68, 6.5, 2, 2)]
OPENINGS = [DOOR] + WINDOWS
# beds: flat straw mats with a blanket on top, each big enough for the WHOLE sleeping raccoon (its sleep pose spreads
# its legs and wraps its tail on the floor: 41 x 33 cm for an adult, 25 x 22 for a kit, measured from the clip), so
# nothing of a sleeper hangs over an edge or cuts through a rim. (blanket centre, half-sizes, blanket colour, variant)
MAT, BLANKET = 0.014, 0.005
SLEEP_BOX = {"chr_raccoon": (V((-0.0315, 0.024)), V((0.207, 0.167))),          # footprint centre + half-sizes, own space
             "chr_raccoon_kit": (V((-0.019, 0.0075)), V((0.124, 0.108)))}
BEDS = [(V((-0.25, CY + 0.27, 0)), "cloth_blue", "chr_raccoon"),               # two adults side by side at the back
        (V((0.23, CY + 0.27, 0)), "cloth_red", "chr_raccoon"),
        (V((-0.42, CY - 0.14, 0)), "teal", "chr_raccoon_kit")]                 # the kit's, front left


def R(a):
    """Outer wall radius at angle a (radians): a slightly squashed, lopsided ring, not a regular polygon."""
    return 0.80 + 0.035 * math.sin(2 * a + 0.7) + 0.018 * math.cos(3 * a - 1.0)


def at(a, r, z):
    return V((math.cos(a) * r, CY + math.sin(a) * r, z))


def course_z(c):
    return sum(COURSES[:c]), sum(COURSES[:c + 1])


class DenMesh(B.M):
    """Building mesh whose faces are built facing the right way, so no normal recalculation is needed (the stones
    are open shells: no bottoms or hidden ends, which recalc_face_normals would flip unpredictably)."""

    WALL, EMBED, FREE = 0, 1, 2          # part kinds: wall stones / meant to sit in the wall / must stay clear of it

    def __init__(self):
        super().__init__()
        self.kl = self.bm.faces.layers.int.new("kind")
        self.kind = self.FREE

    def tag(self, faces, swatch):
        super().tag(faces, swatch)
        for f in faces:
            f[self.kl] = self.kind

    def face(self, vs, want, swatch):
        f = self.bm.faces.new(vs)
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
        self.tag([f], swatch)
        return f

    def obj(self, name, coll):
        ids = [f[self.sw] for f in self.bm.faces]
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        me.materials.append(bpy.data.materials["M_Palette"])
        for i, sid in enumerate(ids):
            P.set_swatch(ob, K.NAMES[sid], [i])
        return ob


def stone(m, a0, a1, z0, z1, lean, rnd, sw, end0=False, end1=False, bottom=False, top=True, crown=False):
    """One wall stone between angles a0..a1, heights z0..z1. Watertight with its neighbours: the inner face and the
    course heights are exact, so there are no see-through slits. The stone reads as a stone because its outer face is
    a little proud or sunk and narrower than its back, so a dark V-groove of mortar runs between neighbours. Openings
    get flat jamb faces instead (end0 / end1). crown: top course, whose top is chamfered and a little uneven."""
    g = 0.011                                                   # half the groove width, as an angle
    dr = rnd.uniform(-0.01, 0.01)
    oa0, oa1 = a0 + (0 if end0 else g), a1 - (0 if end1 else g)
    t0, t1 = (z1 + rnd.uniform(-0.01, 0.006), z1 + rnd.uniform(-0.01, 0.006)) if crown else (z1, z1)
    ch = 0.01 if crown else 0.0
    ro = lambda a: R(a) - lean + dr                             # noqa: E731
    ri = lambda a: R(a) - lean - THICK                          # noqa: E731
    ob0, ob1 = m.bm.verts.new(at(oa0, ro(oa0), z0)), m.bm.verts.new(at(oa1, ro(oa1), z0))
    ot0, ot1 = m.bm.verts.new(at(oa0, ro(oa0) - ch, t0)), m.bm.verts.new(at(oa1, ro(oa1) - ch, t1))
    ib0, ib1 = m.bm.verts.new(at(a0, ri(a0), z0)), m.bm.verts.new(at(a1, ri(a1), z0))
    it0, it1 = m.bm.verts.new(at(a0, ri(a0) + ch, t0)), m.bm.verts.new(at(a1, ri(a1) + ch, t1))
    am = (a0 + a1) / 2
    out = V((math.cos(am), math.sin(am), 0))
    m.face((ob0, ob1, ot1, ot0), out, sw)
    m.face((ib0, ib1, it1, it0), -out, "stone_dark")                            # inner face, in shadow
    if top:
        m.face((ot0, ot1, it1, it0), V((0, 0, 1)), "stone_light")
    m.face((ob0, ot0, it0, ib0), V((-math.sin(a0), math.cos(a0), 0)) * -1, "stone_mid" if end0 else "stone_deep")
    m.face((ob1, ot1, it1, ib1), V((-math.sin(a1), math.cos(a1), 0)), "stone_mid" if end1 else "stone_deep")
    if bottom:
        m.face((ob0, ob1, ib1, ib0), V((0, 0, -1)), "stone_dark")


def wall(m, rnd):
    """Five offset courses of stones; openings are cut out of the stones' angle ranges, so jambs come out straight."""
    m.kind = m.WALL
    for c, h in enumerate(COURSES):
        z0, z1 = course_z(c)
        lean = 0.015 * c                                       # courses step in a little: corbelled, not a tube
        off = rnd.uniform(0, 0.3)
        edges = [off]                                          # stones of mixed lengths, no two courses alike
        while edges[-1] < off + TAU - 0.45:
            edges.append(edges[-1] + rnd.uniform(0.32, 0.55))
        edges.append(off + TAU)
        cuts = [(math.radians(ac - hw), math.radians(ac + hw)) for ac, hw, c0, c1 in OPENINGS if c0 <= c <= c1]
        above = [(math.radians(ac - hw), math.radians(ac + hw)) for ac, hw, c0, c1 in OPENINGS if c == c1 + 1]
        for e0_, e1_ in zip(edges, edges[1:]):
            a0, a1 = e0_, e1_
            pieces = [(a0, a1, False, False)]
            for c0_, c1_ in cuts:                                # clip against every opening in this course
                nxt = []
                for p0, p1, e0, e1 in pieces:
                    lo, hi = _norm(c0_, p0), _norm(c1_, p0)
                    if hi <= p0 or lo >= p1:
                        nxt.append((p0, p1, e0, e1))
                        continue
                    if lo - p0 > math.radians(3):
                        nxt.append((p0, lo, e0, True))
                    if p1 - hi > math.radians(3):
                        nxt.append((hi, p1, True, e1))
                pieces = nxt
            for p0, p1, e0, e1 in pieces:
                mid = (p0 + p1) / 2
                bottom = any(_norm(lo, mid) <= mid <= _norm(hi, mid) for lo, hi in above)     # lintel stones
                sw = rnd.choice(["stone_mid", "stone_mid", "stone_light", "stone_pale"])
                if c == 0 and rnd.random() < 0.1:
                    sw = "moss"
                stone(m, p0, p1, z0, z1, lean, rnd, sw, e0, e1, bottom, top=True, crown=c == len(COURSES) - 1)
    m.kind = m.FREE


def _norm(a, ref):
    """a shifted by whole turns to lie within half a turn of ref."""
    while a - ref > math.pi:
        a -= TAU
    while ref - a > math.pi:
        a += TAU
    return a


def frame_at(ac, rr=0.0):
    """Centre point on the wall surface and the outward / along-wall directions at angle ac (degrees)."""
    a = math.radians(ac)
    out = V((math.cos(a), math.sin(a), 0))
    along = V((-math.sin(a), math.cos(a), 0))
    return at(a, R(a) + rr, 0), out, along, a


def window(m, ac, hw, c0, c1, shutter, curtain, rnd):
    z0, _ = course_z(c0)
    _, z1 = course_z(c1)
    lean = 0.015 * c1
    p, out, along, a = frame_at(ac, -lean - THICK / 2)          # middle of the wall's depth
    w = 2 * R(a) * math.sin(math.radians(hw))
    rot = (0, 0, a + math.pi / 2)
    m.kind = m.EMBED
    m.obox(p + V((0, 0, z0 - 0.01)) + out * 0.02, (w + 0.06, THICK + 0.04, 0.03), "wood_light", rot=rot)  # sill, 3 cm proud
    m.obox(p + V((0, 0, z1 + 0.015)), (w + 0.06, THICK + 0.02, 0.035), "wood_dark", rot=rot)              # lintel board
    for s in (-1, 1):                                                                                      # jamb boards
        m.obox(p + along * s * (w / 2 - 0.01) + V((0, 0, (z0 + z1) / 2)), (0.025, THICK + 0.02, z1 - z0), "wood_mid", rot=rot)
    m.kind = m.FREE
    if shutter:                                     # a plank shutter folded back flat against the wall, a bit askew
        s = shutter
        # tangent to the wall where it hangs (not where the window is), so it lies flat on the curve
        sdeg = ac + s * math.degrees((w * 0.98) / R(a))
        po, sout, _, sa = frame_at(sdeg, -0.015 * max(c0 - 1, 0) + 0.012 + 0.03)   # clear of the proudest stone, wall bulge included
        sh = po + V((0, 0, (z0 + z1) / 2 - 0.01))
        m.obox(sh, (w * 0.9, 0.02, (z1 - z0) * 0.95), "wood_weathered", rot=(0, 0, sa + math.pi / 2))
        m.obox(sh + sout * 0.014, (w * 0.95, 0.01, 0.025), "wood_dark", rot=(0, 0, sa + math.pi / 2))
    if curtain:                                     # a rag tied back on the inside
        pi_ = at(a, R(a) - lean - THICK - 0.05, 0)
        m.obox(pi_ + along * (w * 0.22) + V((0, 0, (z0 + z1) / 2 - 0.005)), (w * 0.5, 0.012, (z1 - z0) * 0.85), curtain,
               rot=rot)


def pad(m, c, rx, ry, h, sw, z0=0.0, n=12, side="wood_bark", band=True):
    """A flat rounded-rectangle pad (a superellipse: top face + side band), bottom at z0."""
    top, bot = [], []
    for k in range(n):
        a = TAU * (k + 0.5) / n
        ca, sa = math.cos(a), math.sin(a)
        p = V((c.x + rx * math.copysign(abs(ca) ** 0.5, ca), c.y + ry * math.copysign(abs(sa) ** 0.5, sa), 0))
        top.append(m.bm.verts.new(p + V((0, 0, z0 + h))))
        bot.append(m.bm.verts.new(p + V((0, 0, z0))))
    m.face(top, V((0, 0, 1)), sw)
    for k in range(n if band else 0):
        j = (k + 1) % n
        a = TAU * (k + 0.5) / n
        m.face((bot[k], bot[j], top[j], top[k]), V((math.cos(a), math.sin(a), 0)), side)


def bed(m, c, blanket, variant):
    """A straw mat with a blanket on top that covers the sleeper's whole footprint (it faces the front, -Y)."""
    off, half = SLEEP_BOX[variant]
    pad(m, c, half.x + 0.03, half.y + 0.03, MAT, "rope", side="rope_dark")          # straw edge showing round it
    pad(m, c, half.x + 0.006, half.y + 0.006, BLANKET, blanket, z0=MAT, side=blanket, band=False)


def bed_spot(c, variant):
    """Where the sleeper stands on its bed (its footprint centred on the blanket), facing the front."""
    off, half = SLEEP_BOX[variant]
    return V((c.x - off.x, c.y - off.y, MAT + BLANKET + 0.002))


def bld_den_2x2(coll, rnd):
    m = DenMesh()
    wall(m, rnd)
    # ---- floor: trampled straw over dirt, a rug in the middle
    pts = [at(TAU * k / 14, R(TAU * k / 14) - THICK + 0.01, 0.004) for k in range(14)]
    vs = [m.bm.verts.new(p) for p in pts]
    m.kind = m.EMBED                                        # its rim tucks under the wall
    m.face(vs, V((0, 0, 1)), "wood_cut")
    m.kind = m.FREE
    m.obox(V((-0.02, CY - 0.08, 0.008)), (0.5, 0.34, 0.008), "cloth_mustard", rot=(0, 0, 0.25))
    m.obox(V((-0.02, CY - 0.08, 0.011)), (0.44, 0.28, 0.008), "cloth_red", rot=(0, 0, 0.25))
    # ---- beds: two adult nests at the back, a small one for a kit on the left
    for c, bl, variant in BEDS:
        bed(m, c, bl, variant)
    # ---- pot-belly stove (pipe continues on the roof object)
    st = V((0.52, CY + 0.0, 0.0))
    m.cyl(st + V((0, 0, 0.03)), 0.075, 0.06, "iron_dark", segs=7)
    m.cyl(st + V((0, 0, 0.13)), 0.1, 0.15, "iron", segs=7, r2=0.085, cap="iron_dark")
    m.obox(st + V((-0.088, 0, 0.12)), (0.022, 0.085, 0.066), "iron_dark")            # fire door frame (glow: a part)
    m.cyl(st + V((0, 0, 0.42)), 0.032, 0.44, "rust", segs=6)                          # pipe up to the wall top
    # ---- crate table with a candle and a mug, a stool
    B.crate(m, V((0.22, CY - 0.33, 0)), 0.15, rot=0.3)
    m.cyl(V((0.2, CY - 0.33, 0.175)), 0.016, 0.05, "cloth_cream", segs=6)
    m.cyl(V((0.26, CY - 0.3, 0.17)), 0.022, 0.04, "pewter", segs=6)
    # ---- shelf on the back wall: plank on pegs, jars and a stolen book
    p, out, along, a = frame_at(112, -THICK - 0.045 - 0.065)
    rot = (0, 0, a + math.pi / 2)
    m.kind = m.EMBED
    m.obox(p + V((0, 0, 0.37)) + out * 0.03, (0.36, 0.13, 0.025), "wood_mid", rot=rot)     # back edge in the wall
    for s in (-0.12, 0.12):
        m.obox(p + along * s + V((0, 0, 0.34)) + out * 0.05, (0.025, 0.08, 0.04), "wood_dark", rot=rot)
    m.kind = m.FREE
    for s, sw, h in ((-0.1, "verdigris", 0.07), (0.0, "gold", 0.06)):
        m.cyl(p + along * s + V((0, 0, 0.383 + h / 2)), 0.024, h, sw, segs=5, cap="cloth_cream")
    m.obox(p + along * 0.12 + V((0, 0, 0.415)), (0.04, 0.06, 0.07), "cloth_blue", rot=(0, 0.25, a + math.pi / 2))
    # ---- the family stash: coins and a gem by the back-right bed
    for i, (dx, dy) in enumerate(((0, 0), (0.05, 0.02), (0.02, 0.05))):
        m.cyl(V((0.42 + dx, CY - 0.2 + dy, 0.008 + 0.012 * (i == 0))), 0.028, 0.012, "gold", segs=5, cap="gold_light")
    m.cyl(V((0.44, CY - 0.18, 0.05)), 0.02, 0.04, "ruby", segs=4, r2=0.0)
    # ---- windows: a shutter on two of them, a rag curtain inside the back-left one
    window(m, *WINDOWS[0], shutter=1, curtain=None, rnd=rnd)
    window(m, *WINDOWS[1], shutter=None, curtain="cloth_red", rnd=rnd)
    window(m, *WINDOWS[2], shutter=-1, curtain=None, rnd=rnd)
    # ---- doorway: log lintel, door posts, plank door swung open outward, step stone, mat
    ac, hw, c0, c1 = DOOR
    p, out, along, a = frame_at(ac, -0.02)
    _, zt = course_z(c1)
    w = 2 * R(a) * math.sin(math.radians(hw))
    m.kind = m.EMBED
    m.cyl(p + V((0, 0, zt + 0.03)) + out * 0.02, 0.04, w + 0.2, "wood_bark", cap="wood_cut", axis=tuple(along), segs=6)
    for s in (-1, 1):
        m.obox(p + along * s * (w / 2 + 0.015) + V((0, 0, zt / 2)), (0.04, 0.16, zt), "wood_dark", rot=(0, 0, a + math.pi / 2))
    m.obox(p + out * 0.08 + V((0, 0, 0.004)) - out * 0.17, (w * 0.8, 0.16, 0.008), "burlap", rot=(0, 0, a + math.pi / 2))
    m.kind = m.FREE
    hinge = p + along * (w / 2 + 0.03) + out * 0.05           # hinged on the right jamb (seen from outside)
    d = -along * math.cos(2.85) + out * math.sin(2.85)         # swung right open, back against the outer wall
    nrm = V((-d.y, d.x, 0))
    door_c = hinge + d * (w * 0.47)
    drot = (0, 0, math.atan2(d.y, d.x))
    m.obox(door_c + V((0, 0, zt * 0.48)), (w * 0.94, 0.035, zt * 0.92), "wood_mid", rot=drot)
    for zz in (0.12, 0.34):
        for sgn in (-1, 1):
            m.obox(door_c + V((0, 0, zz)) + nrm * sgn * 0.02, (w * 0.9, 0.01, 0.03), "iron_dark", rot=drot)
    m.obox(p + out * 0.13 + V((0, 0, 0.012)), (w + 0.04, 0.15, 0.024), "stone_pale", rot=(0, 0, a + math.pi / 2 + 0.05))
    # ---- stolen shield hung on the wall left of the door, lantern post on the right
    sp, sout, _, sa = frame_at(-128, -0.015 + 0.012 + 0.03)
    m.cyl(sp + V((0, 0, 0.33)), 0.13, 0.03, "iron_light", cap="cloth_blue", axis=tuple(sout), segs=8)
    m.cyl(sp + V((0, 0, 0.33)) + sout * 0.022, 0.035, 0.025, "gold", axis=tuple(sout), segs=6)
    lp, lout, lal, la = frame_at(-62, 0.1)                   # arm reaches toward the door, along the wall
    m.obox(lp + V((0, 0, 0.29)), (0.04, 0.04, 0.58), "wood_dark")
    m.obox(lp + V((0, 0, 0.565)) - lal * 0.06, (0.14, 0.03, 0.025), "wood_dark", rot=(0, 0, la + math.pi / 2))
    m.obox(lp + V((0, 0, 0.52)) - lal * 0.11, (0.075, 0.075, 0.02), "iron_dark")         # lantern cap (glow: a part)
    m.obox(lp + V((0, 0, 0.432)) - lal * 0.11, (0.07, 0.07, 0.012), "iron_dark")         # lantern base
    # ---- firewood against the front-left of the wall, rocks and mushrooms round the base
    # two logs side by side along the wall, one resting in the groove between them: every log lies along the wall
    # tangent, the rows step outward from the wall, 4 mm apart, so no log cuts another, the wall or the floor
    lr, gap = 0.038, 0.004
    fp, fout, falong, fa = frame_at(-150, 0.01 + 0.012 + lr + 0.01)      # clear of the proudest stone + a margin
    rest = lr + math.sqrt((2 * lr + gap) ** 2 - ((2 * lr + gap) / 2) ** 2)
    for dz, dout in ((lr + 0.001, 0.0), (lr + 0.001, 2 * lr + gap), (rest, lr + gap / 2)):
        B.log(m, fp + fout * dout + V((0, 0, dz)), lr, 0.3, axis=tuple(falong))
    for ang, s in ((150, 0.06), (25, 0.07)):
        rp, rout, _, _ = frame_at(ang, 0.04 + s * 1.3)
        m.blob(rp + V((0, 0, s * 0.4)), V((s * 1.3, s, s * 0.8)), "stone_light", 5, 3)
    for dx, dy, h in ((0.0, 0.0, 0.07),):
        mp, mout, _, _ = frame_at(45, 0.06)
        m.cyl(mp + V((dx, dy, h / 2)), 0.012, h, "cloth_cream", segs=4)
        m.cyl(mp + V((dx, dy, h)), 0.035, 0.025, "mushroom_glow", segs=5, r2=0.012)
    return m.obj("bld_den_2x2", coll)


# roof tiers, bottom up: (eave radius x R, eave z, top radius x R, top z). Each tier's top edge tucks under the tier
# above with real clearance (>= 1.5 cm below that tier's underside), and each eave lip sits above the tier below, so
# the tiers never cut through each other. All tiers share the same facet angles, so their seams line up.
TIERS = [(1.09, 0.645, 0.70, 0.75), (0.80, 0.775, 0.40, 0.86), (0.50, 0.89, 0.0, 0.975)]
LIP = 0.035
ROOF_N = 14


def roof_angles(rnd):
    rot0 = rnd.uniform(0, TAU)
    return [rot0 + TAU * k / ROOF_N + rnd.uniform(-0.04, 0.04) for k in range(ROOF_N)]


def tier(m, angles, r0, z0, r1, z1, rnd, wobble=0.0):
    """One roof tier: brown shingle facets from the eave up to the top ring (or an apex when r1 is 0), a dark eave
    lip and a dark underside. wobble: how much the eave (only the eave) sags or lifts, for a hand-built look."""
    n = len(angles)
    lo, lip, hi = [], [], []
    for a in angles:
        e = z0 + rnd.uniform(-wobble, wobble * 0.3)
        lo.append(m.bm.verts.new(at(a, R(a) * r0, e)))
        lip.append(m.bm.verts.new(at(a, R(a) * r0 - 0.01, e - LIP)))
        hi.append(m.bm.verts.new(at(a, R(a) * r1, z1)) if r1 > 0 else None)
    top = m.bm.verts.new(V((0.0, CY, z1))) if r1 == 0 else None
    for k in range(n):
        j = (k + 1) % n
        a = (angles[k] + _norm(angles[j], angles[k])) / 2
        out = V((math.cos(a), math.sin(a), 0.8))
        up_k, up_j = (hi[k], hi[j]) if top is None else (top, top)
        if top is None:
            m.face((lo[k], lo[j], up_j, up_k), out, "wood_mid")
            m.face((lip[k], lip[j], up_j, up_k), V((0, 0, -1)), "wood_bark")
        else:
            m.face((lo[k], lo[j], top), out, "wood_mid")
            m.face((lip[k], lip[j], top), V((0, 0, -1)), "wood_bark")
        m.face((lip[k], lip[j], lo[j], lo[k]), V((out.x, out.y, -0.2)), "wood_dark")


def bld_den_roof(coll, rnd):
    m = DenMesh()
    angles = roof_angles(rnd)
    for i, (r0, z0, r1, z1) in enumerate(TIERS):
        tier(m, angles, r0, z0, r1, z1, rnd, wobble=0.012 if i == 0 else 0.0)
    # stovepipe from the wall top (stove inside) up through the roof, a kink, a pot-lid hat
    st = V((0.52, CY, 0.0))
    m.cyl(st + V((0, 0, 0.72)), 0.032, 0.25, "rust", segs=6)
    k0, k1 = st + V((0, 0, 0.84)), st + V((-0.06, 0.04, 0.93))
    m.beam(k0, k1, 0.06, "rust_dark")
    m.cyl(k1 + V((0, 0, 0.03)), 0.075, 0.025, "iron_dark", segs=8, r2=0.03)
    return m.obj("bld_den_2x2_roof", coll)


def check_clipping(den, roof):
    """QA: (1) nothing that should stand clear of the wall (furniture, beds, shield, rocks, shutters...) has a vertex
    inside the stone band, outside the door / window openings; (2) nothing of the den -- wall tops included -- pokes up
    into the roof slab (a ray straight up from it would hit the roof's top surface from inside). Returns the problems."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(den.data)
    kl = bm.faces.layers.int["kind"]
    kind = {}
    for f in bm.faces:
        for v in f.verts:
            kind[v] = min(kind.get(v, 9), f[kl]) if f[kl] != DenMesh.FREE else kind.get(v, DenMesh.FREE)
    rb = bmesh.new()
    rb.from_mesh(roof.data)
    rtree = BVHTree.FromBMesh(rb)
    problems = []
    top = sum(COURSES)
    for v, k in kind.items():
        p = v.co
        if k == DenMesh.FREE and p.z < top - 1e-3:
            a = math.atan2(p.y - CY, p.x)
            r = math.hypot(p.x, p.y - CY)
            c = min(int(next((i for i in range(len(COURSES)) if p.z < course_z(i)[1]), len(COURSES) - 1)), 4)
            opening = any(abs(math.degrees(_norm(a, math.radians(ac))) - ac) <= hw + 0.5 and c0 <= c <= c1
                          for ac, hw, c0, c1 in OPENINGS)
            lo, hi = R(a) - 0.015 * c - THICK - 0.013, R(a) - 0.015 * c + 0.013
            if not opening and lo < r < hi:
                problems.append(("in wall", tuple(round(x, 3) for x in p)))
        if p.z > 0.45:
            h = rtree.ray_cast(p + V((0, 0, 1e-4)), V((0, 0, 1)))
            if h[0] is not None and h[1].z > 0.05 and (h[0] - p).length < 0.5:
                problems.append(("in roof", tuple(round(x, 3) for x in p)))
    # (3) each tier's top edge stays under the tier above: a ray straight up from it must meet that tier's underside
    for v in rb.verts:
        for r0, z0, r1, z1 in TIERS[:-1]:
            if abs(v.co.z - z1) < 1e-4:
                h = rtree.ray_cast(v.co + V((0, 0, 1e-4)), V((0, 0, 1)))
                if h[0] is None or h[1].z > 0 or (h[0] - v.co).length < 0.012:
                    problems.append(("roof tier pokes through", tuple(round(x, 3) for x in v.co)))
    bm.free()
    rb.free()
    return problems


STOVE = V((0.52, CY + 0.0, 0.0))
LANTERN = None                                        # set by den_parts (computed from the lantern post)
SMOKE_FROM = V((0.46, CY + 0.04, 0.99))               # just over the stovepipe's pot-lid hat
FRAMES = 72                                           # = the raccoons' sleep loop: breathing and the room in step


def den_parts(coll, den, roof):
    """The moving parts: the stove's fire glow, the candle flame, the lantern glow (den), three smoke puffs (roof:
    hiding the roof hides its smoke too)."""
    import anim_kit as A
    parts = {}
    m = DenMesh()
    m.obox(STOVE + V((-0.098, 0, 0.12)), (0.006, 0.07, 0.05), "torch_orange")
    m.obox(STOVE + V((-0.1, 0, 0.115)), (0.004, 0.045, 0.028), "flame_yellow")
    parts["pr_stove_glow"] = A.part(m.obj("pr_stove_glow", coll), den, STOVE + V((-0.098, 0, 0.095)))
    m = DenMesh()
    m.obox(V((0.2, CY - 0.33, 0.209)), (0.011, 0.011, 0.018), "flame_yellow")
    parts["pr_candle_flame"] = A.part(m.obj("pr_candle_flame", coll), den, V((0.2, CY - 0.33, 0.2)))
    lp, lout, lal, la = frame_at(-62, 0.1)
    lc = lp + V((0, 0, 0.475)) - lal * 0.11
    m = DenMesh()
    m.obox(lc, (0.055, 0.055, 0.075), "flame_yellow")
    parts["pr_lantern_glow"] = A.part(m.obj("pr_lantern_glow", coll), den, lc)
    for i in range(3):
        m = DenMesh()
        m.blob(SMOKE_FROM, V((0.03, 0.03, 0.026)), "stone_frost", 6, 3)
        parts[f"pr_smoke_{i + 1}"] = A.part(m.obj(f"pr_smoke_{i + 1}", coll), roof, SMOKE_FROM)
    return parts


def den_clips(parts):
    """idle: smoke puffs drift up, the stove fire and the candle flicker, the lantern glows.
    work (someone asleep): the candle is out, the stove has burned low, the smoke comes slower and thinner."""
    import anim_kit as A

    def common(p, slow):
        pose = {}
        for i in range(3):
            u = (p * (2 if not slow else 1) + i / 3) % 1.0                   # each puff: rise, swell, thin out
            rise = V((0.05 * u + 0.012 * math.sin(TAU * (u + i * 0.3)), 0.03 * u, 0.32 * u))
            sz = (0.6 + 1.6 * u) * (1 - smooth_end(u)) * (0.7 if slow else 1.0)
            pose[f"pr_smoke_{i + 1}"] = (rise, None, max(sz, 0.001))
        return pose

    def idle(p):
        pose = common(p, False)
        fl = 1 + 0.18 * math.sin(TAU * 7 * p) + 0.1 * math.sin(TAU * 13 * p + 1)
        pose["pr_stove_glow"] = (None, None, (1, 1, fl))
        pose["pr_candle_flame"] = (None, A.q((1, 0.5, 0), 8 * math.sin(TAU * 5 * p)),
                                   (1, 1, 1 + 0.25 * math.sin(TAU * 9 * p)))
        pose["pr_lantern_glow"] = (None, None, 1 + 0.03 * math.sin(TAU * 6 * p))
        return pose

    def work(p):
        pose = common(p, True)
        pose["pr_stove_glow"] = (None, None, (1, 1, 0.45 + 0.06 * math.sin(TAU * 2 * p)))   # banked low
        pose["pr_candle_flame"] = A.hidden()                                              # snuffed
        pose["pr_lantern_glow"] = (None, None, 1 + 0.03 * math.sin(TAU * 6 * p))
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def smooth_end(u):
    t = min(max((u - 0.75) / 0.25, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def sleep_spots(den):
    """spot_sleep_1 / _2 (the adults' beds) and spot_sleep_3 (the kit's), on the blankets, facing the front."""
    import anim_kit as A
    return [A.spot(den, f"spot_sleep_{i + 1}", bed_spot(c, variant), (0, -1, 0)) for i, (c, bl, variant) in enumerate(BEDS)]


def build(coll, rnd=None):
    rnd = rnd or random.Random(21)
    import build_props_blockout as PR
    den = bld_den_2x2(coll, rnd)
    PR.trim_below_floor(den)              # rocks / logs dip under z 0: flatten onto the floor, drop unseen bottoms
    roof = bld_den_roof(coll, rnd)
    roof.parent = den                                    # rides along in the same .glb as its own node
    return den, roof


def main():
    do_renders = "--no-renders" not in sys.argv
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    den, roof = build(bpy.data.collections["Assets"])
    parts = den_parts(bpy.data.collections["Assets"], den, roof)
    spots = sleep_spots(den)
    den_clips(parts)
    for ob in (den, roof):
        ok, bb = B.check_bounds(ob, 2, 2, 1)
        print(f"STAT {ob.name}: {K.tris(ob)} tris, inside footprint: {ok} {bb}")
    print(f"STAT total: {K.tris(den) + K.tris(roof) + sum(K.tris(o) for o in parts.values())} tris")
    probs = check_clipping(den, roof)
    print(f"STAT clipping problems: {len(probs)}")
    for pr in probs[:30]:
        print("  CLIP", *pr)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "den.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
    # ---- QA: the den's own parts and loops, and the family asleep in the nests (work = someone asleep)
    import anim_kit as A
    crew = []
    for sp, (variant, blend) in zip(spots, (("chr_raccoon", "chr_raccoon_animated.blend"),
                                            ("chr_raccoon", "chr_raccoon_animated.blend"),
                                            ("chr_raccoon_kit", "chr_raccoon_animated_kit.blend"))):
        rig, mesh, _ = A.raccoon_at(sp, variant=variant, blend=blend, clip="sleep")
        crew.append((rig, mesh, None, "work", {}))
    smoke = [f"pr_smoke_{i}" for i in (1, 2, 3)]
    allow = [("pr_stove_glow", "bld_den_2x2"), ("pr_candle_flame", "bld_den_2x2"), ("pr_lantern_glow", "bld_den_2x2")] + \
            [(a, b) for a in smoke for b in smoke if a != b] + [(sm, "bld_den_2x2_roof") for sm in smoke]
    probs = A.check(den, 2, 2, H=1.0, crew=crew, allow=allow, sky=smoke)
    A.report("bld_den_2x2", probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        objs = [o for c in crew for o in c[:2]]
        A.render_loops(den, objs, ROOT / "renders" / "bld_den_loops.gif", target=(0.0, 0.05, 0.3), dist=3.4,
                       pitch=45, idle_frames=36, grid_n=4, hide_in_work=[roof] + [parts[f"pr_smoke_{i}"] for i in (1, 2, 3)])
        for o in objs:
            bpy.data.objects.remove(o)
        renders(den, roof)


def sleeper(blend, name, loc, rot, frame=36):
    """A posed (sleeping) raccoon from an animated character file, as a reference object."""
    with bpy.data.libraries.load(str(ROOT / blend)) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith(name)]
    ref = bpy.data.collections["Reference"]
    rig = next(o for o in dst.objects if o.type == "ARMATURE")
    for o in dst.objects:
        ref.objects.link(o)
    rig.location, rig.rotation_euler = loc, (0, 0, rot)
    tr = rig.animation_data.nla_tracks
    act = next(t.strips[0].action for t in tr if t.name.startswith("sleep"))
    for t in tr:
        t.mute = True
    rig.animation_data.action = act
    return rig, act, frame


def renders(den, roof):
    from PIL import Image, ImageDraw, ImageFont
    sc = bpy.context.scene
    ref = bpy.data.collections["Reference"]
    import build_template
    build_template.grid(ref, n=7)
    for o in (den, roof):
        o.location = (0.5, 0.5, 0) if o is den else o.location
    # the family asleep: two adults and a kit, plus one awake by the door
    s0, s2 = bed_spot(BEDS[0][0], "chr_raccoon"), bed_spot(BEDS[2][0], "chr_raccoon_kit")
    sl = [sleeper("chr_raccoon_animated.blend", "chr_raccoon", (0.5 + s0.x, 0.5 + s0.y, s0.z), 0.0),
          sleeper("chr_raccoon_animated_kit.blend", "chr_raccoon_kit", (0.5 + s2.x, 0.5 + s2.y, s2.z), 0.0)]
    for rig, act, f in sl:
        rig.animation_data.action = act
    sc.frame_set(36)
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_blockout.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rac = dst.objects[0]
    rac.name = "ref_raccoon_door"
    ref.objects.link(rac)
    rac.location, rac.rotation_euler.z = (0.5 + 0.38, 0.5 - 0.95, 0), 0.5
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 40
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    gc = bpy.data.objects["GameCam"]
    shots = []

    def shoot(name, tgt, yaw, dist, pitch=50, res=(1100, 800)):
        K.look(gc, tgt, yaw, dist, pitch_deg=pitch)
        K.shoot(gc, out / f"bld_den_{name}.png", res)
        shots.append((name, out / f"bld_den_{name}.png"))
    shoot("gamecam", (0.5, 0.45, 0.35), -30, 4.6)
    shoot("front", (0.5, 0.4, 0.35), 15, 3.2, pitch=24)
    roof.hide_render = True
    shoot("cutaway", (0.5, 0.5, 0.2), -30, 4.0)
    shoot("inside", (0.5, 0.55, 0.15), 160, 2.9, pitch=58)
    roof.hide_render = False
    # cave mood: the stove and the candle light the inside, glow leaks out of the door and windows
    sun = bpy.data.objects["Sun"]
    sun.data.energy, sun.data.color = 0.35, (0.6, 0.72, 1.0)
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.03, 0.045, 0.09, 1), 1.0
    for nm, loc, e in (("stove", (0.5 + 0.38, 0.5 + CY, 0.2), 14), ("candle", (0.5 + 0.2, 0.5 + CY - 0.33, 0.28), 4),
                       ("lantern", None, 6)):
        if loc is None:
            lp, lout, lal, _ = frame_at(-62, 0.1)
            loc = tuple(lp + V((0.5, 0.5, 0.47)) - lal * 0.11 + lout * 0.08)
        L = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "POINT"))
        sc.collection.objects.link(L)
        L.location, L.data.energy, L.data.color, L.data.shadow_soft_size = loc, e, (1.0, 0.6, 0.28), 0.05
    shoot("mood", (0.5, 0.45, 0.35), -30, 4.6)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    sheet = Image.new("RGB", (1100 * 2, 800 * 3), (24, 26, 32))
    for i, (nm, f) in enumerate(shots):
        im = Image.open(f).convert("RGB")
        ImageDraw.Draw(im).text((16, 12), nm, font=font, fill=(240, 240, 245))
        sheet.paste(im, ((i % 2) * 1100, (i // 2) * 800))
    sheet.save(out / "bld_den_sheet.png")


if __name__ == "__main__":
    main()
