"""Phase 3: clips on an assembled character, upright grips, skirt weights, pose test, animated export."""
import json

import pytest

from server.paths import REPO
from server.style import load_style
from server.tools import animate as T_animate
from server.tools import assemble as T_assemble
from server.tools import export as T_export
from server.tools import project as T_project
from server.tools import qa as T_qa

from .conftest import needs_blender, needs_node

WIZARD_SPEC = REPO / "specs" / "wizard" / "spec.json"


def test_pose_test_values_documented():
    md = (REPO / "STYLE.md").read_text()
    pt, sk = load_style()["pose_test"], load_style()["skinning"]
    assert f"`step` = {pt['step']} frames" in md
    assert f"`penetration_tolerance` = {round(pt['penetration_tolerance'] * 100)} cm" in md
    assert f"`columns` = {pt['columns']}" in md and f"`tile_size` = {pt['tile_size']} px" in md
    assert f"`frame_scale` = {pt['frame_scale']}" in md
    assert f"`floor_margin` = {round(pt['floor_margin'] * 100)} %" in md
    assert all(f"`{c}`" in md for c in pt["foot_contact_clips"])
    assert f"`follow` = {sk['skirt']['follow']}" in md
    assert f"`centre_width` = {round(sk['skirt']['centre_width'] * 100)} cm" in md
    assert f"`full_at` = {round(sk['skirt']['full_at'] * 100)} %" in md
    assert f"`skinning.max_bones_per_vertex` = {sk['max_bones_per_vertex']} bones" in md
    assert all(f"(`{c}`)" in md for c in sk["upright_held_clips"])
    assert f"`upright_clearance` = {sk['upright_clearance'] * 100:.1f} cm" in md
    for b in sk["joint_blends"]:
        assert f"`{b['bone']}` → `{b['parent']}`" in md and f"({round(b['width'] * 100)} cm)" in md or \
            f"{round(b['width'] * 100)} cm)" in md


@needs_blender
@needs_node
def test_wizard_animates_and_exports(workspace):
    spec = json.loads(WIZARD_SPEC.read_text())
    T_project.init_character("wizard", spec)
    r = T_assemble.assemble_from_parts("wizard")
    assert r["ok"], r.get("error")
    assert r["stats"]["skirt_verts"]["torso-robe-chibi"] > 0   # long robe, no legs -> skirt weights
    assert {"upperarm.l", "upperarm.r", "foot.l", "foot.r", "lowerleg.l", "lowerleg.r"} <= set(r["stats"]["joint_blend_verts"])

    r = T_animate.apply_animations("wizard")
    assert r["ok"], r.get("error")
    names = [c["name"] for c in load_style("lowpoly")["animations"]["clips"]]
    assert sorted(r["stats"]["clips"]) == sorted(names)
    assert r["stats"]["upright"] == {"accessory_hand_r": "handslot.r"}
    assert r["stats"]["floor_lift_m"]["idle"] < 0.005   # standing still needs no lift
    assert 0 < r["stats"]["upright_lean_deg"]["run"]["accessory_hand_r"] < 30   # staff leans clear of the brim

    v = T_qa.validate("wizard")
    assert v["valid"], v["hard"]
    assert not any(s["code"] in ("deform_flags", "weights", "unweighted") for s in v["soft"]), v["soft"]

    p = T_animate.pose_test("wizard")
    assert p["ok"], p.get("error")
    clips = p["stats"]["clips"]
    assert clips["walk"]["foot_contact"] and clips["run"]["foot_contact"]
    assert not any(c["below_floor"] for c in clips.values()), {k: c["below_floor"] for k, c in clips.items()}
    # grip `upright` (STYLE.md §9a): the staff's slot keeps its rest orientation (not in held clips: die)
    # (the staff leans out only where it would cut the hat brim)
    assert all(c["upright_tilt_deg"]["handslot.r"] < 30 for n, c in clips.items() if n != "die")
    # hat clearance + chibi hand damping: no staff through the hat, no mitten through the sleeve
    # (not in die: there the staff is held and falls with the hand)
    pairs = {(x["part"], x["into"]) for n, c in clips.items() if n != "die" for x in c["penetrations"]}
    assert not pairs & {("headwear", "accessory_hand_r"), ("accessory_hand_r", "headwear")}, pairs
    assert not any(x["part"] == "hands" and x["into"] == "arms" and x["depth_m"] > 0.03
                   for c in clips.values() for x in c["penetrations"])
    # joint blends: the sleeves' inner ends no longer come out at the shoulder into beard/head
    # (before: 4-5 cm, 5-8 vertices in every clip; now at most a vertex where the arm really comes close)
    assert not any(x["part"] == "arms" and x["into"] in ("head", "face") and (x["depth_m"] > 0.025 or x["verts"] > 2)
                   for c in clips.values() for x in c["penetrations"])
    assert p["previews"] and p["previews"][0].endswith("pose_test.png")

    e = T_export.export("wizard")
    assert e["ok"], e.get("error")
    assert e["report"]["gltf_validator"]["animationCount"] == len(names)
    assert sorted(e["report"]["test_load"]["animations"]) == sorted(names)

