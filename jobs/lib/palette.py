"""Palette material and role -> UV resolution (STYLE.md §4)."""
import bpy

from . import style as S


def palette_image():
    path = S.repo_path(S.load()["palette"]["file"])
    for img in bpy.data.images:
        if img.filepath and bpy.path.abspath(img.filepath) == str(path):
            return img
    img = bpy.data.images.load(str(path))
    img.name = "palette.png"
    img.pack()
    return img


def palette_material():
    name = S.load()["palette"]["material"]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Metallic"].default_value = 0.0
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = palette_image()
    tex.interpolation = "Closest"
    tex.location = (-350, 200)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def apply_roles(obj, colors):
    """Write UVs from the face attribute `role` and a {role_name: palette_index} map.

    Returns (used_palette_indices, missing_roles)."""
    mesh = obj.data
    roles = S.load()["roles"]
    attr = mesh.attributes.get("role")
    if attr is None or attr.domain != "FACE":
        raise RuntimeError(f"{obj.name}: no FACE attribute 'role'")
    uv = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    used, missing = set(), set()
    for poly in mesh.polygons:
        r = attr.data[poly.index].value
        name = roles[r] if 0 <= r < len(roles) else None
        if name is None or name not in colors:
            missing.add(name or f"#{r}")
            continue
        idx = colors[name]
        used.add(idx)
        u, v = S.palette_uv(idx)
        for li in poly.loop_indices:
            uv.data[li].uv = (u, v)
    mesh.materials.clear()
    mesh.materials.append(palette_material())
    return sorted(used), sorted(missing)
