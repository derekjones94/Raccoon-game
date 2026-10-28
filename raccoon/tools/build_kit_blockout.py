"""Batch 4: modular kit blockouts, 1 cell each.

Cell = x,y in [-0.5, 0.5], z in [0, 1]. Origin bottom-centre. Front = -Y (toward the default camera).
  * walls sit on the BACK (+Y) edge, 0.30 m thick, outer face inset 0.03 m; wall ends run to the cell edge
    (neighbouring wall ends meet face to face, hidden, no slit). Rotate in 90 deg steps for other edges.
  * floor tiles inset 0.03 m on all sides (the grooves read as flagstone joints)
  * ramp / stairs climb from the front (z 0) to the back (z 1): one full cell up

Run:  python3 tools/build_kit_blockout.py
Out:  kit_blockout.blend, export/kit_*.glb, renders/kit_*.png
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402

ROOT = P.ROOT
INSET, WALL_T = 0.03, 0.30
WY1 = 0.5 - INSET               # wall outer face
WY0 = WY1 - WALL_T              # wall inner face
DOOR_W, DOOR_H = 0.36, 0.52
NAMES = list(P.SWATCH)


class Mesh:
    def __init__(self):
        self.bm = bmesh.new()
        self.sw = self.bm.faces.layers.int.new("sw")

    def tag(self, faces, swatch):
        for f in faces:
            f[self.sw] = NAMES.index(swatch)

    def box(self, lo, hi, swatch, top=None):
        """Axis box from corner lo to corner hi; optional different swatch on the top face."""
        lo, hi = Vector(lo), Vector(hi)
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation((lo + hi) / 2) @ Matrix.Diagonal((*(hi - lo), 1)), verts=r["verts"])
        faces = list({f for v in r["verts"] for f in v.link_faces})
        self.tag(faces, swatch)
        if top:
            self.tag([f for f in faces if f.normal.z > 0.9], top)
        return r["verts"]

    def beam(self, a, b, t, swatch):
        """Square-section beam from point a to point b."""
        a, b = Vector(a), Vector(b)
        d = b - a
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation((a + b) / 2) @ q @ Matrix.Diagonal((t, t, d.length, 1)),
                            verts=r["verts"])
        self.tag({f for v in r["verts"] for f in v.link_faces}, swatch)

    def poly_prism(self, outline_xz, y0, y1, swatch, holes_inner=None):
        """Extrude an XZ outline (ccw, seen from -Y) between y0 and y1."""
        f0 = [self.bm.verts.new((x, y0, z)) for x, z in outline_xz]
        f1 = [self.bm.verts.new((x, y1, z)) for x, z in outline_xz]
        faces = [self.bm.faces.new(f0), self.bm.faces.new(list(reversed(f1)))]
        n = len(f0)
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((f0[i], f1[i], f1[j], f0[j])))
        self.tag(faces, swatch)

    def obj(self, name, coll):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        ids = [f[self.sw] for f in self.bm.faces]
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        me.materials.append(bpy.data.materials["M_Palette"])
        for i, sid in enumerate(ids):
            P.set_swatch(ob, NAMES[sid], [i])
        return ob


def cap_stones(m, x0, x1, y0, y1, z0, rnd, n=3):
    """Rough-cut capstones along the top of a wall run: chunky blocks of varied height."""
    w = (x1 - x0) / n
    for k in range(n):
        h = 0.1 + rnd.uniform(-0.015, 0.0)
        m.box((x0 + k * w + 0.004, y0 - 0.008, z0), (x0 + (k + 1) * w - 0.004, y1, z0 + h), "stone_mid", top="stone_light")


def base_course(m, x0, x1, y0, y1):
    """A slightly wider footing course (reads as heavy stone from the camera)."""
    m.box((x0, y0 - 0.02, 0), (x1, y1, 0.08), "stone_dark")


# ---------------------------------------------------------------- pieces
def kit_floor_stone(coll, rnd):
    m = Mesh()
    a = -0.5 + INSET
    s = (1 - 2 * INSET) / 2
    for i in range(2):
        for j in range(2):
            h = 0.09 + rnd.uniform(-0.012, 0.01)
            x, y = a + i * s, a + j * s
            m.box((x + 0.008, y + 0.008, 0), (x + s - 0.008, y + s - 0.008, h), "stone_dark",
                  top=("stone_mid", "stone_light", "stone_light", "stone_mid")[i * 2 + j])
    return m.obj("kit_floor_stone", coll)


def kit_wall_stone(coll, rnd):
    m = Mesh()
    base_course(m, -0.5, 0.5, WY0, WY1)
    m.box((-0.5, WY0, 0.08), (0.5, WY1, 0.9), "stone_mid")
    cap_stones(m, -0.5, 0.5, WY0, WY1, 0.9, rnd)
    return m.obj("kit_wall_stone", coll)


def arch_outline(x0, x1, z1):
    hw = DOOR_W / 2
    spring = DOOR_H - hw
    pts = [(x0, 0.08), (-hw, 0.08), (-hw, spring)]
    pts += [(math.cos(math.pi - math.pi * k / 8) * hw, spring + math.sin(math.pi - math.pi * k / 8) * hw) for k in range(1, 8)]
    pts += [(hw, spring), (hw, 0.08), (x1, 0.08), (x1, z1), (x0, z1)]
    return pts


def kit_wall_stone_door(coll, rnd):
    m = Mesh()
    hw = DOOR_W / 2
    for x0, x1 in ((-0.5, -hw), (hw, 0.5)):
        m.box((x0, WY0 - 0.02, 0), (x1, WY1, 0.08), "stone_dark")
    # wall with the arch cut: two halves split at the arch crown so every face is a simple polygon
    o = arch_outline(-0.5, 0.5, 0.9)
    left = [o[0], o[1], o[2]] + o[3:7] + [(0.0, DOOR_H), (0.0, 0.9), o[-1]]
    right = [(0.0, DOOR_H)] + o[7:10] + [o[10], o[11], o[12], o[13], (0.0, 0.9)]
    m.poly_prism(left, WY0, WY1, "stone_mid")
    m.poly_prism(right, WY0, WY1, "stone_mid")
    # threshold stone + darker arch voussoirs ring (one chunky keystone)
    m.box((-hw, WY0 - 0.03, 0), (hw, WY1, 0.03), "stone_light")
    m.box((-0.05, WY0 - 0.015, DOOR_H - 0.02), (0.05, WY0 + 0.01, DOOR_H + 0.07), "stone_light")
    cap_stones(m, -0.5, 0.5, WY0, WY1, 0.9, rnd)
    return m.obj("kit_wall_stone_door", coll)


def kit_wall_stone_corner(coll, rnd):
    """L corner: wall on the back (+Y) and right (+X) edges, meeting in the back-right corner."""
    m = Mesh()
    X0, X1 = WY0, WY1                    # right wall's inner/outer x (same offsets as the back wall)
    base_course(m, -0.5, X0, WY0, WY1)
    m.box((X0 - 0.02, -0.5, 0), (X1, WY1, 0.08), "stone_dark")
    m.box((-0.5, WY0, 0.08), (X0, WY1, 0.9), "stone_mid")
    m.box((X0, -0.5, 0.08), (X1, WY1, 0.9), "stone_mid")
    cap_stones(m, -0.5, X0, WY0, WY1, 0.9, rnd, 2)
    # right-wall caps run along Y
    w = (WY1 + 0.5) / 2
    for k in range(2):
        h = 0.1 + rnd.uniform(-0.015, 0.0)
        y0 = -0.5 + k * w
        m.box((X0 - 0.008, y0 + 0.004, 0.9), (X1, y0 + w - 0.004, 0.9 + h), "stone_mid", top="stone_light")
    # a taller corner stone ties the two runs together
    m.box((X0 - 0.015, WY0 - 0.015, 0.9), (X1, WY1, 1.0), "stone_light", top="stone_frost")
    return m.obj("kit_wall_stone_corner", coll)


def kit_ramp_stone(coll, rnd):
    """Wedge from z 0 at the front edge to z 1 at the back edge, with side curbs."""
    m = Mesh()
    a, b = -0.5 + INSET, 0.5 - INSET
    prof = [(a, 0.0), (b, 0.0), (b, 1.0)]               # (y, z) side profile
    for x0, x1, sw in ((a + 0.06, b - 0.06, "stone_mid"), (a, a + 0.06, "stone_dark"), (b - 0.06, b, "stone_dark")):
        f0 = [m.bm.verts.new((x0, y, z + (0.03 if sw == "stone_dark" else 0))) for y, z in prof]
        f1 = [m.bm.verts.new((x1, y, z + (0.03 if sw == "stone_dark" else 0))) for y, z in prof]
        faces = [m.bm.faces.new(f0), m.bm.faces.new(list(reversed(f1)))]
        for i in range(3):
            j = (i + 1) % 3
            faces.append(m.bm.faces.new((f0[i], f0[j], f1[j], f1[i])))
        m.tag(faces, sw)
        m.tag([f for f in faces if f.calc_center_median().z > 0.05 and abs(f.normal.x) < 0.5 and f.normal.z > 0.1],
              "stone_light" if sw == "stone_mid" else "stone_mid")
    # 4 grip ridges across the slope
    for k in range(1, 5):
        t = k / 5
        y, z = a + (b - a) * t, t
        m.beam((a + 0.06, y, z), (b - 0.06, y, z), 0.03, "stone_dark")
    return m.obj("kit_ramp_stone", coll)


def kit_stairs_stone(coll, rnd):
    """6 chunky steps, 1/6 m rise each, climbing from the front edge to the back edge. One solid (no overlaps)."""
    m = Mesh()
    a, b = -0.5 + INSET, 0.5 - INSET
    n = 6
    run = (b - a) / n
    prof = [(a, 0.0), (b, 0.0), (b, 1.0)]                 # (y, z), walked back -> down -> front up the steps
    for k in range(n - 1, -1, -1):
        prof.append((a + k * run, (k + 1) / n))
        prof.append((a + k * run, k / n))
    prof = prof[:-1]                                      # last point (a, 0) is the first one
    for x0, x1 in ((a, b),):
        f0 = [m.bm.verts.new((x0, y, z)) for y, z in prof]
        f1 = [m.bm.verts.new((x1, y, z)) for y, z in prof]
        faces = [m.bm.faces.new(f0), m.bm.faces.new(list(reversed(f1)))]
        for i in range(len(prof)):
            j = (i + 1) % len(prof)
            faces.append(m.bm.faces.new((f0[i], f0[j], f1[j], f1[i])))
        m.tag(faces, "stone_mid")
        bmesh.ops.recalc_face_normals(m.bm, faces=faces)
        for f in faces:
            c = f.calc_center_median()
            if f.normal.z > 0.9 and c.z > 0.01:          # treads alternate light / pale
                m.tag([f], "stone_light" if int(round(c.z * n)) % 2 else "stone_pale")
    return m.obj("kit_stairs_stone", coll)


def kit_scaffold_wood(coll, rnd):
    """Scavenged-timber platform: deck top at z 1.0 (the next level's floor), 4 posts, cross bracing."""
    m = Mesh()
    a, b = -0.5 + INSET, 0.5 - INSET
    p = 0.07
    for x in (a + p / 2, b - p / 2):
        for y in (a + p / 2, b - p / 2):
            m.box((x - p / 2, y - p / 2, 0), (x + p / 2, y + p / 2, 0.93), "wood_dark")
    # deck: 5 planks, slightly varied, one of them weathered
    w = (b - a) / 5
    for k in range(5):
        top = 1.0 - rnd.uniform(0, 0.008)
        m.box((a + k * w + 0.006, a, 0.93), (a + (k + 1) * w - 0.006, b, top), "wood_mid",
              top="wood_weathered" if k == 3 else ("wood_light" if k % 2 else "wood_mid"))
    # bearers under the deck + X bracing on left and right sides, rope lashings at the joints
    for y in (a + 0.04, b - 0.04):
        m.box((a, y - 0.03, 0.87), (b, y + 0.03, 0.93), "wood_dark")
    for x in (a + p / 2, b - p / 2):
        m.beam((x, a + p, 0.1), (x, b - p, 0.82), 0.04, "wood_mid")
        m.beam((x, b - p, 0.1), (x, a + p, 0.82), 0.04, "wood_mid")
    for x in (a + p / 2, b - p / 2):
        for y in (a + p / 2, b - p / 2):
            m.box((x - p * 0.65, y - p * 0.65, 0.8), (x + p * 0.65, y + p * 0.65, 0.86), "rope")
    return m.obj("kit_scaffold_wood", coll)


# the chicken ladder: a cleated plank a raccoon scrambles up on all fours (its rung spacing would beat any
# raccoon on a rung ladder). build_raccoon_jobs' climb_ladder_up / _down are made on these numbers.
LAD_FOOT, LAD_TOP = (-0.42, 0.0), (0.14, 1.0)   # (y, z) of the plank's walking surface: bottom and top edge
LAD_W, LAD_THICK = 0.26, 0.025
LAD_CLEAT0, LAD_STRIDE = 0.14, 0.1              # cleats: the first one's distance up the plank, then every stride
                                                # (the climber's toes rest above one, its paws grip between two)
CLEAT_H, CLEAT_D = 0.012, 0.018                 # a cleat stands this high off the plank, this deep along it
DECK_Z, DECK_Y = 1.012, (0.15, 0.475)           # the top deck: laid on the wall's capstones, its walking surface
                                                # (it starts just behind the plank's top: nothing sticks out over it)


def kit_ladder_wood(coll, rnd):
    """A chicken ladder: a cleated plank from the front of the cell up to a short deck laid across the top of a back
    wall (the deck's battens hang down both wall faces and hold it on)."""
    m = Mesh()
    fy, fz = LAD_FOOT
    ty, tz = LAD_TOP
    d = Vector((0, ty - fy, tz - fz))
    L = d.length
    d.normalize()
    n = Vector((0, -d.z, d.y))                  # out of the walking surface, toward the climber
    hw = LAD_W / 2

    def slab(pts_yz, x0, x1, swatch):
        """A prism: a (y, z) outline (any winding) extruded from x0 to x1."""
        a = [m.bm.verts.new((x0, y, z)) for y, z in pts_yz]
        b = [m.bm.verts.new((x1, y, z)) for y, z in pts_yz]
        fs = [m.bm.faces.new(a), m.bm.faces.new(list(reversed(b)))]
        for i in range(len(a)):
            j = (i + 1) % len(a)
            fs.append(m.bm.faces.new((a[i], a[j], b[j], b[i])))
        m.tag(fs, swatch)

    def on(s, off):
        p = Vector((0, fy, fz)) + d * s + n * off
        return (p.y, p.z)
    # the plank: the walking surface from foot to top; its underside cut level at the floor, its top end cut plumb
    # against the deck's battens
    bot_back = (fy + LAD_THICK * n.z / d.z * d.y - LAD_THICK * n.y, 0.0)
    slab([(fy, fz), (ty, tz), (ty, tz - LAD_THICK / d.y), bot_back], -hw, hw, "wood_mid")
    # cleats: thin battens across the plank, every stride
    s = LAD_CLEAT0
    while s < L - 0.1:
        c0, c1 = on(s - CLEAT_D / 2, 0.0), on(s + CLEAT_D / 2, 0.0)
        c2, c3 = on(s + CLEAT_D / 2, CLEAT_H), on(s - CLEAT_D / 2, CLEAT_H)
        slab([c0, c1, c2, c3], -hw + 0.012, hw - 0.012, "wood_light")
        s += LAD_STRIDE
    # two rails along the plank's edges, nailed on (keep feet and paws on the planking)
    for x in (-hw, hw - 0.014):
        slab([on(0.02, 0.0), on(L - 0.01, 0.0), on(L - 0.01, 0.016), on(0.02, 0.016)], x, x + 0.014, "wood_dark")
    # the deck on the wall top, and its battens down the wall's inner and outer faces
    m.box((-hw - 0.02, DECK_Y[0], DECK_Z - 0.012), (hw + 0.02, DECK_Y[1], DECK_Z), "wood_mid", top="wood_light")
    for y0, y1 in ((LAD_TOP[0], WY0 - 0.008), (WY1, DECK_Y[1])):          # the plank's top end rests on the inner pair
        for x in (-hw + 0.01, hw - 0.04):
            m.box((x, y0, 0.93), (x + 0.03, y1, DECK_Z - 0.012), "wood_dark")
    return m.obj("kit_ladder_wood", coll)


PIECES = [kit_floor_stone, kit_wall_stone, kit_wall_stone_door, kit_wall_stone_corner,
          kit_ramp_stone, kit_stairs_stone, kit_scaffold_wood, kit_ladder_wood]


# ---------------------------------------------------------------- scene / renders
def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def instance(src, coll, loc, rot=0.0, name=None):
    o = src.copy()
    o.name = name or src.name + "_ref"
    coll.objects.link(o)
    o.location = loc
    o.rotation_euler.z = rot
    o.hide_render = False
    return o


def look(cam, target, yaw_deg, dist, pitch_deg=50):
    yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
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
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    rnd = random.Random(4)
    obs = [f(assets, rnd) for f in PIECES]
    stats = {o.name: tris(o) for o in obs}
    # the approved raccoon for scale
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_blockout.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rac = dst.objects[0]
    rac.name = "ref_raccoon"
    ref.objects.link(rac)
    rac.hide_render = True                 # the source copy; scale references are instances below
    # each piece sits at the origin in Assets (that's what gets exported); the showcase uses copies in Reference
    for o in obs:
        o.hide_render = True
    show = {}
    for i, o in enumerate(obs):
        x, y = (i % 4) * 2, -(i // 4) * 2           # whole cells, one empty cell between pieces
        show[o.name] = instance(o, ref, (x, y, 0))
    for nm, off in (("kit_wall_stone_door", (0, WY0 + WALL_T / 2 - 0.04)), ("kit_stairs_stone", (0.32, -0.62)), ("kit_ladder_wood", (0.3, -0.3))):
        c = show[nm].location
        instance(rac, ref, (c.x + off[0], c.y + off[1], 0), name=f"ref_raccoon_{nm}")
    # assembled test room, off to the right: 3x2 floor, back run wall | door | wall, corner on the right,
    # left wall rotated to the left edge, stairs up to a scaffold
    R = Vector((9, 0, 0))
    fl, wl, dr, cn = (bpy.data.objects[n] for n in ("kit_floor_stone", "kit_wall_stone", "kit_wall_stone_door", "kit_wall_stone_corner"))
    room = []
    for i in range(3):
        for j in range(2):
            room.append(instance(fl, ref, R + Vector((i, -j, 0))))
    room.append(instance(cn, ref, R + Vector((0, 0, 0)), rot=math.pi / 2))        # back-left corner (corner turned 90)
    room.append(instance(dr, ref, R + Vector((1, 0, 0))))
    room.append(instance(cn, ref, R + Vector((2, 0, 0))))                         # back-right corner
    room.append(instance(wl, ref, R + Vector((2, -1, 0)), rot=-math.pi / 2))      # right edge
    room.append(instance(wl, ref, R + Vector((0, -1, 0)), rot=math.pi / 2))       # left edge
    instance(rac, ref, R + Vector((1, -0.35, 0.09)), name="ref_raccoon_room")
    instance(rac, ref, R + Vector((0.2, -1.2, 0.09)), rot=0.8, name="ref_raccoon_room2")

    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "kit_blockout.blend"), relative_remap=True)
    # export each kit piece (Assets only) with the template's exporter
    exp = ROOT / "export"
    sys.argv = [sys.argv[0], "--", str(exp)]
    for o in obs:
        o.hide_render = False
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
    for o in obs:
        o.hide_render = True

    sc.render.engine = "CYCLES"
    sc.cycles.samples = 32
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    gc = bpy.data.objects["GameCam"]
    for n in ("ref_floor", "ref_grid_lines"):            # replace the template grid with a bigger one
        bpy.data.objects.remove(bpy.data.objects[n])
    import build_template
    build_template.grid(ref, n=17)                        # odd n -> lines on the half-integers = cell edges
    for n in ("ref_floor", "ref_grid_lines"):
        bpy.data.objects[n].location.x += 5
        bpy.data.objects[n].location.y += -1
    look(gc, (3.2, -1.3, 0.3), -30, 12.5)
    shoot(gc, out / "kit_blockout_gamecam.png", (1600, 1000))
    look(gc, R + Vector((1.0, -0.6, 0.3)), -30, 4.6)
    shoot(gc, out / "kit_room_gamecam.png", (1280, 800))
    look(gc, R + Vector((1.0, -0.6, 0.3)), 150, 4.6)
    shoot(gc, out / "kit_room_gamecam_back.png", (1280, 800))
    top = bpy.data.objects["TopCam"]
    top.data.ortho_scale = 12.5
    top.location = (5.5, -1.0, 20)
    top.data.clip_end = 100
    shoot(top, out / "kit_blockout_topdown.png", (1600, 700))
    for n, t in stats.items():
        print(f"STAT {n}: {t} tris")


if __name__ == "__main__":
    main()
