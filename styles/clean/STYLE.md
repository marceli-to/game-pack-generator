# styles/clean/STYLE.md — the "clean" style

Clean low-poly characters: flat palette colours, smooth-by-angle shading, Kenney-like but rounder. The mage
(`specs/mage`) is in this style.

This file fills in the **per-style sections** of the root `STYLE.md` (same section numbers). Values marked
`→ style.json` live in `styles/clean/style.json`; the shared rules (skeleton, roles, slots, topology, export,
approval) are in the root `STYLE.md` / `core.json`. Change values here first, then style.json;
`tests/test_style_sync.py` checks they agree.

---

## 1. Visual style

**In one sentence:** chunky, friendly low-poly characters with flat colours, a clear silhouette and no surface details. Kenney's character packs are the visual reference.

- **Proportions:** stylised, 3–4.5 heads tall. Large head, compact torso, short legs, slightly oversized hands and feet.
- **Shapes:** simple, readable volumes (boxes and cylinders with light bevels). Round where it reads round (see §5), crisp where it is a crease.
- **Silhouette:** identifiable as a black shape from the front and the side. Every character has at least one distinctive silhouette feature (headwear, weapon, cape, hairstyle).
- **Face:** minimal. Eyes as simple dark shapes (geometry or a palette cell), optional eyebrows/mouth. No nose, or a very simple one.
- **Details:** only through geometry and colour areas, never through texture detail. No outlines, no gradients, no baked shadows.
- **Mood:** friendly, slightly toy-like, nothing realistic or grim.

**Not allowed:** photo textures, normal maps, gradients, transparency (except deliberate special cases), realistic proportions, more than one material.

## 2a. Archetypes & height → style.json

Every character has an `archetype`. It sets the body height range and the proportion template (§7a). Height is always measured to the top of the head mesh (§2). Hair, headwear and accessories never count.

| Archetype | Body height | Heads tall (approx.) |
|---|---|---|
| `child` | 1.0–1.3 | 3 |
| `dwarf` | 1.2–1.45 | 3.5 (wide) |
| `human` (default) | 1.7–1.9 | 4.4 |
| `tall` (elf, giant-ish) | 1.9–2.2 | 4.5 |

Headwear may add at most 60 % of body height on top (the wizard hat is fine, a 2 m tall hat is not).

## 3. Polygon budget → style.json

| Asset | Target | Hard limit |
|---|---|---|
| Character complete | 1,500–2,500 tris | 3,000 |
| Head incl. hair/headwear | ≤ 700 | 1,000 |
| Hand-held accessory (weapon, tool) | ≤ 300 | 500 |
| Back accessory (cape, backpack) | ≤ 300 | 500 |
| Prop (later) | ≤ 1,000 | 1,600 |

Raised on 2026-11-15 from 600–1,000 (Kenney-chunky) to match the softer low-poly look of the references: still faceted and flat-shaded, but rounder. Spend the triangles on silhouette and on the face/hands, not on hidden geometry.

**Segment & bevel guide** (for part authors):
- Round, visible shapes (hats, robes, sleeves, limbs): 12–16 sides; small round things (staff, fingers): 6–8.
- Boxy shapes (head, hands, boots, belts, pouches): bevel every edge (`P.rbox`, corner radius ≈ 10–20 % of the smaller side); no sharp 90° box corners on base parts. Corners in 45° steps (`seg=1–2`) stay crisp under the §5 smoothing; 30° steps (`seg=3`) shade round (use that for heads and beards).
- Silhouette curves (hat brim droop, robe flare, beard) get extra rings rather than one straight span.

## 4. Surface: palette → style.json

Surface mode **`palette`**: every face resolves its role (root STYLE.md §4) to one flat palette colour.

- **One material** per character: `M_Palette`, Principled BSDF, base colour = `styles/clean/palette.png`, roughness 1.0, metallic 0.0 (metal is suggested by colour only).
- **palette.png:** 256 × 256 px, 8 × 8 grid → 64 cells of 32 × 32 px each. Every cell one flat colour. Texture filter: Closest (no blurring).
- **UV rule:** every face lies entirely inside one cell; UVs are collapsed to the cell centre (prevents bleeding at mip levels).
- **Palette index** = row × 8 + column (row 0 = indices 0–7, row 5 = 40–47, row 7 = 56–63).
- **Palette rows (proposal):**
  - Row 0: skin tones (6) + 2 greys
  - Row 1: hair (brown, black, blond, red, grey, white, 2 fantasy)
  - Row 2: reds/oranges
  - Row 3: yellows/greens
  - Row 4: blues/purples
  - Row 5: metal 40–44 (iron, steel, gold, bronze, copper) + leather 45–47
  - Row 6: neutrals 48–55 (48 white → 55 black)
  - Row 7: 56–63 eyes and special colours (56 eye dark, 57 eye light, 58–63 glow/crystal colours)
- Max. **8 different colours** per character (readability), counted as distinct palette indices actually used on faces. Roles defined in `spec.colors` but not used by any part do not count.

## 5. Shading & normals

- **Smooth by angle, 40°** (changed 2026-11-15 from flat shading, which read too hard): every face is smooth-shaded; edges where faces meet at more than 40° are marked sharp. Curved shapes (robe, sleeves, hat) shade round, creases and bevels (boots, belts, buckles, box corners) stay crisp. Applied at assembly; the GLB carries the split normals, so it looks the same in any engine.
- Want a curve to read round? Give it steps under 40° (≥ 10 sides for a full circle). Want an edge crisp? Make it sharper than 40° (a 45° bevel is crisp).
- Normals consistently outward; no flipped faces.
- No vertex colours (everything via the palette).

## 7a. Proportion templates (values) → style.json

Templates live in `styles/clean/proportions/<archetype>.json` (+ `_preview.png`); how they work is in root STYLE.md §7a.

- **`human` (approved by Marcel, 2026-11-15):** calibrated on the blue-wizard turnaround (`specs/mage/reference/turnaround.webp`). 1.80 m body; head 0.41 m tall (4.4 heads), 0.32 × 0.34 m; head joint at 1.39 m; shoulders at x ±0.21; shoulder-to-wrist 0.49 m; torso guide 0.38 × 0.26 m; hip joints at 0.82 m (x ±0.11) and ankles at 0.12 m (both estimated, hidden by the robe); feet 0.29 m ankle-to-toe + 0.07 m heel, 0.19 m wide, 0.14 m high.

## 11. Preview renders → style.json

- Engine: Workbench (fast) or Eevee, flat lighting, no shadows or a soft contact shadow only.
- Camera: orthographic for the turnaround sheet; perspective ¾ view for the hero render.
- Views: front, side (left), back, ¾ front-right.
- Background: neutral light grey `#E8E8E8`, transparent PNG optionally.
- Resolution: 512 × 512 per view; sheet 2048 × 512.
- Comparison sheet: reference (top) vs. render (bottom), same views.
