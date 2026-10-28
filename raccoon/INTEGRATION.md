# Integration notes: building animations, work spots, tools

Notes for wiring the animated buildings and the raccoons' job clips into the game. Everything is in `raccoon/export/` and keeps the old file names, so it drops in over the old models.

- **Batch 1:** woodpile, fishing spot, washing pool, rummage camp, den.
- **Batch 2:** farm, cave garden, stockpile, cold cellar, rubble heap. The farm, cave garden, cold cellar and rubble heap replace stand-ins with new models; the stockpile replaces our early blockout.
- **Batch 3:** smelter, brewery, tinker bench, fence stall, trash bin. The smelter, brewery and trash bin replace stand-ins; the tinker bench and the fence stall were rebuilt at raccoon size (the old bench top was as tall as a raccoon, and the old counter was out of reach).
- **Batch 4:** patio bar, infirmary, map room, training nook, guild hall. All replace stand-ins; the guild hall is a full overhaul, hollow like the den, with a roof the game can hide.

`raccoon/ANIMATION_TRACKER.md` lists what is done and what is next.

## 1. Facing: put the raccoon exactly on the spot

Every animated building contains invisible marker nodes:

| Node | Where |
|---|---|
| `spot_work` | Woodpile, fishing spot, washing pool, rummage camp, farm, cave garden, stockpile, cold cellar, rubble heap, smelter, brewery, tinker bench, fence stall, trash bin, infirmary (the healer) |
| `spot_seat_1` to `_5` | Patio bar: five seats round the fire |
| `spot_patient_1`, `_2` | Infirmary: the two cots |
| `spot_work_1`, `_2` | Map room: either side of the map table |
| `spot_elder`, `spot_kit_1` to `_3` | Training nook: the elder at the slate, the kits on their cushions |
| `spot_gather_1` to `_4` | Guild hall: round the war table |
| `spot_sleep_1`, `spot_sleep_2`, `spot_sleep_3` | Den. Beds 1 and 2 are adult beds; bed 3 is the kit's bed. |

To put a raccoon to work, copy the marker's **global transform**, position and rotation, onto the raccoon's root. Add no offset, no extra turn and no `look_at`:

```gdscript
var spot := building.get_node("spot_work") as Node3D
raccoon.global_transform = spot.global_transform
```

- Our raccoon models face **+Z** in Godot, and so does every spot. Copying the transform makes the raccoon face the right way.
- **Don't** turn the raccoon toward the building's centre. That is what made the fishing rods point away from the water: the fishing spot's water is off to the side (+X), so its `spot_work` faces +X. The smelter's spot faces +X too (the raccoon pumps the bellows side-on to the furnace).
- Copy the spot's **height** too. At the fence stall the spot is on top of the Fence's stool, 0.24 m up.
- Each spot is placed so the raccoon's feet (or seat) are exactly on the surface and its paws, tool and tail clear everything. If it ends up even a few centimetres away, the axe misses the log, the fishing line won't meet the rod tip, and the tail may go into a rim.

## 2. Tools: attach with no offset

| Tool | Used at | Clip |
|---|---|---|
| `prop_axe.glb` | Woodpile | `work_chop` |
| `prop_fishing_rod.glb` | Fishing spot | `work_fish` |
| `prop_watering_can.glb` | Farm | `work_water` |
| `prop_ladle.glb` | Brewery | `work_stir` |
| `prop_hammer.glb` | Tinker bench | `work_hammer` |
| `prop_mug.glb` | Patio bar | `work_drink` |
| `prop_pestle.glb` | Infirmary | `work_grind` |
| `prop_spear.glb` | Guard post | `work_guard` |
| `prop_brush.glb` | Janitor shed | `work_sweep` |

To attach a tool:
1. Add a `BoneAttachment3D` on the raccoon's skeleton, bone **`handslot.r`**.
2. Instance the tool's `.glb` as its child with an **identity transform**: position 0, rotation 0, scale 1.

