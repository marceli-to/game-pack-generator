"""Clips on an assembled character (STYLE.md §7a, §8, §9a): append, scale, bind, upright grips."""
import json
import math

import bpy
from mathutils import Matrix, Vector

from . import rig as R
from . import scene as SC
from . import style as S


def clip_names(spec=None):
    """The §8 clips, plus the §8b extra clips the spec opts into (spec.extra_clips)."""
    anim = S.load()["animations"]
    extra = {c["name"] for c in anim.get("extra_clips", [])}
    wanted = (spec or {}).get("extra_clips", [])
    unknown = [n for n in wanted if n not in extra]
    if unknown:
        raise ValueError(f"unknown extra clips {unknown}; have {sorted(extra)}")
    by = {c["name"]: c for c in anim.get("extra_clips", [])}
    missing = sorted({by[n]["over"] for n in wanted if by[n].get("over") and by[n]["over"] not in wanted})
    if missing:
        raise ValueError(f"extra clips {[n for n in wanted if by[n].get('over') in missing]} are baked over {missing}; add those too")
    return [c["name"] for c in anim["clips"]] + [n for n in wanted]


def clip_config(name):
    anim = S.load()["animations"]
    return next(c for c in anim["clips"] + anim.get("extra_clips", []) if c["name"] == name)


def is_arms_only(name):
    return bool(clip_config(name).get("arms_only"))


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
    names = clip_names(spec)
    every = clip_names({"extra_clips": [c["name"] for c in S.load()["animations"].get("extra_clips", [])]})
    for a in [a for a in bpy.data.actions if a.name in every or a.name.split(".")[0] in every]:
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
    for a in acts:
        if is_arms_only(a.name):
            over = clip_config(a.name).get("over")
            base = next(b for b in acts if b.name == over) if over else None
            a["arms_only_report"] = bake_arms_only(arm, a, base)
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


# --- stride (STYLE.md §8, clip_stride) --------------------------------------------------------------

def _two_bone(S_, W, P, a, b):
    """Knee/elbow position and reached end for a two-bone chain from S_ towards W, bending towards P."""
    d_vec = W - S_
    d = max(min(d_vec.length, a + b - 1e-4), abs(a - b) + 1e-4)
    n = d_vec.normalized()
    m = (P - S_) - n * n.dot(P - S_)
    m = m.normalized() if m.length > 1e-6 else n.orthogonal().normalized()
    cos_a = (a * a + d * d - b * b) / (2 * a * d)
    sin_a = math.sqrt(max(0.0, 1 - cos_a * cos_a))
    return S_ + n * a * cos_a + m * a * sin_a, S_ + n * d


