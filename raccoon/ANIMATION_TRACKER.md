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

## Batch 2: food and storage. Done, signed off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_farm_2x2` | ✅ rebuilt to fit 2×2 (was 3.09 m wide): fenced patch, rows of cabbages, carrots and seedlings, wheat, sunflowers, scarecrow, water barrel | ✅ wheat and sunflowers sway, scarecrow rags flap, a butterfly | ✅ a water stream from the can's spout along the seedling row, splash rings, seedlings perk up | `work_water` + `prop_watering_can` (new): lifts the can, tips it, pours with a sweep | `spot_work` | ✅ clean | ✅ |
| `bld_cave_garden_2x2` | ✅ rebuilt: dark cave floor ringed by mossy boulders, a plank planter of glowing mushrooms, a drip pool, a log with shelf mushrooms | ✅ glowing caps swell and fade, spores drift up, water drips into the pool | ✅ the young mushroom between the paws wobbles and puffs spores on each pat | `work_tend` (new): crouched, pats the soil round a mushroom | `spot_work` | ✅ clean | ✅ |
| `bld_stockpile_2x2` | ✅ refreshed: plank yard, tarp lean-to over crates, barrels and sacks, hand-cart, tally board, an open crate being packed | ✅ tarp corner flaps, lantern and rope end sway | ✅ goods settle on each shove, the lid rattles | `work_stash` (new): crouched, settles goods in the crate with both paws, rubs them clean | `spot_work` | ✅ clean | ✅ |
| `bld_cold_cellar_2x2` | ✅ rebuilt: earth mound with a grass band and a snow cap (one smooth dome), a frosted stone doorway and plank door, ice bin of fish and apples, salt-fish barrel, sled | ✅ frosty wisps from under the door, drying fish sway | ✅ the door stands open, cold mist rolls out, food settles in the bin | `work_stash` | `spot_work` | ✅ clean | ✅ |
| `bld_rubble_heap_2x2` | ✅ rebuilt: a heap of broken stone, an ore bay, a plank stack with a pick, scrap barrel, wheelbarrow | ✅ pebbles trickle down the heap and settle | ✅ stones by the paws jostle, dust puffs | `work_rummage` (from batch 1): sorts the heap | `spot_work` | ✅ clean | ✅ |

Also new in batch 2:
- **Tool:** `prop_watering_can.glb`, carried by its top handle.
- **Job clips** on `chr_raccoon` (adults only): `work_water`, `work_tend`, `work_stash`. The four batch 1 clips and the six base clips are unchanged.
- Every building is 2,000 triangles or fewer.

## Batch 3: crafting. Done, signed off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_smelter_2x2` | ✅ rebuilt: round stone furnace with a fire-mouth and chimney, bellows, ore bin, coal, ingot moulds, quench bucket | ✅ fire flickers, smoke drifts | ✅ the bellows pump with the paws, the fire flares, sparks fly up the chimney | `work_pump` (new): crouched, both paws pump the bellows handle | `spot_work` (faces the furnace, +X) | ✅ clean | ✅ |
| `bld_brewery_2x2` | ✅ rebuilt: iron cauldron of violet brew over a fire, potion shelf, herb rack, mortar table, smoke bombs, powder sacks | ✅ brew bubbles and steams, fire flickers, herbs sway | ✅ a swirl turns with the ladle, harder boil | `work_stir` + `prop_ladle` (new) | `spot_work` | ✅ clean | ✅ |
| `bld_tinker_bench_1x1` | ✅ rebuilt at raccoon size: low bench, a bar being worked, vise, gears, lamp, grindstone, tool rack | ✅ lamp flickers, grindstone turns | ✅ sparks on each tap, grindstone spins | `work_hammer` + `prop_hammer` (new): crouched, taps the bar, the left paw holds it | `spot_work` | ✅ clean | ✅ |
| `bld_fence_stall_2x2` | ✅ refit: stool pulled up to the counter, counter at paw height, coin stack and a balance scale | ✅ lantern sways, coin sign turns, scale rocks | ✅ the coins jump on each tap, the scale tips | `work_haggle` (new): on the stool, rubs paws, taps the coins, wags a claw "no" | `spot_work` (on the stool) | ✅ clean | ✅ |
| `bld_trash_bin_1x1` | ✅ rebuilt: tipped-over tin can with trash spilling out, its lid on the ground | ✅ flies buzz, the lid rocks now and then | ✅ trash jumps as the paws dig, the lid rattles | `work_rummage` (from batch 1) | `spot_work` | ✅ clean | ✅ |

