"""Phase 2: parts, assembly, palette, reference comparison."""
import json

import pytest

from server import character as C
from server.blender import run_job
from server.paths import REPO
from server.style import load_style
from server.tools import assemble as T_assemble
from server.tools import parts as T_parts
from server.tools import project as T_project
from server.tools import qa as T_qa

from .conftest import needs_blender

MAGE_SPEC = REPO / "specs" / "mage" / "spec.json"
MAGE_REF = "specs/mage/reference/turnaround.webp"
MAGE_VIEWS = {"front": {"center_x": 254, "x_range": [0, 498]}, "side": {"center_x": 650, "x_range": [498, 831]},
              "back": {"center_x": 1072, "x_range": [831, 1309]}}

GOOD = 'P.box((-0.1, -0.1, 1.4), (0.1, 0.1, 1.8), "skin")'


def test_part_names():
    assert T_parts.split("accessory_hand_r-staff-crystal") == ("accessory_hand_r", "staff-crystal")
    assert T_parts.split("head-round") == ("head", "round")
    for bad in ("round", "head-", "head-Round", "hat-wizard"):
        with pytest.raises(T_parts.PartError):
            T_parts.split(bad)


def build(tmp_path, script, part="head-test"):
    return run_job("build_part", {"part": part, "script": script, "out_dir": str(tmp_path), "save": True})


@needs_blender
def test_build_part_valid(tmp_path):
    r = build(tmp_path, GOOD)
    assert r["ok"], r.get("error")
    assert r["stats"]["tris"] == 12 and r["stats"]["roles"] == ["skin"]
    assert (tmp_path / "head-test.blend").exists() and r["previews"]
    assert any("head top" in w for w in r["soft"]) is False


@needs_blender
@pytest.mark.parametrize("script,needle", [
    # face built with raw bmesh and no role
    (GOOD + "\nv = [P.bm.verts.new(c) for c in ((0, 0, 2), (0.1, 0, 2), (0, 0.1, 2), (0, 0, 2.1))]\n"
            "for f in ((0, 2, 1), (0, 1, 3), (1, 2, 3), (0, 3, 2)): P.bm.faces.new([v[i] for i in f])",
     "without a role"),
    # open shell
    (GOOD + "\nP.bm.faces.remove(P.bm.faces[:][0])", "non-manifold"),
    # weight to a bone the slot may not use
    ('P.box((-0.1, -0.1, 1.4), (0.1, 0.1, 1.8), "skin", bone="hand.l")', "not an allowed bone"),
    # over the head budget
    ("\n".join(f'P.box(({i * 0.07}, 0, 1.4), ({i * 0.07 + 0.05}, 0.05, 1.8), "skin")' for i in range(90)),
     "hard limit"),
])
def test_build_part_rejects(tmp_path, script, needle):
    r = build(tmp_path, script)
    assert not r["ok"]
    assert any(needle in h for h in r["hard"]), r["hard"]
    assert not (tmp_path / "head-test.blend").exists()


@needs_blender
def test_mage_assembles_valid(workspace):
    spec = json.loads(MAGE_SPEC.read_text())
    T_project.init_character("mage", {"archetype": "human"})
    r = T_assemble.assemble_from_parts("mage", spec)
    assert r["ok"], r.get("error")
    v = T_qa.validate("mage")
    assert v["valid"], v["hard"]
    assert v["soft"] == []
    st = v["stats"]
    assert st["body_height"] == pytest.approx(1.8, abs=0.005)
    assert st["has_slot"] and st["objects"] == ["Character"]
    assert st["tris"] <= load_style()["budget"]["character"]["target"][1]
    assert len(st["palette_indices"]) <= 8
    assert st["unweighted_verts"] == 0
    # smooth by angle (STYLE.md §5): every face smooth, every crease marked sharp
    assert st["flat_faces"] == 0 and st["unmarked_creases"] == 0

    # recolor: one role, one palette index, the spec follows
    r = T_assemble.recolor("mage", "primary", 37)
    assert r["ok"] and 37 in r["stats"]["palette_indices"] and 34 not in r["stats"]["palette_indices"]
    assert C.load_spec("mage")["colors"]["primary"] == 37


@needs_blender
def test_proportions_not_supported_yet(workspace):
    spec = json.loads(MAGE_SPEC.read_text())
    spec["proportions"] = {"legs": 0.9}
    T_project.init_character("mage", {"archetype": "human"})
    r = T_assemble.assemble_from_parts("mage", spec)
    assert not r["ok"] and "not supported yet" in r["error"]


@needs_blender
def test_mage_matches_reference(workspace):
    spec = json.loads(MAGE_SPEC.read_text())
    T_project.init_character("mage", spec)
    assert T_assemble.assemble_from_parts("mage")["ok"]
    r = T_project.add_reference("mage", MAGE_REF, MAGE_VIEWS, top_y=260, floor_y=1003, height_m=1.8)
    assert r["ok"], r.get("error")
    c = T_qa.compare_reference("mage")
    assert c["ok"], c.get("error")
    assert c["stats"]["hidden_faces"] > 0  # the staff is drawn beside the character
    for view, iou in c["stats"]["iou"].items():
        assert iou >= 0.8, (view, iou)


def test_parts_catalog_lists_library():
    listing = T_parts.list_parts()["parts"]
    spec = json.loads(MAGE_SPEC.read_text())
    have = {p["part"] for ps in listing.values() for p in ps}
    assert {p for p in spec["parts"].values() if p} <= have
    for slot, ps in listing.items():
        for p in ps:
            assert (REPO / load_style()["parts"]["dir"] / slot / f"{p['part']}.py").exists()


@needs_blender
def test_render_parts_catalog(workspace):
    r = T_parts.render_parts_catalog(parts=["head-round", "hands-mitten"])
    assert r["ok"], r.get("error")
    assert r["stats"]["rows"] == {"head": ["head-round"], "hands": ["hands-mitten"]}
    assert any(o.endswith("catalog.html") for o in r["outputs"])


@pytest.mark.parametrize("name", ["mage", "wizard"])
def test_approval_still_valid(name):
    """STYLE.md §14: the approval binds to the spec hash and to every part's build script."""
    import hashlib

    spec = json.loads((REPO / "specs" / name / "spec.json").read_text())
    ap = spec["approval"]
    assert ap["spec_hash"] == C.spec_hash(spec), "spec changed since approval"
    parts_dir = REPO / load_style(spec.get("style"))["parts"]["dir"]
    for slot, part in spec["parts"].items():
        if part:
            script = (parts_dir / slot / f"{part}.py").read_bytes()
            assert ap["parts"][part] == "sha256:" + hashlib.sha256(script).hexdigest(), f"{part} rebuilt since approval"
