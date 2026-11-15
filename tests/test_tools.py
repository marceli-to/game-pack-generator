"""End-to-end through the tool functions (what the MCP server calls)."""
import asyncio
import shutil

import pytest

from server.blender import run_job_checked
from server.main import mcp
from server.tools import export as T_export
from server.tools import project as T_project
from server.tools import qa as T_qa

from .conftest import needs_blender, needs_node

PHASE1_TOOLS = {"get_style", "init_character", "import_glb", "stats", "render_preview", "validate", "export"}


def test_mcp_lists_phase1_tools():
    names = {t.name for t in asyncio.run(mcp.list_tools())}
    assert PHASE1_TOOLS <= names


def test_init_character_rejects_bad_names(workspace):
    with pytest.raises(Exception):
        T_project.init_character("Bad_Name")


@needs_blender
@needs_node
def test_mannequin_exports_and_plays(workspace, mannequin):
    T_project.init_character("mannequin")
    shutil.copy(mannequin, workspace / "mannequin" / "character.blend")
    r = T_export.export("mannequin")
    assert r["ok"], r.get("error")
    rep = r["report"]
    assert rep["valid_style"] is True
    assert rep["gltf_validator"]["errors"] == 0
    assert rep["gltf_validator"]["warnings"] == 0
    assert rep["test_load"]["playing"] == "idle"
    assert set(rep["test_load"]["animations"]) >= {"idle", "walk", "run"}


@needs_blender
@needs_node
def test_import_any_glb_check_render_export(workspace, mannequin, tmp_path):
    """Phase 1 'done when': import any GLB, check it, render it, export it."""
    glb = tmp_path / "external.glb"
    run_job_checked("export_glb", {"out": str(glb)}, blend=mannequin)

    r = T_project.init_character("external")
    assert r["ok"]
    r = T_project.import_glb("external", str(glb), normalize=True)
    assert r["ok"] and r["stats"]["imported"]["armature"] == ["Armature"]

    st = T_qa.stats("external")
    assert st["ok"] and st["stats"]["tris"] == 216

    v = T_qa.validate("external")
    assert v["ok"]
    # glTF carries no face attributes, so an imported GLB has no roles: that's a hard violation.
    assert "no_role" in [h["code"] for h in v["hard"]]

    p = T_qa.render_preview("external")
    assert p["ok"] and p["previews"]

    e = T_export.export("external")
    assert e["ok"], e.get("error")
    assert e["report"]["valid_style"] is False
