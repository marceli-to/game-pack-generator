"""Step 4: project an AI run onto the v3 knight and make a comparison sheet.
Run from the repo root:  .venv/bin/python spikes/ai-texture/project.py <tag>
Rows: reference (knight sheet, head crops), auto paint, AI projected (unlit)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, ".")
from server.blender import run_job_checked
from server.paths import blender_bin

tag = sys.argv[1]
run = (Path("spikes/ai-texture/runs") / tag).resolve()
spec = json.load(open("specs/knight/spec.json"))
spec["colors"]["special"] = 33
ref = json.loads((run / "reference.json").read_text())
r = run_job_checked("paint_surface", {"approach": "projection", "colors": spec["colors"], "out_dir": str(run / "paint"),
                    "ref": ref, "ref_image": str(run / "sheet.png"), "out_blend": str(run / "knight-ai.blend"),
                    "projection": {"facing_power": 2.0, "erode_px": 2},
                    "frame": {"center": [0, 0, 1.08], "extent": 0.75}},
                    blend="workspace/knight-v3/character.blend", timeout=900, style="painted")
print(json.dumps(r["stats"].get("projection"), indent=1))
# reference row: head crops of the knight sheet at the render scale (sheet: floor y 893, 1.2 m = 678 px)
code = f'''
import sys, numpy as np; sys.path.insert(0, "jobs")
from lib import render as RD
src = RD.load_rgba("specs/knight/reference/turnaround.png")
mpp = 1.2 / (893 - 215); half = int(round(0.75 / 2 / mpp)); cy = int(round(893 - 1.08 / mpp))
row = [RD.resample(src[cy - half:cy + half, cx - half:cx + half], 512) for cx in (301, 715, 1120)]
blank = np.ones((512, 512, 4), dtype=np.float32) * np.array([0.91, 0.91, 0.91, 1.0], dtype=np.float32)
rows = [np.concatenate(row + [blank], 1),
        RD.load_rgba("spikes/ai-texture/runs/_auto/auto_flat_sheet.png"),
        RD.load_rgba("{run}/paint/projection_flat_sheet.png")]
RD.save_rgba(np.concatenate(rows, 0), "{run}/compare.png")
'''
subprocess.run([blender_bin(), "-b", "--factory-startup", "--python-expr", code], check=True, capture_output=True)
print(run / "compare.png")
