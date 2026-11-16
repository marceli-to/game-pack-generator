"""Measurements behind `stats` and `validate` (STYLE.md §2–§7, §12).

Everything is measured in the rest pose on the evaluated meshes (modifiers applied),
in world space.
"""
from collections import defaultdict

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import scene as SC
from . import shading as SH
from . import style as S


def _int_face_attr(mesh, name):
    a = mesh.attributes.get(name)
    if a is None or a.domain != "FACE" or a.data_type != "INT":
        return None
    vals = np.zeros(len(mesh.polygons), dtype=np.int32)
    a.data.foreach_get("value", vals)
    return vals


def _islands(bm):
    """Island id per vertex (connected through edges)."""
    ids = {}
    cur = 0
    for v in bm.verts:
        if v.index in ids:
            continue
        stack = [v]
        ids[v.index] = cur
        while stack:
            x = stack.pop()
            for e in x.link_edges:
                o = e.other_vert(x)
                if o.index not in ids:
                    ids[o.index] = cur
                    stack.append(o)
        cur += 1
    return ids, cur


def _palette_matches(img):
    """True if `img` has the same pixels as the style's palette.png."""
    lib = bpy.data.images.load(str(S.repo_path(S.load()["palette"]["file"])), check_existing=False)
    try:
        if tuple(img.size) != tuple(lib.size):
            return False
        a = np.array(img.pixels[:], dtype=np.float32).reshape(-1, img.channels)[:, :3]
        b = np.array(lib.pixels[:], dtype=np.float32).reshape(-1, lib.channels)[:, :3]
        return bool(np.abs(a - b).max() <= 1.5 / 255)
    finally:
        bpy.data.images.remove(lib)


def _material_images(mat):
    if mat is None or not mat.use_nodes:
        return []
    return [n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image is not None]


def _is_unlit(mat):
    """Texture -> Background shader -> output: Blender's glTF exporter writes KHR_materials_unlit."""
    if mat is None or not mat.use_nodes:
        return False
    for n in mat.node_tree.nodes:
        if n.type == "OUTPUT_MATERIAL" and n.is_active_output and n.inputs["Surface"].links:
            return n.inputs["Surface"].links[0].from_node.type == "BACKGROUND"
    return False


