"""Build everything in library/ from the KayKit download (Phase 1).

    python -m server.build_library --source /path/to/KayKit_Character_Animations_1.1

Writes the shared library (library/skeleton.blend, library/animations.blend, library/CREDITS.md, the
`frames` of each clip in core.json) and, for every style in styles/: its palette.png (palette surface)
and its proportion templates (+ _preview.png).
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .blender import run_job_checked
from .palette import make_palette
from .paths import CORE_JSON, LIBRARY, REPO
from .style import available_styles, dump_style, reload_style

CREDITS = """# Credits

## Skeleton and animations
- **KayKit Character Animations 1.1** by Kay Lousberg (www.kaylousberg.com)
  - Licence: CC0 1.0 (Creative Commons Zero), `License.txt` in the download dated 10/12/2025
  - Source: https://kaylousberg.itch.io/kaykit-character-animations
  - Used: `Animations/gltf/Rig_Medium/*.glb` -> `library/skeleton.blend` (rig, plus our `headslot`
    and `backslot` bones) and `library/animations.blend` (clips mapped in core.json)
  - Crediting is not required by the licence; we do it anyway.
"""


def build(source: Path) -> dict:
    if not (source / "Animations" / "gltf" / "Rig_Medium").is_dir():
        raise SystemExit(f"{source} does not look like KayKit_Character_Animations_1.1")
    report = {}
    report["skeleton"] = run_job_checked("build_skeleton", {"source_dir": str(source)})["stats"]
    anim = run_job_checked("build_animations", {"source_dir": str(source)})
    report["animations"] = {k: v["frames"] for k, v in anim["clips"].items()}

    core = json.loads(CORE_JSON.read_text())
    for clip in core["animations"]["clips"]:
        clip["frames"] = anim["clips"][clip["name"]]["frames"]
    CORE_JSON.write_text(dump_style(core))

    report["styles"] = {}
    for name in available_styles():
        style = reload_style(name)
        rep = report["styles"][name] = {"templates": {}}
        if style.get("surface") == "palette":
            rep["palette"] = str(make_palette(style=name))
        for arch, cfg in style["archetypes"].items():
            if "targets" not in cfg:
                continue
            t = run_job_checked("make_template", {"archetype": arch}, style=name)
            with tempfile.TemporaryDirectory() as tmp:
                blend = Path(tmp) / "mannequin.blend"
                run_job_checked("make_mannequin", {"out": str(blend), "template": cfg["template"], "animations": False},
                                style=name)
                r = run_job_checked("render_preview", {"out_dir": tmp}, blend=blend, style=name)
                preview = REPO / cfg["template"].replace(".json", "_preview.png")
                shutil.copy(r["outputs"][0], preview)
            rep["templates"][arch] = {**t["stats"], "preview": str(preview)}

    (LIBRARY / "CREDITS.md").write_text(CREDITS)
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, type=Path, help="KayKit_Character_Animations_1.1 folder")
    print(json.dumps(build(ap.parse_args().source.expanduser()), indent=1))


if __name__ == "__main__":
    main()
