"""Assemble a character from parts (STYLE.md §9a).

args: { spec: {...}, out: <character.blend> }
Template -> standard skeleton -> parts appended -> `slot` attribute -> rigid weights (nearest allowed
bone) -> joined into `Character`, parented to `Armature` -> palette applied from spec.colors.
"""
import json

import bpy
import numpy as np

from lib import palette as PAL
from lib import parts as PT
from lib import rig as R
from lib import scene as SC
from lib import shading as SH
from lib import style as S


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

    objs, per_part = [], {}
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
        PT.weight_nearest(obj, arm, part_bones[slot])
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
            "stats": {"tris": sum(per_part.values()), "part_tris": per_part, "palette_indices": used_idx,
                      "missing_roles": missing}}
