# styles/painted/STYLE.md — the "painted" style (draft)

Hand-painted chibi characters: chunky shapes, a baked base-colour texture with light, shade, edge wear and
grime, smooth-by-angle shading. Reference: the skeleton-knight turnaround (`specs/knight/reference/turnaround.png`, Marcel's own work).

**Status: draft.** Surface approach decided (§4: `auto`, `projection` optional); the remaining values are drafts. Same section numbers as
the root `STYLE.md`; values marked `→ style.json` live in `styles/painted/style.json`.

---

## 1. Visual style

**In one sentence:** stocky, toy-like chibi characters with oversized heads, hands and feet, painted like
stylised mobile-game art: soft top light, darker undersides, worn and chipped edges, a few hand-painted cracks.

- **Proportions:** about 3 skull-heights tall (≈ 2.5 with a helmet). Very short arms and legs, big hands and boots.
- **Shapes:** chunky, bevelled, slightly irregular (dented plates, torn cloth). Silhouette first.
- **Surface detail:** painted, not modelled: highlights on top edges, shade in creases, scratches and rust on
  metal, cracks, torn and darkened cloth hems. No photo textures, no normal maps.
- **Face:** strong, graphic (glowing eyes, big teeth); allowed to break the no-emissive rule via the `special` role.

**Not allowed:** photo textures, normal/roughness maps, realistic proportions, more than one material.

## 2a. Archetypes & height → style.json

| Archetype | Body height | Heads tall (approx.) |
|---|---|---|
| `chibi` (default) | 1.0–1.4 | 3 |

Headwear may add at most 60 % of body height on top.

## 3. Polygon budget → style.json

| Asset | Target | Hard limit |
|---|---|---|
| Character complete | 4,000–6,000 tris | 8,000 |
| Head incl. hair/headwear | ≤ 3,000 | 3,500 |
| Hand-held accessory (weapon, tool) | ≤ 600 | 900 |
| Back accessory (cape, backpack) | ≤ 600 | 900 |
| Prop (later) | ≤ 2,000 | 3,000 |

More than `clean`: painted characters carry dents, rivets, rims and torn edges in geometry.
The head got the most room (raised by Marcel, 2026-11-15, from ≤ 1,800 / 2,500): bevelled bands, rivets, a sculpted
face and damage carry the look, and the chibi body is small and simple. Tris matter for skinning many characters
at once, not for file size (the texture is ~85 % of a painted GLB).

## 4. Surface: painted (draft) → style.json

Surface mode **`painted`**: roles (root STYLE.md §4) still drive colour, but each role resolves to a *base
colour* (palette cell, `styles/painted/palette.png`, mid-tones) plus a *treatment*; the result is baked into one
texture per character.

- **One material** `M_Painted`, base colour = the character's baked texture (`texture_size` 1024², UVs per
  character, `uv_margin_px` padding), roughness 1.0, metallic 0.0.
- **Default: `auto`** (decided by Marcel, 2026-11-15, after the knight spike): procedural paint from the mesh.
  Works for any combination of parts, deterministic per seed. Per texel:
  - a signed **light value** (shadow −1 … +1 light): key light from top-front-left (wrapped), a top-to-bottom
    gradient **per connected piece** (every band, plate and dome is lit at the top, dark at the bottom),
    ambient occlusion; plus **brush dabs** (one random value per small Voronoi cell, ≈ 4–5 cm) and soft
    **value bands** with noisy borders, so the light reads as painted strokes, not an airbrush;
  - a **hue-shifted ramp** per role (`ramp`): shadows darken, saturate and turn towards red/purple, lights
    brighten and turn towards yellow (the art's gold: red-brown → orange → yellow; metal: deep plum → mauve →
    pink); roles may override the ramp;
  - role treatments on top: mottle, **rim light** on convex edges that face the light and rim shadow on the
    others, dirt in concave creases, **rust** creeping in from edges, creases and the lower part of each piece,
    scratches, a few long **cracks** with a lit lip, and **glow** on `special` (bright core) with a halo that
    spills onto nearby surfaces (eye sockets).
  Tuned on the knight against the sheet: per-material value range and mid/dark/light colours (metal, gold,
  bone) are close to the art's.
- **Optional: `projection`**, only for one-off hero characters with their own turnaround sheet: the sheet's
  front/side/back views are projected onto the mesh (z-buffer visibility, facing weights), auto paint fills what
  no view sees. Needs parts fitted to that sheet (overlay check); fitted parts are not reusable across characters,
  and views the sheet doesn't show (¾, top, under the chin) stretch or fall back to auto.
- **Export unlit** (decided by Marcel, 2026-11-15): the GLB material uses `KHR_materials_unlit`; the light lives
  in the painted texture, so scene lights don't light it a second time. A lit variant (less painted light) may
  come later as a per-pack option. The material is texture → Background shader (what Blender's glTF exporter
  writes as `KHR_materials_unlit`), single-sided, linear filter; `export` fails without the extension.
- Max. 8 base colours per character, as in `clean`.
- **Tool:** `paint_surface(name, approach?, seed?)` after every `assemble_from_parts` (assembly puts the palette
  material back, and `validate` reports `not_painted` until the character is painted). It unwraps to one UV layer
  `Paint` (the palette UVs are removed), bakes `workspace/<name>/paint/<approach>.png`, packs it into the
  `.blend` and renders lit + unlit sheets. `approach`/`seed` are stored in `spec.paint`. Colour changes: edit
  `spec.colors`, re-run `paint_surface` (`apply_palette`/`recolor` are palette-only).

## 5. Shading & normals

- **Smooth by angle, 40°**, as in `clean`. The painted texture carries the lighting detail; the normals stay simple.

## 7a. Proportion templates (values) → style.json

- **`chibi` (draft, not approved):** calibrated on the skeleton-knight turnaround. 1.20 m body (skull top
  estimated inside the helmet); head 0.41 m (≈ 3 heads), 0.34 × 0.36 m; head joint at 0.79 m; shoulders at
  x ±0.22; shoulder-to-wrist 0.30 m; torso guide 0.52 × 0.32 m (armour); hips at 0.36 m (x ±0.14, estimated,
  hidden by the tunic); ankles at 0.095 m; feet 0.21 m ankle-to-toe + 0.10 m heel, 0.24 m wide, 0.10 m high.
  The reference draws the arms ≈ 67° down from the T-pose.

## 11. Preview renders → style.json

As in `clean`: front, side, back, ¾; 512 px per view; background `#E8E8E8`.
