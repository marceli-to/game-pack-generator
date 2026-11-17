"""Export the open .blend as GLB per STYLE.md §10.

args: { out: <path.glb> }
"""
from pathlib import Path

import bpy

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
    return {"outputs": [str(out)], "stats": {"bytes": out.stat().st_size, "fps": S.load()["animations"]["fps"],
                                             "actions": sorted(a.name for a in bpy.data.actions),
                                             "arms_only_channels_removed": stripped},
            "warnings": warnings}