Each tool is built in the hand slot's own space:
- The origin is the grip.
- The handle runs along +Y, toward the axe head or the rod tip.
- **The axe's sharp edge points along +X.**
- **The watering can is carried by its top handle.** The handle runs along +Y toward the spout, and the can hangs below it (-Z).
- **The hammer's striking face points along +X**, like the axe's edge. The ladle's bowl is at the +Y end.
- **The mug is held round its body**, not by its handle: its open top points along +Y. A raccoon's arms are too short to hold a mug out by the handle and still reach its mouth.
- **The spear's** point is at the +Y end, its butt 0.12 m the other way. The guard holds it upright beside the right leg.
- **The brush's** head is set at 27° to its handle, so its bristles lie flat on the floor while `work_sweep` holds the handle sloping down to it.
- **The elder's cane** (`prop_cane.glb`) stays in his right paw in `work_teach`, attached the same way as always.

`work_chop` was built against exactly this frame, so the edge lands on the log first. If the game uses a different axe model, such as a KayKit one, its blade sits differently in the slot. That is why the axe struck with its blunt end. Use `prop_axe.glb`, or rotate the other axe in your scene to match it: edge along +X, handle along +Y.

Detach the tool, or hide it, when the raccoon stops working.

## 3. Which clip goes with which building

