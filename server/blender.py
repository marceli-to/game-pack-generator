"""Run one bpy job in a fresh headless Blender process.

Every job gets its args as a JSON file and writes its result as a JSON file
(stdout is too noisy to parse reliably). Result shape:
    { ok, outputs: [...], stats: {...}, previews: [...], warnings: [...], error? }
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from .paths import JOBS, blender_bin
from .style import style_name


class BlenderError(RuntimeError):
    pass


def run_job(job: str, args: dict | None = None, blend: str | Path | None = None,
            timeout: float = 180.0, style: str | None = None) -> dict:
    """Run jobs/<job>.py inside Blender. Opens `blend` first if given. `style` selects the style the
    job sees (default: GPG_STYLE / core.json default_style)."""
    if not (JOBS / f"{job}.py").exists():
        raise BlenderError(f"unknown job: {job}")
    with tempfile.TemporaryDirectory(prefix="gpg-") as tmp:
        args_path = Path(tmp) / "args.json"
        result_path = Path(tmp) / "result.json"
        args_path.write_text(json.dumps(args or {}))
        cmd = [blender_bin(), "-b", "--factory-startup"]
        if blend is not None:
            cmd.append(str(blend))
        cmd += ["--python-exit-code", "1", "-P", str(JOBS / "_entry.py"), "--",
                job, str(args_path), str(result_path)]
        t0 = time.monotonic()
        try:
            env = {**os.environ, "GPG_STYLE": style_name(style)}
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired as e:
            raise BlenderError(f"job {job} timed out after {timeout}s") from e
        except FileNotFoundError as e:
            raise BlenderError(f"Blender not found at {cmd[0]} (set BLENDER_BIN)") from e
        elapsed = round(time.monotonic() - t0, 2)
        if result_path.exists():
            result = json.loads(result_path.read_text())
        else:
            tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-30:])
            result = {"ok": False, "error": f"job {job} produced no result (exit {proc.returncode})", "log": tail}
        result.setdefault("outputs", [])
        result.setdefault("stats", {})
        result.setdefault("previews", [])
        result.setdefault("warnings", [])
        result["elapsed_s"] = elapsed
        return result


def run_job_checked(job: str, args: dict | None = None, blend: str | Path | None = None,
                    timeout: float = 180.0, style: str | None = None) -> dict:
    result = run_job(job, args, blend, timeout, style)
    if not result.get("ok"):
        raise BlenderError(result.get("error", "job failed") + ("\n" + result["log"] if result.get("log") else ""))
    return result
