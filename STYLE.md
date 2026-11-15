# STYLE.md — Character Style & Technical Spec

This file is the binding spec for every character. Every value marked `→ style.json` also lives in `style.json` and is read by the tools. Change values here first, then regenerate style.json.

---

## 1. Visual style

**In one sentence:** chunky, friendly low-poly characters with flat colours, a clear silhouette and no surface details. Kenney's character packs are the visual reference.

- **Proportions:** stylised, 3–4.5 heads tall. Large head, compact torso, short legs, slightly oversized hands and feet.
- **Shapes:** simple, readable volumes (boxes and cylinders with light bevels). Prefer clear facets to smooth rounding.
- **Silhouette:** identifiable as a black shape from the front and the side. Every character has at least one distinctive silhouette feature (headwear, weapon, cape, hairstyle).
- **Face:** minimal. Eyes as simple dark shapes (geometry or a palette cell), optional eyebrows/mouth. No nose, or a very simple one.
- **Details:** only through geometry and colour areas, never through texture detail. No outlines, no gradients, no baked shadows.
- **Mood:** friendly, slightly toy-like, nothing realistic or grim.

**Not allowed:** photo textures, normal maps, gradients, transparency (except deliberate special cases), realistic proportions, more than one material.

## 2. Units & orientation → style.json

| Property | Value |
|---|---|
| Unit | 1 Blender unit = 1 m |
| Body height | floor to the **top of the head mesh** (skull), without hair and headwear; range per archetype, see §2a |
| Origin | between the feet, at floor level (z = 0) |
| Forward (Blender) | −Y |
| Up (Blender) | +Z |
| glTF export | +Y up, forward +Z (Blender converts automatically; matches three.js) |
| Transforms | applied before export (location 0, rotation 0, scale 1) |
| Rest pose | **T-pose** (arms straight out along ±X), legs straight below the hips — the library rig's rest pose (§7) |

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
| Character complete | 600–1,000 tris | 1,500 |
| Head incl. hair/headwear | ≤ 300 | 450 |
| Hand-held accessory (weapon, tool) | ≤ 150 | 250 |
| Back accessory (cape, backpack) | ≤ 150 | 250 |
| Prop (later) | ≤ 500 | 800 |

## 4. Colours & material → style.json

- **One material** per character: `M_Palette`, Principled BSDF, base colour = `palette.png`, roughness 1.0, metallic 0.0 (metal is suggested by colour only).
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
- **Colour roles:** every face of every part carries a **role**, never a colour. The character spec maps roles to palette indices.
  - Roles (fixed enum, stored as integers): `0 skin`, `1 hair`, `2 primary`, `3 secondary`, `4 accent`, `5 metal`, `6 leather`, `7 eyes`, `8 dark` (mouth, inner sleeves, soles), `9 special` (glow, crystals)
  - Stored as a face attribute on the mesh: `role`, domain FACE, type INT. Part authors (agents or humans) set it when building the part.
  - `apply_palette` resolves per face: `role` → `spec.colors[role]` → palette index → UV cell centre.
  - A part never contains palette indices or UVs of its own; recolouring a character only means changing `spec.colors`.
  - A spec must define a colour for every role used by its parts (otherwise hard error).
- Max. **8 different colours** per character (readability), counted as distinct palette indices actually used on faces. Roles defined in `spec.colors` but not used by any part do not count.

## 5. Shading & normals

- Flat shading (each face flat); Auto Smooth off.
- Normals consistently outward; no flipped faces.
- No vertex colours (everything via the palette).

## 6. Topology rules → style.json (validated)

- Manifold geometry per part (no holes, no inner faces); parts may overlap (e.g. helmet over head).
- No zero-area faces, no duplicate vertices (merge distance 0.0001).
- Quads preferred, triangles allowed; no n-gons > 6 vertices.
- **Joints** (shoulder, elbow, hip, knee, neck, wrist): at least 2 edge loops around the joint for clean deformation.
- Symmetry: base parts symmetric on X, asymmetry only via accessories.
- Every face has a valid `role` attribute (see §4).
- Assembled characters also carry a face attribute `slot` (FACE, INT, index into the slot list in §9). `validate` uses it to leave hair/headwear/accessories out of the body height, for the per-slot budgets (§3) and for the symmetry check of base parts. Without it these checks fall back to the whole mesh or are skipped (reported as info).
- Every part is modelled against the proportion template (§7a): joints sit at the template's joint positions.
- Mesh after assembly: one object `Character`, parented to the armature.

## 7. Standard skeleton → style.json

Every character uses one armature (`library/skeleton.blend`), **adopted from KayKit Character Animations 1.1, `Rig_Medium`** (CC0, Kay Lousberg; see §8). Clips play on it without retargeting. Bone names are KayKit's and binding (animations depend on them).