Also new in batch 3:
- **Tools:** `prop_ladle.glb`, `prop_hammer.glb`.
- **Job clips** on `chr_raccoon` (adults only): `work_pump`, `work_stir`, `work_hammer`, `work_haggle`. All earlier clips are unchanged.
- **Cold cellar (batch 2):** the roof was three overlapping shells; it is now one smooth dome in bands (earth, grass, snow), and the snow drifts on the ground have softer outlines.

## Batch 4: social and care. Done, signed off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_patio_bar_2x2` | ✅ rebuilt: round plank deck, fire pit, five rug seats, keg bar, lantern strings, a board game on a crate | ✅ fire flickers, lanterns sway | ✅ the fire burns up with sparks, mugs clink | `work_drink` + `prop_mug` (new), `work_chat` (new): sitting, sipping, talking, laughing | `spot_seat_1` to `_5` | ✅ clean, five at once | ✅ |
| `bld_infirmary_2x2` | ✅ rebuilt: two cots, a healer's corner with a mortar on a stand, kettle on a brazier, jar shelf, bandage line | ✅ bandages sway, kettle steams | ✅ the kettle boils (lid rattles), medicine swirls | `work_grind` + `prop_pestle` (new); patients use `sleep` | `spot_work`, `spot_patient_1`, `_2` | ✅ clean, healer and two patients | ✅ |
| `bld_map_room_2x2` | ✅ rebuilt: low map table, candle, pin-board of charts with string, bookshelf, globe, barrel of rolled maps | ✅ candle flickers, map corner and charts flutter | ✅ a pin jiggles as plans are made | `work_read` (new): crouched over the map, tracing a route | `spot_work_1`, `_2` | ✅ clean, two readers | ✅ |
| `bld_training_nook_2x2` | ✅ rebuilt: slate on an easel with a lock and key in chalk, kit cushions, practice dummy with a purse, books, practice locks | ✅ dummy rocks, purse swings, lantern sways | ✅ the slate rattles on the elder's taps | `work_teach` (new, the elder, cane in hand); `work_listen` (new, kits) | `spot_elder`, `spot_kit_1` to `_3` | ✅ clean, elder and three kits | ✅ |
| `bld_guild_hall_3x3` | ✅ overhauled like the den: hollow timber hall on a stone footing, open door, shuttered windows, a roof the game can hide; inside: war table with a raid map, hearth, notice board, trophy shelf, loot corner, tool rack, guild banner | ✅ hearth fire, chimney smoke, banners and torches | ✅ notices flutter, candles burn up | `work_read`: a crew planning round the war table | `spot_gather_1` to `_4` | ✅ clean, a crew of four | ✅ |

Also new in batch 4:
- **Tools:** `prop_mug.glb` (held round its body), `prop_pestle.glb`.
- **Job clips:** the adult gets `work_drink`, `work_chat`, `work_grind`, `work_read`; the elder gets his first job clip, `work_teach`, and the kit gets `work_listen`. All earlier clips are unchanged.
- **QA:** buildings with several raccoons are also checked raccoon against raccoon (no tail through a neighbour).
- **Guild hall:** 4,300 triangles: the biggest model so far (3x3, a full interior and a roof).

## Batch 5: civic and watch. Done, awaiting your sign-off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_guard_post_2x2` | ✅ rebuilt: a railed watch platform on log posts with a ladder, a teal flag, a lantern on a bracket; round its foot a palisade, a spear rack, a fire basket, sling stones | ✅ flag waves, lantern sways, fire flickers | ✅ flag snaps harder, the lantern turns slowly to light the woods | `work_guard` + `prop_spear` (new): spear upright, scans the woods side to side | `spot_work` (up on the platform) | ✅ clean | ⬜ |
| `bld_alarm_bell_1x1` | ✅ rebuilt: a bronze bell in a timber frame with a shingled cap, a lever and rope, a cobbled pad | ✅ the bell sways a little, a sparrow hops on the beam | ✅ two hard hauls a loop: the bell swings over, the clapper strikes, the sparrow has flown | `work_ring` (new): both paws on the rope, hauls down with the knees | `spot_work` (faces the bell) | ✅ clean | ⬜ |
| `bld_graveyard_3x3` | ✅ rebuilt: a drystone wall and plank gate, a flagstone path to a memorial stone, headstones with carved paws, an old tree, a fresh grave with a plank marker | ✅ candles flicker, grass and the tree sway, the gate creaks, a crow hops between stones | ✅ as idle, and the seedling being planted wiggles on each pat | `work_tend` (batch 2) for the gardener; `work_mourn` (new): head bowed, paws clasped | `spot_work`, `spot_mourn_1`, `_2` | ✅ clean, gardener and two mourners | ⬜ |
| `bld_haulers_lodge_2x2` | ✅ rebuilt: a plank yard and open shed with two bunks, packs on pegs, cargo; a dray, a hoist with a winch, a spare wheel on a stand, a hanging sign | ✅ sign and lantern sway, the wheel on the stand turns | ✅ the hoist lifts a crate and lowers it, the goods in the dray settle | `work_stash` (batch 2) at the dray; haulers sleep on the bunks (`sleep`) | `spot_work`, `spot_rest_1`, `_2` | ✅ clean, loader and two sleepers | ⬜ |
| `bld_janitor_shed_2x1` | ✅ rebuilt: a plank shed with its door open (mops, brooms, rags), a broom leaning outside, a rag line, a flagstone yard with a dustpan | ✅ the broom slips, wobbles and settles; rags stir | ✅ dirt is swept into the pan, a puff of dust each stroke | `work_sweep` + `prop_brush` (new): crouched, two strokes a loop, the left paw on the pan's handle | `spot_work` | ✅ clean | ⬜ |

