# game-pack-generator

Headless Blender + MCP tool for Kenney-style low-poly characters. Current state and next step:

@PROGRESS.md

## Rules
- **The specs are the law.** Shared rules: `STYLE.md` ↔ `core.json`. Each look is a style: `styles/<name>/STYLE.md` ↔ `styles/<name>/style.json` (+ its templates, parts, palette). Tools read constants from the merged style, never hardcode them. Change the .md first, then the .json; `tests/test_style_sync.py` checks they agree.
- A character's spec names its style (`spec.style`); jobs get it via `run_job(..., style=)` → env `GPG_STYLE`.
- Every bpy operation is a job in `jobs/` run through `server/blender.py`; shared bpy code lives in `jobs/lib/`.
- Run `.venv/bin/python -m pytest -q` before saying something works.
- **Update PROGRESS.md before ending a session** or after a milestone: status table, decisions (with the reason), next step, one log line.
- Commit or push only when Marcel asks.
