"""QA tools: stats, render_preview, validate."""
from __future__ import annotations

from .. import character as C
from ..blender import run_job
from ..paths import character_dir


def stats(name: str) -> dict:
    return run_job("stats", {"spec": C.load_spec(name)}, blend=C.require(name), style=C.style_of(name))


def render_preview(name: str, views: list[str] | None = None, pose: str = "rest") -> dict:
    out = character_dir(name) / "renders" / ("preview" if pose == "rest" else pose.replace("@", "_"))
    args = {"out_dir": str(out), "pose": pose}
    if views:
        args["views"] = views
    return run_job("render_preview", args, blend=C.require(name), style=C.style_of(name))


def validate(name: str) -> dict:
    return run_job("validate", {"spec": C.load_spec(name)}, blend=C.require(name), style=C.style_of(name))


def compare_reference(name: str, arms_down_deg: float | None = None,
                      hide_slots: list[str] | None = None) -> dict:
    """Reference crops vs renders at the same scale + silhouette overlay and IoU per view."""
    import json

    blend = C.require(name)
    ref_dir = character_dir(name) / "reference"
    ref_json = ref_dir / "reference.json"
    if not ref_json.exists():
        raise C.CharacterError(f"{name!r} has no reference; call add_reference first")
    ref = json.loads(ref_json.read_text())
    spec = C.load_spec(name) or {}
    cmp = spec.get("compare", {})
    args = {"ref": ref, "ref_dir": str(ref_dir), "out_dir": str(character_dir(name) / "renders" / "compare"),
            "arms_down_deg": arms_down_deg if arms_down_deg is not None else cmp.get("arms_down_deg", 0),
            "hide_slots": hide_slots if hide_slots is not None else cmp.get("hide_slots", [])}
    return run_job("compare_reference", args, blend=blend, style=C.style_of(name))


def fit_to_reference(name: str, apply: bool = True) -> dict:
    """Automatic fit to the reference sheet (STYLE.md §7b): assembles the character without spec.fit, searches
    region scale curves + the comparison arm angle against the sheet's outline and colour classes, then (apply)
    stores them in spec.fit / spec.compare.arms_down_deg and re-assembles. Re-run apply_animations after it."""
    import json
    import tempfile

    from . import assemble as T_assemble

    C.require(name)
    ref_dir = character_dir(name) / "reference"
    ref_json = ref_dir / "reference.json"
    if not ref_json.exists():
        raise C.CharacterError(f"{name!r} has no reference; call add_reference first")
    ref = json.loads(ref_json.read_text())
    spec = C.load_spec(name) or {}
    base = {k: v for k, v in spec.items() if k != "fit"}
    with tempfile.TemporaryDirectory(prefix="gpg-fit-") as tmp:
        blend = f"{tmp}/unfitted.blend"
        a = run_job("assemble", {"spec": base, "out": blend}, style=C.style_of(name))
        if not a.get("ok"):
            return a
        r = run_job("fit_reference", {"ref": ref, "ref_dir": str(ref_dir), "spec": base,
                                      "out_dir": str(character_dir(name) / "renders" / "fit"),
                                      "start": {"arms_down_deg": (spec.get("compare") or {}).get("arms_down_deg")}},
                    blend=blend, style=C.style_of(name), timeout=900)
    if not r.get("ok") or not apply:
        return r
    st = r["stats"]
    spec["fit"] = st["fit"]
    spec.setdefault("compare", {})["arms_down_deg"] = st["arms_down_deg"]
    C.save_spec(name, spec)
    a = T_assemble.assemble_from_parts(name)
    if not a.get("ok"):
        return a
    c = compare_reference(name)
    r["stats"]["iou"] = c.get("stats", {}).get("iou")
    r["previews"] = r["previews"] + c.get("previews", [])
    r["stats"]["spec_hash"] = a["stats"].get("spec_hash")
    return r
