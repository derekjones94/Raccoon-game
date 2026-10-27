# Game models: what the raccoons use

The 30 models in the game that raccoons actually use: 28 buildings plus the ladder and stairs. They were exported straight from the game (`tools/export_buildings.tscn` in the game repo), so they look exactly the way the game shows them now. Most of them are still stand-ins put together from KayKit and Kenney pieces (both CC0).

Decorations (bench, candle shrine, flower pot, guild banner, haybale, lantern post, signpost, stolen painting), paths and the dragon aren't included: raccoons only look at those, or they're in this repo already.

## The job: a little life in each building

Give each model a couple of short looping animations. Keep it subtle: a bob, a sway, a flicker. Nothing should leave the model's footprint.

| Clip | When the game plays it |
|---|---|
| `idle` | Always, looping. Can be very small, or left out for a building that should sit still. |
| `work` | Looping, while a raccoon is working there (or using it: eating, sleeping, drinking). Played instead of `idle`. |

- Put both clips on the model as glTF animations named exactly `idle` and `work`.
- 2 to 4 seconds per loop is plenty. They must loop cleanly.
- Animate objects (whole parts moving, rotating, scaling). No skinning is needed for buildings.
- Export the same way as everything else (`tools/export_assets.py`), keeping the file names below so they drop straight back in.
- Keep the existing conventions: 1 m = 1 cell, origin at the bottom centre of the footprint, door/front facing +Z, the shared palette.

## The models

| File | Building | What raccoons do there | Animation ideas |
|---|---|---|---|
| `bld_guild_hall_3x3` | Guild Hall | Crews gather and set out; loot comes home | Banner sway; a map pinned to a board flutters while a crew gathers |
| `bld_den_2x2` | Den | Sleep | Smoke from a chimney; a blanket rises and falls (`work` = someone asleep) |
| `bld_stockpile_2x2` | Stockpile | Drop off and fetch goods | A tarp flaps; a crate lid lifts as goods go in |
| `bld_cold_cellar_2x2` | Cold Cellar | Store food | A frosty breath at the door; hatch opens and shuts |
| `bld_rubble_heap_2x2` | Rubble Heap | Store stone, wood, ore and scrap from digging | Pebbles trickle down the pile |
| `bld_woodpile_1x1` | Woodpile | Chop wood (Timbering) | An axe chops; chips fly |
| `bld_rummage_camp_2x2` | Rummage Camp | Rummage for berries and scraps (Rummaging) | A sack wiggles; leaves rustle |
| `bld_fishing_spot_1x2` | Fishing Spot | Fish (Dabbling) | Rod line bobs; a fish flips in a bucket |
| `bld_farm_2x2` | Farm | Plant and harvest crops (Tending) | Crops sway |
| `bld_cave_garden_2x2` | Cave Garden | Grow mushrooms (Tending) | Mushroom caps pulse faintly, like a glow |
| `bld_washing_pool_2x1` | Washing Pool | Wash scavenged food (Grubbing) | Water ripples; a scrubbing brush moves |
| `bld_smelter_2x2` | Smelter | Smelt ore into bars (Smelting) | Fire flickers; bellows pump |
| `bld_brewery_2x2` | Brewery | Brew tonics, sleep powder and smoke bombs (Brewing) | A pot bubbles; a ladle stirs |
| `bld_tinker_bench_1x1` | Tinker Bench | Make lockpicks and gear (Tinkering) | A grindstone spins; a hammer taps |
| `bld_fence_stall_2x2` | Fence Stall | Sell loot, buy goods (Haggling) | Awning sways; coins tip on a scale |
| `bld_patio_bar_2x2` | Patio Bar | Drink, chat, have fun | A lantern swings; mugs clink |
| `bld_trash_bin_1x1` | Trash Bin | Rummage through it for fun | The lid rattles and pops up |
| `bld_map_room_2x2` | Map Room | Research (Sniffing) | Maps flutter; a candle flickers |
| `bld_infirmary_2x2` | Infirmary | Heal the injured (Patching) | Bandages sway on a line; a kettle steams |
| `bld_training_nook_2x2` | Training Nook | An elder teaches kits (Mentoring) | A practice dummy wobbles; a pointer taps a board |
| `bld_guard_post_2x2` | Guard Post | Keep watch by day (Guarding) | A flag waves; a lookout lantern turns |
| `bld_alarm_bell_1x1` | Alarm Bell | Ring it when weasels come | The bell swings (`work` = ringing hard) |
| `bld_graveyard_3x3` | Graveyard | Bury the dead | Candles flicker; grass sways |
| `bld_haulers_lodge_2x2` | Haulers' Lodge | Haulers are posted here | A cart wheel turns; a sign swings |
| `bld_janitor_shed_2x1` | Janitor Shed | Janitors are posted here | A broom leaning on the wall slides and tips |
| `bld_practice_yard_3x2` | Practice Yard *(new)* | Practise picking locks and lifting purses (Latchwork, Light Paws) | Dummy purses swing on their line; the lock rack jiggles |
| `bld_shadow_course_2x2` | Shadow Course *(new)* | Creep through unseen (Shadowing, Scurrying) | A rope sways; the lantern dims and brightens |
| `bld_sparring_ring_2x2` | Sparring Ring *(new)* | Two raccoons spar (Scrapping) | A shield wobbles on its post; dust puffs up from the floor |
| `kit_ladder` | Ladder | Climb between layers | Leave still, or a gentle creak |
| `kit_stairs` | Stairs | Walk between layers | Leave still |

The three new buildings, and most of the others, are rough stand-ins. Feel free to remodel them as well as animate them, as long as the file name and footprint stay the same.
