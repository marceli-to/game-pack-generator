# PROGRESS.md

Living status of the project. **Read this first in every session; update it before ending one**
(what changed, decisions, next step). Keep it short: details belong in PLAN.md / STYLE.md / git history.

_Last updated: 2026-11-17 — Rogue + villager detail pass done (awaiting Marcel's look). Then three QA items:
`pose_test` now tells visible overlaps from hidden ones, `validate` checks ears a part declares it covers
(`P.covers`), and the dwarf's axe no longer swings through his face in `interact` (per-clip `clip_offsets`)._

---

## Where we are

| Phase (PLAN.md) | Status |
|---|---|
| 1 — Foundations: wrapper, QA, skeleton, proportions | ✅ done (`ea6705e`) |
| 2 — First static character (the mage) | ✅ done, mage approved 2026-11-15 (`21656d4`) |
| 3 — Skinning & animation | ✅ done, wizard approved 2026-11-16 (animated, GLB plays in three.js) |
| 4 — Parts library | **nearly done** (lowpoly: 3–5 parts per slot, 8 characters from specs, catalog grid; Marcel's look at the new parts) |
| 5 — Packs & batch | — |
| 6 — Integration & extensions (image route, props, …) | — |

| Style | Status | Character |
|---|---|---|
| `clean` | in use | mage (approved 2026-11-15) |
| `painted` | draft; `auto` / `projection` / `ai` paint | knight v3 head, wizard head test |
| `lowpoly` | draft; flat shading, chibi; Phase 4 library | wizard (approved 2026-11-16), knight-lowpoly, rogue, villager (Marcel: "look alright"), dwarf, ranger, farmer, paladin (test mixes, not reviewed) |

## Next session: start here

0. **Marcel's look at the rogue and villager after their detail pass** (viewer / Heerschar; GLBs in
   `workspace/<name>/export/`). Comparison sheets: `workspace/knight-lowpoly/detail/detail_<name>.png` (rows head /
   body / legs: sheet | render per view), `head_<name>.png`, `full4.png` (rogue, villager, ranger, farmer).
   Paladin rebuilt with the new knight parts (3,530 tris, soft over the 3,500 target; animates, exports); metal
   41 → 51 like the knight (Marcel, 2026-11-17).
   Scripts (local, gitignored) in `workspace/knight-lowpoly/detail/`: `body.sh <name> [part ...]` (any character:
   rebuild parts, head/body/legs rows vs its sheet), `head.sh <name> [part ...]` (head close-ups), `loop.sh` +
   `shoulder.sh` (knight only); edit parts in `workspace/lib4/parts/`. Marcel's in-game eye catches things the
   sheets don't: have him look in Heerschar after each character.
1. **Marcel's look at the new parts** (catalog `workspace/_catalog/lowpoly/all/catalog.png` + `catalog.html`) and the
   three test mixes `ranger` (elf head, short hair, gloves, cuffed boots, potions), `farmer` (short hair + beard,
   baggy trousers), `paladin` (stern head, armoured legs, sabatons, book): `workspace/<name>/renders/preview/view_sheet.png`,
   `pose_test/pose_test.png`, GLBs in `export/`. Paladin/ranger not rebuilt since the knight parts changed.
2. **Heerschar in-game test** (Marcel has the wizard and the knight in the game now; wizard "finished", knight fixed
   after his round). Earlier agent brief (Marcel's game, `/Users/marceli.to/Jamon.digital/Webroot/heerschar`): brief handed to
   another agent (knight-lowpoly as the player `krieger`, driven by the game's KayKit Knight clips: same bone names;
   hips track × 0.689; `swaps: []`). Wait for its report; likely generator follow-ups: export with KayKit clip names
   (floor clamp / hand damping baked in), a recolour mapping for the palette texture, separate weapon nodes for the
   swing trail.
3. Phase 4 wrap-up: dwarf slots still have one part each (dwarf parts only fit the dwarf template); decide whether
   Phase 4 needs dwarf variants or moves on to Phase 5 (`build_pack`, 10-character pack).
4. Open from the earlier sheets: all sheets: boots closer together, arms hanging steeper. Dwarf: head group 1,248
   tris (> 1,000); the left shoulder pad pushes 3.5–5 cm into the side of the beard in `attack`/`die` (the beard is
   as wide as the shoulders: narrow it where it meets the shoulders, if Marcel minds).
   **What the visible pose test now shows on every robed/tunic character** (real, was hidden in the noise):
   boots/shins come out through the back of skirts and tunics when the foot kicks back in walk/run/jump
   (villager 12 cm, rogue 10 cm, wizard, ranger, farmer); collars/mantles touch the head in `die`. Fix idea: the
   skirt weights' back hem following the shin, or shorter kick-back via per-clip `clip_offsets` on `lowerleg`.
5. Phase 3 leftovers (optional): kicked-back shins pierce the back of the wizard's robe in walk/run; in `die` the
   held staff lies across the wizard's face; knight `hit` 14 cm torso into helmet (probably the C-shaped guard
   shell fooling the parity test; not among the visible findings any more).
6. Painted/`ai` open points (lower priority): lighter skin treatment in auto paint, mouth spilling onto the beard,
   iron too light/even, 512 px per view thin for a full body; the knight body.

### Phase 1 delivered
- MCP server `server/main.py` (stdio, registered in `.mcp.json`): `get_style`, `init_character`, `import_glb`, `stats`, `render_preview`, `validate`, `export`.
- One headless Blender process per job (`server/blender.py` → `jobs/_entry.py` → `jobs/<job>.py`); JSON args/result files; refuses any Blender other than the pinned version.
- `validate` implements the STYLE.md §12 rules (hard/soft/info). Not yet checked: edge loops at joints, foot contact (both Phase 3, `pose_test`).
- `export`: GLB + Khronos glTF validator + headless three.js test load (Playwright, `viewer/viewer.html`).
- `library/`: `palette.png`, `skeleton.blend` (KayKit Rig_Medium + `headslot`/`backslot`), `animations.blend` (8 clips), `proportions/human.json` (+ preview), `CREDITS.md`. Rebuilt by `python -m server.build_library --source <KayKit folder>`.
- 33 pytest tests; fixtures (mannequin + planted defects) are generated at run time by `jobs/make_mannequin.py`.

### Phase 2 delivered
- New MCP tools: `add_reference`, `build_part`, `list_parts`, `render_parts_catalog`, `assemble_from_parts`, `apply_palette`, `recolor`, `compare_reference` (15 tools total).
- Part builder API (`jobs/lib/parts.py`, `P.loft/ring/rect/rrect/box/rbox/cylinder/shell/mirror_x/transform/set_role/set_bone`) + part checks (STYLE.md §9a). Parts (now in `styles/<style>/parts/<slot>/`) with their build script (`.py` = source of truth), meta and preview.
- `compare_reference`: reference crops / same-scale renders / silhouette overlay + IoU per view; arms lowered for A-pose drawings (`spec.compare.arms_down_deg`), staff hidden (`hide_slots`).
- Mage: `specs/mage/spec.json`, 10 parts, **2,380 tris** (v2, rounder: 12–19-sided rings, bevelled boxes via `P.rbox`; smooth by angle 40°), 8 colours, height 1.80 m, `validate` clean (no hard, no soft), IoU front 0.84 / side 0.85 / back 0.81, GLB passes glTF validator (0/0) and three.js test load (no clips yet).
- 46 pytest tests (incl. `test_mage_approval_still_valid`).
- Viewer default look: soft room lighting + neutral tone mapping (`?look=basic` for the old one); `testload.mjs` takes an extra viewer query.

### Style profiles (committed after `21656d4`, see git log)
- One look = one **style**: `styles/<name>/` with `STYLE.md` ↔ `style.json` (archetypes, budget, shading, surface, palette, parts, previews), `proportions/`, `parts/`, `palette.png`. Shared rules: root `STYLE.md` ↔ `core.json` (skeleton, roles, slots, topology, animations, export, approval). Section numbers are the same in both.
- Loader merges core + style (`server/style.py`, `jobs/lib/style.py`); `run_job(..., style=)` → env `GPG_STYLE`. `spec.style` picks it; specs without one use `core.json` `default_style` (`clean`). Part tools and `get_style` take `style=`.
- Current look moved to `styles/clean` (mage unchanged, approval still valid). 49 tests.

## Painted-style spike (2026-11-15, `4b8d8b7`; decided: auto)

- **`styles/painted/`** (draft): STYLE.md ↔ style.json; surface `painted`; archetype **`chibi`** (1.0–1.4 m, ≈ 3 skull-heights);
  budget 4,000–6,000 (hard 8,000), head ≤ 1,800 / 2,500 (raised to 3,000 / 3,500, see decisions); mid-tone palette (base colours per role); `paint` config
  (`auto` light/AO/crease/noise + per-role treatments, `projection` weights). Root STYLE.md table lists it as "draft".
- **`chibi` template** (`styles/painted/proportions/chibi.json`), calibrated on the knight sheet at 0.00177 m/px
  (1.2 m body, skull top and hips estimated). Mannequin vs sheet IoU 0.77 / 0.73 / 0.80 (arms_down 67°); fits well.
  Factors vs KayKit: leg 0.71, torso 0.61, arm 0.52, head 1.63 (short limbs: watch the clips in Phase 3).
- **Parts** `head-skull` (884 tris) + `headwear-helmet-kettle` (1,276 after the fitting pass) in `styles/painted/parts/`; head group 2,160.
  New builder primitive **`P.shell(grid, thickness, role, cyclic=…)`**: thick sheet from a point grid (plates, guards,
  bands; later capes/tunics).
- **`paint_surface` job** (`jobs/paint_surface.py`, `jobs/lib/paint.py`; a Blender job only, no MCP tool yet): smart-UV unwrap → numpy texel map
  (position/normal/face per texel) → texture. `auto`: analytic light + shadow tint, Cycles AO bake, edge wear /
  dirt by distance to convex / concave creases, value noise, role treatments (mottle, rust, scratches, Voronoi
  cracks, glow). `projection`: sheet views projected with z-buffer visibility + facing weights, falls back to auto.
  `render_views(..., light="FLAT")` for unlit previews.
- **Bug fixes after the first look:** (1) smart UV project can fold a chart onto itself (the outer dome front
  overlapped the hidden inner dome → black bars at the band); `unwrap` now detects texel overlaps, gives those faces
  their own island and repacks (24 faces on the knight), and fails if any overlap is left. (2) Conservative
  rasterisation so faces thinner than a texel still get paint. (3) Projection depth buffer supersampled 3×
  (`zbuffer_scale`), facing power 2 → 4 (less ghosting where views overlap).
- **Fitting pass (v2 parts):** overlay of the model outline on the sheet (`workspace/knight-spike/scripts/overlay.py`,
  output `workspace/knight-spike/overlay.png`; spike scripts are local only, `workspace/` is gitignored) → band 5 cm tall with front/back V points and a 4.8 cm tilt, cheek-guard gold
  frame ~5 cm, slimmer skirt, teeth/nose raised. Helmet 1,276 tris, head group 2,160. v1 scripts kept in
  `workspace/knight-spike/parts/*.v1.py`. Projection now loses the double band and ghost cheek guards in front/side/back;
  ¾ still smears (teeth, stray band line across the eyes) and the skull's edge-on faces in the side view fall back to auto.
- **Knight test character:** `workspace/knight/`; spec in `specs/knight/spec.json`, reference in `specs/knight/reference/` (Marcel's own work, may be published).
  Comparison sheet: `workspace/knight/paint/compare_paint.png` (rows: reference, auto flat, projection flat,
  auto lit, projection lit).
- **Findings:** projection looks like the art from the 3 drawn views, but needs geometry that matches the drawing
  closely (double gold band, ghost cheek guards, stretched teeth in ¾, seams where views meet) and needs a
  turnaround per character, so it can't reuse parts across a pack. Auto works for any part combination and is
  deterministic, but still looks cleaner and flatter than the art (needs stronger, larger-scale painterly
  treatments). Recommendation: auto as the surface mode; projection optional, only for one-off hero characters.
- **Decided (Marcel, 2026-11-15):** `auto` is the painted surface; `projection` stays optional for hero characters.
- **Decided (Marcel, 2026-11-15):** knight sheet is his own work → `specs/knight/reference/`.
- **Decided (Marcel, 2026-11-15):** painted characters export **unlit** (`KHR_materials_unlit`, light lives in the
  texture; `paint.unlit` in style.json); a lit export (less painted light) later as a per-pack option. Not in `export` yet.

## Auto-paint tuning (2026-11-15; Marcel: direction OK)

- **Measured first:** per-material colour stats of the sheet vs the render (`workspace/knight-spike/scripts/colstats.py`:
  hue/sat buckets for metal, gold, bone → value p5/50/95 and dark/mid/light colours). Old auto: metal value range
  half the art's (std 0.08 vs 0.19), gold ochre instead of orange, bone grey (#C1AF8D vs #F6CDA2).
- **New `auto` model** (`jobs/lib/paint.py`, styles/painted STYLE.md §4): signed light value (wrapped key light +
  top-to-bottom gradient **per connected piece** + AO) → brush dabs (random value per Voronoi cell) + soft value
  bands → **hue-shifted ramp** per role (shadows darker/more saturated/towards red, lights brighter/towards
  yellow; `ramp` overrides per role) → treatments: rim light on lit convex edges + rim shadow on the others
  (`edge_width` per role), rust driven by edges/creases/lower part of each piece, fewer longer cracks with a lit
  lip, glow core + **glow halo** spilling onto nearby faces (eye sockets).
- Draft palette cells nudged to the art's mid-tones: 6 bone `#F0C99C`, 40 painted iron `#74566B`, 42 gold `#DE8C30`.
- **Bug fixed:** AO bake had `margin=0`, so the conservative-raster border texels read AO 0 → dashed dark lines
  along every UV seam (also in the old renders). Bake margin 4 px (extend).
- After tuning, stats are close to the art: metal V p5/50/95 0.24/0.44/0.75 (art 0.18/0.44/0.81), gold mid
  #C57A2E (art #D57A2F), bone mid #E7C59C (art #F6CDA2). Sheet: `workspace/knight/paint/compare_auto_tuned.png`
  (rows: reference, old auto, new auto unlit, new auto lit). Tuning loop: `workspace/knight-spike/scripts/tune_auto.py <tag>` (~9 s).
- Remaining gap is mostly **geometry**, not paint: rivet domes, the skull's sculpted cheeks/jaw/teeth, the
  dome's hole; the art's crisp gold top rim needs a bevel on the band to catch the rim light.
- New test `test_auto_paint_on_mannequin` (53 tests).

## Painted surface tool (2026-11-15)

- **MCP tool `paint_surface(name, approach?, seed?)`** (`server/tools/paint.py`, 16 tools): painted styles only;
  bakes into `character.blend`, texture in `workspace/<name>/paint/<approach>.png`, lit + unlit sheets;
  approach/seed default to `spec.paint` (stored there when passed, so the spec hash covers them); projection
  uses the character's `add_reference` sheet. Returns `texture_sha256` (painting is deterministic per seed, tested).
- **Material** (`paint.painted_material`): texture → **Background** shader when `paint.unlit` (Blender's glTF
  exporter writes that as `KHR_materials_unlit`; an Emission shader exports as emissive), backface culling on
  (`doubleSided: false`), palette UV layer removed (the GLB had two TEXCOORDs, the paint on `TEXCOORD_1`).
- **validate** is surface-aware (`_palette_rules` / `_painted_rules` in `jobs/lib/measure.py`): hard
  `not_painted` (still the palette material, e.g. after re-assembly), `texture`, `texture_size`, `uv_outside`
  (0..1), `uv_overlap` (shared texels), `not_unlit`; soft `uv_layers`, `material_name`, `colours` (base colours).
- **export**: report gets `gltf` (extensions, unlit/doubleSided per material, samplers, TEXCOORD count); fails if
  an unlit style's GLB lacks `KHR_materials_unlit`. Viewer only forces nearest filtering on NEAREST textures, so
  painted textures stay linear. `apply_palette` refuses painted styles.
- **Knight (head only)**: `paint_surface` → `validate` 0 hard (soft: head 2,160 > 1,800 target; floor, no body yet)
  → `export` ok: unlit, 1 UV set, linear sampler, glTF validator 0/0, three.js load ok
  (`workspace/knight/export/character-knight-testload.png`).
- Docs: root STYLE.md §10/§12/§14 (approval of painted characters also records `texture`), painted STYLE.md §4,
  PLAN.md tool table + workflow. New test `test_painted_character_paints_validates_and_exports_unlit` (54 tests).

## Knight v3 test: how far can procedural go? (2026-11-15)

Marcel found the painted knight "very mid". Time-boxed test: rebuild only the head, one paint round, compare.
- **Builder:** `P.sweep(path, profile, role, normals, cyclic)` (bevelled straps/bands/rims/frames),
  `P.strap_profile(width, height, bevel)`, `P.dome(center, normal, r, height)` (rivets).
- **Parts (new, old ones kept):** `headwear-helmet-bell` (1,982 tris: bevelled band + wide crest, cheek-guard gold
  frames, dome rivets, broken-hole plate), `head-skull-grin` (1,028: deep slanted sockets, cheekbones, heart nose,
  arched jaws with teeth on the arc, chin). Head group 3,010 (was over the old hard 2,500; budget raised to 3,000 / 3,500).
- **Paint:** `light.facet` (part of the key light from flat face normals: painted planes), `light.shadow`
  (ray-cast key-light shadows: under the band, cheekbones, teeth), bigger dabs, darker metal; special → cell 33.
- Test character `workspace/knight-v3/`, loop `workspace/knight-v3-test/run.py`, sheets in
  `workspace/knight-v3-test/tune/v3*/compare.png` (rows: reference, old head, v3).
- **Result:** clearly better than v2 (silhouette, band, crest, rivets, grin, shadows) but still reads as procedural:
  pastel even iron, the hole reads as a decal, the face is stiff. Ceiling of this route for the look, as predicted.

Decided: keep these parts, head budget raised (3,000 / 3,500). Marcel: "better", but asked whether AI texturing
could close the gap → AI-texture spike below.

## AI-texture spike (2026-11-15; `spikes/ai-texture/`, details in its README)

- **Idea:** geometry, UVs, rig and export stay ours; an image model paints the views, our `projection` paint bakes
  them. Unlike projecting Marcel's hand-drawn sheet, the views are generated *from our renders*, so they match
  the mesh by construction.
- **Setup (Marcel: local, no hosted service):** SDXL base + depth ControlNet + IP-Adapter (style reference = crop
  of the knight sheet, style blocks only) via `diffusers` on MPS; all licences allow commercial use of outputs.
  4 views (front, side, back, side_mirror) in one 2×2 1024² image → one style across views; img2img from the
  auto-paint render. `projection` now takes a real `side_mirror` view (asymmetric details like the helmet hole).
- **Result (run `a1`):** clearly better than auto paint: glowing eyes in dark sockets, shaded teeth, gold with real
  light/shade, the hole reads as torn metal; the ¾ view (never generated, only projected) holds up. Issues:
  vertical "plank" lines on the dome (the model reads the 16 faceted segments of the start image as panels), iron
  still a bit light. Sheet: `spikes/ai-texture/runs/a1/compare.png` (local, gitignored).
- **Cost:** ~18 min per image on the 16 GB M1 Pro: SDXL + ControlNet + encoders don't fit, it swaps (~55 s/step).
  `gen.py` already loads in stages (encoders freed before the UNet). Expected on the Mac Studio: ~1 min (Max)
  or less (Ultra); a few-step SDXL variant (SDXL-Lightning) should cut it ~3× more.

- **Timing on the M4 Max / 64 GB (2026-11-16):** `gen.py a1` loads in 6 s (models cached) and generates in 27–29 s
  (18 steps at ~1.4 s/step, no swapping); ~35 s total. Knight build ~10 s, guides ~2 s, projection ~8 s → one full
  round in under a minute. Result looks like the M1 run (glowing eyes, shaded teeth, torn hole; plank lines on the
  dome still there).

- **Plank lines fixed (2026-11-16):** cause is the depth ControlNet reading the 16 flat dome segments as panels
  (isolated: `--cn 0` → gone; smooth start image, blurred depth, lower `--cn`, prompt words, no style ref → still
  there). Fix: `guides.py` renders depth from a subdivided copy (subsurf 2, edges > 40° creased). Runs `f1`/`f2`
  clean with detail kept. Spike knobs added: `gen.py --guides/--init-blur/--depth-blur/--helmet/--neg-extra`,
  `knight_v3.py --facet/--smooth`, `paint_surface` job arg `auto` (overrides of `paint.auto`, not used by the tools).

- **SDXL-Lightning tested (2026-11-16):** `gen.py --lightning 8 --steps 13` → 6 s instead of 27 s (LoRA, Euler
  trailing, no CFG; `peft` added to the spike requirements). Cleaner and flatter than full SDXL, closer to the
  start image; strength/ip/cfg tweaks change little. Both are fast enough here (a full round < 1 min).
- Flux / image-to-3D notes added to SPIKE.md (Phase 6; FLUX.1 [schnell] for turnarounds, licence caveat, local TRELLIS).

- **Decided (Marcel, 2026-11-16):** full SDXL (30 steps, ~27 s) is the default; Lightning stays an option (`--lightning 8`).

## `ai` paint approach (2026-11-16)

- **`paint_surface(name, approach="ai", subject=…)`**: auto paint (start image + fallback) → `ai_guides` job
  (`jobs/ai_guides.py`, `jobs/lib/aiguides.py`: framing from the bounding box, smoothed depth, real-outline mask,
  reference.json) → `ai/gen.py` in its own env `ai/.venv` (`server/ai.py` runs it; `GPG_AI_PYTHON` overrides) →
  projection (`paint_surface` job, approach `ai`, `paint.ai.projection` overrides). `subject` stored in
  `spec.paint` (required for `ai`); prompt = subject + `paint.ai.style_prompt`.
- Settings in `styles/painted/style.json` `paint.ai` (↔ STYLE.md §4); style reference moved to
  `styles/painted/style_ref.png` (crop of Marcel's knight sheet).
- Knight v3 head via the tool: ~49 s total (auto 4 s, guides 6 s, generation 33 s, projection 5 s); validate 0 hard;
  export ok.
- Tests: `test_ai_guides_on_painted_mannequin`, `test_ai_paint_needs_subject_and_environment`,
  `test_paint_approaches_documented`, and `test_ai_paint_end_to_end` (only with `GPG_AI_TESTS=1`). 58 pass.

- **Second head: wizard (2026-11-16)**, from Marcel's wizard sheet (his own work; later committed as
  `specs/wizard/reference/turnaround.webp`). Parts `head-round-chibi`, `face-beard-wizard`, `hair-white-sides`,
  `headwear-wizard-hat-chibi` (painted, chibi; 1,474 tris), scripts in `workspace/wizard-head/parts/`, built into
  `styles/painted/parts/`. `ai` paint ~50 s, works on hat/band/star/beard, but **reinterprets the face**: adds a
  nose, drops the smile (knight style ref worse than the wizard sheet as ref; strength 0.45 + "nose" in the
  negative prompt doesn't help). Hat colour: painted palette has no mid magenta-purple (cell 15 reads pink).
  Sheets: `workspace/wizard-head/cmp_ai.png`, `cmp_ai2.png`.

- **Decided (Marcel, 2026-11-16):** keep simple faces procedural; add a purple to the painted palette.
  → `spec.paint.keep_roles` (projection/ai; tool arg `keep_roles`, validated against the roles) keeps the auto
  paint on those roles + `paint.ai.keep_margin` (2 cm, voxel-hash `near_mask`) around them; painted palette cell
  38 `#3A2672` (unused deep indigo) → `#8A45AC` magenta-purple, `palette.png` regenerated. Wizard: primary 38,
  skin 0, keep `["skin", "eyes", "dark"]` → face stays (dot eyes, smile, no nose), hat reads purple. Left: the
  model's mouth still spills a few cm onto the beard top (smaller); the kept skin is tan (auto paint puts the face
  in the brim's shadow; the sheet keeps faces light). Sheets `workspace/wizard-head/cmp_ai3.png`, `cmp_ai4.png`
  (H = wizard sheet as style ref looks closest).

Open (painted, parked): lighter skin treatment in auto paint (less shadow/AO on faces), bigger keep margin or
"mouth" in the negative prompt; iron lighter/more even than the sheet; 512 px per view may be thin for a full body
(try 768 or per-region passes); the knight body.

## `lowpoly` style (2026-11-16)

- Marcel's wizard sheet (his own work, now `specs/wizard/reference/turnaround.webp`) is a new look → style
  **`lowpoly`** (draft): palette surface, **flat shading** (new `shading.mode: flat` in `jobs/lib/shading.py`;
  `validate` warns on smooth faces instead), chibi archetype (painted chibi targets, checked against the sheet at
  2.18 mm/px), clean palette with cell 38 → a magenta-purple (now `#9A5BBA`, see round 1), low segment counts (8–10 sides, single chamfers).
  `styles/lowpoly/` (STYLE.md ↔ style.json, palette.png, proportions/chibi.json + preview), root STYLE.md table.
- **Wizard** (`specs/wizard/spec.json`, style lowpoly): 10 parts (scripts in `workspace/wizard/parts/`, built into
  `styles/lowpoly/parts/`), first pass **1,784 tris**, 8 colours; IoU front 0.73 / side 0.76 / back 0.76 (arms_down 50°, staff
  hidden); validate 0 hard (soft: asymmetry from hat tip + pouch); export ok (glTF validator, three.js load:
  `workspace/wizard/export/character-wizard-testload.png`, colours match the sheet). Not approved yet.
- Marcel's round 1 (rounder hands/feet, gap at the shoulders, colours too dark): hands and boots with two chamfer
  steps (`seg=2`); sleeves start inside the robe (x 0.06) and the robe shoulders are broader (gap under the beard
  closed); colours: lowpoly cell 38 → `#9A5BBA` (lighter, softer), skin 0; the dark look was mostly the Blender
  preview (Workbench studio light) → new optional `preview.exposure` (lowpoly: +1.0, background compensated).
  Now 1,992 tris, IoU 0.73 / 0.76 / 0.75. Sheet: `workspace/wizard/preview_bright.png`.
- Round 2 (mittens ended in a flat cut, colours not saturated enough): mittens and thumbs are lofts of rounded
  rectangles that taper and close at the tip; previews use Blender's `paint.sl` studio light (`preview.studio_light`)
  instead of the exposure boost (exposure clipped the lit faces towards white); skin back to cell 1. 2,280 tris,
  IoU 0.73 / 0.75 / 0.76. Sheet: `workspace/wizard/preview_r2.png`.
- Marcel: "perfect" → committed + pushed `035a557` (everything from 2026-11-16). Final: 2,280 tris, 8 colours
  (primary 38, accent 42, skin 1, hair 13, leather 46, secondary 45, eyes/dark 9, special 58).
- Rebuild loop: `.venv/bin/python workspace/wizard/run.py [part ...]` (builds the named parts from
  `workspace/wizard/parts/*.py` into the library, re-inits from `specs/wizard/spec.json`, assembles); then
  `compare_reference("wizard")`, `validate`, `export`. `workspace/` is gitignored: the committed source of truth
  is `styles/lowpoly/parts/<slot>/<part>.py`.
- 62 tests.

## Phase 3: skinning & animation (2026-11-16)

- **`apply_animations(name)`** (job `jobs/apply_animations.py`, `jobs/lib/anim.py`, tool `server/tools/animate.py`):
  appends the 8 §8 clips from `library/animations.blend` (replacing earlier copies), scales location keys by the
  template's `offset_factors`, then a **floor clamp** (hips raised per frame by the depth of the body's lowest point
  under the floor: wizard walk 5.2 cm at heel strike/toe-off, run 2.7 cm, die 16 cm for the 1.6× head), then bakes
  **upright grips** (`spec.grip`): the slot bone keeps its rest orientation and follows the hand's position;
  in `die` (`skinning.upright_held_clips`) upright at frame 0, then held in the hand.
- **Assembly:** upright items weighted 100 % to their slot bone, which deforms (validate allows it); **skirt
  weights** for a torso part below the hips with `legs` empty (blend hips → thigh, 0 at the hips to `follow` 0.85 at
  the hem, faded out within 8 cm of the centre; core.json `skinning`).
- **`pose_test(name, clips?)`** (`jobs/pose_test.py`): every clip sampled every 2 frames: penetration of parts into
  other parts' closed shells vs the rest pose (ray parity per shell, > 1 cm), anything below the floor, foot contact
  on walk/run, upright tilt; sheet one row per clip (4 frames front + side, framed per clip). ~2.5 s for the wizard.
- STYLE.md §7a (floor clamp), new **§8a** (pose test), §9a (skirt, upright weights, held clips) ↔ core.json
  `skinning` / `pose_test`. `pytest.ini` (`testpaths = tests`: `jobs/pose_test.py` was collected as a test).
- **Wizard:** feet on the floor in walk/run (0 cm), nothing below the floor, staff tilt 0° (except die), validate
  0 hard; export: 8 animations, glTF validator 0/0, three.js plays all clips (walk checked: staff upright).
  Remaining penetrations are mostly hidden (boots inside the robe, sleeve tops vs beard 4 cm, staff through the
  sleeve 4–7 cm).
- **Mage** (cross-check, not re-approved; its approval binds spec + part scripts, both unchanged): same rules work;
  robe stretches a lot in run; staff 10 cm below the floor on `jump` landing.
- **Joint blends** (Marcel in the viewer: the sleeve's inner end showed at the shoulder in `run`, boots too):
  rigid parts crossing a joint swing their inner end out of the body. Now vertices on the body side go to the
  parent bone with a linear blend (`skinning.joint_blends`: sleeves upperarm → chest 5 cm, boot shafts foot →
  lowerleg 4 cm). Sleeve-into-beard/head findings dropped from 4–5 cm in every clip to one vertex in die/interact.
  Left: a dark wedge under the hem in `walk` when a leg lifts (robe inside).
- **Round 2** (Marcel in the viewer: robe and feet weird in `run`, black robe inside): the skirt's hard fade to the
  hips at the centre line sheared the hem open at the front → leg share now split between both thighs across
  ±12 cm, full follow from halfway down (`skirt.follow` 1.0, `full_at` 0.5); centre vertices use 3 bones, so the
  soft weight rule is now `skinning.max_bones_per_vertex` = 3. Lowpoly palette cell 37 (blue violet) → dark robe
  purple `#5A3473`; wizard `dark` 9 → 37 (robe/sleeve insides; eyes stay 9) → **9 colours** (soft warning, max 8).
  Left: a bit of boot shows between the legs when the robe front parts in `walk`.
- **Round 3** (Marcel: thumb through the sleeve, staff should be behind the hat in `run`): KayKit bends the hands
  50–76° against the forearm; chibi mittens in wide cuffs swing their thumb through the cuff → per-archetype
  **`clip_damping`** (lowpoly `chibi`: `hand.l/r` rotations at 50 %, slerp to rest). Staff: **hat clearance**
  in the upright bake: the hat's radial profile in head-bone space vs the staff's per-height radius; the staff leans
  outward around the grip just enough (`skinning.upright_clearance` 1.5 cm; 10° in idle, ≤ 18°), and slides up in
  the hand where its foot would go below the floor; quaternion keys kept on one hemisphere (no flips).
  `pose_test` upright tilt now a finding only above `max_upright_tilt_deg` 30°. Left: in `die` (held) the staff
  ends up 2–3 cm across the face when he lies down.
- **Round 4** (Marcel: robe not overlapping the boots in `attack`): the hem (z 0.19) sits at the knee (0.199) and the
  boot shafts ended at 0.2, so a bent knee swung the shaft top out over the hem or opened a gap. Boot shafts now reach
  0.25 (loft with a ring at the knee; boots 320 → 512 tris, character 2,472) + a knee joint blend `lowerleg` →
  `upperleg` (4 cm): the shaft above the knee moves with the thigh and the robe. `attack` from behind is clean now.
  Tried and dropped: shins sharing the skirt below the knee (no effect, the hem is at the knee) and the back hem
  following the shin (hem twisted, still pierced). **Left:** in `walk`/`run` a shin kicked back comes out through
  the back of the robe instead of lifting it; a cloth-like fix (simulation or per-clip corrective) is out of scope
  for now.
- Tests: `tests/test_animate.py` (docs sync, wizard end-to-end incl. export); 63 pass, 1 skipped.

## Phase 4: parts library, lowpoly (2026-11-16, started)

- Marcel: **lowpoly first**, cast = fantasy RPG mix (wizard, knight, rogue, dwarf warrior, villager).
- Dev loop: `.venv/bin/python workspace/lib4/run.py <name> [--build [part ...]] [--anim] [--export]` builds parts
  from `workspace/lib4/parts/<part>.py` (gitignored; the library `.py` is the source of truth), re-inits from
  `specs/<name>/spec.json`, assembles, validates.
- **New parts** (lowpoly, chibi): `headwear-helmet-knight-block` (dome, gold rim, cheek/neck guard shell, red crest),
  `headwear-hood-block`, `hair-bun-block`, `face-scarf-block`, `torso-armor-tabard-chibi`, `torso-tunic-chibi`
  (diagonal bandolier), `torso-dress-chibi` (apron, hem set back so boots stay inside), `arms-armored-chibi`
  (pauldron shells), `arms-sleeves-slim-chibi` (bracers), `hands-gauntlet-block`, `legs-pants-chibi` (first
  `legs` part), `accessory_hand_r-sword-block`, `accessory_hand_r/l-dagger-block`,
  `accessory_hand_l-shield-round-block` (first `weapon`-grip items and first left-hand slot).
- **Characters** (specs only, all `validate` 0 hard, 8 clips, export ok): `knight-lowpoly` 2,646 tris (name: `knight`
  is the painted head test), `rogue` 2,644, `villager` 2,028.
- **Weapon grip works as specified:** blade along the handslot axis (−Y in the T-pose), edges along the forearm;
  swings correctly in `attack`. Shield: face +Z in the T-pose (over the back of the fist) → faces outward with
  the arms down.
- **Skirt weights now for any torso reaching > 5 cm below the hips**, legs or not (STYLE.md §9a, core.json comment,
  `jobs/assemble.py`): the knight's rigid tabard let the thighs/boots swing out through it; with the blend the
  tabard front follows the lifted thigh. Wizard/mage unchanged (both have `legs` empty).

- **Turnaround sheets from Marcel** (generated with the wizard sheet as reference) for knight, rogue, villager, dwarf:
  `specs/<name>/reference/turnaround.png`, wired into the specs (`reference`, `compare.arms_down_deg` 62, hand
  items hidden). All sheets share the wizard's scale (boot widths 96–102 px) → `add_reference` with
  `top_y = floor_y − 550` (2.18 mm/px, 1.2 m); measuring scale from the boots alone put the knight's chin 3–4 cm low.
  Silhouette profiles in metres: `ai/.venv/bin/python workspace/lib4/profile.py <sheet> <floor_y> 0.00218 <x0> <x1>
  <centre_x> <z_from> <z_to> [step]` (`measure_sheet.py` for floor/figure columns).
- **Fitting round 1:** knight helmet wider/lower (dome to 1.245, brow band ±0.276 with a V point, front ridge, cheek
  guards to 0.8, brush crest sweeping back to y 0.31 / z 1.43), smaller pauldrons; villager big hair mass (±0.33),
  cheek locks, big top bun, wider A-line hem (±0.318); rogue big pointed hood (open shell + cone whose tip curls back
  and to the left; ring orientation = bisector tangent, spine checked so no ring dips under the previous one's
  plane: the first try folded and showed a see-through patch), scarf hanging to a point, bandolier right shoulder →
  left hip, satchel (`accessory_waist-pouch-block`). IoU front/side/back: knight 0.81/0.87/0.79, rogue
  0.79/0.77/0.79, villager 0.72/0.84/0.82 (front low because the white apron reads as background in the sheet mask).
  All animate (no floor/contact findings; left: satchel/pouch vs skirt 3–4 cm in walk/run) and export.

- **Second archetype `dwarf`** (lowpoly; STYLE.md §2a/§7a ↔ style.json, `proportions/dwarf.json` + preview): read off
  Marcel's dwarf sheet at the shared 2.18 mm/px with a metric grid overlay (`workspace/lib4/grid.py`): head top 0.95,
  head joint 0.58, shoulders ±0.26, arm 0.24, hips 0.24 (±0.15), ankle 0.075. **foot_length 0.175** (not the sheet's
  0.26: the foot bone slopes down from the low ankle, 0.26 put the toe joint at z −0.035). Template regenerated
  with the `make_template` + `make_mannequin` jobs (what `build_library` does per archetype).
- **Dwarf parts** (`-dwarf`, built against the dwarf template): `head-dwarf-block` (wide head, same face features),
  `headwear-helmet-horned-dwarf` (dome tilted back 14°, ridge, horns as bisector-oriented lofts, fold-checked),
  `face-beard-braided-dwarf` (deep beard shell, moustache, brows, braids with gold rings), `hair-back-dwarf`,
  `torso-jerkin-dwarf` (jerkin over a steel front plate, big buckle), `arms-sleeves-dwarf` (bare forearms, bracers,
  pads), `hands-mitten-dwarf` (1.2×, single chamfers), `legs-pants-dwarf`, `feet-boots-dwarf` (0.27 × 0.39,
  single chamfers to stay under the 3,000 hard limit), `accessory_hand_r-axe-dwarf` (blade along the forearm).
  Dwarf: 2,888 tris, 8 colours (hair cell 43; trousers share the eyes' dark brown 9), IoU 0.85 / 0.84 / 0.83; walk/run
  floor clamp lifts up to 8.7 cm (long boots on short legs), feet contact ok, export ok.

- **Marcel (viewer, 2026-11-16):** dwarf "looks good, best of the new ones"; knight/rogue/villager "very low in
  details/quality compared to the wizard". First point, the rogue's hood (two pieces: flaps flared out at the front,
  the cone's dark underside showed as a black band over the face). Rebuilt as **one closed loft** from the cowl to
  the curled tip, 12 points per ring with the same angles all the way up; on the rings round the face the 3 front
  points are pulled back into the head (lip at the opening, recess at y −0.06 hidden inside the head), so the strip
  between face and rim reads as the hood's dark interior (role `dark` → rogue cell 9, dark brown like the sheet).
  310 tris, IoU 0.81 / 0.77 / 0.81, max 4 cm hood/arm overlap in attack/die. Marcel: "much better". Knight and
  villager: he tests them in the viewer later.

- **Knight round 2** (Marcel in the viewer: helmet too far from the face, chest, shoulders): helmet gets an inner
  flange ring (band sits on the brow, its underside no longer shows above the face), plain steel cheek guards from
  46° (close round the face, no gold edges), brush crest narrow at the base and wide at the top; torso gets a dark
  gorget, a gold collar with a V point and a breastplate; arms get rounded pauldron caps (4 × 7 shell) with a raised
  gold strap swept along their edges, wide gold forearm bands. (A first pauldron edit silently did not apply: a
  text replace missed after round 1 had changed the numbers; check the built tris after script edits.) Knight
  2,986 tris (hard 3,000: pauldrons trimmed from 5 × 9 + 6-sided strap, collar 12 columns), IoU 0.81 / 0.87 / 0.79;
  pose test clean except `hit` reports torso 14 cm into the helmet with nothing visible in the frames (probably
  the C-shaped guard shell confusing the parity test; to check).

- **Villager round 2** (Marcel in the viewer: hair, shoulders/neck): hair rebuilt as one closed loft like the rogue's
  hood (opening reaches behind the ears, front points pulled into the head, fringe ring dipping to a point at the
  centre), tapered locks moved in beside the cheeks so the ears show, 10 × 5 ball bun on top at the back (406
  tris); dress gets a round white collar (cyclic 3-row sheet following the bodice, two rounded points at the front).
  2,422 tris, IoU 0.72 / 0.81 / 0.82 (front held down by the apron mask), animates, export ok.
  Marcel: skirt inside black ("same issue as the wizard"): `dark` faces (skirt underside, sleeve insides) face
  down and only get light from below, so even a dark shade reads black → villager `dark` = 23 (the dress colour).
  Same for the wizard would be `dark` 37 → 38, but that changes its spec hash (re-approval): asked Marcel.
  Marcel (viewer, `run`): skirt front passes through the pouch. The skirt front follows a lifted thigh up to
  z ≈ 0.42 at the pouch, the pouch (`accessory_waist-pouch-block`, rigid on `hips`) hung down to 0.38. Tried and
  dropped: (1) pouch copies the nearest torso vertex's weights (no effect: it hangs above the hip joint, where the
  torso is hips-only); (2) pouch rigid with the skirt weights 5 cm below the hip (worse, 12–14 cm: rotating with
  the thigh swings its top, above the pivot, back into the body). Fix: new `accessory_waist-pouch-small-block`
  hung high on the belt (0.435–0.54) for villager and rogue; ≤ 2.6 cm left. The wizard keeps his approved pouch
  (same overlap, 3–4 cm in walk/run) and his dark-purple insides: **Marcel: leave the wizard as is** (2026-11-16).

- **Marcel (2026-11-16):** knight and villager "look alright" after round 2 (not formally approved).
- **Variants round (2026-11-16):** 11 new lowpoly parts so every slot has ≥ 3: `head-chibi-elf` (pointed ears swept
  back), `head-chibi-stern` (slanted brows, down-turned mouth), `hair-short-chibi` (closed loft 2 cm over the head's
  facets, 12 columns, fringe tufts at the brow, tucked into the head; 142 tris), `face-beard-short-block`,
  `feet-boots-cuffed-chibi` (turned-down cuff, sole; 560), `feet-sabatons-chibi` (stepped toe plates, gold band; each
  plate ring 4 mm higher than the one behind, else the step faces are zero-area at the sole), `legs-pants-baggy-chibi`
  (bloused over the boot tops), `legs-armored-chibi` (cuisses flaring over the greave tops), `hands-glove-chibi`
  (leather mitten + flared cuff), `accessory_hand_l-book-block` (pinched in the fist, covers ±Z like the shield),
  `accessory_waist-potions-block` (wearer's right front, `special` liquid). All shafts keep the 0.25 top so the knee
  blend and robes work with any boot. Test specs `specs/ranger|farmer|paladin` (no reference): validate 0 hard,
  8 clips, foot contact ok, export ok.
- **`render_parts_catalog` is a grid** now: one row per slot, one 3/4 tile per part, mirrored pairs (arms, hands,
  legs, feet) framed on the +X side; `catalog.html` labels the tiles (name, archetypes, tris), since Blender's Python
  has no image library for text; `stats.rows` = `{slot: [parts]}`. The old one-row-per-part sheet was 12,000 px tall.

- **Knight detail pass (2026-11-16, after Marcel's Heerschar test):** part by part against close-ups of the sheet.
  Helmet v3 (736): 12-point dome flaring into a neck guard, thick bevelled gold chevron brow band over the front half
  only (rim + band raised 2.5 cm so the eyes show), raised nose ridge, slanted cheek guards, crest as an arc of
  chamfered sections. Torso (966): breastplate with chest ridge/crease, thick belt, bevelled buckle frame + prong,
  tabard split at the front with gold trim up the slit and round the hem, gold tab behind the slit. Pauldrons
  rounder and standing off the arm, rim from the collar; gauntlets 1.15–1.28×; new `feet-boots-low-chibi` (ankle
  boots with cuff; the wizard's tall boots stay as they are); sword 0.57 m (pommel, ferrule, flared guard, ridged
  blade), shield Ø 0.42 (12 sides, bevelled rim, boss with gold ring). Steel → cell 51 (neutral mid grey, was
  bluish 41). IoU 0.78 / 0.86 / 0.76, animates (no floor/contact findings), export ok. Sword, shield, arms, hands and
  tabard are shared with the paladin/ranger test mixes, which change too.
  **Headwear closer to the head** (Marcel: knight ears visible, rogue hood loose): knight dome 1–1.5 cm tighter, cheek/
  neck guard's inner surface now follows the head 1.2 cm out (`hug()`: ray to the head-chibi-block profile, clears
  the ears at x 0.235) and blends into the dome rim at the top and the flared neck guard at the back. Rogue hood
  from 0.35 to ~0.265 wide at ear level (2.5–3 cm outside head + ears), cone scaled with it; same 310 tris. No head
  pokes through in any clip; hood vs shoulders 2–3.5 cm in attack/die (was up to 4). Head close-ups for any
  character: `workspace/knight-lowpoly/detail/head.sh <name> [part ...]`.
  Round 2 (Marcel in the viewer: right ear through the helmet, gold band between the legs): the guard's angles run
  46..314 deg and the ear clearance used `abs(a)`, so the right ear (270 deg) got none → angle normalised, clearance
  60–120 deg + 6 mm; ray check from every ear vertex (scratch `ear.py`) now escapes only at the face's cheek corner.
  Gold tab behind the slit removed (read as a band hanging between the legs). Knight 3,964 tris.
  Gotcha: running `jobs/lib/render` directly needs `GPG_STYLE=lowpoly`, else it uses `clean`'s light (dark faces).
  Gotcha: `workspace/lib4/run.py` does not refresh `workspace/<name>/renders/preview/` (those stay from the last
  `render_preview`); for current looks use the detail scripts or `render_preview`.

- **Rogue + villager detail pass (2026-11-17)**, rules written into lowpoly STYLE.md §1a ("finished look").
  Rogue: `torso-tunic-chibi` v2 (leather mantle as a closed 5-ring loft: front/back hang onto the chest below the
  hood rim, sides stay above the T-pose sleeve tops at z 0.78; thick stepped hem band; dark slit wedge; buckle
  frame + prong), `face-scarf-block` longer and tapering to a point, `headwear-hood-block` v3 (opening reaches
  behind the ears, a0 100–118° at ear level, lip pulled 24 % inwards there so the inner strip stays in the head:
  ears show from the front, face + ear from the side), leaf daggers (ferrule, flared guard, 8-point leaf blade),
  `feet-boots-low-chibi` instead of the wizard's tall boots, tunic olive (lowpoly cell 29 → `#566539`). 3,094
  tris, IoU 0.77 / 0.75 / 0.78 (was 0.81 / 0.77 / 0.81: wider hood opening + mantle). Villager: `hair-bun-block` v2
  (front sits back, overhang ~4 cm instead of 10; seven flat pointed fringe locks), `torso-dress-chibi` v2 (small
  Peter-Pan collar on the shoulder top, apron ending 9 cm above the hem with chamfered corners, raised wide belt),
  colours from the sheet: dress cell 23 → `#BE5F68`, hair 45, apron 13, hem 24. 2,804 tris, IoU 0.77 / 0.82 / 0.83.
  Shared `arms-sleeves-slim-chibi`: thick two-step leather cuff (rogue, villager, ranger, farmer). Ranger and farmer
  get the mantle too (shared tunic; reads as a capelet). All four animate (no floor/contact findings; overlaps are
  the known hidden ones: boots inside skirts/tunics, mantle vs hood in attack/interact) and export.
  First mantle try was a 1.8 cm shell: seen edge-on from the side it read as flaps/spikes → closed loft.

- **QA: visible overlaps, covered ears, dwarf `interact` (2026-11-17).** New `jobs/lib/overlap.py` (shells,
  inside tests, crossing points, visibility; shared by `pose_test` and `validate`).
  `pose_test`: where a part goes into another shell, the crossing points are *visible* if a ring of view
  directions 10–75° above the horizon (+ straight above) reaches them with a 4° cone of rays (`visible_cone_deg`;
  a few-mm slit doesn't count). Not from below: under a hem every boot "enters" the skirt's underside (first try,
  −10°, flagged them all). Every penetration gets `visible` (+ `visible_depth_m` = depth of the vertices next to
  the visible crossings, so an armpit seam is shallow); findings only for visible ones deeper than
  `visible_tolerance` = 3 cm. Wizard 70 pairs → 23 findings; what is left is real (see Next item 4).
  `validate`: parts declare features they hide, `P.covers = ["ears"]` (core.json `part_covers`, stored in the part
  .json); soft `covered_visible` when ≥ 3 ear vertices are visible in the rest pose (`covers_check`). Ears = the
  head's islands out at the sides (> 70 % of the skull's half-width; the eyes and mouth are islands too).
  Knight helmet declares it (clean; fires when the ears are pushed out 1 cm). First idea dropped: "head vertex
  visible on the outer side of headwear/hair" also flagged the approved wizard (ears on his side hair) and the
  dwarf (ear tips under the rim): only the part knows whether ears should show, hence the declaration.
  Dwarf: per-archetype, per-clip `clip_offsets` (`{clip: {bone: [axis, deg]}}`, q' = q @ offset); `dwarf`
  `interact` turns `hand.r` 60° about local y: the axe stands up beside his head instead of crossing his face
  (6.1 cm into the head → none). Local z −40° swung the blade across his nose. 67 tests (new `tests/test_overlap.py`:
  synthetic head/ears/helmet in Blender, doc sync).

## Decisions (with reasons)

- **Covered features are declared, not inferred** (2026-11-17): whether ears should show depends on the part (the
  knight's guard hides them, the rogue's hood and the villager's hair show them); a geometric rule flagged
  approved looks.
- **Pose-test findings only for visible overlaps** (2026-11-17): hidden ones (boots inside skirts) drowned the real
  problems; the report keeps all of them.

- **Palette cells changed for the sheets** (2026-11-17): lowpoly 29 dark green → olive `#566539` (rogue tunic),
  23 raspberry → dusty rose `#BE5F68` (villager dress); both were used only by those characters (the wizard's
  approval binds spec + part hashes, not the palette).

- **Lowpoly budget 1,500–3,500 tris, hard 4,000** (Marcel, 2026-11-16; was 2,500 / 3,000): the knight read as work in
  progress next to the wizard in Heerschar; the detail that makes it read finished costs ~4,000 tris.

- **Wizard keeps 9 colours** (Marcel, 2026-11-16): the dark robe purple (lowpoly cell 37) for the robe/sleeve insides
  instead of black; `validate`'s soft `colours` warning (max 8) is accepted for this character.
- **Floor clamp on the body, not just the feet** (2026-11-16): feet-only lifted `die` 15 cm (the lying body's head
  is lowest there); hand accessories excluded so a staff touching the floor doesn't lift the character.
- **Upright staff is held in `die`** (2026-11-16): standing upright beside a lying character looked wrong; following
  the hand freely snapped it sideways at frame 0 (it's modelled upright in the T-pose).
- **Skirt weights instead of rigid robes** (2026-11-16): rigid on `hips`, the legs swung out through the robe front
  in walk/run (boots 13 cm through). Extended to short tabards over legs (Phase 4, same failure on the knight).

- **AI texture model: full SDXL, not Lightning** (Marcel, 2026-11-16): 27 s per image is fine; Lightning (6 s) looks flatter and less painterly.
- **Auto paint look** (Marcel, 2026-11-15: "looks ok"): hue-shifted ramps, per-piece light gradient, brush dabs/bands, rim light/shadow, rust from edges, glow halo; tuned on the knight against the sheet's per-material colour stats.
- **Painted export unlit** (Marcel, 2026-11-15): the light is painted into the texture; scene lights would light it twice and flatten the painted contrast.
- **AI texturing runs locally** (Marcel, 2026-11-15): no hosted service; heavy runs on the office Mac Studio.
- **Painted head budget 3,000 / 3,500** (Marcel, 2026-11-15; was 1,800 / 2,500): the v3 knight head needs ~3,000 for
  bevelled bands, rivets and a sculpted face; tris cost skinning time with many characters, not file size (texture
  ~85 % of the GLB); the character total stays 4,000–6,000.
- **Painted approval binds the texture hash** too (STYLE.md §14): the paint code can change the texture without any spec or part change.
- **Painted surface = `auto` paint** (Marcel, 2026-11-15): works for any part combination and needs no art per character; projection looked closer to the art only from the drawn views and only after fitting the parts to that one sheet (¾ smears, fitted parts not reusable). Projection stays optional for hero characters.
- **Procedural route first**; image-to-3D postponed (SPIKE.md archived until Phase 6).
- **three.js / GLB only**; tool code MIT, packs CC0.
- **Animations: KayKit Character Animations 1.1, `Rig_Medium`** (CC0). Chosen after a retarget test over Quaternius (site licence since 2026-08-28 forbids redistribution in asset packs) and Kenney (too few clips). Its rig is the standard skeleton.
- **T-pose rest** (matches the library rig; clips play unchanged).
- **Clip lengths from the source clip**; location keys kept and scaled per segment (STYLE.md §7a).
- **Colour = per-face `role`** (+ `slot` attribute after assembly); spec maps roles → palette indices. 8-colour rule counts indices actually used.
- **Body height** = floor to top of the head mesh, without hair/headwear; ranges per archetype.
- **`human` template** calibrated on the blue-wizard reference: 1.80 m, 4.4 heads; hips (0.82) and ankles (0.12) estimated (hidden by the robe). Approved by Marcel 2026-11-15.
- **Approval** binds to the spec hash **and each part's script hash** (STYLE.md §14): parts are referenced by name, so a rebuilt part must void the approval too.
- **Staff: upright grip** (Marcel): modelled along world +Z through the hand; Phase 3 keeps the slot upright in clips. `weapon` grip (KayKit axis) stays the default for swords/tools.
- **Beard = `face` slot**, robe = one long `torso` part (`legs` empty), pouch = new slot **`accessory_waist`** (appended, so slot indices stay stable): keeps base parts symmetric.
- **Rigid weights by nearest allowed bone** (`skeleton.part_bones`) at assembly; parts may set bones explicitly.
- **Caps** of rings with > 6 points are quad fans (n−2 tris), not centre fans.
- Preview renders: specular highlight off (washed-out robe fronts).
- **Budget raised** (Marcel, 2026-11-15) from 600–1,000 (Kenney-chunky, looked too edgy) to **1,500–2,500, hard 3,000**; head group ≤ 700 / 1,000; accessories ≤ 300 / 500. Segment & bevel guide in STYLE.md §3.
- **Smooth by angle, 40°** replaces flat shading (Marcel, 2026-11-15): flat shading was what read as 'hard', not the triangle count (tested: same GLB, smoothed normals looked soft). Applied at assembly (`jobs/lib/shading.py`), split normals go into the GLB; `validate` warns on flat faces / unmarked creases. Round things use < 40° steps (heads/beards: 30° corner steps).
- Reference images in the repo only when Marcel says they're his to publish (the mage, the knight, the wizard, and the
  Phase 4 sheets for knight-lowpoly, rogue, villager and dwarf are: Marcel, 2026-11-16).
- **Wizard approval after the pose test** (Marcel, 2026-11-16): the static look is accepted, but approval follows STYLE.md §14 (comparison + pose test sheet), so it waits for Phase 3.
- **Simple faces stay procedural under `ai`** (Marcel, 2026-11-16): `keep_roles`; the image model redraws them (nose, lost smile).
- **Preview light per style** (2026-11-16): `preview.studio_light` (lowpoly: `paint.sl`); the default Workbench studio light made flat palettes look dark and dull, and raising the exposure washed them out.
- **New style `lowpoly`** (Marcel, 2026-11-16): the wizard sheet is a different look (flat facets, chibi, few segments), so it gets its own style instead of changing `clean` (whose smooth-by-angle shading Marcel chose for the mage).
- **Style profiles** (Marcel, 2026-11-15): packs may need different looks (clean now, painted next, others later). The shared pipeline (skeleton, roles, parts mechanics, QA, export) stays one; the look is a folder. Roles are the bridge: palette colour in `clean`, material treatment in `painted`.
- The mage spec has no `style` key (adding one would change its hash and void the approval) → it relies on `default_style = clean`. Add `"style": "clean"` at the next re-approval.

## Environment & gotchas

- **Machine (since 2026-11-16):** M4 Max, 64 GB. Two Homebrews: `/usr/local` (Intel) and `/opt/homebrew` (arm64).
- **Blender 5.2.4 LTS** at `/Applications/Blender.app/Contents/MacOS/Blender` (macos-arm64 .dmg from download.blender.org, checksum verified). Override with `BLENDER_BIN`.
- **Python:** use `/opt/homebrew/bin/python3.13` (arm64, `brew install python@3.13`) for every venv (`.venv`, `ai/.venv`, `spikes/ai-texture/.venv`). The Intel `/usr/local` Pythons can't build the MCP SDK's `cryptography`.
- **MCP SDK is 2.x:** `from mcp.server.mcpserver import MCPServer` (FastMCP was renamed).
- **Blender 5 actions are layered** (slots/channelbags): use `jobs/lib/scene.py` helpers (`action_fcurves`, `assign_action`), not `action.fcurves`.
- **glTF importer** adds bone display shapes (icosphere) → `import_glb` removes them; glTF can't carry face attributes, so imported GLBs always fail `no_role`.
- **Export** unparents the mesh from the armature for the session (validator: `NODE_SKINNED_MESH_NON_ROOT`).
- **Repo location:** `/Users/marceli.to/Jamon.digital/Webroot/game-pack-generator` (moved from a scratch folder on 2026-11-15; venvs recreated). Old scratch files (animation comparison report, retarget tests) are in `workspace/_archive/` (local only).
- **`ai` approach** runs `ai/gen.py` in `ai/.venv` (torch + diffusers + peft; `GPG_AI_PYTHON` overrides); models shared with the spike via the Hugging Face cache. On this M4 Max: model load ~4 s, generation ~27 s.
- **AI spike** has its own venv (`spikes/ai-texture/.venv`, torch + diffusers); models (~13 GB) are cached in `~/.cache/huggingface`. 16 GB RAM is not enough to run it without swapping.
- **KayKit source** is not in the repo (only the built `.blend`s). Download "Free 1.1" from https://kaylousberg.itch.io/kaykit-character-animations to rebuild the library.

## Commands

```sh
.venv/bin/python -m pytest -q                       # all tests (64, ~60 s; 1 skipped: the AI end-to-end test)
GPG_AI_TESTS=1 .venv/bin/python -m pytest -q        # + AI end-to-end (~100 s; needs ai/.venv + cached models)
.venv/bin/python -m server.build_library --source <KayKit_Character_Animations_1.1>
.venv/bin/python -m server.main                     # MCP server (stdio); Claude Code uses .mcp.json
npm install --prefix node && npx --prefix node playwright install chromium
.venv/bin/python workspace/lib4/run.py <name> [--build [part ...]] [--anim] [--export]   # Phase 4 dev loop
.venv/bin/python -m http.server 8000   # then http://localhost:8000/viewer/viewer.html?model=/workspace/<name>/export/character-<name>.glb&anim=walk
```
Viewer: `viewer/viewer.html` (drop a GLB on it, or `?model=<url>&anim=<clip>`; needs internet for three.js).
Parts catalog: `render_parts_catalog(style="lowpoly")` → `workspace/_catalog/lowpoly/all/catalog.png` + `catalog.html`.

## Log

- **2026-11-17** — Paladin metal → cell 51 (knight steel; Marcel), rebuilt, animated, exported.

- **2026-11-17** — Visible-overlap pose test, `P.covers` + `covered_visible` in validate, dwarf `interact` axe fix
  (`clip_offsets`). 67 tests pass. Committed + pushed `9360318`.

- **2026-11-17** — Rogue + villager detail pass (tunic mantle, hood behind the ears, cuffs, daggers, low boots;
  hair fringe, collar, apron, belt; two palette cells from the sheets); "finished look" checklist in lowpoly
  STYLE.md §1a. Paladin re-checked; dwarf arm offset tried and dropped. 64 tests pass. Committed + pushed
  `cea44af`. Awaiting Marcel's look.

- **2026-11-16** — Heerschar test: wizard finished, knight WIP → knight detail pass (7 parts, 3,964 tris), helmet
  and rogue hood close to the head, right-ear fix, slit tab removed. Marcel: "all good now". Lowpoly budget → 4,000.
  64 tests pass. Committed + pushed.

- **2026-11-16** — Knight + villager OK'd by Marcel. 11 new lowpoly parts (every slot ≥ 3), test mixes ranger/farmer/
  paladin (built, animated, exported), catalog as a labelled grid. Heerschar in-game test briefed. 64 tests.
  Committed + pushed `fb66f17`; session ends here.

- **2026-11-16** — Marcel's viewer rounds: rogue hood as one loft ("much better"), knight helmet/chest/pauldrons,
  villager hair/collar. Waiting for his check of knight + villager. 64 tests.
- **2026-11-16** — `dwarf` archetype (from Marcel's sheet) + 10 dwarf parts; dwarf fitted (IoU ≈ 0.84), animated,
  exported. All 5 Phase 4 characters now build from specs only. 64 tests.
- **2026-11-16** — Marcel's turnaround sheets for knight/rogue/villager/dwarf; first three fitted (IoU ≈ 0.8),
  animated, exported. Next: dwarf archetype.
- **2026-11-16** — Phase 4 started (lowpoly, RPG cast): 15 new parts; knight-lowpoly, rogue, villager from specs
  only, animated + exported; skirt weights extended to tabards over legs. Awaiting Marcel's look. 64 tests.
- **2026-11-16** — Round 4 (taller boots + knee blend: robe covers the boots in `attack`); **wizard approved**
  (Marcel; spec + 10 part hashes in `specs/wizard/spec.json`, `test_approval_still_valid[wizard]`). Phase 3 done. 64 tests.
- **2026-11-16** — Rounds 2–3 from Marcel's viewer checks: skirt split across both thighs, dark purple robe inside
  (9 colours accepted), chibi hand damping, staff leans clear of the hat brim. Marcel: "amazing".
- **2026-11-16** — Phase 3 built: `apply_animations` (clips, location scaling, floor clamp, upright staff bake),
  skirt weights, `pose_test` (penetration / floor / foot contact / sheet). Wizard + mage animate; wizard GLB has 8
  clips, validator 0/0, three.js plays them. 63 tests. Marcel: "works quite well", sleeve end showed at the
  shoulder → joint blends (shoulder, ankle). Waiting for his approval.
- **2026-11-16** — Session end: everything committed + pushed (`035a557`). Next: Phase 3 on the wizard, approval after its pose test (Marcel).
- **2026-11-16** — New style `lowpoly` (flat shading, chibi) from Marcel's wizard sheet; full wizard built (10 parts, IoU ≈ 0.75), exports clean; round 1 (rounder hands/feet, shoulder gap, brighter colours), round 2 (closed mitten tips, `paint.sl` preview light, skin 1). Marcel: "perfect".
- **2026-11-16** — Repo set up on the M4 Max / 64 GB (Blender 5.2.4, arm64 Python 3.13, 54 tests pass). AI spike `a1`: ~35 s per image (was ~18 min on 16 GB). Plank lines traced to the depth ControlNet, fixed with a subdivided depth guide. Lightning tested, full SDXL kept. `ai` approach in `paint_surface` (58 tests). Wizard head test: `ai` reinterprets simple faces → `keep_roles` + purple cell 38.

- **2026-11-15** — AI-texture spike (local SDXL + depth ControlNet + IP-Adapter, projected): clearly better than auto paint, ~18 min/image on 16 GB. Repo moved to `~/Jamon.digital/Webroot/game-pack-generator`; spike scripts committed under `spikes/ai-texture/`. Next: Mac Studio.
- **2026-11-15** — Painted head budget raised to 3,000 / 3,500 (Marcel); knight v3 head route kept.
- **2026-11-15** — Knight v3 head test (sweep/dome builders, bell helmet, grinning skull, cast shadows + faceted light): better, still procedural-looking; head 3,010 tris. Awaiting Marcel.
- **2026-11-15** — Painted surface tool: `paint_surface` MCP tool, unlit material/export (`KHR_materials_unlit`), surface-aware `validate`, viewer keeps linear textures; knight head exports clean. 54 tests pass.
- **2026-11-15** — Auto paint tuned on the knight (hue-shifted ramps, per-piece gradient, brush dabs/bands, rim light/shadow, rust from edges, glow halo); AO-bake seam bug fixed; palette cells 6/40/42 nudged. Marcel: direction OK; painted export = unlit (decided).
- **2026-11-15** — Knight sheet published (`specs/knight/`), spike committed + pushed (`4b8d8b7`, `7fc89d8`). Unlit export proposed, awaiting Marcel.
- **2026-11-15** — Marcel picked auto paint for `painted` (projection optional).
- **2026-11-15** — Knight head fitted to the sheet (v2 parts) for a fair projection test.
- **2026-11-15** — Spike fixes: UV overlap repair (black bars), conservative raster, 3× z-buffer, facing power 4.
- **2026-11-15** — Painted spike: `styles/painted` (draft), `chibi` template, knight skull + kettle helmet, `P.shell`, `paint_surface` job (auto vs projection), comparison sheet. 52 tests pass.
- **2026-11-15** — Phase 2 committed + pushed (`21656d4`). Style profiles refactor (`core.json` + `styles/clean/`) committed + pushed. Session ends here; next session starts the painted spike.
- **2026-11-15** — Staff switched to upright grip; mage approved by Marcel (spec + part hashes in `specs/mage/spec.json`). Phase 2 done.
- **2026-11-15** — Shading switched to smooth by angle 40°; viewer gets soft lighting by default; head/beard corners at 30° steps (2,380 tris).
- **2026-11-15** — Budget raised to 1,500–2,500 tris; builder got `P.rrect`/`P.rbox`; mage parts reworked (2,364 tris).
- **2026-11-15** — Phase 2 built: part builder + 8 tools, mage assembled from 10 parts (990 tris, IoU ≈ 0.85), awaiting approval.
- **2026-11-15** — Plan + style spec reviewed and revised (roles, archetypes, proportion templates, CC0 animation library). Repo created, Blender 5.2.4 pinned. Animation libraries compared (retarget test) → KayKit. Phase 1 built and pushed; `human` template calibrated on the mage reference and approved.
