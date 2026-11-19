"""Export the open .blend as GLB per STYLE.md §10.

args: { out: <path.glb> }
"""
import json
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix

from lib import glb as G
from lib import scene as SC
from lib import style as S

WANTED = {
    "export_format": "GLB",
    "export_yup": True,
    "export_apply": True,
    "export_animations": True,
    "export_animation_mode": "ACTIONS",
    "export_force_sampling": True,
    "export_cameras": False,
    "export_lights": False,
    "export_draco_mesh_compression_enable": False,
    "export_materials": "EXPORT",
    "export_image_format": "AUTO",
    "export_texcoords": True,
    "export_normals": True,
    "export_skins": True,
    "export_def_bones": False,      # keep the non-deforming slot bones for attachments
    "export_extras": False,
    "export_vertex_color": "MATERIAL",   # COLOR_0 only where the material uses it (baked AO, STYLE.md §5)
    "use_selection": False,
}


def split_pieces():
    """Props (STYLE.md §9b): a mesh with `pieces` becomes one object per piece (face attribute `piece`, 0 = the
    main mesh). A piece with a parent anchor has its origin at that anchor and is its child (local transform
    identity), so turning the anchor node turns the piece; anchors marked with a `piece` become its children."""
    made = {}
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and "pieces" in o]:
        pieces = json.loads(obj["pieces"])
        del obj["pieces"]
        objs = [obj]
        for name in pieces:   # copies first: the main mesh loses the other pieces' faces below
            o = obj.copy()
            o.data = obj.data.copy()
            o.name = o.data.name = name
            bpy.context.scene.collection.objects.link(o)
            objs.append(o)
        for idx, ((name, parent), o) in enumerate(zip([(None, None), *pieces.items()], objs)):
            bm = bmesh.new()
            bm.from_mesh(o.data)
            lay = bm.faces.layers.int["piece"]
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] != idx], context="FACES")
            bm.faces.layers.int.remove(lay)
            bm.to_mesh(o.data)
            bm.free()
            if parent is not None:
                e = bpy.data.objects[parent]
                o.data.transform(Matrix.Translation(-e.matrix_world.translation))
                o.parent = e
                o.matrix_parent_inverse = Matrix.Identity(4)
                o.matrix_basis = Matrix.Identity(4)
            made[name or obj.name] = parent
    bpy.context.view_layer.update()   # the pieces' world matrices, before anchors are parented to them
    for e in [o for o in bpy.context.scene.objects if o.type == "EMPTY" and "piece" in o]:
        target = bpy.data.objects[e["piece"]]
        mw = e.matrix_world.copy()
        e.parent = target
        e.matrix_world = mw
        del e["piece"]
    bpy.context.view_layer.update()
    return made


def run(args):
    out = Path(args["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    arm = SC.main_armature()
    warnings = []
    if arm is not None:
        arm.data.pose_position = "POSE"
        for a in bpy.data.actions:
            a.use_fake_user = True
            if len(a.slots):
                a.slots[0].name_display = arm.name
        # glTF wants skinned meshes at the root (validator: NODE_SKINNED_MESH_NON_ROOT).
        # Unparent in this export session only; the armature modifier keeps the skinning.
        for o in SC.meshes():
            if o.parent is arm:
                mw = o.matrix_world.copy()
                o.parent = None
                o.matrix_world = mw
    for o in [o for o in bpy.context.scene.objects if o.type in ("CAMERA", "LIGHT")]:
        bpy.data.objects.remove(o, do_unlink=True)
    pieces = split_pieces()
    props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    kwargs = {}
    for k, v in WANTED.items():
        if k in props:
            kwargs[k] = v
        else:
            warnings.append(f"exporter has no option {k}")
    bpy.ops.export_scene.gltf(filepath=str(out), **kwargs)
    # arms-only clips (STYLE.md §8b) must not carry the other bones: the exporter samples every bone
    # (force sampling), which would pin the legs and torso at rest when the game layers the clip
    extra = {c["name"] for c in S.load()["animations"].get("extra_clips", []) if c.get("arms_only")}
    keep = {}
    for a in bpy.data.actions:
        if a.name in extra:
            k = keep.setdefault(a.name, {})
            for fc in SC.action_fcurves(a):
                bone, prop = SC.bone_of(fc.data_path), fc.data_path.rsplit(".", 1)[-1]
                if bone and prop in G.PATHS:
                    k.setdefault(bone, set()).add(G.PATHS[prop])
    stripped = G.keep_channels(out, keep) if keep else {}
    # the style's game plays only some clips (STYLE.md §10, `export_clips`): leave the rest out of the GLB
    dropped, missing = [], []
    if S.load().get("export_clips") and arm is not None:
        dropped, missing = G.drop_animations(out, S.load()["export_clips"])
        if missing:
            warnings.append(f"export_clips not in this character: {missing}")
    # channels that never move (scale, most translations) cost bytes and change nothing (STYLE.md §10)
    pruned = G.prune_static(out) if S.load()["export"].get("prune_static_channels") else {}
    # skinned meshes: weights, AO colours and palette UVs as normalised integers (STYLE.md §10)
    packed = G.pack_vertices(out) if S.load()["export"].get("pack_vertex_data") else {}
    # palette textures: no mipmaps (STYLE.md §10)
    nearest = G.nearest_samplers(out) if S.load()["export"].get("texture_filter") == "NEAREST" else 0
    return {"outputs": [str(out)], "stats": {"bytes": out.stat().st_size, "fps": S.load()["animations"]["fps"],
                                             "actions": sorted(a.name for a in bpy.data.actions if a.name not in dropped),
                                             "arms_only_channels_removed": stripped,
                                             "clips_dropped": dropped, "static_channels": pruned,
                                             "packed_bytes_saved": packed,
                                             "samplers_min_nearest": nearest, "pieces": pieces},
            "warnings": warnings}
