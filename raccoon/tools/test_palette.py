"""Batch 2 check: the palette on the reference raccoon + doorway, and a swatch board, from the game camera.
Renders under neutral light and under the cave mood (cool ambient + warm torch). Does not modify template.blend.

Run:  python3 tools/test_palette.py
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


def use_palette(ob):
    ob.data.materials.clear()
    ob.data.materials.append(bpy.data.materials["M_Palette"])


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    img = bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image
    img.reload()
    sc = bpy.context.scene
    # raccoon: grey body, darker feet/arms, ringed tail, cream muzzle, dark ears
    for name in ("ref_raccoon_0.4m", "ref_raccoon_in_door"):
        ob = bpy.data.objects[name]
        use_palette(ob)
        P.set_swatch(ob, "fur_mid")
        for p in ob.data.polygons:
            c = p.center
            if c.y > 0.09:                                    # tail rings
                P.set_swatch(ob, "fur_charcoal" if int((c.y - 0.09) / 0.045) % 2 else "fur_light", [p.index])
            elif c.z < 0.06 or (abs(c.x) > 0.07 and c.z < 0.2):
                P.set_swatch(ob, "fur_dark", [p.index])
            elif c.z > 0.33:
                P.set_swatch(ob, "fur_charcoal", [p.index])
            elif c.y < -0.055 and 0.22 < c.z < 0.26:
                P.set_swatch(ob, "fur_cream", [p.index])
            elif c.y < -0.04 and 0.06 < c.z < 0.2:
                P.set_swatch(ob, "fur_light", [p.index])  # belly
    for o in bpy.data.objects:
        if o.name.startswith("ref_raccoon_mask"):
            use_palette(o)
            P.set_swatch(o, "fur_mask")
    door = bpy.data.objects["ref_doorway_1x1"]
    use_palette(door)
    P.set_swatch(door, "stone_mid")
    for p in door.data.polygons:
        if abs(p.normal.y) < 0.5 and abs(p.normal.x) < 0.99 and p.center.z < 0.6 and abs(p.center.x) < 0.25:
            P.set_swatch(door, "stone_dark", [p.index])       # inside of the arch
        elif p.normal.z > 0.5:
            P.set_swatch(door, "stone_light", [p.index])      # top of the wall
    # swatch board: 8x8 little blocks over two cells, row 0 at the back
    bm = bmesh.new()
    lay = bm.faces.layers.int.new("sw")       # created before any face so face refs stay valid
    s = 0.2
    for name, (r, c, _) in P.SWATCH.items():
        res = bmesh.ops.create_cube(bm, size=1.0)
        h = 0.06 + 0.02 * (c % 2)
        pos = Vector((-1.38 + c * 0.25, 0.9 - r * 0.25, h / 2))
        bmesh.ops.transform(bm, matrix=Matrix.Translation(pos) @ Matrix.Diagonal((s, s, h, 1)), verts=res["verts"])
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f[lay] = r * 8 + c
    me = bpy.data.meshes.new("swatch_board")
    ids = [f[lay] for f in bm.faces]
    bm.to_mesh(me)
    bm.free()
    board = bpy.data.objects.new("swatch_board", me)
    sc.collection.objects.link(board)
    use_palette(board)
    names = list(P.SWATCH)
    for i, sid in enumerate(ids):
        P.set_swatch(board, names[sid], [i])
    board.location = (-0.2, -2.15, 0)
    # wider game camera to take in the board too
    cam = bpy.data.objects["GameCam"]
    target, pitch, yaw, dist = Vector((-0.2, -1.75, 0.1)), math.radians(50), math.radians(-30), 7.9
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    cam.location = target + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.render.resolution_x, sc.render.resolution_y = 1280, 800
    out = ROOT / "renders"
    sc.render.filepath = str(out / "palette_gamecam_neutral.png")
    bpy.ops.render.render(write_still=True)
    # cave mood: dim cool ambient, weak cool key, warm torch between the doorway and the board
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 0.6
    sun.data.color = (0.6, 0.72, 1.0)
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.03, 0.045, 0.09, 1)
    bg.inputs[1].default_value = 1.2
    torch = bpy.data.objects.new("torch", bpy.data.lights.new("torch", "POINT"))
    sc.collection.objects.link(torch)
    torch.location = (0.5, -0.9, 0.6)
    torch.data.energy = 40
    torch.data.color = (1.0, 0.62, 0.3)
    torch.data.shadow_soft_size = 0.08
    sc.render.filepath = str(out / "palette_gamecam_mood.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
