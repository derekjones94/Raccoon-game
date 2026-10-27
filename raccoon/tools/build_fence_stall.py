"""bld_fence_stall_2x2: the Fence's shady market stall, where loot is sold and goods bought (Haggling).

Counter along the front (-Y in Blender = +Z in Godot, same front as every other building), striped awning sloping
toward the customer, back curtain half drawn, stolen goods on the counter and the back shelf (a crown, a painting,
a gem tray, a goblet, a candlestick), a WANTED poster of a raccoon pinned to a post. The Fence stands on a stool pulled up to the counter (spot_work,
facing the customer at the front): the counter top is at its paw height (work_haggle).
2x2 cells, 1 m tall, inset 0.03 m, origin bottom-centre, one palette material.

Clips (24 fps)
  idle  48 fr  the lantern sways, the coin sign turns, the scale on the counter rocks gently
  work  48 fr  as idle, plus the stack of coins jumps on each of the Fence's two taps and the scale tips

Start the building's work and the raccoon's work_haggle together (both 48 frames): the coins jump on the taps.

Run:  python3 tools/build_fence_stall.py   (--no-renders)
Out:  fence_stall.blend, export/bld_fence_stall_2x2.glb, renders/bld_fence_stall_loops.gif, renders/qa_buildings.txt
"""
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_kit as A  # noqa: E402
import build_kit_blockout as K  # noqa: E402
import build_buildings_blockout as B  # noqa: E402
import build_props_blockout as PR  # noqa: E402
import build_raccoon_jobs as J  # noqa: E402

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_fence_stall_2x2"
FRAMES = 48
COUNTER_TOP = 0.32
STOOL_TOP = COUNTER_TOP - J.HAGGLE_TAP.z + 0.015       # the counter top is just under the paw when it taps
SPOT = V((0.15, -0.16, STOOL_TOP + 0.0015))          # on the stool, facing the customer (-Y)
COINS = SPOT + J.HAGGLE_TAP                          # the stack of coins the Fence taps


def build(coll, rnd):
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
    cd = 0.24
    cy, ch = SPOT.y - 0.1 - cd / 2, COUNTER_TOP - 0.02                   # its back edge clears the Fence's belly
    m.obox(V((0, cy, ch / 2)), (1.6, cd, ch), "wood_mid", top="wood_dark")
    for x in (-0.55, 0.0, 0.55):                                             # plank seams on the front
        m.obox(V((x, cy - cd / 2 - 0.004, ch / 2)), (0.03, 0.01, ch - 0.02), "wood_dark")
    m.obox(V((-0.3, cy - cd / 2 - 0.006, 0.12)), (0.2, 0.012, 0.14), "wood_weathered")   # patch board
    m.obox(V((0.62, cy - cd / 2 - 0.007, 0.2)), (0.32, 0.014, 0.12), "cloth_mustard")    # draped cloth
    counter = B.M()                                                      # the counter top: the paws may touch it
    counter.obox(V((0, cy, ch + 0.01)), (1.66, cd + 0.04, 0.02), "wood_dark")
    # ---- goods on the counter
    tray = V((-0.45, cy, ch + 0.02))
    m.obox(tray + V((0, 0, 0.012)), (0.26, 0.15, 0.024), "wood_light")                   # gem tray
    for dx, sw in ((-0.08, "ruby"), (0.0, "sapphire"), (0.08, "emerald")):
        PR.gem(m, tray + V((dx, 0, 0.055)), 0.03, sw, rot=rnd.uniform(0, 1))
    g = V((-0.17, cy, ch + 0.02))                                                         # gold goblet
    m.cyl(g + V((0, 0, 0.012)), 0.045, 0.024, "gold_dark", segs=8)
    m.cyl(g + V((0, 0, 0.06)), 0.014, 0.08, "gold", segs=6)
    m.cyl(g + V((0, 0, 0.13)), 0.035, 0.07, "gold", r2=0.055, segs=8)
    c = V((0.66, cy + 0.03, ch + 0.02))                                                   # silver candlestick
    m.cyl(c + V((0, 0, 0.01)), 0.04, 0.02, "silver", segs=8)
    m.cyl(c + V((0, 0, 0.09)), 0.012, 0.15, "silver", segs=6)
    m.cyl(c + V((0, 0, 0.18)), 0.012, 0.04, "cloth_cream", segs=6)
    for k in range(5):                                                                    # pearl necklace draped over the edge
        m.blob(V((0.48 + 0.035 * k, cy - cd / 2 + 0.01 - 0.004 * (k % 2), ch + 0.005 - 0.012 * abs(k - 2))),
               V((0.014, 0.014, 0.014)), "fur_cream", 6, 3)
    for dx in (-0.45, 0.05):                                                              # price tags
        m.obox(V((dx + 0.08, cy - cd / 2 - 0.012, ch - 0.04)), (0.05, 0.006, 0.035), "cloth_cream", rot=(0, 0.2, 0))
    PR.coin(m, V((-0.32, cy + 0.06, ch + 0.027)))
    # ---- the Fence's stool, pulled up to the counter
    m.cyl(V((SPOT.x, SPOT.y, STOOL_TOP / 2)), 0.09, STOOL_TOP, "wood_mid", cap="wood_light", segs=8)
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
    m.beam((0.0, fy - 0.03, 0.88), (0.0, fy - 0.03, 0.85), 0.01, "rope")                   # the coin sign's string
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    counter = counter.obj("pr_counter", coll)
    counter.parent = root
    parts = {}
    m = B.M()                                                                            # lantern on its arm
    lt = V((0.88, fy - 0.16, 0.705))
    m.obox(lt + V((0, 0, -0.085)), (0.07, 0.07, 0.1), "flame_yellow")
    m.obox(lt + V((0, 0, -0.025)), (0.09, 0.09, 0.025), "iron_dark")
    m.obox(lt + V((0, 0, -0.145)), (0.09, 0.09, 0.02), "iron_dark")
    parts["pr_lantern"] = A.part(m.obj("pr_lantern", coll), root, lt)
    m = B.M()                                                                            # coin sign, turning on a string
    cs = V((0.0, fy - 0.03, 0.85))
    m.cyl(cs + V((0, 0, -0.075)), 0.07, 0.02, "gold", cap="gold_light", axis=(0, 1, 0), segs=10)
    parts["pr_coin_sign"] = A.part(m.obj("pr_coin_sign", coll), root, cs)
    m = B.M()                                                                            # the stack of coins
    for k in range(3):
        PR.coin(m, COINS + V((0.003 * (k % 2), 0.002 * k, 0.007 * k - 0.005)), r=0.022)
    parts["pr_coins"] = A.part(m.obj("pr_coins", coll), root, COINS + V((0, 0, -0.012)))
    sb = V((0.4, cy - 0.02, COUNTER_TOP))                                                # balance scale: post, beam
    m = B.M()
    m.obox(sb + V((0, 0, 0.004)), (0.06, 0.04, 0.008), "wood_dark")
    m.obox(sb + V((0, 0, 0.06)), (0.012, 0.012, 0.11), "copper")
    post = m.obj("pr_scale_post", coll)
    post.parent = root
    m = B.M()
    pv = sb + V((0, 0, 0.115))
    m.beam(pv + V((-0.08, 0, 0)), pv + V((0.08, 0, 0)), 0.008, "copper")
    for x in (-0.075, 0.075):
        m.beam(pv + V((x, 0, 0)), pv + V((x, 0, -0.05)), 0.003, "iron_dark")
        m.cyl(pv + V((x, 0, -0.054)), 0.03, 0.006, "copper", segs=8, cap="gold_dark")
    PR.gem(m, pv + V((-0.075, 0, -0.04)), 0.014, "ruby")
    PR.coin(m, pv + V((0.075, 0, -0.047)), r=0.016)
    parts["pr_scale"] = A.part(m.obj("pr_scale", coll), root, pv)
    return root, counter, post, parts


