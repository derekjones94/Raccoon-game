"""chr_weasel: the raccoons' rival. Same style, same skeleton, same actions as chr_raccoon.

Style: chunky low-poly, flat shaded, palette colours, every limb one smooth loft (no lumps pushed into each other).
Reference read: tall slim standing weasel -- long body flowing into a long neck, small head with a pointed snout,
small round ears, beady black eyes, cream throat and belly, long hind feet, a long tail that runs along the ground
and curls up at the end with a black tip (stoat). Rival touches: sly angled brows and a red bandana.

Rig: KayKit "Rig_Medium" names and hierarchy, identical to the raccoons (KayKit bakes, hand slots and tools work the
same); rest pose = the same relaxed A-pose; the six raccoon actions are baked on with the shared HANG layer.
Size: ~0.43 m to the ear tips (raccoon adult 0.40).

Run:  python3 tools/build_weasel.py
Out:  chr_weasel.blend, export/chr_weasel.glb, renders/weasel_*.png/gif
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_raccoon_blockout as RB  # noqa: E402
import build_raccoon_rig as RR  # noqa: E402
import build_raccoon_anims as AN  # noqa: E402

ROOT = P.ROOT
V = Vector
NAME = "chr_weasel"
if "scarf" not in RB.GROUPS:
    RB.GROUPS.append("scarf")

BROWN, TAN, CREAM, DARK, BLACK = "fur_brown", "fur_tan", "fur_cream", "fur_dark", "fur_charcoal"

BODY_CTRL = [  # (y, z, half-width, half-depth): hips -> belly -> chest -> long neck, ending inside the skull
    (0.016, 0.072, 0.018, 0.018), (0.015, 0.095, 0.057, 0.054), (0.008, 0.140, 0.059, 0.055), (0.000, 0.190, 0.052, 0.049),
    (-0.005, 0.238, 0.046, 0.044), (-0.010, 0.282, 0.035, 0.034), (-0.018, 0.320, 0.030, 0.029), (-0.026, 0.352, 0.026, 0.025),
]
ARM_CTRL = [  # (x, y, z, r) shoulder -> elbow -> wrist -> paw, left side
    (0.028, -0.012, 0.282, 0.010), (0.038, -0.016, 0.272, 0.020), (0.046, -0.022, 0.258, 0.021), (0.052, -0.028, 0.236, 0.017),
    (0.055, -0.032, 0.218, 0.016), (0.057, -0.037, 0.196, 0.014), (0.058, -0.041, 0.178, 0.013), (0.058, -0.045, 0.168, 0.016),
    (0.058, -0.050, 0.156, 0.012), (0.058, -0.053, 0.149, 0.004),
]
LEG_CTRL = [  # (x, y, z, sideways r, other r) hip (inside) -> haunch -> knee -> ankle -> long flat foot -> toes
    (0.040, 0.015, 0.120, 0.015, 0.015), (0.044, 0.012, 0.100, 0.038, 0.040), (0.048, 0.000, 0.075, 0.044, 0.045),
    (0.050, -0.008, 0.050, 0.030, 0.030), (0.050, -0.004, 0.030, 0.020, 0.020), (0.050, -0.020, 0.016, 0.022, 0.012),
    (0.050, -0.048, 0.011, 0.022, 0.011), (0.050, -0.072, 0.009, 0.017, 0.008), (0.050, -0.081, 0.009, 0.006, 0.004),
]
TAIL_CTRL = [  # (x, y, z, r): from inside the hips, back along the floor, curling up at the end
    (0.0, 0.030, 0.110, 0.020), (0.0, 0.070, 0.080, 0.024), (0.010, 0.130, 0.045, 0.027), (0.030, 0.200, 0.032, 0.029),
    (0.045, 0.260, 0.040, 0.031), (0.040, 0.300, 0.075, 0.033), (0.020, 0.305, 0.115, 0.034), (0.000, 0.290, 0.145, 0.028),
    (-0.010, 0.275, 0.160, 0.010),
]
HEAD_C = V((0, -0.03, 0.375))


def flat_tri(m, pts, normal, t, swatch):
    """A thin triangular plate (front + back face + edges), e.g. the bandana's knot lying on the chest."""
    f = [m.bm.verts.new(q + normal * t / 2) for q in pts]
    b = [m.bm.verts.new(q - normal * t / 2) for q in pts]
    faces = [m.bm.faces.new(f), m.bm.faces.new(list(reversed(b)))]
    for i in range(3):
        j = (i + 1) % 3
        faces.append(m.bm.faces.new((f[i], b[i], b[j], f[j])))
    for fc in faces:
        fc[m.sw] = m.names.index(swatch)
        fc[m.grp] = m.cur


