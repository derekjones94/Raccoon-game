# Raccoon-game art

Art for the raccoon colony sim (Godot 4). Every game-ready model is in **`raccoon/export/`**, one `.glb` per asset.

- **[`raccoon/INTEGRATION.md`](raccoon/INTEGRATION.md):** how to wire up the animated buildings. It covers where raccoons stand and which way they face (`spot_` markers), how to attach tools so the axe hits with its edge and the rod points at the water, and which clip plays at which building.
- **[`raccoon/ANIMATION_TRACKER.md`](raccoon/ANIMATION_TRACKER.md):** which buildings are animated and which are still to do.

## Conventions

- 1 m = 1 Godot unit = 1 grid cell. Footprints are whole cells, inset 0.03 m.
- Origin at bottom-centre. Exported +Y up and ready to drop in with no rotation or scale.
- One shared material per model, sampling the 128×128 palette (`raccoon/textures/palette.png`, 16 px swatches). Use nearest filtering, no mipmaps.
- Two palette cells are pattern tiles rather than flat colours: `dragon_scales` (7,0) and `dragon_belly` (6,4). The dragon spreads its UVs over them to get its scales and belly plates; turning on mipmaps would blur those patterns.
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
| `prop_axe.glb`, `prop_fishing_rod.glb`, `prop_watering_can.glb`, `prop_ladle.glb`, `prop_hammer.glb`, `prop_mug.glb`, `prop_pestle.glb`, `prop_spear.glb`, `prop_brush.glb`, `prop_lockpick.glb`, `prop_stick.glb` | Work tools, built in hand-slot space. Attach to `handslot.r` with no offset (see `INTEGRATION.md`). |
| `bld_woodpile_1x1`, `bld_fishing_spot_1x2`, `bld_washing_pool_2x1`, `bld_rummage_camp_2x2` | Animated working buildings (`idle` and `work` clips, a `spot_work` marker), rebuilt in batch 1 |
| `bld_farm_2x2`, `bld_cave_garden_2x2`, `bld_stockpile_2x2`, `bld_cold_cellar_2x2`, `bld_rubble_heap_2x2` | Animated working buildings, rebuilt in batch 2 (same `idle` / `work` / `spot_work` setup) |
| `bld_smelter_2x2`, `bld_brewery_2x2`, `bld_tinker_bench_1x1`, `bld_fence_stall_2x2`, `bld_trash_bin_1x1` | Animated working buildings, batch 3 |
| `bld_patio_bar_2x2`, `bld_infirmary_2x2`, `bld_map_room_2x2`, `bld_training_nook_2x2` | Animated buildings, batch 4 (several spots each: seats, cots, the elder and kits) |
| `bld_guard_post_2x2`, `bld_alarm_bell_1x1`, `bld_graveyard_3x3`, `bld_haulers_lodge_2x2`, `bld_janitor_shed_2x1` | Animated buildings, batch 5 (the guard's spot is up on the watch platform; the graveyard has a gardener and two mourners, the lodge two bunks) |
| `bld_coin_fountain_2x2`, `bld_goblet_planter_1x1`, `bld_mirror_mosaic_1x1`, `bld_trophy_case_1x1`, `bld_duke_portrait_1x1` | Decorations, group D1: loot on show. An `idle` loop each; the fountain has four rim seats, the trophy case one child node per relic. |
| `bld_string_lights_2x1`, `bld_mushroom_lamp_1x1`, `bld_bottlecap_banner_1x1`, `bld_hammock_1x2` | Decorations, group D2: light and rest. The hammock's `spot_sleep` rocks with it. |
| `bld_junk_throne_1x1`, `bld_dice_table_1x1`, `bld_kit_swing_1x1` | Decorations, group D3: fun. A seat on the throne, two players at the dice, a kit on the swing (its spot rides the swing). |
| `bld_practice_yard_3x2`, `bld_shadow_course_2x2`, `bld_sparring_ring_2x2` | Animated buildings, batch 6 (training). The shadow course's `work_course` clip travels a whole lap (see `INTEGRATION.md`). |
| `bld_guild_hall_3x3` | Guild hall: hollow timber hall with a lived-in interior. Its roof is a child node, `bld_guild_hall_3x3_roof`: hide it to look inside, like the den's. `spot_gather_1` to `_4` round the war table. |
| `bld_den_2x2` | Raccoon family den: hollow stone hut with three beds, a stove, a table and a shelf inside, plus a doorway and three windows. Its roof is a child node, `bld_den_2x2_roof`: hide it to look inside (for example when the camera is close or a raccoon is home). It has `idle` and `work` (someone asleep) clips and `spot_sleep_1` to `_3` markers. |
| `kit_floor_stone`, `kit_wall_stone`, `kit_wall_stone_corner`, `kit_wall_stone_door`, `kit_ramp_stone`, `kit_stairs_stone`, `kit_scaffold_wood`, `kit_ladder_wood` | Tunnel kit pieces |
| `prop_barrel`, `prop_crate`, `prop_gemchest`, `prop_goldpile`, `prop_mushrooms`, `prop_torch` | Props |

## Characters

- **Skeleton.** The raccoon, kit, elder and weasel share one 30-bone skeleton, matching the KayKit `Rig_Medium` bone names. Rest pose is an A-pose. Hand slots are `handslot.l` and `handslot.r`.
- **Animations.** All four have the same six looping animations: `idle` (48 frames), `walk` (20), `carry` (24), `work` (24), `sneak` (32), `sleep` (72), all at 24 fps. Feet stay on the floor (y = 0).
- **Job clips.** The adult `chr_raccoon` also has `work_chop` (32), `work_fish` (96), `work_scrub` (48), `work_rummage` (48), `work_water` (64), `work_tend` (48), `work_stash` (48), `work_pump` (48), `work_stir` (48), `work_hammer` (32), `work_haggle` (48), `work_drink` (96), `work_chat` (96), `work_grind` (48), `work_read` (48), `work_guard` (96), `work_ring` (48), `work_mourn` (96), `work_sweep` (48), `work_picklock` (48), `work_lift` (48), `work_spar` (48) and `work_course` (264, travels a lap), made for its buildings. The elder has `work_teach` (96) and the kit `work_listen` (96) for the training nook, and the kit `work_swing` (48) for the kit swing; otherwise kits and the elder don't do these jobs (see `INTEGRATION.md`).
- **Retargeting.** Since the bones match, one AnimationLibrary works on all four, and KayKit animations can be retargeted onto them.
- **Dragon.** Its own 26-bone rig, with two animations: `idle` (a 4 s breathing loop) and `stir` (a 6 s one-shot that starts and ends on the rest pose). `breath_chest`, `breath_spine` and `breath_hips` are leaf bones that only scale for breathing; leave them alone. The hoard is a separate mesh, `chr_dragon_hoard`, inside the same file.
- **Tools.** Attach a held tool with a `BoneAttachment3D` on `handslot.r` (or `.l`), with no offset. The tool's grip is its origin and the handle runs along the slot's +Y.
- **Elder cane.** `prop_cane.glb` goes on `chr_raccoon_elder`'s `handslot.r` with no offset. It was checked against every idle and walk frame and doesn't clip.

## Other folders

- `raccoon/*.blend` – Blender sources. Most were saved from 4.5; files rebuilt since batch 1 (the den, the animated buildings, the raccoon animation files, `tools.blend`) were saved from 5.1. Blender 4.5 LTS opens 5.x files.
- `raccoon/tools/` – the Python scripts that build and export everything. Run them with the `bpy` module. `export_assets.py` writes the GLBs.
- `raccoon/renders/` – preview images and GIFs (`bld_*_loops.gif`: each building's `idle` then `work` loop), plus `qa_report.txt` (the rig and animation checks) and `qa_buildings.txt` (the building clipping checks).
- `raccoon/textures/palette.json` – swatch names and their grid positions.
