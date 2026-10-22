"""prop_cane: the elder's walking cane as a tool that hangs from handslot.r (was welded to the elder's mesh).

A walking stick with a horizontal handle: the handle runs along the slot's +Y through the closed paw (the hand-slot
convention), a knob sits behind the paw, and the shaft drops from the handle's front end to the floor, leaning a
touch forward / outward to clear the legs and feet. Nothing rises above the paw (the elder's paw hangs right under
its forearm, so a crook or a shaft top above the paw went straight into the arm).
Built in the hand slot's own space, measured on the elder in its arms-down look: object origin = the grip.
Attach to handslot.r on chr_raccoon_elder with no offset.

The tilt is not eyeballed: candidate canes are tested against the elder's real deformed body in every sampled frame
of idle and walk (cane points inside or touching any body part, apart from the grip in the paw), and the smallest
tilt with zero clashes is kept.

Run:  python3 tools/build_prop_cane.py
Out:  export/prop_cane.glb, prop_cane.blend, renders/prop_cane_*.png/gif
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402
import build_kit_blockout as K  # noqa: E402
from build_raccoon_anims import HANG, pose_quats  # noqa: E402

ROOT = P.ROOT
SLOT = "handslot.r"
R_SHAFT = 0.0075
CROOK_R = 0.017


def measure_slot():
    """Elder's hand slot in the arms-down look -> slot-space world down / forward / outward, grip height."""
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "chr_raccoon_rigged.blend"))
    rig = bpy.data.objects["chr_raccoon_elder"]
    rig.location = (0, 0, 0)
    qs = pose_quats(rig, HANG)
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = qs[pb.name]
    bpy.context.view_layer.update()
    M = rig.matrix_world @ rig.pose.bones[SLOT].matrix
    Ri = M.to_3x3().normalized().inverted()
    return (Ri @ Vector((0, 0, -1))).normalized(), (Ri @ Vector((0, -1, 0))).normalized(), \
        (Ri @ Vector((-1, 0, 0))).normalized(), M.translation.z


def cane_frame(down, fwd, out):
    fwd = (fwd - down * fwd.dot(down)).normalized()
    out = (out - down * out.dot(down) - fwd * out.dot(fwd)).normalized()
    return down, fwd, out


HANDLE_BACK, HANDLE_FRONT = 0.016, 0.032


def cane_path(down, fwd, out, height, tilt_f, tilt_o):
    """Walking stick with a horizontal handle: the handle runs along the slot's forward axis THROUGH the closed paw
    (the hand-slot convention), a knob sits behind the paw, and the shaft drops from the handle's front end -- in
    front of the paw -- to the floor. Nothing rises above the paw, so it can't push into the forearm."""
    down, fwd, out = cane_frame(down, fwd, out)
    back, front = -fwd * HANDLE_BACK, fwd * HANDLE_FRONT
    sd = (down + fwd * tilt_f + out * tilt_o).normalized()           # shaft leans a touch forward / outward
    start = front + down * 0.006                                     # just under the handle's front end
    length = (height - 0.006 - 0.003) / sd.dot(down)
    return back, front, start, sd, length


def build_cane(coll, down, fwd, out, height, tilt_f, tilt_o):
    m = K.Mesh()
    back, front, start, sd, length = cane_path(down, fwd, out, height, tilt_f, tilt_o)
    m.beam(back, front + fwd * R_SHAFT, R_SHAFT * 2, "wood_light")               # handle, through the paw
    m.beam(back - fwd * 0.006, back + fwd * 0.004, R_SHAFT * 2.8, "wood_dark")   # knob behind the paw
    m.beam(front - (start - front) * 0.6, start + sd * (length + 0.002), R_SHAFT * 2, "wood_mid")   # shaft
    m.beam(start + sd * (length - 0.018), start + sd * (length + 0.002), R_SHAFT * 2.5, "iron_dark")  # ferrule
    return m.obj("prop_cane", coll)


def sample_points(back, front, start, sd, length):
    """Points along the cane's centre-lines; the handle inside the closed paw is excluded (it is meant to be there)."""
    pts = [back.lerp(front, k / 10) for k in range(11)]
    pts += [start + sd * (k * 0.004) for k in range(int(length / 0.004) + 1)]
    return [p for p in pts if p.length > 0.026]


