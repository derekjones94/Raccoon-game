"""Hand tools for the raccoons' job clips, built in HAND-SLOT SPACE so they attach with no offset.

Convention for every tool (same as prop_cane):
  * origin  = the grip, the point the paw closes round
  * +Y      = along the handle, from the grip toward the working end (axe head, rod tip)
  * the axe's sharp edge points along +X; its blunt back (poll) along -X
Attach in the game as a child of the raccoon's handslot.r bone with an identity transform; the job clips (work_chop,
work_fish) were built against exactly this frame, so the axe lands edge-first and the rod points over the water.

Run:  python3 tools/build_tools.py
Out:  tools.blend, export/prop_axe.glb, export/prop_fishing_rod.glb
"""
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


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        bpy.data.objects.remove(o)
    coll = bpy.data.collections["Assets"]
    for fn in (prop_axe, prop_fishing_rod):
        ob = fn(coll)
        print(f"STAT {ob.name}: {K.tris(ob)} tris")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "tools.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})


if __name__ == "__main__":
    main()
