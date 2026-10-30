"""bld_guild_hall_3x3: the guild's hall, second pass. Hollow and lived in, like the den.

A timber-framed hall on a stone footing: posts and beams with plank walls between them (low enough, 0.52 m, that the
inside reads from the game camera), a wide doorway at the front with its door swung open, shuttered windows on the
sides and the back. Inside, the guild at home: a long, low war table with a raid map, candles, a dagger stuck in it
and a stack of coins; a stone hearth on the back wall; a notice board of jobs; a shelf of trophies (a stolen crown, a
golden goblet, a painting); the loot corner (a chest, a coin heap, gems); a rack of thieves' tools (rope and hook,
picks, a crowbar); benches, barrels, a guild banner. Outside: steps, two teal banners and two torches by the door.

The roof is a CHILD object, bld_guild_hall_3x3_roof: plank strips laid edge to edge on two slopes (no overlapping
shingles, nothing z-fights), a ridge beam, gable boards, the hearth's chimney and a banner on a pole. Hide that node
in the game (camera close, or someone inside) to see in; the chimney smoke is its child, so it hides with it.

Spots: spot_gather_1..4 round the war table, where a crew plans a raid (work_read: crouched over the map).

Clips (24 fps)
  idle  96 fr  the hearth fire flickers, smoke from the chimney, banners and the torches' flames stir
  work  96 fr  (a crew is gathered) as idle, plus the notices on the board flutter and the candles burn up

3x3 cells, inset 0.03 m, origin bottom-centre, entrance facing -Y like every other building.

Run:  python3 tools/build_guild_hall.py   (--no-renders)
Out:  guild_hall.blend, export/bld_guild_hall_3x3.glb, renders/bld_guild_hall_loops.gif, renders/qa_buildings.txt
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
NAME = "bld_guild_hall_3x3"
FRAMES = 96
X0, X1, Y0, Y1 = -1.3, 1.3, -1.02, 1.3            # the hall's outer wall faces
FOOT = 0.08                                        # stone footing height; the floor inside is at FOOT
WALL_T = 0.06
WALL_H = 0.52                                      # wall top, above the floor
EAVE = FOOT + WALL_H
RIDGE = EAVE + 0.62
DOOR = (-0.24, 0.24)                               # doorway, x range, front wall
WINDOWS = {"left": [(-0.25, 0.1)], "right": [(-0.75, -0.45), (0.55, 0.9)], "back": [(-0.2, 0.15), (0.55, 0.9)]}   # world x / y ranges
WIN_Z = (0.24, 0.42)                               # above the floor
TABLE_C = V((0.0, 0.18, 0.0))
TABLE_L, TABLE_D = 0.92, 0.28
GAP = 0.105
TOP = FOOT + 0.003 + J.READ_C.z - 0.025            # the map on the table, at the readers paws
GATHER = [(V((x, TABLE_C.y + TABLE_D / 2 + GAP, FOOT + 0.003)), (0, -1, 0)) for x in (-0.24, 0.24)] + \
         [(V((x, TABLE_C.y - TABLE_D / 2 - GAP, FOOT + 0.003)), (0, 1, 0)) for x in (-0.24, 0.24)]   # on the rug
HEARTH = V((-0.62, Y1 - WALL_T, FOOT))


def wall_run(m, a, b, openings, rnd, outward):
    """A plank wall from a to b (on the floor line) with posts at both ends and between, openings (along-wall
    ranges, measured from a) cut out: door openings go to the floor, window openings sit at WIN_Z."""
    d = (b - a)
    L = d.length
    u = d / L
    n = V((outward.x, outward.y, 0))
    posts = [0.0, L] + [t for o in openings for t in (o[0] - 0.035, o[1] + 0.035) if 0.05 < t < L - 0.05]
    k = 2
    while k * 0.62 < L:                                                      # posts every ~0.6 m between openings
        t = k * L / math.ceil(L / 0.62)
        if all(not (o[0] - 0.08 < t < o[1] + 0.08) for o in openings):
            posts.append(t)
        k += 1
    posts = sorted(set(round(t, 4) for t in posts))
    for t in posts:                                                          # posts (proud of the planks)
        p = a + u * t
        m.obox(V((p.x, p.y, FOOT + WALL_H / 2)), (0.07 if abs(u.x) > 0.5 else 0.07, 0.07, WALL_H),
               "wood_dark", rot=(0, 0, math.atan2(u.y, u.x)))
    mid = (a + b) / 2
    m.obox(V((mid.x, mid.y, FOOT + WALL_H - 0.02)), (L + 0.07, 0.075, 0.04),
           "wood_dark", rot=(0, 0, math.atan2(u.y, u.x)))                                  # top plate
    # plank panels between posts, inset a touch so the posts stand proud; openings split them
    for t0, t1 in zip(posts, posts[1:]):
        t0, t1 = t0 + 0.035, t1 - 0.035
        if t1 - t0 < 0.01:
            continue
        spans = []
        door = [o for o in openings if o[2] == "door" and o[0] < t1 and o[1] > t0]
        win = [o for o in openings if o[2] == "win" and o[0] - 0.04 < t1 and o[1] + 0.04 > t0]
        if door:
            continue
        if win:
            spans += [(t0, t1, 0.0, WIN_Z[0]), (t0, t1, WIN_Z[1], WALL_H - 0.04)]
        else:
            spans.append((t0, t1, 0.0, WALL_H - 0.04))
        for s0, s1, z0, z1 in spans:
            nb = max(1, round((z1 - z0) / 0.1))
            for j in range(nb):                                              # horizontal boards
                za, zb = z0 + (z1 - z0) * j / nb, z0 + (z1 - z0) * (j + 1) / nb
                c = a + u * ((s0 + s1) / 2) - n * 0.0
                m.obox(V((c.x, c.y, FOOT + (za + zb) / 2)), (s1 - s0, WALL_T - 0.012, zb - za - 0.004),
                       rnd.choice(["wood_mid", "wood_weathered", "wood_mid", "wood_light"]), rot=(0, 0, math.atan2(u.y, u.x)))
        for o in win:                                                        # window: sill, shutters swung out
            c = a + u * ((o[0] + o[1]) / 2)
            m.obox(V((c.x, c.y, FOOT + WIN_Z[0])) + n * 0.02, (o[1] - o[0] + 0.06, 0.05, 0.02), "wood_light",
                   rot=(0, 0, math.atan2(u.y, u.x)))
            for s, t in ((-1, o[0]), (1, o[1])):
                h = a + u * t + n * (WALL_T / 2 + 0.006)
                q = h + u * (s * 0.075) + n * 0.03
                m.obox(V((q.x, q.y, FOOT + (WIN_Z[0] + WIN_Z[1]) / 2)), (0.15, 0.012, WIN_Z[1] - WIN_Z[0]),
                       "teal_dark", rot=(0, 0, math.atan2(u.y, u.x) + s * 0.6))


def build(coll, rnd):
    m = B.M()
    # ---- stone footing (a course of blocks), steps at the door, the plank floor inside
    for (xa, xb, ya, yb) in ((X0, X1, Y0, Y0 + 0.12), (X0, X1, Y1 - 0.12, Y1), (X0, X0 + 0.12, Y0, Y1), (X1 - 0.12, X1, Y0, Y1)):
        horiz = (xb - xa) > (yb - ya)
        L = (xb - xa) if horiz else (yb - ya)
        nblk = max(1, round(L / 0.28))
        for k in range(nblk):
            t0, t1 = k / nblk, (k + 1) / nblk
            if horiz:
                c = V((xa + (xb - xa) * (t0 + t1) / 2, (ya + yb) / 2, FOOT / 2))
                size = ((xb - xa) / nblk - 0.008, yb - ya, FOOT)
            else:
                c = V(((xa + xb) / 2, ya + (yb - ya) * (t0 + t1) / 2, FOOT / 2))
                size = (xb - xa, (yb - ya) / nblk - 0.008, FOOT)
            m.obox(c, size, rnd.choice(["stone_mid", "stone_light", "stone_mid"]), top="stone_pale")
    m.obox(V(((X0 + X1) / 2, (Y0 + Y1) / 2, (FOOT - 0.01) / 2)), (X1 - X0 - 0.24, Y1 - Y0 - 0.24, FOOT - 0.01), "stone_dark")  # under the boards
    nbo = 12
    for k in range(nbo):                                                     # floor boards (inside the footing)
        x = X0 + 0.12 + (X1 - X0 - 0.24) * (k + 0.5) / nbo
        m.obox(V((x, (Y0 + Y1) / 2, FOOT - 0.004)), ((X1 - X0 - 0.24) / nbo - 0.006, Y1 - Y0 - 0.24, 0.008),
               "wood_light" if k % 2 else "wood_cut")
    for k in range(2):                                                       # front steps
        m.obox(V(((DOOR[0] + DOOR[1]) / 2, Y0 - 0.09 - 0.11 * k + 0.0, FOOT * (2 - k) / 2 / 2 + 0.0)),
               (DOOR[1] - DOOR[0] + 0.3 - 0.1 * k, 0.12, FOOT * (2 - k) / 2), "stone_light", top="stone_pale")
    # ---- walls
    ins = 0.06                                                               # wall centre line, in from the footing's outer edge
    a, b, c_, d = V((X0 + ins, Y0 + ins, 0)), V((X1 - ins, Y0 + ins, 0)), V((X1 - ins, Y1 - ins, 0)), V((X0 + ins, Y1 - ins, 0))
    wall_run(m, a, b, [(DOOR[0] - a.x, DOOR[1] - a.x, "door")], rnd, V((0, -1, 0)))                      # front
    wall_run(m, b, c_, [(lo - b.y, hi - b.y, "win") for lo, hi in WINDOWS["right"]], rnd, V((1, 0, 0)))  # right
    wall_run(m, d, c_, [(lo - d.x, hi - d.x, "win") for lo, hi in WINDOWS["back"]], rnd, V((0, 1, 0)))   # back
    wall_run(m, a, d, [(lo - a.y, hi - a.y, "win") for lo, hi in WINDOWS["left"]], rnd, V((-1, 0, 0)))   # left
    # ---- the door, swung open inward against the front wall (left of the doorway)
    m.obox(V((DOOR[0] - 0.02, Y0 + ins + 0.24, FOOT + 0.22)), (0.025, 0.44, 0.44), "wood_mid", rot=(0, 0, 0.15))
    m.obox(V((DOOR[0] - 0.035, Y0 + ins + 0.24, FOOT + 0.32)), (0.01, 0.38, 0.03), "iron_dark", rot=(0, 0, 0.15))
    m.obox(V((DOOR[0] - 0.035, Y0 + ins + 0.24, FOOT + 0.1)), (0.01, 0.38, 0.03), "iron_dark", rot=(0, 0, 0.15))
    # ---- the hearth on the back wall: stone surround, fire bed (the flames are parts), the chimney goes up the roof
    hz = HEARTH + V((0, -0.11, 0))
    m.obox(hz + V((0, 0.03, 0.24)), (0.42, 0.16, 0.48), "stone_mid", top="stone_light")
    m.obox(hz + V((0, -0.06, 0.13)), (0.24, 0.02, 0.22), "soot")
    m.obox(hz + V((0, -0.11, 0.015)), (0.44, 0.14, 0.03), "stone_light")
    m.blob(hz + V((0, -0.08, 0.04)), V((0.08, 0.035, 0.02)), "torch_orange", 7, 3)
    m.obox(hz + V((0, -0.06, 0.26)), (0.46, 0.06, 0.03), "wood_dark")                                     # mantel
    m.cyl(hz + V((-0.14, -0.06, 0.29)), 0.025, 0.04, "gold", segs=7, r2=0.032)                           # trophy cups on it
    m.cyl(hz + V((0.13, -0.06, 0.295)), 0.015, 0.05, "silver", segs=6)
    # ---- the war table: low, a raid map on it, candles, a dagger, coins; a big rug under it and the crew
    m.obox(V((TABLE_C.x, TABLE_C.y, FOOT + 0.0005)), (1.3, 0.95, 0.001), "teal_dark")
    m.obox(V((TABLE_C.x, TABLE_C.y, FOOT + 0.001)), (1.22, 0.87, 0.001), "cloth_red")
    tz = TOP - 0.003
    m.obox(V((TABLE_C.x, TABLE_C.y, tz - 0.012)), (TABLE_L, TABLE_D, 0.024), "wood_dark", top="wood_mid")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.obox(V((TABLE_C.x + sx * (TABLE_L / 2 - 0.05), TABLE_C.y + sy * (TABLE_D / 2 - 0.04), (tz - 0.024 + FOOT) / 2)),
                   (0.04, 0.04, tz - 0.024 - FOOT), "wood_dark")
    # ---- notice board (right wall, inside), trophy shelf (left wall), loot corner (back right), tool rack (front left)
    nb = V((X1 - ins - WALL_T / 2 - 0.01, 0.0, FOOT))
    m.obox(nb + V((-0.005, 0, 0.3)), (0.02, 0.4, 0.26), "leather")
    for k, (y, z, w, h) in enumerate(((-0.12, 0.35, 0.1, 0.12), (0.05, 0.36, 0.12, 0.1), (0.13, 0.27, 0.08, 0.08), (-0.06, 0.24, 0.1, 0.07))):
        m.obox(nb + V((-0.017, y, z)), (0.003, w, h), "cloth_cream" if k % 2 else "bone")
        m.blob(nb + V((-0.02, y, z + h / 2 - 0.01)), V((0.006, 0.006, 0.006)), "ruby", 4, 3)
    ts = V((X0 + ins + WALL_T / 2 + 0.06, 0.55, FOOT))
    m.obox(ts + V((0, 0, 0.34)), (0.12, 0.5, 0.02), "wood_light")
    for y in (-0.22, 0.22):
        m.obox(ts + V((-0.03, y, 0.3)), (0.04, 0.03, 0.06), "wood_dark")
    cr = ts + V((0, -0.12, 0.35))                                                                        # crown
    m.cyl(cr + V((0, 0, 0.03)), 0.045, 0.06, "gold", segs=8)
    for i in range(5):
        aa = TAU * i / 5
        m.cyl(cr + V((0.04 * math.cos(aa), 0.04 * math.sin(aa), 0.075)), 0.012, 0.03, "gold_light", segs=4, r2=0.0)
    m.cyl(ts + V((0, 0.08, 0.38)), 0.03, 0.06, "gold", segs=7, r2=0.04)                                 # goblet
    m.obox(ts + V((0.02, 0.18, 0.43)), (0.02, 0.16, 0.16), "gold_dark", rot=(0, -0.2, 0))               # painting
    m.obox(ts + V((0.012, 0.18, 0.43)), (0.012, 0.12, 0.12), "teal_dark", rot=(0, -0.2, 0))
    lc = V((0.95, 0.95, FOOT))                                                                           # loot corner
    m.blob(lc + V((0, 0, 0.0)), V((0.22, 0.2, 0.1)), "gold_dark", 10, 4)
    for k in range(10):
        aa = rnd.uniform(0, TAU)
        r = rnd.uniform(0.0, 0.16)
        PR.coin(m, lc + V((r * math.cos(aa), r * math.sin(aa), 0.1 * math.sqrt(max(0.0, 1 - (r / 0.2) ** 2)) + 0.004)), r=0.024,
                tilt=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 1))
    for k, sw in enumerate(("ruby", "sapphire", "emerald")):
        PR.gem(m, lc + V((-0.08 + 0.08 * k, -0.05 + 0.03 * k, 0.11)), 0.026, sw, rot=k)
    ch = V((0.62, 1.0, FOOT))                                                                            # chest
    m.obox(ch + V((0, 0, 0.07)), (0.26, 0.16, 0.14), "wood_mid", top="wood_dark")
    m.obox(ch + V((0, -0.081, 0.09)), (0.04, 0.01, 0.05), "gold")
    for x in (-0.1, 0.1):
        m.obox(ch + V((x, 0, 0.07)), (0.025, 0.17, 0.145), "iron_dark")
    tr = V((X0 + ins + WALL_T / 2 + 0.03, -0.62, FOOT))                                                  # tool rack
    m.obox(tr + V((0, 0, 0.26)), (0.02, 0.42, 0.04), "wood_dark")
    m.obox(tr + V((0, 0, 0.13)), (0.02, 0.42, 0.04), "wood_dark")
    m.cyl(tr + V((0.03, -0.12, 0.18)), 0.05, 0.03, "rope", axis=(1, 0, 0), segs=10, cap="rope_dark")      # rope coil
    m.beam(tr + V((0.03, -0.12, 0.25)), tr + V((0.05, -0.12, 0.3)), 0.008, "iron")                         # grappling hook
    for s in (-1, 1):
        m.beam(tr + V((0.05, -0.12, 0.3)), tr + V((0.06, -0.12 + 0.035 * s, 0.33)), 0.006, "iron")
    m.beam(tr + V((0.02, 0.04, 0.03)), tr + V((0.02, 0.1, 0.3)), 0.01, "iron_dark")                        # crowbar
    for k in range(4):
        m.obox(tr + V((0.022, 0.12 + 0.025 * k, 0.24)), (0.004, 0.006, 0.06), "silver")                    # picks
    for p in (V((-0.9, -0.6, FOOT)), V((0.9, -0.55, FOOT))):                                             # barrels
        m.cyl(p + V((0, 0, 0.1)), 0.08, 0.2, "wood_mid", cap="wood_dark", segs=8)
        for z in (0.04, 0.16):
            m.cyl(p + V((0, 0, z)), 0.084, 0.014, "iron", segs=8)
    for y in (-0.62,):                                                                                   # a bench by the door
        m.obox(V((0.55, y, FOOT + 0.07)), (0.4, 0.1, 0.02), "wood_light")
        for x in (0.4, 0.7):
            m.obox(V((x, y, FOOT + 0.03)), (0.03, 0.08, 0.06), "wood_dark")
    # ---- the guild's banner on the back wall (inside), a bench along the left wall
    gb = V((0.18, Y1 - ins - WALL_T / 2 - 0.006, FOOT))
    m.obox(gb + V((0, 0, 0.3)), (0.26, 0.008, 0.36), "teal")
    m.obox(gb + V((0, -0.005, 0.34)), (0.16, 0.004, 0.07), "fur_mask")                                  # the mask
    for x in (-0.04, 0.04):
        m.obox(gb + V((x, -0.008, 0.34)), (0.03, 0.003, 0.018), "cloth_cream")
    m.obox(gb + V((0, -0.005, 0.15)), (0.26, 0.006, 0.03), "gold")
    m.beam(gb + V((-0.16, -0.01, 0.485)), gb + V((0.16, -0.01, 0.485)), 0.012, "wood_dark")
    lb = V((X0 + ins + WALL_T / 2 + 0.07, -0.15, FOOT))
    m.obox(lb + V((0, 0, 0.075)), (0.1, 0.5, 0.02), "wood_light")
    for y in (-0.2, 0.2):
        m.obox(lb + V((0, y, 0.033)), (0.08, 0.03, 0.066), "wood_dark")
    m.cyl(lb + V((0.0, 0.12, 0.105)), 0.02, 0.044, "wood_light", segs=7, cap="cloth_cream")              # a mug left on it
    # ---- outside: torches on posts by the steps
    for x in (-0.55, 0.55):
        m.obox(V((x, Y0 - 0.2, 0.25)), (0.04, 0.04, 0.5), "wood_dark")
        m.obox(V((x, Y0 - 0.2, 0.51)), (0.07, 0.07, 0.03), "iron_dark")
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    # ---- the map on the table (still): the readers' paws hold it
    mm = B.M()
    mm.obox(V((TABLE_C.x, TABLE_C.y, TOP - 0.0015)), (TABLE_L - 0.04, TABLE_D + 0.004, 0.003), "cloth_cream")
    for k in range(6):
        p = V((TABLE_C.x + rnd.uniform(-0.38, 0.38), TABLE_C.y + rnd.uniform(-0.09, 0.09), TOP + 0.0005))
        mm.obox(p, (rnd.uniform(0.05, 0.12), 0.01, 0.001), "water" if k < 2 else ("moss" if k < 4 else "stone_mid"), rot=(0, 0, rnd.uniform(0, 3)))
    hx = V((TABLE_C.x + 0.32, TABLE_C.y + 0.02, TOP + 0.0006))                                            # the target
    mm.obox(hx, (0.07, 0.05, 0.001), "gold_dark")
    for a_ in (0.78, -0.78):
        mm.obox(hx + V((0, 0, 0.0004)), (0.05, 0.008, 0.001), "cloth_red", rot=(0, 0, a_))
    mm.beam(hx + V((-0.01, 0.01, 0.0)), hx + V((-0.02, 0.015, 0.06)), 0.006, "silver")                    # dagger in it
    mm.obox(hx + V((-0.022, 0.016, 0.066)), (0.03, 0.008, 0.008), "gold")
    for k in range(4):
        PR.coin(mm, V((TABLE_C.x - 0.4, TABLE_C.y - 0.03, TOP + 0.003 + 0.006 * k)), r=0.02)
    for x in (-0.12, 0.12):                                                                             # candle dishes
        mm.cyl(V((TABLE_C.x + x, TABLE_C.y, TOP + 0.005)), 0.018, 0.01, "gold_dark", segs=8)
        mm.cyl(V((TABLE_C.x + x, TABLE_C.y, TOP + 0.028)), 0.007, 0.036, "cloth_cream", segs=6)
    mapo = mm.obj("pr_map", coll)
    mapo.parent = root
    roof = build_roof(coll, rnd)
    roof.parent = root
    parts = {}
    for i, x in enumerate((-0.12, 0.12)):                                                                # candle flames
        mm = B.M()
        c = V((TABLE_C.x + x, TABLE_C.y, TOP + 0.047))
        mm.cyl(c + V((0, 0, 0.011)), 0.006, 0.022, "flame_yellow", segs=5, r2=0.0)
        parts[f"pr_candle_{i + 1}"] = A.part(mm.obj(f"pr_candle_{i + 1}", coll), root, c)
    for i, (dx, h, sw) in enumerate(((0.0, 0.12, "torch_orange"), (0.05, 0.08, "flame_yellow"), (-0.05, 0.085, "flame_yellow"))):
        mm = B.M()
        c = hz + V((dx, -0.08, 0.04))
        mm.cyl(c + V((0, 0, h / 2)), 0.028 if i == 0 else 0.018, h, sw, segs=5, r2=0.0)
        parts[f"pr_fire_{i + 1}"] = A.part(mm.obj(f"pr_fire_{i + 1}", coll), root, c)
    for i, x in enumerate((-0.55, 0.55)):                                                                # torch flames
        mm = B.M()
        c = V((x, Y0 - 0.2, 0.525))
        mm.cyl(c + V((0, 0, 0.04)), 0.025, 0.08, "torch_orange" if i else "flame_yellow", segs=5, r2=0.0)
        parts[f"pr_torch_{i + 1}"] = A.part(mm.obj(f"pr_torch_{i + 1}", coll), root, c)
    for i, x in enumerate((-0.45, 0.45)):                                                                # banners by the door
        mm = B.M()
        top = V((x, Y0 - 0.005, FOOT + WALL_H - 0.03))
        mm.obox(top + V((0, -0.006, -0.16)), (0.18, 0.01, 0.3), "teal")
        mm.obox(top + V((0, -0.012, -0.12)), (0.11, 0.004, 0.05), "fur_mask")                         # the mask emblem
        mm.obox(top + V((-0.03, -0.014, -0.12)), (0.02, 0.003, 0.014), "cloth_cream")
        mm.obox(top + V((0.03, -0.014, -0.12)), (0.02, 0.003, 0.014), "cloth_cream")
        mm.obox(top + V((0, -0.006, -0.3)), (0.18, 0.011, 0.02), "gold")
        parts[f"pr_banner_{i + 1}"] = A.part(mm.obj(f"pr_banner_{i + 1}", coll), root, top)
    for i, (y, z) in enumerate(((-0.12, 0.35), (0.05, 0.36), (0.13, 0.27))):                              # loose notices
        mm = B.M()
        top = nb + V((-0.022, y, z + 0.03))
        mm.obox(top + V((-0.001, 0, -0.035)), (0.002, 0.07, 0.05), "cloth_cream")
        parts[f"pr_notice_{i + 1}"] = A.part(mm.obj(f"pr_notice_{i + 1}", coll), root, top)
    smoke = []
    chim = V((HEARTH.x, HEARTH.y - 0.05, 0))
    for i in range(3):                                                                                   # smoke: children of the roof
        mm = B.M()
        c = V((chim.x, chim.y, RIDGE + 0.32))
        A.puff(mm, c, 0.05, "stone_pale")
        ob = A.part(mm.obj(f"pr_smoke_{i + 1}", coll), root, c)
        ob.parent = roof
        ob.location = c - roof.location
        parts[f"pr_smoke_{i + 1}"] = ob
        smoke.append(ob)
    return root, mapo, roof, parts, smoke


def build_roof(coll, rnd):
    """Two slopes of plank strips laid edge to edge (each strip its own box, butted, never overlapping), a ridge beam,
    filled gables with a round vent, the chimney, a pole with a banner on the ridge."""
    m = B.M()
    ov = 0.07
    xa, xb = X0 - ov, X1 + ov
    ya, yb = Y0 - ov, Y1 + ov
    yc = (Y0 + Y1) / 2
    half = (yb - ya) / 2
    rise = RIDGE - EAVE
    ang = math.atan2(rise, (Y1 - Y0) / 2)
    Ls = half / math.cos(ang)
    t = 0.045
    n = 9
    for s in (-1, 1):
        down = V((0, s * math.cos(ang), -math.sin(ang)))
        up_n = V((0, s * math.sin(ang), math.cos(ang)))
        top = V(((xa + xb) / 2, yc, RIDGE + t * 0.5))
        for k in range(n):                                                  # strips run along X, stacked down the slope
            u0, u1 = Ls * k / n, Ls * (k + 1) / n
            c = top + down * ((u0 + u1) / 2) + up_n * (0.002 * (k % 2))
            m.obox(c, (xb - xa - 0.03 * (k % 2), u1 - u0 - 0.002, t), "wood_mid" if k % 2 else "leather",
                   rot=(-s * ang, 0, 0))
        eave = top + down * Ls + up_n * 0.004                                # a darker trim board along the eave
        m.obox(eave - down * 0.02, (xb - xa + 0.02, 0.04, t + 0.012), "wood_dark", rot=(-s * ang, 0, 0))
    m.prism_x([(Y0 + 0.02, EAVE), (Y1 - 0.02, EAVE), (yc, RIDGE - 0.02)], X0 + 0.04, X0 + 0.07, "wood_weathered")   # gables
    m.prism_x([(Y0 + 0.02, EAVE), (Y1 - 0.02, EAVE), (yc, RIDGE - 0.02)], X1 - 0.07, X1 - 0.04, "wood_weathered")
    for x in (X0 + 0.035, X1 - 0.035):
        m.cyl(V((x, yc, EAVE + 0.3)), 0.06, 0.02, "wood_dark", axis=(1, 0, 0), segs=8, cap="soot")
    m.beam(V((xa - 0.02, yc, RIDGE + t + 0.02)), V((xb + 0.02, yc, RIDGE + t + 0.02)), 0.05, "wood_dark")       # ridge beam
    m.obox(V((0, yc, EAVE - 0.02)), (X1 - X0 - 0.1, Y1 - Y0 - 0.1, 0.012), "wood_dark")                       # ceiling joists line
    chim = V((HEARTH.x, HEARTH.y - 0.05, 0))
    m.obox(V((chim.x, chim.y, (EAVE + RIDGE + 0.3) / 2 + 0.02)), (0.16, 0.16, RIDGE + 0.3 - EAVE), "stone_mid", top="soot")
    m.obox(V((chim.x, chim.y, RIDGE + 0.29)), (0.2, 0.2, 0.03), "stone_light")
    pole = V((0.85, yc, RIDGE + t))
    m.cyl(pole + V((0, 0, 0.18)), 0.01, 0.36, "wood_dark", segs=5)
    m.obox(pole + V((0.07, 0, 0.3)), (0.13, 0.008, 0.09), "teal")
    m.obox(pole + V((0.07, -0.005, 0.3)), (0.06, 0.003, 0.03), "fur_mask")
    roof = m.obj(f"{NAME}_roof", coll)
    return roof


def clips(parts):
    def common(p, crew):
        pose = {}
        for i, (f, ph) in enumerate(((4, 0.0), (5, 0.33), (6, 0.66))):
            pose[f"pr_fire_{i + 1}"] = (None, A.q((0, 0, 1), 20 * math.sin(TAU * (f * p + ph))),
                                        (1, 1, 1 + 0.15 * math.sin(TAU * (f * p + ph))))
        for i in (1, 2):
            pose[f"pr_torch_{i}"] = (None, A.q((0, 0, 1), 25 * math.sin(TAU * (5 * p + 0.4 * i))), (1, 1, 1 + 0.18 * math.sin(TAU * (6 * p + i))))
            pose[f"pr_banner_{i}"] = (None, A.q((1, 0, 0), 4 * math.sin(TAU * (p + 0.3 * i))), None)
            pose[f"pr_candle_{i}"] = (None, A.q((0, 0, 1), 15 * math.sin(TAU * (4 * p + i))),
                                      (1, 1, (1.0 + 0.4 * crew) * (1 + 0.15 * math.sin(TAU * (5 * p + i)))))
        for i in range(1, 4):
            u = (p * 2 + i / 3) % 1.0
            pose[f"pr_smoke_{i}"] = (V((0.05 * u, 0.03 * math.sin(TAU * u), 0.32 * u)), None, A.puff_size(u))
        for i in range(1, 4):
            pose[f"pr_notice_{i}"] = (None, A.q((0, 1, 0), crew * 10 * max(0.0, math.sin(TAU * (2 * p + 0.3 * i)))), None)
        return pose

    A.animate(parts, {"idle": (FRAMES, lambda p: common(p, 0.0)), "work": (FRAMES, lambda p: common(p, 1.0))})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, mapo, roof, parts, smoke = build(coll, random.Random(151))
    for i, (p, face) in enumerate(GATHER):
        A.spot(root, f"spot_gather_{i + 1}", p, face)
    clips(parts)
    total = K.tris(root) + K.tris(mapo) + K.tris(roof) + sum(K.tris(o) for o in parts.values())
    print(f"STAT {NAME}: {total} tris (shell+inside {K.tris(root)}, roof {K.tris(roof)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "guild_hall.blend"), relative_remap=True)
    A.export()
    crew, objs = [], []
    for i in range(len(GATHER)):
        rig, mesh, _ = A.raccoon_at(bpy.data.objects[f"spot_gather_{i + 1}"], clip="work_read")
        crew.append((rig, mesh, None, "work", {"pr_map": None}))
        objs += [rig, mesh]
    allow = [(f"pr_fire_{i}", NAME) for i in (1, 2, 3)] + [("pr_fire_1", "pr_fire_2"), ("pr_fire_1", "pr_fire_3"), ("pr_fire_2", "pr_fire_3")] + \
            [(f"pr_torch_{i}", NAME) for i in (1, 2)] + [(f"pr_banner_{i}", NAME) for i in (1, 2)] + \
            [(f"pr_candle_{i}", "pr_map") for i in (1, 2)] + [(f"pr_notice_{i}", NAME) for i in (1, 2, 3)] + \
            [(f"pr_smoke_{i}", n) for i in (1, 2, 3) for n in (f"{NAME}_roof",)] + \
            [(f"pr_smoke_{i}", f"pr_smoke_{j}") for i in (1, 2, 3) for j in (1, 2, 3) if i < j]
    probs = A.check(root, 3, 3, crew=crew, allow=allow, sky=[o.name for o in smoke])
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, objs, ROOT / "renders" / "bld_guild_hall_loops.gif", target=(0.0, 0.1, 0.25), dist=5.6,
                       pitch=45, idle_frames=24, grid_n=5, step=3, hide_in_work=[roof] + smoke)


if __name__ == "__main__":
    main()
