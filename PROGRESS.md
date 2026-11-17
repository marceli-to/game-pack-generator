# PROGRESS.md

Living status of the project. **Read this first in every session; update it before ending one**
(what changed, decisions, next step). Keep it short: details belong in PLAN.md / STYLE.md / git history.

_Last updated: 2026-11-17 — **Tinfox** (Marcel's FPS, sheets in `~/Desktop/tinfox`, handoff `GENERATOR.md`
there). Guard done (update 2 checked by the game). Marcel handed `RIFLE-GUARD.md` + `GUARD-UPDATE-3.md` (stride
fix: walk/run planted for 1.6 / 4.0 m/s) to the game; replies pending. **Next: the officer** (Marcel, 2026-11-17).
Lowpoly Phase 4 items below still wait for Marcel._

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
| `tinfox` | draft; flat shading, ~5 heads (hero-m) | guard (Marcel's viewer rounds, not formally approved), rifle-guard v1 (not reviewed) |

## Next session: start here

**Tinfox** (Marcel, 2026-11-17: replace the Kenney pack in his shooter with his own sheets; order of work in
`~/Desktop/tinfox/GENERATOR.md`). Done: shooter clips (+ crouch-aim clips), style `tinfox` + `hero-m`, the
**guard** (fitted, in the game; see "Tinfox: guard"), the **rifle guard v1** (see "Tinfox: rifle guard"),
the stride fix (see "Tinfox: stride").

1. **Build the officer** (Marcel, 2026-11-17: next character, in a new session; details below in item 3).
   Started: sheet copied to `specs/officer/reference/turnaround.png` (1672×941, like the guard's). Measured: floor
   y 926, belt centre y ≈ 455 → **2.043 mm/px, `top_y` 45** (same size as the guard); view centres front 309 /
   side 797 / back 1339, x ranges 0–640 / 640–1000 / 1000–1672. From the profiles (front half-widths, side
   front..back): cap top 1.87, crown ±0.195 at 1.74–1.78 (saucer, wider than the guard's cap), peak at 1.70 reaching
   y −0.23; epaulettes ±0.39 at 1.26 (fringed, orange); coat hem ≈ 0.55 m, coat flares to ±0.25 at the hem
   (front) / −0.22..+0.24 (side); boot shafts to ≈ 0.39 m (just under the knee 0.42; trousers show between boot
   top and hem, 0.40–0.55; the hem over the knees in walk/run is the risk), boot ±0.28 wide, sole ±0.39 front. Plan:
   reuse head, hair, mittens, trousers, belt; new `headwear-cap-peaked-hero` (brass badge), `face-moustache-hero`
   (handlebar, hair colour), `torso-coat-hero` (stand-up collar with brass trim, buttons, name patch, epaulettes
   on the torso like the guard's pads, skirt to 0.55), `feet-boots-tall-hero`; maybe sleeves with wide cuffs.
2. Replies pending from the game agent (Marcel handed both over 2026-11-17): `GUARD-UPDATE-3.md` (the game must play
   `run` at `speed / 4.0` instead of `speed / 5`; check planted feet in walk/run) and `RIFLE-GUARD.md` (GLB sha
   `291836f8…`, 7,058 tris; mid distance next to a guard, crouched with the SMG, firing). Possible later polish of
   the rifle guard (not asked for): rounder, fuller shoulder pads, puffier vest plates, vest front a little proud
   in the side view. The guard itself is closed (`GUARD-UPDATE-2-REPLY.md`).
3. **Officer** (`characters/sheets/02-officer.png`, ~25–30 %: peaked cap, coat, tall boots, moustache;
   coat hem vs knees in walk/run is the risk). Workflow as for the rifle guard (below). Still open from the guard
   rounds: a Tinfox "finished look" checklist in `styles/tinfox/STYLE.md` and a `validate` rule "face/detail islands
   must touch or enter their base shell".
4. Then `hero-f` + worker, players (two suits, four heads), weapons (prop mode, `grip`/`muzzle` points).
5. Later (game report): file size / shared clips (drop unused clips or one animation file per body type).

**Workflow for a new Tinfox character** (as used for the rifle guard): copy the sheet to
`specs/<name>/reference/turnaround.png`; spec from the guard's (parts, colours, `extra_clips`,
`compare.fit_exclude: ["feet"]`); measure the sheet (`workspace/lib4/measure_sheet.py` for floor/columns) and set the
scale from **two model heights** (floor + belt centre 0.962 m), not the figure top (headwear sits above the 1.80 m
skull); `add_reference(top_y = floor_y − 1.80 / m_per_px)`; new parts in `workspace/tinfox/parts/`; `run.py <name>
--build …`; `compare_reference`; fix parts where the fit would have to distort (e.g. too-tall helmet); then
`fit_to_reference` and **copy `fit` + `compare.arms_down_deg` from `workspace/<name>/spec.json` into
`specs/<name>/spec.json`** (`run.py` re-inits from `specs/` and drops it otherwise); then `--anim --export`.

**Lowpoly (waiting for Marcel):**

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
2. **Cast sheet for the Heerschar agent** (Marcel, 2026-11-17: to see which characters the game still needs):
   `workspace/_catalog/lowpoly/cast.png` (8 characters, front + 3/4, status, carried items). Rebuild:
   `ai/.venv/bin/python -I workspace/lib4/cast.py "$PWD" "$PWD/workspace/_catalog/lowpoly/cast.png"` after
   `run.py <name>` + `render_preview` per character (PIL lives only in `ai/.venv`). Wait for its list of missing
   characters.
3. **Heerschar in-game test** (Marcel has the wizard and the knight in the game now; wizard "finished", knight fixed
   after his round). Earlier agent brief (Marcel's game, `/Users/marceli.to/Jamon.digital/Webroot/heerschar`): brief handed to
   another agent (knight-lowpoly as the player `krieger`, driven by the game's KayKit Knight clips: same bone names;
   hips track × 0.689; `swaps: []`). Wait for its report; likely generator follow-ups: export with KayKit clip names
   (floor clamp / hand damping baked in), a recolour mapping for the palette texture, separate weapon nodes for the
   swing trail.
4. Phase 4 wrap-up: dwarf slots still have one part each (dwarf parts only fit the dwarf template); decide whether
   Phase 4 needs dwarf variants or moves on to Phase 5 (`build_pack`, 10-character pack).
5. Open from the earlier sheets: all sheets: boots closer together, arms hanging steeper. Dwarf: head group 1,248
   tris (> 1,000); the left shoulder pad pushes 3.5–5 cm into the side of the beard in `attack`/`die` (the beard is
   as wide as the shoulders: narrow it where it meets the shoulders, if Marcel minds).
   **What the visible pose test now shows on every robed/tunic character** (real, was hidden in the noise):
   boots/shins come out through the back of skirts and tunics when the foot kicks back in walk/run/jump
   (villager 12 cm, rogue 10 cm, wizard, ranger, farmer); collars/mantles touch the head in `die`. Fix idea: the
   skirt weights' back hem following the shin, or shorter kick-back via per-clip `clip_offsets` on `lowerleg`.
6. Phase 3 leftovers (optional): kicked-back shins pierce the back of the wizard's robe in walk/run; in `die` the
   held staff lies across the wizard's face; knight `hit` 14 cm torso into helmet (probably the C-shaped guard
   shell fooling the parity test; not among the visible findings any more).
7. Painted/`ai` open points (lower priority): lighter skin treatment in auto paint, mouth spilling onto the beard,
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
  `visible_tolerance` = 3 cm. Wizard 70 pairs → 23 findings; what is left is real (see Next item 5).
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

## Tinfox: shooter clips (2026-11-17)

- KayKit's free pack already has them (`Rig_Medium_CombatRanged`, `Rig_Medium_MovementAdvanced`); the pack is now
  kept locally in `workspace/_sources/KayKit_Character_Animations_1.1` (gitignored). `library/animations.blend`
  rebuilt with only the `build_animations` job (the base clips came out with the same lengths).
- **`animations.extra_clips`** in core.json ↔ STYLE.md §8b, opt-in per spec (`spec.extra_clips`, checked by
  `init_character` and `apply_animations`). `range` cuts source frames, `hold` holds one frame (no crouch idle in
  the pack: `crouch` = frame 8 of `Crouching`, a staggered crouch). Measured first (gun direction per frame): the
  1H/2H `Shooting` clips are 12/8-frame shots that start and end in the held aim pose → `shoot_*` = one shot.
- **Arms-only bake** (`anim.bake_arms_only`, per character in `apply_animations`): the source clips turn the whole
  body (2H: root 25°, chest 46°), so their raw arm rotations layered over walk point the gun sideways (sheet
  `workspace/tinfox/clips/raw_clips.png`, last two rows). Bake: hands keep the clip's orientation and their offset
  from the shoulder midpoint, torso at rest, two-bone IK to the wrist with the clip's elbow as pole; out of reach →
  both hands move in together (2H: 3.6–3.9 cm). Gun axis = handslot local +X. Human mannequin: gun yaw ≤ 1.3°
  (shoot_1h 3.9°), aim pitch ≤ 3.2°, hand spacing kept (2H left hand stays on the gun). Report in the
  `apply_animations` stats (`clips.<name>.arms_only`). Sheet with the clips layered over idle/walk/run:
  `workspace/tinfox/clips/baked_layered.png` (scripts next to it).
- **Export:** the glTF exporter samples every bone for every action (force sampling), which would pin legs and
  torso at rest when the game layers an arms-only clip → `export_glb` drops the other channels and repacks the GLB
  (`jobs/lib/glb.py`); validator 0/0/0, three.js loads all 14 clips.
- Gotcha (measuring scripts): bones an action doesn't key keep the previous action's pose in Blender; reset the
  pose before evaluating an arms-only clip on its own (cost me a false 10 cm "grip error").
- 71 tests (new `tests/test_extra_clips.py`).

## Tinfox: style (2026-11-17)

- **`styles/tinfox/`** (draft): STYLE.md ↔ style.json, palette.png, `proportions/hero-m.json` + preview; root
  STYLE.md table. Look as `lowpoly` (palette surface, flat shading) but ~5 heads. Budget (Marcel): character
  3,000–4,500, hard 5,000; head 1,200 / 1,600; hand items 400 / 700. Hands: mitten + thumb first (Marcel).
- **Palette:** lowpoly's layout, cells from the guard sheet's lit flat areas (1 skin, 8 hair, 19 orange, 29 olive,
  43 brass, 53/54/55 belt grey / glove-boot black / cap peak) + the four player slot colours (33, 17, 28, 25).
- **`hero-m` template** from the guard sheet (`specs/guard/reference/turnaround.png`, committed: Marcel's, OK to
  publish) with a metric grid at 2.055 mm/px (skull top under the cap = 1.80 m; floor y 926, no floor line):
  head joint 1.47, shoulders ±0.30, arm 0.49, hips 0.86 (±0.12), ankles 0.13, foot bone 0.26; head 0.30 × 0.30,
  torso 0.44 × 0.32, boots 0.30 × 0.45 m. Segment factors vs KayKit: leg 1.95, torso 1.0, arm 0.85, head 1.32.
  Mannequin vs sheet IoU 0.66 / 0.78 / 0.65 at arms_down 72° (joints line up; the gap is the guard's bulk:
  pads, sleeves, boots). Measuring files: `workspace/tinfox/guard/grid_front.png`, `grid_side.png`.
- `guard` character: spec (style tinfox, archetype hero-m, reference, compare arms_down 72°), `add_reference`
  top_y 50 / floor_y 926 / 1.80 m, views front 321 / side 795 / back 1343. 75 tests.

## Tinfox: guard (2026-11-17)

- 9 parts (`styles/tinfox/parts/`, dev scripts in `workspace/tinfox/parts/`; `workspace/lib4/run.py` now takes the
  style from the spec): `head-hero-square` (square jaw, neck; eyes, brows, nose wedge, smile, ears as geometry),
  `hair-short-hero` (closed loft 1.6 cm over the head, tucked in; sideburns), `headwear-cap-antenna-hero` (crown
  sloping to the back, black peak, orange earpiece + antenna on the left), `torso-jacket-hero` (stand-up collar,
  placket, name patch, down over the crotch), `arms-sleeves-padded-hero` (bulky sleeves, rolled cuff, bare wrist,
  shoulder pad on the upper arm with a flush orange stripe), `hands-mitten-hero`, `legs-trousers-hero`,
  `feet-boots-big-hero` (cuffed shaft, long foot, grey sole sticking out), `accessory_waist-belt-buckle-hero`.
  Colours (8): skin 1, eyes 9, hair 8, olive 29, orange 19, black 54 (gloves, boots, cap peak), brass 43, grey 53
  (belt, soles).
- 3,746 tris, validate 0 hard; IoU 0.69 / 0.75 / 0.67 (arms_down 72°); all 14 clips (`extra_clips`: the six
  shooter clips) animate, feet on the floor, contact ok in walk/run; export ok. Pose test: visible findings are
  joint seams in one colour (thigh into the jacket's lower edge in crouch/run up to 10 cm, trousers into boots
  4–6 cm, arms into the torso in the aim clips ~3.6 cm); they read as one jumpsuit in the frames.
- Fixes on the way: `hip_x` 0.12 → 0.16 (misread the grid: the guard stands with legs apart); boot soles merged at
  x 0 (non-manifold) → boots 3 cm further out; crown tilted down to the back, antenna shortened; crotch closed
  lower; thighs/boots thicker; shoulder stripe stood 1–2 cm proud and read as orange fins with the arms down →
  flush. Left vs the sheet: the guard reads slimmer (sheet: rounder pads sitting higher on the shoulders,
  rounder and wider cap, arms hanging closer to the body).
- **v2** (Marcel: "chest, hips and shoulders need some refinement, also the plate (foot)"): shoulder pads moved
  from the arms to the torso (caps over the shoulder joints, rigid on the chest: the arm hangs and aims from under
  them, as on the sheet; on the upper arm they tipped outward with the arms down), bigger and lower on the
  outside, wider flush stripes; broader chest with a crease under it, higher shoulders; wide hips, upside-down V
  at the crotch, trousers narrower at the top (they stuck out under the belt); one thick sole (7 cm) following the
  boot's width section by section, underside rising under the arch (the v1 sole was a plate sticking out all
  round; a three-piece sole read as stacked steps from the front). 3,826 tris, IoU 0.70 / 0.76 / 0.68, 14 clips,
  floor/contact ok, export ok. New pose-test findings "torso inside arms" (5–7 cm) are the pad over the sleeve
  top: renders show the arm coming out from under the pad (idle, aim_2h), as intended.
- **v3** (Marcel: chest more V-shaped, bulky): chest 0.28 half-width × 0.40 deep at 1.30 (was 0.235 × 0.37), tapering
  to 0.18 at the waist under the belt (was 0.19); pads bigger (0.18 × 0.135 radii) and reaching further out
  (≈ ±0.43 with the arms down, like the sheet); upper sleeves thicker (0.095–0.1); placket and name patch moved
  out with the chest. 3,834 tris.
- **Budget raised** (Marcel, 2026-11-17: "try 8000"): tinfox character 3,000–7,000, hard 8,000; head 2,000 / 2,600.
  Performance: ~20 characters × 8,000 ≈ 160,000 triangles per frame, small for any current GPU; one mesh and one
  material per character either way (no extra draw calls); flat shading makes ~2–3 vertices per triangle, skinned on
  the GPU. **v4** spends some of it on more sides (torso 16, sleeves/legs 14, pads 16, head and boots two chamfers
  per corner, cap three): 4,746 tris. Side by side with v3 (`workspace/tinfox/guard/v3_vs_v4.png`) the difference
  is small (a little rounder head and pads): more sides barely show at this size; the extra budget is better spent
  on details (fingers, pockets, seams, straps) than on rounding. v3 scripts kept in `workspace/tinfox/parts_v3/`.
- **v5: face + fingers** (Marcel: details, the face first). `head-hero-square` rebuilt: rounded-square rings
  (16 points, superellipse) with a centre-front profile (brow ridge, nose base, mouth recess, chin jutting 3 cm);
  bigger tall eyes, thick stern brows, a nose wedge with a bridge, a slight smirk, ears as rounded plates with a
  raised rim, angled out 15° at the back (flat-shaded skin on skin vanished from the side; angled they catch their
  own light; at 25° they looked like handles) (812 tris). New `hands-glove-fingers-hero` (palm block, four thick
  fingers in three faceted segments curling into a half fist, little finger shorter, thumb, cuff; 936 tris) replaces
  the mitten in the guard's spec (the mitten stays in the library). In the comparison pose the fingers look like an
  outward hook (the tool's arm rotation); in the clips they curl in towards the thigh. 5,474 tris, 14 clips, floor/
  contact ok, export ok; hands vs arms/torso 3.3–3.8 cm in the 1H/2H shoot clips. Sheets
  `workspace/tinfox/guard/guard_v5.png`, `face_hands_v5.png`.
  **Marcel: mittens are OK, fingers not worth the tris** → the guard is back on `hands-mitten-hero` (552 tris
  instead of 936); `hands-glove-fingers-hero` stays in the library. Guard 5,090 tris.
- **v6: more on the face** (Marcel: rather spend on ears, nose, chin). Ears: a rim swept round a C open at the
  front over a recessed bowl, an earlobe, still angled out 15°; nose: a rounded 8-sided loft from the bridge to a
  broad tip (≈ 3 cm in front of the face; a 4.5 cm tip read as a beak in ¾) + nostril wings; chin/jaw: 20 points per
  head ring and extra chin rings (square chin jutting ≈ 3.6 cm), lower face 5 mm wider each side. Head 1,452 tris
  (head group within 2,000), guard 5,730. Sheet `workspace/tinfox/guard/face_v6.png`.
  Fixes (Marcel: ears detached, hole in the nose): angling the ears out swung their back edge off the head → bowl
  and rim now root 3.5–4 cm inside the skull (rim: strap `inset` 0.04); the nose was a tube of round rings whose
  back edge floated up to 9 mm in front of the face → every ring now spans from the nose's front to 1 cm inside the
  face. Check for loose face pieces: each head island's vertex count inside the skull (scratch `/tmp/claude-ear4.py`
  idea: worth a `validate` rule "part islands must touch/enter their base shell").
- **Boots smaller** (Marcel: too big, in the viewer): foot 0.39 × 0.24 m (was 0.47 × 0.30, the sheet's size),
  shaft/cuff 15 % slimmer, sole 6 cm (was 7), boots 1 cm closer in. Deliberately smaller than the sheet.
- **Ears 30 % smaller** (Marcel: massive): whole ear scaled to 70 % about where it meets the head (still rooted).
- **Nose:** nostril wings removed, tip ~20 % wider (Marcel). Head 1,364 tris, guard 5,642.
- **Mouth:** thin warm-brown line (Marcel: thinner and brown), wider and flatter like the sheet (±0.07 m). Colour:
  the sheet's `#A75D35` ≈ palette cell 45 `#A0673A`, on the guard's unused role `special` → **9 colours** (soft
  `colours` warning, like the wizard); within 8 it would have had to be the hair's dark brown. Guard 5,654 tris.
- **Shins back into the boots** (Marcel): the boot shaft is centred 3.5 cm behind the lower-leg bone (the foot reaches
  forward), the trousers followed the bone and entered the boot's front → lower trouser rings run back to the shaft
  centre and end slimmer inside the shaft; v3 (Marcel: a little more to the back/corner): y 0.004 → 0.05 and
  x +2 cm from the knee down (the shaft also sits 2 cm further out than the leg), end 0.082 × 0.08.
- **2H aim/shoot fixed** (Marcel: shoot_2h weird, arms should point forward). Cause: the source 2H stance turns the
  body 46°, so on the wide guard (shoulders ±0.30) the clip's hands were 0.6–0.9 m apart; the bake kept that
  spacing, so the hands ended at the chest centre with the elbows out (and the out-of-reach fix pulled the right
  hand behind the shoulder). Fix: `stance` in the 2H clip configs (core.json ↔ STYLE.md §8b, `anim.bake_arms_only`):
  right wrist placed forward 0.62 / inward 0.5 / down 0.28 arm-lengths from the right shoulder (+ the clip's sway/
  recoil), left wrist 0.15 arm-lengths along the gun from it, elbows bend down; report `stance.hands_forward_m` /
  `hand_spacing_m` (test updated). Reach on the guard needed narrower shoulder joints: `hero-m` shoulder_x 0.30 →
  0.25 (under the pads), arm_length 0.49 → 0.53; all parts rebuilt (no script changes). Hands now 0.34–0.43 m in
  front, both arms forward. 1H unchanged (reach error ≤ 1.4 cm). Sheet `workspace/tinfox/guard/guard_v6.png`.
- **Shoulders move** (Marcel: still weird with the shoulders not moving): pads rigid on the chest stayed put while
  the arm swung forward. Now blended weights: new `P.set_weights(verts, {bone: w})` + core.json
  `skeleton.part_blend_bones` (`torso` may blend into `upperarm.l/r`; never used for nearest-bone weighting;
  STYLE.md §9a). Each pad vertex shares chest/upper arm by its position along the pad (smoothstep, 0 at the collar
  → `follow` 0.6 at the outer end). Plain blending dropped the pads ~40° with the arms hanging (sloping shoulders) →
  in the rest pose each pad vertex is pre-tilted up by its arm share × 72° (the arms-down angle) about the shoulder
  joint, so with the arms down the pads sit as modelled and roll forward when aiming. Sheets
  `workspace/tinfox/guard/shoulders_idle_aim_walk.png`, `guard_v7.png`.
- **2H arms through the chest** (Marcel, after the pads followed the arms): upper arms from the joints at ±0.25
  crossed the deep chest front. Fix in the stance: hands further forward and less inward (forward 0.85, inward
  0.25), elbows out/forward (`stance.elbow`), and **shoulder joints moved forward 12 cm / in 3 cm** during 2H
  (`stance.shoulder`, a location key on `upperarm` in the arms-only clip; stands in for the missing collarbone);
  chest front-outer corners rounder (corner radius 0.09 → 0.15). The arms now reach out in front of the chest.
  Pose-test depths for arms/torso stay 4–10 cm: they include the sleeve's inner end inside the jacket (hidden by
  the pad); judge by the frames.
  Sheet: `workspace/tinfox/guard/guard_v3.png`.
- Close-up renderer (`workspace/knight-lowpoly/detail/render.py`) takes `ARMS=<deg>`; `body.sh`/`head.sh` take
  `GPG_STYLE` and `REG` (regions) from the environment.

## Tinfox: how close to the sheet? (2026-11-17)

Marcel: our characters differ a lot from the sheet (detail, "less smooth"); can we get to 90 %? Estimate given:
procedural tops out ~75–80 %. Two tests on the guard (scripts + renders local in `workspace/tinfox/smooth/`;
sheets `summary_full.png`, `summary_head.png`, details `cmp_*.png` / `paint_*.png`):
- **The sheet is flat-shaded low-poly itself** (facets on thighs, gloves, cap, boots). "Smoother" there means
  **few, large, deliberate planes** with small angles between them + soft light; ours has many small facets
  (20-point head rings band the face into stripes).
- **A. Subdivision** (subsurf 1 → 22,688 tris, decimate to 8,000, smooth by angle 40°; roles survive, UVs fine):
  reads as a soft vinyl toy, *further* from the sheet; thin pieces shrink (antenna → pill, nose → blob, stripes
  thinner). Smooth by angle alone: similar, softer. Dropped.
- **B. Paint** (test style `tinfox-painted` = tinfox + painted surface, 2048² `auto`): the knight-tuned auto
  paint adds camo blotches, a dirty face and a glowing mouth (worse); a soft config (light + AO + cast shadow,
  no brush/rust) adds the shadow under the peak and a little depth but also seam lines along the limbs. Close to
  flat. `ai` not run: the sheet carries no painted detail to transfer, and it can't change the silhouette.
  The temp style/spec are parked in `workspace/tinfox/smooth/temp/` (copy back to `styles/` and `specs/` to rerun;
  they break nothing but don't belong in the repo).
- **Marcel likes the soft paint best** (2026-11-17). Before it becomes the tinfox surface: fix the seam lines
  along the limbs, decide unlit (baked light) vs lit, and solve player colours (a texture can't be recoloured by
  moving palette UVs).
- **Lit vs unlit in three.js** (recommended to Marcel: lit, the shooter's levels light the characters). Viewer
  page `workspace/tinfox/smooth/compare.html` (serve the repo root; `?light=room|game|dusk|dark&cam=front|q|headq`),
  shots in `workspace/tinfox/smooth/vc/`. Four guards side by side: A flat; B flat + AO baked into vertex colours
  (`bake_ao.py`, Cycles AO → corner `COLOR_0` × palette texture: palette swaps keep working; GLB valid) → **barely
  visible** under real light, vertex density too coarse; C soft paint (unlit) → nicest in neutral light but
  **glows in dusk/dark** scenes; D texture with only AO + edge highlights, lit (`paint.py litsoft`, temp style
  with `unlit: false`) → keeps C's soft edges and reacts to the light, but the edge highlight also hits the shallow
  ring edges (pinstripes along arms/legs, cap grid) and it's darker than C. If D: highlight only edges sharper than
  ~35°, lift the base a little; costs a texture per character and a recolour scheme for player colours.
  Test copies (gitignored): `workspace/guard-ao/`, `guard-soft/`, `guard-litsoft/`.
- **Built (Marcel picked B):** `shading.ao` (tinfox: 0.3 m, power 2, strength 1, floor 0.2, 128 samples; tuned
  in three.js: 0.25 m / power 1 barely visible, 0.4 m / power 3 dirty). `SH.bake_ao` at the end of `assemble`
  (rest pose, Cycles AO → corner attribute `AO` → remap → multiply node in the character's palette material; parts
  untouched), export `export_vertex_color: MATERIAL` (→ `COLOR_0` only where a material uses it) + fails without
  `COLOR_0` on an AO style, `validate` soft `vertex_colors` / `no_ao`. Test `tests/test_ao.py` (guard end-to-end,
  ~5 s). Sheets `workspace/tinfox/smooth/vc/ao_*.png` (strengths), `final_*.png` (pipeline guard).
- **Rough % (by eye):** v7 flat ~65 %, soft paint ~65–70 %, subdivided ~55–60 %, knight auto paint ~50 %.
- **What is left is form:** cap (sheet: rounder, fuller crown bulging forward over the peak), head (wider jaw,
  bigger round ears, fewer face planes), bulk (bigger pads sitting higher, thicker sleeves with elbow folds,
  wide cuffs, bulkier thighs with knee planes), gloves with fingers. Soft light can be the game's job (lighting /
  AO in three.js) rather than baked.

## Hunyuan3D image-to-3D spike (2026-11-17, Marcel: "see how far we can get"; licence parked, prototype only)

- **Cleaned up (2026-11-17):** weights, venv and the dinov2-giant HF cache deleted (~25 GB); to rerun, reinstall
  (`install.sh` in the port, ~22 GB download). Kept in `workspace/hunyuan/`: scripts, `run2/` (raw output),
  `hyb10/` (best hybrid), the comparison PNGs.
- Port `hunyuan3d-2.1-mac` (MPS, shape + PBR paint) in `workspace/_sources/hunyuan3d-2.1-mac` (gitignored; venv on
  arm64 Python 3.12 from /opt/homebrew, weights ~14 GB in its `weights/`, dinov2 in the HF cache). Run:
  `venv/bin/python tests/e2e_visual.py --image <png> --out <dir> --octree 256 --tex-preset safe --tex-views 6
  --tex-resolution 256` (`--tex-resolution` = multiview size, not texture size; > 256 needs flash attention, refused
  on MPS). Outputs land in its `outputs/`. ~4 min per character (shape 172 s, texture 54 s).
- Guard from the sheet's front view: `workspace/hunyuan/` (`cmp_guard.png`: sheet / v7 / raw / cut to 5,600 flat;
  `cmp_heads.png`; `render_cmp.py` Blender renders, `compose.py`). **Use the OBJ export**: the port's GLB has
  flipped UVs (camo look in Blender).
- Result: **body much closer to the sheet than v7** (bulk, pads, cuffs, fingered gloves, boots), survives a cut to
  5,600 tris + flat shading. **Head is bad**: smeared orange face, no hair at the back, smudged cap. Texture darker
  and slightly mottled. One fused mesh, no roles, no rig.
- **Palette snap + our head** (`workspace/hunyuan/hybrid.py`, loop `go.sh <abs obj> <tag>` → `cmp_<tag>.png`; best
  so far `cmp_hyb10.png`, GLBs `hyb10/snap.glb`, `hyb10/hybrid.glb`): import the textured OBJ (absolute path, else
  Blender loses the texture), **weld** (the textured OBJ is split at every UV seam: 462 shells, 10k open edges →
  crinkled decimation, AO leaking), scale/align to guard v7 (height at the centre column, belt depth), roles per
  face on the 40k mesh by **hue/saturation** (texture is ~2× darker and over-saturated; brightness gain from the
  olive), 8 rounds of area-weighted majority smoothing, roles → materials → collapse to 4,500 tris → palette UVs,
  flat, AO baked (only with our guard removed from the scene: it overlapped and darkened the back). Hybrid = body
  cut at our collar height (+ Hunyuan's chin skin) + our head/hair/cap (1,914) = 6,412 tris, 6 palette colours.
  Tried and dropped: planar dissolve (no gain), Laplacian smoothing before decimation (spiky).
  Left: orange stripes are zigzag blobs (the texture's own blotches), buckle and a belt patch read as skin, jagged
  glove cuffs, skin wedge at the back of the neck. Not tried yet: rig + pose test, three-view input.

## Tinfox: crouch aim + guard update 2 (2026-11-17)

- Game reply (`GUARD-UPDATE-1-REPLY.md`): the 1H left-arm fix and the breathing crouch work; new problem: aim clips
  layered over `crouch` point the gun ~40° at the floor (the crouch leans the chest forward). Fix (their option 1):
  **`over`** in an arms-only clip's config (core.json ↔ STYLE.md §8b): `bake_arms_only(arm, action, over)` solves
  the arms on the base clip's first-frame torso (shoulders, parent poses) instead of the rest pose; hands keep their
  world orientation. New clips `crouch_aim_1h`, `crouch_shoot_1h`, `crouch_aim_2h`, `crouch_shoot_2h` (same sources,
  cuts, sides, stances; `over: crouch`); a spec listing one must list its `over` clip (checked). Library animations
  rebuilt. Measured in the layered pose: standing clips over `crouch` −37…−45°, crouch clips −5…+3° (1H shot kicks
  to +19° as standing), also over `crouch_walk`. Sheet `workspace/tinfox/clips/crouch/clips_sheet.png`.
- Export: palette samplers get `minFilter` NEAREST (9728; Blender wrote NEAREST_MIPMAP_NEAREST), `glb.nearest_samplers`
  (STYLE.md §10). Test checks it.
- Guard rebuilt (fitted, 18 clips) and sent: `~/Desktop/tinfox/characters/glb/guard.glb` (sha `74a0fec5…`),
  `GUARD-UPDATE-2.md`, `characters/glb/guard-crouch-aim.png`.
- **Bug fixed:** `compare_reference` on an animated character lowered the arms from the idle clip's pose (rifle guard
  IoU 0.86 → 0.77 after `--anim`); the job now clears the action and resets the pose first.

## Tinfox: rifle guard (2026-11-17)

- Sheet `specs/rifle-guard/reference/turnaround.png` (Marcel's set, same as the guard's). Scale 1.913 mm/px from
  floor (y 1004) + belt centre (y 501 ↔ 0.962 m): `top_y` 63; the first try put the helmet top at 1.80 m and the
  whole model came out too tall at the top.
- Guard parts reused (head, hair, sleeves, mittens, boots, belt) + 3 new: `headwear-helmet-earcups-hero` (dome low
  at the back, black visor strip, orange centre stripe, earcups, `P.covers = ["ears"]`, earpiece + antenna on the
  left; 744 tris), `torso-vest-armored-hero` (guard jacket with the hidden middle dropped, vest 2.8 cm proud, rolled
  collar rising at the back to the helmet, three pillow plates front and back via `P.shell`, orange tabs and
  straps, guard pads × 1.1; 1,968), `legs-trousers-kneepads-hero` (guard trousers + octagonal pads, black rim, grey
  face, weights half thigh / half shin; 672).
- First fit squeezed the head to 0.79 at the top to match a too-tall helmet → dome lowered (top 1.84) and narrowed in
  the part. The fit's remaining head narrowing (0.92 → 0.89) is real: the sheet's face is narrower than the guard
  sheet's (cheeks ±0.104 vs ±0.126 m).
- Fit: torso width 1.06–1.08, depth 1.17–1.25 (vest), sleeves 1.15, gloves 1.17–1.22, thighs 1.04 deeper, shins a
  little narrower; arms_down 72°. Score 0.718 → 0.742; IoU 0.86 / 0.84 / 0.86 (unfitted 0.80 / 0.78 / 0.81).
- 7,058 tris, 9 colours (as the guard), validate 0 hard; 18 clips, floor/contact ok; pose-test findings are the
  guard's categories (73 vs the guard's 77; pads over the sleeve tops, thighs into the jacket hem in crouch, belt).
  Export ok (validator, three.js load).

## Tinfox: stride (2026-11-17)

- Marcel (in the game): run takes very big steps, walk looks like moonwalking. Measured: KayKit's run on hero-m legs
  (1.95× KayKit's) = planted foot 6.4 m/s, 2.6 m steps (a sprint; the game plays run at `speed / 5` → 0.76× at
  3.8 m/s); walk 1.5 m/s on average but 2.5 m/s after heel strike, 1.1 m/s before toe-off.
- **`archetypes.<name>.clip_stride`** (`{clip: m/s}`, root STYLE.md §8 ↔ core.json `animations.stride`; tinfox
  `hero-m`: walk 1.6, run 4.0, the game's guard speeds): `anim.bake_stride`, run in `apply_animations` after the
  floor clamp. Stance = ankle or toe joint within 3 cm of its lowest (the longest run); the planted ankle moves
  linearly at the speed, the swing is scaled about the stance centre by the same factor (run 0.62, walk ≈ 1.0),
  hips raised where the planted leg would fold (run up to 8 cm; without it the shorter run stride squatted),
  two-bone IK towards the clip's knee, foot orientation kept. Report `clips.<clip>.stride` incl. the measured
  planted speed after baking (walk 1.58–1.70, run 4.00–4.03 m/s). Contact first read on the raw clip: the left heel
  dips below the floor at heel strike (before the clamp) → asymmetric stances; hence after the clamp.
- Gotcha: after resetting the pose, `frame_set(f)` on the current frame doesn't re-evaluate the action (frame 0 read
  as the rest pose) → `frame_set(f0 - 1)` first.
- Test `tests/test_stride.py` (doc sync, guard end-to-end). 84 tests. Sent: `GUARD-UPDATE-3.md` (guard sha
  `56189789…`, rifle guard `291836f8…`, side views `characters/glb/stride-old-new.png`).

## Fit to the reference (2026-11-17, Marcel: "go ahead with the automatic fitting loop")

- **`fit_to_reference(name, apply=True)`** (MCP tool; `server/tools/qa.py`, job `jobs/fit_reference.py`, numpy core
  `jobs/lib/fit.py`, core.json `fit` ↔ STYLE.md §7b): no part script changes. Body regions (`head`, `torso`, `arms`,
  `hands`, `legs`, `feet`) get a width and a depth scale curve (factors at start/middle/end of the region's axis,
  bounds 0.75–1.35) → `spec.fit`, applied by `assemble` to the joined rest mesh (stats `fit_verts`). Score per
  view over the union of outlines: 0.4 × silhouette IoU + 0.6 × colour-class agreement (sheet pixels → nearest
  palette colour of the character in Lab, lightness ×0.5; colours < 14 apart merge) − smoothness penalty.
  Coordinate descent on log factors (0.08/0.04/0.02) + the comparison arm angle (→ `spec.compare.arms_down_deg`).
  The tool assembles without `fit` into a temp blend, fits, saves, re-assembles, runs `compare_reference`.
  ~300 evaluations, ~20 s (Workbench, flat ID colours via a byte colour attribute written with `color_srgb`:
  plain `color` is treated as linear and the IDs drift).
- **Kept as modelled:** `spec.compare.fit_exclude` (guard: `["feet"]`, the boots are smaller than the sheet on
  purpose); a region end that `meets` an excluded region stays at 1.0 (first run: trousers widened past the
  locked boot cuffs).
- **Guard:** score 0.689 → 0.705; IoU front/side/back 0.69/0.75/0.68 → 0.80/0.77/0.79. Fit: torso width
  1.04 → 1.17 upwards (V), depth 1.13 → 1.04; sleeves 1.2× thicker; gloves 1.2×; thighs 1.13× deeper; head
  slightly narrower at the top; arms_down 69°. Animates (floor/contact ok), validate 0 hard, export ok.
- **Other characters (report only):** knight 0.643 → 0.663, rogue 0.600 → 0.642 (would widen the hood 30 %: Marcel
  had it pulled in), villager 0.682 → 0.721, dwarf 0.679 → 0.724.
- Tests `tests/test_fit.py` (units in a Blender subprocess: the server venv has no numpy; doc sync; guard
  end-to-end). 80 tests pass.

## Decisions (with reasons)

- **Crouch aim as separate baked clips** (2026-11-17, game's preferred option): the aim layer keys arm rotations
  relative to the chest, so one clip can't be level over both an upright and a leaning chest; an upright-chest
  crouch (option 2) would have looked stiff.

- **Fit by region scale curves, not by editing part scripts** (2026-11-17): works for every character and part
  combination, is stored in the spec (hash-covered, reversible), and can't break a part's topology. Deliberate
  deviations from the sheet are protected by `fit_exclude`, not guessed.

- **Tinfox surface: palette + AO in vertex colours, lit** (Marcel, 2026-11-17): the shooter's levels must light
  the characters (an unlit baked look glowed in dusk/dark scenes); vertex AO keeps palette recolours (player colours)
  and needs no texture per character. Subdivision and painted textures were tested and dropped (see the test above).
- **Tinfox budget 3,000–7,000, hard 8,000** (Marcel, 2026-11-17; first 3,000–4,500 / 5,000); **mitten + thumb hands** (Marcel: fingers tried, not worth the tris); **sheets committed** (Marcel).

- **Arms-only clips are baked, not just filtered** (2026-11-17): the KayKit aim clips get their aim from the whole
  body's stance; arm rotations alone point the gun sideways on a forward-facing body.
- **1H clips key the right arm only** (2026-11-17, Tinfox report): the source clip's left arm stood out
  sideways on the upright torso; the base clip's left arm (hanging, swinging) reads better.
- **Arms-only clips export only arm channels** (2026-11-17): the game layers them over walk/run; sampled rest keys on
  the other bones would freeze the legs.

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
- **Fit lives in the workspace spec:** `fit_to_reference` writes `workspace/<name>/spec.json`; `run.py` re-inits from
  `specs/<name>/spec.json`, so copy `fit` + `compare.arms_down_deg` there or the next rebuild drops them.
- **Tests and `GPG_STYLE`:** don't run pytest in a shell where `GPG_STYLE` is exported (e.g. after `export
  GPG_STYLE=tinfox` for the detail renders): the tests then default to that style and ~9 fail. Use a subshell.
- **Detail renders for Tinfox:** `ARMS=72 GPG_STYLE=tinfox REG='{...}' workspace/knight-lowpoly/detail/body.sh guard [part ...]`.
- **KayKit source** is not in the repo (only the built `.blend`s). A local copy is in `workspace/_sources/KayKit_Character_Animations_1.1` (gitignored); else download "Free 1.1" from https://kaylousberg.itch.io/kaykit-character-animations to rebuild the library. Animations only: `run_job_checked("build_animations", {"source_dir": ...})` (the full `build_library` also regenerates templates and palettes).

## Commands

```sh
.venv/bin/python -m pytest -q                       # all tests (84, ~90 s; 1 skipped: the AI end-to-end test)
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

- **2026-11-17** — Officer sheet copied + measured (2.043 mm/px, top_y 45); building starts next session.

- **2026-11-17** — ump: rifle guard + update 3 handed to the game by Marcel; next: the officer.

- **2026-11-17** — Stride bake (`clip_stride`): walk/run feet planted for 1.6 / 4.0 m/s (Marcel: big run steps,
  moonwalking walk); guard + rifle guard re-sent (`GUARD-UPDATE-3.md`). 84 tests pass.

- **2026-11-17** — Game confirmed guard update 2 (guard closed). Rifle guard rebuilt, exported (validator 0/0, 18
  clips) and sent (`RIFLE-GUARD.md`). Next: the officer.

- **2026-11-17** — Crouch-aim clips (`over`), NEAREST sampler, guard update 2 sent; rifle guard v1 (3 new parts,
  fitted, IoU ~0.85); `compare_reference` pose fix. 81 tests pass. Next session: rifle guard to the game, then the officer.

- **2026-11-17** — ump: fit committed, Hunyuan files cleaned up; next: fitted guard to the game.

- **2026-11-17** — Automatic fitting loop (`fit_to_reference`, §7b): guard IoU ~0.69 → ~0.79 (workspace only). 80 tests.

- **2026-11-17** — Tinfox report: guard works in the game. 1H clips right arm only (`sides`), breathing crouch
  (`breathe`, 64 frames; library animations rebuilt). 77 tests pass. Update sent to the game agent.
- **2026-11-17** — Guard handed to the tin-wolf agent (brief + GLB in `~/Desktop/tinfox`). Marcel: ~75 % of the
  sheet is fine for now; see it in the game first.
- **2026-11-17** — Tinfox: AO baked into vertex colours (`shading.ao`, Marcel's pick B), guard rebuilt (COLOR_0,
  lit, validator 0/0). 77 tests pass.
- **2026-11-17** — Lit/unlit test in three.js (A flat, B vertex AO, C soft unlit, D AO + edges lit): vertex AO too
  weak, unlit glows in dark scenes, D is the lit candidate. Awaiting Marcel's look at `compare.html`.

- **2026-11-17** — Smoothness/paint test on the guard: the sheet is faceted too; subdivision and paint don't close
  the gap (form does). Awaiting Marcel: form pass, image-to-3D spike, or move on.

- **2026-11-17** — Marcel asked how close to the sheet we can get (90 %?): estimate 75–80 % procedurally; next
  session runs the subdivision test and the paint test on the guard (start-here list).

- **2026-11-17** — ump: PROGRESS start-here rewritten for Tinfox (guard done, next: guard in the game).

- **2026-11-17** — 2H stance: shoulders forward, arms in front of the chest. Tinfox style + guard committed + pushed.

- **2026-11-17** — Guard shoulders follow the arms (blended pad weights, pre-tilted).

- **2026-11-17** — 2H stance (arms forward), hero-m shoulders 0.25 / arm 0.53; trousers into the boots.

- **2026-11-17** — Guard face: smaller ears, no nostrils, wider nose tip, thin brown smile (9 colours).

- **2026-11-17** — Guard boots smaller (Marcel).

- **2026-11-17** — Guard face fixes: ears rooted in the head, solid nose (Marcel). 5,730 tris.

- **2026-11-17** — Guard v6: ears (rim + bowl + lobe), rounded nose with wings, squarer chin. 5,730 tris.

- **2026-11-17** — Guard back on mittens (Marcel); 5,090 tris.

- **2026-11-17** — Guard v5: face rebuilt (profile, eyes, brows, nose, smirk, ears), gloves with fingers. 5,474 tris.

- **2026-11-17** — Tinfox budget → hard 8,000; guard v4 (more sides, 4,746 tris): barely visible vs v3.

- **2026-11-17** — Guard v3: V-shaped chest. Awaiting Marcel.

- **2026-11-17** — Guard v2 (chest, hips, shoulder pads on the torso, sole). 3,826 tris. Awaiting Marcel.

- **2026-11-17** — Tinfox guard v1: 9 parts, 3,746 tris, 14 clips, exported. Awaiting Marcel's look.

- **2026-11-17** — Style `tinfox` + `hero-m` template from the guard sheet; guard spec + reference. 75 tests.

- **2026-11-17** — Tinfox shooter clips OK'd by Marcel (baked_layered sheet). Next: style `tinfox` + guard.

- **2026-11-17** — Tinfox started: shooter clips (aim/shoot 1H/2H arms-only baked, crouch, crouch walk), opt-in
  `spec.extra_clips`, arms-only channels in the GLB. 71 tests pass. Next: style `tinfox` + guard.

- **2026-11-17** — Cast sheet of all 8 lowpoly characters for the Heerschar agent (`workspace/_catalog/lowpoly/cast.png`).

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
