"""Clips on an assembled character (STYLE.md §7a, §8, §9a): append, scale, bind, upright grips."""
import json
import math

import bpy
from mathutils import Matrix, Vector

from . import rig as R
from . import scene as SC
from . import style as S


def clip_names():
    return [c["name"] for c in S.load()["animations"]["clips"]]


def template_of(spec):
    style = S.load()
    arch = spec.get("archetype", style["default_archetype"])
    return json.loads(S.repo_path(style["archetypes"][arch]["template"]).read_text())


def archetype_of(spec):
    style = S.load()
    return style["archetypes"][spec.get("archetype", style["default_archetype"])]


def damp_rotations(action, factors):
    """Per-archetype clip adaptation (STYLE.md §8): play a bone's rotation keys at `factor` of their angle
    (slerp from the rest pose)."""
    from mathutils import Quaternion
    for bone, f in factors.items():
        path = f'pose.bones["{bone}"].rotation_quaternion'
        fcs = {fc.array_index: fc for fc in SC.action_fcurves(action) if fc.data_path == path}
        if len(fcs) != 4:
            continue
        n = len(fcs[0].keyframe_points)
        if any(len(fc.keyframe_points) != n for fc in fcs.values()):
            raise RuntimeError(f"{action.name}: {bone} rotation curves are not keyed on the same frames")
        for k in range(n):
            q = Quaternion([fcs[i].keyframe_points[k].co[1] for i in range(4)])
            d = Quaternion().slerp(q, f)
            for i in range(4):
                kp = fcs[i].keyframe_points[k]
                kp.co[1] = d[i]
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        for fc in fcs.values():
            fc.update()


def offset_rotations(action, offsets):
    """Per-archetype, per-clip correction (STYLE.md §8): `{bone: [axis, degrees]}` adds a fixed rotation about
    the bone's own local axis ('x', 'y' or 'z') on every key of `action` (q' = q @ offset), e.g. turning the
    dwarf's right wrist in `interact` so the axe swings past his face instead of through it."""
    from mathutils import Quaternion
    axes = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
    for bone, (axis, deg) in offsets.items():
        path = f'pose.bones["{bone}"].rotation_quaternion'
        fcs = {fc.array_index: fc for fc in SC.action_fcurves(action) if fc.data_path == path}
        if len(fcs) != 4:
            raise RuntimeError(f"{action.name}: no rotation keys on {bone} to correct")
        n = len(fcs[0].keyframe_points)
        if any(len(fc.keyframe_points) != n for fc in fcs.values()):
            raise RuntimeError(f"{action.name}: {bone} rotation curves are not keyed on the same frames")
        q_off = Quaternion(axes[axis], math.radians(deg))
        for k in range(n):
            q = Quaternion([fcs[i].keyframe_points[k].co[1] for i in range(4)])
            d = q @ q_off
            for i in range(4):
                kp = fcs[i].keyframe_points[k]
                kp.co[1] = d[i]
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        for fc in fcs.values():
            fc.update()


def upright_slots(spec):
    """{slot: slot bone} for the hand accessories the spec holds upright (spec.grip)."""
    sb = S.load()["skeleton"]["slot_bones"]
    return {s: sb[s] for s, mode in (spec.get("grip") or {}).items() if mode == "upright" and s in sb}


def add_clips(arm, spec):
    """Append the §8 clips (replacing earlier copies), scale their location keys to the character's
    proportions (§7a) and bind them to `arm`. Returns the actions."""
    names = clip_names()
    for a in [a for a in bpy.data.actions if a.name in names or a.name.split(".")[0] in names]:
        bpy.data.actions.remove(a)
    acts = R.append_actions(names)
    off = template_of(spec)["offset_factors"]
    damp = archetype_of(spec).get("clip_damping", {})
    offs = archetype_of(spec).get("clip_offsets", {})
    for a in acts:
        R.scale_clip_locations(a, off)
        damp_rotations(a, damp)
        offset_rotations(a, offs.get(a.name, {}))
    R.bind_actions(arm, acts)
    return sorted(acts, key=lambda a: names.index(a.name))


