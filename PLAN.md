# PLAN.md — Headless Avatar Tool for Agents

## Goal
A headless tool that lets agents create low-poly, rigged, animated game characters in the style of Kenney packs. No UI. Blender (headless) is the engine. A thin MCP server is the interface. `STYLE.md` defines the look and the technical rules. Every output is checked automatically and approved by a human.

**Input:** generated reference images (turnaround: front, side, back) and/or a character spec (JSON)
**Output:** asset packs like Kenney's: GLB (for three.js), one palette texture, preview images, manifest, licence

## Decisions
- **Target engine:** three.js (GLB only). FBX/OBJ only if needed later.
- **Generation route:** procedural first (parts + parameters in Blender). No API keys, no costs, deterministic. Image-to-3D comes later as an optional extension (Phase 6).
- **Licence:** open source. Tool code under MIT, generated packs CC0 (like Kenney).
- **Spike (`SPIKE.md`):** postponed. Only becomes relevant when image-to-3D is added.
- **Animations:** from a CC0 animation library; its skeleton becomes the standard skeleton (STYLE.md §8).
- **Colours:** parts carry per-face roles, the spec maps roles to palette colours (STYLE.md §4).
- **Height:** body height without headwear, range per archetype (STYLE.md §2a).

## Principles
1. **Blender does the work, the wrapper stays thin.** No custom 3D engine; every operation is a `bpy` script.
2. **STYLE.md is the law.** Every tool reads its constants (budget, scale, palette, skeleton) from `style.json` (generated from STYLE.md), never hardcoded.
3. **The quality ceiling = the base parts.** Agents mostly combine, recolour and adjust parameters; they rarely model from scratch.
4. **Every step produces something visible.** Each tool returns stats + a preview render path, so the agent can see what it did.
5. **Deterministic.** Same spec + same seed → same output. Specs are versioned in git.

---

## Architecture

```
Agent (Claude Code)
   │  MCP (stdio)
   ▼
avatar-mcp  (Python, FastMCP)
   │  spawns per call:  blender -b <file.blend> -P jobs/<job>.py -- <args.json>
   ▼
Blender headless  ──►  workspace/   (.blend files, GLBs, renders)
   │
   └─► later (Phase 6): optional image-to-3D adapter
```

- **One Blender process per tool call** (simple and robust, ~1–2 s overhead). Later optimisation if needed: a persistent Blender process with a socket server.
- Each job script gets JSON args and returns JSON on stdout: `{ ok, outputs: [...], stats: {...}, previews: [...], warnings: [...] }`.
- Work state lives in `.blend` files per character; every tool call reads and writes a file → no hidden state, easy to undo (git or versioned files).
- Blender path via env var `BLENDER_BIN`.

### Repo structure
```
game-pack-generator/
  STYLE.md                  # human-readable spec
  style.json                # machine-readable constants (generated/kept in sync)
  server/                   # MCP server (Python)
    main.py
    tools/                  # one module per tool group
    blender.py              # subprocess runner, timeout, JSON parsing
  jobs/                     # bpy scripts, one per operation
  library/
    skeleton.blend          # standard rig (adopted from the CC0 animation library)
    animations.blend        # actions: idle, walk, run, … (CC0 source, see CREDITS.md)
    proportions/            # rest-pose joint positions per archetype (human.json, dwarf.json, …)
    parts/                  # base parts per slot (heads, torsos, …)
    palette.png
  specs/                    # character specs (JSON), versioned
  workspace/                # work files (gitignored)
  packs/                    # finished packs
  tests/                    # pytest: each job against fixture files
```

---

## MCP tools

### Project & reference
| Tool | Purpose |
|---|---|
| `init_character(name, spec?)` | creates `workspace/<name>/`, empty .blend, links the style |
| `add_reference(name, images[])` | stores turnaround images, creates a reference sheet |
| `get_style()` | returns style.json (agents read the rules from here) |
| `import_glb(name, path)` | imports an existing GLB into the character's workspace (for checks, references, CC0 parts) |