def bake_stride(arm, action, speed):
    """Re-plant the feet of a looping locomotion clip for a ground speed of `speed` m/s (STYLE.md §8).

    Per foot: the stance (frames where the ankle or the toe joint is within `animations.stride.contact` of
    its lowest in the clip, the longest such run) moves backwards at exactly `speed`, centred where the clip centres it;
    the swing is scaled about the same centre by the stance's factor, so it lifts off and lands where the new
    stance ends and starts. The hips rise where a planted foot now stands closer under them, so the planted
    leg is as extended as in the clip (interpolated over frames with no foot down). Other heights, sideways positions and the foot orientation stay as in the clip;
    thigh and shin are solved with a two-bone IK bending towards the clip's knee. Assumes the clip loops
    (last frame = first) and the armature has no object transform. Returns per side the source stance speed,
    the stride factor, stance frames and the IK reach error."""
    mw = arm.matrix_world
    if any(abs(mw[r][c] - (r == c)) > 1e-4 for r in range(4) for c in range(4)):
        raise RuntimeError("bake_stride needs an armature without object transform")
    cfg = S.load()["animations"]["stride"]
    fps = bpy.context.scene.render.fps
    bones = arm.data.bones
    rest = {b.name: b.matrix_local.copy() for b in bones}
    f0, f1 = (int(round(x)) for x in action.frame_range)
    N = f1 - f0
    for pb in arm.pose.bones:   # bones the clip doesn't key keep the last pose otherwise
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.scene.frame_set(f0 - 1)   # else frame_set(f0) on the current frame keeps the reset pose
    src = {f: _arm_space_pose(arm, action, f) for f in range(f0, f1 + 1)}
    keys, report, legs = {}, {}, {}
    for side in ("l", "r"):
        U, L, F = (f"{b}.{side}" for b in cfg["leg_bones"])
        # planted: the ankle (flat foot) or the toe joint (heel off) within `contact` of its own lowest
        ankle = [src[f0 + i][F].translation.z for i in range(N)]
        ball = [(src[f0 + i][F] @ Matrix.Translation((0, bones[F].length, 0))).translation.z for i in range(N)]
        ys = [src[f0 + i][F].translation.y for i in range(N)]
        on = [ankle[i] < min(ankle) + cfg["contact"] or ball[i] < min(ball) + cfg["contact"] for i in range(N)]
        if all(on) or not any(on):
            raise RuntimeError(f"{action.name}: no stance/swing split for foot.{side}")
        # longest cyclic run of contact frames: start index a, length n
        best = (0, 0)
        for a in range(N):
            if on[a] and not on[a - 1]:
                n = 0
                while on[(a + n) % N]:
                    n += 1
                best = max(best, (n, a))
        n, a = best
        b = a + n - 1
        dur = (b - a) / fps
        span = ys[b % N] - ys[a]
        sgn = 1.0 if span > 0 else -1.0
        span = abs(span)
        y_m = (ys[b % N] + ys[a]) / 2
        k = speed * dur / span
        target, stance = {}, set()
        for i in range(N):
            j = (i - a) % N            # frames since the stance began
            if j <= b - a:
                target[i] = y_m + sgn * speed * ((j - (b - a) / 2) / fps)
                stance.add(i)
            else:
                target[i] = y_m + k * (ys[i] - y_m)
        legs[side] = (U, L, F, target, stance)
        report[side] = {"source_speed_m_s": round(span / dur, 3), "factor": round(k, 3),
                        "stance_frames": [f0 + a, f0 + b % N]}
    # hips: raised where a planted foot comes closer under them, so the planted leg is as extended as in the
    # clip (a shorter stride under sprint-low hips folds the knees); frames with no foot down are interpolated
    lift = {}
    for i in range(N):
        need = []
        for U, L, F, target, stance in legs.values():
            if i in stance:
                p = src[f0 + i]
                H, Ws = p[U].translation, p[F].translation
                D = (H - Ws).length
                h2 = (H.x - Ws.x) ** 2 + (H.y - target[i]) ** 2
                need.append(Ws.z + math.sqrt(max(0.0, D * D - h2)) - H.z)
        if need:
            lift[i] = max(0.0, max(need))
    known = sorted(lift)
    for i in range(N):
        if i not in lift:
            prev = max((j for j in known if j < i), default=known[-1] - N)
            nxt = min((j for j in known if j > i), default=known[0] + N)
            t = (i - prev) / (nxt - prev)
            lift[i] = lift[prev % N] * (1 - t) + lift[nxt % N] * t
    hips = bones[next(iter(legs.values()))[0]].parent.name
    hp = arm.pose.bones[hips]
    to_local = rest[hips].to_3x3().inverted()
    hip_locs = {}
    SC.assign_action(arm, action)
    for i in range(N + 1):
        bpy.context.scene.frame_set(f0 + i)
        hip_locs[f0 + i] = hp.location.copy() + to_local @ Vector((0, 0, lift[i % N]))
    for side, (U, L, F, target, stance) in legs.items():
        a_len = (rest[U].inverted() @ rest[L]).translation.length
        b_len = (rest[L].inverted() @ rest[F]).translation.length
        v_u = (rest[U].inverted() @ rest[L]).translation
        v_l = (rest[L].inverted() @ rest[F]).translation
        err = 0.0
        for i in range(N + 1):
            f = f0 + i
            p = src[f]
            up = Matrix.Translation((0, 0, lift[i % N]))
            H = p[U].translation + up.translation
            W = p[F].translation.copy()
            W.y = target[i % N]
            E, W2 = _two_bone(H, W, p[L].translation + up.translation, a_len, b_len)
            err = max(err, (W2 - W).length)
            rots = {U: _swing(p[U].to_3x3().normalized(), v_u, E - H),
                    L: _swing(p[L].to_3x3().normalized(), v_l, W2 - E),
                    F: p[F].to_3x3().normalized()}
            pp = up @ p[bones[U].parent.name]
            for bn in (U, L, F):
                base = pp @ (rest[bones[bn].parent.name].inverted() @ rest[bn])
                tgt = Matrix.Translation(base.translation) @ rots[bn].to_4x4()
                basis = base.inverted() @ tgt
                _, q, _ = basis.decompose()
                ks = keys.setdefault(bn, [])
                if ks and ks[-1][1].dot(q) < 0:
                    q.negate()
                ks.append((f, q))
                pp = base @ basis
        report[side]["reach_error_m"] = round(err, 4)
    report["hips_lift_m"] = round(max(lift.values()), 4)
    if report["hips_lift_m"] > 1e-4:
        SC.remove_fcurves(action, lambda fc: fc.data_path == f'pose.bones["{hips}"].location')
        for f, loc in hip_locs.items():
            hp.location = loc
            hp.keyframe_insert("location", frame=f)
    names = set(keys)
    SC.remove_fcurves(action, lambda fc: any(fc.data_path == f'pose.bones["{bn}"].rotation_quaternion' for bn in names))
    bag = action.layers[0].strips[0].channelbag(action.slots[0])
    for bn, ks in keys.items():
        arm.pose.bones[bn].rotation_mode = "QUATERNION"
        for i in range(4):
            fc = bag.fcurves.new(f'pose.bones["{bn}"].rotation_quaternion', index=i)
            fc.keyframe_points.add(len(ks))
            for kp, (f, q) in zip(fc.keyframe_points, ks):
                kp.co = (f, q[i])
                kp.interpolation = "LINEAR"
            fc.update()
    # measured on the baked clip: the planted ankle's speed between consecutive stance frames
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.scene.frame_set(f0 - 1)
    baked = {f: _arm_space_pose(arm, action, f) for f in range(f0, f1 + 1)}
    for side, (U, L, F, target, stance) in legs.items():
        v = [(baked[f0 + i + 1][F].translation - baked[f0 + i][F].translation).length * fps
             for i in range(N) if i in stance and (i + 1) % N in stance]
        report[side]["stance_speed_m_s"] = [round(min(v), 3), round(max(v), 3)]
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    return {"speed_m_s": speed, **report}