def clips(parts):
    def common(p):
        return {"pr_lantern": (None, A.q((1, 0.3, 0), 4 * math.sin(TAU * p)), None),
                "pr_coin_sign": (None, A.q((0, 0, 1), 25 * math.sin(TAU * p)), None)}

    def idle(p):
        pose = common(p)
        pose["pr_scale"] = (None, A.q((0, 1, 0), 3 * math.sin(TAU * p)), None)
        pose["pr_coins"] = (None, None, None)
        return pose

    def work(p):
        pose = common(p)
        tap = sum(math.exp(-((p - c - 0.01) ** 2) / 0.0005) for c in J.HAGGLE_TAPS)
        pose["pr_coins"] = (V((0, 0, 0.006 * tap)), A.q((1, 0.3, 0), 6 * tap), None)
        tip = 7 * math.sin(TAU * p) + 5 * tap                       # the scale tips as the coins jump
        pose["pr_scale"] = (None, A.q((0, 1, 0), tip), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, idle), "work": (FRAMES, work)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, counter, post, parts = build(coll, random.Random(8))
    A.spot(root, "spot_work", SPOT, (0, -1, 0))
    clips(parts)
    print(f"STAT {NAME}: {sum(K.tris(o) for o in (root, counter, post, *parts.values()))} tris (moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "fence_stall.blend"), relative_remap=True)
    A.export()
    sp = bpy.data.objects["spot_work"]
    rig, mesh, _ = A.raccoon_at(sp, clip="work_haggle")
    allow = [("pr_lantern", NAME), ("pr_coin_sign", NAME), ("pr_coins", "pr_counter"), ("pr_scale", "pr_scale_post")]
    probs = A.check(root, 2, 2, H=1, crew=[(rig, mesh, None, "work", {"pr_counter": None, "pr_coins": None})],
                    allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [rig, mesh], ROOT / "renders" / "bld_fence_stall_loops.gif",
                       target=(0.0, 0.0, 0.3), dist=3.8, pitch=42, idle_frames=24, grid_n=4)


if __name__ == "__main__":
    main()
