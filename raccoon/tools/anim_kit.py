"""Building animation kit: animated parts, the idle / work clips, raccoon work spots, and the clipping QA.

How a building with animation is put together (see build_woodpile.py etc.):
  * the building is a ROOT mesh object (the static part) named bld_<name>_<WxD>;
  * every part that moves is its own mesh object, parented to the root, with its origin at its pivot
    (part(ob, root, pivot)) -- it exports as a child node the game animates;
  * clips: animate(parts, {"idle": (frames, fn), "work": (frames, fn)}), fn(p) -> {part name: (offset, rotation,
    scale)} for the loop phase p in [0, 1). EVERY animated part gets keys in EVERY clip (a part a clip leaves alone
    is keyed at rest), so switching clips in the game never leaves a part stranded mid-move. Keys on every frame.
    Each clip ends exactly where it starts (p = 1 is p = 0).
  * spots: spot(root, "spot_work", position, facing) -- an empty the game copies onto the raccoon (position and
    rotation): the raccoon's model faces its -Y (Blender) = +Z (Godot), and so does the spot.

QA (check()): over every frame of every clip
  * footprint: every mesh stays inside the cells (0.03 m inset) and above the floor;
  * loop: each part's transform at the last frame equals the first;
  * clipping: no moving part cuts into anything else (named exceptions only);
  * raccoons at their spots playing their job clip, tool in the paw: the raccoon and the tool cut into nothing
    (named contact exceptions only, e.g. the paws in the water, the axe edge on the log on the hit frames).
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette as P  # noqa: E402

ROOT = P.ROOT
V = Vector
FPS = 24
TAU = 2 * math.pi
IN = 0.03


# ---------------------------------------------------------------- building parts + clips
def part(ob, root, pivot):
    """Make `ob` a moving part of `root`: its origin moves to `pivot` (building space), parented to the root."""
    pivot = V(pivot)
    ob.data.transform(Matrix.Translation(-pivot))
    ob.location = pivot
    ob.parent = root
    ob.rotation_mode = "QUATERNION"
    return ob


def spot(root, name, pos, facing):
    """An empty marking where a raccoon stands (or sits) to work, turned so its -Y points along `facing`."""
    e = bpy.data.objects.new(name, None)
    for c in root.users_collection:
        c.objects.link(e)
    e.empty_display_type = "SINGLE_ARROW"
    e.empty_display_size = 0.15
    f = V(facing).normalized()
    e.rotation_euler = (0, 0, math.atan2(f.x, -f.y))
    e.location = V(pos)
    e.parent = root
    return e


def animate(parts, clips):
    """Key every part in every clip. parts: {name: object}; clips: {clip: (frames, fn)}; fn(p) -> {name: (offset,
    rotation Quaternion, scale)} (any of the three may be None; a missing part stays at rest)."""
    base = {n: (o.location.copy(), o.rotation_quaternion.copy(), o.scale.copy()) for n, o in parts.items()}
    for clip, (frames, fn) in clips.items():
        acts = {}
        for n, o in parts.items():
            o.animation_data_create()
            acts[n] = bpy.data.actions.new(f"{n}|{clip}")
            o.animation_data.action = acts[n]
        for f in range(frames + 1):
            pose = fn((f / frames) % 1.0)
            for n, o in parts.items():
                loc0, rot0, sc0 = base[n]
                off, rot, sc = pose.get(n, (None, None, None))
                o.location = loc0 + (V(off) if off is not None else V())
                o.rotation_quaternion = (rot @ rot0) if rot is not None else rot0
                if sc is None:
                    o.scale = sc0
                elif isinstance(sc, (int, float)):
                    o.scale = sc0 * sc
                else:
                    o.scale = V((sc0.x * sc[0], sc0.y * sc[1], sc0.z * sc[2]))
                for path in ("location", "rotation_quaternion", "scale"):
                    o.keyframe_insert(path, frame=f)
        for n, o in parts.items():
            a = acts[n]
            a.use_frame_range = True
            a.frame_range = (0, frames)
            a.use_cyclic = True
            tr = o.animation_data.nla_tracks.new()
            tr.name = clip
            tr.strips.new(clip, 0, a)
            tr.mute = True
            o.animation_data.action = None
    for n, o in parts.items():                      # back to rest (= what the file shows with no clip playing)
        o.location, o.rotation_quaternion, o.scale = base[n]


def set_clip(objs, clip, frame):
    """Show every animated object at `frame` of `clip` (for QA and renders)."""
    for o in objs:
        ad = o.animation_data
        if ad is None:
            continue
        tr = ad.nla_tracks.get(clip)
        ad.action = tr.strips[0].action if tr else None
    bpy.context.scene.frame_set(frame)


def clip_frames(objs, clip):
    for o in objs:
        ad = o.animation_data
        if ad and ad.nla_tracks.get(clip):
            return int(ad.nla_tracks[clip].strips[0].action.frame_range[1])
    return 0


def q(axis, deg):
    return Quaternion(V(axis).normalized(), math.radians(deg))


def hidden():
    """A part that is not there in this clip: shrunk to nothing where it stands."""
    return (None, None, 0.001)


# ---------------------------------------------------------------- raccoons at spots
VARIANT_BLEND = {"chr_raccoon": "chr_raccoon_animated.blend", "chr_raccoon_kit": "chr_raccoon_animated_kit.blend",
                 "chr_raccoon_elder": "chr_raccoon_animated_elder.blend"}


def raccoon_at(spot_ob, variant="chr_raccoon", blend=None, clip="idle", tool=None, tool_blend="tools.blend"):
    """Load a raccoon from its animated file, stand it on `spot_ob`, play `clip`, tool (prop name) in handslot.r
    exactly as the game attaches it (at the hand slot's origin, no offset). Returns (rig, mesh, tool object).
    Several raccoons of one variant can be placed: each load brings fresh copies."""
    with bpy.data.libraries.load(str(ROOT / (blend or VARIANT_BLEND[variant]))) as (src, dst):
        dst.objects = [variant, variant + "_mesh"]
    rig, mesh = dst.objects
    for o in (rig, mesh):
        bpy.context.scene.collection.objects.link(o)
    rig.matrix_world = spot_ob.matrix_world.copy()
    for t in rig.animation_data.nla_tracks:
        t.mute = True
    rig.animation_data.action = next(t.strips[0].action for t in rig.animation_data.nla_tracks if t.name == clip)
    tob = None
    if tool:
        with bpy.data.libraries.load(str(ROOT / tool_blend)) as (src, dst):
            dst.objects = [tool]
        tob = dst.objects[0]
        bpy.context.scene.collection.objects.link(tob)
        bpy.context.scene.frame_set(0)
        bpy.context.view_layer.update()
        tob.parent = rig
        tob.parent_type = "BONE"
        tob.parent_bone = "handslot.r"
        tob.matrix_world = rig.matrix_world @ rig.pose.bones["handslot.r"].matrix     # at the slot's HEAD, no offset
    return rig, mesh, tob


def _visible_filter(mesh, paws):
    """A function keeping only the overlap pairs whose raccoon face is NOT buried inside the paw (evaluated now)."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    me = ev.to_mesh()
    mw = mesh.matrix_world
    co = [mw @ v.co for v in me.vertices]
    keep = [p.index for p in me.polygons if p.index not in paws]
    centers = [sum((co[i] for i in me.polygons[k].vertices), V()) / len(me.polygons[k].vertices) for k in keep]
    paw_tree = BVHTree.FromPolygons(co, [list(me.polygons[i].vertices) for i in paws])
    ev.to_mesh_clear()
    d = V((0.3, 0.2, 0.93)).normalized()

    def buried(a):
        n, o = 0, centers[a].copy()
        for _ in range(20):
            h = paw_tree.ray_cast(o, d)
            if h[0] is None:
                break
            n += 1
            o = h[0] + d * 1e-6
        return n % 2 == 1
    return lambda pairs: [pr for pr in pairs if not buried(pr[0])]


def raccoon_paws(mesh):
    """Polygons of a raccoon mesh that are paw / wrist (dominant weight): the only parts allowed to touch things."""
    names = {i: g.name for i, g in enumerate(mesh.vertex_groups)}
    paw = set()
    for v in mesh.data.vertices:
        if v.groups and names[max(v.groups, key=lambda e: e.weight).group].startswith(("hand.", "wrist.")):
            paw.add(v.index)
    return {p.index for p in mesh.data.polygons if any(i in paw for i in p.vertices)}


# ---------------------------------------------------------------- QA
def bvh(o, keep=None, skip=None):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    mw = o.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    polys = [list(p.vertices) for p in me.polygons
             if (keep is None or p.index in keep) and (skip is None or p.index not in skip)]
    ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys), verts