# --- arms-only clips (STYLE.md §8b) ------------------------------------------------------------------

def arm_chain(side):
    return [f"{b}.{side}" for b in S.load()["animations"]["arms_only_bones"]]


def _arm_space_pose(arm, action, frame):
    SC.assign_action(arm, action)
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    return {pb.name: pb.matrix.copy() for pb in arm.pose.bones}


def _swing(rot, v_local, target_dir):
    """`rot` turned by the smallest rotation that points its local vector `v_local` along `target_dir`."""
    cur = (rot @ v_local).normalized()
    return cur.rotation_difference(target_dir.normalized()).to_matrix() @ rot


def bake_arms_only(arm, action, over=None):
    """Rewrite `action` to arm-bone rotations only, for an upright, forward-facing torso (STYLE.md §8b),
    or, with `over` (the base clip, e.g. `crouch`), for the torso as posed at that clip's first frame
    (the hands keep their world orientation, so the gun stays level on a leaning chest).

    Per frame of the source clip: the hands keep their armature-space orientation (the gun points where the
    clip points it) and their position relative to the midpoint of the shoulders; the torso, legs and hips
    stay at rest. Upper and lower arm are solved with a two-bone IK to reach the wrist, bending towards the
    clip's elbow. Where a wrist is out of reach, both hands move together towards that shoulder (the grip on
    the gun stays). With a `stance` in the clip's config (2H) the right wrist is placed at a fixed point
    forward of the right shoulder instead, the elbows bend down. Every other curve is removed. Returns the remaining reach error per side, how far the
    hands were moved in, and the frame range."""
    bones = arm.data.bones
    rest = {b.name: b.matrix_local.copy() for b in bones}
    chains = {s: arm_chain(s) for s in ("l", "r")}
    f0, f1 = (int(round(x)) for x in action.frame_range)
    frames = list(range(f0, f1 + 1))
    src = {f: _arm_space_pose(arm, action, f) for f in frames}
    # the torso the arms are solved on: rest, or the base clip's first frame (over, STYLE.md §8b)
    torso = _arm_space_pose(arm, over, int(round(over.frame_range[0]))) if over else rest
    par = {s: bones[chains[s][0]].parent.name for s in chains}
    sh = {s: (torso[par[s]] @ (rest[par[s]].inverted() @ rest[chains[s][0]])).translation for s in chains}

    def anchor(pose):
        return (pose["upperarm.l"].translation + pose["upperarm.r"].translation) / 2

    a_rest = (sh["l"] + sh["r"]) / 2
    # stance (STYLE.md §8b, 2H clips): the right wrist goes to a fixed point forward of / inside / below the right
    # shoulder (fractions of the arm's length), the left hand keeps its place on the gun relative to the right,
    # the clip's sway and recoil ride on top, the elbows bend down
    stance = clip_config(action.name).get("stance")
    # sides (STYLE.md §8b): the arms the clip keys; 1H clips key the right arm only, the left comes from the base clip
    sides = clip_config(action.name).get("sides", ["l", "r"])
    if stance:
        cr = chains["r"]
        L = ((rest[cr[0]].inverted() @ rest[cr[1]]).translation.length
             + (rest[cr[1]].inverted() @ rest[cr[2]]).translation.length)
        st_target = sh["r"] + Vector((stance["inward"] * L, -stance["forward"] * L, -stance["down"] * L))
        mean_r = sum((src[f][cr[2]].translation for f in frames), Vector()) / len(frames)
        lft = stance["left"]
    keys = {b: [] for s in chains for b in chains[s]}
    err = {"l": 0.0, "r": 0.0}
    shift = 0.0
    aim = {"yaw": 0.0, "pitch": 0.0, "spacing": 0.0, "forward": 9.0, "stance_spacing": 0.0}
    for f in frames:
        final = {}
        p = src[f]
        off = (st_target - mean_r) if stance else (a_rest - anchor(p))
        off0 = off.copy()
        if stance:
            # wrists placed directly: right = the stance point + the clip's sway/recoil, left = a short way
            # along the gun from it (the clip's own spacing comes from its turned stance and is far too wide
            # for an upright torso)
            Wr = p[chains["r"][2]].translation + off
            g = (p[chains["r"][-1]].to_3x3().normalized() @ Vector((1, 0, 0))).normalized()
            Wl = Wr + g * (lft["along"] * L) + Vector((lft["out"] * L, 0.0, -lft["down"] * L))
            place = {"r": Wr, "l": Wl}
            # recoil can carry the grip out of one arm's reach: move both hands together towards that shoulder
            for _ in range(4):
                worst = None
                for side, chain in chains.items():
                    up, lo, wr = chain[0], chain[1], chain[2]
                    reach = ((rest[up].inverted() @ rest[lo]).translation.length
                             + (rest[lo].inverted() @ rest[wr]).translation.length) * 0.995
                    v = sh[side] - place[side]
                    excess = v.length - reach
                    if excess > 1e-4 and (worst is None or excess > worst[0]):
                        worst = (excess, v.normalized())
                if worst is None:
                    break
                for k in place:
                    place[k] = place[k] + worst[1] * worst[0]
                off = off + worst[1] * worst[0]
        # out of reach on the upright torso (the turned stance brings a shoulder forward): move both hands
        # together towards that shoulder, so the hands keep their grip on the gun
        for _ in range(0 if stance else 4):
            worst = None
            for side, chain in ((k, v) for k, v in chains.items() if k in sides):
                up, lo, wr = chain[0], chain[1], chain[2]
                reach = ((rest[up].inverted() @ rest[lo]).translation.length
                         + (rest[lo].inverted() @ rest[wr]).translation.length) * 0.995
                v = sh[side] - (p[wr].translation + off)
                excess = v.length - reach
                if excess > 1e-4 and (worst is None or excess > worst[0]):
                    worst = (excess, v.normalized())
            if worst is None:
                break
            off += worst[1] * worst[0]
        shift = max(shift, (off - off0).length)
        for side, chain in chains.items():
            up, lo, wr = chain[0], chain[1], chain[2]
            # rest offsets of each child's head in its parent's space (bone may not be connected)
            v_u = (rest[up].inverted() @ rest[lo]).translation
            v_l = (rest[lo].inverted() @ rest[wr]).translation
            a, b = v_u.length, v_l.length
            parent_pose = torso[par[side]]               # the torso stays at rest (or in the base pose)
            S_ = sh[side].copy()
            # stance: the shoulder joint comes forward (and a little in), standing in for the collarbone the
            # rig lacks, so the upper arms pass in front of the chest when both hands hold the gun
            prot = Vector((0.0, 0.0, 0.0))
            if stance and "shoulder" in stance:
                sgn = 1.0 if side == "l" else -1.0
                prot = Vector((-sgn * stance["shoulder"]["in"], -stance["shoulder"]["forward"], 0.0))
                S_ = S_ + prot
            W = place[side] if stance else p[wr].translation + off
            P = p[lo].translation + off
            if stance:   # elbows down, forward and out (clear of the chest), not the clip's (its stance turns the body)
                out = Vector((1.0 if side == "l" else -1.0, 0.0, 0.0))
                el = stance.get("elbow", {"out": 0.08, "forward": 0.0, "down": 0.3})
                P = (S_ + W) / 2 + Vector((0, -el["forward"], -el["down"])) + out * el["out"]
            d_vec = W - S_
            d = max(min(d_vec.length, a + b - 1e-4), abs(a - b) + 1e-4)
            n = d_vec.normalized()
            m = (P - S_) - n * n.dot(P - S_)
            m = m.normalized() if m.length > 1e-6 else n.orthogonal().normalized()
            cos_a = (a * a + d * d - b * b) / (2 * a * d)
            sin_a = math.sqrt(max(0.0, 1 - cos_a * cos_a))
            E = S_ + n * a * cos_a + m * a * sin_a
            W2 = S_ + n * d
            err[side] = max(err[side], (W2 - W).length)
            r_up = _swing(p[up].to_3x3().normalized(), v_u, E - S_)
            r_lo = _swing(p[lo].to_3x3().normalized(), v_l, W2 - E)
            target_rot = {up: r_up, lo: r_lo}
            for bn in chain[2:]:
                target_rot[bn] = p[bn].to_3x3().normalized()
            # walk down the chain: pose = parent_pose @ rest_local @ basis (basis: rotation only)
            pp = parent_pose
            for i, bn in enumerate(chain):
                pb = bones[bn].parent.name
                rest_local = rest[pb].inverted() @ rest[bn]
                base = pp @ rest_local
                if i == 0:   # upper arm: rotation, head on the rest torso (+ the stance's shoulder shift)
                    target = Matrix.Translation(base.translation + prot) @ target_rot[bn].to_4x4()
                elif i == 1:   # lower arm: rotation only
                    target = Matrix.Translation(base.translation) @ target_rot[bn].to_4x4()
                else:       # wrist, hand, slot: the clip's offset from the parent (recoil moves the slot)
                    t = (pp @ (p[pb].inverted() @ p[bn])).translation
                    target = Matrix.Translation(t) @ target_rot[bn].to_4x4()
                basis = base.inverted() @ target
                loc, q, _ = basis.decompose()
                if keys[bn] and keys[bn][-1][1].dot(q) < 0:
                    q.negate()
                keys[bn].append((f, q, loc))
                pp = base @ basis
            final[side] = pp
        # report: where the gun points (handslot.r local +X) and whether the hands keep their spacing
        g = final["r"].to_3x3().normalized() @ Vector((1, 0, 0))
        yaw = math.degrees(math.atan2(g.x, -g.y))
        pitch = math.degrees(math.asin(max(-1.0, min(1.0, g.z))))
        spacing = (final["l"].translation - final["r"].translation).length
        spacing_src = (p[chains["l"][-1]].translation - p[chains["r"][-1]].translation).length
        aim["yaw"] = max(aim["yaw"], abs(yaw))
        aim["pitch"] = max(aim["pitch"], abs(pitch))
        if len(sides) == 2:   # one-sided clips: the other hand is not on the gun
            aim["spacing"] = max(aim["spacing"], abs(spacing - spacing_src))
        if stance:   # how far in front of the shoulders the hands are, and how far apart (the gun grip)
            fwd = a_rest.y - (final["l"].translation.y + final["r"].translation.y) / 2
            aim["forward"] = min(aim["forward"], fwd)
            aim["stance_spacing"] = max(aim["stance_spacing"], spacing)
    # replace every curve by the baked arm rotations (only the clip's sides)
    keys = {bn: ks for bn, ks in keys.items() if any(bn in chains[sd] for sd in sides)}
    SC.remove_fcurves(action, lambda fc: True)
    bag = action.layers[0].strips[0].channelbag(action.slots[0])
    for bn, ks in keys.items():
        arm.pose.bones[bn].rotation_mode = "QUATERNION"
        curves = [("rotation_quaternion", i, [q[i] for _, q, _ in ks]) for i in range(4)]
        if max(l.length for _, _, l in ks) > 1e-4:
            curves += [("location", i, [l[i] for _, _, l in ks]) for i in range(3)]
        for prop, i, vals in curves:
            fc = bag.fcurves.new(f'pose.bones["{bn}"].{prop}', index=i)
            fc.keyframe_points.add(len(ks))
            for k, (f, *_), v in zip(fc.keyframe_points, ks, vals):
                k.co = (f, v)
                k.interpolation = "LINEAR"
            fc.update()
    for pb in arm.pose.bones:   # clear what the source frames left on the pose
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    return {**({"over": over.name} if over else {}), "sides": sides, "reach_error_m": {s: round(e, 4) for s, e in err.items() if s in sides}, "hands_moved_in_m": round(shift, 4),
            "gun_max_yaw_deg": round(aim["yaw"], 1), "gun_max_pitch_deg": round(aim["pitch"], 1),
            **({"hand_spacing_change_m": round(aim["spacing"], 4)} if len(sides) == 2 else {}), "frames": [f0, f1],
            **({"stance": {"hands_forward_m": round(aim["forward"], 4), "hand_spacing_m": round(aim["stance_spacing"], 4),
                           "arm_length_m": round(L, 4)}} if stance else {})}
