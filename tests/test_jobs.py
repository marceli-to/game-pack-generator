"""Blender jobs against generated fixtures (no binary fixtures in git)."""
import json
import struct

import pytest

from server.blender import run_job, run_job_checked
from server.paths import REPO
from server.style import load_style

from .conftest import needs_blender

pytestmark = needs_blender


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def test_version_pin_is_enforced(monkeypatch):
    monkeypatch.setenv("GPG_PIN_BLENDER_OVERRIDE", "0.0.1")
    r = run_job("stats", {})
    assert not r["ok"] and "pinned version 0.0.1" in r["error"]


def test_template_hits_targets():
    s = load_style()
    t = json.loads((REPO / load_style()["archetypes"]["human"]["template"]).read_text())
    tg = s["archetypes"]["human"]["targets"]
    lm = t["landmarks"]
    assert lm["hip.l"][2] == pytest.approx(tg["hip_z"], abs=1e-3)
    assert lm["head_base"][2] == pytest.approx(tg["head_base_z"], abs=1e-3)
    assert lm["head_top"][2] == pytest.approx(tg["head_top_z"], abs=1e-3)
    assert lm["shoulder.l"][0] == pytest.approx(tg["shoulder_x"], abs=1e-3)
    assert lm["hip.l"][0] == pytest.approx(tg["hip_x"], abs=1e-3)
    assert set(t["bones"]) == {b["name"] for b in s["skeleton"]["bones"]}


def test_clean_mannequin_is_valid(mannequin):
    r = run_job_checked("validate", {}, blend=mannequin)
    assert r["valid"], r["hard"]
    assert r["soft"] == []
    st = r["stats"]
    assert st["body_height"] == pytest.approx(1.8, abs=1e-3)
    assert st["total_top"] > st["body_height"]  # hair is excluded from the body height
    assert st["skeleton"]["bones"] == 25 and st["skeleton"]["deforming"] == 20
    assert st["actions"] == sorted(c["name"] for c in load_style()["animations"]["clips"])
    assert st["materials"] == ["M_Palette"] and st["palette_texture_ok"]


@pytest.mark.parametrize("defect,code", [
    ("flipped_normals", "flipped_normals"),
    ("second_material", "materials"),
    ("no_role", "no_role"),
    ("too_tall", "height"),
    ("open_mesh", "non_manifold"),
])
def test_defects_are_caught(fixtures_dir, defect, code):
    blend = fixtures_dir / f"defect_{defect}.blend"
    run_job_checked("make_mannequin", {"out": str(blend), "defects": [defect], "animations": False})
    r = run_job_checked("validate", {}, blend=blend)
    assert [h["code"] for h in r["hard"]] == [code]


def test_spec_colour_check(mannequin):
    r = run_job_checked("validate", {"spec": {"colors": {"skin": 2}}}, blend=mannequin)
    assert "role_without_colour" in [h["code"] for h in r["hard"]]


def test_render_preview_sheet(mannequin, tmp_path):
    r = run_job_checked("render_preview", {"out_dir": str(tmp_path)}, blend=mannequin)
    assert png_size(r["outputs"][0]) == (2048, 512)
    assert len(r["previews"]) == 5
    r = run_job_checked("render_preview", {"out_dir": str(tmp_path / "walk"), "pose": "walk@8", "views": ["front"]},
                        blend=mannequin)
    assert png_size(r["outputs"][0]) == (512, 512)


def test_animation_feet_stay_on_floor_in_idle(mannequin, tmp_path):
    """Hips location keys are scaled with the legs: in idle the feet must touch the floor."""
    r = run_job_checked("render_preview", {"out_dir": str(tmp_path), "pose": "idle@0", "views": ["front"]},
                        blend=mannequin)
    assert r["ok"]


def test_auto_paint_on_mannequin(mannequin, tmp_path):
    """Painted style, auto approach: unwraps, bakes AO, paints every texel, writes the texture."""
    colors = {"skin": 6, "primary": 17, "secondary": 46, "accent": 42, "metal": 40, "leather": 45,
              "dark": 54, "special": 32, "hair": 8}
    r = run_job_checked("paint_surface", {"approach": "auto", "colors": colors, "out_dir": str(tmp_path),
                                          "size": 256}, blend=mannequin, timeout=600, style="painted")
    tex = tmp_path / "auto.png"
    assert tex.exists() and png_size(tex) == (256, 256)
    st = r["stats"]
    assert st["texels"] > 5000
    assert 0.1 < st["ao_mean"] <= 1.0
    assert -1.0 < st["light_mean"] < 1.0
