"""Batch 5: starter building blockouts.

Footprints in whole cells (W along X, D along Y), whole-cell heights, everything inset 0.03 m from the footprint edge.
Origin = bottom-centre of the footprint. Entrances face -Y (front, toward the default camera).

Run:  python3 tools/build_buildings_blockout.py
Out:  buildings_blockout.blend, export/bld_*.glb, renders/bld_*.png
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402

ROOT = P.ROOT
IN = 0.03
NAMES = K.NAMES


class M(K.Mesh):
    """Kit mesh + a few more primitives for buildings."""

    def obox(self, c, size, swatch, rot=(0, 0, 0), top=None):
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        T = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(self.bm, matrix=T, verts=r["verts"])
        faces = list({f for v in r["verts"] for f in v.link_faces})
        self.tag(faces, swatch)
        if top:
            for f in faces:
                f.normal_update()
            self.tag([f for f in faces if f.normal.z > 0.7], top)

    def cyl(self, c, r, h, swatch, cap=None, axis=(0, 0, 1), segs=8, r2=None, rot=0.0):
        """Cylinder / cone centred at c along axis; caps can take another swatch (log ends, rims)."""
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=segs, radius1=r, radius2=r if r2 is None else r2, depth=h)
        q = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
        T = Matrix.Translation(c) @ q @ Matrix.Rotation(rot, 4, "Z")
        bmesh.ops.transform(self.bm, matrix=T, verts=res["verts"])
        faces = list({f for v in res["verts"] for f in v.link_faces})
        self.tag(faces, swatch)
        if cap:
            self.tag([f for f in faces if len(f.verts) == segs], cap)

    def blob(self, c, r, swatch, segs=8, rings=5):
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=segs, v_segments=rings, radius=1.0)
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*r, 1)), verts=res["verts"])
        self.tag({f for v in res["verts"] for f in v.link_faces}, swatch)

    def prism_x(self, prof_yz, x0, x1, swatch, ends=None):
        """Extrude a (y, z) profile along X (gable ends, wedges)."""
        f0 = [self.bm.verts.new((x0, y, z)) for y, z in prof_yz]
        f1 = [self.bm.verts.new((x1, y, z)) for y, z in prof_yz]
        caps = [self.bm.faces.new(f0), self.bm.faces.new(list(reversed(f1)))]
        sides = []
        for i in range(len(f0)):
            j = (i + 1) % len(f0)
            sides.append(self.bm.faces.new((f0[i], f0[j], f1[j], f1[i])))
        self.tag(sides, swatch)
        self.tag(caps, ends or swatch)

    def gable_roof(self, x0, x1, y0, y1, z_eave, z_ridge, swatch, overhang=0.08, t=0.06, end_sw=None):
        """Two roof slabs + filled gable ends under them."""
        half = (y1 - y0) / 2
        yc = (y0 + y1) / 2
        rise = z_ridge - z_eave
        ang = math.atan2(rise, half)
        L = math.hypot(half, rise) + overhang
        for s in (-1, 1):
            down = Vector((0, s * math.cos(ang), -math.sin(ang)))           # along the slope, toward the eave
            up = Vector((0, s * math.sin(ang), math.cos(ang)))              # slab normal
            mid = Vector(((x0 + x1) / 2, yc + s * half / 2, z_eave + rise / 2))
            self.obox(mid + down * (overhang / 2) + up * (t / 2), (x1 - x0 + 2 * overhang, L, t), swatch, rot=(-s * ang, 0, 0))
        self.prism_x([(y0, z_eave), (y1, z_eave), (yc, z_ridge)], x0, x1, end_sw or swatch)


def crate(m, c, s, rot=0.0):
    m.obox(c + Vector((0, 0, s / 2)), (s, s, s), "wood_mid", rot=(0, 0, rot), top="wood_light")
    m.obox(c + Vector((0, 0, s / 2)), (s * 1.04, s * 0.25, s * 1.04), "wood_dark", rot=(0, 0, rot))   # strap band


def barrel(m, c, r, h):
    m.cyl(c + Vector((0, 0, h / 2)), r, h, "wood_mid", cap="wood_dark", segs=10)
    for z in (0.22, 0.78):
        m.cyl(c + Vector((0, 0, h * z)), r * 1.06, h * 0.08, "iron", segs=10)


def sack(m, c, r, sw="burlap"):
    m.blob(c + Vector((0, 0, r * 0.9)), Vector((r, r * 0.9, r)), sw, 8, 5)
    m.cyl(c + Vector((0, 0, r * 1.9)), r * 0.25, r * 0.4, "rope", segs=6)


def log(m, c, r, length, axis=(1, 0, 0)):
    m.cyl(c, r, length, "wood_bark", cap="wood_cut", axis=axis, segs=7)


# ---------------------------------------------------------------- buildings
def bld_den_2x2(coll, rnd):
    """The den has its own script now (hollow, lived-in, roof as a separate child node): see build_den.py."""
    import build_den
    den, _ = build_den.build(coll)
    return den


def bld_stockpile_2x2(coll, rnd):
    """Pallet yard: plank floor, fenced back and sides, tarp lean-to, crates / sacks / barrel."""
    m = M()
    a = 1.0 - IN
    for k in range(5):
        x = -a + (2 * a) * (k + 0.5) / 5
        m.obox(Vector((x, 0, 0.03)), (2 * a / 5 - 0.02, 2 * a, 0.06), "wood_light" if k % 2 else "wood_mid")
    posts = [(-a + 0.04, a - 0.04, 0.95), (a - 0.04, a - 0.04, 0.95), (-a + 0.04, -a + 0.04, 0.55), (a - 0.04, -a + 0.04, 0.55),
             (-a + 0.04, 0, 0.75), (a - 0.04, 0, 0.75)]
    for x, y, h in posts:
        m.obox(Vector((x, y, h / 2)), (0.07, 0.07, h), "wood_dark")
    for z in (0.3, 0.5):
        m.beam((-a + 0.04, a - 0.04, z), (a - 0.04, a - 0.04, z), 0.04, "wood_mid")
        for x in (-a + 0.04, a - 0.04):
            m.beam((x, -a + 0.04, z), (x, a - 0.04, z), 0.04, "wood_mid")
    # tarp lean-to over the back half
    m.obox(Vector((0, 0.47, 0.8)), (2 * a, 0.95, 0.025), "cloth_blue", rot=(-0.36, 0, 0))
    # goods
    crate(m, Vector((-0.55, 0.55, 0.06)), 0.32, 0.1)
    crate(m, Vector((-0.55, 0.55, 0.38)), 0.26, -0.2)
    crate(m, Vector((-0.15, 0.6, 0.06)), 0.3, 0.05)
    barrel(m, Vector((0.55, 0.55, 0.06)), 0.15, 0.36)
    for c in ((0.2, -0.3), (0.45, -0.45), (0.6, -0.15)):
        sack(m, Vector((*c, 0.06)), 0.12)
    m.obox(Vector((-a + 0.04, -a + 0.12, 0.45)), (0.03, 0.2, 0.12), "teal")         # guild tag on the post
    return m.obj("bld_stockpile_2x2", coll)


def bld_rummage_camp_2x2(coll, rnd):
    """Scavengers' sorting camp: A-frame tent, junk heap, sorting table, lantern pole."""
    m = M()
    a = 1.0 - IN
    m.obox(Vector((0.1, 0.0, 0.006)), (1.7, 1.6, 0.012), "burlap")
    # A-frame tent at the back left (mustard cloth, ridge along X)
    m.gable_roof(-0.95, 0.05, 0.05, 0.92, 0.04, 0.82, "cloth_mustard", overhang=0.0, t=0.03, end_sw="cloth_mustard")
    m.obox(Vector((-0.45, 0.06, 0.22)), (0.3, 0.02, 0.36), "soot")                                 # tent mouth
    for x in (-0.95, 0.05):
        m.obox(Vector((x, 0.5, 0.45)), (0.04, 0.04, 0.9), "wood_dark")
    # junk heap front right: pots, a gear, a cracked shield, a tin plate
    m.blob(Vector((0.55, -0.45, 0.13)), Vector((0.32, 0.28, 0.13)), "iron", 10, 5)
    m.cyl(Vector((0.42, -0.5, 0.2)), 0.12, 0.14, "copper", cap="rust_dark", segs=8)
    m.cyl(Vector((0.68, -0.38, 0.2)), 0.14, 0.04, "rust", axis=(0.3, -0.4, 1), segs=10)            # gear
    m.cyl(Vector((0.55, -0.62, 0.16)), 0.16, 0.03, "iron_light", cap="cloth_red", axis=(0, -1, 0.6), segs=10)
    m.cyl(Vector((0.75, -0.6, 0.06)), 0.07, 0.1, "verdigris", segs=8)
    # sorting table
    m.obox(Vector((0.55, 0.45, 0.36)), (0.6, 0.4, 0.04), "wood_light")
    for dx in (-0.26, 0.26):
        for dy in (-0.16, 0.16):
            m.obox(Vector((0.55 + dx, 0.45 + dy, 0.17)), (0.04, 0.04, 0.34), "wood_dark")
    m.cyl(Vector((0.45, 0.45, 0.42)), 0.05, 0.08, "gold", segs=8)
    m.cyl(Vector((0.65, 0.5, 0.41)), 0.06, 0.05, "pewter", segs=8)
    m.obox(Vector((0.6, 0.38, 0.4)), (0.08, 0.06, 0.05), "silver")
    # lantern pole
    m.obox(Vector((-0.8, -0.75, 0.45)), (0.05, 0.05, 0.9), "wood_dark")
    m.beam((-0.8, -0.75, 0.88), (-0.62, -0.75, 0.88), 0.035, "wood_dark")
    m.obox(Vector((-0.62, -0.75, 0.76)), (0.08, 0.08, 0.12), "flame_yellow")
    m.obox(Vector((-0.62, -0.75, 0.83)), (0.1, 0.1, 0.03), "iron_dark")
    # baskets
    m.cyl(Vector((-0.2, -0.55, 0.1)), 0.13, 0.2, "rope", cap="rope_dark", segs=8, r2=0.15)
    return m.obj("bld_rummage_camp_2x2", coll)


