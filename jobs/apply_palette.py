"""Re-resolve every face's role -> spec.colors -> palette UV (STYLE.md §4).

args: { colors: {role: palette_index}, out: <character.blend> }
"""
from lib import palette as PAL
from lib import scene as SC
from lib import style as S


def run(args):
    import bpy
    name = S.load()["skeleton"]["mesh_object"]
    obj = bpy.context.scene.objects.get(name)
    if obj is None:
        raise RuntimeError(f"no mesh object {name!r}; run assemble_from_parts first")
    used, missing = PAL.apply_roles(obj, args["colors"])
    SC.save(args["out"])
    warnings = [f"roles without a colour: {missing}"] if missing else []
    return {"outputs": [args["out"]], "warnings": warnings,
            "stats": {"palette_indices": used, "colours_used": len(used), "missing_roles": missing}}