def components(me):
    """Per closed shell of the deformed elder mesh: a BVH (arm tube, body, head, leg ...)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    seen, comps = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack, faces = [f], []
        seen.add(f.index)
        while stack:
            g = stack.pop()
            faces.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        stack.append(h)
        vs = list({v for g in faces for v in g.verts})
        idx = {v: i for i, v in enumerate(vs)}
        comps.append(BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in g.verts] for g in faces]))
    bm.free()
    return comps


def inside(tree, p, d=Vector((0.31, 0.17, 0.93)).normalized()):
    n, o = 0, p.copy()
    for _ in range(12):
        hit = tree.ray_cast(o, d)
        if hit[0] is None:
            break
        n += 1
        o = hit[0] + d * 1e-6
    return n % 2 == 1


def clashes(rig, ob, cand, frames):
    """How many sampled cane points end up inside, or touching, the elder's body across the given frames."""
    pts = sample_points(*cand)
    bad = 0
    for act, f in frames:
        rig.animation_data.action = bpy.data.actions[act]
        bpy.context.scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        me = ob.evaluated_get(dg).to_mesh()
        trees = components(me)
        ob.evaluated_get(dg).to_mesh_clear()
        S = ob.matrix_world.inverted() @ rig.matrix_world @ rig.pose.bones[SLOT].matrix     # slot -> mesh space
        for p in pts:
            q = S @ p
            for t in trees:
                hit = t.find_nearest(q)
                if inside(t, q) or (hit[0] is not None and hit[3] < R_SHAFT * 1.1):
                    bad += 1
                    break
    return bad


def main():
    down, fwd, out, height = measure_slot()
    print(f"slot: grip height {height:.3f} m")
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "chr_raccoon_animated_elder.blend"))
    rig = bpy.data.objects["chr_raccoon_elder"]
    ob = bpy.data.objects["chr_raccoon_elder_mesh"]
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    frames = [("idle", f) for f in range(0, 48, 6)] + [("walk", f) for f in range(0, 20, 2)]
    chosen = None
    for tilt_f, tilt_o in [(0.0, 0.0), (0.05, 0.1), (0.1, 0.2), (0.15, 0.3), (0.2, 0.4), (0.25, 0.5), (0.3, 0.6), (0.35, 0.75)]:
        cand = cane_path(down, fwd, out, height, tilt_f, tilt_o)
        n = clashes(rig, ob, cand, frames)
        print(f"  tilt fwd {tilt_f:.2f} out {tilt_o:.2f}: {n} clashing points over {len(frames)} frames")
        if n == 0:
            chosen = (tilt_f, tilt_o)
            break
    if chosen is None:
        raise SystemExit("no clash-free cane found")
    print(f"CHOSEN tilt fwd {chosen[0]} out {chosen[1]}")
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    cane = build_cane(bpy.data.collections["Assets"], down, fwd, out, height, *chosen)
    print(f"STAT prop_cane: {sum(len(p.vertices) - 2 for p in cane.data.polygons)} tris")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "prop_cane.blend"), relative_remap=True)
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
    preview()


def preview():
    """The elder standing (front, side, three-quarter close-up of the hand) and walking, cane in handslot.r."""
    from PIL import Image, ImageDraw, ImageFont
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "chr_raccoon_animated_elder.blend"))
    with bpy.data.libraries.load(str(ROOT / "prop_cane.blend")) as (src, dst):
        dst.objects = ["prop_cane"]
    cane = dst.objects[0]
    sc = bpy.context.scene
    sc.collection.objects.link(cane)
    rig = bpy.data.objects["chr_raccoon_elder"]
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rig.animation_data.action = bpy.data.actions["idle"]
    sc.frame_set(0)
    bpy.context.view_layer.update()
    cane.parent = rig
    cane.parent_type = "BONE"
    cane.parent_bone = SLOT
    cane.matrix_world = rig.matrix_world @ rig.pose.bones[SLOT].matrix       # zero offset from the slot
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("ref_") and o.name not in ("ref_floor", "ref_grid_lines"):
            o.hide_render = True
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 16
    sc.view_settings.view_transform = "Standard"
    cam = bpy.data.objects.new("cc", bpy.data.cameras.new("cc"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    sc.render.resolution_x = sc.render.resolution_y = 380
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    out = ROOT / "renders"

    def shot(d, tgt=(0, 0.02, 0.17), size=0.62):
        d = Vector(d).normalized()
        cam.data.ortho_scale = size
        cam.location = Vector(tgt) + d * 3
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        p = out / "_cane.png"
        sc.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        im = Image.open(p).convert("RGB")
        p.unlink()
        return im
    tiles = [(shot((0, -1, 0.12)), "front"), (shot((-1, 0, 0.12)), "side (cane side)"),
             (shot((-0.7, -0.6, 0.4), (-0.07, -0.03, 0.12), 0.26), "hand close-up"), (shot((0, 1, 0.3)), "back")]
    rig.animation_data.action = bpy.data.actions["walk"]
    gif = []
    for f in range(0, 20, 2):
        sc.frame_set(f)
        im = shot((-0.55, -0.8, 0.35))
        ImageDraw.Draw(im).text((8, 356), f"elder walk + prop_cane  {f}/20", font=font, fill=(240, 240, 245))
        gif.append(im)
    gif[0].save(out / "prop_cane_walk.gif", save_all=True, append_images=gif[1:], duration=int(2000 / 24), loop=0)
    sheet = Image.new("RGB", (380 * 4, 410), (24, 26, 32))
    dd = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(tiles):
        sheet.paste(im, (380 * i, 0))
        dd.text((380 * i + 8, 386), lab, font=font, fill=(235, 236, 242))
    sheet.save(out / "prop_cane_elder.png")


if __name__ == "__main__":
    main()
