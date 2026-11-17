"""Generation & colour tools: assemble_from_parts, apply_palette, recolor."""
from __future__ import annotations

from .. import character as C
from ..blender import run_job
from ..style import load_style


def assemble_from_parts(name: str, spec: dict | None = None) -> dict:
    """Build workspace/<name>/character.blend from the spec (given, or the saved spec.json)."""
    C.check_name(name)
    if spec is not None:
        spec = {**(C.load_spec(name) or {}), **spec}
        spec.setdefault("name", name)
        if not C.is_prop(spec):
            spec.setdefault("archetype", load_style(spec.get("style"))["default_archetype"])
        C.save_spec(name, spec)
    spec = C.load_spec(name)
    if spec is None:
        raise C.CharacterError(f"character {name!r} has no spec; call init_character first")
    if C.is_prop(spec):   # STYLE.md §9b
        from .parts import props_dir
        blend = props_dir(C.style_of(name)) / f"{spec.get('part', name)}.blend"
        if not blend.exists():
            raise C.CharacterError(f"prop {spec.get('part', name)!r} not built yet ({blend}); use build_prop")
        r = run_job("assemble_prop", {"spec": spec, "part_blend": str(blend), "out": str(C.blend_path(name))},
                    style=C.style_of(name))
    else:
        r = run_job("assemble", {"spec": spec, "out": str(C.blend_path(name))}, style=C.style_of(name))
    if r.get("ok"):
        r["stats"]["spec_hash"] = C.spec_hash(spec)
    return r


def apply_palette(name: str) -> dict:
    st = load_style(C.style_of(name))
    if st.get("surface") != "palette":
        raise C.CharacterError(f"apply_palette works on the palette surface; style {st['style']!r} uses "
                               f"{st.get('surface')!r} (change spec.colors, then run paint_surface)")
    spec = C.load_spec(name) or {}
    blend = C.require(name)
    return run_job("apply_palette", {"colors": spec.get("colors") or {}, "out": str(blend)}, blend=blend, style=C.style_of(name))


def recolor(name: str, role: str, palette_index: int) -> dict:
    style = load_style(C.style_of(name))
    if style.get("surface") != "palette":
        raise C.CharacterError(f"recolor works on the palette surface; style {style['style']!r} uses {style.get('surface')!r}")
    if role not in style["roles"]:
        raise C.CharacterError(f"unknown role {role!r}; roles: {style['roles']}")
    n = style["palette"]["grid"] ** 2
    if not 0 <= int(palette_index) < n:
        raise C.CharacterError(f"palette index must be 0..{n - 1}")
    spec = C.load_spec(name) or {}
    spec.setdefault("colors", {})[role] = int(palette_index)
    C.save_spec(name, spec)
    r = apply_palette(name)
    r["stats"]["spec_hash"] = C.spec_hash(spec)
    return r
