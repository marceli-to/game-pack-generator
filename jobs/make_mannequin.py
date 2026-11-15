"""Build a blocky mannequin character on the standard skeleton from a proportion template.

Used as the template preview (STYLE.md §7a) and as the test fixture for QA/export.
args: { out: <path.blend>, template?: <the style's default archetype template>,
        colors?: {role: palette_index}, animations?: true, hair?: true, defects?: [..] }
defects (tests only): "flipped_normals", "second_material", "no_role", "too_tall", "open_mesh"
"""
import bmesh
import bpy
from mathutils import Matrix, Vector

from lib import palette as P
from lib import rig as R
from lib import scene as SC
from lib import shading as SH
from lib import style as S

DEFAULT_COLORS = {"skin": 2, "hair": 8, "primary": 33, "secondary": 45, "accent": 42, "metal": 41,
                  "leather": 46, "eyes": 56, "dark": 54, "special": 58}


def run(args):
    style = S.load()
    tpl_path = args.get("template", style["archetypes"][style["default_archetype"]]["template"])
    colors = {**DEFAULT_COLORS, **args.get("colors", {})}
    defects = set(args.get("defects", []))

    SC.empty_scene()
    arm = R.append_skeleton()
    tpl = R.apply_template(arm, tpl_path)
    lm = {k: Vector(v) for k, v in tpl["landmarks"].items()}

    bm = bmesh.new()
    role_l = bm.faces.layers.int.new("role")
    slot_l = bm.faces.layers.int.new("slot")
    deform = bm.verts.layers.deform.verify()
    groups = {}

    def vgroup(bone):
        if bone not in groups:
            groups[bone] = len(groups)
        return groups[bone]

    def box(lo, hi, role, slot, bone):
        lo, hi = Vector(lo), Vector(hi)
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((lo + hi) / 2) @
                                    Matrix.Diagonal((*(hi - lo), 1.0)))
        verts = res["verts"]
        faces = {f for v in verts for f in v.link_faces}
        g = vgroup(bone)
        for v in verts:
            v[deform][g] = 1.0
        for f in faces:
            f[role_l] = S.role_index(role)
            f[slot_l] = S.slot_index(slot)
        return faces

    def seg(a, b, thick, role, slot, bone, depth=None):
        a, b = Vector(a), Vector(b)
        d = Vector((thick / 2, (depth or thick) / 2, thick / 2))
        lo = Vector((min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))) - d
        hi = Vector((max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))) + d
        # along the segment axis the box spans exactly a..b
        axis = max(range(3), key=lambda i: abs(b[i] - a[i]))
        lo[axis], hi[axis] = min(a[axis], b[axis]), max(a[axis], b[axis])
        return box(lo, hi, role, slot, bone)

    hb, ht = lm["head_base"], lm["head_top"]
    hip_z = lm["hip.l"].z
    spine_z = arm.data.bones["spine"].head_local.z
    g = tpl.get("guides", {})
    hw, hd = g.get("head_width", 0.5) / 2, g.get("head_depth", 0.46) / 2  # head half width / depth
    fw, fh, heel = g.get("foot_width", 0.18), g.get("foot_height", None), g.get("foot_heel", 0.08)
    box((-hw, -hd, hb.z), (hw, hd, ht.z), "skin", "head", "head")
    for x in (-0.1, 0.1):  # eyes on the front (-Y) face
        box((x - 0.035, -hd - 0.02, hb.z + 0.2), (x + 0.035, -hd + 0.01, hb.z + 0.29), "eyes", "face", "head")
    if args.get("hair", True):
        box((-hw - 0.02, -hd + 0.06, ht.z - 0.12), (hw + 0.02, hd + 0.02, ht.z + 0.06), "hair", "hair", "head")
    tw, td = g.get("torso_width", 0.46) / 2, g.get("torso_depth", 0.28) / 2
    box((-tw + 0.02, -td + 0.01, hip_z - 0.08), (tw - 0.02, td - 0.01, spine_z + 0.02), "secondary", "torso", "hips")
    box((-tw, -td, spine_z + 0.02), (tw, td, hb.z), "primary", "torso", "chest")
    for s in ("l", "r"):
        seg(lm[f"shoulder.{s}"], lm[f"elbow.{s}"], 0.14, "primary", "arms", f"upperarm.{s}")
        seg(lm[f"elbow.{s}"], lm[f"wrist.{s}"], 0.12, "skin", "arms", f"lowerarm.{s}")
        w = lm[f"wrist.{s}"]
        sign = 1 if s == "l" else -1
        box((min(w.x, w.x + sign * 0.16), -0.08, w.z - 0.09), (max(w.x, w.x + sign * 0.16), 0.08, w.z + 0.07),
            "skin", "hands", f"hand.{s}")
        seg(lm[f"hip.{s}"], lm[f"knee.{s}"], 0.18, "secondary", "legs", f"upperleg.{s}")
        seg(lm[f"knee.{s}"], lm[f"ankle.{s}"], 0.16, "secondary", "legs", f"lowerleg.{s}")
        a, t = lm[f"ankle.{s}"], lm[f"toes.{s}"]
        top = max(fh if fh is not None else 0.0, a.z + 0.03)  # the shin always enters the foot
        box((a.x - fw / 2, t.y, 0.0), (a.x + fw / 2, a.y + heel, top), "dark", "feet", f"foot.{s}")

    if "open_mesh" in defects:
        bm.faces.ensure_lookup_table()
        bm.faces.remove(bm.faces[0])
    if "flipped_normals" in defects:
        bm.faces.ensure_lookup_table()
        bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if f[slot_l] == S.slot_index("legs")][:6])
    if "too_tall" in defects:
        for v in bm.verts:
            v.co.z *= 1.25

    mesh = bpy.data.meshes.new(style["skeleton"]["mesh_object"])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(style["skeleton"]["mesh_object"], mesh)
    bpy.context.scene.collection.objects.link(obj)
    for bone, g in sorted(groups.items(), key=lambda kv: kv[1]):
        obj.vertex_groups.new(name=bone)
    SH.apply(mesh)
    used, missing = P.apply_roles(obj, colors)
    if "no_role" in defects:
        mesh.attributes.remove(mesh.attributes["role"])
    if "second_material" in defects:
        m2 = bpy.data.materials.new("M_Extra")
        mesh.materials.append(m2)
        mesh.polygons[0].material_index = 1
    obj.parent = arm
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm

    clips = []
    if args.get("animations", True):
        acts = R.append_actions()
        for a in acts:
            R.scale_clip_locations(a, tpl["offset_factors"])
        R.bind_actions(arm, acts)
        idle = next((a for a in acts if a.name == "idle"), None)
        if idle:
            SC.assign_action(arm, idle)
        clips = sorted(a.name for a in acts)
    SC.save(args["out"])
    return {"outputs": [args["out"]], "stats": {"palette_indices": used, "missing_roles": missing,
                                                "clips": clips, "tris": sum(len(p.vertices) - 2 for p in mesh.polygons)}}