Also new in batch 5:
- **Tools:** `prop_spear.glb`, `prop_brush.glb` (its head angled so it lies flat on the floor).
- **Job clips** on `chr_raccoon` (adults only): `work_guard`, `work_ring`, `work_mourn`, `work_sweep`. All earlier clips are unchanged.
- **Guard post:** the guard's spot is raised, on the platform. Until there's a climbing clip, the game moves the raccoon straight onto it (see `INTEGRATION.md`).

## Batch 6: training and the kit pieces. Done, signed off

| Model | Model work | `idle` | `work` | Raccoon clip / tool | Spots | QA | Signed off |
|---|---|---|---|---|---|---|---|
| `bld_practice_yard_3x2` | ✅ rebuilt to fit: a sanded yard with a low fence, a lock board of practice padlocks, a straw dummy in a coat with a purse on its belt, straw bales, a basket of purses, a score board, bunting | ✅ bunting and the coat-tail stir, the locks rock | ✅ the picked padlock springs open and is snapped shut; the purse follows the thief's paw | `work_picklock` + `prop_lockpick` (new); `work_lift` (new): lifts the purse off and hangs it back | `spot_pick`, `spot_lift` (side-on) | ✅ clean, both at work | ✅ |
| `bld_shadow_course_2x2` | ✅ rebuilt to fit: a lap round a dark yard: a bell rope to sneak under, a balance plank on stumps, a sentry lantern, a hurdle, a cardboard weasel guard on a pivot, chalk marks, a start flag | ✅ bells and lantern sway, the weasel scans | ✅ the weasel turns its back while each runner sneaks past, the bells jingle as they pass | `work_course` (new, **travels**): a whole lap: dash, sneak under the bells, hop up and balance along the plank, hop down, sneak past the lantern, hop the hurdle, back to the flag | `spot_course` (two runners, half a lap apart) | ✅ clean, two runners | ✅ |
| `bld_sparring_ring_2x2` | ✅ rebuilt to fit: a roped ring of sand on four posts, a bench, a rack of practice sticks, a dented shield, a water bucket | ✅ the shield wobbles, the ropes sway | ✅ dust puffs at each lunge, the ropes shake | `work_spar` + `prop_stick` (new): thrust then block; both fighters play it, half a loop apart, so one thrusts while the other blocks | `spot_spar_1`, `_2` | ✅ clean, the two never touch | ✅ |
| `kit_ladder_wood` | ✅ rebuilt as a chicken ladder: a cleated plank with edge rails, up to a short deck laid across the wall top (its battens hang down both wall faces). A rung ladder can't work for a raccoon this shape: its rungs are further apart than its arms and legs reach | — still | — still | `climb_ladder_up` (new, **travels**): lean onto the plank, hop the feet up, scramble up a cleat at a time, paws gripping between the cleats and the legs tucked under (the belly is deeper than the legs are long), paws over onto the deck, vault up and stand. `climb_ladder_down`: the same backwards | `spot_ladder_up` (at the foot), `spot_ladder_down` (on the deck); both face up the plank | ✅ clean, both clips | ✅ |
| `kit_stairs_stone` | ours, unchanged | — still | — still | `climb_stairs_up` / `climb_stairs_down` (new, **travel**): a two-footed hop per step, a breath between, arms swinging back; going down it leans on and carries its tail up over the steps behind | `spot_stairs_up` (in front, facing up), `spot_stairs_down` (on top, facing down), `spot_stairs_off` (where going down ends) | ✅ clean, both clips | ✅ |

## Decorations (requested 2026-10-27)

Our own decoration models, in the batch style: an `idle` loop, plus `spot_` markers where raccoons use them. They come before batch 6, in three groups with a sign-off after each. Costs from the request are in brackets.

