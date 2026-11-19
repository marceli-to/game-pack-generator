"""Export shrink (STYLE.md §10): clips the style's game doesn't play are dropped, channels that never move are
left out, constant channels keep two keys, skinned vertex data is packed. Pure GLB edits, no Blender."""
import struct
import sys

from server.paths import REPO

sys.path.insert(0, str(REPO / "jobs"))
from lib import glb as G  # noqa: E402


def _glb(path):
    """Two nodes (b has a rest translation), three clips:
    walk: a rotates, a scale at rest, b translation at rest, b rotation constant (not rest, 3 keys)
    jump: a rotates, b translation at rest
    pose: b translation moves -> b translation must stay everywhere."""
    gltf = {"asset": {"version": "2.0"}, "nodes": [{"name": "a"}, {"name": "b", "translation": [0, 1, 0]}],
            "accessors": [], "bufferViews": [], "buffers": [], "animations": []}
    binary = b""
    t3, binary = G._add_floats(gltf, binary, [(0.0,), (0.5,), (1.0,)], "SCALAR", minmax=True)

    def ch(node, path, rows):
        nonlocal binary
        out, binary = G._add_floats(gltf, binary, rows, {3: "VEC3", 4: "VEC4"}[len(rows[0])])
        return node, path, out

    q0, q1 = (0, 0, 0, 1), (0, 0.7071, 0, 0.7071)
    clips = {
        "walk": [ch(0, "rotation", [q0, q1, q0]), ch(0, "scale", [(1, 1, 1)] * 3),
                 ch(1, "translation", [(0, 1, 0)] * 3), ch(1, "rotation", [q1] * 3)],
        "jump": [ch(0, "rotation", [q1, q0, q1]), ch(1, "translation", [(0, 1, 0)] * 3)],
        "pose": [ch(1, "translation", [(0, 1, 0), (0, 1.2, 0), (0, 1, 0)])],
    }
    for name, chans in clips.items():
        gltf["animations"].append({
            "name": name,
            "samplers": [{"input": t3, "output": o, "interpolation": "LINEAR"} for _, _, o in chans],
            "channels": [{"sampler": i, "target": {"node": n, "path": p}} for i, (n, p, _) in enumerate(chans)],
        })
    gltf["buffers"] = [{"byteLength": len(binary)}]
    G.write(path, gltf, binary)


def test_drop_and_prune(tmp_path):
    glb = tmp_path / "t.glb"
    _glb(glb)
    dropped, missing = G.drop_animations(glb, ["walk", "pose", "idle"])
    assert dropped == ["jump"] and missing == ["idle"]
    r = G.prune_static(glb)
    assert r == {"channels_removed": 1, "channels_shortened": 2}   # a scale gone; b rotation + translation 2 keys
    gltf, binary = G.read(glb)
    walk = {(c["target"]["node"], c["target"]["path"]): c for c in gltf["animations"][0]["channels"]}
    assert set(walk) == {(0, "rotation"), (1, "translation"), (1, "rotation")}   # b translation moves in pose
    s = gltf["animations"][0]["samplers"][walk[(1, "rotation")]["sampler"]]
    assert G._floats(gltf, binary, s["input"]) == [(0.0,), (1.0,)]
    assert [tuple(round(x, 4) for x in v) for v in G._floats(gltf, binary, s["output"])] == [(0, 0.7071, 0, 0.7071)] * 2
    assert gltf["buffers"][0]["byteLength"] == len(binary)
    assert struct.unpack_from("<I", glb.read_bytes(), 8)[0] == glb.stat().st_size


def test_pack_vertices(tmp_path):
    gltf = {"asset": {"version": "2.0"}, "nodes": [{"mesh": 0, "skin": 0}, {"mesh": 1}],
            "accessors": [], "bufferViews": [], "buffers": [], "skins": [{"joints": [0]}]}
    binary = b""
    w = [(0.5, 0.3, 0.2, 0.0), (1 / 3, 1 / 3, 1 / 3, 0.0), (0.9995, 0.0005, 0.0, 0.0)]
    c = [(0.2, 0.5, 1.0), (0.0, 0.66, 0.9), (1.0, 1.0, 1.0)]
    uv = [(0.0625, 0.9375), (0.5625, 0.1875), (1.0, 0.0)]
    acc = {}
    jd = struct.pack("<12B", 1, 2, 3, 0, 1, 2, 3, 0, 4, 5, 0, 0)
    gltf["bufferViews"].append({"buffer": 0, "byteOffset": 0, "byteLength": 12})
    gltf["accessors"].append({"bufferView": 0, "componentType": 5121, "count": 3, "type": "VEC4"})
    binary = jd
    acc["JOINTS_0"] = 0
    for name, rows, kind in (("WEIGHTS_0", w, "VEC4"), ("COLOR_0", c, "VEC3"), ("TEXCOORD_0", uv, "VEC2")):
        acc[name], binary = G._add_floats(gltf, binary, rows, kind)
    prop_uv, binary = G._add_floats(gltf, binary, uv, "VEC2")
    gltf["meshes"] = [{"primitives": [{"attributes": acc}]}, {"primitives": [{"attributes": {"TEXCOORD_0": prop_uv}}]}]
    gltf["buffers"] = [{"byteLength": len(binary)}]
    glb = tmp_path / "v.glb"
    G.write(glb, gltf, binary)
    saved = G.pack_vertices(glb)
    assert set(saved) == {"WEIGHTS_0", "COLOR_0", "TEXCOORD_0"} and all(v > 0 for v in saved.values())
    gltf, binary = G.read(glb)

    def rows(i, fmt, n, norm=True):
        a = gltf["accessors"][i]
        v = gltf["bufferViews"][a["bufferView"]]
        st = v.get("byteStride", struct.calcsize(fmt))
        assert a.get("normalized", False) is norm
        return [struct.unpack_from(fmt, binary, v["byteOffset"] + k * st)[:n] for k in range(a["count"])]

    at = gltf["meshes"][0]["primitives"][0]["attributes"]
    ws = rows(at["WEIGHTS_0"], "<4B", 4)
    assert all(sum(r) == 255 for r in ws) and ws[2] == (255, 0, 0, 0)
    assert rows(at["JOINTS_0"], "<4B", 4, norm=False)[2] == (4, 0, 0, 0)   # joint 5 had weight 0.0005 -> 0
    assert all(abs(x - y / 255) <= 1 / 510 + 1e-9 for r, q in zip(w, ws) for x, y in zip(r, q))
    assert gltf["bufferViews"][gltf["accessors"][at["COLOR_0"]]["bufferView"]]["byteStride"] == 4
    assert all(abs(x - y / 255) <= 1 / 510 for r, q in zip(c, rows(at["COLOR_0"], "<3B", 3)) for x, y in zip(r, q))
    assert all(abs(x - y / 65535) < 1e-5 for r, q in zip(uv, rows(at["TEXCOORD_0"], "<2H", 2)) for x, y in zip(r, q))
    prop = gltf["accessors"][gltf["meshes"][1]["primitives"][0]["attributes"]["TEXCOORD_0"]]
    assert prop["componentType"] == 5126   # not skinned: left as floats
