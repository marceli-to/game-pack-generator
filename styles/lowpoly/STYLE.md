# styles/lowpoly/STYLE.md — the "lowpoly" style (draft)

Chunky chibi low-poly characters: flat palette colours, **flat shading** (every facet visible), big heads and
hats, few segments. Reference: Marcel's wizard turnaround (`specs/wizard/reference/turnaround.webp`, his own work).
Compared with `clean`: chibi instead of realistic-ish proportions, flat facets instead of smooth-by-angle, fewer
sides per round shape.

This file fills in the **per-style sections** of the root `STYLE.md` (same section numbers). Values marked
`→ style.json` live in `styles/lowpoly/style.json`; the shared rules (skeleton, roles, slots, topology, export,
approval) are in the root `STYLE.md` / `core.json`. Change values here first, then style.json;
`tests/test_style_sync.py` checks they agree.

---

## 1. Visual style

**In one sentence:** toy-like chibi characters built from a few big faceted shapes, one flat colour per area,
the facets themselves are the shading.

- **Proportions:** chibi, ≈ 3 heads tall: the head (plus headwear) is as big as the body; short arms and legs,
  mitten hands, chunky boots.
- **Shapes:** few, big volumes with visible facets: 6–10 sides for round things, bevels as single 45° chamfers.
- **Face:** dot eyes (tall dark ovals) and a line smile as geometry; no nose. Ears as small blocks.
- **Details:** only through geometry and colour areas: trims, bands, belts, buckles, pouches are separate shapes
  in their own colour. No texture detail, no outlines, no gradients, no baked light.
- **Mood:** friendly, cute, clean.

**Not allowed:** smooth shading, photo textures, normal maps, gradients, transparency, more than one material.

### 1a. Finished look (detail checklist)

Learnt from the knight, rogue and villager detail passes (2026-11-16/17): characters with only the big shapes right
read as work in progress next to the wizard. A finished character has:

- **Trims stand proud:** hem bands, cuffs, collars and belts are their own raised loft or sweep (1–1.5 cm out from
  the cloth, bevelled or stepped), not just a colour change on the same surface.
- **Hardware is framed:** buckles are a bevelled frame with a prong, not a solid block; guards flare at the ends;
  pommels and ferrules are separate faceted pieces.
- **Layers overlap:** a mantle over the shoulders, an apron on the skirt (ending above the hem, corners chamfered),
  a scarf over the mantle, a cuff over the sleeve: the eye reads each layer by its edge.
- **Thick, closed shapes, not sheets:** a cloth layer that can be seen edge-on (mantles, collars) is a closed loft
  ≥ 2 cm thick; a 1–2 cm shell reads as a flap or spike from the side.
- **Headwear and hair hug the head:** 1–3 cm outside the head; openings show the ears when the sheet does; hair
  overhangs the forehead ≤ 4 cm and ends in a row of pointed locks, not a straight brim.
- **Colours from the sheet:** sample the lit flat areas of the sheet and use the nearest palette cell; if none is
  close (> ~20 in any channel), change an unused cell (§4) rather than settle for a saturated neighbour.
- **Check:** close-ups of the sheet next to renders at the same scale (arms down 62°), one part at a time, front,
  side and back; then the pose test, and an in-game look by Marcel.

## 2a. Archetypes & height → style.json

| Archetype | Body height | Heads tall (approx.) |
|---|---|---|
| `chibi` (default) | 1.0–1.4 | 3 |
| `dwarf` | 0.85–1.05 | 2.5 |

Headwear may add at most 60 % of body height on top (the wizard hat: ≈ 0.35 m on a 1.2 m body).

## 3. Polygon budget → style.json

| Asset | Target | Hard limit |
|---|---|---|
| Character complete | 1,500–3,500 tris | 4,000 |
| Head incl. hair/headwear | ≤ 1,000 | 1,400 |
| Hand-held accessory (weapon, tool) | ≤ 300 | 500 |
| Back accessory (cape, backpack) | ≤ 300 | 500 |
| Prop (later) | ≤ 1,000 | 1,600 |

