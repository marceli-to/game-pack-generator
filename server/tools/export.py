"""Export tool: GLB + Khronos validator + headless three.js test load (STYLE.md §10)."""
from __future__ import annotations

import json

from .. import character as C
from .. import node
from ..blender import run_job
from ..paths import character_dir
from ..style import load_style


def export(name: str) -> dict:
    blend = C.require(name)
    st = C.style_of(name)
    out_dir = character_dir(name) / "export"
    glb = out_dir / f"character-{name}.glb"
    shot = out_dir / f"character-{name}-testload.png"

    check = run_job("validate", {"spec": C.load_spec(name)}, blend=blend, style=st)
    r = run_job("export_glb", {"out": str(glb)}, blend=blend, style=st)
    if not r.get("ok"):
        return r
    gv = node.gltf_validate(glb)
    actions = r["stats"].get("actions", [])
    anim = "idle" if "idle" in actions else "-"
    tl = node.test_load(glb, shot, anim)

    problems = []
    if gv["errors"] > load_style(st)["export"]["max_validator_errors"]:
        problems.append(f"glTF validator: {gv['errors']} errors")
    if not tl.get("ok"):
        problems.append("three.js test load failed")
    if anim == "-":
        r["warnings"].append("no 'idle' animation: test load only checked that the model loads")
    report = {
        "glb": str(glb),
        "valid_style": check.get("valid"),
        "style_hard": check.get("hard", []),
        "style_soft": check.get("soft", []),
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
