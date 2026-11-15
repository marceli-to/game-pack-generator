# game-pack-generator

Headless tool that lets agents create low-poly, rigged, animated game characters in a flat, chunky, Kenney-like style, and package them as CC0 asset packs (GLB for three.js).

- Blender (headless) does the work; a thin MCP server (Python, FastMCP) is the interface.
- [`PLAN.md`](PLAN.md): architecture, tools, phases
- [`STYLE.md`](STYLE.md): binding visual and technical spec
- [`SPIKE.md`](SPIKE.md): image-to-3D route comparison (archived until Phase 6)

## Requirements
- Blender **5.2.4 LTS** (pinned; the runner refuses other versions) — path via `BLENDER_BIN`, macOS default `/Applications/Blender.app/Contents/MacOS/Blender`
- Python 3.11+
- Node 20+ (glTF validator, Playwright test load)

## Licence
Tool code: MIT (see `LICENSE`). Generated packs: CC0.
