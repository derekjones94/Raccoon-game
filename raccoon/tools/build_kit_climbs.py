"""Climbing between levels: the stone stairs (kit_stairs_stone, unchanged), the chicken ladder (kit_ladder_wood) and
their clips, checked for clipping.

climb_stairs_up / climb_stairs_down (build_raccoon_jobs): one-way clips that hop the raccoon up or down the six
steps. The up clip starts on the floor in front of the stairs (spot_stairs_up, facing up them) and ends on the floor
above; the down clip starts there (spot_stairs_down, facing down) and ends in front, a hop past the up clip's start
(spot_stairs_off: its tail clear of the bottom step). The clips travel: the raccoon's
node stays on its spot, the body moves; when the clip ends, move the raccoon's node to where the body is (the other
spot's position) and carry on.

climb_ladder_up / climb_ladder_down: the same for the ladder, a cleated plank leaning on a back wall with a short deck
on the wall's top. Up: from the floor in front (spot_ladder_up, facing the plank), lean on, hop the feet up, then
scramble on all fours, paws reaching a cleat at a time, and stand on the deck (spot_ladder_down). Down: the climb up
backwards, from spot_ladder_down; that spot faces the same way (+Y): the raccoon backs down, facing the plank.

The check scenes: the stairs with the floor in front and the floor above (1 m up, past the top step); the ladder with
a wall and the floor in front. A raccoon on each clip, every frame checked (no body part into the steps / plank /
deck / wall; the feet land on each tread, 1.5 mm above it).

Run:  python3 tools/build_kit_climbs.py   (--no-renders)
Out:  kit_climbs.blend, kit_ladder_climbs.blend (the check scenes), export/kit_ladder_wood.glb,
      renders/kit_stairs_climb_*.gif, renders/kit_ladder_climb_*.gif, renders/qa_buildings.txt
"""
import os
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector


def stairs_scene(coll):
    """The stairs (root) with the floor in front and the floor above as its children, and a tiny keyed marker so the
    check walks the clips' frames."""
    import random
    root = K.kit_stairs_stone(coll, random.Random(1))
    m = B.M()
    m.obox(V((0, -0.75, -0.01)), (0.94, 0.5, 0.02), "stone_dark", top="stone_mid")                 # floor in front
    m.obox(V((0, 0.75, 1.0 - 0.01)), (0.94, 0.5, 0.02), "stone_dark", top="stone_mid")           # floor above
    floors = m.obj("qa_floors", coll)
    floors.parent = root
    m = B.M()
    m.obox(V((0.4, -0.4, 0.001)), (0.001, 0.001, 0.001), "soot")
    mk = A.part(m.obj("qa_clock", coll), root, V((0.4, -0.4, 0.001)))
    n = max(J.STAIRS_FRAMES, J.STAIRS_DOWN_FRAMES)                     # long enough for either clip
    A.animate({"qa_clock": mk}, {"idle": (n, lambda p: {}), "work": (n, lambda p: {})})
    return root


def ladder_scene(coll):
    """The ladder (root) with a wall behind it and the floor in front as its children, and the keyed marker."""
    import random
    root = K.kit_ladder_wood(coll, random.Random(1))
    wall = K.kit_wall_stone(coll, random.Random(1))
    wall.name = "qa_wall"
    wall.parent = root
    m = B.M()
    m.obox(V((0, -0.37, -0.01)), (0.94, 1.06, 0.02), "stone_dark", top="stone_mid")               # floor in front
    floors = m.obj("qa_floors", coll)
    floors.parent = root
    m = B.M()
    m.obox(V((0.4, -0.6, 0.001)), (0.001, 0.001, 0.001), "soot")
    mk = A.part(m.obj("qa_clock", coll), root, V((0.4, -0.6, 0.001)))
    A.animate({"qa_clock": mk}, {"idle": (J.LAD_FRAMES, lambda p: {}), "work": (J.LAD_FRAMES, lambda p: {})})
    return root


