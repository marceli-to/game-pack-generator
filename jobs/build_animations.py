"""Build library/animations.blend from the KayKit clips mapped in core.json (STYLE.md §8, §8b).

args: { source_dir: <KayKit_Character_Animations_1.1>, out: "library/animations.blend" }
Clips keep their source length (imported at the style fps). Scale keys and root-bone
location keys (root motion) are stripped. Actions are renamed to the STYLE.md §8 names.
Extra clips (§8b) are cut to `range` (source frames, shifted to start at 0) or hold one source frame
(`hold`) for `frames`; their arms-only bake happens per character (apply_animations).
"""
from pathlib import Path

import bpy

from lib import scene as SC
from lib import style as S


def _range(fc):
    vals = [k.co[1] for k in fc.keyframe_points]
    return (max(vals) - min(vals)) if vals else 0.0


def resample(action, frames, length=None):
    """Replace every curve's keys by its values at the given source frames, keyed at 0, 1, 2, ...
    (or, with `length`, one value held from 0 to `length`)."""
    for fc in SC.action_fcurves(action):
        vals = [fc.evaluate(f) for f in frames]
        fc.keyframe_points.clear()
        if length is not None:
            keys = [(0, vals[0]), (length, vals[0])]
        else:
            keys = list(enumerate(vals))
        fc.keyframe_points.add(len(keys))
        for k, (f, v) in zip(fc.keyframe_points, keys):
            k.co = (f, v)
            k.interpolation = "LINEAR"
        fc.update()


def run(args):
    style = S.load()
    anim = style["animations"]
    clips = anim["clips"] + anim.get("extra_clips", [])
    src_dir = Path(args["source_dir"]) / "Animations" / "gltf" / "Rig_Medium"
    SC.empty_scene()
    keep = {}
    for f in sorted({c["file"] for c in clips}):
        before = set(bpy.data.actions)
        SC.import_glb(src_dir / f)
        new = {a.name: a for a in bpy.data.actions if a not in before}
        for c in clips:
            if c["file"] == f:
                if c["source"] not in new:
                    raise RuntimeError(f"clip {c['source']} not found in {f}; have {sorted(new)}")
                src = new[c["source"]]
                # two library clips may share one source (crouch, crouch_walk)
                keep[c["name"]] = src.copy() if any(v is src for v in keep.values()) or "range" in c or "hold" in c else src
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        if a not in keep.values():
            bpy.data.actions.remove(a)

    report = {}
    warnings = []
    by_name = {c["name"]: c for c in clips}
    for name, act in keep.items():
        act.name = name
        c = by_name[name]
        scale = SC.remove_fcurves(act, lambda fc: fc.data_path.endswith("scale"))
        def is_root_loc(fc):
            return SC.bone_of(fc.data_path) == "root" and fc.data_path.endswith("location")
        moving = [fc for fc in SC.action_fcurves(act) if is_root_loc(fc) and _range(fc) > 1e-4]
        SC.remove_fcurves(act, is_root_loc)
        if moving:
            warnings.append(f"{name}: stripped {len(moving)} moving root-location curves (root motion)")
        if "hold" in c:
            resample(act, [c["hold"]], length=c["frames"])
        elif "range" in c:
            a, b = c["range"]
            resample(act, list(range(a, b + 1)))
        act.use_fake_user = True
        f0, f1 = act.frame_range
        loc_bones = sorted({SC.bone_of(fc.data_path) for fc in SC.action_fcurves(act)
                            if fc.data_path.endswith("location") and SC.bone_of(fc.data_path) and _range(fc) > 1e-4})
        report[name] = {"frames": int(round(f1 - f0)), "frame_start": int(round(f0)),
                        "stripped_scale_curves": scale, "location_keyed_bones": loc_bones}
    out = S.repo_path(args.get("out", "library/animations.blend"))
    SC.save(out)
    return {"outputs": [str(out)], "stats": {"clips": len(report)}, "clips": report, "warnings": warnings}
