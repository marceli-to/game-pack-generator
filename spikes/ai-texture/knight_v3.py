"""Step 1: build the v3 test knight (head only) from the library parts and paint it with `auto`.
Run from the repo root:  .venv/bin/python spikes/ai-texture/knight_v3.py [--facet F] [--smooth]
--smooth: no brush dabs / value bands / wobble. --facet: auto-paint `light.facet` for the start image (style default 0.5; 0 = smooth light, no plank lines on the dome).
-> workspace/knight-v3/character.blend, spikes/ai-texture/runs/_auto/auto_flat_sheet.png (head framing)."""
import json
import sys
import time

sys.path.insert(0, ".")
from server.blender import run_job_checked
from server.tools import assemble as T_assemble, project as T_project, qa as T_qa

facet = float(sys.argv[sys.argv.index("--facet") + 1]) if "--facet" in sys.argv else None
smooth = "--smooth" in sys.argv   # no brush dabs / value bands in the start image
over = {}
if facet is not None:
    over["light"] = {"facet": facet}
if smooth:
    over["brush"] = {"dab_amount": 0.0, "band_mix": 0.0, "wobble_amount": 0.0}
spec = json.load(open("specs/knight/spec.json"))
spec.pop("reference", None)
spec["colors"]["special"] = 33                      # deeper blue eyes (spike)
spec["parts"] = {"head": "head-skull-grin", "headwear": "headwear-helmet-bell"}
T_project.init_character("knight-v3", spec, overwrite=True)
r = T_assemble.assemble_from_parts("knight-v3")
print("assemble", r["ok"], r.get("error"), r["stats"].get("part_tris"))
t = time.time()
run_job_checked("paint_surface", {"approach": "auto", "colors": spec["colors"],
                "out_dir": "spikes/ai-texture/runs/_auto", "out_blend": "workspace/knight-v3/character.blend",
                "frame": {"center": [0, 0, 1.08], "extent": 0.75},
                **({"auto": over} if over else {})},
                blend="workspace/knight-v3/character.blend", timeout=900, style="painted")
print("auto paint", round(time.time() - t, 1), "s")
v = T_qa.validate("knight-v3")
print("validate hard", [h["message"] for h in v["hard"]])