Raised from 2,500 / 3,000 (Marcel, 2026-11-16): the knight next to the wizard in-game read as unfinished; the detail
that makes it read finished (bevelled trims, buckle frame, slit tabard, chevron brow band, crest) costs ~4,000 tris.

**Segment & bevel guide:** the facets are the look, so keep counts low. Hats, robes, sleeves, heads: 8–10 sides;
staffs, fingers, small round things: 6; spheres/crystals: 8 × 5. Boxy shapes (boots, belts, pouches, hands):
one 45° chamfer (`P.rbox(..., seg=1)`), never a smooth round corner.

## 4. Surface: palette → style.json

Surface mode **`palette`**, as in `clean`: every face resolves its role (root STYLE.md §4) to one flat palette colour.

- **One material** `M_Palette`, base colour = `styles/lowpoly/palette.png`, roughness 1.0, metallic 0.0.
- **palette.png:** 256 × 256 px, 8 × 8 grid → 64 cells of 32 × 32 px each, closest filtering, UVs collapsed to
  cell centres. Same layout and colours as `clean`, except cell 38: a soft magenta-purple `#9A5BBA` (the wizard's robe and
  hat; lighter than `painted`'s `#8A45AC`, so the lit GLB matches the sheet) instead of a deep indigo, and cell 37: its
  dark shade `#5A3473` (inside of robes and sleeves, role `dark`) instead of a blue violet, and cell 29: an olive
  `#566539` (the rogue's tunic, from his sheet) instead of a dark green, and cell 23: a dusty rose `#BE5F68` (the
  villager's dress, from her sheet) instead of a raspberry.
- Max. **8 different colours** per character, counted as distinct palette indices actually used on faces.

## 5. Shading & normals

- **Flat shading**: every face flat-shaded, every facet visible; the GLB carries face normals, so engines light
  each facet on its own (a soft key light gives the sheet's light/dark facets). `validate` warns on smooth faces.
- Normals consistently outward; no flipped faces. No vertex colours.

## 7a. Proportion templates (values) → style.json

Templates live in `styles/lowpoly/proportions/<archetype>.json` (+ `_preview.png`).

- **`chibi` (draft):** the `painted` chibi targets (1.2 m body; head joint 0.79 m, head top 1.2 m; shoulders
  x ±0.22; arm 0.3 m; hips 0.36 m; ankles 0.095 m), checked against the wizard sheet at 2.18 mm/px (floor at
  y 920): face, beard, shoulders (±0.20 m) and boots (0.2 m wide, ≈ 0.31 m long) fit. To recalibrate on the
  wizard if the body comparison asks for it.
- **`dwarf` (draft):** from Marcel's dwarf sheet (`specs/dwarf/reference/turnaround.png`), read at the shared
  2.18 mm/px of the Phase 4 sheets: 0.95 m to the head top under the helmet, head joint 0.58 m (chin under the
  beard), shoulders x ±0.26, arm 0.24 m, hips 0.24 m (x ±0.15), ankles 0.075 m, foot bone 0.175 m ankle to toe
  (longer pitches the toe joint below the floor with this low ankle; the boot mesh itself is 0.27 × 0.39 m). Face features as big as the chibi's, head much wider (cheeks/ears ±0.29), torso
  0.58 × 0.42 m. Same clip damping as `chibi` (mitten hands). Its parts are separate from the chibi's (built
  against this template, named `-dwarf`).
- **Clip damping (`clip_damping`):** `chibi` plays `hand.l`/`hand.r` rotations at 50 % of the clip (slerp towards
  the rest pose). KayKit bends the hands 50–75° against the forearm (small hands); chibi mittens sit in wide cuffs
  and their thumbs swung back through the sleeve (Marcel, `run`).

## 11. Preview renders → style.json

As `clean`: Workbench, orthographic front/side/back + perspective ¾, 512 px per view, background `#E8E8E8`;
lit with Blender's built-in `paint.sl` studio light (the default studio light renders the flat palette much darker
and duller than the sheet and three.js; raising the exposure instead washed the colours out).
