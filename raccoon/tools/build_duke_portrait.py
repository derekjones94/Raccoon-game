"""bld_duke_portrait_1x1: a grand gilt portrait of a duke, stolen from his own hall, with a moustache drawn on. A
decoration.

A heavy gilt frame stands on a wooden easel, leaning back a little. In it the duke: powdered wig, blue coat, a red
sash and a gold medal, against a dark curtain. Someone has painted a big curly moustache on him in soot, and a
raccoon's mask over his eyes. Below it a little round table with a brass candlestick and a lit candle, a pot of soot
and the brush that did it.

Clips (24 fps)
  idle  96 fr  the candle flickers and its flame leans now and then
  work  96 fr  the same (decorations have no work of their own)

Run:  python3 tools/build_duke_portrait.py   (--no-renders)
Out:  duke_portrait.blend, export/bld_duke_portrait_1x1.glb, renders/bld_duke_portrait_loops.gif
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh  # noqa: E402
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_props_blockout as PR  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_duke_portrait_1x1"
FRAMES = 96
LEDGE = V((0.0, 0.05, 0.2))                      # where the frame's bottom rests on the easel
TILT = 9.0                                       # degrees the picture leans back
FW, FH, FB = 0.4, 0.5, 0.055                     # the frame: outer width, outer height, border width
CANDLE = V((0.2, -0.2, 0.0))                     # the little table's foot


def frame_and_picture(m):
    """The gilt frame and the painting, built upright with the frame's bottom centre at LEDGE (the canvas faces -Y)."""
    c = LEDGE + V((0, 0, FH / 2))
    y = LEDGE.y
    # the frame: four moulded sides, corner bosses, a crest
    for z, (sx, sz) in ((c.z - FH / 2 + FB / 2, (FW, FB)), (c.z + FH / 2 - FB / 2, (FW, FB))):
        m.obox(V((0, y, z)), (sx, 0.04, sz), "gold")
        m.obox(V((0, y - 0.021, z)), (sx - 0.02, 0.004, sz * 0.4), "gold_light")
    for x in (-FW / 2 + FB / 2, FW / 2 - FB / 2):
        m.obox(V((x, y, c.z)), (FB, 0.04, FH - 2 * FB), "gold")
        m.obox(V((x, y - 0.021, c.z)), (FB * 0.4, 0.004, FH - 2 * FB), "gold_light")
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.blob(V((sx * (FW / 2 - FB / 2), y - 0.02, c.z + sz * (FH / 2 - FB / 2))), V((0.035, 0.016, 0.035)), "gold_light", 8, 4)
    m.blob(V((0, y - 0.01, c.z + FH / 2 + 0.02)), V((0.07, 0.02, 0.04)), "gold", 8, 4)          # crest
    m.blob(V((0, y - 0.024, c.z + FH / 2 + 0.024)), V((0.016, 0.01, 0.016)), "ruby", 6, 3)
    m.obox(V((0, y - 0.024, c.z - FH / 2 + 0.03)), (0.09, 0.004, 0.022), "gold_dark")           # name plate
    # the canvas: a dark curtain behind him
    iw, ih = FW - 2 * FB, FH - 2 * FB
    cy = y - 0.012
    m.obox(V((0, y - 0.006, c.z)), (iw, 0.012, ih), "teal_dark")
    m.obox(V((-iw / 2 + 0.04, cy - 0.001, c.z + 0.02)), (0.07, 0.004, ih - 0.04), "cloth_red", rot=(0, 0.1, 0))   # curtain
    m.obox(V((0, cy - 0.001, c.z + ih / 2 - 0.02)), (iw - 0.01, 0.004, 0.035), "cloth_red")
    # the duke: shoulders in a blue coat, a red sash, a medal, a white cravat
    bz = c.z - ih / 2
    m.blob(V((0, cy - 0.004, bz + 0.07)), V((0.12, 0.012, 0.09)), "cloth_blue", 10, 4)
    m.obox(V((0.0, cy - 0.016, bz + 0.07)), (0.03, 0.004, 0.16), "cloth_red", rot=(0, -0.6, 0))
    m.blob(V((0.04, cy - 0.02, bz + 0.09)), V((0.016, 0.006, 0.016)), "gold_light", 8, 3)
    m.blob(V((0, cy - 0.016, bz + 0.135)), V((0.03, 0.008, 0.028)), "cloth_cream", 6, 3)
    # his head, the powdered wig with side curls, a stern brow
    hz = bz + 0.2
    m.blob(V((0, cy - 0.006, hz + 0.012)), V((0.075, 0.012, 0.07)), "cloth_cream", 10, 4)          # wig
    for sx in (-1, 1):
        for k in range(2):
            m.blob(V((sx * 0.07, cy - 0.012, hz - 0.03 - 0.03 * k)), V((0.022, 0.01, 0.016)), "bone", 6, 3)
    m.blob(V((0, cy - 0.014, hz - 0.01)), V((0.045, 0.01, 0.055)), "fur_tan", 10, 4)              # face
    m.blob(V((0, cy - 0.024, hz - 0.02)), V((0.01, 0.006, 0.016)), "fur_brown", 5, 3)             # nose
    # the vandalism: a raccoon mask over his eyes and a curly moustache, in soot
    m.obox(V((0, cy - 0.022, hz + 0.008)), (0.09, 0.003, 0.022), "soot")
    for sx in (-1, 1):
        m.blob(V((sx * 0.02, cy - 0.025, hz + 0.008)), V((0.007, 0.003, 0.006)), "cloth_cream", 5, 3)   # eyes
        m.obox(V((sx * 0.022, cy - 0.025, hz - 0.035)), (0.04, 0.003, 0.009), "soot", rot=(0, sx * 0.25, 0))
        m.obox(V((sx * 0.046, cy - 0.025, hz - 0.028)), (0.016, 0.003, 0.008), "soot", rot=(0, -sx * 0.9, 0))
        m.blob(V((sx * 0.052, cy - 0.025, hz - 0.018)), V((0.007, 0.003, 0.007)), "soot", 5, 3)      # the curls
    m.blob(V((0, cy - 0.024, hz - 0.052)), V((0.012, 0.004, 0.006)), "cloth_red", 5, 3)            # mouth
    # a little raccoon paw signature, bottom right
    m.blob(V((iw / 2 - 0.03, cy - 0.003, bz + 0.03)), V((0.01, 0.003, 0.008)), "soot", 5, 3)
    for k in range(3):
        m.blob(V((iw / 2 - 0.042 + 0.012 * k, cy - 0.003, bz + 0.045)), V((0.004, 0.003, 0.004)), "soot", 4, 3)