def build_mesh(coll):
    m = RB.Parts()
    X = V((1, 0, 0))
    # ---- body + neck: one loft, cream down the front (throat and belly), brown elsewhere
    sm = RB.spline([(V((0, y, z)), a, b) for y, z, a, b in BODY_CTRL], 16)
    pts, ra, rb = [q for q, *_ in sm], [a for _, a, _ in sm], [b for *_, b in sm]

    def body_frame(i, d):
        return X, d.cross(X).normalized()             # ub points to the BACK for an upright body

    def body_sw(i, a):
        if a >= 0 and math.sin(a) < -0.5 and 2 <= i <= 13:
            return CREAM
        return BROWN
    m.part("body").loft(pts, ra, rb, body_frame, body_sw, segs=12)
    # ---- bandana round the neck + a triangular flap on the chest
    nc, nr = V((0, -0.012, 0.297)), 0.041
    ring = [nc + V((math.cos(t) * nr, math.sin(t) * nr * 0.95, -0.006 * math.cos(t - math.pi / 2)))
            for t in [2 * math.pi * k / 14 for k in range(15)]]
    m.part("scarf").tube(ring, [0.007] * 15, ["cloth_red"], segs=6)
    flat_tri(m, [nc + V((-0.024, -0.040, 0.002)), nc + V((0.024, -0.040, 0.002)), nc + V((0.0, -0.046, -0.042))],
             V((0, -1, 0.12)).normalized(), 0.004, "cloth_red")                        # knot flap, flat on the chest
    # ---- head: skull, upturned pointed snout, cream muzzle and cheeks, black nose and beady eyes, sly brows
    c = HEAD_C
    m.part("head").blob(c, V((0.052, 0.050, 0.045)), BROWN, 14, 9)
    m.blob(c + V((0, -0.045, -0.010)), V((0.028, 0.046, 0.024)), BROWN, 10, 6)                  # snout
    m.blob(c + V((0, -0.040, -0.022)), V((0.032, 0.042, 0.017)), CREAM, 10, 5)                  # muzzle underside
    m.blob(c + V((0, -0.016, -0.034)), V((0.032, 0.032, 0.016)), CREAM, 10, 5)                  # chin, runs into the throat
    m.blob(c + V((0, -0.089, -0.004)), V((0.011, 0.008, 0.009)), "fur_mask", 6, 4)              # nose
    for sx in (1, -1):
        m.blob(c + V((sx * 0.026, -0.038, 0.014)), V((0.011, 0.007, 0.011)), "fur_mask", 8, 5)  # beady eyes
        m.blob(c + V((sx * 0.024, -0.044, 0.017)), V((0.004, 0.003, 0.004)), "flame_white", 4, 3)   # shine
        m.blob(c + V((sx * 0.026, -0.040, 0.029)), V((0.016, 0.004, 0.004)), BLACK, 6, 3,
               Matrix.Rotation(sx * -0.38, 4, "Y"))                                             # sly brows (inner end low)
        for dz, tilt in ((0.004, 0.25), (0.0, 0.0), (-0.004, -0.22)):                           # whiskers
            m.cone(c + V((sx * 0.016, -0.074, -0.013 + dz)), (sx, -0.25, tilt), 0.0018, 0.03, DARK, segs=3)
    # ---- small round ears: flat lofts out of the skull, tan inner panel
    for sx, sd in ((1, "L"), (-1, "R")):
        ed = V((sx * 0.55, 0.2, 0.8)).normalized()
        e0 = c + V((sx * 0.036, 0.012, 0.022))
        epts = [e0 + ed * (0.04 * k / 6) for k in range(7)]
        prof = [0.015, 0.020, 0.022, 0.021, 0.017, 0.011, 0.003]
        thick = [0.008, 0.008, 0.007, 0.006, 0.005, 0.004, 0.001]
        ew = ed.cross(V((0, 1, 0))).normalized()
        et = ew.cross(ed).normalized()
        et = -et if et.y > 0 else et

        def ear_sw(i, a):
            return TAN if (a >= 0 and 1 <= i <= 3 and math.sin(a) > 0.7) else BROWN
        m.part("ear_" + sd).loft(epts, prof, thick, lambda i, d, ew=ew, et=et: (ew, et), ear_sw, segs=8)
    # ---- arms: shoulder -> paw, one tube
    for sx, sd in ((1, "L"), (-1, "R")):
        sm = RB.spline([(V((sx * x, y, z)), r) for x, y, z, r in ARM_CTRL], 15)
        apts, ar = [q for q, _ in sm], [r for _, r in sm]
        m.part("arm_" + sd).tube(apts, ar, [BROWN if apts[i].z > 0.176 else DARK for i in range(len(apts) - 1)], segs=8)
    # ---- legs: haunch -> knee -> ankle -> long foot, one loft, plus three little claws
    for sx, sd in ((1, "L"), (-1, "R")):
        sm = RB.spline([(V((sx * x, y, z)), a, b) for x, y, z, a, b in LEG_CTRL], 14)
        lpts, la, lb = [q for q, *_ in sm], [a for _, a, _ in sm], [b for *_, b in sm]
        foot_from = next(i for i, q in enumerate(lpts) if q.y < -0.012)
        m.part("thigh_" + sd).loft(lpts, la, lb, lambda i, d: (X, d.cross(X).normalized()),
                                   lambda i, a, f=foot_from: BROWN if i < f else DARK, segs=10)
        for cx in (-0.011, 0.0, 0.011):
            m.cone(V((sx * 0.05 + cx, -0.078, 0.006)), (0, -1, -0.3), 0.0035, 0.012, "bone", segs=3)
    # ---- tail: along the floor and curling up, black tip
    sm = RB.spline([(V((x, y, z)), r) for x, y, z, r in TAIL_CTRL], 20)
    tpts, tr = [q for q, _ in sm], [r for _, r in sm]
    m.part("tail").tube(tpts, tr, [BROWN if i < 14 else BLACK for i in range(len(tpts) - 1)], segs=10)

    ids = [f[m.sw] for f in m.bm.faces]
    me = bpy.data.meshes.new(NAME + "_mesh")
    m.bm.to_mesh(me)
    m.bm.free()
    ob = bpy.data.objects.new(NAME + "_mesh", me)
    coll.objects.link(ob)
    me.materials.append(bpy.data.materials["M_Palette"])
    for i, sid in enumerate(ids):
        P.set_swatch(ob, m.names[sid], [i])
    zmin = min(v.co.z for v in me.vertices)
    for v in me.vertices:
        v.co.z -= zmin
    return ob, zmin