def measure(spec=None):
    style = S.load()
    painted = style.get("surface") == "painted"
    roles = style["roles"]
    slots = style["slots"]
    topo = style["topology"]
    pal = style["palette"]
    spec = spec or {}

    arm = SC.main_armature()
    if arm is not None:
        arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    objs = SC.meshes()

    m = {
        "objects": [o.name for o in objs],
        "tris": 0, "verts": 0, "faces": 0,
        "surface": style.get("surface"),
        "materials": [], "images": [], "image_sizes": {}, "palette_texture_ok": None, "unlit": None,
        "uv_layers": [], "uv_overlap_faces": 0,
        "has_role": True, "invalid_role_faces": 0, "roles_used": set(),
        "has_slot": True, "slot_tris": defaultdict(int),
        "uv_missing": False, "uv_outside": 0, "uv_spanning": 0, "uv_off_centre": 0,
        "palette_indices": set(),
        "non_manifold_edges": 0, "boundary_edges": 0, "wire_edges": 0,
        "flipped_faces": 0, "inverted_islands": 0,
        "zero_area_faces": 0, "duplicate_verts": 0, "ngons_over_max": 0,
        "flat_faces": 0, "unmarked_creases": 0, "vertex_color_layers": 0,
        "asymmetric_verts": 0, "symmetry_checked_verts": 0,
        "weights_over_2_bones": 0, "unweighted_verts": 0,
        "z_min": None, "body_top": None, "headwear_top": None, "total_top": None,
        "transforms_applied": True,
    }
    body_slots = {slots.index(s) for s in slots if s not in style["height_excluded_slots"]}
    headwear_slot = slots.index("headwear")
    base_slots = {slots.index(s) for s in slots if not s.startswith("accessory")}
    deform_bones = {b.name for b in arm.data.bones if b.use_deform} if arm else set()

    for o in objs:
        if any(abs(c) > 1e-5 for c in (*o.location, *o.rotation_euler)) or any(abs(c - 1) > 1e-5 for c in o.scale):
            m["transforms_applied"] = False
        ev = o.evaluated_get(dg)
        mesh = ev.to_mesh()
        mw = ev.matrix_world
        m["verts"] += len(mesh.vertices)
        m["faces"] += len(mesh.polygons)
        m["tris"] += sum(len(p.vertices) - 2 for p in mesh.polygons)
        m["vertex_color_layers"] += len(mesh.color_attributes)
        flat, unmarked = SH.check(o.data)
        m["flat_faces"] += flat
        m["unmarked_creases"] += unmarked

        used_mats = {p.material_index for p in mesh.polygons}
        for i in used_mats:
            mat = o.material_slots[i].material if i < len(o.material_slots) else None
            name = mat.name if mat else None
            if name not in m["materials"]:
                m["materials"].append(name)
                m["unlit"] = _is_unlit(mat) if m["unlit"] is None else (m["unlit"] and _is_unlit(mat))
            for img in _material_images(mat):
                if img.name not in m["images"]:
                    m["images"].append(img.name)
                    m["image_sizes"][img.name] = list(img.size)
                    ok = _palette_matches(img)
                    m["palette_texture_ok"] = ok if m["palette_texture_ok"] is None else (m["palette_texture_ok"] and ok)

        role = _int_face_attr(mesh, "role")
        slot = _int_face_attr(mesh, "slot")
        if role is None:
            m["has_role"] = False
        if slot is None:
            m["has_slot"] = False

        uv = mesh.uv_layers.active
        m["uv_layers"] += [u.name for u in mesh.uv_layers]
        if uv is None:
            m["uv_missing"] = True
        elif painted:
            from . import paint as PT  # local: only painted styles need it
            m["uv_overlap_faces"] += len(PT.uv_overlaps(mesh, uv.name, style["paint"]["texture_size"]))
        for p in mesh.polygons:
            ntri = len(p.vertices) - 2
            if role is not None:
                r = int(role[p.index])
                if 0 <= r < len(roles):
                    m["roles_used"].add(roles[r])
                else:
                    m["invalid_role_faces"] += 1
            s = int(slot[p.index]) if slot is not None else None
            if s is not None and 0 <= s < len(slots):
                m["slot_tris"][slots[s]] += ntri
            zs = [(mw @ mesh.vertices[v].co).z for v in p.vertices]
            top = max(zs)
            m["z_min"] = min(zs) if m["z_min"] is None else min(m["z_min"], min(zs))
            m["total_top"] = top if m["total_top"] is None else max(m["total_top"], top)
            if s is None or s in body_slots:
                m["body_top"] = top if m["body_top"] is None else max(m["body_top"], top)
            if s == headwear_slot:
                m["headwear_top"] = top if m["headwear_top"] is None else max(m["headwear_top"], top)
            if len(p.vertices) > topo["max_ngon"]:
                m["ngons_over_max"] += 1
            if p.area < topo["min_face_area"]:
                m["zero_area_faces"] += 1
            if uv is not None and painted:
                if any(not (0.0 <= c <= 1.0) for li in p.loop_indices for c in uv.data[li].uv):
                    m["uv_outside"] += 1
            elif uv is not None:
                cells = set()
                for li in p.loop_indices:
                    u, v = uv.data[li].uv
                    idx, inside = S.palette_cell_of_uv(u, v)
                    if not inside:
                        m["uv_outside"] += 1
                        break
                    cells.add(idx)
                    cu, cv = S.palette_uv(idx)
                    if abs(u - cu) > 0.25 / pal["grid"] or abs(v - cv) > 0.25 / pal["grid"]:
                        m["uv_off_centre"] += 1
                if len(cells) > 1:
                    m["uv_spanning"] += 1
                elif len(cells) == 1:
                    m["palette_indices"] |= cells

        # topology on a world-space bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.transform(mw)
        bm.verts.index_update()
        for e in bm.edges:
            if e.is_wire:
                m["wire_edges"] += 1
            elif e.is_boundary:
                m["boundary_edges"] += 1
            elif not e.is_manifold:
                m["non_manifold_edges"] += 1
        before = [f.normal.copy() for f in bm.faces]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        m["flipped_faces"] += sum(1 for f, n in zip(bm.faces, before) if f.normal.dot(n) < 0)
        ids, _ = _islands(bm)
        kd = KDTree(len(bm.verts))
        for v in bm.verts:
            kd.insert(v.co, v.index)
        kd.balance()
        dup = set()
        for v in bm.verts:
            for (_, j, _) in kd.find_range(v.co, topo["merge_distance"]):
                if j != v.index and ids[j] == ids[v.index]:
                    dup.add(min(j, v.index))
        m["duplicate_verts"] += len(dup)

        # symmetry of base parts (mirror on X)
        if slot is not None:
            base_verts = set()
            for p in mesh.polygons:
                if int(slot[p.index]) in base_slots:
                    base_verts.update(p.vertices)
            pts = [mw @ mesh.vertices[i].co for i in base_verts]
            if pts:
                kd2 = KDTree(len(pts))
                for i, co in enumerate(pts):
                    kd2.insert(co, i)
                kd2.balance()
                for co in pts:
                    _, _, d = kd2.find(Vector((-co.x, co.y, co.z)))
                    if d > 0.002:
                        m["asymmetric_verts"] += 1
                m["symmetry_checked_verts"] += len(pts)
        bm.free()

        # weights
        if arm is not None and o.vertex_groups:
            gnames = {g.index: g.name for g in o.vertex_groups}
            src = o.data
            for v in src.vertices:
                bones = [g for g in v.groups if g.weight > 1e-4 and gnames.get(g.group) in deform_bones]
                if len(bones) > 2:
                    m["weights_over_2_bones"] += 1
                if not bones:
                    m["unweighted_verts"] += 1
        ev.to_mesh_clear()

    # inverted islands: run on the original (not recalculated) normals
    m["inverted_islands"] = _count_inverted_islands(objs, dg)

    # skeleton
    want = {b["name"]: b["parent"] for b in style["skeleton"]["bones"]}
    if arm is None:
        m["skeleton"] = {"present": False}
    else:
        have = {b.name: (b.parent.name if b.parent else None) for b in arm.data.bones}
        m["skeleton"] = {
            "present": True,
            "name": arm.name,
            "bones": len(have),
            "deforming": sum(1 for b in arm.data.bones if b.use_deform),
            "missing": sorted(set(want) - set(have)),
            "extra": sorted(set(have) - set(want)),
            "wrong_parent": sorted(n for n in want if n in have and have[n] != want[n]),
            "deform_mismatch": sorted(b["name"] for b in style["skeleton"]["bones"]
                                      if b["name"] in arm.data.bones and arm.data.bones[b["name"]].use_deform != b["deform"]),
        }
    m["actions"] = sorted(a.name for a in bpy.data.actions)

    # derived
    floor = 0.0
    m["body_height"] = round(m["body_top"] - floor, 4) if m["body_top"] is not None else None
    m["headwear_height"] = (round(m["headwear_top"] - m["body_top"], 4)
                            if m["headwear_top"] is not None and m["body_top"] is not None else 0.0)
    m["roles_used"] = sorted(m["roles_used"])
    m["palette_indices"] = sorted(m["palette_indices"])
    m["slot_tris"] = dict(m["slot_tris"])
    for k in ("z_min", "body_top", "total_top", "headwear_top"):
        if m[k] is not None:
            m[k] = round(m[k], 4)
    return m


