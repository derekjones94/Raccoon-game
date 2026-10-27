# Building animation tracker

All 30 raccoon-used models from `game_models/`, worked through five at a time. Each batch gets a review and sign-off before the next one starts.

**What "done" means for a model:**
- **Model:** our style and palette, inside its footprint, looking lived in. Stand-ins get rebuilt; our early blockouts get a refresh.
- **Clips:** `idle` and `work`, each a 2–4 s loop that closes exactly.
- **Spots:** `spot_work` (or `spot_sleep_N`) markers that face the raccoon the right way.
- **Raccoon:** a job clip and tool where the job needs one.
- **QA:** a clean clipping check over every frame, with a raccoon at work in it.

How the game should use all this: `INTEGRATION.md`.

**Legend:** ✅ done · 🔁 remodel or refresh · ⬜ to do · — not needed

## Batch 1: core jobs + the axe and rod fixes. Done, signed off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_woodpile_1x1` | ✅ rebuilt: stump, 3-2-1 stack of rounds between stakes, split halves | ✅ hatchet rests in the stump | ✅ log on the stump; chips fly on every hit (frames 0 and 32) | `work_chop` + `prop_axe`: one-handed, **edge first** | `spot_work` | ✅ clean | ✅ |
| `bld_fishing_spot_1x2` | ✅ rebuilt (was a stand-in): plank deck on a stone-rimmed pond, bucket, tackle box, lantern | ✅ ripples, reeds, lily pads, a fish jumps | ✅ line and float, two bites a loop, a fish flips in the bucket | `work_fish` + `prop_fishing_rod`: seated, **facing the water** | `spot_work` (faces +X) | ✅ clean | ✅ |
| `bld_washing_pool_2x1` | ✅ rebuilt: shallow stone-rimmed pool, drying plank, washboard, laundry line | ✅ cloths stir, apple and carrot bob | ✅ ripples from the paws | `work_scrub`: wades in, crouches, rubs food in the water | `spot_work` (in the shallows) | ✅ clean | ✅ |
| `bld_rummage_camp_2x2` | ✅ rebuilt: junk heap with a cart wheel, pot and crate; lean-to, baskets, campfire | ✅ fire flickers, sack twitches, leaf flutters | ✅ junk on the heap jostles | `work_rummage`: digs at the heap from behind | `spot_work` | ✅ clean | ✅ |
| `bld_den_2x2` | ✅ (second pass done before this batch); beds remade as flat mats sized to the sleepers | ✅ chimney smoke, stove, candle and lantern flicker | ✅ someone asleep: candle out, stove low, slow smoke | `sleep` (existing) | `spot_sleep_1`, `_2` (adults), `_3` (kit) | ✅ clean, three sleepers | ✅ |

Also new in batch 1:
- **Tools:** `prop_axe.glb` and `prop_fishing_rod.glb`.
- **Job clips** on `chr_raccoon` (adults only): `work_chop`, `work_fish`, `work_scrub`, `work_rummage`.
- **Tooling:** the job-clip baker with arm IK and a check that keeps paws and forearms out of the body; the building animation and clipping-check kit (`tools/anim_kit.py`).

## Batch 2: food and storage. Done, awaiting your sign-off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_farm_2x2` | ✅ rebuilt to fit 2×2 (was 3.09 m wide): fenced patch, rows of cabbages, carrots and seedlings, wheat, sunflowers, scarecrow, water barrel | ✅ wheat and sunflowers sway, scarecrow rags flap, a butterfly | ✅ a water stream from the can's spout along the seedling row, splash rings, seedlings perk up | `work_water` + `prop_watering_can` (new): lifts the can, tips it, pours with a sweep | `spot_work` | ✅ clean | ⬜ |
| `bld_cave_garden_2x2` | ✅ rebuilt: dark cave floor ringed by mossy boulders, a plank planter of glowing mushrooms, a drip pool, a log with shelf mushrooms | ✅ glowing caps swell and fade, spores drift up, water drips into the pool | ✅ the young mushroom between the paws wobbles and puffs spores on each pat | `work_tend` (new): crouched, pats the soil round a mushroom | `spot_work` | ✅ clean | ⬜ |
| `bld_stockpile_2x2` | ✅ refreshed: plank yard, tarp lean-to over crates, barrels and sacks, hand-cart, tally board, an open crate being packed | ✅ tarp corner flaps, lantern and rope end sway | ✅ goods settle on each shove, the lid rattles | `work_stash` (new): crouched, settles goods in the crate with both paws, rubs them clean | `spot_work` | ✅ clean | ⬜ |
| `bld_cold_cellar_2x2` | ✅ rebuilt: snowy earth mound with a frosted stone doorway and plank door, ice bin of fish and apples, salt-fish barrel, sled | ✅ frosty wisps from under the door, drying fish sway | ✅ the door stands open, cold mist rolls out, food settles in the bin | `work_stash` | `spot_work` | ✅ clean | ⬜ |
| `bld_rubble_heap_2x2` | ✅ rebuilt: a heap of broken stone, an ore bay, a plank stack with a pick, scrap barrel, wheelbarrow | ✅ pebbles trickle down the heap and settle | ✅ stones by the paws jostle, dust puffs | `work_rummage` (from batch 1): sorts the heap | `spot_work` | ✅ clean | ⬜ |

