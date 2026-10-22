"""Raccoon final mesh + rig (adult, kit, elder share one skeleton layout and bone names).

Mesh: the approved blockout volumes, with every face that sits fully inside another volume removed (never seen,
      costs tris, and would poke through when deforming).
Rig:  KayKit "Rig_Medium" names and hierarchy, so KayKit animation packs bake straight on:
        root > hips > spine > chest > head > ear.l/.r
                              chest > upperarm > lowerarm (elbow) > wrist > hand > handslot (tool grip, unweighted)
                hips > upperleg > lowerleg (knee) > foot > toes ;  hips > tail_1..5
      Rest pose = relaxed A-pose (arms ~45 deg out, soft elbows and knees): modelled arms-down, skinned, then posed
      and applied as the new rest (weights carry over exactly).
      Bones are built in the same space as the blockout and go through the same head-size / hunch / scale steps,
      so the elder's skeleton is hunched like its mesh and the kit's is small like its mesh.
Skin: each face knows its body part; a part may only use a few bones (head -> head, arm -> arm chain, tail ->
      tail chain ...), blended by distance to the bones, so parts never get pulled by the wrong bone.

Run:  python3 tools/build_raccoon_rig.py
Out:  chr_raccoon_rigged.blend, export/chr_raccoon*.glb, renders/raccoon_rig_*.png
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_raccoon_blockout as RB  # noqa: E402
import build_kit_blockout as K  # noqa: E402
from build_raccoon_anims import HANG, REST_POSE, merge, pose_quats  # noqa: E402

ROOT = P.ROOT


def tail_point(t):
    """Same path as the blockout tail."""
    return Vector((0, 0.03 + 0.19 * math.sin(t * 1.5), 0.075 + 0.21 * t + 0.06 * math.sin(t * math.pi)))


HC = Vector((0, -0.005, 0.265))
# name: (head, tail, parent, space)  space: lower = planted, upper = tilts with the hunch, head = + head-size knob
BONES = {
    "root": ((0, 0, 0), (0, 0.06, 0), None, "lower"),
    "hips": ((0, 0, 0.08), (0, 0, 0.12), "root", "lower"),
    "spine": ((0, 0, 0.12), (0, 0, 0.175), "hips", "upper"),
    "chest": ((0, 0, 0.175), (0, -0.005, 0.212), "spine", "upper"),
    "head": ((0, -0.005, 0.212), (0, -0.005, 0.33), "chest", "head"),
    "ear.l": ((0.044, 0.01, 0.305), (0.07, 0.019, 0.362), "head", "head"),
    # arm: shoulder -> elbow (halfway down the arm) -> wrist (base of the paw) -> hand (the paw)
    "upperarm.l": ((0.064, -0.012, 0.195), (0.073, -0.028, 0.148), "chest", "upper"),
    "lowerarm.l": ((0.073, -0.028, 0.148), (0.079, -0.040, 0.112), "upperarm.l", "upper"),
    "wrist.l": ((0.079, -0.040, 0.112), (0.080, -0.043, 0.104), "lowerarm.l", "upper"),
    "hand.l": ((0.080, -0.043, 0.104), (0.081, -0.050, 0.080), "wrist.l", "upper"),
    # tool grip: in the middle of the paw, Y axis = along the handle toward the tool head (forward, arms-down look)
    "handslot.l": ((0.081, -0.052, 0.094), (0.081, -0.092, 0.094), "hand.l", "upper"),
    # leg: hip -> knee (halfway) -> ankle -> toes at the front of the foot
    "upperleg.l": ((0.048, 0.0, 0.09), (0.049, -0.004, 0.055), "hips", "lower"),
    "lowerleg.l": ((0.049, -0.004, 0.055), (0.050, -0.006, 0.030), "upperleg.l", "lower"),
    "foot.l": ((0.050, -0.006, 0.030), (0.050, -0.050, 0.018), "lowerleg.l", "lower"),
    "toes.l": ((0.050, -0.050, 0.018), (0.050, -0.072, 0.014), "foot.l", "lower"),
}
for k in list(BONES):                                     # mirror the left side (.l -> .r)
    if k.endswith(".l"):
        h, t, par, sp = BONES[k]
        BONES[k[:-2] + ".r"] = ((-h[0], h[1], h[2]), (-t[0], t[1], t[2]), par[:-2] + ".r" if par.endswith(".l") else par, sp)
TS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
for i in range(5):
    BONES[f"tail_{i + 1}"] = (tuple(tail_point(TS[i])), tuple(tail_point(TS[i + 1])), "hips" if i == 0 else f"tail_{i}", "lower")
UNWEIGHTED = {"root", "handslot.l", "handslot.r"}

ALLOWED = {   # body part -> bones it may be weighted to
    "foot_L": ["foot.l", "toes.l", "lowerleg.l"], "foot_R": ["foot.r", "toes.r", "lowerleg.r"],
    "thigh_L": ["hips", "upperleg.l", "lowerleg.l", "foot.l", "toes.l"],     # the whole leg tube, hip to toes
    "thigh_R": ["hips", "upperleg.r", "lowerleg.r", "foot.r", "toes.r"],
    "tail": ["hips", "tail_1", "tail_2", "tail_3", "tail_4", "tail_5"],
    "body": ["hips", "spine", "chest"],
    "shoulder_L": ["chest", "upperarm.l"], "shoulder_R": ["chest", "upperarm.r"],
    "arm_L": ["chest", "upperarm.l", "lowerarm.l", "wrist.l", "hand.l"],      # the shoulder dome blends into the chest
    "arm_R": ["chest", "upperarm.r", "lowerarm.r", "wrist.r", "hand.r"],
    "head": ["head"], "ear_L": ["ear.l", "head"], "ear_R": ["ear.r", "head"],
    "cane": ["hand.r"],
}
SOFT = {"arm_L", "arm_R", "thigh_L", "thigh_R", "foot_L", "foot_R"}     # softer blend across elbow / knee loops


def place(p, space, spec):
    """Blockout build space -> final mesh space (same steps as RB.raccoon)."""
    p = Vector(p)
    if space == "head":
        p = HC + (p - HC) * spec["head"]
    if space in ("head", "upper"):
        hip = Vector((0, 0, 0.08))
        p = hip + Matrix.Rotation(math.radians(spec["hunch"]), 3, "X") @ (p - hip)
    k = spec["scale"] * 1.06
    return p * k + Vector((0, 0, 0.001 * k))          # + the blockout's "lowest point to z 0" shift (feet bottom at -0.001)


# ---------------------------------------------------------------- hidden faces
def remove_hidden_faces(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    # connected components (each blockout volume is one closed shell)
    comp = {}
    cid = 0
    for f in bm.faces:
        if f in comp:
            continue
        stack = [f]
        comp[f] = cid
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h not in comp:
                        comp[h] = cid
                        stack.append(h)
        cid += 1
    cgrp = {}
    grp_layer = bm.faces.layers.int.get("grp")
    for f in bm.faces:
        cgrp.setdefault(comp[f], f[grp_layer])
    trees = []
    for c in range(cid):
        faces = [f for f in bm.faces if comp[f] == c]
        vs = list({v for f in faces for v in f.verts})
        idx = {v: i for i, v in enumerate(vs)}
        trees.append(BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in faces]))
    d = Vector((0.31, 0.17, 0.93)).normalized()

    def inside(tree, p):
        n, o = 0, p.copy()
        for _ in range(16):
            hit = tree.ray_cast(o, d)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + d * 1e-5
        return n % 2 == 1

    cache = {}
    kill = []
    for f in bm.faces:
        c = comp[f]
        for o in range(cid):
            if o == c or cgrp[o] != cgrp[c]:      # only hide behind volumes that move with this one
                continue
            if all(cache.setdefault((v.index, o), inside(trees[o], v.co)) for v in f.verts):
                kill.append(f)
                break
    before = len(bm.faces)
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()
    return before, len(ob.data.polygons)


# ---------------------------------------------------------------- rig + skin
def build_rig(spec, coll):
    arm = bpy.data.armatures.new(spec["name"] + "_rig")
    rig = bpy.data.objects.new(spec["name"], arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    segs = {}
    for name, (h, t, par, space) in BONES.items():
        b = arm.edit_bones.new(name)
        b.head, b.tail = place(h, space, spec), place(t, space, spec)
        b.roll = 0.0
        if par:
            b.parent = arm.edit_bones[par]
            b.use_connect = False
        segs[name] = (b.head.copy(), b.tail.copy())
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.display_type = "STICK"
    return rig, segs


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (p - (a + ab * t)).length


def skin(ob, rig, segs):
    me = ob.data
    grp = me.attributes["grp"].data
    vpart = {}
    for poly in me.polygons:
        for vi in poly.vertices:
            vpart.setdefault(vi, RB.GROUPS[grp[poly.index].value])
    for b in segs:
        if b not in UNWEIGHTED:
            ob.vertex_groups.new(name=b)
    for v in me.vertices:
        part = vpart[v.index]
        bones = ALLOWED[part]
        if len(bones) == 1:
            ob.vertex_groups[bones[0]].add([v.index], 1.0, "REPLACE")
            continue
        ds = sorted((seg_dist(v.co, *segs[b]), b) for b in bones)[:2]
        k = 2.5 if part in SOFT else 4
        w0, w1 = (1 / max(d, 1e-4) ** k for d, _ in ds)
        ws = {ds[0][1]: w0 / (w0 + w1), ds[1][1]: w1 / (w0 + w1)}
        if part in ("arm_L", "arm_R"):
            # the top of the shoulder dome stays mostly with the chest (like a real shoulder), fading into the arm
            # below: raising the arm then lifts the arm instead of rolling the dome into the chest
            ua = "upperarm." + part[-1].lower()
            sh, el = segs[ua]
            up = (segs["chest"][1] - segs["chest"][0]).normalized()
            L = (el - sh).length
            t = min(max(((v.co - sh).dot(up) + 0.25 * L) / (0.7 * L), 0.0), 1.0)
            wc = 0.7 * t * t * (3 - 2 * t)
            if wc > 0:
                ws = {b_: w * (1 - wc) for b_, w in ws.items()}
                ws["chest"] = ws.get("chest", 0.0) + wc
        for b_, w in ws.items():
            ob.vertex_groups[b_].add([v.index], w, "REPLACE")
    ob.parent = rig
    mod = ob.modifiers.new("rig", "ARMATURE")
    mod.object = rig


def build_variant(spec, coll):
    ob = RB.raccoon(spec, coll)
    ob.name = spec["name"] + "_mesh"
    ob.data.name = spec["name"] + "_mesh"
    before = tris(ob)
    remove_hidden_faces(ob)
    rig, segs = build_rig(spec, coll)
    skin(ob, rig, segs)
    apply_rest_pose(rig, ob)
    return rig, ob, before


def apply_rest_pose(rig, ob):
    """Pose the arms-down model into the relaxed A-pose and make that the rest pose (mesh + bones)."""
    qs = pose_quats(rig, REST_POSE)
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = qs[pb.name]
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    cos = [v.co.copy() for v in ev.data.vertices]          # deformed positions (same vertex order)
    for v, c in zip(ob.data.vertices, cos):
        v.co = c
    ob.data.update()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.armature_apply(selected=False)           # current pose -> new rest
    bpy.ops.object.mode_set(mode="OBJECT")
    clear_pose(rig)


# ---------------------------------------------------------------- posing helpers
def clear_pose(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = Quaternion()
        pb.location = (0, 0, 0)


X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
POSES = {   # None = the rest pose itself; others start from the arms-down game look (HANG)
    "rest: A-pose": None,
    "game look (HANG)": {},
    "elbows": {"upperarm.l": [(X, -35)], "lowerarm.l": [(X, -95)], "upperarm.r": [(Y, 50), (X, -20)], "lowerarm.r": [(X, -80)]},
    "knees (squat)": {"upperleg.l": [(X, -70)], "upperleg.r": [(X, -70)], "lowerleg.l": [(X, 95)], "lowerleg.r": [(X, 95)],
                      "foot.l": [(X, -25)], "foot.r": [(X, -25)], "spine": [(X, 18)], "head": [(X, -12)],
                      "upperarm.l": [(X, -40)], "upperarm.r": [(X, -40)], "lowerarm.l": [(X, -45)], "lowerarm.r": [(X, -45)]},
    "hammer in handslot.r": {"upperarm.r": [(X, -60), (Y, 12)], "lowerarm.r": [(X, -70)], "head": [(X, 8), (Z, -10)],
                             "upperarm.l": [(X, -20)], "lowerarm.l": [(X, -30)]},
    "carry": {"upperarm.l": [(X, -150), (Y, 8)], "upperarm.r": [(X, -150), (Y, -8)], "lowerarm.l": [(X, -35)],
              "lowerarm.r": [(X, -35)], "spine": [(X, -8)], "head": [(X, 10)]},
}
HIPS_DROP = {"knees (squat)": -0.05}


def apply_pose(rig, name, spec):
    clear_pose(rig)
    if POSES[name] is not None:
        qs = pose_quats(rig, merge(HANG, POSES[name]))
        for pb in rig.pose.bones:
            pb.rotation_quaternion = qs[pb.name]
    if name in HIPS_DROP:
        k = spec["scale"] * 1.06
        b = rig.data.bones["hips"]
        rig.pose.bones["hips"].location = b.matrix_local.to_3x3().inverted() @ Vector((0, 0, HIPS_DROP[name] * k))
    bpy.context.view_layer.update()


def tool_in_slot(rig, slot, coll):
    """A test hammer parented to the hand slot: handle along the slot's +Y, head at the +Y end."""
    m = K.Mesh()
    m.box((-0.006, -0.03, -0.006), (0.006, 0.1, 0.006), "wood_light")         # handle passes through the paw
    m.box((-0.012, 0.085, -0.03), (0.012, 0.115, 0.022), "iron_light")        # head
    ob = m.obj(f"test_hammer_{slot}", coll)
    clear_pose(rig)
    bpy.context.view_layer.update()
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = slot
    ob.matrix_world = rig.matrix_world @ rig.pose.bones[slot].matrix        # sits exactly on the slot's frame
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def bone_sticks(rig, segs, coll):
    """Renderable bone display: a thin octahedral stick per bone (Cycles can't draw armatures)."""
    m = K.Mesh()
    for name, (a, b) in segs.items():
        d = b - a
        L = d.length
        r = bmesh.ops.create_cone(m.bm, cap_ends=True, segments=4, radius1=0.006, radius2=0.0015, depth=L)
        q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        bmesh.ops.transform(m.bm, matrix=Matrix.Translation(a + rig.location) @ q @ Matrix.Translation((0, 0, L / 2)), verts=r["verts"])
        m.tag({f for v in r["verts"] for f in v.link_faces}, "torch_orange" if name.startswith("tail") else
              ("ruby" if name.startswith("handslot") else ("teal_light" if name.endswith((".l", ".r")) else "gold_light")))
    return m.obj(rig.name + "_bones_view", coll)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    out = {}
    for spec in (RB.ADULT, RB.KIT, RB.ELDER):
        rig, ob, before = build_variant(spec, assets)
        out[spec["name"]] = (rig, ob, spec, before)
        print(f"STAT {spec['name']}: {before} -> {tris(ob)} tris after removing hidden faces, {len(rig.data.bones)} bones, "
              f"height {round(ob.dimensions.z, 3)} m")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "chr_raccoon_rigged.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})

    # ------------------------------------------------ renders
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 32
    sc.view_settings.view_transform = "Standard"
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.18, 0.23, 1)
    for n in ("ref_floor", "ref_grid_lines"):
        bpy.data.objects[n].hide_render = True
    rnd_dir = ROOT / "renders"
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    cam = bpy.data.objects.new("pcam", bpy.data.cameras.new("pcam"))
    sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    sc.camera = cam
    adult_rig, adult_ob, adult_spec, _ = out["chr_raccoon"]
    for nm, (rig, ob, spec, _) in out.items():
        rig.location.x = {"chr_raccoon": 0, "chr_raccoon_kit": 0.42, "chr_raccoon_elder": 0.86}[nm]

    def shot(path, target, d, scale, res=(520, 560)):
        cam.data.ortho_scale = scale
        K_look(cam, target, d)
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    def K_look(c, target, d):
        d = Vector(d).normalized()
        c.location = Vector(target) + d * 5
        c.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()

    def solo(objs):
        for o in bpy.data.objects:
            if o.type == "MESH" and (o.name.endswith("_mesh") or o.name.endswith("_bones_view") or o.name.startswith("test_")):
                o.hide_render = o not in objs

    # 1) rig view: mesh as see-through + bone sticks, front and side
    segs_adult = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in adult_rig.data.bones}
    sticks = bone_sticks(adult_rig, segs_adult, ref)
    ghost = bpy.data.materials.new("ghost")
    ghost.use_nodes = True
    gb = ghost.node_tree.nodes["Principled BSDF"]
    gb.inputs["Base Color"].default_value = (0.8, 0.82, 0.9, 1)
    gb.inputs["Alpha"].default_value = 0.22
    adult_ob.data.materials.append(ghost)                 # slot 1, used only for this render
    for p in adult_ob.data.polygons:
        p.material_index = 1
    solo([adult_ob, sticks])
    tiles = []
    for lab, d in (("rig front", (0, -1, 0)), ("rig side", (1, 0, 0))):
        f = rnd_dir / f"_{lab}.png"
        shot(f, (0, 0.04, 0.2), d, 0.62)
        tiles.append((lab, f))
    for p in adult_ob.data.polygons:
        p.material_index = 0
    adult_ob.data.materials.pop(index=1)
    # 2) pose tests (adult), three-quarter from above like the game camera; a test hammer rides in handslot.r
    hammer = tool_in_slot(adult_rig, "handslot.r", ref)
    solo([adult_ob, hammer])
    pitch, yaw = math.radians(30), math.radians(-20)
    d34 = (math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch))
    for name in POSES:
        apply_pose(adult_rig, name, adult_spec)
        f = rnd_dir / f"_{name}.png"
        shot(f, (0, 0.03, 0.17), d34, 0.62)
        tiles.append((f"pose: {name}", f))
    clear_pose(adult_rig)
    sheet = Image.new("RGB", (520 * 4, 600 * 2), (24, 26, 32))
    dd = ImageDraw.Draw(sheet)
    for i, (lab, f) in enumerate(tiles):
        x, y = 520 * (i % 4), 600 * (i // 4)
        sheet.paste(Image.open(f), (x, y))
        dd.text((x + 12, y + 568), lab, font=font, fill=(235, 236, 242))
        f.unlink()
    sheet.save(rnd_dir / "raccoon_rig_poses.png")
    # 3) all three variants in the same poses (shared skeleton)
    solo([o for (_, o, _, _) in out.values()])
    tiles = []
    hammer.hide_render = True
    for name in ("rest: A-pose", "game look (HANG)", "knees (squat)"):
        for nm, (rig, ob, spec, _) in out.items():
            apply_pose(rig, name, spec)
        f = rnd_dir / f"_{name}_all.png"
        shot(f, (0.43, 0.03, 0.17), d34, 1.4, (900, 420))
        tiles.append((f"{name}: adult / kit / elder", f))
    for (rig, _, _, _) in out.values():
        clear_pose(rig)
    sheet = Image.new("RGB", (900, 460 * 3), (24, 26, 32))
    dd = ImageDraw.Draw(sheet)
    for i, (lab, f) in enumerate(tiles):
        sheet.paste(Image.open(f), (0, 460 * i))
        dd.text((12, 460 * i + 428), lab, font=font, fill=(235, 236, 242))
        f.unlink()
    sheet.save(rnd_dir / "raccoon_rig_variants.png")


if __name__ == "__main__":
    main()
