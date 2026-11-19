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


def drop_animations(path, keep):
    """Keep only the animations named in `keep` (STYLE.md §10, a style's `export_clips`).
    Returns (dropped names, kept names missing from the file)."""
    gltf, binary = read(path)
    anims = gltf.get("animations", [])
    dropped = [a["name"] for a in anims if a["name"] not in keep]
    missing = sorted(set(keep) - {a["name"] for a in anims})
    if dropped:
        gltf["animations"] = [a for a in anims if a["name"] in keep]
        gltf, binary = _repack(gltf, binary)
        write(path, gltf, binary)
    return dropped, missing


_REST = {"rotation": [0.0, 0.0, 0.0, 1.0], "translation": [0.0, 0.0, 0.0], "scale": [1.0, 1.0, 1.0]}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _floats(gltf, binary, i):
    acc = gltf["accessors"][i]
    if acc["componentType"] != 5126:
        return None
    n = _WIDTH[acc["type"]]
    v = gltf["bufferViews"][acc["bufferView"]]
    off = v.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = v.get("byteStride", 4 * n)
    return [struct.unpack_from(f"<{n}f", binary, off + k * stride) for k in range(acc["count"])]


def _add_floats(gltf, binary, rows, kind, minmax=False):
    binary += b"\0" * (-len(binary) % 4)
    data = b"".join(struct.pack(f"<{len(r)}f", *r) for r in rows)
    gltf["bufferViews"].append({"buffer": 0, "byteOffset": len(binary), "byteLength": len(data)})
    acc = {"bufferView": len(gltf["bufferViews"]) - 1, "componentType": 5126, "count": len(rows), "type": kind}
    if minmax:
        acc["min"] = [min(c) for c in zip(*rows)]
        acc["max"] = [max(c) for c in zip(*rows)]
    gltf["accessors"].append(acc)
    return len(gltf["accessors"]) - 1, binary + data


def prune_static(path, tol=1e-5):
    """Lossless animation shrink (STYLE.md §10): (1) a node property that stays at the node's rest value in every
    animation loses its channel everywhere (nothing ever moves it); (2) any other channel that is constant over a
    clip keeps only its first and last key (same value, the clip keeps its length). Returns counts."""
    gltf, binary = read(path)
    nodes = gltf["nodes"]

    def close(a, b):
        return max(abs(x - y) for x, y in zip(a, b)) <= tol

    info, moving = {}, set()
    for ai, a in enumerate(gltf.get("animations", [])):
        for ci, c in enumerate(a["channels"]):
            s = a["samplers"][c["sampler"]]
            t = c["target"]
            pair = (t.get("node"), t["path"])
            out = _floats(gltf, binary, s["output"]) if s.get("interpolation", "LINEAR") != "CUBICSPLINE" else None
            if out is None or t["path"] not in _REST or t.get("node") is None:
                moving.add(pair)
                continue
            const = all(close(o, out[0]) for o in out)
            rest = nodes[t["node"]].get(t["path"], _REST[t["path"]])
            at_rest = const and (close(out[0], rest) or (t["path"] == "rotation" and close(out[0], [-x for x in rest])))
            info[(ai, ci)] = (const, out[0] if out else None)
            if not at_rest:
                moving.add(pair)
    removed = shortened = 0
    inputs = {}
    for ai, a in enumerate(gltf.get("animations", [])):
        chans, samplers = [], []
        for ci, c in enumerate(a["channels"]):
            t = c["target"]
            if (t.get("node"), t["path"]) not in moving:
                removed += 1
                continue
            s = dict(a["samplers"][c["sampler"]])
            const, first = info.get((ai, ci), (False, None))
            if const and gltf["accessors"][s["input"]]["count"] > 2:
                acc = gltf["accessors"][s["input"]]
                t0, t1 = acc["min"][0], acc["max"][0]
                if (t0, t1) not in inputs:
                    inputs[(t0, t1)], binary = _add_floats(gltf, binary, [(t0,), (t1,)], "SCALAR", minmax=True)
                s["input"] = inputs[(t0, t1)]
                s["output"], binary = _add_floats(gltf, binary, [first, first], gltf["accessors"][s["output"]]["type"])
                shortened += 1
            samplers.append(s)
            chans.append({**c, "sampler": len(samplers) - 1})
        a["channels"], a["samplers"] = chans, samplers
    if removed or shortened:
        gltf, binary = _repack(gltf, binary)
        write(path, gltf, binary)
    return {"channels_removed": removed, "channels_shortened": shortened}


