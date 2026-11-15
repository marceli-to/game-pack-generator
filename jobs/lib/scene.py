"""Scene helpers shared by the jobs."""
import bpy

from . import style as S


def empty_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = S.load()["animations"]["fps"]
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    return sc


def import_glb(path):
    """Import a GLB; returns the list of new objects."""
    before = set(bpy.data.objects)
    bpy.context.scene.render.fps = S.load()["animations"]["fps"]
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]


def armatures():
    return [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]


def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def main_armature():
    name = S.load()["skeleton"]["armature_object"]
    obj = bpy.context.scene.objects.get(name)
    if obj is not None and obj.type == "ARMATURE":
        return obj
    arms = armatures()
    return arms[0] if arms else None


def save(path):
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0  # no .blend1 backups
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)


def action_fcurves(action):
    """All F-curves of a (layered, Blender 4.4+) action."""
    out = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


def remove_fcurves(action, predicate):
    removed = 0
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in [fc for fc in bag.fcurves if predicate(fc)]:
                    bag.fcurves.remove(fc)
                    removed += 1
    return removed


def assign_action(obj, action):
    """Assign an action and its (first) slot to obj."""
    if obj.animation_data is None:
        obj.animation_data_create()
    obj.animation_data.action = action
    if getattr(obj.animation_data, "action_slot", None) is None and len(action.slots):
        obj.animation_data.action_slot = action.slots[0]


def bone_of(data_path):
    if data_path.startswith('pose.bones["'):
        return data_path.split('"')[1]
    return None
