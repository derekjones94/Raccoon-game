# Art checklist: mistakes we've caught, so we check for them every time

Every mistake found in review goes here as a check. Before a model or clip is shown for sign-off, go through the
list. The automatic QA (`renders/qa_buildings.txt`, `renders/qa_report.txt`) catches clipping; most of what's below
it can't, so it needs eyes on a close-up render from several sides (front, back, both ends, low side view).

## Things touching (nothing floating, nothing buried)

- [ ] **Every piece touches what holds it.** Ropes end on the post, ring or knot they tie to, not in the air near it.
  Look at where every rope and chain ends. *(Hammock: the rope fans met 9 cm in front of the posts. Alarm bell: the
  idle rope floated.)*
- [ ] **Decoration that belongs to a part moves with it and sits on its face.** When a box is offset (a crate stacked
  off-centre), its bands, slats and labels move with it. *(Hammock: the upper crates' slats floated 3 cm in front of
  them and read as ladder rungs.)*
- [ ] **Nothing important is hidden inside something else.** Posts, lashings and supports should be visible, not
  buried in a crate with stubs poking out. *(Hammock: posts and lashings were inside the crates.)*
- [ ] **Hanging things start on the edge they hang from.** Tassels, fringes, charms: their top sits on the cloth or
  wood, not just below it. *(Hammock tassels hung 1 cm under the cloth's edge.)*
- [ ] **Read rest positions before animating.** Anything placed relative to a moving part reads that part's rest
  position, not a mid-animation one. *(String lights: the flames sat where their lanterns were mid-sway.)*
- [ ] **Parent after `view_layer.update()`.** A spot or part parented to a freshly moved node takes the node's old
  transform otherwise. *(Hammock: the sleep spot sat 0.46 m too high.)*
- [ ] **Things rest on the floor, not in or above it**, including after `trim_below_floor`.

## Things reading right

- [ ] **Cloth is one piece.** A blanket, banner or tarp is one connected sheet that follows the surface it lies on
  and drapes over edges. A row of flat panels reads as random squares. *(Hammock blanket: five blue panels plus a
  loose strip.)*
- [ ] **Bright accent colours only on small details.** A big patch of a saturated swatch (`sapphire`, `ruby`)
  jumps out as a mistake; use the softer cloth swatch for large areas.
- [ ] **Roofs, lids and caps the right way up.** Check the sign of every tilt. *(Alarm bell: the roof was upside
  down.)*
- [ ] **Characters are raccoons.** Portraits and figures are raccoons (bandit masks, ears, tails), not people.
  *(Duke portrait, first version.)*
- [ ] **The working raccoon is visible from the game camera.** Frames, posts and roofs don't hide it. *(Alarm bell:
  the frame hid the ringer.)*
- [ ] **Things line up.** Repeated elements (slats, bands, rungs, cleats, battens) are evenly spaced and aligned
  across neighbouring parts.

## Surfaces

- [ ] **No z-fighting.** No two faces at the same height or in the same plane: give stacked or overlapping pieces
  distinct heights (a fraction of a millimetre is enough), use one solid ring instead of overlapping blocks. *(Black
  flicker on cobbles, wall tops, the fountain rim.)*
- [ ] **Flat decals sit just above the surface** (chalk marks 0.3 mm up), never in it.

## Raccoons and their clips

- [ ] **No clipping on any frame:** character QA (limbs into body or head under 6 mm, shoulder and hip creases up to
  12 mm) and the building QA with the raccoon in it.
- [ ] **Paws outside the shoulder line.** Targets inside it drive the elbow into the belly. Match a hanging paw's
  target to the real hanging slot.
- [ ] **Mind the proportions.** Arms reach about 0.115 m from the shoulder, legs about 0.063 m, the belly is 0.09 m
  deep. Rungs further apart than that can't be climbed; legs straight forward pass through the belly.
- [ ] **Look past the tail.** It's 0.34 m long: check it against everything behind the raccoon (steps, walls, a
  second raccoon) and against its own head when raised.
- [ ] **Check where a travelling clip starts and ends.** The body must start on its spot, not offset or floating, and
  end somewhere the next clip (`idle`, `walk`) won't clip. *(Stairs down started a metre in the air; it ended with
  the resting tail through the bottom step.)*
- [ ] **No pops at clip ends.** Anything a clip raises or tucks (tail, arms) eases back before the last frame.
- [ ] **Two raccoons at one building never touch** (offset clips, separate spots).

## Before showing it

- [ ] Automatic QA clean (`qa_buildings.txt`, and `qa_report.txt` for clips).
- [ ] Close-up renders from several sides checked against this list, not just the game-camera GIF.
- [ ] Anything new we catch in review gets added here.