def check(root, W, D, H=None, crew=(), allow=(), sky=(), step=1):
    """QA for a building. crew: [(rig, mesh, tool, clip_of_building, contacts)] -- raccoons placed by raccoon_at,
    checked while the building plays clip_of_building; contacts: {object name: frames or None} that the PAWS
    (or for the tool: the tool) may touch, e.g. {"pr_line": None} or {"pr_log": (0, 1, 2)}; "wade" = water the
    raccoon stands in (any part of it may be in it). allow: pairs of building
    object names that may touch. sky: objects allowed above the height limit (smoke). With several raccoons, they are
    also checked against each other (no tail through a neighbour). Returns a list of problems."""
    crew_obs = {id(o) for c in crew for o in c[:3] if o}               # raccoons parented into the building (a sleeper
    objs = [root] + [o for o in root.children_recursive               # riding a hammock) aren't building parts
                     if o.type == "MESH" and id(o) not in crew_obs]
    movers = [o for o in objs if o.animation_data and o.animation_data.nla_tracks]
    clips = sorted({t.name for o in movers for t in o.animation_data.nla_tracks})
    allow = {frozenset(p) for p in allow}
    probs = []
    root_inv = root.matrix_world.inverted()
    paws = {id(c[1]): raccoon_paws(c[1]) for c in crew}
    for clip in clips:
        n = clip_frames(movers, clip)
        rest = {}
        for f in range(0, n + 1, step):
            # the raccoons first, each on its own clip frame (their loops divide the building's), then the building
            crew_trees = []
            for rig, mesh, tool, bclip, contacts in crew:
                if bclip != clip:
                    continue
                rf = int(rig.animation_data.action.frame_range[1])
                bpy.context.scene.frame_set(f % rf)
                crew_trees.append((bvh(mesh, skip=paws[id(mesh)])[0], bvh(mesh, keep=paws[id(mesh)])[0],
                                   bvh(tool)[0] if tool else None, tool, contacts, f % rf, mesh,
                                   _visible_filter(mesh, paws[id(mesh)])))
            set_clip(movers, clip, f)
            trees = {o.name: bvh(o) for o in objs}
            for o in objs:                                          # footprint
                if o.name in sky:
                    continue
                for v in trees[o.name][1]:
                    p = root_inv @ v
                    if abs(p.x) > W / 2 - IN + 1e-3 or abs(p.y) > D / 2 - IN + 1e-3 or p.z < -1e-3 or (H and p.z > H + 1e-3):
                        probs.append((clip, f, "outside footprint", o.name, tuple(round(c, 3) for c in p)))
                        break
            for m in movers:                                        # moving parts vs everything else
                for o in objs:
                    if o is m or frozenset((m.name, o.name)) in allow:
                        continue
                    if trees[m.name][0].overlap(trees[o.name][0]):
                        probs.append((clip, f, "parts cut into each other", m.name, o.name))
            if f == 0:
                rest = {m.name: m.matrix_world.copy() for m in movers}
            if f == n:
                for m in movers:
                    d = max(abs(a - b) for ra, rb in zip(rest[m.name], m.matrix_world) for a, b in zip(ra, rb))
                    if d > 1e-4:
                        probs.append((clip, f, "loop does not close", m.name, round(d, 5)))
            for i, a in enumerate(crew_trees):                       # raccoons against each other
                for b in crew_trees[i + 1:]:
                    if a[0].overlap(b[0]) or a[1].overlap(b[1]) or a[0].overlap(b[1]) or a[1].overlap(b[0]):
                        probs.append((clip, f, "raccoons touch each other", a[6].name, b[6].name))
            for rt_body, rt_paw, tt, tool, contacts, rf, mesh, vis in crew_trees:   # raccoons at work
                for o in objs:
                    ok = contacts.get(o.name, "no")
                    if ok == "wade":                                # water the raccoon stands in: any part may
                        continue
                    hit_ok = ok is None or (ok != "no" and rf in ok)
                    if vis(rt_body.overlap(trees[o.name][0])):
                        probs.append((clip, f, "raccoon body cuts into", o.name))
                    if rt_paw.overlap(trees[o.name][0]) and not hit_ok:
                        probs.append((clip, f, "raccoon paw cuts into", o.name))
                    if tt and tt.overlap(trees[o.name][0]) and not hit_ok:
                        probs.append((clip, f, f"{tool.name} cuts into", o.name))
                if tt and vis([(b, a) for a, b in tt.overlap(rt_body)]):
                    probs.append((clip, f, f"{tool.name} cuts into its raccoon", ""))
    set_clip(movers, "idle" if "idle" in clips else (clips[0] if clips else ""), 0)
    return probs