# ---------------------------------------------------------------- rig (same names + hierarchy as the raccoons)
def tail_pt(t):
    sm = RB.spline([(V((x, y, z)), r) for x, y, z, r in TAIL_CTRL], 41)
    return sm[round(t * 40)][0]


def bones():
    B = {
        "root": ((0, 0, 0), (0, 0.06, 0), None),
        "hips": ((0, 0.012, 0.09), (0, 0.006, 0.15), "root"),
        "spine": ((0, 0.006, 0.15), (0, 0.0, 0.22), "hips"),
        "chest": ((0, 0.0, 0.22), (0, -0.012, 0.30), "spine"),
        "head": ((0, -0.014, 0.30), (0, -0.03, 0.42), "chest"),
        "ear.l": ((0.036, -0.018, 0.397), (0.058, -0.010, 0.43), "head"),
        "upperarm.l": ((0.040, -0.017, 0.270), (0.055, -0.032, 0.218), "chest"),
        "lowerarm.l": ((0.055, -0.032, 0.218), (0.058, -0.041, 0.178), "upperarm.l"),
        "wrist.l": ((0.058, -0.041, 0.178), (0.058, -0.044, 0.168), "lowerarm.l"),
        "hand.l": ((0.058, -0.044, 0.168), (0.058, -0.053, 0.148), "wrist.l"),
        "handslot.l": ((0.058, -0.048, 0.162), (0.058, -0.088, 0.162), "hand.l"),
        "upperleg.l": ((0.044, 0.010, 0.110), (0.050, -0.008, 0.050), "hips"),
        "lowerleg.l": ((0.050, -0.008, 0.050), (0.050, -0.004, 0.026), "upperleg.l"),
        "foot.l": ((0.050, -0.004, 0.026), (0.050, -0.048, 0.011), "lowerleg.l"),
        "toes.l": ((0.050, -0.048, 0.011), (0.050, -0.080, 0.008), "foot.l"),
    }
    for k in list(B):
        if k.endswith(".l"):
            h, t, par = B[k]
            B[k[:-2] + ".r"] = ((-h[0], h[1], h[2]), (-t[0], t[1], t[2]), par[:-2] + ".r" if par.endswith(".l") else par)
    ts = [0.0, 0.22, 0.44, 0.64, 0.82, 1.0]
    for i in range(5):
        B[f"tail_{i + 1}"] = (tuple(tail_pt(ts[i])), tuple(tail_pt(ts[i + 1])), "hips" if i == 0 else f"tail_{i}")
    return B