def ladder(do_renders):
    coll = A.open_template()
    root = ladder_scene(coll)
    A.spot(root, "spot_ladder_up", J.LAD_SPOT_UP, (0, 1, 0))
    A.spot(root, "spot_ladder_down", J.LAD_SPOT_DOWN, (0, 1, 0))      # backs down: faces the same way
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "kit_ladder_climbs.blend"), relative_remap=True)
    objs = []
    names = ("climb_ladder_up", "climb_ladder_down")
    for sp, clip in zip(("spot_ladder_up", "spot_ladder_down"), names):
        rig, mesh, _ = A.raccoon_at(bpy.data.objects[sp], clip=clip, blend=os.environ.get("RACCOON_BLEND"))
        objs.append((rig, mesh))
    for (rig, mesh), name in zip(objs, names):
        probs = A.check(root, 1, 1, H=2.0, crew=[(rig, mesh, None, "work", {"kit_ladder_wood": None})], allow=[
            ("qa_floors", "kit_ladder_wood"), ("qa_wall", "kit_ladder_wood"), ("qa_floors", "qa_wall"),
            ("qa_clock", "kit_ladder_wood")])
        probs = [p for p in probs if p[2] != "outside footprint"]
        A.report(f"kit_ladder_wood + {name}", probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        for (rig, mesh), name in zip(objs, ("up", "down")):
            other = [o for pair in objs if pair[0] is not rig for o in pair]
            for o in other:
                o.hide_render = True
            A.render_loops(root, [rig, mesh], ROOT / "renders" / f"kit_ladder_climb_{name}.gif",
                           target=(0.0, -0.1, 0.5), dist=3.0, pitch=18, yaw=-70, idle_frames=4, grid_n=3, step=2,
                           label=f"kit_ladder_wood  climb_ladder_{name}")
            for o in other:
                o.hide_render = False


def main():
    do_renders = "--no-renders" not in sys.argv
    if "--ladder-only" not in sys.argv:
        stairs(do_renders)
    ladder(do_renders)


def stairs(do_renders):
    coll = A.open_template()
    root = stairs_scene(coll)
    top = J.STAIR_STOPS[-1]
    A.spot(root, "spot_stairs_up", V((0, J.STAIR_STOPS[0][0], 0.0015)), (0, 1, 0))
    A.spot(root, "spot_stairs_down", V((0, top[0], top[1] + 0.0015)), (0, -1, 0))
    A.spot(root, "spot_stairs_off", V((0, J.STAIR_STOPS_DOWN[-1][0], 0.0015)), (0, -1, 0))   # where going down ends
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "kit_climbs.blend"), relative_remap=True)
    crew, objs = [], []
    for sp, clip, dx in (("spot_stairs_up", "climb_stairs_up", 0.0), ("spot_stairs_down", "climb_stairs_down", 0.0)):
        rig, mesh, _ = A.raccoon_at(bpy.data.objects[sp], clip=clip, blend=os.environ.get("RACCOON_BLEND"))   # (a preview bake)
        crew.append((rig, mesh, None, "work", {}))
        objs.append((rig, mesh))
    # one climber at a time (they'd pass each other on the stairs): check each alone
    for (rig, mesh, *_), name in zip(crew, ("climb_stairs_up", "climb_stairs_down")):
        probs = A.check(root, 1, 1, H=2.0, crew=[(rig, mesh, None, "work", {})], allow=[("qa_floors", "kit_stairs_stone"),
                        ("qa_clock", "kit_stairs_stone")])
        probs = [p for p in probs if p[2] != "outside footprint"]          # the floors reach past the piece on purpose
        A.report(f"kit_stairs_stone + {name}", probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        for (rig, mesh), name in zip(objs, ("up", "down")):
            other = [o for pair in objs if pair[0] is not rig for o in pair]
            for o in other:
                o.hide_render = True
            A.render_loops(root, [rig, mesh], ROOT / "renders" / f"kit_stairs_climb_{name}.gif",
                           target=(0.0, 0.0, 0.45), dist=3.0, pitch=24, yaw=-60, idle_frames=4, grid_n=3, step=2,
                           label=f"kit_stairs_stone  climb_stairs_{name}")
            for o in other:
                o.hide_render = False


if __name__ == "__main__":
    main()