def build(coll, rnd):
    m = B.M()
    # ---- the easel: two front legs and a back leg, all behind the picture; the ledge it rests on, a cross bar
    tan = math.tan(math.radians(TILT))
    zt = LEDGE.z + FH + 0.03
    yt = LEDGE.y + 0.045 + (zt - LEDGE.z) * tan                                  # just behind the frame's back
    top = V((0, yt, zt))
    for sx in (-1, 1):
        m.beam(V((sx * 0.15, LEDGE.y + 0.04, 0.0)), top + V((sx * 0.04, 0.0, 0.0)), 0.022, "wood_mid")
    m.beam(V((0, LEDGE.y + 0.32, 0.0)), top + V((0, 0.02, -0.03)), 0.022, "wood_dark")
    m.beam(top + V((-0.07, 0.0, -0.01)), top + V((0.07, 0.0, -0.01)), 0.016, "wood_dark")
    m.obox(LEDGE + V((0, 0.0, -0.012)), (FW + 0.08, 0.1, 0.02), "wood_mid", top="wood_light")    # reaches back to the legs
    m.obox(LEDGE + V((0, -0.048, 0.0)), (FW + 0.08, 0.008, 0.02), "wood_dark")                  # its lip
    m.beam(V((-0.13, LEDGE.y + 0.06, 0.08)), V((0.13, LEDGE.y + 0.06, 0.08)), 0.016, "wood_dark")
    # ---- the little table with a candlestick, the soot pot and the guilty brush
    t = CANDLE
    m.cyl(t + V((0, 0, 0.09)), 0.016, 0.18, "wood_dark", segs=6)
    m.cyl(t + V((0, 0, 0.01)), 0.06, 0.02, "wood_dark", segs=8)
    m.cyl(t + V((0, 0, 0.19)), 0.1, 0.018, "wood_mid", segs=10, cap="wood_light")
    m.cyl(t + V((-0.02, 0.0, 0.205)), 0.035, 0.012, "gold_dark", segs=8)                         # candlestick
    m.cyl(t + V((-0.02, 0.0, 0.235)), 0.01, 0.05, "gold", segs=6)
    m.cyl(t + V((-0.02, 0.0, 0.262)), 0.02, 0.008, "gold_dark", segs=8)
    m.cyl(t + V((-0.02, 0.0, 0.29)), 0.011, 0.05, "cloth_cream", segs=6, cap="bone")              # the candle
    m.blob(t + V((-0.008, 0.0, 0.3)), V((0.004, 0.004, 0.012)), "bone", 4, 3)                    # a drip
    m.cyl(t + V((0.05, 0.03, 0.22)), 0.022, 0.03, "iron_dark", segs=8, cap="soot")               # soot pot
    m.beam(t + V((0.05, 0.03, 0.23)), t + V((0.08, -0.03, 0.27)), 0.006, "wood_light")         # brush in it
    m.blob(t + V((0.085, -0.04, 0.278)), V((0.008, 0.008, 0.012)), "soot", 5, 3)
    m.blob(V((-0.25, -0.25, 0.002)), V((0.035, 0.03, 0.002)), "soot", 6, 3)                      # a smudge
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # the picture, leaning back on the easel
    fm = B.M()
    frame_and_picture(fm)
    piv = LEDGE + V((0, -0.02, 0))
    bmesh.ops.rotate(fm.bm, verts=fm.bm.verts, cent=piv, matrix=Matrix.Rotation(math.radians(-TILT), 3, "X"))
    pic = fm.obj("pr_portrait", coll)
    pic.parent = root
    parts = {}
    mm = B.M()
    fc = t + V((-0.02, 0.0, 0.318))
    mm.cyl(fc + V((0, 0, 0.018)), 0.011, 0.036, "flame_yellow", segs=6, r2=0.0)
    mm.cyl(fc + V((0, 0, 0.012)), 0.006, 0.018, "flame_white", segs=5, r2=0.0)
    mm.beam(fc + V((0, 0, -0.004)), fc + V((0, 0, 0.006)), 0.003, "soot")                         # wick
    parts["pr_flame"] = A.part(mm.obj("pr_flame", coll), root, fc)
    return root, pic, parts


def clips(parts):
    def pose(p):
        fl = math.sin(TAU * 7 * p) + 0.6 * math.sin(TAU * 13 * p + 1.3)
        lean = 14 * math.exp(-((p - 0.4) ** 2) / 0.003) * math.sin(TAU * 4 * (p - 0.4))   # a draught, now and then
        return {"pr_flame": (None, A.q((1, 0.3, 0), 4 * fl + lean), (1 + 0.06 * fl, 1 + 0.06 * fl, 1 + 0.16 * math.sin(TAU * 9 * p)))}

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, pic, parts = build(coll, random.Random(9))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + K.tris(pic) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root) + K.tris(pic)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "duke_portrait.blend"), relative_remap=True)
    A.export()
    probs = A.check(root, 1, 1, allow=[("pr_flame", NAME), ("pr_portrait", NAME)])
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [], ROOT / "renders" / "bld_duke_portrait_loops.gif",
                       target=(0.0, 0.0, 0.38), dist=1.7, pitch=22, grid_n=3, step=3, idle_only=True)


if __name__ == "__main__":
    main()
