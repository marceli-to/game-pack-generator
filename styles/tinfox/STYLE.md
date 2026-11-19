# styles/tinfox/STYLE.md — the "tinfox" style (draft)

Characters for **Tinfox**, Marcel's first-person shooter: low-poly, faceted, **flat shading**, flat saturated
palette colours, like `lowpoly`, but **not chibi**: about 5 heads tall, heroic build. Reference: the guard sheet
(`specs/guard/reference/turnaround.png`, Marcel's own work) and the other sheets in `~/Desktop/tinfox/characters/sheets/`
(handoff: `~/Desktop/tinfox/GENERATOR.md`).

This file fills in the **per-style sections** of the root `STYLE.md` (same section numbers). Values marked
`→ style.json` live in `styles/tinfox/style.json`; the shared rules (skeleton, roles, slots, topology, export,
approval) are in the root `STYLE.md` / `core.json`. Change values here first, then style.json;
`tests/test_style_sync.py` checks they agree.

---

## 1. Visual style

**In one sentence:** sturdy toy-soldier figures built from big faceted volumes, one flat colour per area, the
facets are the shading.

- **Proportions:** about 5 heads tall; head a little larger than realistic, broad shoulders with big padded
  shoulder pieces, slightly oversized hands and boots, sturdy legs.
- **Shapes:** big volumes with visible facets: 8–12 sides for limbs and heads, single 45° chamfers on boxy shapes.
- **Face:** geometry, not paint: eyes, eyebrows, mouth (and moustache, beard) as small flat pieces on the head;
  a nose as a small wedge; ears as blocks.
- **Details:** through geometry and colour areas: stripes on the shoulder pads, chest patch, belts, buckles, cap
  peaks, antennas. Small badges and emblems may be skipped.
- **Mood:** friendly but tough; readable at FPS distances.

**Not allowed:** smooth shading, photo textures, normal maps, gradients, transparency, more than one material.

## 2a. Archetypes & height → style.json

| Archetype | Body height | Heads tall (approx.) |
|---|---|---|
| `hero-m` (default) | 1.65–1.95 | 5 |
| `hero-f` | 1.55–1.85 | 5 |

`hero-m`: guard, officer, rifle guard, players 1 and 3. `hero-f`: worker, players 2 and 4 (slimmer waist, narrower
shoulders, a little shorter, same head size).
Headwear may add at most 30 % of body height on top (caps, helmets, antennas).

The game scales every figure to its gameplay height, so height differences disappear in game; characters are
still modelled at natural heights.

## 3. Polygon budget → style.json

| Asset | Target | Hard limit |
|---|---|---|
| Character complete | 3,000–7,000 tris | 8,000 |
| Head incl. hair/headwear | ≤ 2,000 | 2,600 |
| Hand-held accessory (weapon, tool) | ≤ 400 | 700 |
| Back accessory (cape, backpack) | ≤ 300 | 500 |
| Weapon (held, seen in first person) | ≤ 2,500 | 4,000 |
| Prop (pickup, crate) | ≤ 1,500 | 2,500 |

Marcel, 2026-11-17: first 3,000–4,500 / hard 5,000 (up to 4 players plus guards on screen), then raised to
hard 8,000 to try more detail: ~20 characters × 8,000 tris is ~160,000 triangles per frame, small for any current
GPU (one mesh and one material per character either way, so no extra draw calls). The facets are the look: spend
tris on silhouette and details, not on rounding everything. Weapons (props, root STYLE.md §9b) get their own,
larger budget: the player's gun is always on screen in first person, close up (2026-11-17).

**Hands:** a mitten with a separate thumb first (Marcel, 2026-11-17); fingers only if the guard reads wrong in game.

**Segment & bevel guide:** as `lowpoly`, one size up: heads, limbs, torsos 8–12 sides; small round things 6;
boxy shapes (boots, belts, pouches, gloves) one 45° chamfer (`P.rbox(..., seg=1)`).

## 4. Surface: palette → style.json

Surface mode **`palette`**: every face resolves its role (root STYLE.md §4) to one flat palette colour.

- **One material** `M_Palette`, base colour = `styles/tinfox/palette.png`, roughness 1.0, metallic 0.0.
- **palette.png:** 256 × 256 px, 8 × 8 grid → 64 cells of 32 × 32 px each, closest filtering, UVs collapsed to
  cell centres. Layout and colours of `lowpoly`, with cells taken from the Tinfox sheets (lit flat areas):
  1 skin `#F7AE7A`, 8 hair `#4A2C1B`, 19 orange `#FE7603`, 29 olive `#666B32` (guard uniform), 43 brass `#B8883A`,
  10 bright brass `#DAA645` (the officer's buttons, badge and trim, sampled off his sheet),
  52 gun grey `#565656` (weapon bodies, from the pistol sheet), 53 dark grey `#383838` (belt), 54 black `#2B2B2B` (gloves, boots), 55 near-black `#1A1A1A` (cap peak); the four
  player slot colours 33 blue `#2F5F8F`, 17 red `#8F3A2F`, 28 green `#3F7F3F`, 25 yellow `#8F7F2F`; for the
  props (sheets in `specs/<prop>/reference/`, 2026-11-17): 16 red `#D8201C` (barrel, target rings), 24 yellow
  `#FFCE0A` (hazard stripes), 42 gold `#FBB40C` (surprise box frame), 38 purple `#8A2AAE`, 37 dark purple
  `#5A1E72`, 13 cream `#F2E5C0` (target board), 35 navy `#2A3A62` (target rim); for the cover and depot kit (sheets 05–20, 2026-11-18): 30 dark olive `#4D5130` (recessed
  panels), 7 kit dark grey `#464646` (corner caps, container walls, lids), 26 khaki `#78723A` (container frame), 32 screen blue `#47C3F1` (terminal and console screens; was an unused sky blue), 57 screen highlight `#B1FAFD` (graphics on the screens; was an unused near-white). Depot rest (sheets 10, 11, 16–20): 6 cabinet grey `#A5A5A8` (storage cabinet and shelf bodies, sampled off sheet 11; was an unused mid grey). Pickups and power-ups (sheets 21–29, 2026-11-18; all seven were unused): 11 keycard red `#D33A2C` and 14 keycard blue `#3A6BD3` (the game's key colours), 34 vest steel blue `#1E5E90`, 31 shield sky blue `#0EA6F2`, 27 power-up green `#74D20C`, 15 power-up purple `#A322D2`, 36 lilac `#DDB2F7` (sampled off the sheets). Worker (sheet 04, 2026-11-18): 58 overall teal `#1B8A85` (lit flat teal off the sheet; was an unused glow cyan). Snowfort kit and practice dummy (sheets 33–39, character 09, 2026-11-18; all ten were unused): 41 snow `#EEF0F5`, 62 pine green `#4C7220`, 60 dark green `#33661A`, 61 mid green `#55891F` (bush), 40 granite `#7C7C7E`, 59 straw `#E2B930`, 0 pale wood `#F1C784` and 2 growth rings `#D9A35E` (log ends), 56 window glass `#434E59` (tower, tractor), 3 dummy sand `#E8B66C`.
- Max. **8 different colours** per character, counted as distinct palette indices actually used on faces.

## 5. Shading & normals

- **Flat shading**: every face flat-shaded, every facet visible; the GLB carries face normals. `validate` warns
  on smooth faces.
- Normals consistently outward; no flipped faces.
- **Baked ambient occlusion** (root STYLE.md §5): distance 0.3 m, power 2.0, strength 1.0, floor 0.2, 128 samples.
  Lit in the game (not unlit): the levels light the characters; the AO only darkens creases, under the cap peak,
  the neck, between arm and body. Chosen by Marcel (2026-11-17) over a baked painted texture: palette recolours keep
  working, no texture per character. Tested settings: 0.25 m / power 1 barely visible, 0.4 m / power 3 dirty.
  Props bake over **0.015 m** (`prop_distance`). On the pistol the median corner AO was 0.66 at the body distance
  0.3 m, 0.83 at 0.03 m (flat panels next to other pieces got dark gradients) and 0.95 at 0.015 m (only contact
  corners darken; the sheets show no AO). Vertex AO is sampled at vertices: a tube whose rings all sit inside other
  pieces bakes dark all over (the first barrel), so give such pieces a ring in the open.

## 7a. Proportion templates (values) → style.json

Templates live in `styles/tinfox/proportions/<archetype>.json` (+ `_preview.png`).

- **`hero-m` (draft):** read off the guard sheet with a metric grid (`workspace/lib4/grid.py`), front and side
  view, at 2.055 mm/px so the skull top under the cap is at 1.80 m (floor at y 926; the sheet has no floor line):
  head joint 1.47 m (chin), shoulders x ±0.25 (joint; read ±0.30 off the sheet, moved in under the pads so two-handed
  aiming reaches in front of the chest; the pads reach ±0.43), arm 0.53 m shoulder to wrist (0.49 read off the sheet;
  longer for the same reason), hips 0.86 m (x ±0.16: the guard stands with his legs apart, thighs centred at ≈ ±0.17, boots at ≈ ±0.22; the template legs are straight, so the boots sit 2.5 cm further out than the ankles; crotch ≈ 0.73), ankles 0.13 m, foot bone 0.26 m (the boot
  sole is ≈ 0.45 m long and 0.30 m wide, heel 0.16 m behind the ankle), head 0.30 × 0.30 m, torso 0.44 × 0.32 m
  without the pads.
- **`hero-f` (draft):** read off the worker sheet (`specs/worker/reference/turnaround.png`) with the same metric grid
  at 1.803 mm/px. Scale from the head: the worker's face is drawn the same width as the guard's (≈ 0.22 m between
  the cheeks), so the head is the same size and the body comes out shorter: skull top under the hard hat 1.70 m
  (sheet y 105, floor y 1048). Chin (head joint) 1.37 m, crotch ≈ 0.74 → hips 0.84 m (x ±0.14: thighs at ≈ ±0.14,
  boots at ≈ ±0.17), ankles 0.12 m, foot bone 0.24 m (boot sole ≈ 0.41 m long, heel 0.16 m behind the ankle),
  head 0.28 × 0.28 m, torso 0.36 × 0.30 m at the chest (waist ≈ 0.34 × 0.26). Shoulders x ±0.22 (joint, under the
  rolled sleeves; the sleeves reach ≈ ±0.32), arm 0.48 m shoulder to wrist (≈ 0.43 read off the sheet, longer for
  two-handed aiming like `hero-m`). Stride: `hero-f` re-plants `walk` for 1.6 m/s and `run` for 4.0 m/s, as `hero-m`.
- **Stride (`clip_stride`):** `hero-m` re-plants `walk` for 1.6 m/s and `run` for 4.0 m/s (Tinfox's guards walk
  1.5–1.8 m/s and run 3.8–4.0 m/s). KayKit's clips on these legs (1.95× KayKit's) came out at 1.5 m/s for `walk`, but
  the stance foot slid at 2.5 m/s after heel strike and 1.1 m/s before toe-off (moonwalking, Marcel), and at
  6.4 m/s with 2.6 m steps for `run` (a sprint, played at 0.76× in the game: big, slow steps).

## 9b. Props: weapons

Weapon sheets: `~/Desktop/tinfox/weapons/sheets/` (01 pistol … 06 ammo; side, top and front view, muzzle to the
right), names and roles in the game from its `src/data/weapons.json`.
- **Size:** at the in-game size next to the characters, not real-world: the pistol is 0.30 m long (the Kenney
  blaster the game held before measured 0.46 m × its grip scale 0.65 = 0.30 m; the guard's mitten is ~0.2 m long),
  1.2 × the length its sheet prompt gives (25 cm). Every other item uses the same factor: silenced pistol 0.49 m
  (its sheet: pistol + suppressor), SMG 0.60 m, sniper 1.32 m, ammo cell 0.14 m, SMG
  magazine 0.24 m (Kenney in hand: 0.42 / 0.59 / 1.06 m for the guns). The grenade 1.3 × that again, 0.15 m with
  the ring, ball 9 cm (Marcel: at 7 cm it looked like a marble in the mitten).
- **Look:** as the characters: big faceted volumes, 8-sided barrels and rings, single 45° chamfers, details as
  geometry (stripes, rings, ridges, sights). The bore is a dark recess, not a hole (shells stay closed).
- **Colours** (roles → cells): `primary` body 52 gun grey, `secondary` grip and details 54 black, `metal` 51 silver,
  `accent` 19 orange, `special` 39 light blue (energy window), `dark` 55 (bore).
- **Magazines:** the guns keep the sheets' silver magazines, the pickups are dark grey with an orange top and a blue
  window (as drawn). The guns' magazines use role `leather` (→ 51 silver), so one spec colour (`leather` → 52)
  gives them the pickups' grey.
- **Two-handed guns** (SMG, sniper) carry a `grip_l` anchor (front grip, fore-end); the 2H clips hold the left hand
  ~10 cm in front of the right one, so the game decides whether to solve the left hand onto it.
- **Grip:** on the handle's centre line where the mitten closes (≈ the middle of the handle); checked with the
  guard holding the gun in `aim_1h`. Around `handslot.r` in that pose the guard's mitten reaches ~13 cm back and
  ~8 cm forward, 7.5 cm down and 12 cm up (thumb), 3 cm to the inner side and 13 cm to the outer side: the handle
  sits on the palm side of the fist.

## 10. Export → style.json

`export_clips`: the GLB carries only the clips the Tin Fox game plays (`tin-wolf/src/render/modelCharacter.ts`,
`tinfoxChar`: base clips, the 1H/2H aim layers and their crouch versions):
`idle`, `walk`, `run`, `die`, `crouch`, `aim_1h`, `shoot_1h`, `aim_2h`, `shoot_2h`, `crouch_aim_1h`,
`crouch_shoot_1h`, `crouch_aim_2h`, `crouch_shoot_2h`. Left out: `jump`, `attack`, `hit`, `interact`, `crouch_walk`
(still built, so the pose test and the viewer can use them in the workspace .blend). With the static-channel pruning
(root STYLE.md §10) the guard goes from 0.99 to 0.83 MB. Add a clip here when the game starts playing it.

## 11. Preview renders → style.json

As `lowpoly`: Workbench, orthographic front/side/back + perspective ¾, 512 px per view, background `#E8E8E8`, lit
with Blender's built-in `paint.sl` studio light.
