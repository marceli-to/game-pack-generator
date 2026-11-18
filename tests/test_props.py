"""Props (STYLE.md §9b): build with anchors, assemble on the grip, validate, export with named nodes."""
import json
import struct

import pytest

from server.blender import run_job
from server.tools import parts as T_parts
from server.tools.export import glb_nodes

from .conftest import needs_blender, needs_node

# a toy gun lying along +X: body, barrel, handle; grip on the handle, muzzle at the barrel tip
GUN = """
P.box((0.0, -0.02, 0.10), (0.16, 0.02, 0.16), "primary")
P.cylinder((0.15, 0, 0.13), (0.24, 0, 0.13), 0.015, n=8, role="accent")
P.box((0.02, -0.018, 0.0), (0.06, 0.018, 0.11), "secondary")
P.anchor("grip", (0.04, 0, 0.05))
P.anchor("muzzle", (0.24, 0, 0.13))
"""
SPEC = {"name": "toygun", "kind": "prop", "type": "weapon", "style": "tinfox", "part": "toygun",
        "colors": {"primary": 52, "secondary": 54, "accent": 19}}


def test_prop_names_and_types():
    with pytest.raises(T_parts.PartError):
        T_parts.build_prop("Toy Gun", GUN, "weapon", style="tinfox")
    with pytest.raises(T_parts.PartError):
        T_parts.build_prop("toygun", GUN, "rocket", style="tinfox")
    with pytest.raises(T_parts.PartError):   # lowpoly has no weapon budget
        T_parts.build_prop("toygun", GUN, "weapon", style="lowpoly")


@needs_blender
def test_build_prop_rejects_missing_anchor(tmp_path):
    r = run_job("build_prop", {"prop": "toygun", "type": "weapon", "script": GUN.replace('P.anchor("muzzle"', '# ('),
                               "out_dir": str(tmp_path), "save": True}, style="tinfox")
    assert not r["ok"] and "muzzle" in r["error"]
    r = run_job("build_prop", {"prop": "toygun", "type": "weapon",
                               "script": GUN.replace("(0.24, 0, 0.13))\n", "(-0.1, 0, 0.13))\n"),
                               "out_dir": str(tmp_path), "save": True}, style="tinfox")
    assert not r["ok"] and "in front of the grip" in r["error"]


@needs_blender
@needs_node
def test_prop_end_to_end(tmp_path):
    from server import node
    r = run_job("build_prop", {"prop": "toygun", "type": "weapon", "script": GUN, "out_dir": str(tmp_path), "save": True},
                style="tinfox")
    assert r["ok"], r.get("error")
    assert r["stats"]["anchors"] == {"grip": [0.04, 0.0, 0.05], "muzzle": [0.24, 0.0, 0.13]}
    blend = tmp_path / "prop.blend"
    a = run_job("assemble_prop", {"spec": SPEC, "part_blend": str(tmp_path / "toygun.blend"), "out": str(blend)},
                style="tinfox")
    assert a["ok"], a.get("error")
    assert a["stats"]["anchors"]["grip"] == [0.0, 0.0, 0.0]
    assert a["stats"]["anchors"]["muzzle"] == pytest.approx([0.2, 0.0, 0.08], abs=1e-4)
    assert a["stats"]["ao"] is not None   # tinfox bakes AO (prop_distance)
    v = run_job("validate", {"spec": SPEC}, blend=blend, style="tinfox")
    assert v["ok"] and v["valid"], v["hard"]
    assert not [w for w in v["soft"] if w["code"] in ("objects", "no_ao", "armature")], v["soft"]
    # a grip moved off the origin is a hard error
    bad = run_job("validate", {"spec": {**SPEC, "type": "pickup"}}, blend=blend, style="tinfox")
    assert any(h["code"] == "origin" for h in bad["hard"])
    glb = tmp_path / "prop-toygun.glb"
    e = run_job("export_glb", {"out": str(glb)}, blend=blend, style="tinfox")
    assert e["ok"], e.get("error")
    nodes = glb_nodes(glb)
    assert set(nodes) == {"toygun", "grip", "muzzle"}
    # glTF: +X stays the muzzle direction, Blender +Z becomes +Y (STYLE.md §9b: the frame of handslot.r)
    assert nodes["grip"] == [0, 0, 0] or nodes["grip"] == pytest.approx([0, 0, 0], abs=1e-6)
    assert nodes["muzzle"] == pytest.approx([0.2, 0.08, 0.0], abs=1e-4)
    gv = node.gltf_validate(glb)
    assert gv["errors"] == 0, gv
    data = glb.read_bytes()
    j = json.loads(data[20:20 + struct.unpack("<I", data[12:16])[0]])
    assert not j.get("skins") and not j.get("animations")
    assert all(s.get("minFilter") == 9728 for s in j.get("samplers", []))
    prims = [p for m in j["meshes"] for p in m["primitives"]]
    assert all("COLOR_0" in p["attributes"] for p in prims)


