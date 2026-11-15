"""MCP server (stdio). Run:  .venv/bin/python -m server.main

Each tool spawns one headless Blender process (see server/blender.py) and returns
{ ok, outputs, stats, previews, warnings, error? }. Look at the preview PNGs.
"""
from __future__ import annotations

import functools
import traceback

from mcp.server.mcpserver import MCPServer

from .tools import assemble as T_assemble
from .tools import export as T_export
from .tools import paint as T_paint
from .tools import parts as T_parts
from .tools import project as T_project
from .tools import qa as T_qa

INSTRUCTIONS = """\
Headless tool for stylised low-poly game characters (Blender + GLB for three.js).
STYLE.md (shared rules) + styles/<style>/STYLE.md (the look) are the law; read them with get_style.
A character's spec names its style (spec.style); parts belong to a style (pass style= to part tools).
Characters live in workspace/<name>/.
Build a character: get_style -> init_character -> add_reference -> list_parts /
render_parts_catalog (build missing parts with build_part) -> assemble_from_parts ->
[painted styles: paint_surface] -> validate -> compare_reference (max. 3 correction rounds, then ask
the human) -> export. Re-run paint_surface after every assemble_from_parts on a painted style.
Check an existing model: init_character -> import_glb -> stats / validate -> render_preview -> export.
Every result lists preview images: open them to see what you did.
"""

mcp = MCPServer("game-pack-generator", instructions=INSTRUCTIONS)


