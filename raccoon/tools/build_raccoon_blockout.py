"""Batch 3: raccoon blockouts (proportions only): adult, kit (~60%), elder (hunched, grey).

Built from simple flat-shaded volumes, coloured with palette swatches. Faces -Y in Blender (= +Z in glTF/Godot, the
model-front convention). Origin at the feet, bottom-centre.

Run:  python3 tools/build_raccoon_blockout.py
Out:  chr_raccoon_blockout.blend, renders/raccoon_*.png
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402

ROOT = P.ROOT

ADULT = dict(name="chr_raccoon", scale=1.0, head=1.0, hunch=0.0, cane=False,
             fur=("fur_mid", "fur_dark", "fur_charcoal", "fur_light", "fur_cream"))
KIT = dict(name="chr_raccoon_kit", scale=0.6, head=1.12, hunch=0.0, cane=False,
           fur=("fur_mid", "fur_dark", "fur_charcoal", "fur_light", "fur_cream"))
ELDER = dict(name="chr_raccoon_elder", scale=1.0, head=0.97, hunch=26.0, cane=False,   # cane: prop_cane in handslot.r
             fur=("fur_light", "fur_mid", "fur_dark", "fur_cream", "fur_cream"))


GROUPS = ["body", "head", "ear_L", "ear_R", "shoulder_L", "shoulder_R", "arm_L", "arm_R", "thigh_L", "thigh_R",
          "foot_L", "foot_R", "tail", "cane"]      # body part per face: the rig script skins by these


class Parts:
    """Collects volumes; each face remembers its swatch and its body part (self.cur)."""

    def __init__(self):
        self.bm = bmesh.new()
        self.sw = self.bm.faces.layers.int.new("sw")
        self.grp = self.bm.faces.layers.int.new("grp")
        self.cur = 0
        self.names = list(P.SWATCH)

    def part(self, name):
        self.cur = GROUPS.index(name)
        return self

    def _tag(self, verts, swatch):
        for f in {f for v in verts for f in v.link_faces}:
            f[self.sw] = self.names.index(swatch)
            f[self.grp] = self.cur

    def blob(self, c, r, swatch, segs=12, rings=8, M=None):
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=segs, v_segments=rings, radius=1.0)
        T = Matrix.Translation(c) @ (M or Matrix.Identity(4)) @ Matrix.Diagonal((*r, 1))
        bmesh.ops.transform(self.bm, matrix=T, verts=res["verts"])
        self._tag(res["verts"], swatch)
        return res["verts"]

    def cone(self, base, tip_dir, r, length, swatch, segs=7):
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=segs, radius1=r, radius2=r * 0.12, depth=length)
        q = Vector((0, 0, 1)).rotation_difference(Vector(tip_dir).normalized()).to_matrix().to_4x4()
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(base) @ q @ Matrix.Translation((0, 0, length / 2)), verts=res["verts"])
        self._tag(res["verts"], swatch)
        return res["verts"]

    def loft(self, pts, ra, rb, frame, swatch_fn, segs=10):
        """Rings along pts; ring i is an ellipse ra[i] x rb[i] on the axes frame(i, tangent) -> (ua, ub).
        swatch_fn(i, angle) picks the colour of the face between ring i and i+1 at that angle. Ends are capped."""
        rings = []
        for i, p in enumerate(pts):
            d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            ua, ub = frame(i, d)
            rings.append([self.bm.verts.new(p + ua * math.cos(2 * math.pi * k / segs) * ra[i]
                                            + ub * math.sin(2 * math.pi * k / segs) * rb[i]) for k in range(segs)])
        for i in range(len(rings) - 1):
            for k in range(segs):
                j = (k + 1) % segs
                f = self.bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]))
                f[self.sw] = self.names.index(swatch_fn(i, 2 * math.pi * (k + 0.5) / segs))
                f[self.grp] = self.cur
        for ring, i in ((list(reversed(rings[0])), 0), (rings[-1], len(rings) - 2)):
            f = self.bm.faces.new(ring)
            f[self.sw] = self.names.index(swatch_fn(i, -1.0))
            f[self.grp] = self.cur
        return [v for r in rings for v in r]

    def tube(self, pts, radii, swatches, segs=8):
        """Loft rings along pts; swatches per segment (ringed tail)."""
        rings = []
        for k, p in enumerate(pts):
            d = (pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
            a = Vector((1, 0, 0))
            b = d.cross(a).normalized()
            a = b.cross(d).normalized()
            rings.append([self.bm.verts.new(p + (a * math.cos(2 * math.pi * i / segs) + b * math.sin(2 * math.pi * i / segs)) * radii[k])
                          for i in range(segs)])
        for k in range(len(rings) - 1):
            for i in range(segs):
                j = (i + 1) % segs
                f = self.bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
                f[self.sw] = self.names.index(swatches[k % len(swatches)])
                f[self.grp] = self.cur
        for ring, sw in ((rings[0], swatches[0]), (rings[-1], swatches[(len(rings) - 2) % len(swatches)])):
            f = self.bm.faces.new(ring)
            f[self.sw] = self.names.index(sw)
            f[self.grp] = self.cur
        return [v for r in rings for v in r]


ARM_CTRL = [  # (x, y, z, radius) shoulder top -> wrist, left side (x mirrored for the right)
    (0.055, -0.008, 0.214, 0.012), (0.060, -0.010, 0.206, 0.030), (0.064, -0.012, 0.190, 0.037),
    (0.069, -0.020, 0.170, 0.031), (0.073, -0.028, 0.148, 0.027), (0.076, -0.034, 0.130, 0.026),
    (0.079, -0.040, 0.113, 0.023), (0.080, -0.044, 0.104, 0.020),       # wrist
    (0.081, -0.047, 0.094, 0.023), (0.081, -0.050, 0.083, 0.018), (0.081, -0.051, 0.076, 0.005),   # paw, rounded tip
]


def spline(ctrl, n):
    """Catmull-Rom through ctrl = [(Vector, *values)]; returns n samples of (point, values...) (values lerped)."""
    P = [c[0] for c in ctrl]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    segs = len(ctrl) - 1
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
        vals = [a + (b - a) * t for a, b in zip(ctrl[k][1:], ctrl[k + 1][1:])]
        out.append((q, *vals))
    return out


def arm_tube(sx, base, dark, paw, n=16):
    """Shoulder dome -> upper arm -> elbow -> forearm -> wrist -> paw, one smooth tube (paw is the tube's end)."""
    sm = spline([(Vector((sx * x, y, z)), r) for x, y, z, r in ARM_CTRL], n)
    pts, radii = [q for q, _ in sm], [r for _, r in sm]
    sws = [base if pts[i].z > 0.172 else (dark if pts[i].z > 0.104 else paw) for i in range(n - 1)]
    return pts, radii, sws


LEG_CTRL = [  # (x, y, z, sideways radius, other radius): hip (inside the body) -> thigh -> knee -> ankle -> flat foot -> toes
    (0.048, 0.004, 0.112, 0.016, 0.016), (0.048, 0.002, 0.092, 0.038, 0.038), (0.048, 0.0, 0.068, 0.043, 0.042),
    (0.049, -0.004, 0.050, 0.037, 0.036), (0.050, -0.008, 0.034, 0.031, 0.029), (0.050, -0.026, 0.021, 0.033, 0.020),
    (0.050, -0.048, 0.019, 0.036, 0.019), (0.050, -0.066, 0.018, 0.031, 0.016), (0.050, -0.075, 0.018, 0.012, 0.008),
]


def leg_tube(sx, n=14):
    sm = spline([(Vector((sx * x, y, z)), ra, rb) for x, y, z, ra, rb in LEG_CTRL], n)
    return [q for q, *_ in sm], [ra for _, ra, _ in sm], [rb for *_, rb in sm]


def raccoon(spec, coll):
    base, dark, ring_dark, light, cream = spec["fur"]
    h = spec["head"]
    up = Parts()       # everything above the hips: tilts forward for the hunch
    lo = Parts()       # feet + tail stay planted
    # ---- lower: feet, legs, tail
    for sx, sd in ((1, "L"), (-1, "R")):
        pts, ra, rb = leg_tube(sx)
        side = Vector((1, 0, 0))

        def leg_frame(i, d, side=side):
            ub = d.cross(side).normalized()                       # front/back on the leg, up/down on the foot
            return side, ub
        foot_from = next(i for i, q in enumerate(pts) if q.y < -0.012)   # where the leg turns into the foot
        lo.part("thigh_" + sd).loft(pts, ra, rb, leg_frame,
                                    lambda i, a, f=foot_from: base if i < foot_from else dark, segs=10)
    # big fluffy tail: rises behind, curls up, thick in the middle
    tail, radii, bands = [], [], []
    n = 18
    ts = [math.sin(k / n * math.pi / 2) for k in range(n + 1)]      # rings bunch up toward the tip -> rounded point
    for t in ts:
        # path always moves back and up (no doubling back), so the rings never cross
        tail.append(Vector((0, 0.03 + 0.19 * math.sin(t * 1.5), 0.075 + 0.21 * t + 0.06 * math.sin(t * math.pi))))
        r = 0.036 + 0.038 * math.sin(math.pi * 0.85 * min(t / 0.9, 1))           # slim root, fluffy bulge mid-tail
        cap = math.sqrt(max(0.0, 1 - ((t - 0.8) / 0.2) ** 2)) if t > 0.8 else 1.0  # rounded end cap
        radii.append(max(0.003, r * cap))
    for t0, t1 in zip(ts, ts[1:]):                                    # rings by distance along the tail
        m = (t0 + t1) / 2
        bands.append(ring_dark if m > 0.25 and int((m - 0.25) / 0.17) % 2 == 0 else base)
    lo.part("tail").tube(tail, radii, bands, segs=10)
    # ---- upper: body, arms, head
    up.part("body").blob(Vector((0, 0.0, 0.135)), Vector((0.085, 0.075, 0.095)), base, 16, 10)     # pear body
    up.blob(Vector((0, -0.04, 0.13)), Vector((0.055, 0.045, 0.07)), cream, 12, 8)                 # belly patch
    for sx, sd in ((1, "L"), (-1, "R")):
        # shoulder + arm as ONE smooth tube: a rounded shoulder dome buried in the body, tapering through the upper
        # arm, elbow and forearm into the paw (two separate blobs left a notch where they met)
        pts, radii, sws = arm_tube(sx, base, dark, ring_dark)
        up.part("arm_" + sd).tube(pts, radii, sws, segs=10)
    hz = 0.265
    hc = Vector((0, -0.005, hz))
    S = Matrix.Translation(hc) @ Matrix.Scale(h, 4) @ Matrix.Translation(-hc)                       # head size knob
    head = []
    head += up.part("head").blob(hc, Vector((0.088, 0.075, 0.072)), base, 16, 10)                    # skull
    for sx, sd in ((1, "L"), (-1, "R")):
        ed = Vector((sx * 0.45, 0.15, 1)).normalized()
        e0 = hc + Vector((sx * 0.040, 0.010, 0.030))                       # root, buried in the skull
        n_e = 9
        epts = [e0 + ed * (0.094 * k / (n_e - 1)) for k in range(n_e)]
        prof = [0.024, 0.031, 0.032, 0.029, 0.024, 0.018, 0.012, 0.006, 0.0015]   # width: swells, then a soft point
        thick = [0.013, 0.012, 0.011, 0.010, 0.009, 0.007, 0.005, 0.003, 0.001]
        ew = ed.cross(Vector((0, 1, 0))).normalized()                      # across the ear
        et = ew.cross(ed).normalized()
        et = -et if et.y > 0 else et                                       # thickness axis points to the front

        def ear_sw(i, a, dark_ear=ring_dark):
            if a >= 0 and 1 <= i <= 4 and math.sin(a) > 0.75:              # front face, inner panel with a dark rim
                return "fur_light"
            return dark_ear
        head += up.part("ear_" + sd).loft(epts, prof, thick, lambda i, d, ew=ew, et=et: (ew, et), ear_sw, segs=8)
        head += up.part("head").blob(hc + Vector((sx * 0.035, -0.063, 0.028)), Vector((0.026, 0.008, 0.009)), cream, 6, 4)  # brows
    head += up.blob(hc + Vector((0, -0.058, 0.004)), Vector((0.085, 0.03, 0.026)), "fur_mask", 14, 6)   # mask band
    head += up.blob(hc + Vector((0, -0.075, -0.03)), Vector((0.035, 0.04, 0.026)), cream, 12, 6)       # muzzle
    head += up.blob(hc + Vector((0, -0.112, -0.024)), Vector((0.012, 0.009, 0.009)), "fur_mask", 6, 4)   # nose
    for sx in (1, -1):
        head += up.blob(hc + Vector((sx * 0.032, -0.083, 0.008)), Vector((0.011, 0.006, 0.011)), "flame_white", 6, 4)  # eye shine
        for dz, tilt in ((0.006, 0.28), (0.0, 0.0), (-0.006, -0.24)):                                 # 3 whiskers a side
            head += up.part("head").cone(hc + Vector((sx * 0.026, -0.094, -0.026 + dz)), (sx, -0.22, tilt), 0.0022, 0.03,
                                         "fur_cream", segs=3)
    bmesh.ops.transform(up.bm, matrix=S, verts=list(set(head)))
    # merge upper into lower with the hunch (rotate about the hips, then pull the head forward/down a touch)
    hip = Vector((0, 0.0, 0.08))
    R = Matrix.Translation(hip) @ Matrix.Rotation(math.radians(spec["hunch"]), 4, "X") @ Matrix.Translation(-hip)
    bmesh.ops.transform(up.bm, matrix=R, verts=up.bm.verts)
    me_up = bpy.data.meshes.new("tmp")
    up.bm.to_mesh(me_up)
    lo.bm.from_mesh(me_up)
    bpy.data.meshes.remove(me_up)
    if spec["cane"]:
        hand = R @ Vector((-0.1, -0.045, 0.095))
        lo.part("cane").tube([Vector((hand.x - 0.01, hand.y - 0.03, 0.0)), Vector((hand.x, hand.y, hand.z + 0.02)),
                 Vector((hand.x + 0.012, hand.y + 0.01, hand.z + 0.045))], [0.009, 0.009, 0.012], ["wood_mid"], 6)
    # whole-body scale (kit)
    bmesh.ops.transform(lo.bm, matrix=Matrix.Scale(spec["scale"] * 1.06, 4), verts=lo.bm.verts)   # 1.06: adult to 0.40 m
    ids = [f[lo.sw] for f in lo.bm.faces]
    me = bpy.data.meshes.new(spec["name"])
    lo.bm.to_mesh(me)
    lo.bm.free()
    up.bm.free()
    ob = bpy.data.objects.new(spec["name"], me)
    coll.objects.link(ob)
    me.materials.append(bpy.data.materials["M_Palette"])
    for i, sid in enumerate(ids):
        P.set_swatch(ob, lo.names[sid], [i])
    # origin at the feet: lowest point -> z 0
    zmin = min(v.co.z for v in me.vertices)
    for v in me.vertices:
        v.co.z -= zmin
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def cam_obj(name, ortho=None):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    bpy.context.scene.collection.objects.link(c)
    if ortho:
        c.data.type = "ORTHO"
        c.data.ortho_scale = ortho
    return c


def look(cam, target, d, dist):
    d = Vector(d).normalized()
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()


def shoot(cam, path, res):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):            # this file keeps cell + grid + cameras; the old silhouette goes
        if o.name.startswith(("ref_raccoon", "ref_doorway")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    obs = [raccoon(s, assets) for s in (ADULT, KIT, ELDER)]
    for o, x in zip(obs, (0, 1, 2)):
        o.location.x = x
    # cell cubes over the other two cells
    bars = bpy.data.objects["ref_cell_bars"]
    for x in (1, 2):
        b2 = bars.copy()
        ref.objects.link(b2)
        b2.location.x = x
    stats = {o.name: (tris(o), round(o.dimensions.z, 3), round(o.dimensions.x, 3), round(o.dimensions.y, 3)) for o in obs}
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "chr_raccoon_blockout.blend"), relative_remap=True)

    sc.render.engine = "CYCLES"
    sc.cycles.samples = 32
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    # turnarounds: front / side / top, ortho, grid hidden, cell visible
    hide = [bpy.data.objects[n] for n in ("ref_floor", "ref_grid_lines")]
    for o in hide:
        o.hide_render = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.18, 0.23, 1)
    cam = cam_obj("ortho", 0.62)
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    for o in obs:
        x = o.location.x
        k = o.dimensions.z / 0.4 if o.name.endswith("kit") else 1.0
        cam.data.ortho_scale = 0.62 * max(k, 0.62)
        tiles = []
        for other in obs:
            other.hide_render = other is not o
        for lab, d, tgt in (("front", (0, -1, 0), (x, 0, 0.2 * k)), ("side", (1, 0, 0), (x, 0.05, 0.2 * k)),
                            ("top", (0, 0, 1), (x, 0.05, 0))):
            look(cam, tgt, d, 5)
            if lab == "top":
                cam.rotation_euler = (0, 0, 0)
            f = out / f"_{lab}.png"
            shoot(cam, f, (500, 560))
            tiles.append((lab, f))
        sheet = Image.new("RGB", (1500, 600), (24, 26, 32))
        dd = ImageDraw.Draw(sheet)
        for i, (lab, f) in enumerate(tiles):
            sheet.paste(Image.open(f), (500 * i, 0))
            dd.text((500 * i + 14, 570), f"{o.name}  {lab}", font=font, fill=(230, 232, 240))
            f.unlink()
        sheet.save(out / f"{o.name}_blockout_views.png")
    for o in hide:
        o.hide_render = False
    for o in obs:
        o.hide_render = False
    for o in ref.objects:
        if o.name.startswith("ref_cell_bars"):
            o.hide_render = True      # the floor grid shows the cells; the cages only cluttered the view
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
    # game camera: all three standing in their cells
    gc = bpy.data.objects["GameCam"]
    look(gc, (1.0, 0.0, 0.25), (math.sin(math.radians(-30)) * math.cos(math.radians(50)),
                               -math.cos(math.radians(-30)) * math.cos(math.radians(50)), math.sin(math.radians(50))), 4.6)
    shoot(gc, out / "raccoon_blockout_gamecam.png", (1280, 800))
    # close game-cam view of the adult alone in its cell (what the player sees at mid zoom, cropped)
    look(gc, (0.0, 0.0, 0.2), (math.sin(math.radians(-30)) * math.cos(math.radians(50)),
                               -math.cos(math.radians(-30)) * math.cos(math.radians(50)), math.sin(math.radians(50))), 2.4)
    shoot(gc, out / "raccoon_adult_gamecam_cell.png", (1000, 800))
    top = bpy.data.objects["TopCam"]
    top.location = (1.0, 0, 10)
    top.data.ortho_scale = 4.0
    shoot(top, out / "raccoon_blockout_topdown.png", (1000, 1000))
    for n, s in stats.items():
        print(f"STAT {n}: {s[0]} tris, h {s[1]} m, w {s[2]} m, d {s[3]} m")


if __name__ == "__main__":
    main()
