# STYLE.md — Character Spec (shared rules)

This file is the binding spec for every character, in every style. Every value marked `→ core.json` also lives in `core.json` and is read by the tools. Change values here first, then core.json.

**Styles.** The look is a pluggable **style** (`styles/<name>/`: its own `STYLE.md`, `style.json`, proportion templates, parts and, for the `palette` surface, `palette.png`). A style fills in the sections marked *per style* below, with the same section numbers. A character spec names its style (`"style": "clean"`; specs without one use `core.json` `default_style`); a pack is always one style. Tools merge `core.json` with the style's `style.json`.

| Style | Look | Status |
|---|---|---|
| `clean` | flat palette colours, smooth by angle, Kenney-like but rounder | in use (mage) |
| `painted` | chibi, baked hand-painted texture (light, wear, grime; auto paint) | draft (knight head) |
| `lowpoly` | chibi, flat palette colours, flat shading (visible facets), few segments | draft (wizard) |
| `tinfox` | ~5 heads, heroic build, flat palette colours, flat shading (Tinfox shooter) | draft (guard) |

---

## 1. Visual style → per style

Defined by each style in `styles/<name>/STYLE.md` §1 (look, proportions, details, mood).

## 2. Units & orientation → core.json

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

## 2a. Archetypes & height → per style

Defined by each style in `styles/<name>/STYLE.md` §2a (archetypes, height ranges, headwear limit).

## 3. Polygon budget → per style

Defined by each style in `styles/<name>/STYLE.md` §3 (triangle budgets and the segment & bevel guide).

## 4. Colours, roles & surface → core.json + per style

How a role becomes a visible surface is the style's **surface mode** (`styles/<name>/STYLE.md` §4; e.g. `palette`: one flat colour per role). The roles themselves are shared:

- **Colour roles:** every face of every part carries a **role**, never a colour. The character spec maps roles to surface values (palette indices in the `palette` mode).
  - Roles (fixed enum, stored as integers): `0 skin`, `1 hair`, `2 primary`, `3 secondary`, `4 accent`, `5 metal`, `6 leather`, `7 eyes`, `8 dark` (mouth, inner sleeves, soles), `9 special` (glow, crystals), `10 armor` (armour worn over the clothes: vests, plates, pads; lets a vest differ from the uniform under it)
  - Stored as a face attribute on the mesh: `role`, domain FACE, type INT. Part authors (agents or humans) set it when building the part.
  - A part never contains colours, UVs or textures of its own; recolouring a character only means changing `spec.colors`.
  - A spec must define a colour for every role used by its parts (otherwise hard error).

## 5. Shading & normals → per style

Defined by each style in `styles/<name>/STYLE.md` §5 (shading rule; normals always consistently outward).

**Vertex colours** only for baked ambient occlusion, opt-in per style (`shading.ao`): at the end of assembly, Cycles
bakes AO in the rest pose into the corner colour attribute `AO` (grey), remapped as `max(floor, 1 − strength ×
(1 − ao^power))`, and the palette material multiplies the texture with it. glTF writes it as `COLOR_0`, which
three.js multiplies with the base colour, so the palette (and palette recolours) stay unchanged and the game's
lights still light the character; only creases, the shadow under a cap peak, the neck etc. get darker. Styles
without `shading.ao` have no vertex colours.

## 6. Topology rules → core.json (validated)

- Manifold geometry per part (no holes, no inner faces); parts may overlap (e.g. helmet over head).
- No zero-area faces, no duplicate vertices (merge distance 0.0001).
- Quads preferred, triangles allowed; no n-gons > 6 vertices.
- **Joints** (shoulder, elbow, hip, knee, neck, wrist): at least 2 edge loops around the joint for clean deformation.
- Symmetry: base parts symmetric on X, asymmetry only via accessories.
- Every face has a valid `role` attribute (see §4).
- Assembled characters also carry a face attribute `slot` (FACE, INT, index into the slot list in §9). `validate` uses it to leave hair/headwear/accessories out of the body height, for the per-slot budgets (§3) and for the symmetry check of base parts. Without it these checks fall back to the whole mesh or are skipped (reported as info).
- Every part is modelled against the proportion template (§7a): joints sit at the template's joint positions.
- Mesh after assembly: one object `Character`, parented to the armature.

## 7. Standard skeleton → core.json

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

## 7a. Proportion templates → core.json

A proportion template = the rest-pose joint positions of the skeleton for one archetype (`styles/<name>/proportions/<archetype>.json`): world positions of hips, head base (top of `chest`), head top, shoulders (`upperarm` heads), elbows, wrists, knees, ankles, plus the attachment slots.

