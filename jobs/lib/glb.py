"""Small GLB edits after Blender's exporter (no bpy): drop animation channels, repack the binary chunk."""
import json
import struct
from pathlib import Path

PATHS = {"rotation_quaternion": "rotation", "location": "translation", "scale": "scale"}


def read(path):
    b = Path(path).read_bytes()
    magic, version, _ = struct.unpack_from("<III", b, 0)
    if magic != 0x46546C67 or version != 2:
        raise ValueError(f"{path} is not a glTF 2.0 binary")
    off, gltf, binary = 12, None, b""
    while off < len(b):
        n, kind = struct.unpack_from("<II", b, off)
        chunk = b[off + 8:off + 8 + n]
        if kind == 0x4E4F534A:
            gltf = json.loads(chunk)
        elif kind == 0x004E4942:
            binary = chunk
        off += 8 + n
    return gltf, binary


def write(path, gltf, binary):
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    binary += b"\0" * (-len(binary) % 4)
    chunks = struct.pack("<II", len(js), 0x4E4F534A) + js
    if binary:
        chunks += struct.pack("<II", len(binary), 0x004E4942) + binary
    Path(path).write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(chunks)) + chunks)


def _repack(gltf, binary):
    """Remove accessors and buffer views nothing references any more; rebuild the binary chunk."""
    used = set()
    for m in gltf.get("meshes", []):
        for p in m["primitives"]:
            used.update(p.get("attributes", {}).values())
            if "indices" in p:
                used.add(p["indices"])
            for t in p.get("targets", []):
                used.update(t.values())
    for s in gltf.get("skins", []):
        if "inverseBindMatrices" in s:
            used.add(s["inverseBindMatrices"])
    for a in gltf.get("animations", []):
        for s in a["samplers"]:
            used.update((s["input"], s["output"]))
    acc_map = {}
    accessors = []
    for i, acc in enumerate(gltf.get("accessors", [])):
        if i in used:
            acc_map[i] = len(accessors)
            accessors.append(acc)
    views_used = {a["bufferView"] for a in accessors if "bufferView" in a}
    views_used |= {im["bufferView"] for im in gltf.get("images", []) if "bufferView" in im}
    view_map, views, out = {}, [], bytearray()
    for i, v in enumerate(gltf.get("bufferViews", [])):
        if i not in views_used:
            continue
        out += b"\0" * (-len(out) % 4)
        data = binary[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]]
        v = {**v, "byteOffset": len(out), "buffer": 0}
        out += data
        view_map[i] = len(views)
        views.append(v)
    for acc in accessors:
        if "bufferView" in acc:
            acc["bufferView"] = view_map[acc["bufferView"]]
    for im in gltf.get("images", []):
        if "bufferView" in im:
            im["bufferView"] = view_map[im["bufferView"]]
    for m in gltf.get("meshes", []):
        for p in m["primitives"]:
            p["attributes"] = {k: acc_map[v] for k, v in p.get("attributes", {}).items()}
            if "indices" in p:
                p["indices"] = acc_map[p["indices"]]
            p["targets"] = [{k: acc_map[v] for k, v in t.items()} for t in p.get("targets", [])] or p.pop("targets", None)
            if p.get("targets") is None:
                p.pop("targets", None)
    for s in gltf.get("skins", []):
        if "inverseBindMatrices" in s:
            s["inverseBindMatrices"] = acc_map[s["inverseBindMatrices"]]
    for a in gltf.get("animations", []):
        for s in a["samplers"]:
            s["input"], s["output"] = acc_map[s["input"]], acc_map[s["output"]]
    gltf["accessors"], gltf["bufferViews"] = accessors, views
    out += b"\0" * (-len(out) % 4)
    gltf["buffers"] = [{"byteLength": len(out)}]
    return gltf, bytes(out)


def keep_channels(path, keep):
    """keep = {animation name: {node name: {glTF paths}}}: in those animations, drop every other channel.
    Returns {animation: channels removed}."""
    gltf, binary = read(path)
    names = [n.get("name") for n in gltf["nodes"]]
    removed = {}
    for a in gltf.get("animations", []):
        if a["name"] not in keep:
            continue
        k = keep[a["name"]]
        chans = [c for c in a["channels"] if c["target"]["path"] in k.get(names[c["target"]["node"]], ())]
        removed[a["name"]] = len(a["channels"]) - len(chans)
        smap, samplers = {}, []
        for c in chans:
            if c["sampler"] not in smap:
                smap[c["sampler"]] = len(samplers)
                samplers.append(a["samplers"][c["sampler"]])
            c["sampler"] = smap[c["sampler"]]
        a["channels"], a["samplers"] = chans, samplers
    gltf, binary = _repack(gltf, binary)
    write(path, gltf, binary)
    return removed
