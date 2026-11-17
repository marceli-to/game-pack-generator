"""Automatic fit to the reference sheet (STYLE.md §7b, core.json `fit`)."""
import json
import subprocess

from server.paths import JOBS, REPO, blender_bin
from server.style import load_style
from server.tools import assemble as T_assemble
from server.tools import project as T_project
from server.tools import qa as T_qa

from .conftest import needs_blender

UNITS = """
import sys, json
sys.path.insert(0, {jobs!r})
import numpy as np
from lib import fit as F, style as S
style = S.load()
slots, groups = style["slots"], style["fit"]["groups"]
z = np.linspace(0.7, 1.5, 9)
torso = np.stack([np.full(9, 0.2), np.full(9, 0.1), z], 1)
leg = np.stack([np.full(9, 0.25), np.full(9, 0.08), np.linspace(0.0, 0.9, 9)], 1)
co = np.concatenate([torso, leg])
vslot = np.array([slots.index("torso")] * 9 + [slots.index("legs")] * 9)
fr = F.frames(co, vslot, slots, groups, {{"hip.l": [0.15, 0, 0.9], "shoulder.l": [0.25, 0, 1.35]}})
r = {{}}
r["identity"] = bool(np.allclose(F.apply(co, fr, {{}}), co))
out = F.apply(co, fr, {{"torso": {{"u": [1.0, 1.0, 1.5], "v": [1, 1, 1]}}}})
r["top"] = [float(out[8, 0]), float(out[0, 0])]
r["kept"] = bool(np.allclose(out[:, 2], co[:, 2]) and np.allclose(out[9:], co[9:]))
out = F.apply(co, fr, {{"legs": {{"u": [2.0, 2.0, 2.0], "v": [1, 1, 1]}}}})
r["legs_x"] = float(out[12, 0])
cls, lab = F.classes(["#2B2B2B", "#383838", "#666B32", "#F7AE7A"], 14)
r["cls"] = cls.tolist()
rgb = np.array([[[0.40, 0.42, 0.20], [0.97, 0.68, 0.48]]])
r["classify"] = F.classify(rgb, np.ones((1, 2), bool), lab, cls).tolist()
r["score"] = list(F.score(np.array([[0, 1, -1]]), np.array([[0, 2, 1]]), 0.4))
print("RESULT" + json.dumps(r))
"""


@needs_blender
def test_fit_units(tmp_path):
    """Scale curves keep heights and other regions; classes merge close colours; score over the union."""
    p = tmp_path / "units.py"
    p.write_text(UNITS.format(jobs=str(JOBS)))
    out = subprocess.run([blender_bin(), "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(p)],
                         capture_output=True, text=True, timeout=120, env={"GPG_STYLE": "tinfox", "PATH": ""})
    line = [x for x in out.stdout.splitlines() if x.startswith("RESULT")]
    assert line, (out.stdout + out.stderr)[-2000:]
    r = json.loads(line[0][6:])
    assert r["identity"] and r["kept"]
    assert abs(r["top"][0] - 0.3) < 1e-9 and abs(r["top"][1] - 0.2) < 1e-9   # top widened, bottom kept
    assert abs(r["legs_x"] - (0.15 + 0.10 * 2)) < 1e-9                       # legs scale about the hip line
    cls = r["cls"]
    assert cls[0] == cls[1] and len(set(cls)) == 3                           # black and dark grey merge
    assert r["classify"] == [[cls[2], cls[3]]]
    sil, agree, _ = r["score"]
    assert abs(sil - 2 / 3) < 1e-9 and abs(agree - 1 / 3) < 1e-9


def test_fit_documented():
    md = (REPO / "STYLE.md").read_text()
    cfg = load_style()["fit"]
    for g, gc in cfg["groups"].items():
        assert f"`{g}`" in md
    assert f"`size` = {cfg['size']} px" in md and f"`colour_merge` = {cfg['colour_merge']}" in md
    assert f"`w_silhouette` = {cfg['w_silhouette']}" in md and f"`smooth_penalty` = {cfg['smooth_penalty']}" in md
    lo, hi = cfg["bounds"]
    assert f"`bounds` = {lo}–{hi}" in md
    assert f"`arms_down_step` = {cfg['arms_down_step']}°" in md


@needs_blender
def test_guard_fit_improves_score(workspace):
    spec = json.loads((REPO / "specs" / "guard" / "spec.json").read_text())
    spec.pop("fit", None)
    T_project.init_character("guard", spec)
    r = T_project.add_reference("guard", "specs/guard/reference/turnaround.png",
                                {"front": {"center_x": 321, "x_range": [0, 620]},
                                 "side": {"center_x": 795, "x_range": [620, 1010]},
                                 "back": {"center_x": 1343, "x_range": [1010, 1672]}},
                                top_y=50, floor_y=926, height_m=1.8)
    assert r["ok"], r.get("error")
    f = T_qa.fit_to_reference("guard", apply=True)
    assert f["ok"], f.get("error")
    st = f["stats"]
    assert st["after"]["score"] > st["before"]["score"] + 0.01, st
    assert "feet" not in st["fit"]                                            # excluded in the spec
    assert st["fit"]["legs"]["u"][0] == 1.0 and st["fit"]["legs"]["v"][0] == 1.0   # meets the kept boots
    a = T_assemble.assemble_from_parts("guard")
    assert a["ok"] and a["stats"]["fit_verts"] > 1000
