"""Build library/skeleton.blend from KayKit Rig_Medium (STYLE.md §7).

args: { source_dir: <KayKit_Character_Animations_1.1>, out: "library/skeleton.blend" }
"""
from pathlib import Path

import bpy
from mathutils import Vector

from lib import scene as SC
from lib import style as S


def run(args):
    style = S.load()
    sk = style["skeleton"]
    src = Path(args["source_dir"]) / "Animations" / "gltf" / "Rig_Medium" / "Rig_Medium_General.glb"
    SC.empty_scene()
    SC.import_glb(src)
    arms = SC.armatures()
    if len(arms) != 1:
        raise RuntimeError(f"expected one armature in {src.name}, found {len(arms)}")
    arm = arms[0]
    for o in list(bpy.data.objects):
        if o is not arm:
            bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    arm.animation_data_clear()
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    arm.name = sk["armature_object"]
    arm.data.name = sk["armature_object"]

    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    head, chest = eb["head"], eb["chest"]
    # headslot: at the top of the head bone, pointing forward (-Y) like the handslots.
    hs = eb.new("headslot")
    hs.head = head.tail.copy()
    hs.tail = head.tail + Vector((0, -0.1, 0))
    hs.parent = head
    # backslot: behind the chest at shoulder-blade height, pointing backwards (+Y).
    bs = eb.new("backslot")
    mid = (chest.head + chest.tail) / 2
    bs.head = mid + Vector((0, 0.15, 0))
    bs.tail = bs.head + Vector((0, 0.1, 0))
    bs.parent = chest
    bpy.ops.object.mode_set(mode="OBJECT")

    want = {b["name"]: b for b in sk["bones"]}
    have = {b.name: b for b in arm.data.bones}
    missing = sorted(set(want) - set(have))
    extra = sorted(set(have) - set(want))
    if missing or extra:
        raise RuntimeError(f"bone mismatch vs style.json: missing={missing} extra={extra}")
    for n, spec in want.items():
        b = have[n]
        parent = b.parent.name if b.parent else None
        if parent != spec["parent"]:
            raise RuntimeError(f"bone {n}: parent {parent}, style.json says {spec['parent']}")
        b.use_deform = spec["deform"]

    out = S.repo_path(args.get("out", "library/skeleton.blend"))
    SC.save(out)
    bones = {b.name: {"head": [round(v, 4) for v in b.head_local], "tail": [round(v, 4) for v in b.tail_local],
                      "deform": b.use_deform} for b in arm.data.bones}
    return {"outputs": [str(out)], "stats": {"bones": len(bones), "deforming": sum(b["deform"] for b in bones.values())},
            "bones": bones}
