"""bld_kit_swing_1x1: a tyre swing on a frame, for the kits. A decoration, best outdoors.

A timber A-frame with a crossbar; from it a rope runs down to a ring, and three ropes from the ring to an old tyre
hung flat (the two side ropes kink where the kit's paws pull them in). A kit sits on the tyre's back rim holding the two side ropes and pumps with its legs (spot_swing:
chr_raccoon_kit's work_swing). Trodden earth under it, a few dandelions, a ball someone left.

The spot is a child of the swinging node `pr_swing`: parent the kit to the spot and it swings with the tyre.

Clips (24 fps)
  idle  48 fr  the empty swing sways a little, turning on its rope
  work  48 fr  a kit on it: the swing goes back and forth (build_raccoon_jobs.swing_angle), in step with the kit's
               pumping legs in work_swing: start them together

Run:  python3 tools/build_kit_swing.py   (--no-renders)
Out:  kit_swing.blend, export/bld_kit_swing_1x1.glb, renders/bld_kit_swing_loops.gif
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_kit_swing_1x1"
FRAMES = 48
BAR_Z = 0.95
PIVOT = V((0, 0, BAR_Z))
TYRE_TOP = 0.26                                  # the flat tyre's top face
TYRE_R, TYRE_IN, TYRE_H = 0.17, 0.09, 0.07
RING = V((0, 0, TYRE_TOP + 0.5))                 # where the three ropes meet
SPOT = V((0, 0.12, TYRE_TOP + 0.0015))           # the kit, on the back rim, facing the front (-Y)


def tyre(m, c):
    """A flat tyre: a closed ring with a rounded look from two stacked rings, tread notches round the outside."""
    n = 14
    for z0, z1, r0, r1, sw in ((c.z - TYRE_H, c.z - TYRE_H * 0.5, TYRE_IN + 0.01, TYRE_R - 0.012, "soot"),
                               (c.z - TYRE_H * 0.5, c.z, TYRE_IN, TYRE_R, "fur_dark")):
        pts = [(math.cos(TAU * k / n), math.sin(TAU * k / n)) for k in range(n)]
        vs = {key: [m.bm.verts.new(V((c.x + r * a, c.y + r * b, z))) for a, b in pts] for key, (r, z) in
              {"ib": (r0, z0), "ob": (r1, z0), "it": (r0, z1), "ot": (r1, z1)}.items()}
        fs = []
        for k in range(n):
            j = (k + 1) % n
            fs.append(m.bm.faces.new((vs["it"][k], vs["ot"][k], vs["ot"][j], vs["it"][j])))
            fs.append(m.bm.faces.new((vs["ib"][k], vs["ib"][j], vs["ob"][j], vs["ob"][k])))
            fs.append(m.bm.faces.new((vs["ob"][k], vs["ob"][j], vs["ot"][j], vs["ot"][k])))
            fs.append(m.bm.faces.new((vs["ib"][k], vs["it"][k], vs["it"][j], vs["ib"][j])))
        m.tag(fs, sw)
    for k in range(n):                                                               # tread notches
        a = TAU * (k + 0.5) / n
        m.obox(V((c.x + (TYRE_R + 0.001) * math.cos(a), c.y + (TYRE_R + 0.001) * math.sin(a), c.z - TYRE_H * 0.25)),
               (0.006, 0.02, TYRE_H * 0.4), "soot", rot=(0, 0, a))


def build(coll, rnd, grips):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (0.94, 0.94, 0.004), "moss")
    m.blob(V((0, 0, -0.015)), V((0.32, 0.3, 0.02)), "wood_weathered", 10, 3)                       # trodden earth
    for sx in (-1, 1):                                                                              # the A-frame
        x = sx * 0.4
        for sy in (-1, 1):
            m.beam(V((x, sy * 0.3, 0.0)), V((x, 0.0, BAR_Z + 0.02)), 0.035, "wood_mid")
        m.beam(V((x, -0.16, 0.42)), V((x, 0.16, 0.42)), 0.025, "wood_dark")
        for sy in (-1, 1):
            m.blob(V((x, sy * 0.3, 0.01)), V((0.04, 0.04, 0.02)), "stone_mid", 5, 3)
    m.beam(V((-0.45, 0, BAR_Z + 0.03)), V((0.45, 0, BAR_Z + 0.03)), 0.04, "wood_dark")                # crossbar
    m.cyl(V((0, 0, BAR_Z + 0.006)), 0.018, 0.03, "iron", segs=6, axis=(1, 0, 0))                    # the hook
    for k in range(5):                                                                              # dandelions
        a = rnd.uniform(0, TAU)
        r = rnd.uniform(0.33, 0.42)
        c = V((r * math.cos(a), r * math.sin(a), 0.0))
        m.beam(c, c + V((0, 0, 0.05)), 0.004, "moss")
        m.blob(c + V((0, 0, 0.055)), V((0.012, 0.012, 0.008)), "gold_light" if k % 2 else "cloth_cream", 5, 3)
    m.blob(V((-0.3, -0.33, 0.035)), V((0.035, 0.035, 0.035)), "cloth_red", 8, 4)                  # a ball
    m.obox(V((-0.3, -0.33, 0.035)), (0.072, 0.012, 0.02), "cloth_cream")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # the swing: rope from the hook, the ring, three ropes to the tyre (two through the kit's paws), the tyre
    sm = B.M()
    sm.beam(PIVOT + V((0, 0, -0.01)), RING, 0.012, "rope")
    sm.cyl(RING, 0.02, 0.012, "iron", segs=8, axis=(1, 0, 0))
    ends, held = [], []
    for g in grips:                                                    # ring -> past the paw's outer side -> a knot on
        g = g + V((math.copysign(0.016, g.x), 0, 0))                   # the rim: the paw pulls the rope in a little, so
        held.append(g)                                                 # it kinks there, clear of the forearm and cheeks
        ends.append(V((math.copysign(0.12, g.x), 0.07, TYRE_TOP)))
    ends.append(V((0, -0.13, TYRE_TOP)))
    for g, e in zip(held, ends):
        sm.beam(RING, g, 0.008, "rope")
        sm.beam(g, e, 0.008, "rope")
    sm.beam(RING, ends[2], 0.008, "rope")
    for e in ends:
        sm.blob(e + V((0, 0, 0.005)), V((0.014, 0.014, 0.01)), "rope_dark", 5, 3)                 # the knot on the rim
    tyre(sm, V((0, 0, TYRE_TOP)))
    swing = sm.obj("pr_swing", coll)
    parts = {"pr_swing": A.part(swing, root, PIVOT)}
    return root, parts, ends


def clips(parts):
    def idle(p):
        return {"pr_swing": (None, A.q((1, 0, 0), -3 * math.sin(TAU * p)) @ A.q((0, 0, 1), 6 * math.sin(TAU * p + 1)), None)}

    def work(p):
        return {"pr_swing": (None, A.q((1, 0, 0), -J.swing_angle(p)), None)}            # forward is -Y

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def kit_grips():
    """Where the kit's paws are in work_swing (constant: they hold the ropes), from the baked clip, in building space."""
    coll = A.open_template()
    root = bpy.data.objects.new("tmp", None)
    coll.objects.link(root)
    sp = A.spot(root, "s", SPOT, (0, -1, 0))
    bpy.context.view_layer.update()
    rig, mesh, _ = A.raccoon_at(sp, variant="chr_raccoon_kit", clip="work_swing")
    bpy.context.scene.frame_set(0)
    return [rig.matrix_world @ rig.pose.bones[f"handslot.{s}"].head for s in ("l", "r")]


