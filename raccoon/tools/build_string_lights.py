"""bld_string_lights_2x1: two posts with a sag of stolen lanterns strung between them. A decoration: warm light for
the tunnels.

Two rough posts, guyed with rope to stakes, a wire sagging between them, and seven mismatched lanterns hanging from
it, each pinched from somewhere else: tin lanterns, a paper one, a jar of glow-worms, a ship's lamp, a teapot with a
candle in it. A coil of spare wire and a crate at one post.

Clips (24 fps)
  idle  96 fr  the lanterns sway on the wire, each to its own beat, and their flames flicker
  work  96 fr  the same (decorations have no work of their own)

Run:  python3 tools/build_string_lights.py   (--no-renders)
Out:  string_lights.blend, export/bld_string_lights_2x1.glb, renders/bld_string_lights_loops.gif
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

ROOT = A.ROOT
V = Vector
TAU = 2 * math.pi
NAME = "bld_string_lights_2x1"
FRAMES = 96
POST_X, POST_H = 0.82, 0.72
SAG = 0.16
LIGHTS = 7


def wire_at(x):
    """The wire's height at x: a gentle sag between the post tops."""
    t = x / POST_X
    return POST_H - 0.02 - SAG * (1 - t * t)


def lantern(m, kind, c, sw_glow):
    """A lantern hanging with its hook at c; returns the flame's centre."""
    if kind == "tin":
        m.cyl(c + V((0, 0, -0.03)), 0.004, 0.06, "iron_dark", segs=4)
        m.cyl(c + V((0, 0, -0.07)), 0.032, 0.02, "iron", segs=6, r2=0.012)
        m.cyl(c + V((0, 0, -0.11)), 0.026, 0.06, sw_glow, segs=6)
        for k in range(3):
            a = TAU * k / 3
            m.beam(c + V((0.027 * math.cos(a), 0.027 * math.sin(a), -0.08)), c + V((0.027 * math.cos(a), 0.027 * math.sin(a), -0.14)),
                   0.005, "iron_dark")
        m.cyl(c + V((0, 0, -0.145)), 0.03, 0.01, "iron", segs=6)
        return c + V((0, 0, -0.11))
    if kind == "paper":
        m.cyl(c + V((0, 0, -0.02)), 0.003, 0.04, "rope", segs=4)
        m.blob(c + V((0, 0, -0.09)), V((0.045, 0.045, 0.05)), "cloth_red", 8, 5)
        m.cyl(c + V((0, 0, -0.045)), 0.022, 0.008, "wood_dark", segs=6)
        m.cyl(c + V((0, 0, -0.135)), 0.022, 0.008, "wood_dark", segs=6)
        return c + V((0, 0, -0.09))
    if kind == "jar":
        m.cyl(c + V((0, 0, -0.02)), 0.003, 0.04, "rope", segs=4)
        m.cyl(c + V((0, 0, -0.05)), 0.022, 0.012, "iron", segs=8)
        m.cyl(c + V((0, 0, -0.095)), 0.03, 0.08, "teal_light", segs=8)
        return c + V((0, 0, -0.095))
    if kind == "ship":
        m.cyl(c + V((0, 0, -0.025)), 0.004, 0.05, "iron_dark", segs=4)
        m.cyl(c + V((0, 0, -0.065)), 0.028, 0.03, "copper", segs=8, r2=0.014)
        m.cyl(c + V((0, 0, -0.11)), 0.026, 0.06, sw_glow, segs=8)
        m.cyl(c + V((0, 0, -0.11)), 0.03, 0.01, "copper", segs=8)
        m.cyl(c + V((0, 0, -0.145)), 0.03, 0.012, "copper", segs=8)
        return c + V((0, 0, -0.11))
    # a teapot with a candle in it, hung by its handle
    m.beam(c, c + V((0, 0, -0.03)), 0.004, "rope")
    m.blob(c + V((0, 0, -0.09)), V((0.045, 0.045, 0.04)), "cloth_blue", 8, 4)
    m.cyl(c + V((0.055, 0, -0.085)), 0.008, 0.04, "cloth_blue", segs=5, axis=(1, 0, 0.7), r2=0.005)
    m.cyl(c + V((0, 0, -0.05)), 0.02, 0.012, "cloth_cream", segs=6)
    m.cyl(c + V((0, -0.04, -0.09)), 0.016, 0.004, sw_glow, segs=6, axis=(0, 1, 0))             # light from its hole
    return c + V((0, -0.04, -0.09))


KINDS = ["tin", "paper", "jar", "ship", "teapot", "tin", "paper"]
GLOWS = ["flame_yellow", "flame_yellow", "teal_light", "flame_yellow", "torch_orange", "torch_orange", "flame_yellow"]