### Generation (procedural)
| Tool | Purpose |
|---|---|
| `assemble_from_parts(name, spec)` | builds the character: loads the archetype's proportion template, scales bones per `spec.proportions`, attaches parts to their bones |
| `build_part(name, slot, archetype, script)` | creates a new part with an agent-written bpy snippet against the proportion template; must set the per-face `role` attribute (validated) |
| `render_parts_catalog(slot?)` | preview sheet of all parts per slot, so agents can choose visually |

*Later (Phase 6):* `image_to_3d` + `cleanup_mesh` for the image route.

### Colours
| Tool | Purpose |
|---|---|
| `apply_palette(name)` | resolves each face's `role` → `spec.colors` → palette cell, writes UVs |
| `recolor(name, role, palette_index)` | changes one role's colour (for variants), re-applies the palette |

### Rig & animation
| Tool | Purpose |
|---|---|
| `skin(name, method="auto"\|"parts")` | auto weights, or rigid weights per part (more robust for modular characters) |
| `apply_animations(name, set="default")` | links actions from animations.blend |
| `pose_test(name)` | renders extreme poses (arms up, squat, walk-cycle frames) → for checking deformation |

### QA
| Tool | Purpose |
|---|---|
| `stats(name)` | tris, verts, materials, height, non-manifold, bone count, UV outside palette cells |
| `render_preview(name, views?)` | turnaround sheet (front/side/back/¾) as in STYLE.md |
| `compare_reference(name)` | sheet: reference next to render, same views |
| `validate(name)` | checks every rule in style.json → list of violations (hard/soft) |

### Export
| Tool | Purpose |
|---|---|
| `export(name)` | GLB per STYLE.md, Khronos glTF validator, test load: headless Chromium (Playwright) opens `viewer.html`, no console errors, plays `idle`, screenshot |
| `build_pack(pack_name, characters[])` | Kenney-style folder (see below) + overview sheet + manifest |

### Escape hatch
| Tool | Purpose |
|---|---|
| `run_bpy(name, script)` | arbitrary bpy for special cases; runs only on the workspace copy, with a timeout, and is logged. Goal: everything the agent needs repeatedly becomes its own tool. |

### Pack output (Kenney-like)
```
packs/<pack-name>/
  Models/GLB/character-knight.glb
  Textures/palette.png
  Previews/character-knight.png
  Preview.png            # overview sheet of all characters
  manifest.json          # name, tris, bones, animations, spec hash, version
  License.txt            # CC0
  viewer.html            # three.js viewer: all characters, animation switcher
```

---

## Character spec (JSON)

```json
{
  "name": "knight",
  "seed": 42,
  "archetype": "human",
  "proportions": { "head": 1.2, "shoulders": 1.1, "legs": 0.9 },
  "parts": {
    "head": "head-round",
    "hair": null,
    "headwear": "headwear-helmet-visor",
    "torso": "torso-armor",
    "arms": "arms-default",
    "hands": "hands-mitten",
    "legs": "legs-default",
    "feet": "feet-boots-chunky",
    "accessory_back": "accessory_back-cape-short",
    "accessory_hand_r": "accessory_hand_r-sword-short"
  },
  "colors": { "skin": 2, "hair": 9, "primary": 18, "secondary": 52, "accent": 42, "metal": 41, "leather": 45, "eyes": 56, "dark": 55 },
  "reference": ["reference/front.png", "reference/side.png", "reference/back.png"]
}
```

---

## Agent workflow (standard)

1. `get_style` → read the rules
2. `init_character` + `add_reference`
3. Analyse the reference → write the spec (parts, proportions, colours)
4. `render_parts_catalog` → choose parts → `assemble_from_parts`
5. `apply_palette` → `validate` → `compare_reference`
6. Max. 3 correction rounds on the spec or parts, then hand over to a human
7. `skin` → `apply_animations` → `pose_test` (the skeleton is already in place from step 4)
8. **Human approval** (preview + pose sheet)
9. `export` → `build_pack`