### Decorations D1: loot on show. Done, signed off

| Model | What it is | `idle` | Raccoons | QA | Signed off |
|---|---|---|---|---|---|
| `bld_coin_fountain_2x2` | ✅ an octagonal basin on a flagstone pad, coins round its wall and in the shallows, a coin heap at the foot of two stone bowls, a gold money bag spouting on top, flower bushes | ✅ water spouts and runs from bowl to bowl, ripples spread, coins glint | ✅ four rim seats (`spot_seat_1` to `_4`) facing the water: `work_drink` / `work_chat` | ✅ clean, four sitters | ⬜ |
| `bld_goblet_planter_1x1` | ✅ a raccoon-sized silver goblet with a gold band and set gems, full of soil, a fern and trailing ivy, on a stone plinth; coins and a spoon round it | ✅ the fronds sway, each a little behind the last | — | ✅ clean | ⬜ |
| `bld_mirror_mosaic_1x1` | ✅ an arched panel on feet, a round mirror in a sunburst of bottle glass and mirror shards, a wire edge, a bead string with a spoon; bottles and chips below | ✅ glints flash across the shards in turn, the spoon charm swings | — | ✅ clean | ⬜ |
| `bld_trophy_case_1x1` | ✅ a brass-edged glass case with a pointed lid on a turned-leg stand, a velvet cushion on a turning pedestal, a velvet rope in front; relics as child nodes: `pr_relic_caravan_bell`, `pr_relic_duke_signet` | ✅ the relic turns slowly, sparkles wink | — | ✅ clean | ⬜ |
| `bld_duke_portrait_1x1` | ✅ a heavy gilt frame on an easel: the duke, a pompous raccoon lord with his ears up through a powdered wig, a monocle, blue coat and sash, with a bandit's eyepatch and a soot moustache painted on; a side table with a candle, the soot pot and the brush | ✅ the candle flickers, leans in a draught | — | ✅ clean | ⬜ |

### Decorations D2: light and rest. Done, signed off

| Model | What it is | `idle` | Raccoons | QA | Signed off |
|---|---|---|---|---|---|
| `bld_string_lights_2x1` | ✅ two guyed posts and a sagging wire of seven mismatched stolen lanterns: tin, paper, a glow-worm jar, a ship's lamp, a teapot with a candle | ✅ the lanterns sway, each to its own beat; flames flicker | — | ✅ clean | ⬜ |
| `bld_mushroom_lamp_1x1` | ✅ a tall pale stalk on a mossy mound, a broad dark cap with a glowing band and glowing spots, little glowing caps round its foot | ✅ the glow swells and fades in turn, spores drift up | — | ✅ clean | ⬜ |
| `bld_bottlecap_banner_1x1` | ✅ two crooked sticks in stone heaps, two sagging twines of painted bottle caps, bent spoons and a tin star | ✅ the caps swing and twist in a breeze that comes and goes | — | ✅ clean | ⬜ |
| `bld_hammock_1x2` | ✅ a striped hammock on spreader bars, roped to posts on two stacked crates; a blanket over its side, tassels; a mug and a book under it | ✅ rocks gently | ✅ `spot_sleep` (the base `sleep` clip); the spot rides on the hammock, so the sleeper rocks with it | ✅ clean, with a sleeper | ⬜ |

### Decorations D3: fun. Done, signed off

| Model | What it is | `idle` | Raccoons | QA | Signed off |
|---|---|---|---|---|---|
| `bld_junk_throne_1x1` | ✅ a crate seat with a saddle strapped on, crate arms with gold knobs, a dented copper pot-lid backrest with a crown nailed on, a spoon flagpole; a red rug, coins, a goblet, a loot sack | ✅ a teal pennant flutters | ✅ `spot_seat`: the best thief feasts (`work_drink` + `prop_mug`); a gap under the backrest takes the tail | ✅ clean, with the king | ⬜ |
| `bld_dice_table_1x1` | ✅ an upturned crate under green cloth, three dice, stacks of bets, a dice cup, a candle stub; two floor cushions | ✅ a die rocks now and then, the candle flickers; in `work` a die is thrown and tumbles | ✅ `spot_seat_1`, `_2` on the diagonals, seen side-on: two players (`work_chat`) | ✅ clean, two players | ⬜ |
| `bld_kit_swing_1x1` | ✅ a timber A-frame, a rope to a ring, three ropes to a flat tyre; dandelions and a ball | ✅ the empty swing sways and turns a little | ✅ `spot_swing` rides the swing: a kit pumps on it (`work_swing`, new kit clip, in step with the swing) | ✅ clean, with a kit | ⬜ |