def _safe(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001 - tools report errors as data
            return {"ok": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc(limit=3)}
    return wrapper


@mcp.tool()
@_safe
def get_style(style: str | None = None) -> dict:
    """Return the merged style (core.json + styles/<style>/style.json; default style if omitted):
    budgets, units, archetypes, surface/palette, colour roles, slots,
    skeleton (bone names/parents) and animation names. Read this before building anything."""
    return T_project.get_style(style)


@mcp.tool()
@_safe
def init_character(name: str, spec: dict | None = None, overwrite: bool = False) -> dict:
    """Create workspace/<name>/ with an empty character.blend and spec.json.
    name: kebab-case (e.g. 'forest-mage'). spec: optional character spec (archetype, proportions,
    parts, colors as {role: palette_index}); defaults to archetype 'human'."""
    return T_project.init_character(name, spec, overwrite)


@mcp.tool()
@_safe
def import_glb(name: str, path: str, normalize: bool = False) -> dict:
    """Import a GLB into the character's .blend (e.g. an external CC0 model to check against the
    rules). normalize=true applies rotation/scale and renames a single armature/mesh to
    'Armature'/'Character'."""
    return T_project.import_glb(name, path, normalize)


@mcp.tool()
@_safe
def stats(name: str) -> dict:
    """Measure the character in rest pose: tris, verts, materials, texture, body height (without
    hair/headwear), palette colours, roles, per-slot tris, topology counts, skeleton, actions."""
    return T_qa.stats(name)


@mcp.tool()
@_safe
def render_preview(name: str, views: list[str] | None = None, pose: str = "rest") -> dict:
    """Render the turnaround sheet (front, side, back, 3/4) to workspace/<name>/renders/.
    pose: 'rest' or '<action>@<frame>' (e.g. 'walk@8'). Open the returned sheet PNG."""
    return T_qa.render_preview(name, views, pose)


@mcp.tool()
@_safe
def validate(name: str) -> dict:
    """Check every STYLE.md §12 rule. Returns valid (no hard violations), hard[], soft[], info[]
    and the measured stats. Hard violations block approval; soft ones need a human decision."""
    return T_qa.validate(name)


@mcp.tool()
@_safe
def export(name: str) -> dict:
    """Export workspace/<name>/export/character-<name>.glb per STYLE.md §10, run the Khronos glTF
    validator and a headless three.js test load (plays 'idle', screenshot). ok=false if the
    validator reports errors or the test load fails. Style violations are reported, not blocking."""
    return T_export.export(name)


@mcp.tool()
@_safe
def add_reference(name: str, image: str, views: dict, top_y: float, floor_y: float,
                  height_m: float | None = None, extent_m: float = 2.6) -> dict:
    """Store a turnaround sheet and cut square, same-scale crops per view into
    workspace/<name>/reference/ (used by compare_reference).
    views: {"front": {"center_x": px, "x_range": [x0, x1]}, "side": ..., "back": ...}; center_x is the
    column of the body axis, x_range keeps neighbouring views out of the crop.
    top_y / floor_y: pixel rows of the skull top and the floor; together = height_m (default: middle of
    the archetype's height range). extent_m: width/height of each crop in metres."""
    return T_project.add_reference(name, image, views, top_y, floor_y, height_m, extent_m)


@mcp.tool()
@_safe
def build_part(part: str, script: str, archetype: str | None = None, overwrite: bool = False,
               style: str | None = None) -> dict:
    """Build a library part '<slot>-<variant>' (e.g. 'headwear-wizard-hat') from a bpy script run
    against the archetype's proportion template. Saved to styles/<style>/parts/<slot>/ (.blend, .py, .json,
    .png) only if it passes the hard checks (roles on every face, closed shells, budget, allowed bones).
    In the script: P = builder (P.loft(rings, role), P.ring(center, rx, ry, n, axis), P.rect(...),
    P.rrect(center, sx, sy, r, seg, axis), P.box(lo, hi, role), P.rbox(lo, hi, role, r, bevel, seg, axis)
    (bevelled box), P.cylinder(a, b, r, n, role), P.mirror_x(faces), P.transform(faces, M),
    P.set_role(faces, role), P.set_bone(faces, bone), P.bm raw bmesh), lm = template landmarks
    (Vector: head_top, head_base, shoulder.l, elbow.l, wrist.l, hip.l, knee.l, ankle.l, toes.l,
    handslot.r, ...), bones = {name: (head, tail)}, guides, Vector, Matrix, math.
    Model in metres, -Y forward, +Z up, T-pose; left side is +X. Follow the STYLE.md §3 segment & bevel
    guide (12-16 sides for round shapes, bevelled boxes). Look at the returned preview."""
    return T_parts.build_part(part, script, archetype, overwrite, style)


@mcp.tool()
@_safe
def list_parts(slot: str | None = None, style: str | None = None) -> dict:
    """List a style's library parts per slot (name, archetypes, tris, roles)."""
    return T_parts.list_parts(slot, style)


@mcp.tool()
@_safe
def render_parts_catalog(slot: str | None = None, parts: list[str] | None = None, style: str | None = None) -> dict:
    """Preview sheet of library parts (one row per part: front, side, 3/4), in stats.rows order."""
    return T_parts.render_parts_catalog(slot, parts, style)


@mcp.tool()
@_safe
def assemble_from_parts(name: str, spec: dict | None = None) -> dict:
    """Build the character from spec.parts ({slot: part}) on the standard skeleton: slot attribute,
    rigid weights, one 'Character' mesh, palette from spec.colors. spec (optional) is merged into
    the saved spec.json first."""
    return T_assemble.assemble_from_parts(name, spec)


@mcp.tool()
@_safe
def apply_palette(name: str) -> dict:
    """Re-apply spec.colors (role -> palette index) to the character's faces."""
    return T_assemble.apply_palette(name)


@mcp.tool()
@_safe
def recolor(name: str, role: str, palette_index: int) -> dict:
    """Set one role's palette index in the spec and re-apply the palette."""
    return T_assemble.recolor(name, role, palette_index)


@mcp.tool()
@_safe
def compare_reference(name: str, arms_down_deg: float | None = None, hide_slots: list[str] | None = None) -> dict:
    """Sheet: reference crops (top) / renders at the same scale (middle) / silhouette overlay (bottom:
    red = only in the reference, blue = only in the render). stats.iou per view.
    arms_down_deg: lower the T-pose arms to match an A-pose drawing (default spec.compare.arms_down_deg).
    hide_slots: slots left out of the render, e.g. a staff drawn beside the character."""
    return T_qa.compare_reference(name, arms_down_deg, hide_slots)


@mcp.tool()
@_safe
def paint_surface(name: str, approach: str | None = None, seed: int | None = None) -> dict:
    """Painted styles only (surface 'painted'): UV-unwrap the assembled character and bake its painted
    texture from the face roles + spec.colors into one material (unlit when the style says so), saved in
    character.blend. Run after every assemble_from_parts. approach: 'auto' (default; procedural, works for
    any parts) or 'projection' (hero characters: projects the add_reference sheet, auto fills the rest).
    seed varies brush dabs/cracks/rust. approach/seed default to spec.paint and are stored there when
    given. Previews: lit and unlit (flat) turnaround sheets; stats.texture_sha256 goes into an approval."""
    return T_paint.paint_surface(name, approach, seed)


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
