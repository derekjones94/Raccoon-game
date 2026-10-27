# Integration notes: building animations, work spots, tools

Notes for wiring the animated buildings and the raccoons' job clips into the game. Batch 1: the woodpile, fishing spot, washing pool, rummage camp and den. Everything is in `raccoon/export/` and keeps the old file names, so it drops in over the old models.

`raccoon/ANIMATION_TRACKER.md` lists what is done and what is next.

## 1. Facing: put the raccoon exactly on the spot

Every animated building contains invisible marker nodes:

| Node | Where |
|---|---|
| `spot_work` | Woodpile, fishing spot, washing pool, rummage camp |
| `spot_sleep_1`, `spot_sleep_2`, `spot_sleep_3` | Den. Beds 1 and 2 are adult beds; bed 3 is the kit's bed. |

To put a raccoon to work, copy the marker's **global transform**, position and rotation, onto the raccoon's root. Add no offset, no extra turn and no `look_at`:

```gdscript
var spot := building.get_node("spot_work") as Node3D
raccoon.global_transform = spot.global_transform
```

- Our raccoon models face **+Z** in Godot, and so does every spot. Copying the transform makes the raccoon face the right way.
- **Don't** turn the raccoon toward the building's centre. That is what made the fishing rods point away from the water: the fishing spot's water is off to the side (+X), so its `spot_work` faces +X.
- Each spot is placed so the raccoon's feet (or seat) are exactly on the surface and its paws, tool and tail clear everything. If it ends up even a few centimetres away, the axe misses the log, the fishing line won't meet the rod tip, and the tail may go into a rim.

## 2. Tools: attach with no offset

| Tool | Used at | Clip |
|---|---|---|
| `prop_axe.glb` | Woodpile | `work_chop` |
| `prop_fishing_rod.glb` | Fishing spot | `work_fish` |

To attach a tool:
1. Add a `BoneAttachment3D` on the raccoon's skeleton, bone **`handslot.r`**.
2. Instance the tool's `.glb` as its child with an **identity transform**: position 0, rotation 0, scale 1.

Each tool is built in the hand slot's own space:
- The origin is the grip.
- The handle runs along +Y, toward the axe head or the rod tip.
- **The axe's sharp edge points along +X.**

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

All clips are 24 fps and loop.

**Start the raccoon's clip and the building's `work` together, at the same speed.** The two loops line up:
- **Woodpile:** 64 = 2 × 32. The hatchet's edge hits the log on raccoon frame 0, which is building frames 0 and 32. The building's chips fly on those frames.
- **Fishing spot:** the float dips on building frames 29 and 69, exactly when the raccoon's ears perk up in `work_fish`.
- **Washing pool:** ripple rings start from the paws twice a loop, on the scrubbing beat.
- **Rummage camp:** the junk on the heap jostles while the paws dig.
- **Den:** the room's 72-frame loop matches the sleep loop.

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

## 6. Who does which job

- **Adults** (`chr_raccoon`) have all four job clips.
- **Kits** (`chr_raccoon_kit`) have none. The buildings' contact points (log height, water depth, heap face) are set for the adult's size, so a kit would chop and wash in mid-air. It also shouldn't swing an axe.
- **The elder** (`chr_raccoon_elder`) has none. He keeps his cane in his right paw, and these poses would need their own versions for his hunched posture.

If the game gives a kit or the elder one of these jobs, play their generic `work` clip at the spot, or keep them off these jobs.

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
- paws in the water and in the heap;
- the wader's legs in the water.

Results are in `renders/qa_buildings.txt`. The job clips also pass the character check (`renders/qa_report.txt`): no limb into the body or head, nothing under the floor.