def _count_inverted_islands(objs, dg):
    count = 0
    for o in objs:
        ev = o.evaluated_get(dg)
        mesh = ev.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.transform(ev.matrix_world)
        bm.verts.index_update()
        ids, n = _islands(bm)
        vol = defaultdict(float)
        closed = defaultdict(lambda: True)
        for e in bm.edges:
            if not e.is_manifold:
                closed[ids[e.verts[0].index]] = False
        for f in bm.faces:
            isl = ids[f.verts[0].index]
            for t in range(1, len(f.verts) - 1):
                a, b, c = f.verts[0].co, f.verts[t].co, f.verts[t + 1].co
                vol[isl] += a.dot(b.cross(c)) / 6.0
        count += sum(1 for isl, v in vol.items() if closed[isl] and v < 0)
        bm.free()
        ev.to_mesh_clear()
    return count


def violations(m, spec=None):
    """Apply the STYLE.md §12 thresholds. Returns {hard: [...], soft: [...], info: [...]}."""
    style = S.load()
    spec = spec or {}
    hard, soft, info = [], [], []

    def H(code, msg):
        hard.append({"code": code, "message": msg})

    def W(code, msg):
        soft.append({"code": code, "message": msg})

    b = style["budget"]
    if m["tris"] > b["character"]["hard"]:
        H("tris_hard", f"{m['tris']} tris > hard limit {b['character']['hard']}")
    elif m["tris"] > b["character"]["target"][1]:
        W("tris_target", f"{m['tris']} tris above target {b['character']['target'][1]}")
    for key in ("head", "accessory_hand", "accessory_back"):
        if not m["has_slot"]:
            continue
        for s in b[key]["slots"] if key != "head" else [None]:
            n = (sum(m["slot_tris"].get(x, 0) for x in b[key]["slots"]) if s is None else m["slot_tris"].get(s, 0))
            label = key if s is None else s
            if n > b[key]["hard"]:
                H(f"tris_{label}_hard", f"{label}: {n} tris > hard limit {b[key]['hard']}")
            elif n > b[key]["target"]:
                W(f"tris_{label}_target", f"{label}: {n} tris above target {b[key]['target']}")

    arch = spec.get("archetype", style["default_archetype"])
    lo, hi = style["archetypes"][arch]["height"]
    h = m["body_height"]
    if h is None:
        H("no_geometry", "no mesh geometry")
    else:
        if not (lo <= h <= hi):
            H("height", f"body height {h:.3f} m outside {arch} range {lo}–{hi}")
        if m["headwear_height"] > style["headwear_max_ratio"] * h:
            H("headwear_height", f"headwear adds {m['headwear_height']:.3f} m > {style['headwear_max_ratio']:.0%} of body height")
        if m["z_min"] is not None and abs(m["z_min"]) > 0.01:
            W("floor", f"lowest point at z={m['z_min']:.3f} (origin should be at the floor between the feet)")
    if not m["has_slot"]:
        info.append({"code": "no_slot_attr", "message": "no 'slot' face attribute: height includes hair/headwear/accessories; per-slot budgets and symmetry not checked"})

    if not m["has_role"]:
        H("no_role", "faces without a 'role' attribute (FACE, INT)")
    if m["invalid_role_faces"]:
        H("invalid_role", f"{m['invalid_role_faces']} faces with an invalid role value")
    if spec.get("colors") is not None:
        missing = [r for r in m["roles_used"] if r not in spec["colors"]]
        if missing:
            H("role_without_colour", f"roles without a colour in the spec: {missing}")

    if m["surface"] == "painted":
        _painted_rules(m, spec, style, H, W)
    else:
        _palette_rules(m, style, H, W)

    if m["boundary_edges"] or m["non_manifold_edges"] or m["wire_edges"]:
        H("non_manifold", f"non-manifold geometry: {m['boundary_edges']} open edges, "
                          f"{m['non_manifold_edges']} non-manifold edges, {m['wire_edges']} wire edges")
    if m["flipped_faces"] or m["inverted_islands"]:
        H("flipped_normals", f"flipped normals: {m['flipped_faces']} inconsistent faces, {m['inverted_islands']} inside-out parts")
    if m["zero_area_faces"]:
        W("zero_area", f"{m['zero_area_faces']} zero-area faces")
    if m["duplicate_verts"]:
        W("duplicate_verts", f"{m['duplicate_verts']} duplicate vertices (merge distance {style['topology']['merge_distance']})")
    if m["ngons_over_max"]:
        W("ngons", f"{m['ngons_over_max']} n-gons with more than {style['topology']['max_ngon']} vertices")
    if m["flat_faces"]:
        if style["shading"]["mode"] == "flat":
            W("smooth_shading", f"{m['flat_faces']} faces are smooth-shaded (flat shading required, STYLE.md §5)")
        else:
            W("flat_shading", f"{m['flat_faces']} faces are flat-shaded (smooth by angle required, STYLE.md §5)")
    if m["unmarked_creases"]:
        W("unmarked_creases", f"{m['unmarked_creases']} edges sharper than {style['shading']['crease_deg']}° are not marked sharp")
    if m["vertex_color_layers"]:
        W("vertex_colors", "mesh has vertex colours (everything goes through the palette)")
    if m["symmetry_checked_verts"] and m["asymmetric_verts"]:
        pct = 100 * m["asymmetric_verts"] / m["symmetry_checked_verts"]
        if pct > 1:
            W("asymmetry", f"{pct:.0f}% of base-part vertices have no X-mirror partner")

    sk = m["skeleton"]
    if not sk["present"]:
        H("no_armature", "no armature")
    else:
        if sk["missing"] or sk["extra"] or sk["wrong_parent"]:
            H("skeleton", f"skeleton differs from the standard: missing={sk['missing']} extra={sk['extra']} wrong_parent={sk['wrong_parent']}")
        if sk["deform_mismatch"]:
            W("deform_flags", f"deform flags differ from core.json: {sk['deform_mismatch']}")
    if m["weights_over_2_bones"]:
        W("weights", f"{m['weights_over_2_bones']} vertices weighted to more than 2 bones")
    if sk.get("present") and m["unweighted_verts"]:
        W("unweighted", f"{m['unweighted_verts']} vertices have no bone weights")

    if len(m["objects"]) != 1 or m["objects"][0] != style["skeleton"]["mesh_object"]:
        W("objects", f"expected one mesh object '{style['skeleton']['mesh_object']}', found {m['objects']}")
    if not m["transforms_applied"]:
        W("transforms", "mesh objects have unapplied transforms")
    info.append({"code": "joint_loops", "message": "edge loops at joints: not checked yet (Phase 3, pose_test)"})
    info.append({"code": "gltf_validator", "message": "glTF validator runs in `export`"})
    return {"hard": hard, "soft": soft, "info": info}