# a toy target: post (main mesh), board as a separate piece hanging off the hinge, board_centre moving with it
TARGET = """
P.box((-0.03, -0.03, 0.0), (0.03, 0.03, 0.5), "primary")
P.anchor("hinge", (0, 0, 0.5))
P.piece("board", parent="hinge")
P.box((-0.2, -0.04, 0.5), (0.2, -0.02, 0.9), "accent")
P.anchor("board_centre", (0, -0.04, 0.7), piece="board")
"""
TSPEC = {"name": "toytarget", "kind": "prop", "type": "target", "style": "tinfox", "part": "toytarget",
         "colors": {"primary": 52, "accent": 16}}


@needs_blender
@needs_node
def test_prop_pieces_export_as_child_nodes(tmp_path):
    from server import node
    bad = run_job("build_prop", {"prop": "toytarget", "type": "target", "script": TARGET.replace('P.piece("board"', 'P.piece("plate"'),
                                 "out_dir": str(tmp_path), "save": True}, style="tinfox")
    assert not bad["ok"] and "'board'" in bad["error"]
    r = run_job("build_prop", {"prop": "toytarget", "type": "target", "script": TARGET, "out_dir": str(tmp_path),
                               "save": True}, style="tinfox")
    assert r["ok"], r.get("error")
    assert r["stats"]["pieces"] == {"(main)": 6, "board": 6}   # faces
    blend = tmp_path / "prop.blend"
    a = run_job("assemble_prop", {"spec": TSPEC, "part_blend": str(tmp_path / "toytarget.blend"), "out": str(blend)},
                style="tinfox")
    assert a["ok"], a.get("error")
    v = run_job("validate", {"spec": TSPEC}, blend=blend, style="tinfox")
    assert v["ok"] and v["valid"], v["hard"]   # still one mesh until export
    glb = tmp_path / "prop-toytarget.glb"
    e = run_job("export_glb", {"out": str(glb)}, blend=blend, style="tinfox")
    assert e["ok"], e.get("error")
    data = glb.read_bytes()
    j = json.loads(data[20:20 + struct.unpack("<I", data[12:16])[0]])
    nodes = {n["name"]: n for n in j["nodes"]}
    names = [n["name"] for n in j["nodes"]]
    assert {names[i] for i in j["scenes"][0]["nodes"]} == {"toytarget", "hinge"}
    assert [names[i] for i in nodes["hinge"]["children"]] == ["board"]
    assert [names[i] for i in nodes["board"]["children"]] == ["board_centre"]
    assert nodes["hinge"]["translation"] == pytest.approx([0, 0.5, -0.005], abs=1e-5)   # footprint centred (floor origin)
    assert "translation" not in nodes["board"]   # origin at the hinge: turning the hinge turns the board
    assert nodes["board_centre"]["translation"] == pytest.approx([0, 0.2, 0.04], abs=1e-5)
    assert node.gltf_validate(glb)["errors"] == 0