Also new in batch 2:
- **Tool:** `prop_watering_can.glb`, carried by its top handle.
- **Job clips** on `chr_raccoon` (adults only): `work_water`, `work_tend`, `work_stash`. The four batch 1 clips and the six base clips are unchanged.
- Every building is 2,000 triangles or fewer.

## Batch 3: crafting

| Model | Now | Model work | `idle` | `work` | Raccoon clip / tool | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_smelter_2x2` | stand-in | 🔁 rebuild | ⬜ fire | ⬜ bellows | ⬜ | ⬜ | ⬜ |
| `bld_brewery_2x2` | stand-in | 🔁 rebuild | ⬜ bubbling pot | ⬜ ladle | ⬜ stir | ⬜ | ⬜ |
| `bld_tinker_bench_1x1` | our early blockout | 🔁 refresh | ⬜ | ⬜ grindstone, hammer | ⬜ hammer | ⬜ | ⬜ |
| `bld_fence_stall_2x2` | ours | — | ⬜ awning | ⬜ coins on the scale | ⬜ haggle | ⬜ | ⬜ |
| `bld_trash_bin_1x1` | stand-in | 🔁 rebuild | ⬜ lid rattles | ⬜ | ⬜ rummage | ⬜ | ⬜ |

## Batch 4: social and care

| Model | Now | Model work | `idle` | `work` | Raccoon clip / tool | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_patio_bar_2x2` | stand-in | 🔁 rebuild | ⬜ lantern swings | ⬜ mugs | ⬜ drink | ⬜ | ⬜ |
| `bld_infirmary_2x2` | stand-in | 🔁 rebuild | ⬜ bandages sway | ⬜ kettle steams | ⬜ patch up | ⬜ | ⬜ |
| `bld_map_room_2x2` | stand-in | 🔁 rebuild | ⬜ maps flutter | ⬜ candle | ⬜ read | ⬜ | ⬜ |
| `bld_training_nook_2x2` | stand-in | 🔁 rebuild | ⬜ dummy wobbles | ⬜ pointer | ⬜ elder teaches kits | ⬜ | ⬜ |
| `bld_guild_hall_3x3` | our early blockout | 🔁 refresh | ⬜ banner | ⬜ map board | ⬜ | ⬜ | ⬜ |

## Batch 5: civic and watch

| Model | Now | Model work | `idle` | `work` | Raccoon clip / tool | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_guard_post_2x2` | stand-in | 🔁 rebuild | ⬜ flag | ⬜ lantern turns | ⬜ keep watch | ⬜ | ⬜ |
| `bld_alarm_bell_1x1` | stand-in | 🔁 rebuild | ⬜ bell sways | ⬜ rings hard | ⬜ pull the rope | ⬜ | ⬜ |
| `bld_graveyard_3x3` | stand-in | 🔁 rebuild | ⬜ candles, grass | ⬜ | ⬜ | ⬜ | ⬜ |
| `bld_haulers_lodge_2x2` | stand-in | 🔁 rebuild | ⬜ sign swings | ⬜ cart wheel | ⬜ | ⬜ | ⬜ |
| `bld_janitor_shed_2x1` | stand-in | 🔁 rebuild | ⬜ broom tips | ⬜ | ⬜ sweep | ⬜ | ⬜ |

## Batch 6: training and the kit pieces

| Model | Now | Model work | `idle` | `work` | Raccoon clip / tool | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_practice_yard_3x2` | stand-in, **3.4 × 2.7 m and 2.3 m tall on a 3×2 lot** | 🔁 rebuild to fit | ⬜ purses swing | ⬜ lock rack jiggles | ⬜ pick locks, lift purses | ⬜ | ⬜ |
| `bld_shadow_course_2x2` | stand-in, **2.8 m wide on a 2×2 lot** | 🔁 rebuild to fit | ⬜ rope sways | ⬜ lantern dims | ⬜ creep | ⬜ | ⬜ |
| `bld_sparring_ring_2x2` | stand-in, **2.4 m wide on a 2×2 lot** | 🔁 rebuild to fit | ⬜ shield wobbles | ⬜ dust puffs | ⬜ two raccoons spar (may need more effort) | ⬜ | ⬜ |
| `kit_ladder` | ours | — | — still | — | climb (`walk` for now) | ⬜ | ⬜ |
| `kit_stairs` | ours | — | — still | — | — | ⬜ | ⬜ |
