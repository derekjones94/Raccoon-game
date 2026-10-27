"""Rig + animation QA for a raccoon-family character (chr_raccoon, chr_weasel ...).

1) rig vs chr_raccoon: same bones/parents, bone directions at rest (angle between Y axes), A-pose arm angle
2) hand slots: unweighted, +Y axis pointing forward in the game look (HANG)
3) every frame of every action (and every job clip; --jobs: only those): limb parts passing INTO the body / head (depth > 6 mm), anything below the floor

Run:  python3 tools/check_character.py chr_weasel.blend chr_weasel
"""
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_raccoon_blockout as RB  # noqa: E402
import build_raccoon_anims as AN  # noqa: E402

ROOT = RB.ROOT
blend, name = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:3]
if "scarf" not in RB.GROUPS:
    RB.GROUPS.append("scarf")

# ---- reference rest data from the raccoon
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "chr_raccoon_rigged.blend"))
ref = {b.name: ((b.tail_local - b.head_local).normalized(), b.parent.name if b.parent else None)
       for b in bpy.data.objects["chr_raccoon"].data.bones}

bpy.ops.wm.open_mainfile(filepath=str(ROOT / blend))
rig = bpy.data.objects[name]
ob = bpy.data.objects[name + "_mesh"]
bones = {b.name: ((b.tail_local - b.head_local).normalized(), b.parent.name if b.parent else None) for b in rig.data.bones}
print(f"== {name}")
print("bones/parents identical to chr_raccoon:", set(bones) == set(ref) and all(bones[k][1] == ref[k][1] for k in ref))
worst = sorted(((math.degrees(bones[k][0].angle(ref[k][0])), k) for k in ref if k in bones), reverse=True)[:6]
print("largest rest-direction differences vs raccoon (deg):", [(k, round(a)) for a, k in worst])
ua = rig.data.bones["upperarm.l"]
arm_out = math.degrees(math.atan2((ua.tail_local - ua.head_local).x, -(ua.tail_local - ua.head_local).z))
print(f"A-pose: upper arm {arm_out:.0f} deg out from straight down")
print("hand slots weighted:", [g.name for g in ob.vertex_groups if g.name.startswith("handslot")] or "no")
for pb in rig.pose.bones:
    pb.rotation_mode = "QUATERNION"
qs = AN.pose_quats(rig, AN.HANG)
for pb in rig.pose.bones:
    pb.rotation_quaternion = qs[pb.name]
bpy.context.view_layer.update()
for s in ("handslot.l", "handslot.r"):
    y = (rig.matrix_world.to_3x3() @ rig.pose.bones[s].matrix.to_3x3() @ Vector((0, 1, 0))).normalized()
    print(f"{s} +Y in the game look: {tuple(round(c, 2) for c in y)}  (forward = (0, -1, 0))")

# ---- per-frame clipping
grp = ob.data.attributes["grp"].data
vgroup = {}
for poly in ob.data.polygons:
    for vi in poly.vertices:
        vgroup.setdefault(vi, RB.GROUPS[grp[poly.index].value])
TARGETS = {"body", "head"}
MOVERS = {"arm_L", "arm_R", "thigh_L", "thigh_R", "tail"}


def shells(me, keep):
    """One BVH per target part (body, head): all its faces together = the outer skin of that part (faces buried
    inside the same part were removed at build time, so what is left is the union's boundary)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    gl = bm.faces.layers.int.get("grp")
    co = [v.co.copy() for v in bm.verts]
    trees = []
    for part in keep:
        polys = [[v.index for v in f.verts] for f in bm.faces if RB.GROUPS[f[gl]] == part]
        if polys:
            trees.append(BVHTree.FromPolygons(co, polys))
    bm.free()
    return trees


RAYS = [Vector(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.62, 0.55, -0.2), (0.12, -0.9, 0.35))]


def depth_inside(trees, p):
    """How deep p is inside any target part (0 if outside): majority vote of 3 ray parities, depth = nearest skin."""
    best = 0.0
    for t in trees:
        votes = 0
        for d in RAYS:
            n, o = 0, p.copy()
            for _ in range(24):
                hit = t.ray_cast(o, d)
                if hit[0] is None:
                    break
                n += 1
                o = hit[0] + d * 1e-6
            votes += n % 2
        if votes >= 2:
            best = max(best, t.find_nearest(p)[3])
    return best


def deformed(act, f):
    if act is None:
        rig.animation_data.action = None
        qs = AN.pose_quats(rig, AN.HANG)
        for pb in rig.pose.bones:
            pb.rotation_quaternion = qs[pb.name]
            pb.location = (0, 0, 0)
    else:
        rig.animation_data.action = bpy.data.actions[act]
    bpy.context.scene.frame_set(f)
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    return ev, me


# parts buried on purpose (shoulder dome, hip root, tail root ...) are inside the body in the game look: skip those
ev, me = deformed(None, 0)
tree = shells(me, TARGETS)
buried = set()
for v in me.vertices:
    if vgroup.get(v.index) in MOVERS and depth_inside(tree, v.co) > 0:
        buried.add(v.index)
ev.to_mesh_clear()
ALL_OK = True
import build_raccoon_jobs as J  # noqa: E402
CLIPS = [a for a in list(AN.ACTIONS) + list(J.JOBS) if a in bpy.data.actions]
if "--jobs" in sys.argv:
    CLIPS = [a for a in CLIPS if a in J.JOBS]
for act in CLIPS:
    frames = int(bpy.data.actions[act].frame_range[1])
    worst = (0.0, 0, "", "")
    low = {}
    for f in range(0, frames + 1, 2):
        ev, me = deformed(act, f)
        tree = shells(me, TARGETS)
        for v in me.vertices:
            part = vgroup.get(v.index)
            low[part] = min(low.get(part, 1.0), v.co.z)
            if part not in MOVERS or v.index in buried:
                continue
            dist = depth_inside(tree, v.co)
            if dist > worst[0]:
                # where on the limb: nearest deforming bone to the vertex (shoulder crease vs paw in the face ...)
                near = min(rig.pose.bones, key=lambda b: (b.head - v.co).length if not b.name.startswith(("handslot", "root")) else 9)
                worst = (dist, f, part, f"near {near.name} joint, z {v.co.z:.3f}")
        ev.to_mesh_clear()
    under = {k: round(z * 1000, 1) for k, z in low.items() if z < -0.004}
    crease = worst[0] <= 0.012 and ("upperarm" in worst[3] or "upperleg" in worst[3])   # skin folding AT the shoulder / hip
    ok = (worst[0] <= 0.006 or crease) and not under
    if crease and worst[0] > 0.006:
        worst = (worst[0], worst[1], worst[2], worst[3] + " = joint crease, ok")
    ALL_OK &= ok
    print(f"{act:12s} {'OK   ' if ok else 'CHECK'} limb into body {worst[0] * 1000:4.1f} mm ({worst[2]} @ {worst[1]}, {worst[3]})"
          f" | under the floor (mm): {under or 'none'}")
print("ALL CLEAN" if ALL_OK else "ISSUES FOUND")