def main():
    do_renders = "--no-renders" not in sys.argv
    grips = kit_grips()
    print("GRIPS", [tuple(round(c, 3) for c in g) for g in grips])
    coll = A.open_template()
    root, parts, ends = build(coll, random.Random(19), grips)
    print("ROPE ENDS (dist from tyre centre)", [round(V((e.x, e.y)).length, 3) for e in ends])
    sp = A.spot(root, "spot_swing", SPOT, (0, -1, 0))
    bpy.context.view_layer.update()
    mw = sp.matrix_world.copy()
    sp.parent = parts["pr_swing"]                                        # it swings with the tyre
    sp.matrix_world = mw
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "kit_swing.blend"), relative_remap=True)
    A.export()
    bpy.context.view_layer.update()
    rig, mesh, _ = A.raccoon_at(sp, variant="chr_raccoon_kit", clip="work_swing")
    mw = rig.matrix_world.copy()
    rig.parent = sp
    rig.matrix_world = mw
    probs = A.check(root, 1, 1, crew=[(rig, mesh, None, "work", {"pr_swing": None})], allow=[("pr_swing", NAME)])
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_kit_swing_loops.gif",
                       target=(0.0, 0.0, 0.4), dist=2.2, pitch=26, idle_frames=24, grid_n=3, step=2)


if __name__ == "__main__":
    main()