def bld_woodpile_1x1(coll, rnd):
    """Stacked logs between two post cradles, a chopping stump with an axe."""
    m = M()
    a = 0.5 - IN
    for x in (-0.36, 0.36):
        for y in (-0.15, 0.25):
            m.obox(Vector((x, y, 0.33)), (0.05, 0.05, 0.66), "wood_dark")
    r = 0.068
    rows = [4, 3, 2, 1]
    for k, n in enumerate(rows):
        for i in range(n):
            y = 0.05 + (i - (n - 1) / 2) * 2 * r * 1.02
            log(m, Vector((rnd.uniform(-0.02, 0.02), y, r + k * r * 1.75)), r, 0.78 + rnd.uniform(-0.04, 0.04))
    m.cyl(Vector((0.25, -0.36, 0.09)), 0.1, 0.18, "wood_bark", cap="wood_cut", segs=8)            # stump
    m.beam((0.2, -0.36, 0.18), (0.08, -0.33, 0.38), 0.025, "wood_light")                           # axe handle
    m.obox(Vector((0.22, -0.36, 0.2)), (0.1, 0.02, 0.06), "iron_light", rot=(0, 0.5, 0))           # axe head
    return m.obj("bld_woodpile_1x1", coll)


def bld_washing_pool_2x1(coll, rnd):
    """Stone basin with water, washboard, bucket, a drying line with cloths."""
    m = M()
    ax, ay = 1.0 - IN, 0.5 - IN
    h, t = 0.26, 0.12
    m.obox(Vector((0, 0, 0.04)), (2 * ax, 2 * ay, 0.08), "stone_dark")
    for c, s in (((0, -ay + t / 2 + 0.02), (2 * ax - 0.12, t, h)), ((0, ay - t / 2 - 0.02), (2 * ax - 0.12, t, h)),
                 ((-ax + 0.06 + t / 2, 0), (t, 2 * ay - 2 * t - 0.04, h)), ((ax - 0.06 - t / 2, 0), (t, 2 * ay - 2 * t - 0.04, h))):
        m.obox(Vector((c[0], c[1], h / 2)), s, "stone_mid", top="stone_light")
    m.obox(Vector((0, 0, h - 0.06)), (2 * ax - 0.3, 2 * ay - 0.26, 0.02), "water")
    m.obox(Vector((0, 0.02, h - 0.055)), (2 * ax - 0.7, 2 * ay - 0.5, 0.02), "water_deep")         # deeper middle
    m.obox(Vector((-0.45, -0.1, h - 0.02)), (0.2, 0.03, 0.26), "wood_weathered", rot=(0.5, 0, 0))  # washboard
    barrel(m, Vector((0.75, -0.3, 0.0)), 0.08, 0.16)                                               # bucket
    for x in (-0.85, 0.85):
        m.obox(Vector((x, 0.38, 0.4)), (0.04, 0.04, 0.8), "wood_dark")
    m.beam((-0.85, 0.38, 0.76), (0.85, 0.38, 0.76), 0.012, "rope")
    for x, sw in ((-0.4, "cloth_cream"), (0.05, "cloth_red"), (0.45, "cloth_blue")):
        m.obox(Vector((x, 0.38, 0.62)), (0.22, 0.015, 0.26), sw)
    return m.obj("bld_washing_pool_2x1", coll)


