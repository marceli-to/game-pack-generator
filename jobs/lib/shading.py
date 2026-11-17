"""Shading (STYLE.md §5), per style (`shading.mode`):
- `smooth_by_angle`: faces are smooth-shaded; edges whose faces meet at more than `shading.crease_deg` are
  marked sharp, so curves read round and creases stay crisp.
- `flat`: every face flat-shaded, every facet visible (the `lowpoly` look).
The glTF exporter writes the resulting normals, so the GLB looks the same everywhere."""
import math

import bmesh

from . import style as S


def mode():
    return S.load()["shading"]["mode"]


def crease_rad():
    return math.radians(S.load()["shading"]["crease_deg"])


def apply(mesh):
    if mode() == "flat":
        mesh.shade_flat()
        return mesh
    mesh.shade_smooth()
    mesh.set_sharp_from_angle(angle=crease_rad())
    return mesh


def check(mesh):
    """(wrong_faces, unmarked_creases): faces not shaded the style's way (flat faces under smooth by
    angle, smooth faces under flat), and edges sharper than the crease angle between two smooth faces
    that are not marked sharp (smooth by angle only)."""
    if mode() == "flat":
        return sum(1 for p in mesh.polygons if p.use_smooth), 0
    flat = sum(1 for p in mesh.polygons if not p.use_smooth)
    sharp = mesh.attributes.get("sharp_edge")
    lim = crease_rad() + math.radians(1)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    unmarked = 0
    for e in bm.edges:
        if len(e.link_faces) != 2 or not all(f.smooth for f in e.link_faces):
            continue
        if e.calc_face_angle(0.0) > lim and not (sharp is not None and sharp.data[e.index].value):
            unmarked += 1
    bm.free()
    return flat, unmarked


AO_ATTR = "AO"


def ao_config():
    """`shading.ao` of the style (STYLE.md §5), or None."""
    return S.load()["shading"].get("ao")


def bake_ao(obj, distance=None):
    """Bake ambient occlusion (rest pose, Cycles) into the corner colour attribute `AO` and multiply it into
    the object's palette material (STYLE.md §5). No-op without `shading.ao`. `distance` overrides the style's
    (props: `shading.ao.prop_distance`, STYLE.md §9b). Returns stats or None."""
    import bpy
    import numpy as np
    cfg = ao_config()
    if not cfg:
        return None
    me = obj.data
    for a in list(me.color_attributes):
        me.color_attributes.remove(a)
    ca = me.color_attributes.new(AO_ATTR, "FLOAT_COLOR", "CORNER")
    me.color_attributes.active_color = ca
    me.attributes.active_color = ca

    sc = bpy.context.scene
    engine = sc.render.engine
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = cfg["samples"]
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.light_settings.distance = distance or cfg["distance"]
    sc.render.bake.target = "VERTEX_COLORS"
    vl = bpy.context.view_layer
    vl.update()   # objects linked just before (props loaded from a library) are not in the layer yet
    for o in vl.objects:
        o.select_set(o is obj)
    vl.objects.active = obj
    bpy.ops.object.bake(type="AO", target="VERTEX_COLORS")
    sc.render.engine = engine

    c = np.zeros(len(me.loops) * 4, dtype=np.float32)
    ca.data.foreach_get("color", c)
    c = c.reshape(-1, 4)
    ao = np.clip(c[:, 0], 0.0, 1.0)
    v = np.maximum(cfg["floor"], 1.0 - cfg["strength"] * (1.0 - ao ** cfg["power"]))
    c[:, 0] = c[:, 1] = c[:, 2] = v
    c[:, 3] = 1.0
    ca.data.foreach_set("color", c.ravel())

    for mat in me.materials:
        if mat is None or not mat.use_nodes:
            continue
        nt = mat.node_tree
        if nt.nodes.get(AO_ATTR) is not None:
            continue
        tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None)
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if tex is None or bsdf is None:
            continue
        va = nt.nodes.new("ShaderNodeVertexColor")
        va.name = AO_ATTR
        va.layer_name = AO_ATTR
        va.location = (-350, -100)
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.location = (-120, 100)
        nt.links.new(tex.outputs["Color"], mix.inputs["A"])
        nt.links.new(va.outputs["Color"], mix.inputs["B"])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    p = np.percentile(v, [5, 50, 95])
    return {"corners": int(len(v)), "p5": round(float(p[0]), 3), "p50": round(float(p[1]), 3),
            "p95": round(float(p[2]), 3)}
