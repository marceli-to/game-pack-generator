"""Palette material and role -> UV resolution (STYLE.md §4)."""
import bpy

from . import style as S


def palette_image():
    path = S.repo_path(S.load()["palette"]["file"])
    for img in bpy.data.images:
        if img.filepath and bpy.path.abspath(img.filepath) == str(path):
            # a .blend packs the palette as it was when assembled: reload it from the style, so a palette
            # change reaches every re-assembled or exported character (REVIEW.md B3)
            if img.packed_file is not None:
                img.unpack(method="REMOVE")
            img.reload()
            img.pack()
            return img
    img = bpy.data.images.load(str(path))
    img.name = "palette.png"
    img.pack()
    return img


def palette_material():
    name = S.load()["palette"]["material"]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        refresh_palette_material(mat)
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_backface_culling = True   # every part is a closed shell: export single-sided (STYLE.md §10)
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


def refresh_palette_material(mat):
    """Current palette image + single-sided, on a palette material from an older .blend (REVIEW.md B2/B3)."""
    mat.use_backface_culling = True
    if mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image is not None and n.image.name.startswith("palette"):
                n.image = palette_image()


def refresh_all():
    """Every material that samples the palette (incl. split copies such as M_Bubble)."""
    img = palette_image()
    for mat in bpy.data.materials:
        if mat.node_tree and any(n.type == "TEX_IMAGE" and n.image is img for n in mat.node_tree.nodes):
            mat.use_backface_culling = True


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