def _add_bytes(gltf, binary, data, stride=None):
    binary += b"\0" * (-len(binary) % 4)
    view = {"buffer": 0, "byteOffset": len(binary), "byteLength": len(data), "target": 34962}
    if stride:
        view["byteStride"] = stride
    gltf["bufferViews"].append(view)
    return len(gltf["bufferViews"]) - 1, binary + data


def _weights_255(w):
    """Float weights -> bytes summing to exactly 255 (largest remainder)."""
    total = sum(w) or 1.0
    scaled = [x / total * 255 for x in w]
    q = [int(x) for x in scaled]
    for i in sorted(range(len(w)), key=lambda i: q[i] - scaled[i])[:255 - sum(q)]:
        q[i] += 1
    return q


def pack_vertices(path):
    """Core-glTF vertex packing for skinned meshes (STYLE.md §10, `export.pack_vertex_data`): WEIGHTS_0 and
    COLOR_0 as normalised unsigned bytes (COLOR_0 VEC3 with a 4-byte stride), TEXCOORD_0 as normalised unsigned
    shorts. No extension; three.js reads them as normalised attributes. Returns {attribute: bytes saved}."""
    gltf, binary = read(path)
    skinned = {n["mesh"] for n in gltf["nodes"] if "skin" in n and "mesh" in n}
    saved, done = {}, {}

    def repoint(i, comp, data, stride=None):
        nonlocal binary
        acc = gltf["accessors"][i]
        old = gltf["bufferViews"][acc["bufferView"]]["byteLength"]
        acc["bufferView"], binary = _add_bytes(gltf, binary, data, stride)
        acc.pop("byteOffset", None)
        acc["componentType"], acc["normalized"] = comp, True
        acc.pop("min", None)
        acc.pop("max", None)
        return old - len(data)

    for mi in sorted(skinned):
        for prim in gltf["meshes"][mi]["primitives"]:
            at = prim["attributes"]
            for name in ("WEIGHTS_0", "COLOR_0", "TEXCOORD_0"):
                i = at.get(name)
                if i is None or i in done:
                    continue
                rows = _floats(gltf, binary, i)
                if rows is None:      # already packed
                    continue
                if name == "WEIGHTS_0":
                    q = [_weights_255(r) for r in rows]
                    data = b"".join(struct.pack("<4B", *r) for r in q)
                    d = repoint(i, 5121, data)
                    j = at.get("JOINTS_0")
                    ja = gltf["accessors"][j] if j is not None else None
                    if ja is not None and ja["componentType"] in (5121, 5123):
                        # a weight that rounded to 0 must not name a joint (validator: JOINTS_USED_ZERO_WEIGHT)
                        fmt = "<4B" if ja["componentType"] == 5121 else "<4H"
                        v = gltf["bufferViews"][ja["bufferView"]]
                        st = v.get("byteStride", struct.calcsize(fmt))
                        off = v.get("byteOffset", 0) + ja.get("byteOffset", 0)
                        buf = bytearray(binary)
                        for k, r in enumerate(q):
                            jt = list(struct.unpack_from(fmt, buf, off + k * st))
                            nj = [0 if wq == 0 else x for wq, x in zip(r, jt)]
                            if nj != jt:
                                struct.pack_into(fmt, buf, off + k * st, *nj)
                        binary = bytes(buf)
                elif name == "COLOR_0":
                    if any(not 0.0 <= x <= 1.0 for r in rows for x in r):
                        continue
                    n = len(rows[0])
                    pad = b"\0" * (4 - n)
                    data = b"".join(struct.pack(f"<{n}B", *(round(x * 255) for x in r)) + pad for r in rows)
                    d = repoint(i, 5121, data, stride=4 if n == 3 else None)
                else:
                    if any(not 0.0 <= x <= 1.0 for r in rows for x in r):
                        continue      # outside 0..1 can't be a normalised short
                    data = b"".join(struct.pack("<2H", *(round(x * 65535) for x in r)) for r in rows)
                    d = repoint(i, 5123, data)
                done[i] = True
                saved[name] = saved.get(name, 0) + d
    if saved:
        gltf, binary = _repack(gltf, binary)
        write(path, gltf, binary)
    return saved


def nearest_samplers(path):
    """Samplers with a NEAREST magFilter get a plain NEAREST minFilter (9728): Blender writes
    NEAREST_MIPMAP_NEAREST (9984), which asks for mipmaps on a palette texture (STYLE.md §10).
    Returns the number of samplers changed."""
    gltf, binary = read(path)
    n = 0
    for s in gltf.get("samplers", []):
        if s.get("magFilter") == 9728 and s.get("minFilter") != 9728:
            s["minFilter"] = 9728
            n += 1
    if n:
        write(path, gltf, binary)
    return n
