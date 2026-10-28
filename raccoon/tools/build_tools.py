"""Hand tools for the raccoons' job clips, built in HAND-SLOT SPACE so they attach with no offset.

Convention for every tool (same as prop_cane):
  * origin  = the grip, the point the paw closes round
  * +Y      = along the handle, from the grip toward the working end (axe head, rod tip)
  * the axe's sharp edge points along +X; its blunt back (poll) along -X
  * the watering can is carried by its top handle (+Y toward the spout); the can hangs below it, along -Z
  * the hammer's striking face points along +X (like the axe's edge); the ladle's bowl opens toward +Z
  * the mug is held round its body: its axis runs along +Y (open top at +Y), the paw on its back, the body a touch along +X
  * the pestle's grinding end is at +Y
  * the spear's point is at +Y (held upright, the butt toward -Y); the hand brush's bristles face -X
Attach in the game as a child of the raccoon's handslot.r bone with an identity transform; the job clips (work_chop,
work_fish) were built against exactly this frame, so the axe lands edge-first and the rod points over the water.

Run:  python3 tools/build_tools.py
Out:  tools.blend, export/prop_axe.glb, prop_fishing_rod.glb, prop_watering_can.glb, prop_hammer.glb, prop_ladle.glb, prop_mug.glb, prop_pestle.glb, prop_spear.glb, prop_brush.glb
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_buildings_blockout as B  # noqa: E402

ROOT = P.ROOT
V = Vector
AXE_HEAD_Y = 0.148            # centre of the axe head along the handle
AXE_EDGE = V((0.05, AXE_HEAD_Y, 0.0))    # middle of the cutting edge, slot space
ROD_TIP = V((0.0, 0.43, 0.0))  # rod tip, slot space (the fishing line hangs from here)
CAN_SPOUT = V((0.0, 0.15, -0.018)) # middle of the watering can's rose (the water comes out here), slot space
CAN_SPOUT_DIR = V((0.0, 0.08, 0.045)).normalized()   # the way the spout points, slot space
HAMMER_Y = 0.092                     # centre of the hammer head along the handle
HAMMER_FACE = V((0.02, HAMMER_Y, 0.0))   # middle of the striking face, slot space
LADLE_BOWL = V((0.0, 0.15, 0.0))     # centre of the ladle's bowl, slot space
MUG_C = V((0.021, 0.0, 0.0))         # centre of the mug's body, slot space (its axis runs along Y)
MUG_R, MUG_H = 0.021, 0.046
PESTLE_TIP = V((0.0, 0.07, 0.0))  
SPEAR_BUTT, SPEAR_TIP = -0.118, 0.33  # along Y from the grip
BRUSH_C = V((-0.012, 0.075, 0.0))   # middle of the brush's bristle block (its bristles face -X)
BRUSH_TILT = 27.0                     # degrees the head is turned from the handle (work_sweep holds it 27 deg down)    # the pestle's grinding end, slot space


def prop_axe(coll):
    m = B.M()
    m.cyl(V((0, 0.0905, 0)), 0.0065, 0.169, "wood_light", axis=(0, 1, 0), segs=6, cap="wood_dark")   # handle 0.006 .. 0.175 (ends inside the fist)
    # head: a wedge, blunt poll at -X, flaring to a taller edge at +X; flat across Z
    prof = [(-0.018, AXE_HEAD_Y - 0.016), (0.02, AXE_HEAD_Y - 0.014), (0.05, AXE_HEAD_Y - 0.03),
            (0.05, AXE_HEAD_Y + 0.03), (0.02, AXE_HEAD_Y + 0.016), (-0.018, AXE_HEAD_Y + 0.016)]
    _plate(m, prof, 0.013, "iron")
    _plate(m, [(0.04, AXE_HEAD_Y - 0.026), (0.051, AXE_HEAD_Y - 0.031), (0.051, AXE_HEAD_Y + 0.031),
               (0.04, AXE_HEAD_Y + 0.026)], 0.008, "iron_light")                                      # bright edge
    return m.obj("prop_axe", coll)


def _plate(m, outline_xy, t, sw):
    """A flat plate: an XY outline extruded symmetrically across Z."""
    f0 = [m.bm.verts.new((x, y, -t / 2)) for x, y in outline_xy]
    f1 = [m.bm.verts.new((x, y, t / 2)) for x, y in outline_xy]
    faces = [m.bm.faces.new(list(reversed(f0))), m.bm.faces.new(f1)]
    n = len(f0)
    for i in range(n):
        j = (i + 1) % n
        faces.append(m.bm.faces.new((f0[i], f0[j], f1[j], f1[i])))
    m.tag(faces, sw)


def prop_fishing_rod(coll):
    m = B.M()
    m.cyl(V((0, 0.015, 0)), 0.0085, 0.07, "cloth_cream", axis=(0, 1, 0), segs=6)                     # cork grip -0.02 .. 0.05
    m.cyl(V((0, 0.24, 0)), 0.0055, 0.38, "wood_cut", axis=(0, 1, 0), segs=5, r2=0.0025)               # rod 0.05 .. 0.43
    m.cyl(V((0, ROD_TIP.y - 0.004, 0)), 0.0035, 0.008, "rust", axis=(0, 1, 0), segs=5)                # tip ring
    for y in (0.15, 0.27):
        m.cyl(V((0, y, 0)), 0.0065, 0.006, "iron_dark", axis=(0, 1, 0), segs=5)                     # line guides
    m.cyl(V((0.0, 0.035, -0.016)), 0.013, 0.012, "iron", axis=(1, 0, 0), segs=8, cap="iron_light")   # reel under the rod
    m.beam(V((0, 0.035, -0.006)), V((0, 0.035, -0.012)), 0.006, "iron_dark")
    return m.obj("prop_fishing_rod", coll)


def prop_watering_can(coll):
    """A small copper can carried by its top handle: the handle runs along +Y toward the spout, the can hangs below
    it (-Z) and the spout rises ahead of it."""
    m = B.M()
    c = V((0.0, 0.03, -0.054))                                  # the can hangs ahead of the paw, clear of the leg
    m.cyl(c, 0.031, 0.058, "copper", segs=8, cap="rust")                                               # body
    m.cyl(c + V((0, 0, 0.027)), 0.033, 0.006, "rust_dark", segs=8)                                     # top rim
    m.cyl(c + V((0, 0, -0.025)), 0.033, 0.006, "rust_dark", segs=8)                                    # base band
    m.beam(V((0, -0.016, 0)), V((0, 0.056, 0)), 0.007, "iron_dark")                                   # handle (grip at its back end)
    for y in (0.004, 0.056):
        m.beam(V((0, y, 0.0035)), V((0, y, -0.026)), 0.007, "iron_dark")                              # handle legs
    a, b = V((0, 0.056, -0.068)), CAN_SPOUT - CAN_SPOUT_DIR * 0.008
    m.cyl((a + b) / 2, 0.007, (b - a).length, "copper", axis=tuple(b - a), segs=5, r2=0.0045)           # spout
    m.cyl(CAN_SPOUT - CAN_SPOUT_DIR * 0.004, 0.006, 0.008, "rust", axis=tuple(CAN_SPOUT_DIR), segs=6,
          r2=0.012, cap="iron_light")                                                                 # rose
    return m.obj("prop_watering_can", coll)


def prop_hammer(coll):
    """A small tinker's hammer: the handle runs from the fist along +Y, the striking face points along +X, a narrow
    peen along -X."""
    m = B.M()
    m.cyl(V((0, 0.044, 0)), 0.0055, 0.112, "wood_light", axis=(0, 1, 0), segs=6, cap="wood_dark")       # handle -0.012 .. 0.1
    m.cyl(V((0.005, HAMMER_Y, 0)), 0.011, 0.03, "iron", axis=(1, 0, 0), segs=6, cap="iron_light")       # head, face at +X
    m.cyl(V((-0.017, HAMMER_Y, 0)), 0.008, 0.018, "iron_dark", axis=(-1, 0, 0), segs=4, r2=0.003)       # peen
    return m.obj("prop_hammer", coll)


def prop_ladle(coll):
    """A long wooden ladle: handle along +Y from the fist, the bowl at the end, opening toward +Z."""
    m = B.M()
    m.cyl(V((0, 0.06, 0)), 0.005, 0.16, "wood_light", axis=(0, 1, 0), segs=5, cap="wood_dark")         # handle -0.02 .. 0.14
    m.cyl(LADLE_BOWL + V((0, 0, 0.002)), 0.022, 0.018, "wood_mid", segs=7, r2=0.012, cap="wood_dark", axis=(0, 0, -1))
    return m.obj("prop_ladle", coll)


def prop_mug(coll):
    """A small wooden tankard held round its body (raccoon paws are too short to hold one out by a handle and still
    reach the mouth): axis along +Y, the open top toward +Y, a handle on the far side. Frothy cider inside."""
    m = B.M()
    m.cyl(MUG_C, MUG_R, MUG_H, "wood_light", axis=(0, 1, 0), segs=8, cap="cloth_cream")         # body, froth on top
    for y in (-MUG_H * 0.32, MUG_H * 0.32):
        m.cyl(MUG_C + V((0, y, 0)), MUG_R + 0.0025, 0.005, "iron", axis=(0, 1, 0), segs=8)       # hoops
    hx = MUG_C.x + MUG_R + 0.008
    m.beam(V((hx, -0.012, 0)), V((hx, 0.014, 0)), 0.005, "wood_dark")                          # handle, far side
    for y in (-0.012, 0.014):
        m.beam(V((hx + 0.002, y, 0)), V((MUG_C.x + MUG_R - 0.003, y, 0)), 0.005, "wood_dark")
    return m.obj("prop_mug", coll)


def prop_pestle(coll):
    """A stone pestle: the grip at the top, the heavy rounded end at +Y."""
    m = B.M()
    m.cyl(V((0, 0.028, 0)), 0.006, 0.076, "stone_pale", axis=(0, 1, 0), segs=6, r2=0.009)
    m.blob(PESTLE_TIP + V((0, -0.006, 0)), V((0.011, 0.012, 0.011)), "stone_light", 6, 3)
    return m.obj("prop_pestle", coll)


def prop_spear(coll):
    """A guard's spear: a long shaft through the fist (along Y), the butt near the floor, an iron point up top, a
    teal pennant under the point."""
    m = B.M()
    L = SPEAR_TIP - 0.05 - SPEAR_BUTT
    m.cyl(V((0, SPEAR_BUTT + L / 2, 0)), 0.0055, L, "wood_mid", axis=(0, 1, 0), segs=5, cap="wood_dark")
    m.cyl(V((0, SPEAR_TIP - 0.028, 0)), 0.012, 0.056, "iron_light", axis=(0, 1, 0), segs=4, r2=0.0)     # point
    m.cyl(V((0, SPEAR_TIP - 0.055, 0)), 0.008, 0.01, "iron_dark", axis=(0, 1, 0), segs=5)
    m.obox(V((0.0, SPEAR_TIP - 0.09, -0.024)), (0.003, 0.05, 0.04), "teal")                           # pennant
    return m.obj("prop_spear", coll)


def prop_brush(coll):
    """A janitor's hand brush: a short handle from the fist along +Y, a wooden block with bristles facing -X."""
    m = B.M()
    m.cyl(V((0, 0.02, 0)), 0.006, 0.06, "wood_light", axis=(0, 1, 0), segs=5, cap="wood_dark")
    tilt = math.radians(BRUSH_TILT)                  # the head is set at an angle to the handle, so it lies flat on the
    up = V((math.cos(tilt), -math.sin(tilt), 0))     # floor while the handle slopes down to it (its bristles face -up)
    m.obox(BRUSH_C + up * 0.008, (0.014, 0.06, 0.028), "wood_mid", rot=(0, 0, -tilt))
    m.obox(BRUSH_C - up * 0.008, (0.018, 0.056, 0.024), "rope", rot=(0, 0, -tilt))          # bristles
    return m.obj("prop_brush", coll)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        bpy.data.objects.remove(o)
    coll = bpy.data.collections["Assets"]
    for fn in (prop_axe, prop_fishing_rod, prop_watering_can, prop_hammer, prop_ladle, prop_mug, prop_pestle, prop_spear, prop_brush):
        ob = fn(coll)
        print(f"STAT {ob.name}: {K.tris(ob)} tris")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "tools.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})


if __name__ == "__main__":
    main()
