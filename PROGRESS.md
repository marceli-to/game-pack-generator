# PROGRESS.md

Living status of the project. **Read this first in every session; update it before ending one**
(what changed, decisions, next step). Keep it short: details belong in PLAN.md / STYLE.md / git history.

_Last updated: 2026-11-15 — Painted spike done (uncommitted). Marcel picked **auto** paint (projection optional for hero characters)._

---

## Where we are

| Phase (PLAN.md) | Status |
|---|---|
| 1 — Foundations: wrapper, QA, skeleton, proportions | ✅ done (`ea6705e`) |
| 2 — First static character (the mage) | ✅ done, mage approved 2026-11-15 (`21656d4`) |
| 3 — Skinning & animation | after the painted spike |
| 4 — Parts library | — |
| 5 — Packs & batch | — |
| 6 — Integration & extensions (image route, props, …) | — |

### Phase 1 delivered
- MCP server `server/main.py` (stdio, registered in `.mcp.json`): `get_style`, `init_character`, `import_glb`, `stats`, `render_preview`, `validate`, `export`.
- One headless Blender process per job (`server/blender.py` → `jobs/_entry.py` → `jobs/<job>.py`); JSON args/result files; refuses any Blender other than the pinned version.
- `validate` implements the STYLE.md §12 rules (hard/soft/info). Not yet checked: edge loops at joints, foot contact (both Phase 3, `pose_test`).
- `export`: GLB + Khronos glTF validator + headless three.js test load (Playwright, `viewer/viewer.html`).
- `library/`: `palette.png`, `skeleton.blend` (KayKit Rig_Medium + `headslot`/`backslot`), `animations.blend` (8 clips), `proportions/human.json` (+ preview), `CREDITS.md`. Rebuilt by `python -m server.build_library --source <KayKit folder>`.
- 33 pytest tests; fixtures (mannequin + planted defects) are generated at run time by `jobs/make_mannequin.py`.

### Phase 2 delivered
- New MCP tools: `add_reference`, `build_part`, `list_parts`, `render_parts_catalog`, `assemble_from_parts`, `apply_palette`, `recolor`, `compare_reference` (15 tools total).
- Part builder API (`jobs/lib/parts.py`, `P.loft/ring/rect/box/cylinder/mirror_x/transform/set_role/set_bone`) + part checks (STYLE.md §9a). Parts in `library/parts/<slot>/` with their build script (`.py` = source of truth), meta and preview.
- `compare_reference`: reference crops / same-scale renders / silhouette overlay + IoU per view; arms lowered for A-pose drawings (`spec.compare.arms_down_deg`), staff hidden (`hide_slots`).
- Mage: `specs/mage/spec.json`, 10 parts, **2,380 tris** (v2, rounder: 12–19-sided rings, bevelled boxes via `P.rbox`; smooth by angle 40°), 8 colours, height 1.80 m, `validate` clean (no hard, no soft), IoU front 0.84 / side 0.85 / back 0.81, GLB passes glTF validator (0/0) and three.js test load (no clips yet).
- 46 pytest tests (incl. `test_mage_approval_still_valid`).
- Viewer default look: soft room lighting + neutral tone mapping (`?look=basic` for the old one); `testload.mjs` takes an extra viewer query.

### Style profiles (committed after `21656d4`, see git log)
- One look = one **style**: `styles/<name>/` with `STYLE.md` ↔ `style.json` (archetypes, budget, shading, surface, palette, parts, previews), `proportions/`, `parts/`, `palette.png`. Shared rules: root `STYLE.md` ↔ `core.json` (skeleton, roles, slots, topology, animations, export, approval). Section numbers are the same in both.
- Loader merges core + style (`server/style.py`, `jobs/lib/style.py`); `run_job(..., style=)` → env `GPG_STYLE`. `spec.style` picks it; specs without one use `core.json` `default_style` (`clean`). Part tools and `get_style` take `style=`.
- Current look moved to `styles/clean` (mage unchanged, approval still valid). 49 tests.

## Painted-style spike (built 2026-11-15, uncommitted; decided: auto)

- **`styles/painted/`** (draft): STYLE.md ↔ style.json; surface `painted`; archetype **`chibi`** (1.0–1.4 m, ≈ 3 skull-heights);
  budget 4,000–6,000 (hard 8,000), head ≤ 1,800 / 2,500; mid-tone palette (base colours per role); `paint` config
  (`auto` light/AO/crease/noise + per-role treatments, `projection` weights). Root STYLE.md table lists it as "spike".
- **`chibi` template** (`styles/painted/proportions/chibi.json`), calibrated on the knight sheet at 0.00177 m/px
  (1.2 m body, skull top and hips estimated). Mannequin vs sheet IoU 0.77 / 0.73 / 0.80 (arms_down 67°); fits well.
  Factors vs KayKit: leg 0.71, torso 0.61, arm 0.52, head 1.63 (short limbs: watch the clips in Phase 3).
