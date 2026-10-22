"""Batch 6: prop blockouts (50-300 tris each). Origin bottom-centre, front -Y, all inside one cell.

Run:  python3 tools/build_props_blockout.py
Out:  props_blockout.blend, export/prop_*.glb, renders/prop_*.png
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_buildings_blockout as B  # noqa: E402

ROOT = P.ROOT


def gem(m, c, r, sw, rot=0.0):
    """Octahedron-ish gem: two 4-sided cones base to base."""
    m.cyl(c + Vector((0, 0, r * 0.35)), r, r * 0.7, sw, segs=4, r2=0.0, rot=rot)
    m.cyl(c - Vector((0, 0, r * 0.35)), 0.0, r * 0.7, sw, segs=4, r2=r, rot=rot)


def coin(m, c, r=0.035, tilt=(0, 0, 1)):
    m.cyl(c, r, 0.012, "gold_light", cap="gold", axis=tilt, segs=6)


def prop_goldpile(coll, rnd):
    m = B.M()
    m.blob(Vector((0, 0, 0.0)), Vector((0.26, 0.23, 0.17)), "gold", 10, 6)               # mound (lower half buried, trimmed below)
    m.blob(Vector((0.08, 0.05, 0.1)), Vector((0.12, 0.1, 0.1)), "gold_light", 8, 4)      # a brighter heap on top
    for k in range(7):
        a = k / 7 * 2 * math.pi + rnd.uniform(-0.3, 0.3)
        r = rnd.uniform(0.24, 0.33)
        coin(m, Vector((math.cos(a) * r, math.sin(a) * r, 0.007)))
    coin(m, Vector((-0.08, -0.12, 0.13)), tilt=(0.3, -0.5, 1))
    m.cyl(Vector((-0.1, 0.05, 0.19)), 0.035, 0.07, "silver", r2=0.05, segs=6)            # a goblet poking out
    gem(m, Vector((0.12, -0.08, 0.13)), 0.035, "ruby")
    return m.obj("prop_goldpile", coll)


def prop_gemchest(coll, rnd):
    m = B.M()
    w, d, h = 0.34, 0.22, 0.16
    m.obox(Vector((0, 0, h / 2)), (w, d, h), "wood_mid", top="gold")                      # body (top reads as heaped gold)
    for x in (-w / 2 + 0.03, w / 2 - 0.03):
        m.obox(Vector((x, 0, h / 2)), (0.03, d + 0.012, h + 0.008), "iron_dark")         # iron bands
    m.obox(Vector((0, -d / 2 - 0.004, h - 0.03)), (0.05, 0.012, 0.05), "gold_light")      # lock plate
    # open lid, tipped back
    m.obox(Vector((0, d / 2 + 0.035, h + 0.07)), (w, 0.04, 0.16), "wood_dark", rot=(-0.35, 0, 0))
    m.obox(Vector((0, d / 2 + 0.03, h + 0.07)), (w + 0.01, 0.044, 0.03), "gold", rot=(-0.35, 0, 0))
    # treasure spilling out of the top
    for c, sw in (((-0.08, -0.02), "ruby"), ((0.02, 0.03), "sapphire"), ((0.1, -0.03), "emerald"), ((-0.02, -0.06), "amethyst")):
        gem(m, Vector((c[0], c[1], h + 0.03)), 0.035, sw, rot=rnd.uniform(0, 1))
    coin(m, Vector((0.16, -0.16, 0.007)))
    coin(m, Vector((0.22, -0.1, 0.007)))
    return m.obj("prop_gemchest", coll)


def prop_torch(coll, rnd):
    """Standing torch: stone foot, stick, cloth-wrapped head, layered flame (glows in-game)."""
    m = B.M()
    m.cyl(Vector((0, 0, 0.04)), 0.09, 0.08, "stone_mid", cap="stone_light", segs=7, r2=0.07)
    m.cyl(Vector((0, 0, 0.27)), 0.022, 0.4, "wood_mid", segs=6)
    m.cyl(Vector((0, 0, 0.48)), 0.045, 0.07, "rope_dark", cap="soot", segs=7, r2=0.05)
    m.cyl(Vector((0, 0, 0.565)), 0.055, 0.11, "torch_orange", segs=7, r2=0.0)
    m.cyl(Vector((0.005, -0.005, 0.56)), 0.036, 0.12, "flame_yellow", segs=6, r2=0.0, rot=0.3)
    m.cyl(Vector((0.0, -0.01, 0.55)), 0.018, 0.07, "flame_white", segs=5, r2=0.0)
    return m.obj("prop_torch", coll)


def prop_barrel(coll, rnd):
    m = B.M()
    r, h = 0.13, 0.32
    m.cyl(Vector((0, 0, 0.03)), r * 0.88, 0.06, "wood_mid", segs=10, r2=r)                 # bulged staves: 3 stacked frusta
    m.cyl(Vector((0, 0, h / 2)), r, h - 0.12, "wood_mid", segs=10)
    m.cyl(Vector((0, 0, h - 0.03)), r, 0.06, "wood_mid", cap="wood_light", segs=10, r2=r * 0.88)
    for z in (0.06, h - 0.06):
        m.cyl(Vector((0, 0, z)), r * 1.04, 0.025, "iron", segs=10)
    m.obox(Vector((0, 0, h + 0.003)), (r * 1.3, 0.025, 0.006), "wood_dark")               # lid plank seam
    return m.obj("prop_barrel", coll)


def prop_crate(coll, rnd):
    m = B.M()
    s = 0.3
    m.obox(Vector((0, 0, s / 2)), (s - 0.02, s - 0.02, s - 0.02), "wood_mid", top="wood_light")
    t = 0.03                                                                              # frame boards on the edges
    for x in (-1, 1):
        for y in (-1, 1):
            m.obox(Vector((x * (s / 2 - t / 2), y * (s / 2 - t / 2), s / 2)), (t * 1.15, t * 1.15, s + 0.004), "wood_dark")  # posts cover rail ends
    for z in (t / 2, s - t / 2):
        for y in (-1, 1):
            m.obox(Vector((0, y * (s / 2 - t / 2), z)), (s, t, t), "wood_dark")
        for x in (-1, 1):
            m.obox(Vector((x * (s / 2 - t / 2), 0, z)), (t, s, t), "wood_dark")
    m.obox(Vector((0, -s / 2 + 0.002, s / 2)), (0.11, 0.006, 0.11), "teal", rot=(0, 0.785, 0))   # guild stencil
    return m.obj("prop_crate", coll)


def prop_mushrooms(coll, rnd):
    """Glowing cave mushrooms: 4 of different heights, caps with pale spots (caps glow in-game)."""
    m = B.M()
    for (x, y, h, r, cap) in ((0.0, 0.02, 0.22, 0.09, "mushroom_glow"), (0.12, -0.06, 0.13, 0.06, "amethyst"),
                              (-0.11, -0.05, 0.1, 0.055, "mushroom_glow"), (0.06, 0.12, 0.08, 0.045, "amethyst")):
        m.cyl(Vector((x, y, h / 2)), r * 0.32, h, "bone", segs=6, r2=r * 0.26)
        m.cyl(Vector((x, y, h + r * 0.18)), r, r * 0.45, cap, segs=8, r2=r * 0.35)          # cap
        m.cyl(Vector((x, y, h - 0.004)), r * 0.95, 0.008, "fur_cream", segs=6)              # gills underside
    m.blob(Vector((0.0, 0.0, 0.0)), Vector((0.2, 0.17, 0.035)), "moss", 7, 4)              # mossy base
    return m.obj("prop_mushrooms", coll)


PROPS = [prop_goldpile, prop_gemchest, prop_torch, prop_barrel, prop_crate, prop_mushrooms]


def trim_below_floor(ob):
    """Mounds are half spheres: flatten anything under z 0 onto the floor, then drop faces lying flat on the
    floor (never seen from the game camera; saves the hidden half of every mound)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z < 1e-5 for v in f.verts)], context="FACES")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    rnd = random.Random(6)
    obs, stats = [], {}
    for fn in PROPS:
        ob = fn(assets, rnd)
        trim_below_floor(ob)
        ok, bb = B.check_bounds(ob, 1, 1, 1)
        stats[ob.name] = (K.tris(ob), ok, tuple(round(v, 2) for v in ob.dimensions))
        obs.append(ob)
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_blockout.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rac = dst.objects[0]
    rac.name = "ref_raccoon"
    ref.objects.link(rac)
    rac.hide_render = True
    import build_template
    build_template.grid(ref, n=9)
    for n in ("ref_floor", "ref_grid_lines"):
        bpy.data.objects[n].location.x += 2
    show = {}
    for i, ob in enumerate(obs):
        ob.hide_render = True
        show[ob.name] = K.instance(ob, ref, ((i % 3) * 2, -(i // 3) * 2 + 1, 0))
    for i, ob in enumerate(obs):
        c = show[ob.name].location
        K.instance(rac, ref, (c.x + 0.42, c.y + 0.08, 0), rot=0.5, name=f"ref_raccoon_{ob.name}")     # beside, not in front

    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "props_blockout.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})

    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    gc = bpy.data.objects["GameCam"]
    K.look(gc, (2.1, -0.45, 0.1), -30, 8.2)
    K.shoot(gc, out / "prop_blockout_gamecam.png", (1500, 950))
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    tiles = []
    for ob in obs:
        c = show[ob.name].location
        K.look(gc, (c.x + 0.12, c.y, max(0.12, ob.dimensions.z * 0.45)), -30, 1.9)
        f = out / f"_{ob.name}.png"
        K.shoot(gc, f, (600, 450))
        tiles.append((ob.name, f))
    sheet = Image.new("RGB", (600 * 3, 490 * 2), (24, 26, 32))
    d = ImageDraw.Draw(sheet)
    for i, (nm, f) in enumerate(tiles):
        x, y = 600 * (i % 3), 490 * (i // 3)
        sheet.paste(Image.open(f), (x, y))
        d.text((x + 12, y + 458), f"{nm}   {stats[nm][0]} tris", font=font, fill=(235, 236, 242))
        f.unlink()
    sheet.save(out / "prop_blockout_closeups.png")
    # cave mood: cool dim ambient, warm torch light, cyan mushroom light, gold catches the torch
    sun = bpy.data.objects["Sun"]
    sun.data.energy, sun.data.color = 0.5, (0.6, 0.72, 1.0)
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.03, 0.045, 0.09, 1), 1.2
    for nm, col, e, dz in (("prop_torch", (1.0, 0.6, 0.28), 25, 0.58), ("prop_mushrooms", (0.45, 0.95, 0.9), 6, 0.3)):
        L = bpy.data.objects.new("L_" + nm, bpy.data.lights.new("L_" + nm, "POINT"))
        sc.collection.objects.link(L)
        c = show[nm].location
        L.location = (c.x, c.y - 0.05, dz)
        L.data.energy, L.data.color, L.data.shadow_soft_size = e, col, 0.05
    K.look(gc, (2.1, -0.45, 0.1), -30, 8.2)
    K.shoot(gc, out / "prop_blockout_gamecam_mood.png", (1500, 950))
    top = bpy.data.objects["TopCam"]
    top.data.ortho_scale = 6.5
    top.location = (2.0, 0.0, 20)
    top.data.clip_end = 100
    sun.data.energy, sun.data.color = 3.0, (1, 1, 1)
    sun.rotation_euler = (math.radians(15), math.radians(8), math.radians(-35))
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.05, 0.06, 0.09, 1), 1.5
    for o in bpy.data.objects:
        if o.name.startswith("L_prop"):
            o.hide_render = True
    K.shoot(top, out / "prop_blockout_topdown.png", (1200, 900))
    for n, (t, ok, dims) in stats.items():
        print(f"STAT {n}: {t} tris, inside cell: {ok}, size {dims}")


if __name__ == "__main__":
    main()