def _frames(action):
    f0, f1 = action.frame_range
    return range(int(round(f0)), int(round(f1)) + 1)


def _slot_vertices(char, slot):
    a = char.data.attributes.get("slot")
    if a is None:
        return []
    i = S.slot_index(slot)
    out = set()
    for p in char.data.polygons:
        if a.data[p.index].value == i:
            out.update(p.vertices)
    return sorted(out)


class Clearance:
    """Keeps an upright item clear of the headwear (STYLE.md §9a): the hat's radial profile in the head bone's
    space (2 cm bins along the bone) and the item's samples along world +Z from its grip (rest pose)."""
    BIN = 0.02

    def __init__(self, arm, char, item_slot, slot_bone, margin):
        to_arm = arm.matrix_world.inverted() @ char.matrix_world
        head_inv = arm.data.bones["head"].matrix_local.inverted()
        self.profile = {}
        for i in _slot_vertices(char, "headwear"):
            q = head_inv @ (to_arm @ char.data.vertices[i].co)
            k = int(q.y // self.BIN)
            self.profile[k] = max(self.profile.get(k, 0.0), (q.x ** 2 + q.z ** 2) ** 0.5)
        grip = arm.data.bones[slot_bone].head_local
        rows = {}
        for i in _slot_vertices(char, item_slot):
            p = to_arm @ char.data.vertices[i].co
            k = int((p.z - grip.z) // self.BIN)
            rows[k] = max(rows.get(k, 0.0), ((p.x - grip.x) ** 2 + (p.y - grip.y) ** 2) ** 0.5)
        self.samples = [((k + 0.5) * self.BIN, r + margin) for k, r in sorted(rows.items())]
        self.bottom = min((to_arm @ char.data.vertices[i].co).z for i in _slot_vertices(char, item_slot)) - grip.z \
            if rows else 0.0
        self.ok = bool(self.profile and self.samples)

    def lean(self, arm, grip, max_deg=40):
        """Smallest outward tilt (radians, axis) around `grip` that keeps the item clear of the hat."""
        if not self.ok:
            return 0.0, None
        head = arm.pose.bones["head"].matrix
        hinv = head.inverted()
        d = grip - head.translation
        d.z = 0
        if d.length < 1e-6:
            return 0.0, None
        d.normalize()
        axis = Vector((0, 0, 1)).cross(d).normalized()
        for deg in range(0, max_deg + 1):
            r = Matrix.Rotation(math.radians(deg), 3, axis)
            clear = True
            for t, rad in self.samples:
                q = hinv @ (grip + r @ Vector((0, 0, t)))
                hat = self.profile.get(int(q.y // self.BIN))
                if hat is not None and (q.x ** 2 + q.z ** 2) ** 0.5 < hat + rad:
                    clear = False
                    break
            if clear:
                return math.radians(deg), axis
        return math.radians(max_deg), axis


def bake_upright(arm, action, slot_bone, held=False, clearance=None):
    """Key `slot_bone` so it follows its parent's position but keeps its rest orientation in armature
    space (STYLE.md §9a, grip `upright`): staffs, banners and lanterns stay vertical in every clip.
    clearance: a Clearance; where the item would cut through the headwear it leans outward around the grip
    just enough (e.g. the staff's crystal and the hat brim in `run`), and where its foot would go below the
    floor it slides up in the hand.
    held=True: upright only at the first frame, then fixed in the hand (e.g. `die`: the staff falls with
    the character instead of standing next to it). Returns the largest lean (degrees)."""
    pb = arm.pose.bones[slot_bone]
    parent = pb.parent
    rest = arm.data.bones[slot_bone].matrix_local
    prest_inv = arm.data.bones[parent.name].matrix_local.inverted()
    rot = rest.to_3x3().to_4x4()
    sc = bpy.context.scene
    SC.assign_action(arm, action)
    pb.rotation_mode = "QUATERNION"
    targets, grip, max_lean = [], None, 0.0
    for f in _frames(action):
        sc.frame_set(f)
        natural = parent.matrix @ prest_inv @ rest   # where the slot would be, held like the hand
        upright = Matrix.Translation(natural.translation) @ rot
        if held:
            if grip is None:
                grip = parent.matrix.inverted() @ upright   # the slot relative to the hand at the start
            upright = parent.matrix @ grip
        elif clearance is not None:
            ang, axis = clearance.lean(arm, natural.translation)
            if ang > 0:
                upright = (Matrix.Translation(natural.translation) @ Matrix.Rotation(ang, 4, axis) @ rot)
                max_lean = max(max_lean, math.degrees(ang))
            # the item's foot stays on/above the floor: it slides up in the hand (staff on landing in `jump`)
            foot = upright.translation + upright.to_3x3() @ rot.to_3x3().inverted() @ Vector((0, 0, clearance.bottom))
            if foot.z < 0:
                upright = Matrix.Translation((0, 0, -foot.z)) @ upright
        targets.append((f, upright))
    path = f'pose.bones["{slot_bone}"]'
    SC.remove_fcurves(action, lambda fc: fc.data_path.startswith(path))
    prev = None
    for f, m in targets:
        sc.frame_set(f)
        pb.matrix = m
        bpy.context.view_layer.update()
        q = pb.rotation_quaternion.copy()
        if prev is not None and q.dot(prev) < 0:   # q and -q are the same rotation: keep keys continuous
            q.negate()
            pb.rotation_quaternion = q
        prev = q
        pb.keyframe_insert("location", frame=f)
        pb.keyframe_insert("rotation_quaternion", frame=f)
    for fc in SC.action_fcurves(action):
        if fc.data_path.startswith(path):
            for k in fc.keyframe_points:
                k.interpolation = "LINEAR"
    return max_lean


def _lowest(char, verts):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = char.evaluated_get(dg)
    m = ev.to_mesh()
    mw = char.matrix_world
    z = min((mw @ m.vertices[i].co).z for i in verts)
    ev.to_mesh_clear()
    return z


def body_vertices(char):
    """Vertex indices of the base parts (not accessories; assembled characters carry the face attribute
    `slot`). Staffs may touch the floor; the body may not go through it."""
    a = char.data.attributes.get("slot")
    if a is None:
        return []
    slots = S.load()["slots"]
    base = {i for i, s in enumerate(slots) if not s.startswith("accessory")}
    out = set()
    for p in char.data.polygons:
        if a.data[p.index].value in base:
            out.update(p.vertices)
    return sorted(out)


def floor_clamp(arm, char, action, body_verts):
    """Raise `hips` per frame by the depth of the body's lowest point below the floor (STYLE.md §7a).

    Chibi feet are long for their legs, so heel strike / toe-off pitch them deeper than in the source
    rig. Frames with the body above the floor stay as they are. Returns the largest lift (m)."""
    sc = bpy.context.scene
    SC.assign_action(arm, action)
    pb = arm.pose.bones["hips"]
    to_local = arm.data.bones["hips"].matrix_local.to_3x3().inverted()
    samples = []
    for f in _frames(action):
        sc.frame_set(f)
        lift = max(0.0, -_lowest(char, body_verts))
        samples.append((f, pb.location.copy() + to_local @ Vector((0, 0, lift)), lift))
    if max(s[2] for s in samples) < 1e-4:
        return 0.0
    path = 'pose.bones["hips"].location'
    SC.remove_fcurves(action, lambda fc: fc.data_path == path)
    for f, loc, _ in samples:
        pb.location = loc
        pb.keyframe_insert("location", frame=f)
    return max(s[2] for s in samples)
