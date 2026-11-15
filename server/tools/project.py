"""Project & reference tools: init_character, get_style, import_glb."""
from __future__ import annotations

from pathlib import Path

from .. import character as C
from ..blender import run_job
from ..paths import REPO
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


def add_reference(name: str, image: str, views: dict, top_y: float, floor_y: float,
                  height_m: float | None = None, extent_m: float = 2.6) -> dict:
    """Store a turnaround sheet in workspace/<name>/reference/ and cut same-scale view crops."""
    import json
    import shutil

    C.require(name)
    src = Path(image).expanduser()
    if not src.is_absolute() and not src.exists():
        src = REPO / src  # repo-relative, e.g. specs/<name>/reference/turnaround.webp
    src = src.resolve()
    if not src.exists():
        raise C.CharacterError(f"reference image not found: {image}")
    allowed = set(load_style()["preview"]["views"])
    bad = [v for v in views if v not in allowed or v == "three_quarter"]
    if bad or not views:
        raise C.CharacterError(f"views must be a subset of front/side/back, got {list(views)}")
    if floor_y <= top_y:
        raise C.CharacterError("floor_y must be below top_y (pixel rows grow downwards)")
    spec = C.load_spec(name) or {}
    if height_m is None:
        arch = load_style()["archetypes"][spec.get("archetype", load_style()["default_archetype"])]
        height_m = sum(arch["height"]) / 2
    ref_dir = C.character_dir(name) / "reference"
    ref_dir.mkdir(parents=True, exist_ok=True)
    dst = ref_dir / ("source" + src.suffix.lower())
    shutil.copyfile(src, dst)
    views = {v: (d if isinstance(d, dict) else {"center_x": d}) for v, d in views.items()}
    args = {"image": str(dst), "out_dir": str(ref_dir), "top_y": top_y, "floor_y": floor_y,
            "height_m": height_m, "extent_m": extent_m, "size": load_style()["preview"]["view_size"],
            "views": views}
    r = run_job("crop_reference", args)
    if not r.get("ok"):
        return r
    st = r["stats"]
    ref = {"source": dst.name, "original": str(image), "top_y": top_y, "floor_y": floor_y, "height_m": height_m,
           "extent_m": extent_m, "size": args["size"], "views": views, "m_per_px": st["m_per_px"],
           "crop_px": st["crop_px"], "pad_px": st["pad_px"], "background": st["background"],
           "crops": {v: Path(p).name for v, p in st["crops"].items()}}
    (ref_dir / "reference.json").write_text(json.dumps(ref, indent=1) + "\n")
    r["outputs"].append(str(ref_dir / "reference.json"))
    return r