---

## Phases

### Phase 1 — Foundations: wrapper, QA, skeleton, proportions (2–3 days)
- MCP server, Blender runner (subprocess, timeout, JSON in and out)
- `init_character`, `get_style`, `stats`, `render_preview`, `validate`, `export`
- style.json from STYLE.md, palette.png, role enum
- **Choose the CC0 animation library**, import its rig as `skeleton.blend` and its clips as `animations.blend`; update STYLE.md §7 bone names to match
- **Proportion template `human.json`**: rest-pose joint positions measured from the rig, adjusted to the target proportions; render it as a stick-figure preview for approval
- pytest: every job against a fixture cube/character
- **Done when:** an agent can import any GLB, check it, render it and export it; the skeleton plays the library's idle/walk in the three.js viewer; the human proportion template is approved.

### Phase 2 — First static character (2–3 days)
- 1–2 parts per slot, built with `build_part` **against the proportion template**, with per-face roles
- `assemble_from_parts`, `render_parts_catalog`, `apply_palette`, `recolor`, `compare_reference`
- **Done when:** the mage from the reference as a static GLB (rest pose), no manual modelling, approved by Marcel.
- Note: the mage is a deliberate stress test (long robe = worst case for skinning in Phase 3). If an easier first win is wanted, build a character in trousers first and the mage second.

### Phase 3 — Skinning & animation (2–4 days)
- `skin` (rigid per part + smooth for the robe/skirt case), `apply_animations` from the library, `pose_test`
- Map the library's clips to the STYLE.md animation names; note gaps
- Minimal three.js viewer (`viewer.html`): load GLB, orbit, switch animations
- **Done when:** the character from Phase 2 animates without visible deformation errors and the GLB plays in three.js.

### Phase 4 — Parts library (ongoing, 1 week to a usable set)
- 3–5 variants per slot, all built against the proportion templates and attachment points
- Second archetype (e.g. `dwarf.json`) to prove the template system
- Optionally adapt Kenney/Quaternius CC0 parts as a base
- Parts preview sheet (`render_parts_catalog`) so agents can choose visually
- **Done when:** 5 different characters from specs only, consistent in style.

### Phase 5 — Packs & batch (1–2 days)
- `build_pack`, overview sheet, manifest
- Batch: list of specs → pack, with a QA report per character
- **Done when:** a pack of 10 characters is used in a game project.

### Phase 6 — Integration & extensions (optional)
- Use it in your own game projects
- **Image route:** run `SPIKE.md`, then `image_to_3d` + `cleanup_mesh` (open-source models like Hunyuan3D/TRELLIS or a hosted API)
- Props/items with the same tools (separate budget in STYLE.md)
- FBX/OBJ export if other engines are needed
- Persistent Blender process for speed
- Variant generator (colour/part permutations from one spec)

---

## Risks
| Risk | Mitigation |
|---|---|
| Characters look generic | invest in base parts; human approval as the gate; Kenney as the visual reference in every comparison sheet |
| Stiff or missing animations | CC0 animation library as the source and its rig as the standard; agents only adapt clips; gaps filled from other CC0 clips on the same rig before any keyframing |
| Deformation at shoulders/hips | parts with prepared edge loops at joints; rigid skinning per part as the fallback |
| Agent gets lost in `run_bpy` | logging; recurring snippets → become dedicated tools |
| Blender API changes | pin one Blender version (current LTS at project start): recorded in README and style.json; the runner checks `bpy.app.version` and refuses to run on a mismatch |

## Open decisions
- CC0 animation library: Quaternius vs. Kenney — comparison of rigs and clip coverage in progress (Phase 1)
