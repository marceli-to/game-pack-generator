"""Run the Node-side checks (glTF validator, Playwright test load)."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .paths import NODE


class NodeError(RuntimeError):
    pass


def _run(script: str, *args: str, timeout: float = 120) -> dict:
    node = shutil.which("node")
    if node is None:
        raise NodeError("node not found on PATH")
    if not (NODE / "node_modules").exists():
        raise NodeError("Node deps missing: run `npm install --prefix node`")
    proc = subprocess.run([node, str(NODE / script), *args], capture_output=True, text=True,
                          timeout=timeout, cwd=NODE)
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith("{")]
    if not lines:
        raise NodeError(f"{script} failed (exit {proc.returncode}): {proc.stderr.strip()[-2000:]}")
    return json.loads(lines[-1])


def gltf_validate(glb: Path) -> dict:
    return _run("validate.mjs", str(glb))


def test_load(glb: Path, screenshot: Path, anim: str = "idle") -> dict:
    return _run("testload.mjs", str(glb), str(screenshot), anim, timeout=180)
