"""Assemble a prop (STYLE.md §9b): the built prop moved to its origin, palette, shading, AO, anchor empties.

args: { spec: {...}, part_blend: <styles/<style>/props/<part>.blend>, out: <character.blend> }
"""
import json

import bpy
from mathutils import Matrix, Vector

from lib import palette as PAL
from lib import scene as SC
from lib import shading as SH
from lib import style as S


def origin_offset(obj, origin, anchors):
    """Translation that puts the prop on its origin rule: `grip` at 0,0,0 or `floor` (footprint centred, z 0)."""
    if origin == "grip":
        return -Vector(anchors["grip"])
    pts = [v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))


def split_materials(obj, materials):
    """spec.materials = {name: [roles]} (STYLE.md §9b): faces of those roles get a copy of the palette material
    (same texture and baked AO) under that name, for the game to treat apart (e.g. `M_Bubble`, made translucent)."""
    if not materials:
        return {}
    mesh = obj.data
    roles = S.load()["roles"]
    attr = mesh.attributes["role"]
    base = mesh.materials[0]
    out = {}
    for name, rlist in materials.items():
        bad = [r for r in rlist if r not in roles]
        if bad or name == base.name:
            raise RuntimeError(f"spec.materials[{name!r}]: unknown roles {bad}" if bad else f"{name!r} is the palette material")
        mat = base.copy()
        mat.name = name
        mesh.materials.append(mat)
        idx = len(mesh.materials) - 1
        want = {roles.index(r) for r in rlist}
        n = 0
        for poly in mesh.polygons:
            if attr.data[poly.index].value in want:
                poly.material_index = idx
                n += 1
        if not n:
            raise RuntimeError(f"spec.materials[{name!r}]: no faces with roles {rlist}")
        out[name] = n
    return out


def run(args):
    style = S.load()
    spec = args["spec"]
    types = style["props"]["types"]
    ptype = spec.get("type")
    if ptype not in types:
        raise RuntimeError(f"spec.type {ptype!r} is not a prop type {sorted(types)}")
    SC.empty_scene()
    with bpy.data.libraries.load(str(args["part_blend"]), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n == "prop"]
    if not dst.objects or dst.objects[0] is None:
        raise RuntimeError(f"{args['part_blend']} has no object 'prop'")
    obj = dst.objects[0]
    bpy.context.scene.collection.objects.link(obj)
    anchors = json.loads(obj.get("anchors", "{}"))
    built_as = obj.get("prop_type")
    if built_as and built_as != ptype:
        raise RuntimeError(f"part {spec['part']!r} was built as a {built_as!r}, spec.type is {ptype!r}")
    missing = [a for a in types[ptype]["anchors"] if a not in anchors]
    if missing:
        raise RuntimeError(f"part {spec['part']!r} lacks anchors {missing}")

    off = origin_offset(obj, types[ptype]["origin"], anchors)
    obj.data.transform(Matrix.Translation(off))
    obj.data.update()
    for k in ("anchors", "prop_type"):   # `pieces` stays: export_glb splits the mesh by it
        if k in obj:
            del obj[k]
    obj.name = obj.data.name = spec["name"]

    SH.apply(obj.data)
    used_idx, missing_roles = PAL.apply_roles(obj, spec.get("colors") or {})
    cfg = SH.ao_config()
    ao = SH.bake_ao(obj, distance=(cfg or {}).get("prop_distance"))
    split = split_materials(obj, spec.get("materials") or {})
    anchor_pieces = json.loads(obj.get("anchor_pieces", "{}"))
    if "anchor_pieces" in obj:
        del obj["anchor_pieces"]
    empties = {}
    for name, p in anchors.items():
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 0.03
        e.location = Vector(p) + off
        if name in anchor_pieces:
            e["piece"] = anchor_pieces[name]   # export_glb parents it to that piece
        bpy.context.scene.collection.objects.link(e)
        empties[name] = [round(x, 4) for x in e.location]
    SC.save(args["out"])
    warnings = [f"roles without a colour in spec.colors: {missing_roles} (validate will fail)"] if missing_roles else []
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    return {"outputs": [args["out"]], "warnings": warnings,
            "stats": {"tris": tris, "palette_indices": used_idx, "anchors": empties, "origin_offset": [round(x, 4) for x in off],
                      "ao": ao, "missing_roles": missing_roles, "materials": split,
                      "pieces": json.loads(obj.get("pieces", "{}"))}}
