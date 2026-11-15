# game-pack-generator

Headless tool that lets agents create low-poly, rigged, animated game characters in a flat, chunky, Kenney-like style, and package them as CC0 asset packs (GLB for three.js).

- Blender (headless) does the work; a thin MCP server (Python, MCP SDK 2.x `MCPServer`) is the interface.
- [`PROGRESS.md`](PROGRESS.md): current status, decisions, next step — read first
- [`PLAN.md`](PLAN.md): architecture, tools, phases
- [`STYLE.md`](STYLE.md): binding shared spec (skeleton, roles, slots, export, approval) — `core.json` is its machine-readable twin
- [`styles/`](styles/): one folder per look (`clean`: the mage), each with its own `STYLE.md` + `style.json`, templates and parts
- [`SPIKE.md`](SPIKE.md): image-to-3D route comparison (archived until Phase 6)

## Requirements
- Blender **5.2.4 LTS** (pinned; the runner refuses other versions) — path via `BLENDER_BIN`, macOS default `/Applications/Blender.app/Contents/MacOS/Blender`
- Python 3.11+ (on Apple Silicon use a native arm64 Python, e.g. `/opt/homebrew/bin/python3.13`; an Intel/Rosetta Python can't install the MCP SDK's dependencies)
- Node 20+ (Khronos glTF validator, Playwright test load)

## Setup
```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install --prefix node && npx --prefix node playwright install chromium
```

The built library (`library/skeleton.blend`, `animations.blend`) and each style's `palette.png` and `proportions/` are committed. To rebuild it from the KayKit download ([KayKit Character Animations 1.1](https://kaylousberg.itch.io/kaykit-character-animations), free, CC0):
```sh
.venv/bin/python -m server.build_library --source ~/Downloads/KayKit_Character_Animations_1.1
```

## Use from Claude Code
`.mcp.json` registers the server (`.venv/bin/python -m server.main`, stdio). Phase 1 tools:

| Tool | What it does |
|---|---|
| `get_style(style?)` | returns the merged style (`core.json` + `styles/<style>/style.json`) |
| `init_character(name, spec?)` | `workspace/<name>/` with `character.blend` + `spec.json` |
| `import_glb(name, path, normalize?)` | imports a GLB into the character |
| `stats(name)` | tris, height (without hair/headwear), palette colours, topology, skeleton, … |
| `render_preview(name, views?, pose?)` | turnaround sheet (front/side/back/¾), optionally posed (`walk@8`) |
| `validate(name)` | every STYLE.md §12 rule → `hard[]`, `soft[]`, `info[]` |
| `export(name)` | GLB + Khronos validator + headless three.js test load (plays `idle`, screenshot) |

Every tool runs one headless Blender process and returns `{ ok, outputs, stats, previews, warnings, error? }`.

## Viewer
`viewer/viewer.html`: open it in a browser (it loads three.js from unpkg), then drop a `.glb` on it or pass `?model=<url>&anim=walk`.

## Tests
```sh
.venv/bin/python -m pytest -q
```
Blender tests build their fixtures (a mannequin on the standard skeleton, plus copies with planted defects) at run time; nothing binary lives in `tests/`.

## Licence
Tool code: MIT (see `LICENSE`). Generated packs: CC0. Skeleton and animations: KayKit by Kay Lousberg, CC0 (see `library/CREDITS.md`).
