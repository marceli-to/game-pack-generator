"""Import a GLB into the open character .blend.

args: { path, out, normalize?: false }
normalize: apply object transforms, rename the single armature to 'Armature' and, if there is
exactly one mesh, rename it to 'Character' (for checking external models against the rules).
"""
import bpy

from lib import scene as SC
from lib import style as S


def run(args):  # noqa: C901
    new = SC.import_glb(args["path"])
    warnings = []
    # The glTF importer creates display shapes for bones (e.g. an icosphere mesh object);
    # they are not character geometry.
    shapes = {pb.custom_shape for o in new if o.type == "ARMATURE" for pb in o.pose.bones if pb.custom_shape}
    for o in new:
        if o.type == "ARMATURE":
            for pb in o.pose.bones:
                pb.custom_shape = None
    shape_names = {o.name for o in shapes}
    new = [o for o in new if o.name not in shape_names]
    for n in shape_names:
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    if args.get("normalize"):
        sk = S.load()["skeleton"]
        for o in new:
            o.select_set(True)
        bpy.context.view_layer.objects.active = new[0] if new else None
        if new:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        arms = [o for o in new if o.type == "ARMATURE"]
        meshes = [o for o in new if o.type == "MESH"]
        if len(arms) == 1:
            arms[0].name = sk["armature_object"]
        elif len(arms) > 1:
            warnings.append(f"{len(arms)} armatures imported; not renamed")
        if len(meshes) == 1:
            meshes[0].name = sk["mesh_object"]
        elif len(meshes) > 1:
            warnings.append(f"{len(meshes)} meshes imported; not joined or renamed")
    SC.save(args["out"])
    summary = {}
    for o in new:
        summary.setdefault(o.type.lower(), []).append(o.name)
    return {"outputs": [args["out"]], "stats": {"imported": summary,
                                                 "actions": sorted(a.name for a in bpy.data.actions)},
            "warnings": warnings}
