"""QA tools: stats, render_preview, validate."""
from __future__ import annotations

from .. import character as C
from ..blender import run_job
from ..paths import character_dir


def stats(name: str) -> dict:
    return run_job("stats", {"spec": C.load_spec(name)}, blend=C.require(name))


def render_preview(name: str, views: list[str] | None = None, pose: str = "rest") -> dict:
    out = character_dir(name) / "renders" / ("preview" if pose == "rest" else pose.replace("@", "_"))
    args = {"out_dir": str(out), "pose": pose}
    if views:
        args["views"] = views
    return run_job("render_preview", args, blend=C.require(name))


def validate(name: str) -> dict:
    return run_job("validate", {"spec": C.load_spec(name)}, blend=C.require(name))