ALLOWED = {
    "body": ["hips", "spine", "chest", "head"],              # the long neck bends between chest and head
    "head": ["head"], "ear_L": ["ear.l", "head"], "ear_R": ["ear.r", "head"],
    "arm_L": ["chest", "upperarm.l", "lowerarm.l", "wrist.l", "hand.l"],
    "arm_R": ["chest", "upperarm.r", "lowerarm.r", "wrist.r", "hand.r"],
    "thigh_L": ["hips", "upperleg.l", "lowerleg.l", "foot.l", "toes.l"],
    "thigh_R": ["hips", "upperleg.r", "lowerleg.r", "foot.r", "toes.r"],
    "tail": ["hips", "tail_1", "tail_2", "tail_3", "tail_4", "tail_5"],
    "scarf": ["chest"],
}
SOFT = {"body", "arm_L", "arm_R", "thigh_L", "thigh_R"}


def build_rig(coll, zshift):
    arm = bpy.data.armatures.new(NAME + "_rig")
    rig = bpy.data.objects.new(NAME, arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    segs = {}
    for name, (h, t, par) in bones().items():
        b = arm.edit_bones.new(name)
        b.head, b.tail = V(h) - V((0, 0, zshift)), V(t) - V((0, 0, zshift))
        b.roll = 0.0
        if par:
            b.parent = arm.edit_bones[par]
        segs[name] = (b.head.copy(), b.tail.copy())
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.display_type = "STICK"
    return rig, segs


def skin(ob, rig, segs):
    me = ob.data
    grp = me.attributes["grp"].data
    vpart = {}
    for poly in me.polygons:
        for vi in poly.vertices:
            vpart.setdefault(vi, RB.GROUPS[grp[poly.index].value])
    for b in segs:
        if b not in RR.UNWEIGHTED:
            ob.vertex_groups.new(name=b)
    for v in me.vertices:
        part = vpart[v.index]
        bl = ALLOWED[part]
        if len(bl) == 1:
            ob.vertex_groups[bl[0]].add([v.index], 1.0, "REPLACE")
            continue
        ds = sorted((RR.seg_dist(v.co, *segs[b]), b) for b in bl)[:2]
        k = 2.5 if part in SOFT else 4
        w0, w1 = (1 / max(d, 1e-4) ** k for d, _ in ds)
        ob.vertex_groups[ds[0][1]].add([v.index], w0 / (w0 + w1), "REPLACE")
        ob.vertex_groups[ds[1][1]].add([v.index], w1 / (w0 + w1), "REPLACE")
    ob.parent = rig
    mod = ob.modifiers.new("rig", "ARMATURE")
    mod.object = rig


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    sc = bpy.context.scene
    sc.render.fps = AN.FPS
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell")):
            bpy.data.objects.remove(o)
    assets = bpy.data.collections["Assets"]
    ob, zmin = build_mesh(assets)
    before = tris(ob)
    RR.remove_hidden_faces(ob)
    rig, segs = build_rig(assets, zmin)
    skin(ob, rig, segs)
    RR.apply_rest_pose(rig, ob)
    print(f"STAT {NAME}: {before} -> {tris(ob)} tris, {len(rig.data.bones)} bones, height {ob.dimensions.z:.3f} m")
    AN.TAIL_LOW = True                                    # the weasel's tail already lies along the floor
    for name, (fn, frames) in AN.ACTIONS.items():
        AN.bake_action(rig, name, fn, frames, 1.1, ob)
    AN.TAIL_LOW = False
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "chr_weasel.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
    renders(rig, ob)


def renders(rig, ob):
    from PIL import Image, ImageDraw, ImageFont
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.view_settings.view_transform = "Standard"
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.18, 0.23, 1)
    for n in ("ref_floor", "ref_grid_lines"):
        bpy.data.objects[n].hide_render = True
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    out = ROOT / "renders"
    cam = bpy.data.objects.new("wcam", bpy.data.cameras.new("wcam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"

    def shot(d, tgt, size, res=(460, 520)):
        d = V(d).normalized()
        cam.data.ortho_scale = size
        cam.location = V(tgt) + d * 3
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x, sc.render.resolution_y = res
        p = out / "_w.png"
        sc.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        im = Image.open(p).convert("RGB")
        p.unlink()
        return im

    def sheet(tiles, cols, path, w=460, h=520):
        rows = (len(tiles) + cols - 1) // cols
        S = Image.new("RGB", (w * cols, (h + 34) * rows), (24, 26, 32))
        dd = ImageDraw.Draw(S)
        for i, (im, lab) in enumerate(tiles):
            x, y = w * (i % cols), (h + 34) * (i // cols)
            S.paste(im, (x, y))
            dd.text((x + 10, y + h + 8), lab, font=font, fill=(235, 236, 242))
        S.save(path)

    # 1) turnaround in the game look (idle frame 0), like the reference sheet
    rig.animation_data.action = bpy.data.actions["idle"]
    sc.frame_set(0)
    T = (0, 0.06, 0.21)
    sheet([(shot((-0.6, -0.8, 0.15), T, 0.62), "three-quarter"), (shot((0, -1, 0.1), T, 0.62), "front"),
           (shot((-1, 0, 0.1), T, 0.62), "side"), (shot((0.2, 1, 0.15), T, 0.62), "back"),
           (shot((-0.55, -0.6, 0.45), (0, -0.04, 0.37), 0.2), "head close-up"),
           (shot((0.7, 0.5, 0.5), (0.03, 0.2, 0.08), 0.32), "tail")], 3, out / "weasel_turnaround.png")
    # 2) rival lineup with the raccoon adult, from the game camera angle
    with bpy.data.libraries.load(str(ROOT / "chr_raccoon_animated.blend")) as (src, dst):
        dst.objects = ["chr_raccoon", "chr_raccoon_mesh"]
    rrig, rmesh = dst.objects
    for o in (rrig, rmesh):
        sc.collection.objects.link(o)
    rrig.location = (-0.32, 0.0, 0)
    rrig.animation_data_create()
    rrig.animation_data.action = bpy.data.actions.get("idle.001") or rrig.animation_data.action
    for a in bpy.data.actions:
        if a.name.startswith("idle") and a != bpy.data.actions["idle"]:
            rrig.animation_data.action = a
    sc.frame_set(0)
    lineup = [(shot((-0.45, -0.85, 0.75), (-0.16, 0.05, 0.18), 0.9, (920, 520)), "rival lineup: raccoon (0.40 m) vs weasel (0.43 m)")]
    sheet(lineup, 1, out / "weasel_lineup.png", w=920)
    for o in (rrig, rmesh):
        o.hide_render = True
    # 3) rig tests: A-pose rest, elbows, knees, a hammer in handslot.r
    rig.animation_data.action = None
    hammer = RR.tool_in_slot(rig, "handslot.r", bpy.data.collections["Reference"])
    tests = []
    for lab, rots, drop in (("rest: A-pose", None, 0), ("game look", {}, 0),
                            ("elbows", {"upperarm.l": [((1, 0, 0), -35)], "lowerarm.l": [((1, 0, 0), -95)],
                                        "upperarm.r": [((0, 1, 0), 50), ((1, 0, 0), -20)], "lowerarm.r": [((1, 0, 0), -80)]}, 0),
                            ("knees (squat)", {"upperleg.l": [((1, 0, 0), -70)], "upperleg.r": [((1, 0, 0), -70)],
                                               "lowerleg.l": [((1, 0, 0), 95)], "lowerleg.r": [((1, 0, 0), 95)],
                                               "foot.l": [((1, 0, 0), -25)], "foot.r": [((1, 0, 0), -25)], "spine": [((1, 0, 0), 15)]}, -0.05),
                            ("hammer in handslot.r", {"upperarm.r": [((1, 0, 0), -60), ((0, 1, 0), 12)],
                                                      "lowerarm.r": [((1, 0, 0), -70)]}, 0)):
        RR.clear_pose(rig)
        if rots is not None:
            qs = AN.pose_quats(rig, AN.merge(AN.HANG, rots))
            for pb in rig.pose.bones:
                pb.rotation_quaternion = qs[pb.name]
        if drop:
            b = rig.data.bones["hips"]
            rig.pose.bones["hips"].location = b.matrix_local.to_3x3().inverted() @ V((0, 0, drop))
        bpy.context.view_layer.update()
        hammer.hide_render = lab != "hammer in handslot.r"
        tests.append((shot((-0.45, -0.85, 0.3), (0, 0.04, 0.2), 0.62), lab))
    RR.clear_pose(rig)
    hammer.hide_render = True
    sheet(tests, 5, out / "weasel_rig_tests.png")
    # 4) the six actions: frame strips + GIFs of idle and walk
    sc.cycles.samples = 12
    rows, gifs = [], {}
    for name, (fn, frames) in AN.ACTIONS.items():
        rig.animation_data.action = bpy.data.actions[name]
        step = 2 if frames <= 48 else 3
        ims = []
        for f in range(0, frames, step):
            sc.frame_set(f)
            ims.append(shot((-0.5, -0.8, 0.45), (0, 0.06, 0.18), 0.66, (360, 360)))
        if name in ("idle", "walk", "sneak"):
            ims[0].save(out / f"weasel_{name}.gif", save_all=True, append_images=ims[1:], duration=int(1000 * step / AN.FPS), loop=0)
        rows.append((name, [ims[int(i * len(ims) / 6)] for i in range(6)]))
    S = Image.new("RGB", (6 * 240, len(rows) * 270), (24, 26, 32))
    dd = ImageDraw.Draw(S)
    for r, (name, ims) in enumerate(rows):
        for i, im in enumerate(ims):
            S.paste(im.resize((240, 240), Image.LANCZOS), (240 * i, 270 * r))
        dd.text((10, 270 * r + 244), f"chr_weasel  {name}", font=font, fill=(235, 236, 242))
    S.save(out / "weasel_anim_frames.png")


if __name__ == "__main__":
    main()
