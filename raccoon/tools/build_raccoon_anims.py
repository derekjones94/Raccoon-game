"""Raccoon actions: idle, walk, carry, work, sneak, sleep -- 24 fps, in place, every one a seamless loop -- plus the
job clips from build_raccoon_jobs.py (work_chop, work_fish, work_scrub, work_rummage, work_water, work_tend,
work_stash, work_pump, work_stir, work_hammer, work_haggle, work_drink, work_chat, work_grind, work_read;
the elder's work_teach, the kit's work_listen).
Bones follow KayKit Rig_Medium names (upperarm.l, lowerarm.l, wrist.l, hand.l, handslot.l, upperleg.l ...).

Each action is a function of the loop phase p in [0, 1): it returns rotations per bone (armature-space axis, degrees,
applied like the rig's pose tests) and a hips offset. Keys are sampled every 2 frames from p = 0 to p = 1 inclusive,
so the last key equals the first. The same actions go on all three raccoons (same bone names); each variant is
built in its own session so the actions keep their plain names in every .glb.

Run:  python3 tools/build_raccoon_anims.py
Out:  chr_raccoon_animated.blend (+ _kit, _elder), export/chr_raccoon*.glb (with actions), renders/anim_*.gif/png
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402

ROOT = P.ROOT
FPS = 24
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)      # +X tips a down-pointing bone BACK (forward = negative)
TAU = 2 * math.pi


def s(p, k=1.0, ph=0.0):
    return math.sin(TAU * (k * p + ph))


def tail_sway(p, amp, k=1.0, lag=0.08, down=0.0):
    """Wave travelling down the tail chain."""
    return {f"tail_{i + 1}": [(Z, amp * (0.6 + 0.12 * i) * s(p, k, -lag * i))] + ([(X, down)] if i == 0 and down else [])
            for i in range(5)}


def merge(*ds):
    out = {}
    for d in ds:
        for b, rots in d.items():
            out.setdefault(b, []).extend(rots)
    return out


# ---------------------------------------------------------------- rest pose <-> game look
# The rig's REST pose is a relaxed A-pose (KayKit-style, so baked KayKit clips line up): arms ~45 deg out with a soft
# elbow, a slight knee bend. Our own actions start from the old arms-down look, so every action begins with HANG,
# the exact inverse of REST_POSE (rotations are about armature axes after the parent's pose, see pose_quats).
ARM_OUT, ELBOW, HIP, KNEE, ANKLE = 38.0, 15.0, 10.0, 18.0, 8.0
REST_POSE = {
    "upperarm.l": [(Y, -ARM_OUT)], "upperarm.r": [(Y, ARM_OUT)],
    "lowerarm.l": [(X, -ELBOW)], "lowerarm.r": [(X, -ELBOW)],
    "upperleg.l": [(X, -HIP)], "upperleg.r": [(X, -HIP)],
    "lowerleg.l": [(X, KNEE)], "lowerleg.r": [(X, KNEE)],
    "foot.l": [(X, -ANKLE)], "foot.r": [(X, -ANKLE)],
}
_c, _s = math.cos(math.radians(ARM_OUT)), math.sin(math.radians(ARM_OUT))
HANG = {
    "upperarm.l": [(Y, ARM_OUT)], "upperarm.r": [(Y, -ARM_OUT)],
    # forearm: undo the elbow about the X axis as it sits once the upper arm is swung back down
    "lowerarm.l": [((_c, 0, -_s), ELBOW)], "lowerarm.r": [((_c, 0, _s), ELBOW)],
    "upperleg.l": [(X, HIP)], "upperleg.r": [(X, HIP)],
    "lowerleg.l": [(X, -KNEE)], "lowerleg.r": [(X, -KNEE)],
    "foot.l": [(X, ANKLE)], "foot.r": [(X, ANKLE)],
}


def act(*ds):
    """An action pose: HANG first, then the action's own rotations on top."""
    return merge(HANG, *ds)


# ---------------------------------------------------------------- the six actions
def idle(p):
    breath = s(p, 2)
    flick = max(0.0, math.sin(TAU * (p - 0.62) * 6)) if 0.62 <= p < 0.62 + 1 / 6 else 0.0   # one quick ear flick
    look = 9 * math.sin(TAU * p)                                                            # slow look left / right
    rots = act({
        "spine": [(X, -1.5 * breath)], "chest": [(X, -2 * breath)],
        "head": [(Z, look), (X, 1.5 * breath)],
        "upperarm.l": [(Y, -3 - 2 * breath)], "upperarm.r": [(Y, 3 + 2 * breath)],
        "lowerarm.l": [(X, -10 - 3 * breath)], "lowerarm.r": [(X, -10 - 3 * breath)],
        "ear.l": [(Y, -30 * flick)], "ear.r": [(Y, 4 * s(p, 2, 0.3))],
    }, tail_sway(p, 7, 1))
    return rots, 0.003 * breath


