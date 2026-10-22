"""Batch 1: template.blend for the raccoon colony game.

  * Metric, unit scale 1.0, 1 m = 1 Godot unit = 1 grid cell; snapping to whole/increment grid
  * M_Palette: the one shared material (palette.png, closest filtering)
  * Reference collection (never exported): 1x1x1 wire cube, 0.4 m raccoon silhouette, 1-cell doorway, grid
  * Assets collection: where models go (export_assets.py exports each object in it as its own .glb)

Run:  python3 tools/build_template.py
"""
import math
from pathlib import Path

import bpy  # noqa: I001  (bpy first: it makes bmesh importable)
import bmesh
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
INSET = 0.03
RACCOON_H = 0.40
DOOR_W, DOOR_H = 0.36, 0.52          # raccoon-sized opening (0.4 m raccoon + ears/clearance)
WALL_T = 0.30                        # chunky wall thickness


def placeholder_palette(path):
    """Neutral 8x8 swatch grid so the material has an image until batch 2 delivers the real palette."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (128, 128))
    d = ImageDraw.Draw(im)
    for r in range(8):
        for c in range(8):
            v = 70 + 18 * ((r + c) % 2) + 6 * r
            d.rectangle([c * 16, r * 16, c * 16 + 15, r * 16 + 15], fill=(v, v, v + 8))
    im.save(path)


def palette_material(img_path):
    m = bpy.data.materials.new("M_Palette")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.9
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(img_path), check_existing=True)
    t.image.filepath = "//textures/palette.png"
    t.interpolation = "Closest"
    m.use_fake_user = True              # kept in the file even before any model uses it
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m


def ref_material(name, rgb, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = 0.8
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    m.diffuse_color = (*rgb, alpha)
    return m


def mesh_obj(name, bm, coll, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


def wire_cube(coll):
    """1x1x1 cell, origin bottom-centre, edges only."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for z in (0, 1) for y in (-0.5, 0.5) for x in (-0.5, 0.5)]
    for a, b in ((0, 1), (2, 3), (0, 2), (1, 3), (4, 5), (6, 7), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)):
        bm.edges.new((vs[a], vs[b]))
    ob = mesh_obj("ref_cell_1x1x1", bm, coll)
    ob.display_type = "WIRE"
    ob.show_in_front = True
    # render version: thin bars along each edge so it shows up in renders
    bm = bmesh.new()
    t = 0.008
    for a, b in ((0, 1), (2, 3), (0, 2), (1, 3), (4, 5), (6, 7), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)):
        p, q = vs_pos(a), vs_pos(b)
        c = (p + q) / 2
        size = Vector((abs(q.x - p.x) or t, abs(q.y - p.y) or t, abs(q.z - p.z) or t))
        r = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*size, 1)), verts=r["verts"])
    bars = mesh_obj("ref_cell_bars", bm, coll, ref_material("ref_white", (0.9, 0.92, 1.0)))
    bars.hide_viewport = True          # viewport uses the wire version; renders use the bars
    ob.hide_render = True
    return ob


def vs_pos(i):
    return Vector(((-0.5, 0.5)[i & 1], (-0.5, 0.5)[(i >> 1) & 1], (0, 1)[(i >> 2) & 1]))


def ellipsoid(bm, c, r, segs=10, rings=6):
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*r, 1)), verts=res["verts"])


def raccoon_silhouette(coll):
    """0.4 m standing raccoon, primitives only: scale reference, not the character."""
    bm = bmesh.new()
    H = RACCOON_H
    ellipsoid(bm, Vector((0, 0.01, 0.13)), Vector((0.085, 0.075, 0.10)))         # body / belly
    ellipsoid(bm, Vector((0, 0.0, 0.265)), Vector((0.085, 0.075, 0.075)))       # big head
    ellipsoid(bm, Vector((0, -0.075, 0.25)), Vector((0.03, 0.035, 0.022)), 8, 4)  # muzzle
    for sx in (1, -1):
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.032, radius2=0.004, depth=0.07)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((sx * 0.05, 0.01, H - 0.034)) @ Matrix.Rotation(-sx * 0.35, 4, "Y"),
                            verts=r["verts"])                                   # ears to 0.40 m
        ellipsoid(bm, Vector((sx * 0.045, -0.01, 0.03)), Vector((0.03, 0.045, 0.03)), 8, 4)   # feet
        ellipsoid(bm, Vector((sx * 0.085, -0.03, 0.15)), Vector((0.022, 0.022, 0.05)), 6, 4)  # arms
    for k in range(4):                                                          # big fluffy tail, behind (+Y)
        ellipsoid(bm, Vector((0, 0.11 + 0.05 * k, 0.07 + 0.045 * k)), Vector((0.05 - 0.004 * k, 0.05, 0.05 - 0.004 * k)), 8, 5)
    ob = mesh_obj("ref_raccoon_0.4m", bm, coll, ref_material("ref_raccoon", (0.45, 0.43, 0.42)))
    # dark mask band
    bm = bmesh.new()
    ellipsoid(bm, Vector((0, -0.06, 0.275)), Vector((0.075, 0.025, 0.022)), 8, 4)
    mesh_obj("ref_raccoon_mask", bm, coll, ref_material("ref_mask", (0.06, 0.05, 0.05)))
    return ob


