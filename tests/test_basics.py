import pytest

from server import character as C
from server.blender import BlenderError, run_job
from server.palette import hex_to_rgb, palette_pixels, write_png
from server.paths import REPO
from server.style import dump_style, load_style


def test_palette_png_is_up_to_date(tmp_path):
    out = tmp_path / "p.png"
    s = load_style("clean")
    write_png(out, palette_pixels(s))
    assert out.read_bytes() == (REPO / s["palette"]["file"]).read_bytes()


def test_palette_layout_row0_is_top():
    s = load_style()
    rows = palette_pixels(s)
    cell = s["palette"]["cell"]
    assert rows[cell // 2][cell // 2] == hex_to_rgb(s["palette"]["colors"][0])
    assert rows[cell * 7 + 5][cell * 2 + 5] == hex_to_rgb(s["palette"]["colors"][58])


@pytest.mark.parametrize("name,ok", [("knight", True), ("forest-mage", True), ("Knight", False),
                                     ("forest_mage", False), ("-x", False), ("", False)])
def test_character_names(name, ok):
    if ok:
        assert C.check_name(name) == name
    else:
        with pytest.raises(C.CharacterError):
            C.check_name(name)


def test_spec_hash_ignores_approval_and_key_order():
    a = {"name": "x", "colors": {"skin": 2, "primary": 18}}
    b = {"colors": {"primary": 18, "skin": 2}, "name": "x", "approval": {"by": "marcel"}}
    assert C.spec_hash(a) == C.spec_hash(b)
    assert C.spec_hash(a) != C.spec_hash({**a, "seed": 1})


def test_unknown_job():
    with pytest.raises(BlenderError):
        run_job("does_not_exist")


def test_dump_style_roundtrip():
    import json
    s = load_style()
    assert json.loads(dump_style(s)) == s