CANE_HAND = False      # set while baking the elder: its right paw holds prop_cane, so that arm barely swings
TAIL_LOW = False       # set for species whose tail already lies along the floor (weasel): no extra tail droop


def walk(p, stride=28, arms=True):
    leg = stride * s(p)
    knee_l, knee_r = 30 * max(0, s(p, 1, 0.25)), 30 * max(0, s(p, 1, 0.75))       # knee folds as the leg swings through
    rots = {
        "upperleg.l": [(Y, -5), (X, -leg)], "upperleg.r": [(Y, 5), (X, leg)],             # a touch of splay: clears the belly
        "lowerleg.l": [(X, knee_l)], "lowerleg.r": [(X, knee_r)],
        "foot.l": [(X, 0.5 * leg - 12 * max(0, s(p, 1, 0.25)) - knee_l)],
        "foot.r": [(X, -0.5 * leg - 12 * max(0, s(p, 1, 0.75)) - knee_r)],
        "hips": [(Y, 5 * s(p)), (Z, -4 * s(p))],
        "spine": [(X, 4)], "chest": [(Z, 6 * s(p)), (Y, -3 * s(p))],
        "head": [(Z, -5 * s(p)), (X, -3 * s(p, 2, 0.1)), (Y, -2 * s(p))],
        "ear.l": [(Y, -6 * s(p, 2, 0.2))], "ear.r": [(Y, 6 * s(p, 2, 0.2))],
    }
    if arms:
        # swing OUT first (while the arm hangs: -Y = left arm out, +Y = right arm out), THEN raise / swing: raising
        # first would turn the outward swing into an inward one (overhead) or nothing (arm pointing forward)
        rots["upperarm.l"] = [(Y, -11), (X, 0.8 * leg)]
        rots["upperarm.r"] = [(Y, 11), (X, -0.8 * leg)]
        rots["lowerarm.l"] = [(X, -12 - 16 * max(0, -s(p)))]                           # elbow bends more on the forward swing
        rots["lowerarm.r"] = [(X, -12 - 16 * max(0, s(p)))]
        if CANE_HAND:                                       # steady cane arm, held a little out from the body
            rots["upperarm.r"] = [(X, -0.15 * leg - 6), (Y, 14)]
            rots["lowerarm.r"] = [(X, -10)]
    rots = act(rots, tail_sway(p, 12, 1, 0.1, down=0 if TAIL_LOW else -6))
    bob = 0.011 * (0.5 - 0.5 * math.cos(2 * TAU * p))          # up on each passing step
    return rots, bob


def carry(p):
    rots, bob = walk(p, stride=20, arms=False)
    hold = 3 * s(p, 2, 0.15)                                    # the load bobs a beat after the body
    rots = merge(rots, {
        "upperarm.l": [(Y, -30), (X, -120 + hold)], "upperarm.r": [(Y, 30), (X, -120 + hold)],   # load held above, arms clear of the head
        "lowerarm.l": [(X, -35 - hold)], "lowerarm.r": [(X, -35 - hold)],                 # elbows bent under the load
        "hand.l": [(X, -15)], "hand.r": [(X, -15)],
        "spine": [(X, -9)], "chest": [(X, -5)], "head": [(X, 8)],
    })
    return rots, bob * 0.7


def work(p):
    """Hammer / rummage: arms wind up with the elbows folded, then snap down straightening; body follows the hit."""
    t = p % 1.0
    lift = (t / 0.7) if t < 0.7 else (1 - (t - 0.7) / 0.3) ** 2.2        # slow up, snappy down
    lift = 0.5 - 0.5 * math.cos(math.pi * lift)
    hit = math.exp(-((t - 0.98) % 1.0) * 14) if t > 0.9 or t < 0.1 else 0.0
    rots = act({
        # hammering in front of the chest: wind up to shoulder height, never past the face
        "upperarm.l": [(Y, -22), (X, -25 - 42 * lift)], "upperarm.r": [(Y, 22), (X, -25 - 42 * lift)],
        "lowerarm.l": [(X, -20 - 25 * lift)], "lowerarm.r": [(X, -20 - 25 * lift)],
        "hand.l": [(X, -10 * lift)], "hand.r": [(X, -10 * lift)],
        "spine": [(X, 6 + 8 * (1 - lift))], "chest": [(X, 4 - 6 * lift)],
        "head": [(X, 10 - 8 * lift + 6 * hit)],
        "ear.l": [(Y, -8 * hit)], "ear.r": [(Y, 8 * hit)],
        "upperleg.l": [(X, -12)], "upperleg.r": [(X, -12)], "lowerleg.l": [(X, 18)], "lowerleg.r": [(X, 18)],
        "foot.l": [(X, -6)], "foot.r": [(X, -6)],
    }, tail_sway(p, 6, 1))
    return rots, -0.01 - 0.004 * hit


