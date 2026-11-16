# SPIKE.md — Avatar Tool: Route Comparison

> **Status: archived until Phase 6.** Its "After the spike" outline is superseded by PLAN.md.

> **Status: postponed.** The tool starts with the procedural route. Run this spike only before adding the image route (PLAN.md, Phase 6).

> **Notes for when this is revived (2026-11-16):**
> - **Turnaround generation: FLUX.1 [schnell]** (Apache 2.0, ~4 steps, fits the 64 GB M4 Max) — stronger than SDXL at
>   clean, consistent multi-view sheets and prompt adherence. Also useful *before* Phase 6: generated sheets as
>   `add_reference` / `compare_reference` input for the procedural route, so a pack doesn't need a hand-drawn sheet per character.
> - **Licence caveat:** FLUX.1 [dev], BFL's own depth/redux models and most Flux ControlNets/adapters are under the
>   non-commercial dev licence → check each one; packs are commercial CC0. Use only Apache/MIT-licensed parts.
> - **Image-to-3D can run locally** now (Marcel prefers local): open models such as TRELLIS (MIT) instead of
>   Tripo/Meshy. Check licence and Apple Silicon (MPS) support before relying on one.
> - The cost is still the cleanup (dense, unrigged, baked-texture meshes → budget, roles, palette/paint, skeleton), so §4 stays the core of the test.

## Goal
Find out which route produces Kenney-like characters with less effort:

- **Route A — Image-to-3D + cleanup:** generated turnaround → image-to-3D service → automated cleanup in headless Blender
- **Route B — Procedural:** generated turnaround as reference only → agent builds the character from primitives in headless Blender

Timebox: one afternoon (~4 h). Output is a decision, not a product.

---

## 0. Setup (30 min)

- Install Blender (latest stable). Verify headless: `blender -b --python-expr "import bpy; print(bpy.app.version_string)"`
- Project folder:
  ```
  avatar-spike/
    STYLE.md
    reference/        # generated images
    route-a/          # raw + cleaned meshes, scripts
    route-b/          # build scripts, meshes
    renders/          # preview PNGs
    shared/           # palette.png, render + export helpers
    RESULTS.md
  ```
- Create `shared/palette.png`: 8×8 px, 16–32 flat colours (Kenney-style colour palette texture).
- Account / API key for one image-to-3D service (Tripo or Meshy — hosted, no local GPU needed). Check current pricing and whether it offers a low-poly / stylised mode.

## 1. Style spec — `STYLE.md` (20 min)

Minimal version, enough for the spike:

- Budget: ≤ 1,000 tris per character
- Height: 1.8 units (1 unit = 1 m), origin at feet, facing −Y (Blender) → +Z forward in glTF
- Materials: one material, UVs mapped to palette cells; no gradients, no baked lighting
- Proportions: stylised, ~3–4 heads tall, chunky hands/feet, readable silhouette
- Pose: A-pose
- Export: GLB, +Y up, applied transforms, no unused data

## 2. Reference image (20 min)

- Pick **one** character: simple but with personality (e.g. a knight or adventurer with a helmet, a belt and one accessory).
- Generate a turnaround: front, side, back on one sheet or as separate images. A-pose, neutral lighting, plain background, flat colours, low-poly game-asset look.
- Save to `reference/`. Same images for both routes.

## 3. Shared helpers (30 min)

Agent writes these once in `shared/`:

- `render_preview.py <in.glb> <out_dir>` — headless Workbench/Eevee render: front, side, back, 3/4 view, flat lighting, 512 px. Plus one sheet with the reference next to the renders.
- `stats.py <in.glb>` — tris, verts, materials, bounding box height, non-manifold edges.
- `export_glb.py` — applies transforms, exports to the STYLE.md settings.
- Validate every GLB with the Khronos glTF validator.

## 4. Route A — Image-to-3D + cleanup (60 min)

1. Upload the reference to the image-to-3D service (use the low-poly mode if available). Save the raw output to `route-a/raw.glb`.
2. Cleanup script `route-a/cleanup.py` (headless):
   - import, apply transforms, scale to 1.8 units, origin at feet
   - voxel remesh (fix holes/overlaps) → decimate to ≤ 1,000 tris
   - recolour: sample the original texture per face → snap to nearest palette colour → reassign UVs to palette cells → delete the original texture
   - recalculate normals, flat shading
3. Export `route-a/character.glb`, render previews, run stats.
4. Agent compares renders with the reference and lists differences. **Max. 2 correction rounds.**

## 5. Route B — Procedural (60 min)

1. Agent analyses the reference: proportions (head/torso/legs ratio), main shapes, colour list → writes `route-b/spec.json`.
2. Build script `route-b/build.py`: a separate function per body part (head, torso, arms, legs, hands, feet, accessories) from primitives (cubes, cylinders, bevels, simple extrusions), then joined into one mesh with palette UVs.
3. Export `route-b/character.glb`, render previews, run stats.
4. Agent compares renders with the reference and lists differences. **Max. 2 correction rounds.**

Same rule for both routes: same timebox, same number of correction rounds, no manual modelling.

## 6. Evaluation (30 min)

Put both preview sheets side by side (plus a Kenney character for scale) and score each 1–5 in `RESULTS.md`:

| Criterion | Route A | Route B |
|---|---|---|
| Resemblance to reference | | |
| Charm / appeal (Marcel's judgement) | | |
| Silhouette readability | | |
| Kenney-style look (flat, chunky, clean) | | |
| Topology (tris, manifold, clean edges) | | |
| Suitability for rigging (joint edge flow, A-pose) | | |
| Repeatability (would a second run look the same?) | | |
| Cost per character (API cost, agent time) | | |

Also record what broke, where the agent got stuck, and what it would take to get to 90 %.

## 7. Decision

- **A clearly better:** next phase = robust cleanup pipeline + auto-rig onto the standard skeleton
- **B clearly better:** next phase = parts library + parameter presets + shared skeleton
- **Mixed (likely):** hybrid — A for shape and charm, B's tools for cleanup, colours and parts (e.g. procedural body + image-to-3D heads/accessories)

---

## After the spike (outline only)

1. Full `STYLE.md` + standard skeleton + animation set (idle, walk, run, attack, die)
2. Blender MCP server exposing the chosen pipeline as tools (`create_character`, `render_preview`, `rig`, `export`)
3. Batch run: 5 characters → consistency check across a set
4. Use it in a real game project

## Out of scope for the spike
Rigging, animation, an MCP server, multiple characters, textures beyond the palette.