# ---------------------------------------------------------------- export + GIF
def save_gif(imgs, path, ms):
    """GIF with one shared palette, no dithering, light median filter (render noise otherwise bloats GIFs)."""
    from PIL import Image, ImageFilter
    imgs = [im.filter(ImageFilter.MedianFilter(3)) for im in imgs]
    strip = Image.new("RGB", (imgs[0].width, imgs[0].height * 4))
    for i, k in enumerate((0, len(imgs) // 3, 2 * len(imgs) // 3, len(imgs) - 1)):
        strip.paste(imgs[k], (0, imgs[0].height * i))
    pal = strip.quantize(128, method=Image.Quantize.MEDIANCUT)
    qs = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
    qs[0].save(path, save_all=True, append_images=qs[1:], duration=ms, loop=0, optimize=True)


def export(root_name=None):
    sys.argv = [sys.argv[0], "--", str(ROOT / "export")]
    exec(compile((ROOT / "tools" / "export_assets.py").read_text(), "export_assets.py", "exec"), {"__name__": "__main__"})


# ---------------------------------------------------------------- scaffolding shared by the building scripts
def open_template():
    """Fresh scene from template.blend (palette reloaded, reference raccoons / cells removed); returns Assets."""
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "template.blend"))
    bpy.context.scene.render.fps = FPS
    bpy.data.materials["M_Palette"].node_tree.nodes["Image Texture"].image.reload()
    ref = bpy.data.collections["Reference"]
    for o in list(ref.objects):
        if o.name.startswith(("ref_raccoon", "ref_doorway", "ref_cell", "ref_floor", "ref_grid")):
            bpy.data.objects.remove(o)
    return bpy.data.collections["Assets"]


