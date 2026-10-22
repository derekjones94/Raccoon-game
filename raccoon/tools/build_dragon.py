"""chr_dragon: a huge red dragon asleep, curled round its hoard. 6 x 4 cells, 2 cells tall.

Modelled in the sleeping pose (that's the rest pose). The body is one lofted tube along a curl path (neck -> torso ->
tail); head, horns, legs, folded wings and the spine ridge are separate volumes. The hoard is its own static mesh in
the same .glb (chr_dragon_hoard) so the game can swap / shrink it as raccoons steal from it.
Front (-Y in Blender = +Z in Godot) is where the head rests.

Rig: root, spine, chest, hips, neck_3/2/1, head, jaw, eyelid_L/R, tail_1..6, wing_L/R, fore_L/R, hind_L/R.
Body skin follows distance ALONG the body (not straight-line distance), so the tail tip lying next to the snout never
gets pulled by the head.
Actions (24 fps): idle (4 s breathing loop), stir (6 s one-shot: inhale, neck lifts, eyes open, look round, snort,
eyes close, settle -- starts and ends on the rest pose so it blends back into idle).

Run:  python3 tools/build_dragon.py
Out:  chr_dragon.blend, export/chr_dragon.glb, renders/dragon_*.png/gif
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_props_blockout as PR  # noqa: E402
from build_raccoon_anims import pose_quats  # noqa: E402

ROOT = P.ROOT
V = Vector
W, D, H = 6, 4, 2
FPS = 24
GROUPS = ["body", "head", "jaw", "eyelid_L", "eyelid_R", "wing_L", "wing_R", "fore_L", "fore_R", "hind_L", "hind_R"]

# curl path from the back of the head (s = 0) to the tail tip (s = 1): x, y, z(centre), radius
PATH = [(-0.95, -1.15, 0.36, 0.30), (-1.75, -1.05, 0.40, 0.36), (-2.33, -0.45, 0.46, 0.42), (-2.28, 0.45, 0.54, 0.52),
        (-1.60, 1.04, 0.62, 0.62), (-0.40, 1.20, 0.66, 0.66), (0.85, 1.10, 0.62, 0.62), (1.95, 0.60, 0.48, 0.46),
        (2.43, -0.30, 0.35, 0.34), (2.05, -1.22, 0.26, 0.25), (1.05, -1.60, 0.19, 0.18), (0.20, -1.66, 0.13, 0.12),
        (-0.25, -1.56, 0.08, 0.05)]
S_BONES = [  # body chain bones by arc position along the path (s), parents first
    ("spine", 0.42, 0.55, "root"), ("chest", 0.42, 0.30, "spine"), ("hips", 0.55, 0.66, "spine"),
    ("neck_3", 0.30, 0.20, "chest"), ("neck_2", 0.20, 0.10, "neck_3"), ("neck_1", 0.10, 0.0, "neck_2"),
] + [(f"tail_{i + 1}", 0.66 + 0.34 * i / 6, 0.66 + 0.34 * (i + 1) / 6, "hips" if i == 0 else f"tail_{i}") for i in range(6)]


def catmull(pts, n):
    """Sample a Catmull-Rom spline through pts (tuples of 4) at n points; returns list of (pos, radius)."""
    P4 = [V(p) for p in pts]
    P4 = [P4[0] * 2 - P4[1]] + P4 + [P4[-1] * 2 - P4[-2]]
    out = []
    segs = len(pts) - 1
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = P4[k], P4[k + 1], P4[k + 2], P4[k + 3]
        q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
        out.append((V((q.x, q.y, q.z)), q.w))
    return out


class Path3:
    """The sampled body curve with arc-length parameter s and a frame (tangent / side / up) per sample."""

    def __init__(self, n=56):
        self.samples = catmull(PATH, n)
        L = [0.0]
        for (a, _), (b, _) in zip(self.samples, self.samples[1:]):
            L.append(L[-1] + (b - a).length)
        self.s = [x / L[-1] for x in L]
        self.length = L[-1]

    def at(self, s):
        """Position, radius, tangent (toward the tail), side, up at arc parameter s."""
        s = min(max(s, 0.0), 1.0)
        for i in range(len(self.s) - 1):
            if self.s[i + 1] >= s:
                break
        t = (s - self.s[i]) / max(self.s[i + 1] - self.s[i], 1e-9)
        (a, ra), (b, rb) = self.samples[i], self.samples[i + 1]
        p, r = a.lerp(b, t), ra + (rb - ra) * t
        tan = (b - a).normalized()
        side = tan.cross(V((0, 0, 1))).normalized()          # right of the direction of travel
        up = side.cross(tan).normalized()
        return p, r, tan, side, up


class DM(B.M):
    """Building mesh helpers + per-face body-part group + per-vertex body position s."""

    def __init__(self):
        super().__init__()
        self.grp = self.bm.faces.layers.int.new("grp")
        self.sv = self.bm.verts.layers.float.new("s")
        self.cur, self.cur_s = 0, 0.0

    def part(self, name, s=0.0):
        self.cur, self.cur_s = GROUPS.index(name), s
        return self

    def tag(self, faces, swatch):
        super().tag(faces, swatch)
        for f in faces:
            f[self.grp] = self.cur
            for v in f.verts:
                v[self.sv] = self.cur_s


def oriented_blob(m, c, r, fwd, swatch, segs=10, rings=6, pitch=0.0):
    """Ellipsoid with its X axis along fwd (horizontal heading) and an optional nose-down pitch."""
    yaw = math.atan2(fwd.y, fwd.x)
    res = bmesh.ops.create_uvsphere(m.bm, u_segments=segs, v_segments=rings, radius=1.0)
    T = Matrix.Translation(c) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(pitch, 4, "Y") @ Matrix.Diagonal((*r, 1))
    bmesh.ops.transform(m.bm, matrix=T, verts=res["verts"])
    m.tag({f for v in res["verts"] for f in v.link_faces}, swatch)


def horn(m, base, d, r, length, swatch="bone", segs=6):
    res = bmesh.ops.create_cone(m.bm, cap_ends=True, segments=segs, radius1=r, radius2=r * 0.08, depth=length)
    q = V((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(m.bm, matrix=Matrix.Translation(base) @ q @ Matrix.Translation((0, 0, length / 2)), verts=res["verts"])
    m.tag({f for v in res["verts"] for f in v.link_faces}, swatch)


# ---------------------------------------------------------------- dragon mesh
HEAD_C = V((-0.52, -1.22, 0.30))
HEAD_F = V((1.0, -0.12, 0.0)).normalized()                    # heading of the snout (toward the hoard / front right)
HEAD_SIDE = V((0, 0, 1)).cross(HEAD_F).normalized()            # head's left


def build_dragon(coll, path):
    m = DM()
    # ---- body tube: elliptical rings, darker back stripe, pale belly plates underneath / on the inner side
    segs = 12
    rings = []
    for i, (p, r) in enumerate(path.samples):
        s = path.s[i]
        _, _, tan, side, up = path.at(s)
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            off = side * math.cos(a) * r + up * math.sin(a) * r * 0.86
            v = m.bm.verts.new(p + off)
            v[m.sv] = s
            ring.append((v, math.sin(a)))
        rings.append(ring)
    m.part("body")
    for i in range(len(rings) - 1):
        for k in range(segs):
            j = (k + 1) % segs
            (a, ua), (b, ub) = rings[i][k], rings[i][j]
            c, d = rings[i + 1][j][0], rings[i + 1][k][0]
            f = m.bm.faces.new((a, b, c, d))
            u = (ua + ub) / 2
            sw = "dragon_dark" if u > 0.8 else ("bone" if u < -0.45 else "dragon_red")
            f[m.sw] = B.NAMES.index(sw)
            f[m.grp] = 0
    f = m.bm.faces.new([v for v, _ in reversed(rings[-1])])          # tail tip cap
    f[m.sw], f[m.grp] = B.NAMES.index("dragon_dark"), 0
    f = m.bm.faces.new([v for v, _ in rings[0]])                     # neck end (inside the head)
    f[m.sw], f[m.grp] = B.NAMES.index("dragon_red"), 0
    # ---- spine ridge: spikes from the neck to the end of the tail, shrinking toward both ends
    k = 0
    s = 0.04
    while s < 0.93:
        p, r, tan, side, up = path.at(s)
        size = r * (0.55 if 0.25 < s < 0.7 else 0.45)
        m.part("body", s)
        horn(m, p + up * r * 0.78, up * 0.85 - tan * 0.5, size * 0.4, size, "dragon_dark" if k % 2 else "dragon_light", 4)
        s += 0.035 + 0.02 * (r < 0.3)
        k += 1
    # ---- head (resting on the floor, eyes shut)
    c, f, sd = HEAD_C, HEAD_F, HEAD_SIDE
    m.part("head", 0.0)
    oriented_blob(m, c, V((0.36, 0.3, 0.25)), f, "dragon_red", 12, 7)                              # cranium
    oriented_blob(m, c + f * 0.42 + V((0, 0, -0.03)), V((0.38, 0.22, 0.16)), f, "dragon_red", 12, 6, pitch=0.08)  # snout
    oriented_blob(m, c + f * 0.42 + V((0, 0, 0.09)), V((0.3, 0.12, 0.06)), f, "dragon_dark", 8, 4)   # snout ridge
    for sx in (1, -1):
        oriented_blob(m, c + f * 0.74 + sd * sx * 0.08 + V((0, 0, 0.06)), V((0.035, 0.03, 0.025)), f, "dragon_dark", 6, 3)  # nostrils
        oriented_blob(m, c + f * 0.1 + sd * sx * 0.2 + V((0, 0, 0.16)), V((0.16, 0.07, 0.05)), f, "dragon_dark", 8, 4)      # brow
        horn(m, c - f * 0.12 + sd * sx * 0.17 + V((0, 0, 0.17)), -f * 0.8 + V((0, 0, 0.45)) + sd * sx * 0.25, 0.08, 0.5)  # horns
        horn(m, c - f * 0.05 + sd * sx * 0.27 + V((0, 0, -0.02)), -f * 0.7 + sd * sx * 0.6, 0.06, 0.26, "dragon_dark", 4)  # cheek frills
        oriented_blob(m, c + f * 0.12 + sd * sx * 0.245 + V((0, 0, 0.07)), V((0.07, 0.04, 0.06)), f, "flame_yellow", 8, 4)  # eye (glows)
        m.part("eyelid_L" if sx > 0 else "eyelid_R", 0.0)
        oriented_blob(m, c + f * 0.12 + sd * sx * 0.255 + V((0, 0, 0.075)), V((0.085, 0.05, 0.075)), f, "dragon_red", 8, 5)  # shut lid
        m.part("head", 0.0)
    for t in (0.55, 0.68):                                                                          # teeth peeking out
        for sx in (1, -1):
            horn(m, c + f * t + sd * sx * 0.17 + V((0, 0, -0.1)), V((0, 0, -1)), 0.022, 0.06, "bone", 4)
    m.part("jaw", 0.0)
    oriented_blob(m, c + f * 0.36 + V((0, 0, -0.15)), V((0.38, 0.2, 0.08)), f, "dragon_light", 10, 5, pitch=0.05)  # jaw
    # ---- legs: thigh + paw + claws, tucked along the body
    def leg(name, s, side_sign, fwd_sign, size):
        p, r, tan, side, up = path.at(s)
        m.part(name, s)
        out = side * side_sign
        thigh = p + out * r * 0.65 + V((0, 0, -r * 0.25))
        oriented_blob(m, thigh, V((size * 0.5, size * 0.36, size * 0.42)), tan, "dragon_red", 10, 6)
        paw = V((thigh.x, thigh.y, 0)) + out * size * 0.25 + tan * fwd_sign * size * 0.45 + V((0, 0, size * 0.12))
        oriented_blob(m, paw, V((size * 0.32, size * 0.22, size * 0.13)), tan * fwd_sign, "dragon_dark", 8, 5)
        for cl in (-1, 0, 1):
            cb = paw + tan * fwd_sign * size * 0.28 + out.cross(V((0, 0, 1))).normalized() * cl * size * 0.12
            horn(m, cb, tan * fwd_sign + V((0, 0, -0.35)), size * 0.05, size * 0.16, "bone", 4)
    leg("fore_L", 0.36, -1, -1, 0.62)       # outer side (away from the hoard)
    leg("fore_R", 0.36, 1, -1, 0.55)        # inner side
    leg("hind_L", 0.6, -1, 1, 0.7)
    leg("hind_R", 0.6, 1, 1, 0.62)
    # ---- folded wings on the back: a bony arm + membrane panel per side, both sides of the panel faced
    def wing(name, side_sign):
        p0, r0, tan0, side0, up0 = path.at(0.37)
        p1, r1, tan1, side1, up1 = path.at(0.62)
        out = side0 * side_sign
        sh = p0 + up0 * r0 * 0.75 + out * r0 * 0.35
        elbow = sh + tan0 * 0.75 + V((0, 0, 0.3)) + out * 0.18
        tip = p1 + up1 * r1 * 0.5 + tan1 * 0.55 + out * r1 * 0.7 + V((0, 0, 0.08))
        trail = [p1 + up1 * r1 * 0.2 + out * r1 * 0.95, path.at(0.5)[0] + out * path.at(0.5)[1] * 0.95,
                 p0 + out * r0 * 0.95 + tan0 * 0.2]
        m.part(name, 0.37)
        m.beam(sh, elbow, 0.08, "dragon_red")
        m.beam(elbow, tip, 0.06, "dragon_red")
        horn(m, elbow, (elbow - sh).normalized() * 0.3 + V((0, 0, 1)), 0.05, 0.18, "bone", 4)       # wing thumb claw
        outline = [sh, elbow, tip] + trail
        for flip in (False, True):
            vs = [m.bm.verts.new(q + out * (0.012 if flip else -0.012)) for q in outline]
            for i in range(1, len(vs) - 1):                                                       # fan triangles
                tri = (vs[0], vs[i], vs[i + 1]) if not flip else (vs[0], vs[i + 1], vs[i])
                fc = m.bm.faces.new(tri)
                fc[m.sw], fc[m.grp] = B.NAMES.index("dragon_dark"), m.cur
                for v in tri:
                    v[m.sv] = 0.37
        return sh, tip
    wl = wing("wing_L", -1)
    wr = wing("wing_R", 1)
    bmesh.ops.recalc_face_normals(m.bm, faces=[f for f in m.bm.faces if f[m.grp] != GROUPS.index("wing_L")
                                                and f[m.grp] != GROUPS.index("wing_R")])
    me = bpy.data.meshes.new("chr_dragon_mesh")
    ids = [f[m.sw] for f in m.bm.faces]
    m.bm.to_mesh(me)
    m.bm.free()
    ob = bpy.data.objects.new("chr_dragon_mesh", me)
    coll.objects.link(ob)
    me.materials.append(bpy.data.materials["M_Palette"])
    for i, sid in enumerate(ids):
        P.set_swatch(ob, B.NAMES[sid], [i])
    return ob, {"wing_L": wl, "wing_R": wr}


def build_hoard(coll, rnd):
    m = B.M()
    c = V((0.05, -0.15, 0.0))
    m.blob(c, V((1.75, 1.0, 0.4)), "gold", 16, 8)
    for off, r in (((-0.5, 0.15), (0.6, 0.45, 0.42)), ((0.6, -0.1), (0.55, 0.4, 0.38)), ((0.05, 0.25), (0.45, 0.35, 0.5))):
        m.blob(c + V((*off, 0)), V(r), "gold_light", 10, 6)
    for k in range(26):                                                     # coins spilled round the edge
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.9, 1.15)
        PR.coin(m, c + V((math.cos(a) * 1.75 * rr, math.sin(a) * 1.0 * rr, 0.007)), r=0.05)
    for k, sw in enumerate(("ruby", "sapphire", "emerald", "amethyst", "ruby", "emerald", "sapphire", "amethyst")):
        a = k / 8 * 2 * math.pi + 0.3
        p = c + V((math.cos(a) * 1.1, math.sin(a) * 0.55, 0))
        p.z = 0.4 * math.sqrt(max(0.0, 1 - (math.cos(a) * 1.1 / 1.75) ** 2 - (math.sin(a) * 0.55 / 1.0) ** 2)) + 0.03
        PR.gem(m, p, 0.06, sw, rot=rnd.uniform(0, 1))
    cr = c + V((0.1, 0.2, 0.5))                                             # crown on the summit
    m.cyl(cr + V((0, 0, 0.05)), 0.12, 0.1, "gold_dark", segs=10)
    for i in range(6):
        a = i / 6 * 2 * math.pi
        m.cyl(cr + V((math.cos(a) * 0.11, math.sin(a) * 0.11, 0.14)), 0.03, 0.09, "gold_light", segs=4, r2=0.0)
    PR.gem(m, cr + V((0, -0.12, 0.06)), 0.03, "ruby")
    sw_base = c + V((-0.75, -0.2, 0.3))                                     # a sword stuck in the gold
    m.beam(sw_base, sw_base + V((0.05, -0.04, 0.55)), 0.05, "iron_light")
    m.beam(sw_base + V((-0.12, -0.04, 0.5)), sw_base + V((0.17, -0.02, 0.52)), 0.04, "gold")
    m.beam(sw_base + V((0.05, -0.04, 0.55)), sw_base + V((0.06, -0.05, 0.68)), 0.035, "leather")
    for gx, gy in ((0.85, -0.55), (-1.2, -0.5), (0.5, 0.55)):               # goblets
        g = c + V((gx, gy, 0.0))
        m.cyl(g + V((0, 0, 0.02)), 0.07, 0.04, "gold_dark", segs=8)
        m.cyl(g + V((0, 0, 0.1)), 0.02, 0.12, "gold", segs=6)
        m.cyl(g + V((0, 0, 0.2)), 0.05, 0.1, "silver" if gx > 0 else "gold", r2=0.08, segs=8)
    ch = c + V((1.25, 0.35, 0.0))                                           # an open chest on the edge
    m.obox(ch + V((0, 0, 0.13)), (0.42, 0.28, 0.26), "wood_mid", rot=(0, 0, 0.4), top="gold_light")
    m.obox(ch + V((0.06, 0.15, 0.36)), (0.42, 0.05, 0.22), "wood_dark", rot=(-0.4, 0, 0.4))
    m.cyl(c + V((-1.3, 0.3, 0.2)), 0.26, 0.04, "iron_light", cap="cloth_red", axis=(0.3, -0.2, 1), segs=12)   # a shield
    ob = m.obj("chr_dragon_hoard", coll)
    PR.trim_below_floor(ob)
    return ob


# ---------------------------------------------------------------- rig + skin
def build_rig(coll, path, wings):
    arm = bpy.data.armatures.new("chr_dragon_rig")
    rig = bpy.data.objects.new("chr_dragon", arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    segs = {}

    def bone(name, h, t, parent):
        b = eb.new(name)
        b.head, b.tail = V(h), V(t)
        b.roll = 0.0
        if parent:
            b.parent = eb[parent]
        segs[name] = (V(h), V(t))
    bone("root", (0, 0, 0), (0, 0.5, 0), None)
    for name, s0, s1, par in S_BONES:
        bone(name, path.at(s0)[0], path.at(s1)[0], par)
    neck_end = path.at(0.0)[0]
    bone("head", neck_end, HEAD_C + HEAD_F * 0.75, "neck_1")
    bone("jaw", HEAD_C - HEAD_F * 0.05 + V((0, 0, -0.1)), HEAD_C + HEAD_F * 0.72 + V((0, 0, -0.16)), "head")
    for sx, nm in ((1, "eyelid_L"), (-1, "eyelid_R")):
        e = HEAD_C + HEAD_F * 0.12 + HEAD_SIDE * sx * 0.255 + V((0, 0, 0.075))
        bone(nm, e - HEAD_F * 0.05, e + HEAD_F * 0.1, "head")
    for nm, (sh, tip) in wings.items():
        bone(nm, sh, tip, "chest")
    for nm, s, sign, par in (("fore_L", 0.36, -1, "chest"), ("fore_R", 0.36, 1, "chest"), ("hind_L", 0.6, -1, "hips"),
                             ("hind_R", 0.6, 1, "hips")):
        p, r, tan, side, up = path.at(s)
        top = p + side * sign * r * 0.6
        bone(nm, top, V((top.x, top.y, 0.05)) + side * sign * 0.15, par)
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig, segs


def skin(ob, rig):
    me = ob.data
    grp = me.attributes["grp"].data
    sval = me.attributes["s"].data
    vgrp = {}
    for poly in me.polygons:
        for vi in poly.vertices:
            vgrp.setdefault(vi, GROUPS[grp[poly.index].value])
    for b in rig.data.bones:
        ob.vertex_groups.new(name=b.name)
    chain = sorted(((min(s0, s1), max(s0, s1), n) for n, s0, s1, _ in S_BONES), key=lambda x: x[0])
    blend = 0.035
    for v in me.vertices:
        g = vgrp.get(v.index, "body")
        if g != "body":
            ob.vertex_groups[g].add([v.index], 1.0, "REPLACE")
            continue
        s = sval[v.index].value
        ws = []
        for a, b, n in chain:                      # tent weights that cross-fade over +-blend at each joint
            w = min(s - a, b - s) / blend + 0.5
            if a == 0.0:
                w = max(w, 0.5 + (b - s) / blend if s <= b else w)
            if b == 1.0 or b >= 0.999:
                w = max(w, 0.5 + (s - a) / blend if s >= a else w)
            w = min(max(w, 0.0), 1.0)
            if w > 0:
                ws.append((w, n))
        tot = sum(w for w, _ in ws) or 1.0
        for w, n in ws:
            ob.vertex_groups[n].add([v.index], w / tot, "REPLACE")
    ob.parent = rig
    mod = ob.modifiers.new("rig", "ARMATURE")
    mod.object = rig


# ---------------------------------------------------------------- animation
def ss(t, a, b):
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lift_axis(rig, name):
    b = rig.data.bones[name]
    d = (b.tail_local - b.head_local).normalized()
    a = d.cross(V((0, 0, 1)))
    return tuple(a.normalized()) if a.length > 1e-4 else (1, 0, 0)


def roll_axis(rig, name):
    b = rig.data.bones[name]
    return tuple((b.tail_local - b.head_local).normalized())


def anim_idle(rig, p):
    b = 0.5 - 0.5 * math.cos(2 * math.pi * p)          # 0 -> 1 (full breath) -> 0
    rots = {
        "neck_2": [(lift_axis(rig, "neck_2"), 1.2 * b)], "neck_1": [(lift_axis(rig, "neck_1"), 1.5 * b)],
        "head": [(lift_axis(rig, "head"), -1.0 * b)],
        "wing_L": [(roll_axis(rig, "wing_L"), 3 * b)], "wing_R": [(roll_axis(rig, "wing_R"), -3 * b)],
        "tail_5": [((0, 0, 1), 3 * math.sin(2 * math.pi * p))], "tail_6": [((0, 0, 1), 6 * math.sin(2 * math.pi * p))],
    }
    scale = {"chest": 1 + 0.045 * b, "spine": 1 + 0.06 * b, "hips": 1 + 0.03 * b}
    return rots, {}, scale


def anim_stir(rig, p):
    up = ss(p, 0.12, 0.32) * (1 - ss(p, 0.72, 0.97))                # neck raised
    eyes = ss(p, 0.22, 0.3) * (1 - ss(p, 0.7, 0.78))                 # eyelids up
    look = math.sin(2 * math.pi * (p - 0.35) / 0.25) * ss(p, 0.33, 0.38) * (1 - ss(p, 0.57, 0.62))   # look left / right
    snort = math.exp(-((p - 0.64) / 0.025) ** 2)
    breath = ss(p, 0.0, 0.1) * (1 - ss(p, 0.1, 0.3)) + 0.6 * ss(p, 0.85, 0.92) * (1 - ss(p, 0.92, 1.0))
    flick = math.sin(2 * math.pi * (p - 0.38) * 3) * ss(p, 0.38, 0.42) * (1 - ss(p, 0.5, 0.56))
    rots = {
        "neck_3": [(lift_axis(rig, "neck_3"), 2 * up)], "neck_2": [(lift_axis(rig, "neck_2"), 5 * up)],
        "neck_1": [(lift_axis(rig, "neck_1"), 16 * up), ((0, 0, 1), 6 * look)],
        "head": [(lift_axis(rig, "head"), 10 * up - 7 * snort), ((0, 0, 1), 14 * look)],
        "jaw": [(lift_axis(rig, "jaw"), -14 * snort)],
        "wing_L": [(roll_axis(rig, "wing_L"), 10 * up)], "wing_R": [(roll_axis(rig, "wing_R"), -10 * up)],
        "tail_4": [((0, 0, 1), 6 * flick)], "tail_5": [((0, 0, 1), 12 * flick)], "tail_6": [((0, 0, 1), 18 * flick)],
        "fore_R": [(lift_axis(rig, "fore_R"), 4 * up)],
    }
    loc = {"eyelid_L": V((0, 0, 0.075 * eyes)), "eyelid_R": V((0, 0, 0.075 * eyes))}
    scale = {"chest": 1 + 0.07 * breath, "spine": 1 + 0.08 * breath, "hips": 1 + 0.03 * breath}
    return rots, loc, scale


def bake(rig, name, fn, frames, cyclic):
    act = bpy.data.actions.new(name)
    rig.animation_data_create()
    rig.animation_data.action = act
    for f in range(0, frames + 1, 2):
        rots, loc, scale = fn(rig, f / frames)
        qs = pose_quats(rig, rots)
        for pb in rig.pose.bones:
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = qs[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=f)
            Mi = pb.bone.matrix_local.to_3x3().inverted()
            pb.location = Mi @ loc.get(pb.name, V((0, 0, 0)))
            pb.keyframe_insert("location", frame=f)
            k = scale.get(pb.name, 1.0)
            pb.scale = (k, 1.0, k)                       # swell across the bone, not along it
            pb.keyframe_insert("scale", frame=f)
    act.use_frame_range = True
    act.frame_range = (0, frames)
    act.use_cyclic = cyclic
    tr = rig.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    tr.mute = True
    rig.animation_data.action = None


# ---------------------------------------------------------------- main
def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    sc.render.fps = FPS
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    path = Path3()
    body, wings = build_dragon(assets, path)
    PR.trim_below_floor(body)                           # paws / claws / jaw dip under z 0: flatten, drop unseen bottoms
    hoard = build_hoard(assets, random.Random(11))
    rig, segs = build_rig(assets, path, wings)
    skin(body, rig)
    hoard.parent = rig                                   # static: rides with the root, no skin
    for o, nm in ((body, "dragon"), (hoard, "hoard")):
        ok, bb = B.check_bounds(o, W, D, H)
        print(f"STAT chr_{nm}: {tris(o)} tris, inside 6x4x2: {ok} {bb}")
    print(f"STAT bones: {len(rig.data.bones)}")
    bake(rig, "idle", anim_idle, 96, True)
    bake(rig, "stir", anim_stir, 144, False)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "chr_dragon.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
    renders(rig, body, hoard)


def renders(rig, body, hoard):
    from PIL import Image, ImageDraw, ImageFont
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    ref = bpy.data.collections["Reference"]
    import build_template
    build_template.grid(ref, n=13)                       # odd: lines on the half-steps
    rig.location = (0.5, 0.5, 0)                         # 6 x 4 footprint sits on whole cells
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_blockout.blend")) as (src, dst):
        dst.objects = ["chr_raccoon", "chr_raccoon_kit"]
    rac, kit = dst.objects
    for o in (rac, kit):
        ref.objects.link(o)
    rac.location, rac.rotation_euler.z = (0.5 + 0.9, 0.5 - 2.25, 0), 2.6            # a thief tiptoeing up to the hoard
    kit.location, kit.rotation_euler.z = (0.5 + 1.35, 0.5 - 2.4, 0), 2.9
    r2 = rac.copy()
    ref.objects.link(r2)
    r2.location, r2.rotation_euler.z = (0.5 - 3.3, 0.5 - 1.9, 0), -0.6               # a lookout by the head
    gc = bpy.data.objects["GameCam"]
    K.look(gc, (0.5, 0.2, 0.5), -30, 11.0)
    K.shoot(gc, out / "dragon_gamecam.png", (1600, 1100))
    K.look(gc, (0.5 - 1.0, 0.5 - 1.1, 0.4), -20, 4.6, pitch_deg=34)
    K.shoot(gc, out / "dragon_closeup.png", (1400, 1000))
    top = bpy.data.objects["TopCam"]
    top.data.ortho_scale = 8.0
    top.data.clip_end = 100
    top.location = (0.5, 0.5, 30)
    sun = bpy.data.objects["Sun"]
    sun.rotation_euler = (math.radians(15), math.radians(8), math.radians(-35))
    K.shoot(top, out / "dragon_topdown.png", (1200, 900))
    # mood: cool cave, the hoard glowing gold, a lantern-carrying thief
    sun.data.energy, sun.data.color = 0.4, (0.6, 0.72, 1.0)
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.03, 0.045, 0.09, 1), 1.0
    for i, (loc, col, e) in enumerate((((0.55, 0.4, 1.0), (1.0, 0.78, 0.35), 220), ((1.6, -1.6, 0.6), (1.0, 0.62, 0.28), 20))):
        L = bpy.data.objects.new(f"ML{i}", bpy.data.lights.new(f"ML{i}", "POINT"))
        sc.collection.objects.link(L)
        L.location, L.data.color, L.data.energy, L.data.shadow_soft_size = loc, col, e, 0.3
    K.look(gc, (0.5, 0.2, 0.5), -30, 11.0)
    K.shoot(gc, out / "dragon_gamecam_mood.png", (1600, 1100))
    for i in range(2):
        bpy.data.objects[f"ML{i}"].hide_render = True
    sun.data.energy, sun.data.color = 3.0, (1, 1, 1)
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.05, 0.06, 0.09, 1), 1.5
    # animation previews
    for o in (rac, kit, r2):
        o.hide_render = True
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    sc.cycles.samples = 10
    tmp = out / "_dragon"
    tmp.mkdir(exist_ok=True)
    rows = []
    for name, frames, step in (("idle", 96, 4), ("stir", 144, 4)):
        rig.animation_data.action = bpy.data.actions[name]
        imgs = []
        K.look(gc, (0.5 - 0.6, 0.2, 0.5), -25, 8.5, pitch_deg=40)
        for f in range(0, frames + (0 if name == "idle" else 1), step):
            sc.frame_set(f)
            pth = tmp / f"{name}_{f:03d}.png"
            sc.render.resolution_x, sc.render.resolution_y = 640, 440
            sc.render.filepath = str(pth)
            bpy.ops.render.render(write_still=True)
            im = Image.open(pth).convert("RGB")
            ImageDraw.Draw(im).text((10, 416), f"chr_dragon  {name}  frame {f}/{frames}", font=font, fill=(240, 240, 245))
            imgs.append(im)
        imgs[0].save(out / f"dragon_{name}.gif", save_all=True, append_images=imgs[1:], duration=int(1000 * step / FPS), loop=0)
        rows.append((name, [imgs[int(i * (len(imgs) - 1) / 5)] for i in range(6)]))
        for q in tmp.iterdir():
            q.unlink()
    tmp.rmdir()
    rig.animation_data.action = None
    sheet = Image.new("RGB", (6 * 320, len(rows) * 220), (24, 26, 32))
    for r, (name, ims) in enumerate(rows):
        for i, im in enumerate(ims):
            sheet.paste(im.resize((320, 220), Image.LANCZOS), (320 * i, 220 * r))
    sheet.save(out / "dragon_anim_frames.png")


if __name__ == "__main__":
    main()