def _palette_rules(m, style, H, W):
    """Surface `palette` (STYLE.md §4, §12): one M_Palette material, palette.png, UVs in single cells."""
    mats = m["materials"]
    if len(mats) > 1:
        H("materials", f"{len(mats)} materials ({mats}); exactly one ({style['palette']['material']}) allowed")
    elif mats and mats[0] != style["palette"]["material"]:
        W("material_name", f"material is {mats[0]!r}, expected {style['palette']['material']!r}")
    if len(m["images"]) != 1 or not m["palette_texture_ok"]:
        H("texture", f"texture must be palette.png; found {m['images'] or 'none'}"
                     + ("" if m["palette_texture_ok"] in (None, True) else f" (pixels differ from {style['palette']['file']})"))
    if m["uv_missing"]:
        H("uv_missing", "mesh has no UV map")
    if m["uv_outside"]:
        H("uv_outside", f"{m['uv_outside']} faces with UVs outside the palette")
    if m["uv_spanning"]:
        H("uv_spanning", f"{m['uv_spanning']} faces span several palette cells")
    if m["uv_off_centre"]:
        W("uv_off_centre", f"{m['uv_off_centre']} UV loops not collapsed to the cell centre")
    if len(m["palette_indices"]) > style["palette"]["max_colors"]:
        W("colours", f"{len(m['palette_indices'])} palette colours used (max {style['palette']['max_colors']})")


