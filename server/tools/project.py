"""Project & reference tools: init_character, get_style, import_glb."""
from __future__ import annotations

from pathlib import Path

from .. import character as C
from ..blender import run_job
from ..style import load_style


def init_character(name: str, spec: dict | None = None, overwrite: bool = False) -> dict:
    C.check_name(name)
    blend = C.blend_path(name)
    if blend.exists() and not overwrite:
        raise C.CharacterError(f"character {name!r} already exists (pass overwrite=true to replace it)")
    spec = dict(spec or {})
    spec.setdefault("name", name)
    spec.setdefault("archetype", load_style()["default_archetype"])
    if spec["archetype"] not in load_style()["archetypes"]:
        raise C.CharacterError(f"unknown archetype {spec['archetype']!r}")
    C.save_spec(name, spec)
    r = run_job("init_character", {"out": str(blend)})
    r["outputs"] = [str(blend), str(C.spec_path(name))]
    r["stats"] = {"spec_hash": C.spec_hash(spec)}
    return r


def get_style() -> dict:
    return load_style()


def import_glb(name: str, path: str, normalize: bool = False) -> dict:
    blend = C.require(name)
    p = Path(path).expanduser().resolve()
    if not p.exists() or p.suffix.lower() not in (".glb", ".gltf"):
        raise C.CharacterError(f"not a .glb/.gltf file: {p}")
    return run_job("import_glb", {"path": str(p), "out": str(blend), "normalize": normalize}, blend=blend)