def bld_tinker_bench_1x1(coll, rnd):
    """Workbench with vise, gears and a pegboard of tools on the back edge, a stool in front."""
    m = M()
    a = 0.5 - IN
    m.obox(Vector((0, 0.12, 0.38)), (0.86, 0.42, 0.05), "wood_mid", top="wood_light")
    for x in (-0.38, 0.38):
        for y in (-0.05, 0.29):
            m.obox(Vector((x, y, 0.18)), (0.05, 0.05, 0.36), "wood_dark")
    m.obox(Vector((0, 0.12, 0.08)), (0.8, 0.36, 0.03), "wood_dark")                                # lower shelf
    m.obox(Vector((0, a - 0.03, 0.62)), (0.9, 0.04, 0.5), "wood_weathered")                        # pegboard
    for x, ln in ((-0.3, 0.2), (-0.15, 0.25), (0.15, 0.18), (0.3, 0.22)):
        m.obox(Vector((x, a - 0.06, 0.66)), (0.03, 0.02, ln), "iron_light")
    m.cyl(Vector((0.0, a - 0.07, 0.72)), 0.07, 0.02, "copper", axis=(0, 1, 0), segs=10)           # hung gear
    m.obox(Vector((0.3, -0.04, 0.45)), (0.1, 0.12, 0.08), "iron")                                   # vise
    m.obox(Vector((0.3, -0.12, 0.45)), (0.12, 0.02, 0.07), "iron_dark")
    m.cyl(Vector((-0.15, 0.1, 0.42)), 0.07, 0.025, "rust", segs=10)                                # loose gears
    m.cyl(Vector((-0.02, 0.18, 0.415)), 0.045, 0.02, "copper", segs=8)
    m.obox(Vector((-0.3, 0.2, 0.44)), (0.06, 0.06, 0.08), "flame_yellow")                          # little lamp
    m.cyl(Vector((0, -0.3, 0.12)), 0.09, 0.24, "wood_mid", cap="wood_light", segs=8)                # stool
    m.obox(Vector((0.36, -0.36, 0.03)), (0.12, 0.12, 0.06), "iron_dark")                            # scrap ingot
    return m.obj("bld_tinker_bench_1x1", coll)