def doorway(coll):
    """1-cell stone wall with a raccoon-sized arched opening. Wall runs along X; placed on the cell's back (+Y) edge.
    Ends run to the cell edge (they meet the neighbouring wall face to face, hidden); the outer face is inset."""
    bm = bmesh.new()
    x0, x1 = -0.5, 0.5
    y0, y1 = -WALL_T / 2, WALL_T / 2
    # front/back outlines: rectangle with the arch cut out, built as a polygon ring
    arch = []
    hw = DOOR_W / 2
    spring = DOOR_H - hw                       # semicircular arch on top
    arch.append((-hw, 0.0))
    for k in range(9):
        a = math.pi - math.pi * k / 8
        arch.append((math.cos(a) * hw, spring + math.sin(a) * hw))
    arch.append((hw, 0.0))
    outer = [(x1, 0.0), (x1, 1.0), (x0, 1.0), (x0, 0.0)]
    # build faces: two sides, each = outer quad minus arch -> fan the region between arch and outer edge
    front, back = [], []
    for y, store in ((y0, front), (y1, back)):
        store.append([bm.verts.new((x, y, z)) for x, z in arch])
        store.append([bm.verts.new((x, y, z)) for x, z in outer])
    for side, flip in ((front, False), (back, True)):
        a, o = side
        # left piece: x0 bottom -> arch start
        polys = [[o[3], a[0]] + a[1:6] + [o[2]],          # left of the arch crown
                 a[5:11] + [o[0], o[1], o[2]]]            # right of it + the top
        for p in polys:
            bm.faces.new(list(reversed(p)) if flip else p)
    # thickness: outer box sides + arch tunnel
    fa, fo = front
    ba, bo = back
    for i in range(4):
        j = (i + 1) % 4
        if (i, j) == (3, 0):     # bottom between x0 and x1 is open where the door is: split around the arch
            bm.faces.new((fo[3], bo[3], ba[0], fa[0]))
            bm.faces.new((fa[-1], ba[-1], bo[0], fo[0]))
            continue
        bm.faces.new((fo[i], fo[j], bo[j], bo[i]))
    for i in range(len(fa) - 1):
        bm.faces.new((fa[i], fa[i + 1], ba[i + 1], ba[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj("ref_doorway_1x1", bm, coll, ref_material("ref_stone", (0.32, 0.38, 0.46)))


def grid(coll, n=7):
    """Floor + cell lines for renders (Reference only)."""
    bm = bmesh.new()
    r = bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=n / 2)
    floor = mesh_obj("ref_floor", bm, coll, ref_material("ref_floor", (0.12, 0.14, 0.18)))
    floor.location.z = -0.002
    bm = bmesh.new()
    t = 0.012
    for k in range(n + 1):
        c = -n / 2 + k
        for size, pos in (((n, t, 0.002), (0, c, 0)), ((t, n, 0.002), (c, 0, 0))):
            r = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.transform(bm, matrix=Matrix.Translation(pos) @ Matrix.Diagonal((*size, 1)), verts=r["verts"])
    mesh_obj("ref_grid_lines", bm, coll, ref_material("ref_grid", (0.35, 0.45, 0.6)))
    return floor


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    us = sc.unit_settings
    us.system, us.scale_length, us.length_unit = "METRIC", 1.0, "METERS"
    ts = sc.tool_settings
    ts.use_snap = True
    ts.snap_elements = {"INCREMENT"}
    ts.use_snap_grid_absolute = True       # snaps to the 1 m world grid, not relative steps
    pal = ROOT / "textures" / "palette.png"
    if not pal.exists():
        placeholder_palette(pal)
    palette_material(pal)

    ref = bpy.data.collections.new("Reference")
    ref.color_tag = "COLOR_01"
    ref["no_export"] = True
    sc.collection.children.link(ref)
    assets = bpy.data.collections.new("Assets")
    assets.color_tag = "COLOR_04"
    sc.collection.children.link(assets)

    wire_cube(ref)
    rac = raccoon_silhouette(ref)
    door = doorway(ref)
    grid(ref)
    # lay the references out on neighbouring cells
    door.location = (1, 0.5 - INSET - WALL_T / 2, 0)      # on the back edge
    rac.location = (0, 0, 0)
    bpy.data.objects["ref_raccoon_mask"].location = rac.location
    for o in ref.objects:
        if o.type == "MESH":
            o.hide_select = o.name.startswith(("ref_floor", "ref_grid"))
    # a raccoon walking through the doorway, for scale
    rac2 = rac.copy()
    rac2.name = "ref_raccoon_in_door"
    ref.objects.link(rac2)
    m2 = bpy.data.objects["ref_raccoon_mask"].copy()
    ref.objects.link(m2)
    rac2.location = m2.location = (1, 0.5 - INSET - WALL_T / 2 - 0.05, 0)

    # game camera: perspective, 50 deg down (saved in the file so every asset is checked from it)
    cam = bpy.data.objects.new("GameCam", bpy.data.cameras.new("GameCam"))
    ref.objects.link(cam)
    cam.data.lens = 50
    cam.data.sensor_width = 36
    target = Vector((0.5, 0, 0.35))
    pitch = math.radians(50)
    yaw = math.radians(-30)
    dist = 4.2
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    cam.location = target + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    top = bpy.data.objects.new("TopCam", bpy.data.cameras.new("TopCam"))
    ref.objects.link(top)
    top.data.type = "ORTHO"
    top.data.ortho_scale = 4.0
    top.location = (0.5, 0, 10)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    ref.objects.link(sun)
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(-35))
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.5

    txt = bpy.data.texts.new("export_assets.py")
    txt.write((ROOT / "tools" / "export_assets.py").read_text())
    for o in list(sc.collection.all_objects):
        o.select_set(False)
    out = ROOT / "template.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out), relative_remap=True)
    render(sc, cam, top)


def render(sc, cam, top):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 32
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x, sc.render.resolution_y = 1280, 800
    for name, c in (("template_gamecam", cam), ("template_topdown", top)):
        sc.camera = c
        if c is top:
            sc.render.resolution_x, sc.render.resolution_y = 1000, 1000
        sc.render.filepath = str(ROOT / "renders" / f"{name}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
