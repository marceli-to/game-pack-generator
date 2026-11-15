"""Shading (STYLE.md §5): smooth by angle. Faces are smooth-shaded; edges whose faces meet at
more than `shading.crease_deg` are marked sharp, so curves read round and creases stay crisp.
The glTF exporter writes the resulting split normals, so the GLB looks the same everywhere."""
import math

import bmesh

from . import style as S


def crease_rad():
    return math.radians(S.load()["shading"]["crease_deg"])


def apply(mesh):
    mesh.shade_smooth()
    mesh.set_sharp_from_angle(angle=crease_rad())
    return mesh


def check(mesh):
    """(flat_faces, unmarked_creases): faces not smooth-shaded, and edges sharper than the crease
    angle between two smooth faces that are not marked sharp."""
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