def bld_guild_hall_3x3(coll, rnd):
    """HQ: stone ground floor with a great golden shield door, timber upper storey, teal roof, banners, torches."""
    m = M()
    a = 1.5 - IN
    m.obox(Vector((0, 0.05, 0.05)), (2.8, 2.6, 0.1), "stone_dark")
    m.obox(Vector((0, 0.15, 0.55)), (2.6, 2.2, 0.9), "stone_mid", top="stone_light")
    for x in (-1.25, 1.25):                                                                            # corner buttresses
        for y in (-0.92, 1.22):
            m.obox(Vector((x, y, 0.53)), (0.22, 0.22, 1.06), "stone_light", top="stone_pale")
    # upper storey: timber frame
    m.obox(Vector((0, 0.2, 1.3)), (2.3, 1.9, 0.6), "wood_mid")
    for x in (-1.1, 0, 1.1):
        m.obox(Vector((x, -0.76, 1.3)), (0.08, 0.04, 0.6), "wood_dark")
    m.obox(Vector((0, -0.76, 1.03)), (2.3, 0.05, 0.06), "wood_dark")
    for x in (-0.55, 0.55):                                                                            # round junk windows
        m.cyl(Vector((x, -0.77, 1.32)), 0.12, 0.04, "iron", cap="flame_yellow", axis=(0, 1, 0), segs=10)
    # teal roof (ridge along X) with a gold ridge cap
    m.gable_roof(-1.15, 1.15, -0.75, 1.15, 1.6, 1.88, "teal", overhang=0.12, t=0.05, end_sw="wood_dark")
    m.beam((-1.3, 0.2, 1.94), (1.3, 0.2, 1.94), 0.05, "gold")
    m.obox(Vector((0.95, 0.85, 1.75)), (0.24, 0.24, 0.5), "stone_mid", top="soot")                  # chimney
    # front: steps, great round shield door with gold boss, banners, torches
    for k in range(2):
        m.obox(Vector((0, -1.05 - 0.12 * k + 0.12, 0.05 + 0.05 * k)), (0.9 - 0.15 * k, 0.24, 0.1 + 0.1 * k), "stone_light")
    m.obox(Vector((0, -0.98, 0.42)), (0.62, 0.06, 0.64), "stone_deep")
    m.cyl(Vector((0, -1.02, 0.42)), 0.32, 0.06, "gold", cap="gold_light", axis=(0, 1, 0), segs=14)
    m.cyl(Vector((0, -1.06, 0.42)), 0.09, 0.05, "ruby", axis=(0, 1, 0), segs=8)
    for x in (-0.75, 0.75):
        m.obox(Vector((x, -0.97, 0.62)), (0.3, 0.025, 0.5), "teal")
        m.obox(Vector((x, -0.985, 0.66)), (0.2, 0.02, 0.07), "fur_mask")                             # mask emblem
        m.obox(Vector((x, -0.97, 0.36)), (0.3, 0.03, 0.04), "gold")
        m.obox(Vector((x * 1.47, -1.2, 0.3)), (0.05, 0.05, 0.6), "wood_dark")                        # torch posts
        m.obox(Vector((x * 1.47, -1.2, 0.64)), (0.09, 0.09, 0.1), "torch_orange")
        m.obox(Vector((x * 1.47, -1.2, 0.72)), (0.05, 0.05, 0.07), "flame_yellow")
    return m.obj("bld_guild_hall_3x3", coll)


