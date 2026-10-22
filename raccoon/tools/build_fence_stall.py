"""bld_fence_stall_2x2: the Fence's shady market stall.

Counter along the front (-Y in Blender = +Z in Godot, same front as every other building), striped awning sloping
toward the customer, back curtain half drawn, stolen goods on the counter and the back shelf (a crown, a painting,
a gem tray, a goblet, a candlestick), a WANTED poster of a raccoon pinned to a post, a stool for the Fence.
2x2 cells, 1 m tall, inset 0.03 m, origin bottom-centre, one palette material.

Run:  python3 tools/build_fence_stall.py
Out:  fence_stall.blend, export/bld_fence_stall_2x2.glb, renders/bld_fence_stall_*.png
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
import build_props_blockout as PR  # noqa: E402

ROOT = P.ROOT
V = Vector


def bld_fence_stall_2x2(coll, rnd):
    m = B.M()
    a = 1.0 - B.IN                                   # 0.97: footprint half-size
    # ---- ground: a worn rug under the stall
    m.obox(V((0, 0.05, 0.006)), (1.8, 1.7, 0.012), "cloth_red")
    m.obox(V((0, 0.05, 0.007)), (1.5, 1.4, 0.012), "leather_dark")
    # ---- frame + canopy over the BACK half only: from the 50 deg game camera a full awning hid the counter and
    #      the goods, so the canopy hangs off the back posts and tips up toward the customer (open, inviting, shady)
    by = 0.85
    for x in (-0.88, 0.88):
        m.obox(V((x, by, 0.47)), (0.07, 0.07, 0.94), "wood_dark")                      # back posts
        m.obox(V((x, 0.02, 0.43)), (0.06, 0.06, 0.86), "wood_dark")                     # canopy front poles
        m.beam((x, 0.02, 0.84), (x, by, 0.92), 0.045, "wood_mid")                        # side rails
    z0, z1, y0, y1 = 0.88, 0.97, -0.02, 0.95                                             # canopy front / back
    ang = math.atan2(z1 - z0, y1 - y0)
    L = math.hypot(y1 - y0, z1 - z0)
    n = 7
    w = 1.94 / n
    for i in range(n):
        x = -0.97 + w * (i + 0.5)
        sw = "cloth_red" if i % 2 == 0 else "leather_dark"
        m.obox(V((x, (y0 + y1) / 2, (z0 + z1) / 2 - 0.012)), (w, L, 0.022), sw, rot=(ang, 0, 0))
        m.obox(V((x, y0 + 0.012, z0 - 0.05)), (w * 0.55, 0.014, w * 0.55), sw, rot=(0, math.pi / 4, 0))   # scallops
    fy = 0.02                                                                            # poster / lantern hang off the front poles
    # ---- counter: patched planks, a darker top, a "closed" flap on one side
    cy, ch, cd = -0.42, 0.3, 0.24
    m.obox(V((0, cy, ch / 2)), (1.6, cd, ch), "wood_mid", top="wood_dark")
    for x in (-0.55, 0.0, 0.55):                                             # plank seams on the front
        m.obox(V((x, cy - cd / 2 - 0.004, ch / 2)), (0.03, 0.01, ch - 0.02), "wood_dark")
    m.obox(V((-0.3, cy - cd / 2 - 0.006, 0.12)), (0.2, 0.012, 0.14), "wood_weathered")   # patch board
    m.obox(V((0.62, cy - cd / 2 - 0.007, 0.2)), (0.32, 0.014, 0.12), "cloth_mustard")    # draped cloth
    m.obox(V((0, cy, ch + 0.01)), (1.66, cd + 0.04, 0.02), "wood_dark")                 # counter lip
    # ---- goods on the counter
    tray = V((-0.45, cy, ch + 0.02))
    m.obox(tray + V((0, 0, 0.012)), (0.26, 0.15, 0.024), "wood_light")                   # gem tray
    for dx, sw in ((-0.08, "ruby"), (0.0, "sapphire"), (0.08, "emerald")):
        PR.gem(m, tray + V((dx, 0, 0.055)), 0.03, sw, rot=rnd.uniform(0, 1))
    g = V((0.05, cy, ch + 0.02))                                                          # gold goblet
    m.cyl(g + V((0, 0, 0.012)), 0.045, 0.024, "gold_dark", segs=8)
    m.cyl(g + V((0, 0, 0.06)), 0.014, 0.08, "gold", segs=6)
    m.cyl(g + V((0, 0, 0.13)), 0.035, 0.07, "gold", r2=0.055, segs=8)
    c = V((0.3, cy + 0.03, ch + 0.02))                                                    # silver candlestick
    m.cyl(c + V((0, 0, 0.01)), 0.04, 0.02, "silver", segs=8)
    m.cyl(c + V((0, 0, 0.09)), 0.012, 0.15, "silver", segs=6)
    m.cyl(c + V((0, 0, 0.18)), 0.012, 0.04, "cloth_cream", segs=6)
    for k in range(5):                                                                    # pearl necklace draped over the edge
        m.blob(V((0.48 + 0.035 * k, cy - cd / 2 + 0.01 - 0.004 * (k % 2), ch + 0.005 - 0.012 * abs(k - 2))),
               V((0.014, 0.014, 0.014)), "fur_cream", 6, 3)
    for dx in (-0.45, 0.05):                                                              # price tags
        m.obox(V((dx + 0.08, cy - cd / 2 - 0.012, ch - 0.04)), (0.05, 0.006, 0.035), "cloth_cream", rot=(0, 0.2, 0))
    PR.coin(m, V((0.18, cy - 0.05, ch + 0.027)))
    PR.coin(m, V((-0.2, cy + 0.06, ch + 0.027)))
    # ---- the Fence's stool behind the counter
    m.cyl(V((0.0, -0.1, 0.11)), 0.08, 0.22, "wood_mid", cap="wood_light", segs=8)
    # ---- back shelf between the back posts: crown, painting, jar, bundled rug
    for z in (0.32, 0.6):
        m.obox(V((0, by - 0.06, z)), (1.7, 0.16, 0.03), "wood_light")
    cr = V((-0.55, by - 0.06, 0.335))                                                     # stolen crown
    m.cyl(cr + V((0, 0, 0.035)), 0.07, 0.07, "gold", segs=10)
    for i in range(5):
        aa = i / 5 * 2 * math.pi
        m.cyl(cr + V((math.cos(aa) * 0.062, math.sin(aa) * 0.062, 0.095)), 0.018, 0.05, "gold_light", segs=4, r2=0.0)
    PR.gem(m, cr + V((0, -0.07, 0.04)), 0.018, "ruby")
    pf = V((0.25, by - 0.04, 0.47))                                                       # painting, leaning
    m.obox(pf, (0.36, 0.03, 0.26), "gold_dark", rot=(-0.18, 0, 0))
    m.obox(pf + V((0, -0.012, 0.0)), (0.29, 0.02, 0.19), "teal_dark", rot=(-0.18, 0, 0))
    m.blob(pf + V((0.03, -0.03, -0.01)), V((0.07, 0.008, 0.05)), "moss_light", 6, 3)    # a painted hill
    m.cyl(V((0.65, by - 0.06, 0.4)), 0.05, 0.13, "verdigris", cap="cloth_cream", segs=8)  # jar
    m.cyl(V((-0.15, by - 0.06, 0.66)), 0.05, 0.3, "cloth_blue", cap="cloth_mustard", axis=(1, 0, 0), segs=8)  # rolled rug
    PR.gem(m, V((0.6, by - 0.06, 0.66)), 0.025, "amethyst")
    # ---- half-drawn back curtain: hides the "good stuff"
    m.obox(V((-0.45, a - 0.02, 0.5)), (0.85, 0.02, 0.86), "cloth_blue")
    m.obox(V((0.62, a - 0.02, 0.5)), (0.5, 0.02, 0.86), "cloth_blue")
    m.beam((-0.92, a - 0.02, 0.93), (0.92, a - 0.02, 0.93), 0.025, "iron")
    # ---- side stock: a locked iron chest, sacks, a crate
    m.obox(V((-0.72, 0.25, 0.1)), (0.3, 0.22, 0.2), "iron_dark", top="iron")
    m.obox(V((-0.72, 0.135, 0.12)), (0.05, 0.012, 0.06), "gold")                          # lock
    B.sack(m, V((0.75, 0.15, 0.0)), 0.1)
    B.sack(m, V((0.68, 0.38, 0.0)), 0.085, "cloth_cream")
    B.crate(m, V((0.72, -0.15, 0.0)), 0.22, 0.2)
    # ---- WANTED poster on the front-left post, a lantern on the front-right corner, a coin sign
    m.obox(V((-0.88, fy - 0.04, 0.6)), (0.14, 0.008, 0.18), "cloth_cream")
    m.obox(V((-0.88, fy - 0.045, 0.62)), (0.1, 0.006, 0.03), "fur_mask")                  # the masked face
    m.obox(V((-0.88, fy - 0.045, 0.55)), (0.08, 0.006, 0.012), "cloth_red")              # "WANTED" bar
    m.beam((0.88, fy, 0.72), (0.88, fy - 0.16, 0.72), 0.025, "wood_dark")
    m.obox(V((0.88, fy - 0.16, 0.62)), (0.07, 0.07, 0.1), "flame_yellow")                # lantern
    m.obox(V((0.88, fy - 0.16, 0.68)), (0.09, 0.09, 0.025), "iron_dark")
    m.obox(V((0.88, fy - 0.16, 0.56)), (0.09, 0.09, 0.02), "iron_dark")
    m.cyl(V((0.0, fy - 0.03, 0.78)), 0.07, 0.02, "gold", cap="gold_light", axis=(0, 1, 0), segs=10)  # coin sign under the canopy edge
    return m.obj("bld_fence_stall_2x2", coll)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    ob = bld_fence_stall_2x2(bpy.data.collections["Assets"], random.Random(8))
    PR.trim_below_floor(ob)              # sacks dip under z 0: flatten onto the floor, drop the unseen bottoms
    ok, bb = B.check_bounds(ob, 2, 2, 1)
    tris = K.tris(ob)
    print(f"STAT {ob.name}: {tris} tris, inside footprint: {ok} {bb}")
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_blockout.blend")) as (src, dst):
        dst.objects = ["chr_raccoon"]
    rac = dst.objects[0]
    rac.name = "ref_raccoon"
    ref.objects.link(rac)
    rac.location = (0.0, -0.1, 0.22)                     # the Fence, standing on the stool behind the counter
    K.instance(rac, ref, (-0.2, -0.95, 0), rot=math.pi * 0.9, name="ref_raccoon_customer")   # a customer, facing the counter
    import build_template
    build_template.grid(ref, n=7)            # odd n centred on 0: lines on the half-steps = cell edges
    show = K.instance(ob, ref, (0.5, 0.5, 0), name="bld_fence_stall_show")             # on a 2x2 cell block
    ob.hide_render = True
    rac.location += Vector((0.5, 0.5, 0))
    bpy.data.objects["ref_raccoon_customer"].location += Vector((0.5, 0.5, 0))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "fence_stall.blend"), relative_remap=True)
    ob.hide_render = False
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
    ob.hide_render = True

    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.view_settings.view_transform = "Standard"
    out = ROOT / "renders"
    gc = bpy.data.objects["GameCam"]
    K.look(gc, (0.5, 0.35, 0.35), -30, 5.2)
    K.shoot(gc, out / "bld_fence_stall_gamecam.png", (1400, 1000))
    K.look(gc, (0.5, 0.45, 0.35), 25, 3.4, pitch_deg=38)
    K.shoot(gc, out / "bld_fence_stall_closeup.png", (1400, 1000))
    # cave mood: the lantern is the only warm light; shady
    sun = bpy.data.objects["Sun"]
    sun.data.energy, sun.data.color = 0.45, (0.6, 0.72, 1.0)
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.03, 0.045, 0.09, 1), 1.1
    L = bpy.data.objects.new("lantern", bpy.data.lights.new("lantern", "POINT"))
    sc.collection.objects.link(L)
    L.location = (0.5 + 0.86, 0.5 + 0.02 - 0.24, 0.5)        # just outside the lantern box (inside, it is shadowed)
    L.data.energy, L.data.color, L.data.shadow_soft_size = 28, (1.0, 0.62, 0.3), 0.04
    K.look(gc, (0.5, 0.35, 0.35), -30, 5.2)
    K.shoot(gc, out / "bld_fence_stall_mood.png", (1400, 1000))
    L.hide_render = True
    sun.data.energy, sun.data.color = 3.0, (1, 1, 1)
    sun.rotation_euler = (math.radians(15), math.radians(8), math.radians(-35))
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.05, 0.06, 0.09, 1), 1.5
    top = bpy.data.objects["TopCam"]
    top.data.ortho_scale = 4.0
    top.location = (0.5, 0.3, 20)
    top.data.clip_end = 100
    K.shoot(top, out / "bld_fence_stall_topdown.png", (1000, 1000))


if __name__ == "__main__":
    main()