def build(coll, rnd):
    m = B.M()
    m.obox(V((0, 0, 0.002)), (1.94, 0.94, 0.004), "wood_weathered")
    for sx in (-1, 1):
        x = sx * POST_X
        m.cyl(V((x, 0, POST_H / 2)), 0.028, POST_H, "wood_bark", segs=7, cap="wood_cut")
        m.blob(V((x, 0, 0.02)), V((0.07, 0.07, 0.03)), "stone_mid", 6, 3)                          # rocks at its foot
        m.beam(V((x, 0, POST_H - 0.04)), V((x + sx * 0.12, 0.0, 0.0)), 0.006, "rope")              # guy rope
        m.cyl(V((x + sx * 0.12, 0, 0.03)), 0.012, 0.06, "wood_mid", segs=5)                         # its stake
        m.obox(V((x - sx * 0.02, 0, POST_H - 0.02)), (0.05, 0.02, 0.02), "iron_dark")              # the wire's hook
    prev = None
    for k in range(25):                                                                                # the wire
        x = -POST_X + 2 * POST_X * k / 24
        p = V((x, 0, wire_at(x)))
        if prev is not None:
            m.beam(prev, p, 0.005, "iron_dark")
        prev = p
    m.cyl(V((POST_X - 0.12, 0.2, 0.025)), 0.06, 0.03, "iron_dark", segs=10, cap="iron")              # spare wire coil
    m.obox(V((-POST_X + 0.14, 0.18, 0.06)), (0.14, 0.12, 0.12), "wood_mid", top="wood_light")       # a crate
    m.cyl(V((-POST_X + 0.14, 0.18, 0.135)), 0.02, 0.03, "cloth_cream", segs=6)                      # a spare candle
    root = m.obj(NAME, coll)
    PR.trim_below_floor(root)
    parts = {}
    for i in range(LIGHTS):
        x = -POST_X + 2 * POST_X * (i + 1) / (LIGHTS + 1)
        hook = V((x, 0, wire_at(x) - 0.004))
        mm = B.M()
        flame = lantern(mm, KINDS[i], hook, GLOWS[i])
        parts[f"pr_lantern_{i + 1}"] = A.part(mm.obj(f"pr_lantern_{i + 1}", coll), root, hook)
        mm = B.M()
        sw = "teal_light" if KINDS[i] == "jar" else "flame_white"
        mm.blob(flame, V((0.008, 0.008, 0.014)), sw, 5, 3)
        parts[f"pr_flame_{i + 1}"] = A.part(mm.obj(f"pr_flame_{i + 1}", coll), root, flame)
    return root, parts


def clips(parts):
    rel = {i: parts[f"pr_flame_{i + 1}"].location - parts[f"pr_lantern_{i + 1}"].location for i in range(LIGHTS)}   # at rest

    def pose(p):
        out = {}
        for i in range(LIGHTS):
            a = 6 * math.sin(TAU * (2 * p + 0.13 * i)) + 3 * math.sin(TAU * (3 * p + 0.31 * i))
            b = 4 * math.sin(TAU * (p + 0.2 * i))
            r = A.q((1, 0, 0), a) @ A.q((0, 1, 0), b)
            out[f"pr_lantern_{i + 1}"] = (None, r, None)
            s = 1 + 0.25 * math.sin(TAU * (7 * p + 0.4 * i)) * (0.5 if KINDS[i] == "jar" else 1)
            out[f"pr_flame_{i + 1}"] = ((r @ rel[i]) - rel[i], r, (s, s, s))                          # rides in its lantern
        return out

    A.animate(parts, {"idle": (FRAMES, pose), "work": (FRAMES, pose)})
    A.rest_at(parts, "idle", 0)


def main():
    do_renders = "--no-renders" not in sys.argv
    coll = A.open_template()
    root, parts = build(coll, random.Random(21))
    clips(parts)
    print(f"STAT {NAME}: {K.tris(root) + sum(K.tris(o) for o in parts.values())} tris "
          f"(static {K.tris(root)}, moving parts {len(parts)})")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "string_lights.blend"), relative_remap=True)
    A.export()
    allow = [(n, NAME) for n in parts] + [(f"pr_flame_{i + 1}", f"pr_lantern_{i + 1}") for i in range(LIGHTS)]
    probs = A.check(root, 2, 1, allow=allow)
    A.report(NAME, probs, ROOT / "renders" / "qa_buildings.txt")
    if do_renders:
        A.render_loops(root, [], ROOT / "renders" / "bld_string_lights_loops.gif",
                       target=(0.0, 0.0, 0.4), dist=2.5, pitch=24, grid_n=4, step=3, idle_only=True)


if __name__ == "__main__":
    main()
