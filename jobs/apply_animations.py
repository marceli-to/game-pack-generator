"""Add the library clips to an assembled character (STYLE.md §7a, §8, §9a).

args: { spec: {...}, out: <character.blend> }
Appends the §8 clips (+ the §8b extra clips in spec.extra_clips, arms-only ones baked) from library/animations.blend (replacing earlier copies), scales their location keys
by the template's offset factors, binds them to the armature and bakes upright grips (spec.grip).
"""
import bpy

from lib import anim as A
from lib import scene as SC
from lib import style as S


def run(args):
    spec = args["spec"]
    style = S.load()
    arm = SC.main_armature()
    if arm is None or bpy.data.objects.get(style["skeleton"]["mesh_object"]) is None:
        raise RuntimeError("no assembled character (Armature + Character); run assemble_from_parts first")
    acts = A.add_clips(arm, spec)
    char = bpy.data.objects[style["skeleton"]["mesh_object"]]
    body = A.body_vertices(char)
    # arms-only clips (§8b) leave the hips to the clip they are layered over
    lifts = {a.name: round(A.floor_clamp(arm, char, a, body), 4) for a in acts
             if not A.is_arms_only(a.name)} if body else {}
    upright = A.upright_slots(spec)
    leans = {}
    for slot, bone in upright.items():
        if not arm.data.bones[bone].use_deform:
            raise RuntimeError(f"{slot} is held upright but {bone} does not deform; re-run assemble_from_parts")
        clear = A.Clearance(arm, char, slot, bone, style["skinning"]["upright_clearance"])
        for a in acts:
            # e.g. die: upright at the start, then held, so the staff falls with the character
            lean = A.bake_upright(arm, a, bone, held=a.name in style["skinning"]["upright_held_clips"],
                                  clearance=clear)
            if lean:
                leans.setdefault(a.name, {})[slot] = round(lean, 1)
    idle = next((a for a in acts if a.name == "idle"), acts[0])
    SC.assign_action(arm, idle)
    arm.data.pose_position = "POSE"
    bpy.context.scene.frame_set(0)
    SC.save(args["out"])
    clips = {a.name: {"frames": int(round(a.frame_range[1] - a.frame_range[0])),
                      **({"arms_only": a["arms_only_report"].to_dict()} if "arms_only_report" in a else {})}
             for a in acts}
    return {"outputs": [args["out"]], "stats": {"clips": clips, "upright": upright, "floor_lift_m": lifts, "upright_lean_deg": leans}}
