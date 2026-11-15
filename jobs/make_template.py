"""Compute a proportion template from the skeleton + archetype targets (STYLE.md §7a).

args: { archetype: "human", out?: the archetype's template path in the style }
Writes the full rest layout (bone head/tail/roll), landmarks, segment factors and the
per-bone offset factors used to scale clip location keys.
"""
import json

from lib import rig as R
from lib import scene as SC
from lib import style as S


def _r(v):
    return [round(x, 4) for x in v]


def run(args):
    style = S.load()
    arch = args.get("archetype", style["default_archetype"])
    targets = {k: v for k, v in style["archetypes"][arch]["targets"].items() if not k.startswith("_")}
    targets.update(args.get("targets", {}))  # overrides for trying variants
    SC.empty_scene()
    arm = R.append_skeleton()
    src = R.rest_layout(arm)
    layout, factors, off = R.compute_layout(src, targets)
    L = {n: (h, t) for n, (h, t, _) in layout.items()}
    landmarks = {
        "hips": _r(L["hips"][0]), "hip.l": _r(L["upperleg.l"][0]), "hip.r": _r(L["upperleg.r"][0]),
        "head_base": _r(L["head"][0]), "head_top": _r(L["head"][1]),
        "shoulder.l": _r(L["upperarm.l"][0]), "shoulder.r": _r(L["upperarm.r"][0]),
        "elbow.l": _r(L["lowerarm.l"][0]), "elbow.r": _r(L["lowerarm.r"][0]),
        "wrist.l": _r(L["hand.l"][0]), "wrist.r": _r(L["hand.r"][0]),
        "knee.l": _r(L["lowerleg.l"][0]), "knee.r": _r(L["lowerleg.r"][0]),
        "ankle.l": _r(L["foot.l"][0]), "ankle.r": _r(L["foot.r"][0]),
        "toes.l": _r(L["toes.l"][1]), "toes.r": _r(L["toes.r"][1]),
        "headslot": _r(L["headslot"][0]), "backslot": _r(L["backslot"][0]),
        "handslot.l": _r(L["handslot.l"][0]), "handslot.r": _r(L["handslot.r"][0]),
    }
    data = {
        "archetype": arch,
        "source_rig": style["skeleton"]["source"],
        "targets": targets,
        # Guide sizes for the main volumes (used by the mannequin and as a reference for parts).
        "guides": {k: targets[k] for k in ("head_width", "head_depth", "torso_width", "torso_depth",
                                                 "foot_width", "foot_height", "foot_heel")
                   if k in targets},
        "body_height": round(targets["head_top_z"], 4),
        "factors": {k: round(v, 4) for k, v in factors.items()},
        "offset_factors": {k: round(v, 4) for k, v in off.items()},
        "landmarks": landmarks,
        "bones": {n: {"head": _r(h), "tail": _r(t), "roll": round(r, 6)} for n, (h, t, r) in layout.items()},
    }
    out = S.repo_path(args.get("out", style["archetypes"][arch]["template"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1) + "\n")
    return {"outputs": [str(out)], "stats": {"factors": data["factors"], "body_height": data["body_height"]}}