def rest_at(parts, clip="idle", frame=0):
    """Make the parts' static transform (what the file shows with no clip playing) the given clip frame."""
    objs = list(parts.values())
    set_clip(objs, clip, frame)
    bpy.context.view_layer.update()
    snap = {o: (o.location.copy(), o.rotation_quaternion.copy(), o.scale.copy()) for o in objs}
    for o in objs:
        o.animation_data.action = None
    for o, (l, r, s) in snap.items():
        o.location, o.rotation_quaternion, o.scale = l, r, s


def report(name, probs, path):
    """Print + append the QA result to renders/qa_buildings.txt (one block per building, replaced on re-run)."""
    lines = [f"== {name}: " + ("CLEAN (footprint, loops, part clipping, raccoons at their spots)" if not probs
                               else f"{len(probs)} problem(s)")]
    seen = set()
    for p in probs:
        key = p[2:]
        if key in seen:
            continue
        seen.add(key)
        frames = sorted({q[1] for q in probs if q[2:] == key})
        lines.append(f"   {p[0]} frames {frames[0]}-{frames[-1]} ({len(frames)}): {' '.join(str(x) for x in key)}")
    txt = "\n".join(lines)
    print(txt)
    old = path.read_text() if path.exists() else ""
    blocks = [b.strip("\n") for b in old.split("\n\n") if b.strip() and not b.strip("\n").startswith(f"== {name}:")]
    path.write_text("\n\n".join(blocks + [txt]) + "\n")


