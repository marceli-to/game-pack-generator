"""Animation tools: apply_animations, pose_test (STYLE.md §7a, §8, §8a)."""
from __future__ import annotations

from .. import character as C
from ..blender import run_job
from ..paths import character_dir


def apply_animations(name: str) -> dict:
    """Add the library clips to workspace/<name>/character.blend (re-run after every assemble_from_parts)."""
    blend = C.require(name)
    C.require_character(name)
    return run_job("apply_animations", {"spec": C.load_spec(name) or {}, "out": str(blend)},
                   blend=blend, style=C.style_of(name))


def pose_test(name: str, clips: list[str] | None = None) -> dict:
    blend = C.require(name)
    C.require_character(name)
    args = {"spec": C.load_spec(name) or {}, "out_dir": str(character_dir(name) / "renders" / "pose_test")}
    if clips:
        args["clips"] = clips
    return run_job("pose_test", args, blend=blend, style=C.style_of(name), timeout=600)
