"""End-to-end through the tool functions (what the MCP server calls)."""
import asyncio
import os
import shutil

import pytest

from server import ai as AI
from server.blender import run_job_checked
from server.main import mcp
from server.tools import assemble as T_assemble
from server.tools import export as T_export
from server.tools import paint as T_paint
from server.tools import project as T_project
from server.tools import qa as T_qa

from .conftest import needs_blender, needs_node

PHASE1_TOOLS = {"get_style", "init_character", "import_glb", "stats", "render_preview", "validate", "export",
                "add_reference", "build_part", "list_parts", "render_parts_catalog", "assemble_from_parts",
                "apply_palette", "recolor", "compare_reference", "paint_surface", "apply_animations", "pose_test"}


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

    e = T_export.export("external", allow_hard=True)   # imported GLBs always fail no_role
    assert e["ok"], e.get("error")
    assert e["report"]["valid_style"] is False


@needs_blender
@needs_node
def test_painted_character_paints_validates_and_exports_unlit(workspace, mannequin):
    """Painted surface: validate demands paint, paint_surface bakes it (deterministic per seed), the GLB is
    unlit with one UV set and a linear sampler; apply_palette refuses the painted style."""
    colors = {"skin": 6, "primary": 17, "secondary": 46, "accent": 42, "metal": 40, "leather": 45,
              "dark": 54, "special": 32, "hair": 8, "eyes": 56}
    T_project.init_character("painted-dummy", {"style": "painted", "colors": colors})
    shutil.copy(mannequin, workspace / "painted-dummy" / "character.blend")

    v = T_qa.validate("painted-dummy")
    assert "not_painted" in [h["code"] for h in v["hard"]]
    with pytest.raises(Exception, match="palette surface"):
        T_assemble.apply_palette("painted-dummy")

    r = T_paint.paint_surface("painted-dummy", seed=3)
    assert r["ok"], r.get("error")
    assert r["stats"]["unlit"] is True and r["stats"]["approach"] == "auto"
    assert T_project.C.load_spec("painted-dummy")["paint"] == {"seed": 3}
    first = r["stats"]["texture_sha256"]
    assert T_paint.paint_surface("painted-dummy")["stats"]["texture_sha256"] == first, "paint not deterministic"

    v = T_qa.validate("painted-dummy")
    codes = {h["code"] for h in v["hard"]} | {s["code"] for s in v["soft"]}
    surface = {"not_painted", "materials", "texture", "texture_size", "uv_missing", "uv_outside", "uv_overlap",
               "not_unlit", "uv_layers", "material_name", "colours"}
    assert not codes & surface, codes & surface
    assert v["stats"]["uv_layers"] == ["Paint"] and v["stats"]["unlit"] is True

    e = T_export.export("painted-dummy", allow_hard=True)   # a test mannequin: height is not the point here
    assert e["ok"], e.get("error")
    g = e["report"]["gltf"]
    assert "KHR_materials_unlit" in g["extensions_used"]
    assert g["materials"] == [{"name": "M_Painted", "unlit": True, "double_sided": False}]
    assert g["texcoords"] == 1
    assert g["samplers"][0]["magFilter"] == 9729  # LINEAR
    assert e["report"]["gltf_validator"]["errors"] == 0


@needs_blender
def test_ai_paint_needs_subject_and_environment(workspace, mannequin, monkeypatch):
    """approach 'ai' refuses to run without a subject or without the AI environment (before any Blender run)."""
    T_project.init_character("ai-dummy", {"style": "painted", "colors": {"primary": 17}})
    shutil.copy(mannequin, workspace / "ai-dummy" / "character.blend")
    with pytest.raises(Exception, match="needs a subject"):
        T_paint.paint_surface("ai-dummy", approach="ai")
    monkeypatch.setenv("GPG_AI_PYTHON", "/nonexistent/python")
    with pytest.raises(Exception, match="AI environment"):
        T_paint.paint_surface("ai-dummy", approach="ai", subject="a test dummy")
    assert T_project.C.load_spec("ai-dummy")["paint"] == {"approach": "ai", "subject": "a test dummy"}
    with pytest.raises(Exception, match="unknown roles"):
        T_paint.paint_surface("ai-dummy", keep_roles=["face"])
    with pytest.raises(Exception, match="AI environment"):
        T_paint.paint_surface("ai-dummy", keep_roles=["skin", "eyes"])
    assert T_project.C.load_spec("ai-dummy")["paint"]["keep_roles"] == ["skin", "eyes"]


@needs_blender
@pytest.mark.skipif(os.environ.get("GPG_AI_TESTS") != "1" or not AI.available(),
                    reason="AI generation test: set GPG_AI_TESTS=1 (needs ai/.venv and ~13 GB of cached models)")
def test_ai_paint_end_to_end(workspace, mannequin):
    """Full `ai` approach on the mannequin: auto -> guides -> SDXL -> projection; validates clean."""
    colors = {"skin": 6, "primary": 17, "secondary": 46, "accent": 42, "metal": 40, "leather": 45,
              "dark": 54, "special": 32, "hair": 8, "eyes": 56}
    T_project.init_character("ai-dummy", {"style": "painted", "colors": colors})
    shutil.copy(mannequin, workspace / "ai-dummy" / "character.blend")
    r = T_paint.paint_surface("ai-dummy", approach="ai", subject="chibi wooden training dummy, blue cloth wraps",
                              keep_roles=["eyes"])
    assert r["ok"], r.get("error")
    st = r["stats"]
    assert st["kept_texels"] > 0
    assert st["approach"] == "ai" and st["ai"]["gen_s"] > 0 and 0 < st["projection"]["coverage"] <= 1
    v = T_qa.validate("ai-dummy")
    assert not {h["code"] for h in v["hard"]} & {"not_painted", "texture", "uv_overlap", "not_unlit"}
