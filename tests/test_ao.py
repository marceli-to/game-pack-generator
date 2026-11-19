"""Baked ambient occlusion in vertex colours (STYLE.md §5, `shading.ao`): the tinfox guard."""
import json

from server.paths import REPO
from server.style import load_style
from server.tools import assemble as T_assemble
from server.tools import export as T_export
from server.tools import project as T_project
from server.tools import qa as T_qa

from .conftest import needs_blender, needs_node


def test_ao_only_where_documented():
    assert load_style("tinfox")["shading"].get("ao")
    for name in ("clean", "lowpoly", "painted"):   # approved/other looks stay without vertex colours
        assert not load_style(name)["shading"].get("ao"), name


@needs_blender
@needs_node
def test_guard_bakes_ao_and_exports_vertex_colours(workspace):
    spec = json.loads((REPO / "specs" / "guard" / "spec.json").read_text())
    T_project.init_character("guard", spec)
    r = T_assemble.assemble_from_parts("guard")
    assert r["ok"], r.get("error")
    ao, cfg = r["stats"]["ao"], load_style("tinfox")["shading"]["ao"]
    assert ao and ao["corners"] > 6000   # guard after the facet pass: ~8,600 corners
    assert ao["p5"] >= cfg["floor"] - 1e-6 and ao["p95"] > 0.95   # open surfaces stay at full brightness
    assert ao["p50"] < 0.9                                        # ...but creases get darker

    v = T_qa.validate("guard")
    assert v["valid"], v["hard"]
    assert not any(s["code"] in ("vertex_colors", "no_ao") for s in v["soft"]), v["soft"]

    e = T_export.export("guard")
    assert e["ok"], e.get("error")
    g = e["report"]["gltf"]
    assert g["vertex_colors"] and g["texcoords"] == 1
    assert not any(m["unlit"] for m in g["materials"])            # lit: the game's lights still apply
    assert not any(m["double_sided"] for m in g["materials"])     # closed shells: single-sided (REVIEW.md B2)
