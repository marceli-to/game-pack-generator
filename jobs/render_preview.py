"""Turnaround sheet of the open .blend (STYLE.md §11).

args: { out_dir, views?: [..], pose?: "rest" | "<action name>@<frame>", size?: px,
        frame?: {center: [x, y, z], extent: m} }
"""
import bpy

from lib import render as RD
from lib import scene as SC


def run(args):
    arm = SC.main_armature()
    pose = args.get("pose", "rest")
    if arm is not None:
        if pose == "rest":
            arm.data.pose_position = "REST"
        else:
            name, _, frame = pose.partition("@")
            act = bpy.data.actions.get(name)
            if act is None:
                raise RuntimeError(f"no action {name!r}")
            arm.data.pose_position = "POSE"
            SC.assign_action(arm, act)
            bpy.context.scene.frame_set(int(frame or 0))
    bpy.context.view_layer.update()
    views, sheet = RD.render_views(args["out_dir"], args.get("views"), size=args.get("size"), frame=args.get("frame"))
    return {"outputs": [sheet], "previews": [sheet] + views}