- Defined in Phase 1, **before any part exists**. Generated by `python -m server.build_library` from the targets in style.json (`archetypes.<name>.targets`) and saved with a mannequin preview (`<archetype>_preview.png` next to it).
- Template **values** (target joint positions per archetype) are per style: `styles/<name>/STYLE.md` §7a, files in `styles/<name>/proportions/`.
- Besides joints, a template carries **volume guides** (head, torso, feet) as a reference for part sizes.
- Every part is modelled to fit the template of its archetype (e.g. a sleeve ends at the wrist joint, a boot top sits below the knee).
- `spec.proportions` changes **rest-pose bone lengths** (edit bones in Edit Mode), e.g. `legs: 0.9` shortens the upper and lower leg bones and moves child joints accordingly. Parts follow via their bone attachment, not via free scaling of the mesh.
- **Never pose-mode scaling:** pose scale is inherited by child bones and attached accessories and ends up in exported animations. After assembly, every bone has pose scale 1.
- **Clip rules (so proportions don't break animations):**
  - Rotation keys are applied unchanged (bone directions and rolls are preserved when lengths change).
  - **Location keys are kept and scaled** by the factor of the offset they move: hips by the leg-length ratio (character ÷ template), so feet stay on the floor; the small authored offsets on `upperarm`/`upperleg` (KayKit, mostly < 10 cm) by the factor of their parent segment; `handslot` keys by the arm factor.
  - Scale keys are stripped on import (they only occur in clips we don't use).
  - **Floor clamp:** `apply_animations` raises `hips` per frame by the depth of the body's lowest point below the floor (base parts only; hand accessories may touch it). Chibi feet are long for their legs, so heel strike and toe-off pitch them deeper than in the source rig (wizard: up to 5 cm in `walk`), and a 1.6× head lies deeper in `die`. Frames above the floor stay unchanged, so feet still lift.
  - `pose_test` includes a foot-contact check on walk/run (each foot's lowest point over the cycle within ±2 cm of the floor, §8a).
- A part may support several archetypes only if it was checked against each template.

## 7b. Fit to the reference → core.json (`fit`)

`fit_to_reference` matches a character to its `add_reference` sheet without touching any part script: it scales body regions across their main axis and stores the factors in `spec.fit`, which `assemble_from_parts` applies to the joined rest mesh (so the spec hash covers them; joints and heights stay where the template puts them).
- **Regions** (`fit.groups`): `head` (head, hair, headwear, face), `torso` (+ waist and back accessories), `arms`, `hands`, `legs`, `feet`. Each has a width (`u`) and a depth (`v`) scale curve: factors at three stations along the region's axis (its start, middle and end; linear in between). Vertical regions scale about the body's centre line (legs and feet about each hip's line); arms and hands (axis along the T-pose arm) scale front–back (`u`) and up–down (`v`) about the arm line. Factors stay within `bounds` = 0.75–1.35.
- **Score** per view, over the union of the two outlines (renders at `size` = 256 px, same framing as `compare_reference`): silhouette IoU and colour agreement. The sheet's pixels are classified to the character's palette colours (nearest in Lab, lightness weighted half: the sheet is shaded); colours closer than `colour_merge` = 14 form one class (black gloves and a dark grey belt). Score = `w_silhouette` = 0.4 × silhouette + 0.6 × colour; minus `smooth_penalty` = 0.05 × the squared log-steps between neighbouring stations (no wobbly outlines).
- **Search:** coordinate descent on the log factors, steps 0.08 → 0.04 → 0.02 (`steps`, `passes` = 2 per step), plus the comparison pose's arm angle (`arms_down_step` = 3°, within `arms_down_range` = 50–85°; stored in `spec.compare.arms_down_deg`). One Blender session, ~300 evaluations, ~20 s.
- **Kept as modelled:** `spec.compare.fit_exclude` lists regions that deviate from the sheet on purpose (Tinfox guard: `feet`, smaller boots than drawn). A region's end that meets an excluded region (`meets`: the trousers' lower end at the feet, the sleeves' end at the hands) stays as modelled too, so it keeps fitting inside it.
- It fits outline and colour areas, not crafted detail: it can make the sleeves as thick as drawn, not add a fold. Re-run `apply_animations` (and `pose_test`) afterwards. On a character already tuned by hand, run it with `apply=false` first: it will undo deliberate deviations from the sheet unless they are excluded.

## 8. Animations → core.json

**Source: KayKit Character Animations 1.1** (Kay Lousberg, CC0, `License.txt` in the download dated 10/12/2025; https://kaylousberg.itch.io/kaykit-character-animations), `Rig_Medium` clips. Recorded in `library/CREDITS.md`. Agents keyframing through bpy produces stiff motion; this is the biggest quality risk of the tool.

- Chosen over Quaternius' Universal Animation Library (CC0 inside the download, but quaternius.com's licence page, since 28 Aug 2026, forbids redistribution in asset packs) and Kenney's animated characters (too few clips).
- Mixamo is **not** used: its terms don't allow redistributing the animations, which conflicts with CC0 packs.
- Agents may *adapt* library animations (trimming, blending, per-archetype adjustments) but do not author full cycles from scratch. Per-archetype adjustment in the style: `archetypes.<name>.clip_damping` = `{bone: factor}` plays that bone's rotations at `factor` of their angle (e.g. chibi hands, styles/lowpoly §7a); `archetypes.<name>.clip_offsets` = `{clip: {bone: [axis, degrees]}}` adds a fixed rotation about the bone's own axis on every key of that clip (a per-clip correction, e.g. the dwarf's wrist in `interact`). `archetypes.<name>.clip_stride` = `{clip: m/s}` re-plants the feet of a locomotion clip (`walk`, `run`) for that ground speed, after the floor clamp (§7a): each foot's stance (the frames its ankle or toe joint is within `stride.contact` = 3 cm of its lowest) moves backwards at exactly that speed, the swing is scaled by the same factor as the stance (it lands where the next stance starts), the hips rise where a planted foot now stands closer under them (the planted leg stays as extended as in the clip: a shorter stride under a sprint's low hips folds the knees), foot heights and orientation stay as in the clip, and thigh and shin are solved with a two-bone IK bending towards the clip's knee. Without it the clip's stride scales with the legs (KayKit's run on long legs is a sprint) and the stance foot slides at an uneven speed; the game plays the clip at `speed / clip_stride` (the speeds go into the export notes). Settings in core.json `animations.stride`.
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

## 8a. Pose test → core.json (`pose_test`)

`apply_animations` adds the clips to an assembled character; `pose_test` plays them and checks the skinned mesh, sampled every `step` = 2 frames (plus the last):
- **Penetration:** vertices of one part that end up inside another part's closed shell (ray parity per shell) although they were outside it in the rest pose, deeper than `penetration_tolerance` = 1 cm. Reported per clip and part pair (depth, worst frame, vertex count).
- **Visible or hidden:** where an edge of the part goes in, the crossing point on the other shell's surface is *visible* if a viewer can see it from a ring of directions around the body at 10–75° above the horizon (and from straight above), with a cone of rays `visible_cone_deg` = 4° wide getting out (a slit of a few millimetres between parts does not count). Not from below: under a hem every boot "enters" the skirt's underside. Hidden overlaps (boots inside a skirt) stay in the report; only visible ones deeper than `visible_tolerance` = 3 cm become findings (the depth of the vertices next to the visible crossings; shallower ones are the seams where limbs meet the body). A boot shaft coming out through the back of a robe when the shin kicks back is visible.
- **Floor:** any slot's lowest point more than `foot_contact_tolerance` (2 cm) below the floor.
- **Upright tilt:** an upright item's slot leaning more than `max_upright_tilt_deg` = 30° (outside `upright_held_clips`).
- **Foot contact** on `walk` and `run` (`foot_contact_clips`): each foot's lowest point over the cycle within ±2 cm of the floor.
- **Sheet:** one row per clip, `columns` = 4 evenly spaced frames from the front, then the same frames from the side, tiles `tile_size` = 256 px, framed per clip (box over its frames × `frame_scale` = 1.1, floor `floor_margin` = 6 % above the bottom edge).
- Findings are not blocking; Marcel judges them with the sheet (§14). Edge loops at joints are not checked: parts are rigid per bone, only skirts and joint blends blend (§9a); a part that crosses a joint needs a ring at the joint for its blend to bend cleanly.

## 8b. Extra clips → core.json (`animations.extra_clips`)

Clips only some games need (first: Tinfox, a shooter). A character gets them when its spec lists them: `spec.extra_clips` = `["aim_1h", ...]`. Same source pack and rules as §8; `range` = source frames kept (shifted to start at 0), `hold` = one source frame held for the clip's length.

| Name | Source clip (KayKit `Rig_Medium`) | Loop | Cut | Arms only |
|---|---|---|---|---|
| `aim_1h` | `Ranged_1H_Aiming` (CombatRanged) | yes | range 12–32 (arm raised, held) | yes |
| `shoot_1h` | `Ranged_1H_Shooting` (CombatRanged) | no | range 0–12 (one shot, starts and ends in the aim pose) | yes |
| `aim_2h` | `Ranged_2H_Aiming` (CombatRanged) | yes | range 8–48 (held, slight sway) | yes |
| `shoot_2h` | `Ranged_2H_Shooting` (CombatRanged) | no | range 0–8 (one recoil) | yes |
| `crouch` | `Crouching` (MovementAdvanced) | yes | hold frame 8 for 64 frames (the pack has no crouch idle), one breath per loop | no |
| `crouch_walk` | `Crouching` (MovementAdvanced) | yes | whole clip | no |
| `crouch_aim_1h` | `Ranged_1H_Aiming` (CombatRanged) | yes | range 12–32, as `aim_1h`, over `crouch` | yes |
| `crouch_shoot_1h` | `Ranged_1H_Shooting` (CombatRanged) | no | range 0–12, as `shoot_1h`, over `crouch` | yes |
| `crouch_aim_2h` | `Ranged_2H_Aiming` (CombatRanged) | yes | range 8–48, as `aim_2h`, over `crouch` | yes |
| `crouch_shoot_2h` | `Ranged_2H_Shooting` (CombatRanged) | no | range 0–8, as `shoot_2h`, over `crouch` | yes |

- **Arms-only clips** are layered by the game over walk/run/idle on the arm bones (`arms_only_bones`: upperarm, lowerarm, wrist, hand, handslot, both sides). The source clips turn the whole body into a stance (2H: root 25°, chest 46°), so their raw arm rotations point the gun sideways on a forward-facing body. `apply_animations` bakes them per character: per frame, the hands keep the clip's orientation (the gun points where the clip points it, along the handslot's local +X) and their position relative to the midpoint of the shoulders; the torso stays at rest; upper and lower arm are solved by a two-bone IK to the wrist, bending towards the clip's elbow. Where a wrist is out of reach on the upright torso, both hands move together towards that shoulder (the grip on the gun stays). Wrist, hand and slot keep the clip's offset from their parent (the slot's recoil). The result keys only those bones; no floor clamp.
- **One side** (`sides` in the clip's config): the 1H clips key the right arm only (`sides` = `["r"]`). The left arm then comes from the base clip the game layers them over (hangs in `idle`, swings in `walk`/`run`); the source clip's left arm stood out almost horizontally on the upright torso (a scarecrow from the front, Tinfox report 2026-11-17). The game layers 1H clips with the right-arm bones only; 2H clips key both arms.
- **Breath** (`breathe` in a held clip's config): a held pose gets one breath per loop, a sine rotation about each listed bone's local X axis, in degrees: `crouch`: spine 1.0, chest 1.5, head −1.5 (the head counters the chest so the gaze stays level). Hips and legs stay still, so the floor clamp has nothing to correct.
- **Stance** (`stance` in a 2H clip's config): the clip's two-handed stance turns the body, so its hands are far apart (0.6–0.9 m on wide shoulders) and the raw positions put both hands at the chest centre with the elbows out. With a stance the right wrist is placed directly: `forward` / `inward` / `down` of the right shoulder as fractions of the arm's length (shoulder to wrist), plus the clip's sway and recoil; the left wrist sits a short way along the gun from it (`left.along`, `left.out`, `left.down`, same unit); the elbows bend towards `elbow` (`out`, `forward`, `down` in metres from the shoulder–wrist midpoint); the shoulder joints come forward and in by `shoulder` (metres; the rig has no collarbone, so this stands in for the shoulders rolling forward and keeps the upper arms in front of a broad chest instead of through it); where recoil carries the grip out of one arm's reach, both hands move together towards that shoulder. Values: `aim_2h` and `shoot_2h`: forward 0.85, inward 0.25, down 0.3; left along 0.18, out 0.08, down 0.02; elbow out 0.25, forward 0.2, down 0.15; shoulder forward 0.12, in 0.03. Reaching in front of the chest needs shoulder joints that are not too wide for the arm's length (Tinfox `hero-m`: joints ±0.25 under the pads, arm 0.53).
- In the GLB an arms-only clip has channels for those bones only (the exporter samples every bone; `export` removes the rest), so the game can layer it without pinning the legs.
- **Over** (`over` in an arms-only clip's config): the arms are solved on the torso of that clip's first frame instead of the rest pose; the hands keep their world orientation, so the gun stays level. `crouch` leans the chest forward and the standing aim clips layered over it pointed the gun ~40° at the floor (Tinfox, 2026-11-17) → `crouch_aim_*` / `crouch_shoot_*`: same sources, cuts, sides and stances as the standing ones, `over` = `crouch`; the game picks them while crouched (also over `crouch_walk`, same source clip). A spec listing one also needs its `over` clip.
- Leaning base clips tilt the aim with the chest (`run` leans 10–20° forward); the game's aim pitch corrects that.

## 9. Naming conventions

- Characters: `character-<name>` (kebab-case), e.g. `character-knight`; props (§9b): `prop-<name>`, e.g. `prop-pistol`
- Parts: `<slot>-<variant>`, the slot name exactly as listed below, e.g. `head-round`, `torso-armor`, `feet-boots-chunky`, `headwear-wizard-hat`, `accessory_hand_r-staff-crystal`
- Slots: `head`, `hair`, `headwear`, `face`, `torso`, `arms`, `hands`, `legs`, `feet`, `accessory_back`, `accessory_hand_l`, `accessory_hand_r`, `accessory_waist`
  - `face`: eyes, brows, moustache and beard. `torso`: also long robes/skirts down to the boots (then `legs` may be empty) and symmetric belts. `accessory_waist`: one-sided belt items (pouch, scabbard), rigid on `hips`. New slots are only ever appended (the `slot` attribute stores the index).
- Objects in Blender: `Character`, `Armature`, part objects before joining: `part_<slot>`
- Files: `character-<name>.glb|fbx|obj`, previews `character-<name>.png`

## 9a. Parts → core.json

- A part is one mesh object `part_<slot>` in `styles/<name>/parts/<slot>/<part>.blend`, next to its build script (`.py`, the source of truth: same script → same part), metadata (`.json`: archetypes, tris, roles, script hash) and preview (`.png`).
- Built only through `build_part`: an agent-written script runs against the proportion template of one archetype, in world space (metres, −Y forward, T-pose, left = +X). It must give every face a role. Parts carry roles, never UVs or materials.
- Hard checks (part is not saved): faces without a valid role, open or non-manifold shells, inside-out shells, tris over the slot group's hard limit (§3), weights to bones the slot may not use.
- Soft checks: tris above target, n-gons, asymmetry of base parts, **fit** to the template (e.g. head top at the head joint's tip, feet on the floor, arms reaching the wrists, hand accessories through their handslot; tolerance `parts.fit_tolerance` in the style).
- Separate closed shells may overlap (helmet over head, belt over robe); hidden geometry still counts towards the budget.
- **Covers:** a part that is meant to hide a feature of another part says so in its script, `P.covers = ["ears"]` (a helmet with cheek guards); stored in its `.json` as `covers`, checked by `validate` (§12, `covered_visible`). Known features: core.json `part_covers`.
- **Weights:** rigid. A part may weight vertices to its slot's bones (`skeleton.part_bones`); `assemble_from_parts` gives every other vertex its nearest allowed bone. Headwear is weighted to `head`, hand accessories to `hand.l/r`: the deforming parents of the slot bones, because slot bones don't deform. A part may also set **blended weights** (`P.set_weights(verts, {bone: w})`) and then use the bones its slot lists in `skeleton.part_blend_bones` (`torso`: the upper arms; the rig has no clavicle, so shoulder pads on the torso share chest and upper arm and turn partway with the arm. `hair`: `chest`, so a long braid or ponytail hanging down the back blends from the head to the chest along its length and stays on the back when the head turns or the body leans). Exceptions applied at assembly (core.json `skinning`):
  - **Skirts:** a `torso` part reaching more than 5 cm below the hip joints (long robes with `legs` empty, short tabards over legs) blends `hips` with the thighs below the hips, from 0 at the hip joints to `follow` = 1.0 at `full_at` = 50 % of the way down to the hem (the lower robe moves with the thigh, so boot shafts stay under it); the leg share is split between both thighs across the centre line, linear over ±`centre_width` = 12 cm (centre vertices: hips + both thighs). A part may override these (`P.skirt = {...}`, stored in its `.json`): e.g. the Tinfox officer's coat, split up the front below the belt, uses `follow` 0.6 ramping to the hem (`full_at` 1.0) and `centre_width_front` 0.01 (front vertices only), so each front panel follows its own thigh and bends instead of lifting as a plank. Small separate pieces (bounding-box diagonal under 12 cm: buttons) take the weights of their centre, so they move as one. Without it the legs swing out through a rigid robe in walk/run; with a hard fade to the hips at the centre line (first try) the hem sheared open at the front in `run`.
  - **Joint blends** (`joint_blends`): rigid parts that reach across a joint swing their inner end out of the body when the joint bends (Marcel saw the sleeve's inner end come out at the shoulder in `run`, the boot shafts at the ankle). Vertices on the body side of the joint go to the parent bone, blended linearly from the joint to `width` inside it: sleeves `upperarm` → `chest` along ±X (5 cm), boots `foot` → `lowerleg` above the ankle (4 cm) and `lowerleg` → `upperleg` above the knee (4 cm): boots under a long robe reach past the knee into the robe, so the part above the knee moves with the thigh and the robe, and a bent knee neither opens a gap at the hem nor swings the shaft top out over it. Only vertices fully on the child bone are changed.
  - **Upright grips:** the item is weighted 100 % to its slot bone (`handslot.l/r`), which then deforms (`validate` allows that for upright slots).
- **Hand accessories** have a grip mode, set per character in `spec.grip` (`{slot: mode}`, default `weapon`):
  - `weapon`: modelled along the handslot's bone axis (KayKit convention, −Y in the T-pose); swings with the hand in every clip (swords, axes, tools).
  - `upright`: modelled along world +Z in the rest pose, grip at the handslot; in the clips the slot keeps its rest orientation and only follows the hand's position, so the item stays vertical (staffs, banners, lanterns). `apply_animations` bakes this into the slot's keys of every clip. Where the item would cut through the headwear (the staff's crystal and the hat brim in `run`), it leans outward around the grip just enough to clear the hat's profile by `upright_clearance` = 1.5 cm (wizard: 10° in `idle`, up to 18° in `interact`); where its foot would go below the floor it slides up in the hand. In `upright_held_clips` (`die`) it is upright only at the first frame and then stays fixed in the hand, so the staff falls with the character instead of standing next to it.

## 9b. Props → core.json (`props`)

A **prop** is an item on its own, outside a character: weapons, thrown items, pickups (later: crates, barrels).
Same style, palette, roles and shading as the characters; no rig, no animation, no slots.

- **Spec:** `specs/<name>/spec.json` with `"kind": "prop"`, `style`, `type` (one of `props.types`), `part` (the
  prop's build script in the library) and `colors` (roles → palette cells, as for characters). A spec without
  `kind` is a character. Optional `reference` (for `compare_reference`): `image` (repo-relative), `length_m` (the
  item's length in the side view, sets the scale), `views` = `{view: [x0, y0, x1, y1]}` (a pixel box around each
  drawn view, views from `props.views` or `item_bottom`; `{"box": [...], "blank": [[...]]}` blanks parts of the box
  where another view reaches into it, e.g. the sniper's top view under its side view's barrel).
- **Built like a part** (§9a): `build_prop(prop, script, type)` runs an agent-written script with the same builder
  `P` (no template: `lm`, `bones` and `guides` are empty) and stores `styles/<style>/props/<prop>.{py,blend,json,png}`.
  Hard checks as for parts (roles, closed shells, not inside-out, the type's hard budget) plus the type's anchors.
- **Units & orientation:** metres, at the size the item has next to the characters in the game (not its real-world
  size: Tinfox hands are oversized). Held items (`weapon`, `thrown`) are modelled **lying along +X**: muzzle /
  front towards +X, top towards +Z, so their right side faces −Y. In glTF that is front +X, top +Y: the frame of
  `handslot.r` while aiming (§8b: the gun points along the slot's local +X, local +Y is up, local +Z is the
  hand's outer side), so the game parents the GLB to `handslot.r` without a rotation.
- **Anchors:** the script names points with `P.anchor(name, point)`; assembly exports each as an empty glTF node of
  that name (identity rotation: its +X is the item's forward). Required per type (`props.types.<type>.anchors`):
  - `grip`: the point that sits at the hand's slot (the `handslot` origin). Weapons: on the handle's centre line, at
    the height where the fist closes round it. Thrown items: offset from their centre towards the item's right side
    (−Y) so that the item sits on the palm side of the fist and shows: the slot lies deep inside a mitten (Tinfox: a
    7 cm grenade centred on it vanished in the fist).
  - `muzzle`: the barrel tip on the bore axis; shots and the muzzle flash start there, along +X.
  - Optional: `grip_l`, where the left hand holds a two-handed gun (front grip, fore-end), for the game to place or
    solve the left hand; the 2H clips (§8b) put it a fixed ~10 cm in front of the right hand.
- **Origin** (`props.types.<type>.origin`): `grip` (held items: assembly moves the mesh so the `grip` anchor is at
  0, 0, 0; the GLB's origin is the grip) or `floor` (pickups: the footprint's centre at x = y = 0, bottom at z = 0).
- **Types:**

| Type | Anchors | Pieces | Origin | Budget (§3) |
|---|---|---|---|---|
| `weapon` | `grip`, `muzzle` | — | `grip` | `weapon` |
| `thrown` | `grip` | — | `grip` | `weapon` |
| `pickup` | — | — | `floor` | `prop` |
| `world` | — | — | `floor` | `prop` |
| `target` | `hinge`, `board_centre` | `board` | `floor` | `prop` |

  `world`: props that stand in the level (barrels, boxes). `target`: a board on a post that the game tips back
  about `hinge` (on the board's bottom edge); `board_centre` is the centre of the board's face and moves with it.
- **Pieces:** a prop is one mesh, unless the game moves part of it on its own. `P.piece(name, parent=<anchor>)`
  puts the faces built after it into a separate piece (`P.piece(None)`: back to the main mesh); faces carry a
  `piece` attribute through assembly (one object, so `validate` and `compare_reference` see the whole prop), and
  `export` splits them: each piece is its own glTF mesh node, named after the piece, with its origin at the parent
  anchor and as that anchor's child (identity local transform), so the game turns the anchor node to move the
  piece. `P.anchor(name, point, piece=…)` makes an anchor a child of a piece (it moves with it). A type's
  `pieces` must exist.
- **Front:** props that stand in the level face −Y (Blender), like the characters: glTF +Z. Their sheet views map
  to the item views by camera: front = `item_side` (camera at −Y, so `length_m` is the front view's width), side
  = `item_front` (camera at +X, front to the left), back = `item_back` (camera at +Y), top = `item_top`.

- **Assembly** (`assemble_from_parts` on a prop spec): the part, moved to its origin, one mesh object named after
  the spec, palette from `spec.colors`, the style's shading, AO baked like characters (§5) but over the style's
  `shading.ao.prop_distance` when it sets one (an AO distance made for bodies darkens a 30 cm gun broadly), one
  empty per anchor. Vertex AO is sampled at vertices: a piece whose vertices all sit inside other pieces bakes dark.
- **Split materials** (`spec.materials` = `{name: [roles]}`, optional): faces of those roles get a copy of the
  palette material under that name (same palette texture, same baked AO), so the game can treat them apart. Only
  for what the game asks for: the Tinfox bubble shield's bubble (`{"M_Bubble": ["special"]}`, made translucent in
  the game). `validate` allows exactly the named extra materials.
- **validate** (§12 rules for roles, colours, surface, topology, shading, vertex colours) and for props: hard: tris
  over the type's hard limit, a required anchor missing, origin wrong (held items: `grip` not at 0, 0, 0 within
  `props.origin_tolerance` = 1 mm; pickups: bottom not at z 0 or footprint not centred), `muzzle` not in front of
  the grip (x ≤ 0); soft: tris above the type's target. No height, skeleton, weight or symmetry rules.
- **Export:** `export/prop-<name>.glb`: §10 rules (palette sampler, `COLOR_0` for AO styles, glTF validator, test
  load without a clip); no skin, no animations; nodes: the mesh and the anchor empties, all at the scene root.
- **Views** (`props.views`, used by `render_preview` and `compare_reference` on props) named like the sheets:
  `item_side` (from −Y: the right side, muzzle to the right), `item_top` (from above, muzzle to the right),
  `item_front` (from +X, into the muzzle), `item_three_quarter` (perspective, front right, from above); extra:
  `item_bottom` (from below, +X to the right).
  `compare_reference` crops each drawn view from `spec.reference`, renders the same view at the same metres per
  pixel, aligns the two by the centres of their outlines (sheets are not always consistent between views; the
  sniper's top view is drawn ~5 % short), and reports IoU per view plus an overlay (red = sheet only, blue = render
  only).

## 10. Export → core.json

Target is **three.js only**; the only format is **GLB**.

- +Y up, apply modifiers, the style's texture embedded (palette.png or the baked paint), one UV set, animations as separate actions, no cameras/lights, Draco off
- Material and texture sampler depend on the surface mode (styles/<name>/STYLE.md §4):
  - `palette`: nearest filter, `magFilter` and `minFilter` both `NEAREST` (9728; Blender writes `NEAREST_MIPMAP_NEAREST` for the minification, `export` rewrites it: a palette texture must never be mipmapped), material exported as `MeshStandardMaterial` (roughness 1, metallic 0), **single-sided** (`doubleSided: false`: every part is a closed shell, §9a), with the style's current palette.png (`export` reloads it; a `.blend` packs the palette as it was when assembled)
  - `painted`: linear filter; unlit (`KHR_materials_unlit` → `MeshBasicMaterial` in three.js) when the style sets `paint.unlit`, else `MeshStandardMaterial`; `export` fails if an unlit style's GLB has no `KHR_materials_unlit`. Blender writes the extension for a texture → **Background** shader → output (not for an Emission shader).
- Vertex colours: `COLOR_0` only when the style bakes AO (`shading.ao`, §5); `export` fails if such a style's GLB
  has no `COLOR_0`.
- Animations: a channel whose node property stays at the node's rest value in every clip is left out (all
  scale channels, most translations: nothing ever moves them, so the result plays the same everywhere;
  `export.prune_static_channels`); a channel that is constant within one clip keeps only its first and last key.
- Skinned meshes (characters) store `WEIGHTS_0` and `COLOR_0` as normalised unsigned bytes (weights summing to
  exactly 255; `COLOR_0` VEC3 with a 4-byte stride) and `TEXCOORD_0` as normalised unsigned shorts (only when
  inside 0..1): core glTF, no extension, ~0.25 MB less per figure; errors ≤ 1/510 (weights, AO) and 1.5e-5 (UVs,
  well inside a palette cell) (`export.pack_vertex_data`). Props keep float attributes (games may copy them into
  batches as plain arrays).
- A style may list the clips its game plays (`export_clips` in its style.json, its STYLE.md §10): the other clips are
  built and checked as usual but left out of the GLB (`export` warns about listed clips the character lacks).
  Without the list every clip is exported.
- FBX/OBJ: not planned; only add if needed later

- For export the mesh is unparented from the armature (skinning stays via the armature modifier/skin), because glTF wants skinned meshes at the scene root (validator: `NODE_SKINNED_MESH_NON_ROOT`).
- Every GLB must pass the Khronos glTF validator with no errors.
- `export` fails (the GLB is still written) when `validate` finds hard style violations (§12); `allow_hard=True`
  turns them into warnings, e.g. for a quick look at a work in progress.
- Test load: headless Chromium via Playwright opens `viewer.html` with the GLB; it must load without console errors, play `idle`, and produce a screenshot. (Plain Node + GLTFLoader fails on embedded textures without image polyfills, so it is not used.)

## 11. Preview renders → per style

Defined by each style in `styles/<name>/STYLE.md` §11 (engine, lighting, views, sizes).

## 12. QA thresholds (`validate`)

**Hard (blocking):**
- Tris > hard limit
- Body height outside the archetype range (§2a), or headwear taller than 60 % of body height
- Faces without a valid `role`, or a role without a colour in the spec
- More than 1 material, or the wrong texture: `palette` surface: anything but palette.png; `painted` surface: not painted yet (still the palette material), more than one texture, or not `paint.texture_size`²
- `palette`: UVs outside palette cells, or a face spanning several cells; `painted`: UVs outside 0..1, faces sharing texels, or not unlit although the style sets `paint.unlit`
- Non-manifold geometry, flipped normals
- Bone names/hierarchy differ from the standard skeleton
- glTF validator errors

**Soft (warning, human decides):**
- Tris above target
- More than 8 distinct palette indices used on faces (`painted`: base colours of the roles used)
- Asymmetry in base parts
- `vertex_colors`: colour attributes other than the baked `AO` layer, or `AO` on a style without `shading.ao`; `no_ao`: a style with `shading.ao` but no `AO` layer (re-assemble)
- Fewer than 2 edge loops at joints
- Vertices with weights from more than `skinning.max_bones_per_vertex` = 3 bones (rigid parts use 1, joint blends 2, skirts up to 3; glTF allows 4)
- `covered_visible`: a part declares it hides a feature of another part (`P.covers`, §9a) but a viewer can still see `covers_check.min_verts` = 3 or more of its vertices in the rest pose (same view directions as the pose test, cone `covers_check.cone_deg` = 4°). Features (`part_covers`): `ears` = the head's islands out at the sides (centre beyond 70 % of the skull's half-width). Catches an ear coming through a helmet's guard (the knight in Heerschar).

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
   The block also records `parts`: the `script_sha256` of every part used (from its `.json`). Rebuilding a part with a different script voids the approval too, even though the spec is unchanged.
   `painted` surface: the block also records `texture`: the `texture_sha256` returned by `paint_surface` (approach and seed live in `spec.paint`, so the spec hash covers them; the texture hash catches changes to the paint code). Painting is deterministic per seed.
