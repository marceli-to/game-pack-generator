"""Stride bake (STYLE.md §8, `clip_stride`): walk/run feet re-planted for a ground speed; the tinfox guard."""
import json

from server.paths import REPO
from server.style import load_style
from server.tools import animate as T_animate
from server.tools import assemble as T_assemble
from server.tools import project as T_project

from .conftest import needs_blender


def test_stride_documented():
    core_md = (REPO / "STYLE.md").read_text()
    stride = load_style("tinfox")["animations"]["stride"]
    assert "clip_stride` = `{clip: m/s}`" in core_md
    assert f"`stride.contact` = {round(stride['contact'] * 100)} cm" in core_md
    for name in ("clean", "lowpoly", "painted", "tinfox"):
        style = load_style(name)
        md = (REPO / "styles" / name / "STYLE.md").read_text()
        for arch, a in style["archetypes"].items():
            cs = a.get("clip_stride", {})
            if cs:
                line = f"`{arch}` re-plants " + " and ".join(f"`{c}` for {v} m/s" for c, v in cs.items())
                assert line in md.replace("\n  ", " "), line


@needs_blender
def test_guard_walk_and_run_planted_at_their_speed(workspace):
    spec = json.loads((REPO / "specs" / "guard" / "spec.json").read_text())
    T_project.init_character("guard", spec)
    assert T_assemble.assemble_from_parts("guard")["ok"]
    r = T_animate.apply_animations("guard")
    assert r["ok"], r.get("error")
    clips = r["stats"]["clips"]
    for clip, speed in load_style("tinfox")["archetypes"]["hero-m"]["clip_stride"].items():
        st = clips[clip]["stride"]
        assert st["speed_m_s"] == speed
        for side in ("l", "r"):
            lo, hi = st[side]["stance_speed_m_s"]
            # the planted foot moves at the ground speed the whole stance (the moonwalk was 1.1-2.5 m/s)
            assert abs(lo - speed) < 0.1 * speed and abs(hi - speed) < 0.1 * speed, (clip, side, lo, hi)
            assert st[side]["reach_error_m"] < 0.02, (clip, side)
    assert clips["run"]["stride"]["l"]["factor"] < 0.7    # KayKit's run on hero-m legs was a 6.4 m/s sprint
    assert "stride" not in clips["idle"] and "stride" not in clips["crouch_walk"]