def _painted_rules(m, spec, style, H, W):
    """Surface `painted` (styles/<style>/STYLE.md §4, §12): one material with the baked texture
    (not palette.png), one UV layer inside 0..1 without shared texels, unlit if paint.unlit."""
    pc = style["paint"]
    mats, imgs = m["materials"], m["images"]
    if len(mats) > 1:
        H("materials", f"{len(mats)} materials ({mats}); exactly one ({pc['material']}) allowed")
    if mats == [style["palette"]["material"]] or m["palette_texture_ok"]:
        H("not_painted", "the character still has the palette material: run paint_surface "
                         "(needed after every assemble_from_parts)")
        return
    if mats and mats[0] != pc["material"]:
        W("material_name", f"material is {mats[0]!r}, expected {pc['material']!r}")
    size = pc["texture_size"]
    if len(imgs) != 1:
        H("texture", f"exactly one painted texture expected; found {imgs or 'none'}")
    elif m["image_sizes"][imgs[0]] != [size, size]:
        H("texture_size", f"texture is {m['image_sizes'][imgs[0]]}, expected {size} x {size}")
    if m["uv_missing"]:
        H("uv_missing", "mesh has no UV map")
    if len(set(m["uv_layers"])) > 1:
        W("uv_layers", f"{len(set(m['uv_layers']))} UV layers {sorted(set(m['uv_layers']))}; the GLB should carry one")
    if m["uv_outside"]:
        H("uv_outside", f"{m['uv_outside']} faces with UVs outside 0..1")
    if m["uv_overlap_faces"]:
        H("uv_overlap", f"{m['uv_overlap_faces']} faces share texels with other faces (wrong paint)")
    if pc.get("unlit") and not m["unlit"]:
        H("not_unlit", "style exports unlit (paint.unlit) but the material is not texture -> Background "
                       "(KHR_materials_unlit); re-run paint_surface")
    colors = spec.get("colors") or {}
    base = {colors[r] for r in m["roles_used"] if r in colors}
    if len(base) > style["palette"]["max_colors"]:
        W("colours", f"{len(base)} base colours used (max {style['palette']['max_colors']})")
