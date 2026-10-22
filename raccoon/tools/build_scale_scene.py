"""Batch 7: scale reference scene. One of everything (plus the repeats a real layout needs) on the grid.

Pulls the approved blockouts from their .blend files, places them on whole cells:
  1x1 / 3x3 footprints centre on a cell (integer x, y); 2x2 on a cell corner (+0.5, +0.5); 2x1 on (+0.5, 0).
Nothing here is exported: it's a review / layout file.

Run:  python3 tools/build_scale_scene.py
Out:  scale_reference.blend, renders/scale_*.png, scale_stats.txt
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402

ROOT = P.ROOT
SOURCES = {
    "chr_raccoon_blockout.blend": ["chr_raccoon", "chr_raccoon_kit", "chr_raccoon_elder"],
    "kit_blockout.blend": ["kit_floor_stone", "kit_wall_stone", "kit_wall_stone_door", "kit_wall_stone_corner",
                           "kit_ramp_stone", "kit_stairs_stone", "kit_scaffold_wood", "kit_ladder_wood"],
    "buildings_blockout.blend": ["bld_den_2x2", "bld_stockpile_2x2", "bld_rummage_camp_2x2", "bld_woodpile_1x1",
                                 "bld_washing_pool_2x1", "bld_tinker_bench_1x1", "bld_guild_hall_3x3"],
    "props_blockout.blend": ["prop_goldpile", "prop_gemchest", "prop_torch", "prop_barrel", "prop_crate", "prop_mushrooms"],
}
R90 = math.pi / 2

# (asset, x, y, z, rotation) -- rotation in 90 degree steps about Z
LAYOUT = [
    # buildings
    ("bld_guild_hall_3x3", 0, 3, 0, 0),
    ("bld_den_2x2", -3.5, 3.5, 0, 0),
    ("bld_stockpile_2x2", 3.5, 3.5, 0, 0),
    ("bld_rummage_camp_2x2", 6.5, 0.5, 0, 0),
    ("bld_woodpile_1x1", 5, 3, 0, 0),
    ("bld_washing_pool_2x1", -3.5, 0, 0, 0),
    ("bld_tinker_bench_1x1", 3, 0, 0, 0),
    # kit: a walled tunnel mouth at the back left (door in the back wall leads deeper into the mountain)
    *[("kit_floor_stone", x, y, 0, 0) for x in (-4, -3, -2) for y in (6, 7)],
    ("kit_wall_stone_corner", -4, 7, 0, R90),        # back + left edges
    ("kit_wall_stone_door", -3, 7, 0, 0),
    ("kit_wall_stone_corner", -2, 7, 0, 0),          # back + right edges
    ("kit_wall_stone", -4, 6, 0, R90),               # left edge
    ("kit_wall_stone", -2, 6, 0, -R90),              # right edge
    # kit: the climb at the back right: ramp (from the front) and stairs (from the left) up onto the scaffold
    ("kit_scaffold_wood", 2, 7, 0, 0),
    ("kit_ramp_stone", 2, 6, 0, 0),
    ("kit_stairs_stone", 1, 7, 0, -R90),             # climbs toward +X, onto the scaffold
    ("kit_wall_stone", 3, 7, 0, 0),
    ("kit_ladder_wood", 3, 7, 0, 0),                 # leans on the wall in its own cell, top at z 1
    # props
    ("prop_torch", -1, 1, 0, 0),
    ("prop_torch", 1, 1, 0, 0),
    ("prop_goldpile", -1, 6, 0, 0),
    ("prop_gemchest", 0, 6, 0, 0),
    ("prop_barrel", 5, 2, 0, 0),
    ("prop_crate", 4, 1, 0, 0),
    ("prop_crate", 4.12, 1.08, 0.3, 0.3),            # stacked
    ("prop_mushrooms", -6, 3, 0, 0),
    ("prop_mushrooms", 6, 5, 0, R90),
    # raccoons
    ("chr_raccoon", 0, 0.6, 0, 0),
    ("chr_raccoon", 2, 7, 1.0, 0.6),                 # on the scaffold deck
    ("chr_raccoon", -3, 6.6, 0.09, 0.2),             # in the tunnel doorway
    ("chr_raccoon", 3.2, -0.45, 0, 2.8),             # at the tinker bench
    ("chr_raccoon_kit", -3.0, -0.75, 0, 0.4),
    ("chr_raccoon_kit", -2.55, -0.6, 0, -0.5),
    ("chr_raccoon_elder", -3.5, 1.95, 0, 0.3),        # at the den door
]


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    lib = {}
    for blend, names in SOURCES.items():
        with bpy.data.libraries.load(str(ROOT / blend)) as (src, dst):
            dst.objects = list(names)          # a copy: the loader swaps the names for objects in place
        for o in dst.objects:
            lib[o.name] = o
    # one palette material for everything (appending brought in copies)
    pal = bpy.data.materials["M_Palette"]
    for o in lib.values():
        o.data.materials.clear()
        o.data.materials.append(pal)
    layout = bpy.data.collections.new("Layout")
    sc.collection.children.link(layout)
    counts = {}
    for name, x, y, z, rot in LAYOUT:
        o = lib[name].copy()
        layout.objects.link(o)
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, rot)
        o.hide_render = False
        counts[name] = counts.get(name, 0) + 1
    import build_template
    build_template.grid(ref, n=21)
    for n in ("ref_floor", "ref_grid_lines"):
        bpy.data.objects[n].location += Vector((0, 2, 0))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "scale_reference.blend"), relative_remap=True)

    # stats
    lines = ["asset                       tris   placed", "-" * 44]
    total = 0
    for name in [n for names in SOURCES.values() for n in names]:
        t = tris(lib[name])
        lines.append(f"{name:<27} {t:>5}   x{counts.get(name, 0)}")
        total += t * counts.get(name, 0)
    lines.append("-" * 44)
    lines.append(f"scene total (all placed)    {total:>5}")
    (ROOT / "scale_stats.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    gc = bpy.data.objects["GameCam"]
    gc.data.clip_end = 200
    K.look(gc, (0.6, 2.6, 0.3), -30, 21.0)
    K.shoot(gc, out / "scale_gamecam_wide.png", (1920, 1200))
    K.look(gc, (-0.4, 3.4, 0.4), -30, 11.0)
    K.shoot(gc, out / "scale_gamecam_mid.png", (1920, 1200))
    # cave mood: dim cool ambient + warm lights at every flame / lamp + cyan at mushrooms + a gold glow
    sun = bpy.data.objects["Sun"]
    sun.data.energy, sun.data.color = 0.45, (0.6, 0.72, 1.0)
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.03, 0.045, 0.09, 1), 1.1
    warm, cyan, gold = (1.0, 0.6, 0.28), (0.45, 0.95, 0.9), (1.0, 0.8, 0.35)
    lights = [((-1, 1 - 0.05, 0.6), warm, 22), ((1, 1 - 0.05, 0.6), warm, 22),                   # standing torches
              ((-1.1, 1.8, 0.72), warm, 14), ((1.1, 1.8, 0.72), warm, 14),                       # guild hall torches
              ((6.5 - 0.62, 0.5 - 0.75, 0.76), warm, 10), ((3 - 0.3, 0.2, 0.5), warm, 5),        # lantern, tinker lamp
              ((-3.5, 2.6, 0.3), warm, 6), ((-3, 6.2, 0.6), warm, 10),                            # den door, tunnel mouth
              ((-6, 3, 0.3), cyan, 6), ((6, 5, 0.3), cyan, 6), ((-1, 5.9, 0.35), gold, 6)]
    for i, (loc, col, e) in enumerate(lights):
        L = bpy.data.objects.new(f"L{i}", bpy.data.lights.new(f"L{i}", "POINT"))
        sc.collection.objects.link(L)
        L.location, L.data.color, L.data.energy, L.data.shadow_soft_size = loc, col, e, 0.06
    K.shoot(gc, out / "scale_gamecam_mid_mood.png", (1920, 1200))
    for i in range(len(lights)):
        bpy.data.objects[f"L{i}"].hide_render = True
    sun.data.energy, sun.data.color = 3.0, (1, 1, 1)
    sun.rotation_euler = (math.radians(15), math.radians(8), math.radians(-35))
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.05, 0.06, 0.09, 1), 1.5
    top = bpy.data.objects["TopCam"]
    top.data.ortho_scale = 16.5
    top.data.clip_end = 100
    top.location = (0.5, 3.0, 30)
    K.shoot(top, out / "scale_topdown.png", (1650, 1050))


if __name__ == "__main__":
    main()
