"""Parts: the builder API for agent-written part scripts, part checks, and loading parts.

A part is one mesh object `part_<slot>` in <style parts dir>/<slot>/<part>.blend, modelled in the
world space of a proportion template (STYLE.md §7a), with a FACE INT attribute `role` on every
face and optional rigid bone weights (vertex groups named after deforming bones).

Part scripts run with these names in scope (see `script_namespace`):
    P        PartBuilder (primitives below; P.bm is the raw bmesh)
    lm       template landmarks {name: Vector} (hip.l, shoulder.l, wrist.l, ankle.l, head_top, ...)
    bones    template rest bones {name: (head Vector, tail Vector)}
    guides   template volume guides {head_width, torso_width, foot_width, ...}
    tpl      the whole template dict
    Vector, Matrix, math, bmesh, bpy
"""
import math
from collections import defaultdict

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

from . import style as S



def split_part_name(part):
    """'accessory_hand_r-staff-crystal' -> ('accessory_hand_r', 'staff-crystal')."""
    slots = sorted(S.load()["slots"], key=len, reverse=True)
    for s in slots:
        if part.startswith(s + "-") and len(part) > len(s) + 1:
            return s, part[len(s) + 1:]
    raise ValueError(f"part name {part!r} must be '<slot>-<variant>' with slot in {S.load()['slots']}")


def part_path(part, ext=".blend"):
    slot, _ = split_part_name(part)
    return S.repo_path(f"{S.load()['parts']['dir']}/{slot}/{part}{ext}")


def mirror_bone(name):
    if name.endswith(".l"):
        return name[:-2] + ".r"
    if name.endswith(".r"):
        return name[:-2] + ".l"
    return name