BUILDINGS = [  # (fn, W, D, H, showcase position = footprint centre)
    (bld_den_2x2, 2, 2, 1, (0.5, 0.5)),
    (bld_stockpile_2x2, 2, 2, 1, (3.5, 0.5)),
    (bld_rummage_camp_2x2, 2, 2, 1, (6.5, 0.5)),
    (bld_guild_hall_3x3, 3, 3, 2, (10.0, 0.0)),
    (bld_woodpile_1x1, 1, 1, 1, (0.0, -3.0)),
    (bld_washing_pool_2x1, 2, 1, 1, (2.5, -3.0)),
    (bld_tinker_bench_1x1, 1, 1, 1, (5.0, -3.0)),
]


def check_bounds(ob, W, D, H):
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    ok = (min(xs) >= -W / 2 + IN - 1e-3 and max(xs) <= W / 2 - IN + 1e-3 and min(ys) >= -D / 2 + IN - 1e-3 and
          max(ys) <= D / 2 - IN + 1e-3 and min(zs) >= -1e-3 and max(zs) <= H + 1e-3)
    return ok, (round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3), round(max(zs), 3))


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    rnd = random.Random(5)
    obs, stats = [], {}
    for fn, W, D, H, pos in BUILDINGS:
        ob = fn(assets, rnd)
        ok, bb = check_bounds(ob, W, D, H)
        stats[ob.name] = (K.tris(ob), ok, bb)
        obs.append((ob, W, D, H, pos))
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_blockout.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rac = dst.objects[0]
    rac.name = "ref_raccoon"
    ref.objects.link(rac)
    rac.hide_render = True
    import build_template
    build_template.grid(ref, n=21)
    for n in ("ref_floor", "ref_grid_lines"):
        bpy.data.objects[n].location.x += 5
        bpy.data.objects[n].location.y += -1
    show = {}
    for ob, W, D, H, pos in obs:
        ob.hide_render = True
        show[ob.name] = K.instance(ob, ref, (pos[0], pos[1], 0))
    for nm, off, rot in (("bld_den_2x2", (-0.75, -1.2), 0.3), ("bld_guild_hall_3x3", (0.4, -1.75), -0.2),
                         ("bld_washing_pool_2x1", (0.3, -0.75), 0.0), ("bld_tinker_bench_1x1", (0.0, -0.3), 0.0),
                         ("bld_rummage_camp_2x2", (-0.2, -0.4), 0.6)):
        c = show[nm].location
        K.instance(rac, ref, (c.x + off[0], c.y + off[1], 0), rot=rot, name=f"ref_raccoon_{nm}")

    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "buildings_blockout.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})

    sc.render.engine = "CYCLES"
    sc.cycles.samples = 32
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    gc = bpy.data.objects["GameCam"]
    K.look(gc, (4.4, -1.4, 0.4), -30, 17.5)
    K.shoot(gc, out / "bld_blockout_gamecam.png", (1600, 1000))
    # close-ups from the game camera, one per building, into a contact sheet
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    tiles = []
    for ob, W, D, H, pos in obs:
        K.look(gc, (pos[0], pos[1], H * 0.3), -30, 2.2 + 1.35 * max(W, D, H * 0.8) + (1.4 if W == 3 else 0))
        f = out / f"_{ob.name}.png"
        K.shoot(gc, f, (640, 480))
        tiles.append((ob.name, f))
    sheet = Image.new("RGB", (640 * 4, 520 * 2), (24, 26, 32))
    d = ImageDraw.Draw(sheet)
    for i, (nm, f) in enumerate(tiles):
        x, y = 640 * (i % 4), 520 * (i // 4)
        sheet.paste(Image.open(f), (x, y))
        d.text((x + 12, y + 488), f"{nm}   {stats[nm][0]} tris", font=font, fill=(235, 236, 242))
        f.unlink()
    sheet.save(out / "bld_blockout_closeups.png")
    top = bpy.data.objects["TopCam"]
    top.data.ortho_scale = 14.0
    top.data.clip_end = 100
    top.location = (5.0, -1.2, 20)
    sun = bpy.data.objects["Sun"]
    sun.rotation_euler = (math.radians(15), math.radians(8), math.radians(-35))     # short shadows for the plan view
    K.shoot(top, out / "bld_blockout_topdown.png", (1600, 900))
    for n, (t, ok, bb) in stats.items():
        print(f"STAT {n}: {t} tris, inside footprint: {ok} {bb}")


if __name__ == "__main__":
    main()
