# game-pack-generator

Headless Blender + MCP tool for Kenney-style low-poly characters. Current state and next step:

@PROGRESS.md

## Rules
- **STYLE.md is the law.** Tools read constants from `style.json`, never hardcode them. Change STYLE.md first, then `style.json`; `tests/test_style_sync.py` checks they agree.
- Every bpy operation is a job in `jobs/` run through `server/blender.py`; shared bpy code lives in `jobs/lib/`.
- Run `.venv/bin/python -m pytest -q` before saying something works.
- **Update PROGRESS.md before ending a session** or after a milestone: status table, decisions (with the reason), next step, one log line.
- Commit or push only when Marcel asks.