def sneak(p):
    leg = 16 * s(p)
    rots = act({
        "spine": [(X, 22)], "chest": [(X, 14), (Z, 4 * s(p))], "head": [(X, -30), (Z, 6 * s(p, 0.5))],
        "upperleg.l": [(Y, -7), (X, -32 - leg)], "upperleg.r": [(Y, 7), (X, -32 + leg)],  # crouch through the knees
        "lowerleg.l": [(X, 42 + 10 * max(0, s(p, 1, 0.25)))], "lowerleg.r": [(X, 42 + 10 * max(0, s(p, 1, 0.75)))],
        "foot.l": [(X, -10 + 0.6 * leg - 20 * max(0, s(p, 1, 0.25)))], "foot.r": [(X, -10 - 0.6 * leg - 20 * max(0, s(p, 1, 0.75)))],
        "upperarm.l": [(Y, -16), (X, -30 + 0.5 * leg)], "upperarm.r": [(Y, 16), (X, -30 - 0.5 * leg)],
        "lowerarm.l": [(X, -50)], "lowerarm.r": [(X, -50)],                                # paws up, tiptoe thief
        "hand.l": [(X, -20)], "hand.r": [(X, -20)],
        "ear.l": [(Y, 30)], "ear.r": [(Y, -30)],
        **({} if TAIL_LOW else {"tail_1": [(X, -45)], "tail_2": [(X, -18)], "tail_3": [(X, -8)]}),   # tail held low
    }, tail_sway(p, 5, 1, 0.12))
    return rots, -0.035 + 0.004 * (0.5 - 0.5 * math.cos(2 * TAU * p))


def sleep(p):
    """Sitting slumped, chin on chest, tail wrapped round the front; slow breathing, a sleepy ear twitch."""
    breath = s(p, 1)
    twitch = max(0.0, math.sin(TAU * (p - 0.45) * 8)) if 0.45 <= p < 0.45 + 1 / 8 else 0.0
    rots = act({
        "upperleg.l": [(Y, -34), (X, -66)], "upperleg.r": [(Y, 34), (X, -66)],
        "lowerleg.l": [(X, 25)], "lowerleg.r": [(X, 25)], "foot.l": [(X, 30)], "foot.r": [(X, 30)],
        # the elder (CANE_HAND) is already hunched in his rest pose: he dozes sitting up, with only a slight curl
        "spine": [(X, (3 if CANE_HAND else 10) + 2 * breath)], "chest": [(X, (2 if CANE_HAND else 9) + 2 * breath)],
        "head": [(X, 22 + 3 * breath), (Z, 10)],
        "upperarm.l": [(Y, -44), (X, -6)], "upperarm.r": [(Y, 44), (X, -6)],
        "lowerarm.l": [(X, -38)], "lowerarm.r": [(X, -38)],                                # paws resting on the legs
        "hand.l": [(X, -20)], "hand.r": [(X, -20)],
        "ear.l": [(Y, 32 - 25 * twitch)], "ear.r": [(Y, -32)],
        # tail laid on the floor and wrapped round the right side toward the front
        "tail_1": [("AIM", (-0.4, 0.75, -0.3))], "tail_2": [("AIM", (-1.0, 0.15, -0.02))], "tail_3": [("AIM", (-0.6, -0.8, 0.0))],
        "tail_4": [("AIM", (0.1, -1.0, 0.03))], "tail_5": [("AIM", (0.6, -0.8, 0.03)), (Z, 4 * breath)],
    })
    return rots, -0.05 + 0.002 * breath


ACTIONS = {   # name: (fn, frames per loop)
    "idle": (idle, 48), "walk": (walk, 20), "carry": (carry, 24), "work": (work, 24), "sneak": (sneak, 32), "sleep": (sleep, 72),
}


