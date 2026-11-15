"""style.json and STYLE.md must agree on the values the tools read."""
import re

from server.paths import REPO
from server.style import load_style

STYLE_MD = (REPO / "STYLE.md").read_text()
S = load_style()


def test_budgets_match():
    b = S["budget"]
    assert f"| Character complete | {b['character']['target'][0]:,}–{b['character']['target'][1]:,} tris | {b['character']['hard']:,} |" in STYLE_MD
    assert f"| Head incl. hair/headwear | ≤ {b['head']['target']:,} | {b['head']['hard']:,} |" in STYLE_MD
    assert f"| Hand-held accessory (weapon, tool) | ≤ {b['accessory_hand']['target']:,} | {b['accessory_hand']['hard']:,} |" in STYLE_MD
    assert f"| Back accessory (cape, backpack) | ≤ {b['accessory_back']['target']:,} | {b['accessory_back']['hard']:,} |" in STYLE_MD
    assert f"| Prop (later) | ≤ {b['prop']['target']:,} | {b['prop']['hard']:,} |" in STYLE_MD


def test_archetypes_match():
    for name, a in S["archetypes"].items():
        lo, hi = a["height"]
        assert re.search(rf"\| `{name}`[^|]*\| {lo}–{hi} \|", STYLE_MD), name
    assert "at most 60 %" in STYLE_MD and S["headwear_max_ratio"] == 0.6


def test_palette_and_roles_match():
    p = S["palette"]
    assert f"{p['size']} × {p['size']} px, {p['grid']} × {p['grid']} grid" in STYLE_MD
    assert len(p["colors"]) == p["grid"] ** 2
    assert f"Max. **{p['max_colors']} different colours**" in STYLE_MD
    roles_md = ", ".join(f"`{i} {r}`" for i, r in enumerate(S["roles"]))
    assert roles_md.replace("`8 dark`", "`8 dark` (mouth, inner sleeves, soles)").replace(
        "`9 special`", "`9 special` (glow, crystals)") in STYLE_MD


def test_shading_matches():
    sh = S["shading"]
    assert sh["mode"] == "smooth_by_angle"
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