def render_loops(root, crew_objs, out_gif, target, dist, pitch=48, yaw=-30, res=(640, 480), step=2,
                 idle_frames=None, work_repeat=1, label=None, samples=14, grid_n=5, hide_in_work=(), idle_only=False):
    """The building's idle loop (no raccoon) then its work loop (raccoons shown), from the game camera, as a GIF.
    crew_objs: objects to show only in the work part (rigs, meshes, tools)."""
    from PIL import Image, ImageDraw, ImageFont
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "Standard"
    gc = bpy.data.objects["GameCam"]
    import build_kit_blockout as K
    import build_template
    if not bpy.data.objects.get("ref_floor"):                # floor + cell grid: odd n = lines on cell edges for
        build_template.grid(bpy.data.collections["Reference"], n=grid_n)    # odd-sized lots, even n for even ones
    K.look(gc, target, yaw, dist, pitch_deg=pitch)
    sc.camera = gc
    sc.render.resolution_x, sc.render.resolution_y = res
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    objs = [root] + [o for o in root.children_recursive if o.type == "MESH"]
    movers = [o for o in objs if o.animation_data and o.animation_data.nla_tracks]
    tmp = ROOT / "renders" / "_loop.png"
    imgs = []
    loops = (("idle", False, 1),) if idle_only else (("idle", False, 1), ("work", True, work_repeat))
    for clip, show_crew, reps in loops:                 # idle_only: decorations, whose work is their idle
        n = clip_frames(movers, clip) or 48
        n_show = idle_frames if (clip == "idle" and idle_frames) else n
        for o in crew_objs:
            o.hide_render = not show_crew
        for o in hide_in_work:                          # e.g. the den's roof, so the sleepers can be seen
            o.hide_render = show_crew
        for r in range(reps):
            for f in range(0, n_show, step):
                set_clip(movers, clip, f)
                if show_crew:
                    _pose_crew_frames(crew_objs, f)
                sc.render.filepath = str(tmp)
                bpy.ops.render.render(write_still=True)
                im = Image.open(tmp).convert("RGB")
                ImageDraw.Draw(im).text((10, res[1] - 24), f"{label or root.name}  {clip}  {f}/{n}", font=font,
                                        fill=(240, 240, 245))
                imgs.append(im)
    tmp.unlink()
    for o in list(crew_objs) + list(hide_in_work):
        o.hide_render = False
    save_gif(imgs, out_gif, int(1000 * step / FPS))
    return imgs


def _pose_crew_frames(crew_objs, f):
    """Raccoons play their own (shorter) loops: offset each rig's action so it shows frame f mod its length at
    scene frame f, via an NLA-free trick -- a Cycles modifier on every f-curve, added once."""
    for o in crew_objs:
        if o.type != "ARMATURE" or o.get("_cyc"):
            continue
        for fc in _fcurves(o.animation_data.action):
            if not any(m.type == "CYCLES" for m in fc.modifiers):
                fc.modifiers.new("CYCLES")
        o["_cyc"] = True
    bpy.context.scene.frame_set(f)


def offset_clip(rig, frames):
    """Play this raccoon's clip `frames` ahead of the others (two runners half a lap apart): its action is copied,
    keyed `frames` earlier and made cyclic, so scene frame f shows clip frame f + frames (QA and renders alike)."""
    act = rig.animation_data.action.copy()
    rig.animation_data.action = act
    for fc in _fcurves(act):
        for kp in fc.keyframe_points:
            kp.co.x -= frames
            kp.handle_left.x -= frames
            kp.handle_right.x -= frames
        if not any(m.type == "CYCLES" for m in fc.modifiers):
            fc.modifiers.new("CYCLES")
    rig["_cyc"] = True


def _fcurves(act):
    """F-curves of an action (Blender 5 keeps them in the action's layers / strips / channel bags)."""
    try:
        return list(act.fcurves)
    except AttributeError:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out.extend(cb.fcurves)
        return out
