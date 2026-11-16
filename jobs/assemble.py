"""Assemble a character from parts (STYLE.md §9a).

args: { spec: {...}, out: <character.blend> }
Template -> standard skeleton -> parts appended -> `slot` attribute -> rigid weights (nearest allowed
bone) -> joined into `Character`, parented to `Armature` -> palette applied from spec.colors.
"""
import json

import bpy
import numpy as np

from lib import anim as A
from lib import palette as PAL
from lib import parts as PT
from lib import rig as R
from lib import scene as SC
from lib import shading as SH
from lib import style as S


def skirt_weights(obj, arm, cfg):
    """Long robe without legs (STYLE.md §9a): below the hip joints, blend `hips` with the thighs, from 0 at
    the hips to `follow` at `full_at` of the way down to the hem; the leg share is split between both thighs across the centre line
    (linear over ±`centre_width`), so the front and back stretch between the legs instead of tearing.
    Returns the number of blended vertices."""
    hip_z = arm.data.bones["upperleg.l"].head_local.z
    co = [obj.matrix_world @ v.co for v in obj.data.vertices]
    hem_z = min(p.z for p in co)
    if hem_z >= hip_z - 0.05:
        return 0
    for b in ("hips", "upperleg.l", "upperleg.r"):
        if b not in obj.vertex_groups:
            obj.vertex_groups.new(name=b)
    groups = {g.name: g for g in obj.vertex_groups}
    n = 0
    for v, p in zip(obj.data.vertices, co):
        if p.z >= hip_z:
            continue
        leg = cfg["follow"] * min(1.0, (hip_z - p.z) / ((hip_z - hem_z) * cfg["full_at"]))
        if leg < 1e-3:
            continue
        a = min(1.0, max(0.0, 0.5 + p.x / (2 * cfg["centre_width"])))   # share of the left thigh
        for g in obj.vertex_groups:
            g.remove([v.index])
        for name, w in (("hips", 1.0 - leg), ("upperleg.l", leg * a), ("upperleg.r", leg * (1 - a))):
            if w > 1e-4:
                groups[name].add([v.index], w, "REPLACE")
        n += 1
    return n


def joint_blends(obj, arm, blends):
    """STYLE.md §9a: vertices on the body side of a joint go to the parent bone, blended linearly over
    `width` (so a sleeve's inner end stays in the robe and a boot shaft stays with the shin).
    Only vertices fully on the child bone are touched. Returns {joint: vertices changed}."""
    out = {}
    for b in blends:
        for side in ("l", "r"):
            child, parent = f"{b['bone']}.{side}", f"{b['parent']}.{side}" if b["parent"] != "chest" else "chest"
            if child not in obj.vertex_groups or parent not in arm.data.bones:
                continue
            head = arm.data.bones[child].head_local
            cg = obj.vertex_groups[child]
            pg = obj.vertex_groups.get(parent) or obj.vertex_groups.new(name=parent)
            n = 0
            for v in obj.data.vertices:
                ws = [g for g in v.groups if g.weight > 1e-4]
                if len(ws) != 1 or ws[0].group != cg.index:
                    continue
                p = obj.matrix_world @ v.co
                if b["axis"] == "out_x":
                    s = (abs(p.x) - abs(head.x)) if p.x * head.x > 0 else -abs(head.x)
                else:   # down_z
                    s = head.z - p.z
                if s >= 0:
                    continue
                w = max(0.0, 1.0 + s / b["width"])   # child weight: 1 at the joint, 0 at `width` inside
                cg.add([v.index], w, "REPLACE")
                pg.add([v.index], 1.0 - w, "REPLACE")
                if w == 0.0:
                    cg.remove([v.index])
                n += 1
            if n:
                out[child] = n
    return out


def run(args):
    style = S.load()
    spec = args["spec"]
    arch = spec.get("archetype", style["default_archetype"])
    tpl_rel = style["archetypes"][arch].get("template")
    if not tpl_rel:
        raise RuntimeError(f"archetype {arch!r} has no proportion template yet")
    props = {k: v for k, v in (spec.get("proportions") or {}).items() if abs(v - 1.0) > 1e-6}
    if props:
        raise RuntimeError(f"spec.proportions {props} not supported yet (Phase 4); parts are built "
                           "against the archetype template as-is")
    parts = {s: p for s, p in (spec.get("parts") or {}).items() if p}
    if not parts:
        raise RuntimeError("spec.parts is empty")

    SC.empty_scene()
    arm = R.append_skeleton()
    R.apply_template(arm, tpl_rel)
    part_bones = style["skeleton"]["part_bones"]
    upright = A.upright_slots(spec)   # grip `upright`: weighted to the slot bone, which then deforms (§9a)

    objs, per_part, skirt, blended = [], {}, {}, {}
    for slot, part in parts.items():
        pslot, _ = PT.split_part_name(part)
        if pslot != slot:
            raise RuntimeError(f"spec.parts.{slot} = {part!r} belongs to slot {pslot!r}")
        meta_path = PT.part_path(part, ".json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            if arch not in meta.get("archetypes", [arch]):
                raise RuntimeError(f"part {part!r} was built for {meta['archetypes']}, not {arch!r}")
        obj = PT.load_part(part)
        mesh = obj.data
        a = mesh.attributes.get("slot") or mesh.attributes.new("slot", "INT", "FACE")
        a.data.foreach_set("value", np.full(len(mesh.polygons), S.slot_index(slot), dtype=np.int32))
        if slot in upright:
            for g in list(obj.vertex_groups):
                obj.vertex_groups.remove(g)
            obj.vertex_groups.new(name=upright[slot]).add(list(range(len(mesh.vertices))), 1.0, "REPLACE")
            arm.data.bones[upright[slot]].use_deform = True
        else:
            PT.weight_nearest(obj, arm, part_bones[slot])
        blended.update(joint_blends(obj, arm, style["skinning"]["joint_blends"]))
        if slot == "torso" and not spec["parts"].get("legs"):
            skirt[part] = skirt_weights(obj, arm, style["skinning"]["skirt"])
        per_part[part] = sum(len(p.vertices) - 2 for p in mesh.polygons)
        objs.append(obj)

    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs,
                                   selected_objects=objs):
        bpy.ops.object.join()
    char = objs[0]
    char.name = char.data.name = style["skeleton"]["mesh_object"]
    # drop empty vertex groups left over from weight_nearest
    used = {g.group for v in char.data.vertices for g in v.groups if g.weight > 0}
    for g in [g for g in char.vertex_groups if g.index not in used]:
        char.vertex_groups.remove(g)

    SH.apply(char.data)
    used_idx, missing = PAL.apply_roles(char, spec.get("colors") or {})
    char.parent = arm
    mod = char.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    SC.save(args["out"])
    warnings = []
    if missing:
        warnings.append(f"roles without a colour in spec.colors: {missing} (validate will fail)")
    return {"outputs": [args["out"]], "warnings": warnings,
            "stats": {"tris": sum(per_part.values()), "part_tris": per_part, "palette_indices": used_idx, "skirt_verts": skirt, "joint_blend_verts": blended,
                      "missing_roles": missing}}
