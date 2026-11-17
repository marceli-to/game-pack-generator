"""Part overlaps on the assembled character (STYLE.md §8a, §12): closed shells, inside tests, crossing points and
whether anyone can see them.

Everything works on plain vertex coordinates (numpy, world space), so the same code checks the rest pose
(`validate`) and posed frames (`pose_test`)."""
import math
from collections import defaultdict

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

RAY = Vector((0.31, 0.17, 0.93)).normalized()   # parity ray, skewed so it rarely grazes edges


def view_dirs(n_around=12, elevations=(10, 30, 50, 75)):
    """Directions a viewer can look from (towards the viewer): rings around the body from just above the horizon
    to steep top-down, plus straight above. Not from below: looking up under a hem every boot "enters" the skirt's
    underside, which no game camera shows."""
    out = [Vector((0, 0, 1))]
    for e in elevations:
        ce, se = math.cos(math.radians(e)), math.sin(math.radians(e))
        for k in range(n_around):
            a = 2 * math.pi * (k + 0.5 * (e > 30)) / n_around
            out.append(Vector((ce * math.cos(a), ce * math.sin(a), se)))
    return out


def islands(mesh):
    """Connected face islands -> list of polygon index lists (union-find over shared vertices)."""
    parent = list(range(len(mesh.vertices)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for p in mesh.polygons:
        vs = p.vertices
        for a in vs[1:]:
            ra, rb = find(vs[0]), find(a)
            if ra != rb:
                parent[ra] = rb
    groups = defaultdict(list)
    for p in mesh.polygons:
        groups[find(p.vertices[0])].append(p.index)
    return list(groups.values())


def coords(obj):
    """Evaluated (posed) vertex coordinates of `obj` in world space."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    m = ev.to_mesh()
    co = np.empty(len(m.vertices) * 3, dtype=np.float64)
    m.vertices.foreach_get("co", co)
    ev.to_mesh_clear()
    co = co.reshape(-1, 3)
    mw = np.array(obj.matrix_world)
    return co @ mw[:3, :3].T + mw[:3, 3]


def rest_coords(obj):
    """Undeformed vertex coordinates in world space (the rest pose, whatever the armature plays)."""
    m = obj.data
    co = np.empty(len(m.vertices) * 3, dtype=np.float64)
    m.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    mw = np.array(obj.matrix_world)
    return co @ mw[:3, :3].T + mw[:3, 3]


def vertex_slots(mesh, slot_face):
    vslot = np.full(len(mesh.vertices), -1, dtype=np.int32)
    for p in mesh.polygons:
        for v in p.vertices:
            vslot[v] = slot_face[p.index]
    return vslot


class Shells:
    """Closed shells (connected islands) of the character with their slot, for inside tests and crossings."""

    def __init__(self, mesh, slot_face):
        self.polys = [list(p.vertices) for p in mesh.polygons]
        self.islands = []
        for faces in islands(mesh):
            verts = sorted({v for f in faces for v in self.polys[f]})
            remap = {v: i for i, v in enumerate(verts)}
            self.islands.append({
                "slot": int(slot_face[faces[0]]),
                "verts": np.array(verts),
                "polys": [[remap[v] for v in self.polys[f]] for f in faces],
            })
        self.island_of = np.full(len(mesh.vertices), -1, dtype=np.int32)
        for k, isl in enumerate(self.islands):
            self.island_of[isl["verts"]] = k
        nbr = defaultdict(set)
        for e in mesh.edges:
            a, b = e.vertices
            nbr[a].add(b)
            nbr[b].add(a)
        self.neighbours = nbr
        self._bvh = {}
        self._co_id = None

    def bvh(self, co, k):
        """BVH of island k at the coordinates `co` (cached per coordinate array)."""
        if self._co_id is not id(co):
            self._bvh, self._co_id = {}, id(co)
        if k not in self._bvh:
            isl = self.islands[k]
            self._bvh[k] = BVHTree.FromPolygons([Vector(p) for p in co[isl["verts"]]], isl["polys"])
        return self._bvh[k]

    def inside(self, co, vert_slot, skip_same_slot=True, tol=0.0):
        """{(vertex, island): depth} for vertices inside a shell of another slot, deeper than `tol`."""
        out = {}
        for k, isl in enumerate(self.islands):
            pts = co[isl["verts"]]
            lo, hi = pts.min(axis=0), pts.max(axis=0)
            cand = np.nonzero(np.all((co > lo) & (co < hi), axis=1))[0]
            cand = cand[vert_slot[cand] != isl["slot"]] if skip_same_slot else cand
            if not len(cand):
                continue
            bvh = self.bvh(co, k)
            for v in cand:
                if is_inside(bvh, Vector(co[v])):
                    depth = bvh.find_nearest(Vector(co[v]))[3]
                    if depth > tol:
                        out[(int(v), k)] = depth
        return out

    def crossings(self, co, inside_keys, verts, k):
        """[(point, inside vertex)] where edges from `verts` (inside island k) to neighbours outside it cross
        island k's surface."""
        bvh = self.bvh(co, k)
        pts = []
        for v in verts:
            pv = Vector(co[v])
            for w in self.neighbours[v]:
                if (w, k) in inside_keys or self.island_of[w] == k:
                    continue
                pw = Vector(co[w])
                d = pv - pw
                L = d.length
                if L < 1e-7:
                    continue
                hit = bvh.ray_cast(pw, d / L, L)[0]
                if hit is not None:
                    pts.append((hit, v))
        return pts


def is_inside(bvh, p, ray=RAY):
    hits, o = 0, p
    for _ in range(64):
        loc = bvh.ray_cast(o, ray)[0]
        if loc is None:
            break
        hits += 1
        o = loc + ray * 1e-5
    return bool(hits % 2)


def scene_bvh(co, polys):
    return BVHTree.FromPolygons([Vector(p) for p in co], polys)


def _cone(d, spread_deg):
    """`d` and four directions `spread_deg` around it."""
    if spread_deg <= 0:
        return [d]
    u = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
    w = d.cross(u)
    c, s = math.cos(math.radians(spread_deg)), math.sin(math.radians(spread_deg))
    return [d] + [(d * c + e * s).normalized() for e in (u, -u, w, -w)]


def visible(bvh, p, dirs, offset=0.003, spread_deg=0.0):
    """True if `p` can be seen from any of `dirs` (nothing in the way, apart from what lies within `offset`).
    With `spread_deg`, a direction counts only if a cone of rays that wide around it gets out too: a slit a few
    millimetres wide between two parts does not make what lies behind it visible."""
    for d in dirs:
        if all(bvh.ray_cast(p + e * offset, e)[0] is None for e in _cone(d, spread_deg)):
            return True
    return False


def spec_covers(spec):
    """{feature: [parts of the spec that declare they cover it]} from the parts' .json (`covers`)."""
    import json
    from . import parts as PT
    by = defaultdict(list)
    for part in (spec.get("parts") or {}).values():
        if not part:
            continue
        mp = PT.part_path(part, ".json")
        if mp.exists():
            for c in json.loads(mp.read_text()).get("covers", []):
                by[c].append(part)
    return dict(by)


def covered_visible(obj, by, slot_face, slots, cfg, co=None):
    """Features that parts declare they hide (`by` = {feature: [parts]}, from `P.covers`, core.json
    `part_covers`) but that a viewer can still see in the rest pose (STYLE.md §12). `ears`: the head's islands
    out at the sides. `cfg` = core.json `covers_check` (cone width, minimum vertex count); `co` overrides the
    rest coordinates.
    Returns {feature: {"by": [parts], "verts": visible, "of": total, "at": xyz of one visible vertex}}."""
    if not by or "head" not in slots:
        return {}
    mesh = obj.data
    co = rest_coords(obj) if co is None else co
    shells = Shells(mesh, slot_face)
    allb = scene_bvh(co, shells.polys)
    dirs = view_dirs()
    out = {}
    if "ears" in by:
        hs = slots.index("head")
        heads = sorted((k for k, isl in enumerate(shells.islands) if isl["slot"] == hs),
                       key=lambda k: -len(shells.islands[k]["verts"]))
        # ears: the head's islands out at the sides (centre beyond 70 % of the skull's half-width), not the eyes,
        # brows or mouth on the face
        half = float(np.abs(co[shells.islands[heads[0]]["verts"], 0]).max()) if heads else 0.0
        side = [k for k in heads[1:] if abs(float(co[shells.islands[k]["verts"], 0].mean())) > 0.7 * half]
        ears = np.concatenate([shells.islands[k]["verts"] for k in side]) if side else []
        seen = [int(v) for v in ears if visible(allb, Vector(co[v]), dirs, spread_deg=cfg["cone_deg"])]
        if len(seen) >= cfg["min_verts"]:
            out["ears"] = {"by": by["ears"], "verts": len(seen), "of": len(ears),
                           "at": [round(float(x), 3) for x in co[seen[0]]]}
    return out