# ---------------------------------------------------------------- keying
def pose_quats(rig, rots):
    """Rotations are about armature axes AFTER the parent's pose ("tip the tail down, then curl it round on the
    floor" works). Walk bones parents-first: D = world delta of a bone; local q = M^-1 Dp^-1 R Dp M."""
    D, out = {}, {}
    for pb in rig.pose.bones:                       # creation order = parents before children
        b = pb.bone
        M = b.matrix_local.to_3x3().normalized()
        Dp = D[b.parent.name] if b.parent else Quaternion().to_matrix()
        R = Quaternion().to_matrix()
        for axis, deg in rots.get(pb.name, []):
            if axis == "AIM":                       # point the bone along a world direction (deg = the direction)
                cur = Dp @ (M @ Vector((0, 1, 0)))
                R = cur.rotation_difference(Vector(deg).normalized()).to_matrix() @ R
            elif axis == "MAT":                     # set the bone's whole armature-space orientation (deg = a 3x3)
                R = deg @ M.inverted() @ Dp.inverted()
            else:
                R = Quaternion(Vector(axis), math.radians(deg)).to_matrix() @ R
        D[b.name] = R @ Dp
        out[pb.name] = (M.inverted() @ Dp.inverted() @ R @ Dp @ M).to_quaternion()
    return out


def _groups(ob):
    """Body part of every vertex (from the mesh's 'grp' face attribute)."""
    import build_raccoon_blockout as RB
    grp = ob.data.attributes["grp"].data
    vg = {}
    for poly in ob.data.polygons:
        for vi in poly.vertices:
            vg.setdefault(vi, RB.GROUPS[grp[poly.index].value])
    return vg


def _lowest(ob, idx):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    z = min(me.vertices[i].co.z for i in idx) if idx else 0.0
    ev.to_mesh_clear()
    return z


def bake_action(rig, name, fn, frames, k, ob=None):
    """Key the action. With the mesh given, every keyed frame is also GROUND-LOCKED: the hips height is set so the
    lowest foot (sleep: the lowest point of the body) touches the floor exactly, and a tail that dips under the floor
    is lifted at the root just enough to clear it."""
    act = bpy.data.actions.new(name)
    rig.animation_data_create()
    rig.animation_data.action = act
    hips = rig.data.bones["hips"]
    up_local = hips.matrix_local.to_3x3().inverted() @ Vector((0, 0, 1))
    if ob is not None:
        vg = _groups(ob)
        legs = [i for i, g in vg.items() if g.startswith(("thigh_", "foot_"))]
        support = [i for i, g in vg.items() if g != "tail"] if name == "sleep" else legs
        tail = [i for i, g in vg.items() if g == "tail"]
        t1 = rig.data.bones["tail_1"]
        d = (t1.tail_local - t1.head_local).normalized()
        lift_ax = d.cross(Vector((0, 0, 1))).normalized()          # +angle tips the tail root up
    for f in range(0, frames + 1, 2):
        rots, dz = fn((f / frames) % 1.0)

        def pose(rots, z):
            qs = pose_quats(rig, rots)
            for pb in rig.pose.bones:
                pb.rotation_mode = "QUATERNION"
                pb.rotation_quaternion = qs[pb.name]
                pb.location = (0, 0, 0)
            rig.pose.bones["hips"].location = up_local * z
            bpy.context.view_layer.update()
        z = dz * k
        pose(rots, z)
        if ob is not None:
            z -= _lowest(ob, support)                               # feet (or seat) exactly on the floor
            pose(rots, z)
            if tail and _lowest(ob, tail) < -0.001:                 # lift the tail root until it clears the floor
                lo, hi = 0.0, 70.0
                for _ in range(7):
                    mid = (lo + hi) / 2
                    trial = merge(rots, {"tail_1": [(tuple(lift_ax), mid)]})
                    pose(trial, z)
                    lo, hi = (lo, mid) if _lowest(ob, tail) >= -0.001 else (mid, hi)
                rots = merge(rots, {"tail_1": [(tuple(lift_ax), hi)]})
                pose(rots, z)
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=f)
        rig.pose.bones["hips"].keyframe_insert("location", frame=f)
    act.use_frame_range = True
    act.frame_range = (0, frames)
    act.use_cyclic = True
    # push to its own NLA track so the exporter writes every action, named as is
    tr = rig.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    tr.mute = True
    rig.animation_data.action = None
    return act


