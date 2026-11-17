"""Export tool: GLB + Khronos validator + headless three.js test load (STYLE.md §10)."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from .. import character as C
from .. import node
from ..blender import run_job
from ..paths import character_dir
from ..style import load_style


def glb_summary(glb: Path) -> dict:
    """Material facts from the GLB's JSON chunk: extensions, texture filters, UV sets per primitive."""
    data = glb.read_bytes()
    n = struct.unpack("<I", data[12:16])[0]
    j = json.loads(data[20:20 + n])
    prims = [p for m in j.get("meshes", []) for p in m["primitives"]]
    return {
        "extensions_used": j.get("extensionsUsed", []),
        "materials": [{"name": m.get("name"), "unlit": "KHR_materials_unlit" in m.get("extensions", {}),
                       "double_sided": m.get("doubleSided", False)} for m in j.get("materials", [])],
        "samplers": j.get("samplers", []),
        "texcoords": max((sum(k.startswith("TEXCOORD_") for k in p["attributes"]) for p in prims), default=0),
        "vertex_colors": any("COLOR_0" in p["attributes"] for p in prims),
    }


def glb_nodes(glb: Path) -> dict:
    """Root-level nodes of the GLB: name -> translation (props: the mesh and the anchor empties)."""
    data = glb.read_bytes()
    n = struct.unpack("<I", data[12:16])[0]
    j = json.loads(data[20:20 + n])
    return {nd.get("name"): nd.get("translation", [0, 0, 0]) for nd in j.get("nodes", [])}


def export(name: str) -> dict:
    blend = C.require(name)
    st = C.style_of(name)
    out_dir = character_dir(name) / "export"
    kind = "prop" if C.is_prop(C.load_spec(name)) else "character"   # STYLE.md §9: prop-<name>.glb
    glb = out_dir / f"{kind}-{name}.glb"
    shot = out_dir / f"{kind}-{name}-testload.png"

    check = run_job("validate", {"spec": C.load_spec(name)}, blend=blend, style=st)
    r = run_job("export_glb", {"out": str(glb)}, blend=blend, style=st)
    if not r.get("ok"):
        return r
    gv = node.gltf_validate(glb)
    actions = r["stats"].get("actions", [])
    anim = "idle" if "idle" in actions else "-"
    tl = node.test_load(glb, shot, anim, "cam=fit" if kind == "prop" else "")

    style = load_style(st)
    summary = glb_summary(glb)
    problems = []
    if style.get("surface") == "painted" and style["paint"].get("unlit"):
        if not summary["materials"] or not all(m["unlit"] for m in summary["materials"]):
            problems.append("painted style exports unlit, but the GLB material has no KHR_materials_unlit "
                            "(run paint_surface)")
    if style["shading"].get("ao") and not summary["vertex_colors"]:
        problems.append("the style bakes AO (shading.ao) but the GLB has no COLOR_0 (re-assemble)")
    if gv["errors"] > style["export"]["max_validator_errors"]:
        problems.append(f"glTF validator: {gv['errors']} errors")
    if not tl.get("ok"):
        problems.append("three.js test load failed")
    if anim == "-" and kind == "character":
        r["warnings"].append("no 'idle' animation: test load only checked that the model loads")
    if kind == "prop":
        need = load_style(st)["props"]["types"][C.load_spec(name)["type"]]["anchors"]
        summary["nodes"] = glb_nodes(glb)
        lost = [a for a in need if a not in summary["nodes"]]
        if lost:
            problems.append(f"anchor nodes missing in the GLB: {lost}")
    report = {
        "glb": str(glb),
        "valid_style": check.get("valid"),
        "style_hard": check.get("hard", []),
        "style_soft": check.get("soft", []),
        "gltf": summary,
        "gltf_validator": gv,
        "test_load": tl,
        "problems": problems,
    }
    (out_dir / "export-report.json").write_text(json.dumps(report, indent=1))
    r.update({
        "ok": not problems,
        "outputs": [str(glb), str(out_dir / "export-report.json")],
        "previews": [str(shot)],
        "report": report,
    })
    if problems:
        r["error"] = "; ".join(problems)
    if check.get("hard"):
        r["warnings"].append(f"{len(check['hard'])} hard style violations (see report.style_hard); "
                             "the GLB was written but is not approvable")
    return r
