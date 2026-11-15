# PROGRESS.md

Living status of the project. **Read this first in every session; update it before ending one**
(what changed, decisions, next step). Keep it short: details belong in PLAN.md / STYLE.md / git history.

_Last updated: 2026-11-15 — Phase 1 done, Phase 2 not started._

---

## Where we are

| Phase (PLAN.md) | Status |
|---|---|
| 1 — Foundations: wrapper, QA, skeleton, proportions | ✅ done (`ea6705e`) |
| 2 — First static character (the mage) | ⏭ next |
| 3 — Skinning & animation | — |
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

## Next step: Phase 2 — the mage as a static GLB

Target: `specs/mage/reference/turnaround.webp` (Marcel's own image, OK to publish). Done when the mage goes from reference to GLB with no manual modelling and Marcel approves it.

To build (PLAN.md tool list):
1. `add_reference(name, images)` — store/crop the turnaround (front/side/back) into the character workspace.
2. `build_part(name, slot, archetype, script)` — agent-written bpy snippet → part `.blend` in `library/parts/<slot>/`, validated: per-face `role` set, fits the `human` template (joints + volume guides), manifold, budget.
3. `assemble_from_parts(name, spec)` — template → skeleton → parts attached to bones, join to `Character`, write `role` + `slot` face attributes, rigid weights per part.
4. `apply_palette(name)` / `recolor(name, role, index)` — `jobs/lib/palette.py:apply_roles` already exists.
5. `render_parts_catalog(slot?)`.
6. `compare_reference(name)` — reference vs render at the same scale (fixed framing already supported: `render_preview` arg `frame`; scale of the mage sheet: skull top y=260, floor y=1003 → 743 px = 1.80 m).
7. Mage spec in `specs/mage/spec.json`; parts needed: head, hair/beard, headwear (wizard hat), torso (robe), arms (wide sleeves), hands, legs/feet (boots), accessory_hand_r (crystal staff), belt + pouch.

Open questions for Phase 2:
- Robe: one long torso part over the legs (static is fine) — skinning approach decided in Phase 3.
- Beard: its own slot (`face`?) or part of `hair`? STYLE.md §9 slots don't name it yet.

## Decisions (with reasons)

- **Procedural route first**; image-to-3D postponed (SPIKE.md archived until Phase 6).
- **three.js / GLB only**; tool code MIT, packs CC0.
- **Animations: KayKit Character Animations 1.1, `Rig_Medium`** (CC0). Chosen after a retarget test over Quaternius (site licence since 2026-08-28 forbids redistribution in asset packs) and Kenney (too few clips). Its rig is the standard skeleton.
- **T-pose rest** (matches the library rig; clips play unchanged).
- **Clip lengths from the source clip**; location keys kept and scaled per segment (STYLE.md §7a).
- **Colour = per-face `role`** (+ `slot` attribute after assembly); spec maps roles → palette indices. 8-colour rule counts indices actually used.
- **Body height** = floor to top of the head mesh, without hair/headwear; ranges per archetype.
- **`human` template** calibrated on the blue-wizard reference: 1.80 m, 4.4 heads; hips (0.82) and ankles (0.12) estimated (hidden by the robe). Approved by Marcel 2026-11-15.
- **Approval** binds to the spec hash (STYLE.md §14).
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

- **2026-11-15** — Plan + style spec reviewed and revised (roles, archetypes, proportion templates, CC0 animation library). Repo created, Blender 5.2.4 pinned. Animation libraries compared (retarget test) → KayKit. Phase 1 built and pushed; `human` template calibrated on the mage reference and approved.
