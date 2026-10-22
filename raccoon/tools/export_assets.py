"""Export every top-level object in the 'Assets' collection as its own .glb (children ride along).

  * the 'Reference' collection is never exported
  * each asset is exported at the origin (its own location is restored afterwards), +Y up for Godot
  * names must follow bld_<name>_<WxD> / kit_<name> / prop_<name> / chr_<name>; others are skipped with a warning
  * transforms must be applied (scale 1, rotation 0) or the asset is skipped

Run inside Blender (Scripting tab -> this text -> Run), or:
  blender -b file.blend --python export_assets.py -- <out_dir>
Default out dir: <blend folder>/export/
"""
import re
import sys
from pathlib import Path

import bpy

NAME_RE = re.compile(r"^(bld_[a-z0-9]+(_[a-z0-9]+)*_\d+x\d+|kit_[a-z0-9_]+|prop_[a-z0-9_]+|chr_[a-z0-9_]+)$")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(argv[0]) if argv else Path(bpy.path.abspath("//export"))
    out.mkdir(parents=True, exist_ok=True)
    assets = bpy.data.collections.get("Assets")
    if not assets:
        print("no 'Assets' collection")
        return
    roots = [o for o in assets.all_objects if o.parent is None]
    done = []
    for ob in roots:
        if not NAME_RE.match(ob.name):
            print(f"SKIP {ob.name}: name doesn't follow bld_/kit_/prop_/chr_ convention")
            continue
        if any(abs(v - 1) > 1e-4 for v in ob.scale) or any(abs(v) > 1e-4 for v in ob.rotation_euler):
            print(f"SKIP {ob.name}: apply rotation & scale first")
            continue
        loc = ob.location.copy()
        ob.location = (0, 0, 0)
        bpy.ops.object.select_all(action="DESELECT")
        for o in [ob] + list(ob.children_recursive):
            o.hide_set(False)
            o.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.gltf(filepath=str(out / f"{ob.name}.glb"), export_format="GLB", use_selection=True,
                                  export_yup=True, export_apply=True,
                                  export_animations=ob.name.startswith("chr_"))
        ob.location = loc
        done.append(ob.name)
    print(f"exported {len(done)} asset(s) to {out}: {', '.join(done)}")


main()