class PartBuilder:
    """Primitives for low-poly parts. Every primitive takes a role name and an optional bone
    (rigid weight 1.0); vertices without a bone get the nearest allowed bone at assembly."""

    def __init__(self):
        self.bm = bmesh.new()
        self.role_layer = self.bm.faces.layers.int.new("role")
        self._set = self.bm.faces.layers.int.new("_role_set")
        self.deform = self.bm.verts.layers.deform.verify()
        self.groups = {}
        self.covers = []   # features of other parts this part hides (core.json `part_covers`), e.g. ["ears"]
        self.skirt = {}    # torso parts: overrides of core.json skinning.skirt (STYLE.md §9a), e.g. {"follow": 0.8}
        self.anchors = {}  # props (STYLE.md §9b): named points exported as empties, e.g. grip, muzzle
        self.pieces = {}   # props: {piece: parent anchor or None}; faces carry `piece` (0 = the main mesh)
        self._piece = None
        self.anchor_pieces = {}  # {anchor: piece} for anchors that move with a piece

    def piece(self, name, parent=None):
        """Props (STYLE.md §9b): faces built from here on belong to the separate mesh `name` (None: back to
        the main mesh); exported as its own glTF node, a child of the anchor `parent` when given (a board
        turning about its `hinge`)."""
        if not self.pieces and name is not None:
            self.pieces[str(name)] = parent   # register first, so faces built before stay the main mesh (0)
            self._close_piece()
        self._close_piece()
        if name is not None:
            self.pieces[str(name)] = parent
            self._piece = str(name)
        else:
            self._piece = None

    def _close_piece(self):
        """Give the faces built since the last piece() call the current piece's index (1-based)."""
        if not self.pieces:
            return
        if "piece" not in self.bm.faces.layers.int:
            self.bm.faces.layers.int.new("piece")
        lay = self.bm.faces.layers.int["piece"]
        idx = 0 if self._piece is None else list(self.pieces).index(self._piece) + 1
        tag = self.bm.faces.layers.int.get("_piece_done") or self.bm.faces.layers.int.new("_piece_done")
        for f in self.bm.faces:
            if not f[tag]:
                f[tag] = 1
                f[lay] = idx

    def anchor(self, name, point, piece=None):
        """Name a point of a prop (STYLE.md §9b: `grip`, `muzzle`); exported as an empty glTF node. With
        `piece`, the node is a child of that piece and moves with it (`board_centre` on a tipping board)."""
        self.anchors[str(name)] = [float(x) for x in Vector(point)]
        if piece is not None:
            self.anchor_pieces[str(name)] = str(piece)
        return self.anchors[str(name)]

    # --- roles & bones -------------------------------------------------------------------
    def set_role(self, faces, role):
        r = S.role_index(role) if isinstance(role, str) else int(role)
        for f in faces:
            f[self.role_layer] = r
            f[self._set] = 1
        return faces

    def group(self, bone):
        if bone not in self.groups:
            self.groups[bone] = len(self.groups)
        return self.groups[bone]

    def set_bone(self, verts_or_faces, bone):
        g = self.group(bone)
        verts = set()
        for x in verts_or_faces:
            verts.update(x.verts if isinstance(x, bmesh.types.BMFace) else [x])
        for v in verts:
            v[self.deform].clear()
            v[self.deform][g] = 1.0

    def set_weights(self, verts_or_faces, weights):
        """Blended weights `{bone: weight}` (normalised) on these vertices, e.g. a shoulder pad shared between
        `chest` and `upperarm.l`. Bones outside the slot's `part_bones` must be in `part_blend_bones`."""
        tot = sum(weights.values()) or 1.0
        verts = set()
        for x in verts_or_faces:
            verts.update(x.verts if isinstance(x, bmesh.types.BMFace) else [x])
        for v in verts:
            v[self.deform].clear()
            for b, w in weights.items():
                if w > 1e-4:
                    v[self.deform][self.group(b)] = w / tot

    # --- helpers -------------------------------------------------------------------------
    @staticmethod
    def ring(center, rx, ry=None, n=8, axis="z", phase=None, angles=None):
        """Points of an ellipse around `center`. axis: normal of the ring ('x', 'y' or 'z').
        Default phase puts a flat edge (not a vertex) at the front (-Y) / bottom.
        angles: explicit angles in degrees (0 = +first axis, counter-clockwise)."""
        c = Vector(center)
        ry = rx if ry is None else ry
        if angles is None:
            ph = (180.0 / n) if phase is None else phase
            angles = [ph + i * 360.0 / n for i in range(n)]
        pts = []
        for a in angles:
            t = math.radians(a)
            u, w = rx * math.cos(t), ry * math.sin(t)
            if axis == "z":
                pts.append(c + Vector((u, w, 0)))
            elif axis == "x":
                pts.append(c + Vector((0, u, w)))
            else:
                pts.append(c + Vector((u, 0, w)))
        return pts

    @staticmethod
    def rect(center, sx, sy, chamfer=0.0, axis="z"):
        """Rectangle (half sizes sx, sy) as a ring, optionally with chamfered corners (8 points).
        The first axis is X (axis z or y) or Y (axis x)."""
        c = Vector(center)
        if chamfer <= 0:
            q = [(sx, sy), (-sx, sy), (-sx, -sy), (sx, -sy)]
        else:
            k = chamfer
            q = [(sx, sy - k), (sx - k, sy), (-sx + k, sy), (-sx, sy - k),
                 (-sx, -sy + k), (-sx + k, -sy), (sx - k, -sy), (sx, -sy + k)]
        out = []
        for u, w in q:
            if axis == "z":
                out.append(c + Vector((u, w, 0)))
            elif axis == "x":
                out.append(c + Vector((0, u, w)))
            else:
                out.append(c + Vector((u, 0, w)))
        return out

    @staticmethod
    def rrect(center, sx, sy, r, seg=2, axis="z"):
        """Rounded rectangle ring (half sizes sx, sy; corner radius r, `seg` segments per corner,
        4 * (seg + 1) points). Same axis convention as rect()."""
        c = Vector(center)
        r = max(1e-4, min(r, sx - 1e-4, sy - 1e-4))
        out = []
        for k, (cx, cy) in enumerate(((sx - r, sy - r), (-sx + r, sy - r), (-sx + r, -sy + r), (sx - r, -sy + r))):
            for j in range(seg + 1):
                t = math.radians(90 * k + 90 * j / seg)
                u, w = cx + r * math.cos(t), cy + r * math.sin(t)
                if axis == "z":
                    out.append(c + Vector((u, w, 0)))
                elif axis == "x":
                    out.append(c + Vector((0, u, w)))
                else:
                    out.append(c + Vector((u, 0, w)))
        return out

    # --- primitives ----------------------------------------------------------------------
    def loft(self, rings, role, cap_start=True, cap_end=True, bone=None, cap_roles=None):
        """Closed tube through `rings` (lists of points, same count; a 1-point ring is an apex).
        role: a role name, a list with one role per band, or a function (band, i) -> role.
        Caps: an n-gon if n <= max_ngon, else a fan of quads. Returns the faces."""
        bm = self.bm
        vrings = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
        faces = []
        nb = len(vrings) - 1

        def role_of(b, i):
            if callable(role):
                return role(b, i)
            if isinstance(role, (list, tuple)):
                return role[b]
            return role

        for b in range(nb):
            A, B = vrings[b], vrings[b + 1]
            if len(A) == 1 or len(B) == 1:
                apex, ring = (A[0], B) if len(A) == 1 else (B[0], A)
                n = len(ring)
                for i in range(n):
                    v = [ring[i], ring[(i + 1) % n], apex]
                    if len(A) == 1:
                        v = v[::-1]
                    f = bm.faces.new(v)
                    self.set_role([f], role_of(b, i))
                    faces.append(f)
                continue
            n = len(A)
            assert len(B) == n, "rings must have the same number of points"
            for i in range(n):
                f = bm.faces.new([A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]])
                self.set_role([f], role_of(b, i))
                faces.append(f)
        cr = cap_roles or (None, None)
        if cap_start and len(vrings[0]) > 2:
            faces += self._cap(vrings[0], cr[0] or role_of(0, 0), flip=False)
        if cap_end and len(vrings[-1]) > 2:
            faces += self._cap(vrings[-1], cr[1] or role_of(nb - 1, 0), flip=True)
        if bone:
            self.set_bone(faces, bone)
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        return faces

    def _cap(self, ring, role, flip):
        """Cap a planar convex ring: one n-gon if allowed, else a fan of quads from the first
        vertex (n - 2 triangles, no extra vertex)."""
        bm = self.bm
        vs = ring[::-1] if not flip else ring
        n = len(vs)
        if n <= S.load()["topology"]["max_ngon"]:
            polys = [vs]
        else:
            polys, i = [], 1
            while i + 1 < n:
                polys.append([vs[0], vs[i], vs[i + 1]] + ([vs[i + 2]] if i + 2 < n else []))
                i += 2
        out = []
        for vv in polys:
            f = bm.faces.new(vv)
            self.set_role([f], role)
            out.append(f)
        return out

    def box(self, lo, hi, role, bone=None, chamfer=0.0):
        """Axis-aligned box from corner lo to corner hi (optionally chamfered vertical edges)."""
        lo, hi = Vector(lo), Vector(hi)
        c = (lo + hi) / 2
        sx, sy = (hi.x - lo.x) / 2, (hi.y - lo.y) / 2
        r0 = self.rect((c.x, c.y, lo.z), sx, sy, chamfer)
        r1 = self.rect((c.x, c.y, hi.z), sx, sy, chamfer)
        return self.loft([r0, r1], role, bone=bone)

    def rbox(self, lo, hi, role, r=None, bevel=None, seg=2, axis="z", bone=None):
        """Box from corner lo to hi with rounded edges along `axis` (radius r, default 20 % of the
        smaller cross-section side) and 45-degree bevels of size `bevel` on both end faces."""
        lo, hi = Vector(lo), Vector(hi)
        a = "xyz".index(axis)
        cross = [i for i in range(3) if i != a]
        if axis == "x":
            cross = [1, 2]
        sx, sy = (hi[cross[0]] - lo[cross[0]]) / 2, (hi[cross[1]] - lo[cross[1]]) / 2
        r = 0.2 * min(sx, sy) * 2 if r is None else r
        bevel = min(r, (hi[a] - lo[a]) / 4) if bevel is None else bevel
        c = (lo + hi) / 2

        def at(t):
            p = c.copy()
            p[a] = t
            return p
        rings = []
        if bevel > 0:
            rings.append(self.rrect(at(lo[a]), sx - bevel, sy - bevel, max(r - bevel, r * 0.4), seg, axis))
        rings.append(self.rrect(at(lo[a] + bevel), sx, sy, r, seg, axis))
        rings.append(self.rrect(at(hi[a] - bevel), sx, sy, r, seg, axis))
        if bevel > 0:
            rings.append(self.rrect(at(hi[a]), sx - bevel, sy - bevel, max(r - bevel, r * 0.4), seg, axis))
        return self.loft(rings, role, bone=bone)

    def cylinder(self, a, b, r, n=6, role="primary", bone=None, r_end=None):
        """Tube from point a to point b (radius r, optionally tapering to r_end)."""
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized()
        q = Vector((0, 0, 1)).rotation_difference(d)
        r_end = r if r_end is None else r_end
        rings = []
        for p, rr in ((a, r), (b, r_end)):
            pts = self.ring((0, 0, 0), rr, n=n)
            rings.append([p + q @ v for v in pts])
        return self.loft(rings, role, bone=bone)

    def shell(self, grid, thickness, role, cyclic=False, bone=None, edge_role=None):
        """Thick sheet (plates, guards, capes): `grid` is rows (v) of points (u), the outer surface.
        A copy offset by `thickness` along the surface normal (negative: the other side) closes it
        into one manifold shell. cyclic=True joins the last column to the first (a band).
        edge_role: role of the rim faces (default `role`). Returns the faces."""
        bm = self.bm
        rows = [[Vector(p) for p in r] for r in grid]
        nv, nu = len(rows), len(rows[0])
        assert nv >= 2 and nu >= 2 and all(len(r) == nu for r in rows), "grid must be >= 2 x 2 and rectangular"

        def P_(i, j):
            if cyclic:
                j %= nu
            return rows[max(0, min(nv - 1, i))][max(0, min(nu - 1, j))]

        inner = []
        for i in range(nv):
            row = []
            for j in range(nu):
                du = P_(i, j + 1) - P_(i, j - 1)
                dv = P_(i + 1, j) - P_(i - 1, j)
                n = du.cross(dv)
                n = n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))
                row.append(rows[i][j] - n * thickness)
            inner.append(row)
        O = [[bm.verts.new(p) for p in r] for r in rows]
        I = [[bm.verts.new(p) for p in r] for r in inner]
        faces, rim = [], []
        ju = nu if cyclic else nu - 1
        for i in range(nv - 1):
            for j in range(ju):
                k = (j + 1) % nu
                faces.append(bm.faces.new([O[i][j], O[i][k], O[i + 1][k], O[i + 1][j]]))
                faces.append(bm.faces.new([I[i][j], I[i + 1][j], I[i + 1][k], I[i][k]]))
        self.set_role(faces, role)
        for j in range(ju):  # top and bottom rims
            k = (j + 1) % nu
            rim.append(bm.faces.new([O[0][j], I[0][j], I[0][k], O[0][k]]))
            rim.append(bm.faces.new([O[-1][j], O[-1][k], I[-1][k], I[-1][j]]))
        if not cyclic:  # side rims
            for i in range(nv - 1):
                rim.append(bm.faces.new([O[i][0], O[i + 1][0], I[i + 1][0], I[i][0]]))
                rim.append(bm.faces.new([O[i][-1], I[i][-1], I[i + 1][-1], O[i + 1][-1]]))
        self.set_role(rim, edge_role or role)
        faces += rim
        if bone:
            self.set_bone(faces, bone)
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        return faces

    def sweep(self, path, profile, role, normals, cyclic=False, bone=None):
        """Sweep a 2D cross-section along `path` (bevelled straps, bands, rims, frames).
        normals: outward direction per path point (e.g. the surface normal under a strap).
        profile: list of (out, side) points, a closed convex-ish ring: `out` along the normal, `side`
        along tangent x normal; or a function i -> such a list (same length) to vary it along the path.
        Ends are capped unless cyclic. Returns the faces."""
        path = [Vector(p) for p in path]
        n = len(path)
        rings = []
        for i, p in enumerate(path):
            a = path[(i - 1) % n] if (cyclic or i > 0) else p
            b = path[(i + 1) % n] if (cyclic or i < n - 1) else p
            t = (b - a).normalized()
            nn = Vector(normals[i])
            nn = (nn - t * nn.dot(t)).normalized()
            side = t.cross(nn)
            prof = profile(i) if callable(profile) else profile
            rings.append([p + nn * o + side * s for o, s in prof])
        if cyclic:
            rings.append(rings[0])
            faces = self.loft(rings, role, cap_start=False, cap_end=False, bone=bone)
            bmesh.ops.remove_doubles(self.bm, verts=list({v for f in faces for v in f.verts}), dist=1e-6)
            faces = [f for f in faces if f.is_valid]
            bmesh.ops.recalc_face_normals(self.bm, faces=faces)
            return faces
        return self.loft(rings, role, bone=bone)

    @staticmethod
    def strap_profile(width, height, bevel, inset=0.004):
        """Cross-section of a bevelled strap lying on a surface: `width` across, `height` above it
        (starting `inset` below the surface so it sits in it), 45-degree bevels of size `bevel`."""
        w, h, k = width / 2, height, min(bevel, width / 2 - 1e-4, height - 1e-4)
        return [(-inset, -w), (h - k, -w), (h, -w + k), (h, w - k), (h - k, w), (-inset, w)]

    def dome(self, center, normal, r, height, n=8, role="accent", bone=None):
        """Rivet / stud: a low dome of radius r on a surface (base sunk 3 mm into it)."""
        c, nn = Vector(center), Vector(normal).normalized()
        q = Vector((0, 0, 1)).rotation_difference(nn)
        base = [c - nn * 0.003 + q @ v for v in self.ring((0, 0, 0), r, n=n)]
        mid = [c + nn * height * 0.6 + q @ v for v in self.ring((0, 0, 0), r * 0.72, n=n)]
        return self.loft([base, mid, [c + nn * height]], role, bone=bone)

    def transform(self, faces, matrix):
        verts = {v for f in faces for v in f.verts}
        bmesh.ops.transform(self.bm, matrix=Matrix(matrix), verts=list(verts))
        return faces

    def mirror_x(self, faces):
        """Duplicate `faces` mirrored on X (bone weights .l <-> .r). Returns the new faces."""
        ret = bmesh.ops.duplicate(self.bm, geom=list(faces))
        new_faces = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
        new_verts = {g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)}
        for v in new_verts:
            v.co.x = -v.co.x
            w = dict(v[self.deform].items())
            if w:
                inv = {i: n for n, i in self.groups.items()}
                v[self.deform].clear()
                for gi, wt in w.items():
                    v[self.deform][self.group(mirror_bone(inv[gi]))] = wt
        bmesh.ops.reverse_faces(self.bm, faces=new_faces)
        return new_faces

    # --- output --------------------------------------------------------------------------
    def to_object(self, slot):
        bm = self.bm
        self._close_piece()
        if "_piece_done" in bm.faces.layers.int:
            bm.faces.layers.int.remove(bm.faces.layers.int["_piece_done"])
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=S.load()["topology"]["merge_distance"])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        unset = sum(1 for f in bm.faces if not f[self._set])
        bm.faces.layers.int.remove(self._set)
        name = f"part_{slot}"
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = False
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for bone, _ in sorted(self.groups.items(), key=lambda kv: kv[1]):
            obj.vertex_groups.new(name=bone)
        return obj, unset