def main():
    from build_raccoon_blockout import ADULT, ELDER, KIT
    sc = None
    global CANE_HAND
    want = sys.argv[1:] or ["chr_raccoon", "chr_raccoon_kit", "chr_raccoon_elder"]
    for spec in (ADULT, KIT, ELDER):
        if spec["name"] not in want:
            continue
        CANE_HAND = spec is ELDER
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / "chr_raccoon_rigged.blend"))
        sc = bpy.context.scene
        sc.render.fps = FPS
        keep = {spec["name"], spec["name"] + "_mesh"}
        for o in list(bpy.data.collections["Assets"].objects):
            if o.name not in keep:
                bpy.data.objects.remove(o)
        rig = bpy.data.objects[spec["name"]]
        rig.location = (0, 0, 0)
        k = spec["scale"] * 1.06
        for name, (fn, frames) in ACTIONS.items():
            bake_action(rig, name, fn, frames, k, bpy.data.objects[spec["name"] + "_mesh"])
        import build_raccoon_jobs as J                      # the job clips (work_chop, work_fish ...), see that file
        rep = {}
        # job clips belong to one raccoon each (build_raccoon_jobs.JOB_RIG): almost all are adult work (the buildings'
        # contact points are set for the adult's size, and a kit doesn't swing an axe); the elder teaches, kits listen
        for name in [n for n in J.JOBS if J.rig_of(n) == spec["name"]]:
            J.bake_job(rig, bpy.data.objects[spec["name"] + "_mesh"], name, k, rep)
        print("STAT", spec["name"], "job clips, worst paw miss (m):", {n: round(v, 4) for n, v in rep.items() if not isinstance(v, list)})
        suffix = spec["name"].replace("chr_raccoon", "")
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / f"chr_raccoon_animated{suffix}.blend"), relative_remap=True)
        sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
        exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})
        render_previews(rig, spec, suffix)


def render_previews(rig, spec, suffix):
    from PIL import Image, ImageDraw, ImageFont
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 12
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "Standard"
    for o in bpy.data.objects:
        if o.name.startswith("ref_") and o.type == "MESH" and o.name not in ("ref_floor", "ref_grid_lines"):
            o.hide_render = True
    cam = bpy.data.objects.new("acam", bpy.data.cameras.new("acam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    k = spec["scale"] * 1.06
    cam.data.ortho_scale = 0.62 * k
    pitch, yaw = math.radians(30), math.radians(-30)
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    cam.location = Vector((0, 0.02 * k, 0.17 * k)) + d * 5
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 360
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    out = ROOT / "renders"
    tmp = out / "_anim"
    tmp.mkdir(exist_ok=True)
    strip_rows = []
    names = list(ACTIONS) if not suffix else ["walk", "sleep"]       # variants: a quick check only
    for name in names:
        frames = ACTIONS[name][1]
        rig.animation_data.action = bpy.data.actions[name]
        step = 2 if frames <= 48 else 3
        imgs = []
        for f in range(0, frames, step):
            sc.frame_set(f)
            p = tmp / f"{name}_{f:03d}.png"
            sc.render.filepath = str(p)
            bpy.ops.render.render(write_still=True)
            imgs.append(Image.open(p).convert("RGB"))
        lab = f"chr_raccoon{suffix}  {name}  ({frames} fr loop @ {FPS} fps)"
        gif = [im.copy() for im in imgs]
        for im in gif:
            ImageDraw.Draw(im).text((10, 336), lab, font=font, fill=(240, 240, 245))
        if not suffix:
            gif[0].save(out / f"anim_{name}.gif", save_all=True, append_images=gif[1:], duration=int(1000 * step / FPS), loop=0)
        pick = [imgs[int(i * len(imgs) / 6)] for i in range(6)]
        strip_rows.append((lab, pick))
        rig.animation_data.action = None
        for p in tmp.iterdir():
            p.unlink()
    tmp.rmdir()
    W, Hh = 6 * 240, len(strip_rows) * 270
    sheet = Image.new("RGB", (W, Hh), (24, 26, 32))
    dd = ImageDraw.Draw(sheet)
    for r, (lab, pick) in enumerate(strip_rows):
        for i, im in enumerate(pick):
            sheet.paste(im.resize((240, 240), Image.LANCZOS), (240 * i, 270 * r))
        dd.text((10, 270 * r + 244), lab, font=font, fill=(235, 236, 242))
    sheet.save(out / f"anim_frames{suffix}.png")


if __name__ == "__main__":
    main()
