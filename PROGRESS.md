# PROGRESS.md

Living status of the project. **Read this first in every session; update it before ending one**
(what changed, decisions, next step). Keep it short: details belong in PLAN.md / STYLE.md / git history.

_Last updated: 2026-11-15 — Phase 2 done, mage approved by Marcel (uncommitted). Next: Phase 3._

---

## Where we are

| Phase (PLAN.md) | Status |
|---|---|
| 1 — Foundations: wrapper, QA, skeleton, proportions | ✅ done (`ea6705e`) |
| 2 — First static character (the mage) | ✅ done, mage approved 2026-11-15 (uncommitted) |
| 3 — Skinning & animation | ⏭ next |
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

## Next step: Phase 3 — skinning & animation (the mage)

Rebuild the mage: `init_character("mage", <specs/mage/spec.json>)` + `assemble_from_parts("mage")`.

1. `skin`: the long robe is the hard case (rigid per part fails: it spans hips + both legs). Smooth weights hips/upperleg on the robe below the belt; rigid elsewhere.
2. `apply_animations`: clips from `library/animations.blend` + clip mapping for a mage (`attack` → `Ranged_Magic_Shoot`?).
3. **Upright grip** (`spec.grip.accessory_hand_r = "upright"`, STYLE.md §9a): staff weighted to `handslot.r`, slot keeps its rest orientation in every clip (bake: world rotation locked, position follows the hand). Slot bones don't deform today → decide: make `handslot.*` deforming, or a staff-only bone.
4. `pose_test` + edge-loop check at joints + foot contact; viewer plays clips.
5. Re-approval: any spec/part change voids the approval (spec hash + part script hashes).

Open:
- `spec.proportions` ≠ 1 is refused for now (Phase 4).
- Headwear weighted to `head` (fine: `headslot` has no clip keys).

## Decisions (with reasons)

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

- **2026-11-15** — Staff switched to upright grip; mage approved by Marcel (spec + part hashes in `specs/mage/spec.json`). Phase 2 done.
- **2026-11-15** — Shading switched to smooth by angle 40°; viewer gets soft lighting by default; head/beard corners at 30° steps (2,380 tris).
- **2026-11-15** — Budget raised to 1,500–2,500 tris; builder got `P.rrect`/`P.rbox`; mage parts reworked (2,364 tris).
- **2026-11-15** — Phase 2 built: part builder + 8 tools, mage assembled from 10 parts (990 tris, IoU ≈ 0.85), awaiting approval.
- **2026-11-15** — Plan + style spec reviewed and revised (roles, archetypes, proportion templates, CC0 animation library). Repo created, Blender 5.2.4 pinned. Animation libraries compared (retarget test) → KayKit. Phase 1 built and pushed; `human` template calibrated on the mage reference and approved.
