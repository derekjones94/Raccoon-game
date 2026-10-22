# Raccoon-game art

Art for the raccoon colony sim (Godot 4). Every game-ready model is in **`raccoon/export/`**, one `.glb` per asset.

## Conventions

- 1 m = 1 Godot unit = 1 grid cell. Footprints are whole cells, inset 0.03 m.
- Origin at bottom-centre. Exported +Y up and ready to drop in with no rotation or scale.
- One shared material per model, sampling the 128×128 palette (`raccoon/textures/palette.png`, 16 px swatches). Use nearest filtering, no mipmaps.
- Names: `bld_<name>_<W>x<D>` buildings, `kit_` 1-cell building pieces, `prop_` props, `chr_` characters.
- Walls sit on the edge of their cell.

## Assets

| File | What it is |
|---|---|
| `chr_raccoon.glb` | Adult raccoon, about 0.40 m tall |
| `chr_raccoon_kit.glb` | Young raccoon, about 0.25 m |
| `chr_raccoon_elder.glb` | Elder raccoon, about 0.37 m, hunched |
| `chr_weasel.glb` | Weasel rival, about 0.43 m |
| `chr_dragon.glb` | Sleeping dragon on its hoard, about 6×4 cells |
| `prop_cane.glb` | The elder's cane, attached to the hand slot |
| `bld_den_2x2`, `bld_stockpile_2x2`, `bld_rummage_camp_2x2`, `bld_fence_stall_2x2`, `bld_washing_pool_2x1`, `bld_woodpile_1x1`, `bld_tinker_bench_1x1`, `bld_guild_hall_3x3` | Buildings |
| `kit_floor_stone`, `kit_wall_stone`, `kit_wall_stone_corner`, `kit_wall_stone_door`, `kit_ramp_stone`, `kit_stairs_stone`, `kit_scaffold_wood`, `kit_ladder_wood` | Tunnel kit pieces |
| `prop_barrel`, `prop_crate`, `prop_gemchest`, `prop_goldpile`, `prop_mushrooms`, `prop_torch` | Props |

## Characters

- **Skeleton.** The raccoon, kit, elder and weasel share one 30-bone skeleton, matching the KayKit `Rig_Medium` bone names. Rest pose is an A-pose. Hand slots are `handslot.l` and `handslot.r`.
- **Animations.** All four have the same six looping animations: `idle` (48 frames), `walk` (20), `carry` (24), `work` (24), `sneak` (32), `sleep` (72), all at 24 fps. Feet stay on the floor (y = 0).
- **Retargeting.** Since the bones match, one AnimationLibrary works on all four, and KayKit animations can be retargeted onto them.
- **Dragon.** Its own 23-bone rig, with two animations: `idle` (breathing) and `stir`.
- **Tools.** Attach a held tool with a `BoneAttachment3D` on `handslot.r` (or `.l`), with no offset. The tool's grip is its origin and the handle runs along the slot's +Y.
- **Elder cane.** `prop_cane.glb` goes on `chr_raccoon_elder`'s `handslot.r` with no offset. It was checked against every idle and walk frame and doesn't clip.

## Other folders

- `raccoon/*.blend` – Blender 4.5 sources.
- `raccoon/tools/` – the Python scripts that build and export everything. Run them with the `bpy` module. `export_assets.py` writes the GLBs.
- `raccoon/renders/` – preview images and GIFs, plus `qa_report.txt` (the rig and animation checks).
- `raccoon/textures/palette.json` – swatch names and their grid positions.