```
root                          (floor, between the feet)
└─ hips
   ├─ spine
   │  └─ chest
   │     ├─ head
   │     │  └─ headslot        (added by us; attachment for headwear)
   │     ├─ upperarm.l
   │     │  └─ lowerarm.l
   │     │     └─ wrist.l
   │     │        └─ hand.l
   │     │           └─ handslot.l   (from KayKit; attachment for hand-held items)
   │     ├─ upperarm.r … (mirrored, incl. handslot.r)
   │     └─ backslot           (added by us; attachment for cape/backpack)
   ├─ upperleg.l
   │  └─ lowerleg.l
   │     └─ foot.l
   │        └─ toes.l
   └─ upperleg.r … (mirrored)
```

- 20 deforming bones (`root` doesn't deform) + 4 slots (`handslot.l/r`, `headslot`, `backslot`).
- **No neck and no shoulder/clavicle bones.** Head turns come from `head` on `chest`; arms attach directly to `chest`. Parts are modelled accordingly (no separate neck deformation, shoulders are part of the torso).
- **Adopting the rig (Phase 1):**
  - Source: `Rig_Medium` from KayKit Character Animations 1.1 (GLB). The rig is identical in KayKit Adventurers 2.0.
  - `handslot.l/r` exist in KayKit; they are set to non-deforming. `headslot` and `backslot` are added by us; clips never key them.
  - The final bone list is recorded in style.json; `validate` checks against it.
  - The large-character rig (`Rig_Large`) is not used.
- Slots are non-deforming bones; accessories are rigidly parented to them (100 % weight).
- Bone roll consistent (Blender "Recalculate Roll → Global +Z" for spine/legs).
- Proportions adapt by changing rest-pose bone lengths per the proportion template and `spec.proportions` (§7a); hierarchy and names never change.

## 7a. Proportion templates → style.json

A proportion template = the rest-pose joint positions of the skeleton for one archetype (`library/proportions/<archetype>.json`): world positions of hips, head base (top of `chest`), head top, shoulders (`upperarm` heads), elbows, wrists, knees, ankles, plus the attachment slots.

- Defined in Phase 1, **before any part exists**. Generated by `python -m server.build_library` from the targets in style.json (`archetypes.<name>.targets`) and saved with a mannequin preview (`library/proportions/<archetype>_preview.png`).
- **`human` (approved by Marcel, 2026-11-15):** calibrated on the blue-wizard turnaround (`specs/mage/reference/turnaround.webp`). 1.80 m body; head 0.41 m tall (4.4 heads), 0.32 × 0.34 m; head joint at 1.39 m; shoulders at x ±0.21; shoulder-to-wrist 0.49 m; torso guide 0.38 × 0.26 m; hip joints at 0.82 m (x ±0.11) and ankles at 0.12 m (both estimated, hidden by the robe); feet 0.29 m ankle-to-toe + 0.07 m heel, 0.19 m wide, 0.14 m high.
- Besides joints, a template carries **volume guides** (head, torso, feet) as a reference for part sizes.
- Every part is modelled to fit the template of its archetype (e.g. a sleeve ends at the wrist joint, a boot top sits below the knee).
- `spec.proportions` changes **rest-pose bone lengths** (edit bones in Edit Mode), e.g. `legs: 0.9` shortens the upper and lower leg bones and moves child joints accordingly. Parts follow via their bone attachment, not via free scaling of the mesh.
- **Never pose-mode scaling:** pose scale is inherited by child bones and attached accessories and ends up in exported animations. After assembly, every bone has pose scale 1.
- **Clip rules (so proportions don't break animations):**
  - Rotation keys are applied unchanged (bone directions and rolls are preserved when lengths change).
  - **Location keys are kept and scaled** by the factor of the offset they move: hips by the leg-length ratio (character ÷ template), so feet stay on the floor; the small authored offsets on `upperarm`/`upperleg` (KayKit, mostly < 10 cm) by the factor of their parent segment; `handslot` keys by the arm factor.
  - Scale keys are stripped on import (they only occur in clips we don't use).
  - `pose_test` includes a foot-contact check on walk/run (feet within ±2 cm of the floor at contact frames).
- A part may support several archetypes only if it was checked against each template.

## 8. Animations → style.json

**Source: KayKit Character Animations 1.1** (Kay Lousberg, CC0, `License.txt` in the download dated 10/12/2025; https://kaylousberg.itch.io/kaykit-character-animations), `Rig_Medium` clips. Recorded in `library/CREDITS.md`. Agents keyframing through bpy produces stiff motion; this is the biggest quality risk of the tool.

- Chosen over Quaternius' Universal Animation Library (CC0 inside the download, but quaternius.com's licence page, since 28 Aug 2026, forbids redistribution in asset packs) and Kenney's animated characters (too few clips).
- Mixamo is **not** used: its terms don't allow redistributing the animations, which conflicts with CC0 packs.
- Agents may *adapt* library animations (trimming, blending, per-archetype adjustments) but do not author full cycles from scratch.
- Missing animations: first look for another KayKit clip on `Rig_Medium`; agent keyframing only as the last resort, always reviewed by Marcel.
- **Clip lengths come from the source clip** (imported at 30 fps), not fixed numbers; the actual frame counts are recorded in style.json.

| Name | Source clip (KayKit `Rig_Medium`) | Loop |
|---|---|---|
| `idle` | `Idle_A` (General) | yes |
| `walk` | `Walking_A` (MovementBasic) | yes |
| `run` | `Running_A` (MovementBasic) | yes |
| `jump` | `Jump_Full_Short` (MovementBasic) | no |
| `attack` | `Melee_1H_Attack_Chop` (CombatMelee) | no |
| `hit` | `Hit_A` (General) | no |
| `die` | `Death_A` (General) | no |
| `interact` | `Interact` (General) | no |

The mapping can be changed per pack (e.g. `attack` → `Ranged_Magic_Shoot` for a mage); the GLB animation name stays the §8 name.

- Actions live in `library/animations.blend`, keyed to the standard skeleton.
- Root motion: none (character stays in place; movement is handled in the game).
- In GLB: every action as its own glTF animation with exactly this name.

## 9. Naming conventions

- Characters: `character-<name>` (kebab-case), e.g. `character-knight`
- Parts: `<slot>-<variant>`, the slot name exactly as listed below, e.g. `head-round`, `torso-armor`, `feet-boots-chunky`, `headwear-wizard-hat`, `accessory_hand_r-staff-crystal`
- Slots: `head`, `hair`, `headwear`, `face`, `torso`, `arms`, `hands`, `legs`, `feet`, `accessory_back`, `accessory_hand_l`, `accessory_hand_r`
- Objects in Blender: `Character`, `Armature`, part objects before joining: `part_<slot>`
- Files: `character-<name>.glb|fbx|obj`, previews `character-<name>.png`

## 10. Export → style.json

Target is **three.js only**; the only format is **GLB**.

- +Y up, apply modifiers, palette texture embedded, animations as separate actions, no cameras/lights, Draco off
- Texture sampler: nearest filter (in three.js: `texture.magFilter = THREE.NearestFilter`, set by the viewer)
- Material exported as `MeshStandardMaterial` (roughness 1, metallic 0)
- FBX/OBJ: not planned; only add if needed later

- For export the mesh is unparented from the armature (skinning stays via the armature modifier/skin), because glTF wants skinned meshes at the scene root (validator: `NODE_SKINNED_MESH_NON_ROOT`).
- Every GLB must pass the Khronos glTF validator with no errors.
- Test load: headless Chromium via Playwright opens `viewer.html` with the GLB; it must load without console errors, play `idle`, and produce a screenshot. (Plain Node + GLTFLoader fails on embedded textures without image polyfills, so it is not used.)

## 11. Preview renders → style.json

- Engine: Workbench (fast) or Eevee, flat lighting, no shadows or a soft contact shadow only.
- Camera: orthographic for the turnaround sheet; perspective ¾ view for the hero render.
- Views: front, side (left), back, ¾ front-right.
- Background: neutral light grey `#E8E8E8`, transparent PNG optionally.
- Resolution: 512 × 512 per view; sheet 2048 × 512.
- Comparison sheet: reference (top) vs. render (bottom), same views.

## 12. QA thresholds (`validate`)

**Hard (blocking):**
- Tris > hard limit
- Body height outside the archetype range (§2a), or headwear taller than 60 % of body height
- Faces without a valid `role`, or a role without a colour in the spec
- More than 1 material, or a texture other than palette.png
- UVs outside palette cells, or a face spanning several cells
- Non-manifold geometry, flipped normals
- Bone names/hierarchy differ from the standard skeleton
- glTF validator errors

**Soft (warning, human decides):**
- Tris above target
- More than 8 distinct palette indices used on faces
- Asymmetry in base parts
- Fewer than 2 edge loops at joints
- Vertices with weights from > 2 bones (with rigid part skinning)

## 13. Licence

- Generated packs: **CC0** (`License.txt` in every pack)
- Tool code: **MIT**
- Externally used base parts (e.g. Kenney, Quaternius): CC0 only, source recorded in `library/parts/CREDITS.md`

## 14. Approval

A character is approved when:
1. `validate` has no hard errors
2. The comparison sheet and the pose test sheet have been viewed by Marcel
3. Marcel says yes; the spec stores the approval bound to the exact spec version:
   ```json
   "approval": { "by": "marcel", "date": "2026-11-15", "spec_hash": "sha256:…" }
   ```
   Any later change to the spec changes its hash and voids the approval. `spec_hash` = SHA-256 of the spec JSON without the `approval` block, keys sorted.
