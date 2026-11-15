"""Build everything in library/ from the KayKit download (Phase 1).

    python -m server.build_library --source /path/to/KayKit_Character_Animations_1.1

Writes: library/palette.png, library/skeleton.blend, library/animations.blend,
library/proportions/<archetype>.json (+ _preview.png), library/CREDITS.md, and the
generated `frames` of each clip in style.json.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .blender import run_job_checked
from .palette import make_palette
from .paths import LIBRARY, STYLE_JSON
from .style import dump_style, reload_style

CREDITS = """# Credits

## Skeleton and animations
- **KayKit Character Animations 1.1** by Kay Lousberg (www.kaylousberg.com)
  - Licence: CC0 1.0 (Creative Commons Zero), `License.txt` in the download dated 10/12/2025
  - Source: https://kaylousberg.itch.io/kaykit-character-animations
  - Used: `Animations/gltf/Rig_Medium/*.glb` -> `library/skeleton.blend` (rig, plus our `headslot`
    and `backslot` bones) and `library/animations.blend` (clips mapped in style.json)
  - Crediting is not required by the licence; we do it anyway.
"""


def build(source: Path) -> dict:
    if not (source / "Animations" / "gltf" / "Rig_Medium").is_dir():
        raise SystemExit(f"{source} does not look like KayKit_Character_Animations_1.1")
    report = {"palette": str(make_palette())}
    report["skeleton"] = run_job_checked("build_skeleton", {"source_dir": str(source)})["stats"]
    anim = run_job_checked("build_animations", {"source_dir": str(source)})
    report["animations"] = {k: v["frames"] for k, v in anim["clips"].items()}

    style = json.loads(STYLE_JSON.read_text())
    for clip in style["animations"]["clips"]:
        clip["frames"] = anim["clips"][clip["name"]]["frames"]
    STYLE_JSON.write_text(dump_style(style))
    style = reload_style()

    report["templates"] = {}
    for arch, cfg in style["archetypes"].items():
        if "targets" not in cfg:
            continue
        t = run_job_checked("make_template", {"archetype": arch})
        with tempfile.TemporaryDirectory() as tmp:
            blend = Path(tmp) / "mannequin.blend"
            run_job_checked("make_mannequin", {"out": str(blend), "template": cfg["template"], "animations": False})
            r = run_job_checked("render_preview", {"out_dir": tmp}, blend=blend)
            preview = LIBRARY / "proportions" / f"{arch}_preview.png"
            shutil.copy(r["outputs"][0], preview)
        report["templates"][arch] = {**t["stats"], "preview": str(preview)}

    (LIBRARY / "CREDITS.md").write_text(CREDITS)
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, type=Path, help="KayKit_Character_Animations_1.1 folder")
    print(json.dumps(build(ap.parse_args().source.expanduser()), indent=1))


if __name__ == "__main__":
    main()
