"""Close-up review sheet for the raccoon's joins (shoulder/arm/paw, ear, leg/foot, whiskers) + bend tests."""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_raccoon_rig as RR  # noqa: E402
import build_raccoon_blockout as RB  # noqa: E402

ROOT = RR.ROOT
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "chr_raccoon_rigged.blend"))
sc = bpy.context.scene
rig = bpy.data.objects["chr_raccoon"]
for o in bpy.data.objects:
    if o.type == "MESH":
        o.hide_render = o.name != "chr_raccoon_mesh"
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.18, 0.23, 1)
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
sc.render.engine = "CYCLES"
sc.cycles.samples = 24
sc.view_settings.view_transform = "Standard"
sc.render.resolution_x = sc.render.resolution_y = 420
SHOTS = [  # label, pose, ortho size, target, view direction
    ("front (game look)", "game look (HANG)", 0.5, (0, 0, 0.2), (0, -1, 0.12)),
    ("three-quarter", "game look (HANG)", 0.5, (0, 0, 0.2), (0.6, -0.8, 0.45)),
    ("shoulder > arm > paw", "game look (HANG)", 0.2, (0.075, -0.03, 0.15), (0.75, -0.6, 0.25)),
    ("ear + inner panel", "game look (HANG)", 0.13, (0.05, -0.01, 0.34), (0.35, -0.9, 0.25)),
    ("leg > foot", "game look (HANG)", 0.16, (0.05, -0.02, 0.06), (0.8, -0.55, 0.2)),
    ("whiskers", "game look (HANG)", 0.16, (0, -0.07, 0.25), (0.25, -0.95, 0.15)),
    ("rest: A-pose", "rest: A-pose", 0.55, (0, 0, 0.2), (0, -1, 0.12)),
    ("elbows", "elbows", 0.55, (0, 0, 0.2), (0, -1, 0.12)),
    ("knees (squat)", "knees (squat)", 0.5, (0, 0, 0.17), (0.6, -0.8, 0.3)),
]
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
tiles = []
for lab, pose, size, tgt, d in SHOTS:
    RR.apply_pose(rig, pose, RB.ADULT)
    cam.data.ortho_scale = size
    d = Vector(d).normalized()
    cam.location = Vector(tgt) + d * 3
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    f = ROOT / "renders" / f"_{len(tiles)}.png"
    sc.render.filepath = str(f)
    bpy.ops.render.render(write_still=True)
    tiles.append((lab, f))
sheet = Image.new("RGB", (420 * 3, 450 * 3), (24, 26, 32))
dd = ImageDraw.Draw(sheet)
for i, (lab, f) in enumerate(tiles):
    x, y = 420 * (i % 3), 450 * (i // 3)
    sheet.paste(Image.open(f), (x, y))
    dd.text((x + 10, y + 424), lab, font=font, fill=(235, 236, 242))
    f.unlink()
sheet.save(ROOT / "renders" / "raccoon_details.png")
