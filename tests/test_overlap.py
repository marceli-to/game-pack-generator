"""Overlap checks (jobs/lib/overlap.py): covered features (`validate`, STYLE.md §12) and their docs."""
import json
import subprocess
import textwrap

from server.paths import JOBS, REPO, blender_bin
from server.style import load_style

from .conftest import needs_blender

SCRIPT = textwrap.dedent('''
    import sys, json, math
    sys.path.insert(0, {jobs!r})
    import bpy
    from mathutils import Vector
    from lib import parts as PT, overlap as O, style as S, measure as M, scene as SC
    st = S.load()
    slots = st["slots"]
    out = {{}}
    for name, ear_out in (("inside", 0.22), ("through", 0.29)):
        SC.empty_scene()
        objs = []
        for slot, build in (("head", "head"), ("headwear", "helmet")):
            B = PT.PartBuilder()
            if build == "head":
                lat = [-70, -40, -10, 20, 50, 75]
                B.loft([[Vector((0, 0, 0.81))]] + [B.ring((0, 0, 1.0 + 0.19 * math.sin(math.radians(a))),
                        0.19 * math.cos(math.radians(a)), n=10) for a in lat] + [[Vector((0, 0, 1.19))]], "skin")
                for s in (1, -1):
                    lo, hi = sorted((s * 0.17, s * ear_out))
                    B.box((lo, -0.03, 0.95), (hi, 0.03, 1.02), "skin")
            else:   # a closed dome over the head and ears, down to z 0.88
                B.loft([B.ring((0, 0, 0.88), 0.25, n=12), B.ring((0, 0, 1.1), 0.25, n=12),
                        B.ring((0, 0, 1.25), 0.17, n=12), [Vector((0, 0, 1.3))]], "metal")
            obj, _ = B.to_object(slot)
            a = obj.data.attributes.new("slot", "INT", "FACE")
            a.data.foreach_set("value", [slots.index(slot)] * len(obj.data.polygons))
            objs.append(obj)
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        char = bpy.context.view_layer.objects.active
        sf = M._int_face_attr(char.data, "slot")
        out[name] = O.covered_visible(char, {{"ears": ["headwear-test"]}}, sf, slots, st["covers_check"])
    print("RESULT" + json.dumps(out))
''')


@needs_blender
def test_covered_ears(tmp_path):
    """Ears under a helmet that covers them: no finding; ears sticking out through it: found."""
    p = tmp_path / "covers.py"
    p.write_text(SCRIPT.format(jobs=str(JOBS)))
    r = subprocess.run([blender_bin(), "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(p)],
                       capture_output=True, text=True, timeout=120, env={"GPG_STYLE": "lowpoly", "PATH": ""})
    line = [x for x in r.stdout.splitlines() if x.startswith("RESULT")]
    assert line, (r.stdout + r.stderr)[-2000:]
    res = json.loads(line[0][6:])
    assert res["inside"] == {}, res
    assert res["through"]["ears"]["verts"] >= load_style()["covers_check"]["min_verts"], res
    assert res["through"]["ears"]["by"] == ["headwear-test"]


def test_overlap_values_documented():
    md = (REPO / "STYLE.md").read_text()
    style = load_style()
    pt, cc = style["pose_test"], style["covers_check"]
    assert f"`visible_cone_deg` = {pt['visible_cone_deg']}°" in md
    assert f"`visible_tolerance` = {round(pt['visible_tolerance'] * 100)} cm" in md
    assert f"`covers_check.min_verts` = {cc['min_verts']}" in md
    assert f"`covers_check.cone_deg` = {cc['cone_deg']}°" in md
    assert all(f"`{f}`" in md for f in style["part_covers"] if not f.startswith("_"))


def test_clip_offsets_documented():
    """Every per-clip correction in a style is described in its STYLE.md (clip, bone, angle)."""
    for name in ("lowpoly",):
        style = load_style(name)
        md = (REPO / "styles" / name / "STYLE.md").read_text()
        for arch, a in style["archetypes"].items():
            for clip, bones in a.get("clip_offsets", {}).items():
                for bone, (axis, deg) in bones.items():
                    assert f"`{arch}` turns `{bone}` by {deg}° about its local {axis} axis in `{clip}`" in md