- **Parts** `head-skull` (884 tris) + `headwear-helmet-kettle` (1,180) in `styles/painted/parts/`; head group 2,064.
  New builder primitive **`P.shell(grid, thickness, role, cyclic=…)`**: thick sheet from a point grid (plates, guards,
  bands; later capes/tunics).
- **`paint_surface` job** (`jobs/paint_surface.py`, `jobs/lib/paint.py`): smart-UV unwrap → numpy texel map
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
  output `workspace/knight-spike/overlay.png`) → band 5 cm tall with front/back V points and a 4.8 cm tilt, cheek-guard gold
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
- **Proposed, awaiting Marcel's OK:** painted characters export **unlit** (`KHR_materials_unlit`, light lives in the
  texture); a lit export (less painted light) later as a per-pack option.

Next: make auto paint look closer to the art (bolder, larger-scale painterly treatments; tune on the knight
against the sheet), then the `painted` surface properly (MCP tool, validate/export rules, approval), finish the
knight (body parts), then Phase 3 (skinning & animation).

## Decisions (with reasons)

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
- Reference images in the repo only when Marcel says they're his to publish (the mage is).
- **Style profiles** (Marcel, 2026-11-15): packs may need different looks (clean now, painted next, others later). The shared pipeline (skeleton, roles, parts mechanics, QA, export) stays one; the look is a folder. Roles are the bridge: palette colour in `clean`, material treatment in `painted`.
- The mage spec has no `style` key (adding one would change its hash and void the approval) → it relies on `default_style = clean`. Add `"style": "clean"` at the next re-approval.

## Environment & gotchas

- **Blender 5.2.4 LTS** at `/Applications/Blender.app/Contents/MacOS/Blender` (installed from blender.org; Homebrew here is Intel/Rosetta and the cask is arm-only). Override with `BLENDER_BIN`.
- **Python:** use `/opt/homebrew/bin/python3.13` (arm64) for `.venv`. The Intel `/usr/local` Python can't build the MCP SDK's `cryptography`.
- **MCP SDK is 2.x:** `from mcp.server.mcpserver import MCPServer` (FastMCP was renamed).
- **Blender 5 actions are layered** (slots/channelbags): use `jobs/lib/scene.py` helpers (`action_fcurves`, `assign_action`), not `action.fcurves`.
- **glTF importer** adds bone display shapes (icosphere) → `import_glb` removes them; glTF can't carry face attributes, so imported GLBs always fail `no_role`.
- **Export** unparents the mesh from the armature for the session (validator: `NODE_SKINNED_MESH_NON_ROOT`).
- **KayKit source** is not in the repo (only the built `.blend`s). Download "Free 1.1" from https://kaylousberg.itch.io/kaykit-character-animations to rebuild the library.

## Commands

```sh
.venv/bin/python -m pytest -q                       # all tests (~45 s)
.venv/bin/python -m server.build_library --source <KayKit_Character_Animations_1.1>
.venv/bin/python -m server.main                     # MCP server (stdio); Claude Code uses .mcp.json
npm install --prefix node && npx --prefix node playwright install chromium
```

## Log

- **2026-11-15** — Marcel picked auto paint for `painted` (projection optional).
- **2026-11-15** — Knight head fitted to the sheet (v2 parts) for a fair projection test.
- **2026-11-15** — Spike fixes: UV overlap repair (black bars), conservative raster, 3× z-buffer, facing power 4.
- **2026-11-15** — Painted spike: `styles/painted` (draft), `chibi` template, knight skull + kettle helmet, `P.shell`, `paint_surface` job (auto vs projection), comparison sheet. 52 tests pass. Uncommitted.
- **2026-11-15** — Phase 2 committed + pushed (`21656d4`). Style profiles refactor (`core.json` + `styles/clean/`) committed + pushed. Session ends here; next session starts the painted spike.
- **2026-11-15** — Staff switched to upright grip; mage approved by Marcel (spec + part hashes in `specs/mage/spec.json`). Phase 2 done.
- **2026-11-15** — Shading switched to smooth by angle 40°; viewer gets soft lighting by default; head/beard corners at 30° steps (2,380 tris).
- **2026-11-15** — Budget raised to 1,500–2,500 tris; builder got `P.rrect`/`P.rbox`; mage parts reworked (2,364 tris).
- **2026-11-15** — Phase 2 built: part builder + 8 tools, mage assembled from 10 parts (990 tris, IoU ≈ 0.85), awaiting approval.
- **2026-11-15** — Plan + style spec reviewed and revised (roles, archetypes, proportion templates, CC0 animation library). Repo created, Blender 5.2.4 pinned. Animation libraries compared (retarget test) → KayKit. Phase 1 built and pushed; `human` template calibrated on the mage reference and approved.
