"""Run the AI-texture generator (ai/gen.py) in its own environment (ai/.venv, torch + diffusers).
Same contract as the Blender jobs: JSON args in, JSON result out."""
from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path

from .paths import AI, ai_python


class AIError(RuntimeError):
    pass


def available() -> bool:
    return Path(ai_python()).exists()


def run_gen(args: dict, timeout: float = 1800.0) -> dict:
    if not available():
        raise AIError(f"AI environment not found at {ai_python()}: set it up with "
                      "`python3.13 -m venv ai/.venv && ai/.venv/bin/pip install -r ai/requirements.txt` "
                      "(or set GPG_AI_PYTHON)")
    with tempfile.TemporaryDirectory(prefix="gpg-ai-") as tmp:
        a, r = Path(tmp) / "args.json", Path(tmp) / "result.json"
        a.write_text(json.dumps(args))
        t0 = time.monotonic()
        try:
            proc = subprocess.run([ai_python(), str(AI / "gen.py"), str(a), str(r)],
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            raise AIError(f"AI generation timed out after {timeout}s") from e
        if r.exists():
            result = json.loads(r.read_text())
        else:
            tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-30:])
            result = {"ok": False, "error": f"ai/gen.py produced no result (exit {proc.returncode})", "log": tail}
        result["elapsed_s"] = round(time.monotonic() - t0, 2)
        return result
