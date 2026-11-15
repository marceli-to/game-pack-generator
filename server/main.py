"""MCP server (stdio). Run:  .venv/bin/python -m server.main

Each tool spawns one headless Blender process (see server/blender.py) and returns
{ ok, outputs, stats, previews, warnings, error? }. Look at the preview PNGs.
"""
from __future__ import annotations

import functools
import traceback

from mcp.server.mcpserver import MCPServer

from .tools import export as T_export
from .tools import project as T_project
from .tools import qa as T_qa

INSTRUCTIONS = """\
Headless tool for Kenney-style low-poly characters (Blender + GLB for three.js).
STYLE.md is the law; read it with get_style. Characters live in workspace/<name>/.
Typical Phase-1 flow: get_style -> init_character -> import_glb -> stats / validate ->
render_preview (look at the sheet) -> export (GLB + glTF validator + three.js test load).
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
def get_style() -> dict:
    """Return style.json: budgets, units, archetypes, palette (64 colours), colour roles, slots,
    skeleton (bone names/parents) and animation names. Read this before building anything."""
    return T_project.get_style()


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


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
