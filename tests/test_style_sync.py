"""The JSON twins must agree with the docs: core.json <-> STYLE.md (shared rules) and, for every style,
styles/<name>/style.json <-> styles/<name>/STYLE.md (the look)."""
import json
import re

import pytest

from server.paths import CORE_JSON, REPO, STYLES
from server.style import available_styles, load_style

STYLE_MD = (REPO / "STYLE.md").read_text()          # shared rules
S = load_style()
STYLES_ALL = available_styles()


def style_md(name):
    return (STYLES / name / "STYLE.md").read_text()


def test_core_and_styles_do_not_overlap():
    core = set(json.loads(CORE_JSON.read_text())) - {"_comment"}
    for name in STYLES_ALL:
        st = set(json.loads((STYLES / name / "style.json").read_text())) - {"_comment"}
        assert not core & st, (name, core & st)
        assert load_style(name)["style"] == name
        assert f"`{name}`" in STYLE_MD, f"style {name} missing from the table in STYLE.md"


@pytest.mark.parametrize("name", STYLES_ALL)
def test_budgets_match(name):
    S, STYLE_MD = load_style(name), style_md(name)
    b = S["budget"]
    assert f"| Character complete | {b['character']['target'][0]:,}–{b['character']['target'][1]:,} tris | {b['character']['hard']:,} |" in STYLE_MD
    assert f"| Head incl. hair/headwear | ≤ {b['head']['target']:,} | {b['head']['hard']:,} |" in STYLE_MD
    assert f"| Hand-held accessory (weapon, tool) | ≤ {b['accessory_hand']['target']:,} | {b['accessory_hand']['hard']:,} |" in STYLE_MD
    assert f"| Back accessory (cape, backpack) | ≤ {b['accessory_back']['target']:,} | {b['accessory_back']['hard']:,} |" in STYLE_MD
    assert f"| Prop (later) | ≤ {b['prop']['target']:,} | {b['prop']['hard']:,} |" in STYLE_MD


@pytest.mark.parametrize("name", STYLES_ALL)
def test_archetypes_match(name):
    S, STYLE_MD = load_style(name), style_md(name)
    for arch, a in S["archetypes"].items():
        lo, hi = a["height"]
        assert re.search(rf"\| `{arch}`[^|]*\| {lo}–{hi} \|", STYLE_MD), arch
    assert f"at most {round(S['headwear_max_ratio'] * 100)} %" in STYLE_MD


@pytest.mark.parametrize("name", [n for n in STYLES_ALL if load_style(n).get("surface") == "palette"])
def test_palette_matches(name):
    S, md = load_style(name), style_md(name)
    p = S["palette"]
    assert f"{p['size']} × {p['size']} px, {p['grid']} × {p['grid']} grid" in md
    assert len(p["colors"]) == p["grid"] ** 2
    assert f"Max. **{p['max_colors']} different colours**" in md


def test_roles_match():
    roles_md = ", ".join(f"`{i} {r}`" for i, r in enumerate(S["roles"]))
    assert roles_md.replace("`8 dark`", "`8 dark` (mouth, inner sleeves, soles)").replace(
        "`9 special`", "`9 special` (glow, crystals)") in STYLE_MD


@pytest.mark.parametrize("name", STYLES_ALL)
def test_shading_matches(name):
    S, STYLE_MD = load_style(name), style_md(name)
    sh = S["shading"]
    assert sh["mode"] in ("smooth_by_angle", "flat")
    if sh["mode"] == "flat":
        assert "**Flat shading**" in STYLE_MD
    else:
        assert f"**Smooth by angle, {sh['crease_deg']}°**" in STYLE_MD


def test_slots_match():
    assert "- Slots: " + ", ".join(f"`{s}`" for s in S["slots"]) in STYLE_MD


def test_skeleton_bones_appear_in_style_md():
    for b in S["skeleton"]["bones"]:
        base = b["name"]
        assert base in STYLE_MD or base.replace(".r", ".l") in STYLE_MD, base
    deform = sum(b["deform"] for b in S["skeleton"]["bones"])
    assert f"{deform} deforming bones" in STYLE_MD


def test_animation_mapping_matches():
    for c in S["animations"]["clips"]:
        row = re.search(rf"\| `{c['name']}` \| `{c['source']}` \([A-Za-z]+\) \| (yes|no) \|", STYLE_MD)
        assert row, c["name"]
        assert (row.group(1) == "yes") == c["loop"], c["name"]
        assert c["file"].startswith("Rig_Medium_")


def test_blender_version_pinned_everywhere():
    v = S["blender"]["version"]
    assert v in (REPO / "README.md").read_text()


def test_unknown_style_is_rejected():
    from server.style import StyleError, style_name
    with pytest.raises(StyleError):
        style_name("no-such-style")


@pytest.mark.parametrize("name", [n for n in STYLES_ALL if load_style(n).get("surface") == "painted"])
def test_paint_approaches_documented(name):
    S, md = load_style(name), style_md(name)
    p = S["paint"]
    for a in p["approaches"]:
        assert f"`{a}`" in md, a
    assert p["default_approach"] in p["approaches"]
    if "ai" in p["approaches"]:
        ai = p["ai"]
        assert (STYLES / name / ai["style_ref"]).exists()
        assert f"`steps` {ai['steps']}" in md
        for key in ("view_size", "frame_margin", "depth_subsurf", "crease_deg", "projection"):
            assert f"`ai.{key}`" in md, key
