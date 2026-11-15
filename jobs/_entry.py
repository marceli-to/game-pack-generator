"""Entry point for every job:  blender -b [file.blend] -P jobs/_entry.py -- <job> <args.json> <result.json>

Checks the pinned Blender version, runs jobs/<job>.py:run(args) and writes the result JSON.
"""
import importlib
import os
import json
import sys
import traceback
from pathlib import Path

JOBS = Path(__file__).resolve().parent
sys.path.insert(0, str(JOBS))

import bpy  # noqa: E402

from lib import style as style_lib  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    job, args_path, result_path = argv[0], Path(argv[1]), Path(argv[2])
    result = {"ok": False, "outputs": [], "stats": {}, "previews": [], "warnings": []}
    try:
        style = style_lib.load()
        want = os.environ.get("GPG_PIN_BLENDER_OVERRIDE") or style["blender"]["version"]  # override: tests only
        have = ".".join(str(v) for v in bpy.app.version)
        if have != want:
            raise RuntimeError(f"Blender {have} does not match the pinned version {want} (core.json)")
        args = json.loads(args_path.read_text())
        module = importlib.import_module(job)
        out = module.run(args) or {}
        result.update(out)
        result.setdefault("ok", True)
        if "ok" not in out:
            result["ok"] = True
    except Exception as e:  # noqa: BLE001 - report everything back to the caller
        result["ok"] = False
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()
    result_path.write_text(json.dumps(result, indent=1, default=str))


main()