| Building | Raccoon stands at | Raccoon clip | Tool | Building clip while working |
|---|---|---|---|---|
| `bld_woodpile_1x1` | `spot_work` | `work_chop` (32 frames) | `prop_axe` | `work` (64 frames) |
| `bld_fishing_spot_1x2` | `spot_work` (faces the water) | `work_fish` (96) | `prop_fishing_rod` | `work` (96) |
| `bld_washing_pool_2x1` | `spot_work` (in the shallows) | `work_scrub` (48) | none | `work` (48) |
| `bld_rummage_camp_2x2` | `spot_work` (behind the heap) | `work_rummage` (48) | none | `work` (48) |
| `bld_den_2x2` | `spot_sleep_1` to `_3` | `sleep` (72) | none | `work` (72) = someone asleep |
| `bld_farm_2x2` | `spot_work` (behind the seedling row) | `work_water` (64) | `prop_watering_can` | `work` (64) |
| `bld_cave_garden_2x2` | `spot_work` (behind the planter) | `work_tend` (48) | none | `work` (48) |
| `bld_stockpile_2x2` | `spot_work` (behind the open crate) | `work_stash` (48) | none | `work` (48) |
| `bld_cold_cellar_2x2` | `spot_work` (behind the ice bin) | `work_stash` (48) | none | `work` (48) |
| `bld_rubble_heap_2x2` | `spot_work` (behind the heap) | `work_rummage` (48) | none | `work` (48) |
| `bld_smelter_2x2` | `spot_work` (at the bellows, faces the furnace: +X) | `work_pump` (48) | none | `work` (48) |
| `bld_brewery_2x2` | `spot_work` (behind the cauldron) | `work_stir` (48) | `prop_ladle` | `work` (48) |
| `bld_tinker_bench_1x1` | `spot_work` (at the bench) | `work_hammer` (32) | `prop_hammer` | `work` (32) |
| `bld_fence_stall_2x2` | `spot_work` (on the stool behind the counter) | `work_haggle` (48) | none | `work` (48) |
| `bld_trash_bin_1x1` | `spot_work` (behind the spill) | `work_rummage` (48) | none | `work` (48) |
| `bld_patio_bar_2x2` | `spot_seat_1` to `_5` (sitting, facing the fire) | `work_drink` (96) or `work_chat` (96) | `prop_mug` with `work_drink` | `work` (96) while anyone's there |
| `bld_infirmary_2x2` | `spot_work` (the healer) | `work_grind` (48) | `prop_pestle` | `work` (48) |
| `bld_infirmary_2x2` | `spot_patient_1`, `_2` (on the cots) | `sleep` (72, the base clip) | none | (any) |
| `bld_map_room_2x2` | `spot_work_1`, `_2` | `work_read` (48) | none | `work` (48) |
| `bld_training_nook_2x2` | `spot_elder` | `work_teach` (96), on `chr_raccoon_elder` | `prop_cane` (as always) | `work` (96) |
| `bld_training_nook_2x2` | `spot_kit_1` to `_3` | `work_listen` (96), on `chr_raccoon_kit` | none | |
| `bld_guild_hall_3x3` | `spot_gather_1` to `_4` (round the war table) | `work_read` (48) | none | `work` (96) while a crew is gathered |
| `bld_guard_post_2x2` | `spot_work` (up on the watch platform, at the front rail) | `work_guard` (96) | `prop_spear` | `work` (96) |
| `bld_alarm_bell_1x1` | `spot_work` (faces the bell, along the lot's diagonal) | `work_ring` (48) | none | `work` (48) |
| `bld_graveyard_3x3` | `spot_work` (behind the fresh grave) | `work_tend` (48) | none | `work` (96) |
| `bld_graveyard_3x3` | `spot_mourn_1`, `_2` (at the foot of a grave, facing its stone) | `work_mourn` (96) | none | |
| `bld_haulers_lodge_2x2` | `spot_work` (behind the dray) | `work_stash` (48) | none | `work` (48) |
| `bld_haulers_lodge_2x2` | `spot_rest_1`, `_2` (on the bunks) | `sleep` (72, the base clip) | none | (any) |
| `bld_janitor_shed_2x1` | `spot_work` (on the flagstones) | `work_sweep` (48) | `prop_brush` | `work` (48) |
| `bld_coin_fountain_2x2` | `spot_seat_1` to `_4` (on the rim, facing the water) | `work_drink` (96) or `work_chat` (96) | `prop_mug` with `work_drink` | `work` (48) while anyone's there |
| `bld_hammock_1x2` | `spot_sleep` (a child of `pr_hammock`) | `sleep` (72, the base clip) | none | `work` (72) while someone's asleep |

All clips are 24 fps and loop.

**Start the raccoon's clip and the building's `work` together, at the same speed.** The two loops line up:
- **Woodpile:** 64 = 2 × 32. The hatchet's edge hits the log on raccoon frame 0, which is building frames 0 and 32. The building's chips fly on those frames.
- **Fishing spot:** the float dips on building frames 29 and 69, exactly when the raccoon's ears perk up in `work_fish`.
- **Washing pool:** ripple rings start from the paws twice a loop, on the scrubbing beat.
- **Rummage camp:** the junk on the heap jostles while the paws dig.
- **Den:** the room's 72-frame loop matches the sleep loop.
- **Farm:** the water stream hangs from the can's spout. It only flows while the can is tipped (building frames 10 to 47) and slides with the raccoon's arm as it sweeps along the row. Out of sync, the water would pour from mid-air. This is the one batch 2 building where sync matters as much as at the fishing spot.
- **Cave garden:** the young mushroom between the paws wobbles, and puffs spores, on each pat.
- **Stockpile and cold cellar:** the goods on top of the crate (or ice bin) settle on each of the paws' two shoves (frames 14 and 20).
- **Rubble heap:** the stones beside the dig spot jostle on each paw's dig, and a puff of dust rises.
- **Smelter:** the bellows' top board and its handle move with the raccoon's paws, two pumps a loop, and the fire flares on each. Out of sync, the paws would float above the handle. Keep these two in step, as at the fishing spot and the farm.
- **Brewery:** the swirl in the brew turns with the ladle, two turns a loop.
- **Tinker bench:** sparks jump off the bar on the hammer's taps (frames 0 and 16).
- **Fence stall:** the stack of coins jumps when the Fence taps it (frames 17 and 22), and the scale tips.
- **Trash bin:** the banana peel and a can on the heap jump as the paws dig; the lid rattles.
- **Training nook:** the slate rattles when the elder taps it (frames 23 and 30), so start his `work_teach` with the building's `work`. The kits' `work_listen` can start whenever.
- **Infirmary:** the medicine in the mortar swirls with the pestle (two turns a loop).
- **Alarm bell:** the rope and the bell follow the haul in `work_ring` exactly: the bell swings over on each pull and the clapper strikes. Out of sync, the paws would slide up and down a still rope. Keep these two in step, as at the smelter.
- **Janitor shed:** a little drift of dirt rides ahead of the brush on each stroke and tips into the pan, with a puff of dust. Out of sync, the dirt would move by itself, so keep these in step too.
- **Graveyard:** the seedling between the gardener's paws wiggles on each pat (as at the cave garden). The mourners can start whenever.
- **Haulers' lodge:** the goods in the dray settle on the two shoves, as at the stockpile. The hoist and the wheel on its stand aren't tied to anyone.
- **Guard post:** the lantern turns slowly with the guard's scan (both 96 frames). It still looks fine if they drift apart.
- **Patio bar, map room, guild hall:** nothing in the building is tied to one raccoon. Start each raccoon's clip when it sits down or arrives. Offsetting them, and mixing `work_drink` with `work_chat` at the bar, looks livelier than everyone moving in step.

If you can't keep them in sync, the buildings still look right on their own. You just lose the hit lining up with the chips, and the bite with the ears.

## 4. Building clips

- Every animated building has exactly two glTF animations, **`idle`** and **`work`**, on the building's moving child nodes.
- Every moving part is keyed in **both** clips, including parts that hold still in one of them. Switching between `idle` and `work` at any moment therefore never leaves a part stuck mid-move.
- Some parts exist in only one clip. Those are shrunk to nothing (scale 0.001) in the other: the hatchet stuck in the stump appears only in `idle` (in `work` it is in the raccoon's paw), and the fishing line and float appear only in `work`.
- With no animation playing, a building shows the first frame of `idle`.

## 5. Building notes

- **Den:** the roof is the child node **`bld_den_2x2_roof`**. Hide it to look inside, for example when the camera is close or a raccoon is home. The chimney smoke is a child of the roof, so it hides with it. In `work` (someone asleep) the candle is out, the stove burns low and the smoke comes slower.
- **Fishing spot:** the pond is part of the building, on its +X side. The line and float belong to the building. They hang from where the adult's rod tip is in `work_fish`, which never moves, down to the water.
- **Washing pool:** the raccoon *wades*: it stands inside the pool, ankle-deep, and crouches to wash its food. That's intentional. With the raccoon's round belly and short arms, any wall between it and the water would sit in its wrists or belly.
- **Stockpile and cold cellar:** the open crate and the ice bin have a low lip on the raccoon's side, for the same reason: the paws reach over it into the goods.
- **Stockpile:** the crate's lid leans open in both clips; in `work` it rattles.
- **Cold cellar:** the door (`pr_door`) is shut in `idle` and open in `work`, so it snaps open or shut when the clip switches. If you'd rather it swing, blend the two clips over a few frames (AnimationTree crossfade), or start `work` a moment before the raccoon arrives. Frosty wisps curl from under the shut door; when it's open, cold mist rolls out along the ground.
- **Rubble heap:** the raccoon sorts the heap with the same `work_rummage` clip as at the rummage camp. So does the trash bin: the raccoon digs into the spill from a tipped-over can.
- **Fence stall:** the Fence stands on its stool behind the counter, with the counter top at paw height. Customers stand at the front of the counter. There's no customer spot yet; tell me if you want one.
- **Tinker bench:** a low bench the raccoon crouches at, sized for a 0.4 m raccoon.
- **Patio bar:** up to five raccoons at once, sitting on rugs round the fire pit (`spot_seat_1` to `_5`). Seated raccoons sit on the floor with their legs out in front, so the seats are on the ground, not on stools. Adults only for now (see section 6).
- **Infirmary:** patients sit propped up and doze on the cots with the base `sleep` clip. Each cot is sized for the whole sleeping raccoon, tail included, like the den's beds.
- **Guild hall:** the roof is the child node **`bld_guild_hall_3x3_roof`**, with a ceiling under it. Hide it to look inside, as with the den. The chimney smoke is the roof's child, so it hides with it. The walls stop at 0.52 m so the inside reads from the game camera.
- **Guard post:** the guard's spot is up on the watch platform, 0.34 m above the ground, and the raccoon reaches it by the ladder at the back. There's no climbing clip yet (the tracker lists `kit_ladder`'s climb for batch 6), so for now move the raccoon straight onto the spot, or fade it out at the ladder's foot and in at the top.
- **Alarm bell:** the frame stands across the lot's diagonal, and the ringer faces the bell along it. That way the game camera sees the ringer side-on, with the rope running in at a slant from the lever above the bell. In `idle` the rope hangs straight down; in `work` it runs to the ringer's paws. It snaps between the two when the clip switches, like the cold cellar's door.
- **Graveyard:** a gardener tends the fresh grave (`work_tend`, the cave garden's clip), and up to two mourners stand at the foot of graves with their heads bowed (`work_mourn`). About 3,900 triangles: a 3×3 lot with a wall all round.
- **Haulers' lodge:** off-shift haulers sleep on the two bunks in the shed. The loader packs the dray with `work_stash`, the stockpile's clip.
- **Janitor shed:** the dustpan is part of the building, with its handle at the janitor's left paw.

### Decorations

- **Decorations** (`bld_coin_fountain_2x2`, `bld_goblet_planter_1x1`, `bld_mirror_mosaic_1x1`, `bld_trophy_case_1x1`, `bld_duke_portrait_1x1`) have the same two clips as the buildings, `idle` and `work`, but they're identical: decorations have no work of their own. Just loop `idle`. They're checked like the buildings.
- **Coin fountain:** raccoons sit on the rim facing the water, with their toes over it and their tails hanging off the back of the rim toward the lot's corners. So keep those corners clear. It reads best outdoors.
- **Trophy case:** one child node per relic, `pr_relic_caravan_bell` and `pr_relic_duke_signet`. Both are in the file and both play the same slow turn; show the one the colony owns and hide the rest. To add a relic, ask for another node like these.
- **Duke portrait:** a still painting; only the candle moves.
- **D2 decorations** (`bld_string_lights_2x1`, `bld_mushroom_lamp_1x1`, `bld_bottlecap_banner_1x1`, `bld_hammock_1x2`) work the same way. The mushroom lamp is for the deep layers.
- **Hammock:** `spot_sleep` is a child of the rocking node `pr_hammock`, not of the building's root. **Parent the sleeping raccoon to the spot** (or play it at the spot's global transform every frame), and it rocks with the hammock. Play the hammock's `work` while someone sleeps (it rocks slower and less), `idle` when it's empty.

## 6. Who does which job

- **Adults** (`chr_raccoon`) have nineteen job clips: `work_chop`, `work_fish`, `work_scrub`, `work_rummage`, `work_water`, `work_tend`, `work_stash`, `work_pump`, `work_stir`, `work_hammer`, `work_haggle`, `work_drink`, `work_chat`, `work_grind`, `work_read`, `work_guard`, `work_ring`, `work_mourn`, `work_sweep`.
- **Kits** (`chr_raccoon_kit`) have one: `work_listen` (training nook). The work buildings' contact points (log height, water depth, heap face) are set for the adult's size, so a kit would chop and wash in mid-air, and it shouldn't swing an axe anyway.
- **The elder** (`chr_raccoon_elder`) has one: `work_teach` (training nook), leaning on his cane with his right paw and teaching with his left.

If the game gives a kit or the elder an adult job, play their generic `work` clip at the spot, or keep them off those jobs. The patio bar's drink and chat clips are adult-only for now; kits and the elder could get their own versions later.

Everything else on the characters (bones, the six base clips, `prop_cane` on the elder) is unchanged. The six base clips were compared channel by channel with the previous export and are identical.

## 7. Checked for clipping

Every building is checked over every frame of both clips:
- All of it stays inside its cells (0.03 m inset) and above the floor.
- Each loop ends exactly where it starts.
- No moving part cuts into anything.
- A raccoon at each spot, playing its job clip with its tool in its paw, cuts into nothing.

The only allowed contacts are the intended ones:
- the axe edge in the log on the hit frames;
- the rod tip at the line;
- the watering can's spout at its water stream;
- the hammer on the bar it works, the ladle in the brew;
- the brush's bristles on the janitor's flagstones;
- paws in the water, the heaps, the planter's soil, the goods in the crates, the bellows handle, the counter and its coins, the bar on the bench, the maps, the mortar, the elder's slate, the bell rope, the fresh grave's soil, the dustpan's handle;
- the wader's legs in the water.

Results are in `renders/qa_buildings.txt`. The job clips also pass the character check (`renders/qa_report.txt`): no limb into the body or head, nothing under the floor.
