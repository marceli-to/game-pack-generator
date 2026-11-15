"""Skeleton, proportion templates and clip scaling (STYLE.md §7, §7a)."""
import json

import bpy
from mathutils import Vector

from . import scene as SC
from . import style as S

SKELETON_BLEND = "library/skeleton.blend"
ANIMATIONS_BLEND = "library/animations.blend"

# Segment groups of the KayKit Rig_Medium bones (STYLE.md §7).
LEG = ("upperleg", "lowerleg")
FOOT = ("foot", "toes")
ARM = ("upperarm", "lowerarm", "wrist", "hand", "handslot")
HEAD = ("head", "headslot")


def group_of(bone_name):
    base = bone_name.split(".")[0]
    if bone_name == "root" or base in LEG:
        return "leg"
    if base in FOOT:
        return "foot"
    if base in ARM:
        return "arm"
    if base in HEAD:
        return "head"
    return "torso"  # hips, spine, chest, backslot


def append_skeleton():
    """Append the standard armature from library/skeleton.blend into the current scene."""
    path = S.repo_path(SKELETON_BLEND)
    name = S.load()["skeleton"]["armature_object"]
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n == name]
    obj = dst.objects[0]
    bpy.context.scene.collection.objects.link(obj)
    return obj


def append_actions(names=None):
    """Append actions from library/animations.blend (all clips, or the given names)."""
    path = S.repo_path(ANIMATIONS_BLEND)
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.actions = [n for n in src.actions if names is None or n in names]
    return list(dst.actions)


def rest_layout(arm):
    """{bone: (head, tail, roll)} in armature space, read from edit bones."""
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    out = {e.name: (e.head.copy(), e.tail.copy(), e.roll) for e in arm.data.edit_bones}
    bpy.ops.object.mode_set(mode="OBJECT")
    return out


def compute_layout(src, targets):
    """New rest layout for a proportion template.

    src: rest_layout() of the source rig. targets (metres, rest pose, T-pose):
      hip_z        height of the hip joints (upperleg heads) -> leg factor
      head_base_z  height of the head joint (head bone head)  -> torso factor
      head_top_z   top of the head mesh (head bone tail)       -> head factor
      arm_length   shoulder (upperarm head) to wrist joint (hand head) -> arm factor
      shoulder_x   |x| of the shoulder joints
      hip_x        |x| of the hip joints
      ankle_z      height of the ankle joints (optional; default: scales with the legs)
      foot_length  ankle to toe tip, along -Y (optional; default: leg factor)
    Bone directions and rolls are preserved; only lengths/offsets change, so
    rotation keys of the clips stay valid.
    """
    def H(n):
        return src[n][0]

    def T(n):
        return src[n][1]

    # Legs: hip joint -> ankle spans hip_z - ankle_z; the root->hips offset absorbs the rest,
    # so ankle height and foot size can be set independently of the leg length.
    src_hip, src_ankle = H("upperleg.l").z, H("foot.l").z
    ankle_z = targets.get("ankle_z", src_ankle * targets["hip_z"] / src_hip)
    f_leg = (targets["hip_z"] - ankle_z) / (src_hip - src_ankle)
    hips_z = targets["hip_z"] - (src_hip - H("hips").z) * f_leg
    f_root = hips_z / H("hips").z
    f_torso = (targets["head_base_z"] - hips_z) / (H("head").z - H("hips").z)
    f_arm = targets["arm_length"] / (H("hand.l") - H("upperarm.l")).length
    f_head = (targets["head_top_z"] - targets["head_base_z"]) / (T("head") - H("head")).length
    src_foot = abs(T("toes.l").y - H("foot.l").y)
    f_foot = targets["foot_length"] / src_foot if "foot_length" in targets else f_leg
    factors = {"leg": f_leg, "torso": f_torso, "arm": f_arm, "head": f_head, "foot": f_foot}

    parents = {}
    for b in S.load()["skeleton"]["bones"]:
        parents[b["name"]] = b["parent"]
    children = {}
    for n, p in parents.items():
        children.setdefault(p, []).append(n)

    def own(n):
        return factors[group_of(n)]

    def offset_factor(n):
        p = parents[n]
        if p is None or n == "hips":
            return f_leg  # root at the floor; root->hips is a leg-height offset
        if p in ("root", "hips"):
            return own(n)  # children of the pelvis: legs scale with legs, spine with torso
        return own(p)

    new, off = {}, {}

    def place(n):
        h, t, roll = src[n]
        p = parents[n]
        f_off = offset_factor(n)
        f_place = f_root if n == "hips" else f_off
        nh = h.copy() if p is None else new[p][0] + (h - src[p][0]) * f_place
        new[n] = (nh, nh + (t - h) * own(n), roll)
        off[n] = f_off
        for c in children.get(n, []):
            place(c)

    place("root")

    # Explicit widths: shift each arm / leg subtree sideways.
    def shift(n, dx):
        h, t, r = new[n]
        new[n] = (h + Vector((dx, 0, 0)), t + Vector((dx, 0, 0)), r)
        for c in children.get(n, []):
            shift(c, dx)

    for side, sign in (("l", 1), ("r", -1)):
        if "shoulder_x" in targets:
            shift(f"upperarm.{side}", sign * targets["shoulder_x"] - new[f"upperarm.{side}"][0].x)
        if "hip_x" in targets:
            shift(f"upperleg.{side}", sign * targets["hip_x"] - new[f"upperleg.{side}"][0].x)
    return new, factors, off


def apply_layout(arm, layout):
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    for e in eb:
        e.use_connect = False
    for n, (h, t, roll) in layout.items():
        e = eb[n]
        e.head = Vector(h)
        e.tail = Vector(t)
        e.roll = roll
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()


def load_template(path):
    data = json.loads(S.repo_path(path).read_text() if not str(path).startswith("/") else open(path).read())
    layout = {n: (Vector(b["head"]), Vector(b["tail"]), b["roll"]) for n, b in data["bones"].items()}
    return data, layout


def apply_template(arm, template_path):
    data, layout = load_template(template_path)
    apply_layout(arm, layout)
    return data


def scale_clip_locations(action, offset_factors):
    """Scale location keys per bone by the factor of the offset they move (STYLE.md §7a)."""
    for fc in SC.action_fcurves(action):
        b = SC.bone_of(fc.data_path)
        if b is None or not fc.data_path.endswith("location"):
            continue
        f = offset_factors.get(b, 1.0)
        for k in fc.keyframe_points:
            k.co[1] *= f
            k.handle_left[1] *= f
            k.handle_right[1] *= f


def bind_actions(arm, actions):
    """Rename each action's slot to match `arm` so it binds (and exports) cleanly."""
    for a in actions:
        if len(a.slots):
            a.slots[0].name_display = arm.name
        a.use_fake_user = True