def script_namespace(builder, tpl):
    lm = {k: Vector(v) for k, v in tpl["landmarks"].items()}
    bones = {n: (Vector(b["head"]), Vector(b["tail"])) for n, b in tpl["bones"].items()}
    return {"P": builder, "lm": lm, "bones": bones, "guides": dict(tpl.get("guides", {})), "tpl": tpl,
            "Vector": Vector, "Matrix": Matrix, "math": math, "bmesh": bmesh, "bpy": bpy}


# --- checks ------------------------------------------------------------------------------

def _bbox(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def budget_for(slot):
    b = S.load()["budget"]
    for key in ("head", "accessory_hand", "accessory_back"):
        if slot in b[key]["slots"]:
            return key, b[key]["target"], b[key]["hard"]
    return "character", b["character"]["target"][1], b["character"]["hard"]


def fit_checks(slot, lo, hi, lm, tol):
    """Does the part sit where its slot belongs on the template? Returns a list of problems."""
    out = []

    def near(val, want, what):
        if abs(val - want) > tol:
            out.append(f"{what}: {val:.3f} (template {want:.3f})")

    if slot == "head":
        near(hi.z, lm["head_top"].z, "head top z")
        if lo.z > lm["head_base"].z + tol:
            out.append(f"head bottom z {lo.z:.3f} above the head joint {lm['head_base'].z:.3f}: gap at the neck")
    elif slot == "torso":
        if hi.z < lm["shoulder.l"].z:
            out.append(f"torso top z {hi.z:.3f} below the shoulders {lm['shoulder.l'].z:.3f}")
        if hi.x < lm["shoulder.l"].x - tol:
            out.append(f"torso half width {hi.x:.3f} does not reach the shoulder joint x {lm['shoulder.l'].x:.3f}")
    elif slot == "arms":
        if hi.x < lm["wrist.l"].x - 2 * tol:
            out.append(f"arms end at x {hi.x:.3f}, wrist joint at {lm['wrist.l'].x:.3f}")
        if lo.x > -lm["wrist.l"].x + 2 * tol:
            out.append("arms: right arm missing or too short (mirror the left one)")
    elif slot == "hands":
        if not (lo.x <= -lm["wrist.l"].x + tol and hi.x >= lm["wrist.l"].x - tol):
            out.append("hands must start at both wrist joints")
    elif slot == "feet":
        near(lo.z, 0.0, "feet bottom z")
        if lo.y > lm["toes.l"].y + tol:
            out.append(f"feet end at y {lo.y:.3f}, template toe tip at {lm['toes.l'].y:.3f}")
    elif slot == "legs":
        if hi.z < lm["hip.l"].z - tol:
            out.append("legs do not reach the hip joints")
    elif slot in ("accessory_hand_r", "accessory_hand_l"):
        hs = lm["handslot.r" if slot.endswith("_r") else "handslot.l"]
        if not all(lo[i] - tol <= hs[i] <= hi[i] + tol for i in range(3)):
            out.append(f"{slot} must pass through its handslot at {tuple(round(x, 3) for x in hs)}")
    elif slot == "headwear":
        if hi.z < lm["head_top"].z - 0.1:
            out.append(f"{slot} top {hi.z:.3f} is well below the head top {lm['head_top'].z:.3f}")
    return out


def check_part(obj, slot, tpl, unset_roles):
    """Hard errors and warnings for a freshly built part."""
    style = S.load()
    mesh = obj.data
    if not mesh.polygons:
        return ["part has no faces"], [], {"tris": 0}
    key, target, hard_lim = budget_for(slot)
    hard, soft, st = mesh_checks(obj, unset_roles, key, target, hard_lim)

    lo, hi = _bbox(obj)
    lm = {k: Vector(v) for k, v in tpl["landmarks"].items()}
    soft += [f"fit: {m}" for m in fit_checks(slot, lo, hi, lm, style["parts"]["fit_tolerance"])]

    if not slot.startswith("accessory"):
        pts = [v.co for v in mesh.vertices]
        kd = KDTree(len(pts))
        for i, co in enumerate(pts):
            kd.insert(co, i)
        kd.balance()
        asym = sum(1 for co in pts if kd.find(Vector((-co.x, co.y, co.z)))[2] > 0.002)
        if asym:
            soft.append(f"asymmetric: {asym} of {len(pts)} vertices have no X-mirror partner (base parts are symmetric)")

    allowed = set(style["skeleton"]["part_bones"][slot]) | set(style["skeleton"].get("part_blend_bones", {}).get(slot, []))
    for g in obj.vertex_groups:
        if g.name not in allowed:
            hard.append(f"vertex group {g.name!r} is not an allowed bone for {slot}: {sorted(allowed)}")
    return hard, soft, st


def check_prop(obj, ptype, unset_roles, anchors, pieces=None, anchor_pieces=None):
    """Hard errors and warnings for a freshly built prop (STYLE.md §9b)."""
    style = S.load()
    types = style["props"]["types"]
    if ptype not in types:
        return [f"unknown prop type {ptype!r} (known: {sorted(types)})"], [], {"tris": 0}
    if not obj.data.polygons:
        return ["prop has no faces"], [], {"tris": 0}
    key = types[ptype]["budget"]
    b = style["budget"].get(key)
    if b is None:
        return [f"style {style['style']!r} has no {key!r} budget (styles/<style>/STYLE.md §3)"], [], {"tris": 0}
    hard, soft, st = mesh_checks(obj, unset_roles, key, b["target"], b["hard"])
    missing = [a for a in types[ptype]["anchors"] if a not in anchors]
    if missing:
        hard.append(f"missing anchors {missing} for a {ptype} (P.anchor(name, point))")
    if "grip" in anchors and "muzzle" in anchors and anchors["muzzle"][0] <= anchors["grip"][0]:
        hard.append("muzzle must lie in front of the grip (+X: held items are modelled along +X, top +Z)")
    if "grip" in anchors and "tip" in anchors and anchors["tip"][2] <= anchors["grip"][2]:
        hard.append("tip must lie above the grip (+Z: melee items and shields stand upright in the hand slot's frame)")
    if obj.vertex_groups:
        hard.append("props carry no bone weights")
    pieces = pieces or {}
    for piece, parent in pieces.items():
        if parent is not None and parent not in anchors:
            hard.append(f"piece {piece!r}: parent anchor {parent!r} is not named (P.anchor)")
    for a, piece in (anchor_pieces or {}).items():
        if piece not in pieces:
            hard.append(f"anchor {a!r} follows piece {piece!r}, which is not declared (P.piece)")
    for piece in types[ptype].get("pieces", []):
        if piece not in pieces:
            hard.append(f"a {ptype} needs a separate piece {piece!r} (P.piece)")
    if pieces:
        lay = obj.data.attributes.get("piece")
        counts = [0] * (len(pieces) + 1)
        for v in (lay.data if lay else []):
            counts[v.value] += 1
        empty = [n for n, c in zip(["(main)", *pieces], counts) if c == 0]
        if empty:
            hard.append(f"pieces without faces: {empty}")
        st["pieces"] = dict(zip(["(main)", *pieces], [c for c in counts]))
    st["anchors"] = {k: [round(x, 4) for x in v] for k, v in anchors.items()}
    return hard, soft, st


def mesh_checks(obj, unset_roles, key, target, hard_lim):
    """Checks every built mesh gets: roles, budget, closed and outward shells, n-gons, zero-area faces."""
    style = S.load()
    mesh = obj.data
    hard, soft = [], []
    tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
    if unset_roles:
        hard.append(f"{unset_roles} faces without a role (use P.set_role or a primitive's role argument)")
    roles = style["roles"]
    attr = mesh.attributes["role"]
    used = sorted({roles[attr.data[p.index].value] for p in mesh.polygons if 0 <= attr.data[p.index].value < len(roles)})
    bad = sum(1 for p in mesh.polygons if not 0 <= attr.data[p.index].value < len(roles))
    if bad:
        hard.append(f"{bad} faces with an invalid role value")

    if tris > hard_lim:
        hard.append(f"{tris} tris > hard limit {hard_lim} ({key} budget)")
    elif tris > target:
        soft.append(f"{tris} tris above the {key} target {target} (the whole {key} group shares it)")

    bm = bmesh.new()
    bm.from_mesh(mesh)
    open_e = sum(1 for e in bm.edges if e.is_boundary)
    nonman = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
    if open_e or nonman:
        hard.append(f"non-manifold: {open_e} open edges, {nonman} non-manifold edges (close every shell)")
    # inside-out shells (negative signed volume)
    ids = {}
    for v in bm.verts:
        if v.index in ids:
            continue
        stack, ids[v.index] = [v], v.index
        while stack:
            x = stack.pop()
            for e in x.link_edges:
                o = e.other_vert(x)
                if o.index not in ids:
                    ids[o.index] = v.index
                    stack.append(o)
    vol = defaultdict(float)
    for f in bm.faces:
        for t in range(1, len(f.verts) - 1):
            a, b, c = f.verts[0].co, f.verts[t].co, f.verts[t + 1].co
            vol[ids[f.verts[0].index]] += a.dot(b.cross(c)) / 6.0
    inverted = sum(1 for v in vol.values() if v < 0)
    if inverted:
        hard.append(f"{inverted} inside-out shells")
    ngons = sum(1 for f in bm.faces if len(f.verts) > style["topology"]["max_ngon"])
    if ngons:
        soft.append(f"{ngons} n-gons with more than {style['topology']['max_ngon']} vertices")
    tiny = sum(1 for f in bm.faces if f.calc_area() < style["topology"]["min_face_area"])
    if tiny:
        soft.append(f"{tiny} zero-area faces")
    bm.free()
    lo, hi = _bbox(obj)
    st = {"tris": tris, "verts": len(mesh.vertices), "roles": used, "shells": len(vol),
          "bbox": [[round(x, 4) for x in lo], [round(x, 4) for x in hi]]}
    return hard, soft, st


# --- loading & weighting -----------------------------------------------------------------

def load_part(part):
    """Append the part object from its .blend into the current scene."""
    path = part_path(part)
    if not path.exists():
        raise FileNotFoundError(f"part {part!r} not found ({path}); build it with build_part")
    slot, _ = split_part_name(part)
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n == f"part_{slot}"]
    if not dst.objects or dst.objects[0] is None:
        raise RuntimeError(f"{path} has no object part_{slot}")
    obj = dst.objects[0]
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (p - (a + ab * t)).length


def weight_nearest(obj, arm, bones):
    """Rigid weights: every vertex without a deform weight gets its nearest bone of `bones`."""
    segs = {b: (arm.data.bones[b].head_local.copy(), arm.data.bones[b].tail_local.copy()) for b in bones}
    for b in bones:
        if b not in obj.vertex_groups:
            obj.vertex_groups.new(name=b)
    gi = {g.index: g.name for g in obj.vertex_groups}
    for v in obj.data.vertices:
        if any(g.weight > 0 and gi[g.group] in segs for g in v.groups):
            continue
        p = obj.matrix_world @ v.co
        best = min(segs, key=lambda b: _seg_dist(p, *segs[b]))
        obj.vertex_groups[best].add([v.index], 1.0, "REPLACE")
