"""STYLE.md §8b: opt-in extra clips (shooter set), arms-only bake, arms-only channels in the GLB."""
import json
import re
import struct

import pytest

from server.blender import run_job_checked
from server.paths import REPO
from server.style import load_style

from .conftest import needs_blender

STYLE_MD = (REPO / "STYLE.md").read_text()
EXTRA = load_style()["animations"]["extra_clips"]


def test_extra_clips_documented():
    for c in EXTRA:
        row = re.search(rf"\| `{c['name']}` \| `{c['source']}` \([A-Za-z]+\) \| (yes|no) \| (.+?) \| (yes|no) \|", STYLE_MD)
        assert row, c["name"]
        assert (row.group(1) == "yes") == c["loop"], c["name"]
        assert (row.group(3) == "yes") == c["arms_only"], c["name"]
        if "range" in c:
            assert f"range {c['range'][0]}–{c['range'][1]}" in row.group(2), c["name"]
        if "hold" in c:
            assert f"hold frame {c['hold']} for {c['frames']} frames" in row.group(2), c["name"]
        if c.get("sides"):
            assert c["sides"] == ["r"] and c["name"].endswith("_1h"), c["name"]
        if c.get("breathe"):
            md = STYLE_MD.split("## 8b.")[1]
            assert f"`{c['name']}`: " + ", ".join(f"{b} {d}".replace("-", "−") for b, d in c["breathe"].items()) in md, c["name"]
            assert "one breath per loop" in row.group(2), c["name"]
        if c.get("over"):   # solved on the base clip's torso; the base clip is an extra clip itself
            assert f"over `{c['over']}`" in row.group(2), c["name"]
            assert c["over"] in {e["name"] for e in EXTRA} and c["arms_only"], c["name"]
    for b in load_style()["animations"]["arms_only_bones"]:
        assert b in STYLE_MD.split("## 8b.")[1].split("## 9.")[0], b


def _glb_channels(path):
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    g = json.loads(b[20:20 + n])
    names = [nd.get("name") for nd in g["nodes"]]
    return {a["name"]: {names[c["target"]["node"]] for c in a["channels"]} for a in g["animations"]}


@needs_blender
def test_extra_clips_bake_and_export(mannequin, tmp_path):
    names = [c["name"] for c in EXTRA]
    out = tmp_path / "shooter.blend"
    r = run_job_checked("apply_animations", {"spec": {"extra_clips": names}, "out": str(out)},
                        blend=mannequin, timeout=400)
    clips = r["stats"]["clips"]
    assert set(names) <= set(clips)
    for c in EXTRA:
        if not c["arms_only"]:
            assert "arms_only" not in clips[c["name"]]
            continue
        rep = clips[c["name"]]["arms_only"]
        assert max(rep["reach_error_m"].values()) < 0.01, (c["name"], rep)
        assert rep["gun_max_yaw_deg"] < 5, (c["name"], rep)          # points forward on the upright torso
        if c.get("stance"):   # 2H stance: both hands well in front of the shoulders, close together on the gun
            st = rep["stance"]
            assert st["hands_forward_m"] > 0.4 * st["arm_length_m"], (c["name"], rep)
            assert st["hand_spacing_m"] < 0.5 * st["arm_length_m"], (c["name"], rep)
        elif c.get("sides", ["l", "r"]) == ["l", "r"]:
            assert rep["hand_spacing_change_m"] < 0.01, (c["name"], rep)  # the left hand stays on the gun
        if c["name"].startswith(("aim", "crouch_aim")):   # level, also on the crouch's leaning chest
            assert rep["gun_max_pitch_deg"] < 6, (c["name"], rep)
        assert rep.get("over") == c.get("over"), (c["name"], rep)
    assert not set(names) & set(r["stats"]["floor_lift_m"]) - {"crouch", "crouch_walk"}

    glb = tmp_path / "shooter.glb"
    e = run_job_checked("export_glb", {"out": str(glb)}, blend=out)
    chans = _glb_channels(glb)
    arm_bones = {f"{b}.{s}" for b in load_style()["animations"]["arms_only_bones"] for s in "lr"}
    for c in EXTRA:
        if c["arms_only"]:   # 1H: right arm only, the left arm comes from the base clip
            want = {f"{b}.{s}" for b in load_style()["animations"]["arms_only_bones"] for s in c.get("sides", "lr")}
            assert chans[c["name"]] == want, c["name"]
            assert e["stats"]["arms_only_channels_removed"][c["name"]] > 0
    assert len(chans["walk"]) > len(arm_bones)
    assert len(chans["crouch"]) > len(arm_bones)
    # palette texture: NEAREST both ways, no mipmaps (STYLE.md §10)
    b = glb.read_bytes()
    g = json.loads(b[20:20 + struct.unpack("<I", b[12:16])[0]])
    assert g.get("samplers") and all(s.get("minFilter") == 9728 for s in g["samplers"] if s.get("magFilter") == 9728)


@needs_blender
def test_over_clip_needs_its_base(mannequin, tmp_path):
    with pytest.raises(Exception, match="baked over"):
        run_job_checked("apply_animations", {"spec": {"extra_clips": ["crouch_aim_1h"]}, "out": str(tmp_path / "x.blend")},
                        blend=mannequin)


@needs_blender
def test_unknown_extra_clip_is_rejected(mannequin, tmp_path):
    with pytest.raises(Exception, match="unknown extra clips"):
        run_job_checked("apply_animations", {"spec": {"extra_clips": ["moonwalk"]}, "out": str(tmp_path / "x.blend")},
                        blend=mannequin)


@needs_blender
def test_init_character_rejects_unknown_extra_clips(workspace):
    from server import character as C
    from server.tools import project as T_project
    with pytest.raises(C.CharacterError, match="unknown extra clips"):
        T_project.init_character("x", {"extra_clips": ["aim_1h", "moonwalk"]})
