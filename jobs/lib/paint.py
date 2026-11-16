"""Painted surface (styles/painted, STYLE.md §4, SPIKE): per-character UVs, a texel map (3D position,
normal, face of every texel) and two ways to fill the base-colour texture:

  auto        procedural paint from the mesh: light, AO (Cycles bake), edge wear by convex creases,
              dirt in concave creases, noise, role treatments (rust/scratches/cracks on metal, ...)
  projection  the reference sheet's front/side/back views projected onto the mesh (z-buffer
              visibility, facing weights); texels no view sees fall back to `auto`

All colours are display (sRGB) values in 0..1, the way Blender stores 8-bit PNG pixels.
"""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from . import style as S

# ------------------------------------------------------------------------------------------------
# UVs + texel map


def unwrap(obj, name="Paint", angle=60.0, margin=0.004, check_size=1024):
    """Smart-UV-project `obj` into a new UV layer `name` (made active for render), then make sure no
    two faces share texels: smart project can fold a chart onto itself (seen: outer dome face over the
    hidden inner dome), and a shared texel paints the wrong face. Overlapping faces get their own
    planar island and everything is repacked. Returns (uv layer, overlapping faces fixed)."""
    mesh = obj.data
    uv = mesh.uv_layers.get(name) or mesh.uv_layers.new(name=name)
    mesh.uv_layers.active = uv
    uv.active_render = True
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin, area_weight=0.0,
                             scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    fixed = 0
    for _ in range(3):
        bad = uv_overlaps(mesh, name, check_size)
        if not bad:
            break
        fixed += len(bad)
        _own_islands(obj, name, bad)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")
        bpy.ops.uv.pack_islands(rotate=True, margin=margin)
        bpy.ops.object.mode_set(mode="OBJECT")
    left = uv_overlaps(mesh, name, check_size)
    if left:
        raise RuntimeError(f"UV overlaps left after repacking: {len(left)} faces")
    return uv, fixed


def uv_overlaps(mesh, name, size):
    """Faces whose triangles strictly cover a texel centre that another face also covers."""
    mesh.calc_loop_triangles()
    nl = len(mesh.loops)
    uv = np.empty(nl * 2)
    mesh.uv_layers[name].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2) * size - 0.5
    owner = -np.ones((size, size), dtype=np.int64)
    bad = set()
    for lt in mesh.loop_triangles:
        a, b, c = uv[list(lt.loops)]
        x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
        x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, size - 1), min(y1, size - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(d) < 1e-12:
            continue
        l0 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / d
        l1 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / d
        ins = (l0 > 1e-3) & (l1 > 1e-3) & (1 - l0 - l1 > 1e-3)
        yy, xx = ys[ins], xs[ins]
        prev = owner[yy, xx]
        clash = prev[(prev >= 0) & (prev != lt.polygon_index)]
        if len(clash):
            bad.add(lt.polygon_index)
            bad.update(int(p) for p in np.unique(clash))
        owner[yy, xx] = lt.polygon_index
    return bad


def _own_islands(obj, name, faces):
    """Give each face in `faces` its own planar UV island at the mesh's average texel density."""
    mesh = obj.data
    uvl = mesh.uv_layers[name]
    area3d = sum(p.area for p in mesh.polygons) or 1.0
    area_uv = 0.0
    for p in mesh.polygons:
        pts = [uvl.data[li].uv for li in p.loop_indices]
        area_uv += abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
    k = math.sqrt(area_uv / area3d)
    for fi in faces:
        p = mesh.polygons[fi]
        n = p.normal
        t = (mesh.vertices[p.vertices[1]].co - mesh.vertices[p.vertices[0]].co).normalized()
        b = n.cross(t)
        o = mesh.vertices[p.vertices[0]].co
        for li, vi in zip(p.loop_indices, p.vertices):
            d = mesh.vertices[vi].co - o
            uvl.data[li].uv = (d.dot(t) * k, d.dot(b) * k)


class TexelMap:
    """For a size x size texture: which triangle covers each texel and where that is in 3D."""

    def __init__(self, obj, size, uv_name="Paint"):
        mesh = obj.data
        mesh.calc_loop_triangles()
        self.size = size
        mw = obj.matrix_world
        nl = len(mesh.loops)
        uv = np.empty(nl * 2, dtype=np.float64)
        mesh.uv_layers[uv_name].data.foreach_get("uv", uv)
        uv = uv.reshape(-1, 2)
        lv = np.empty(nl, dtype=np.int64)
        mesh.loops.foreach_get("vertex_index", lv)
        co = np.empty(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        M = np.array(mw)
        co = co @ M[:3, :3].T + M[:3, 3]
        cn = np.empty(nl * 3)
        mesh.corner_normals.foreach_get("vector", cn)
        cn = cn.reshape(-1, 3) @ np.array(mw.to_3x3().inverted().transposed()).T
        nt = len(mesh.loop_triangles)
        tl = np.empty(nt * 3, dtype=np.int64)
        mesh.loop_triangles.foreach_get("loops", tl)
        tl = tl.reshape(-1, 3)
        tp = np.empty(nt, dtype=np.int64)
        mesh.loop_triangles.foreach_get("polygon_index", tp)

        tri = -np.ones((size, size), dtype=np.int64)
        bary = np.zeros((size, size, 3), dtype=np.float64)
        prio = np.zeros((size, size), dtype=np.int8)   # 2 = texel centre inside, 1 = within reach of an edge
        puv = uv[tl] * size - 0.5          # texel centres at integer coords
        for t in range(nt):
            a, b, c = puv[t]
            x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
            x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
            x0, y0 = max(x0 - 1, 0), max(y0 - 1, 0)
            x1, y1 = min(x1 + 1, size - 1), min(y1 + 1, size - 1)
            if x1 < x0 or y1 < y0:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
            d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(d) < 1e-12:
                continue
            l0 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / d
            l1 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / d
            l2 = 1 - l0 - l1
            # conservative raster: also take texels whose centre is within ~1 texel of the triangle,
            # so faces thinner than a texel (band rims, bevels) still get painted; real hits win
            hts = [abs(d) / max(np.hypot(*(q - r)), 1e-9) for q, r in ((b, c), (c, a), (a, b))]
            strict = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
            near = (l0 * hts[0] >= -0.75) & (l1 * hts[1] >= -0.75) & (l2 * hts[2] >= -0.75)
            for sel, pr in ((near & ~strict, 1), (strict, 2)):
                yy, xx = ys[sel], xs[sel]
                ok = prio[yy, xx] <= pr if pr == 2 else prio[yy, xx] < pr
                yy, xx = yy[ok], xx[ok]
                tri[yy, xx] = t
                prio[yy, xx] = pr
                bary[yy, xx] = np.stack([l0[sel][ok], l1[sel][ok], l2[sel][ok]], -1)
        self.mask = tri >= 0
        self.iy, self.ix = np.nonzero(self.mask)       # covered texels (row = v, col = u)
        t = tri[self.iy, self.ix]
        bw = np.clip(bary[self.iy, self.ix], 0, 1)
        bw /= bw.sum(1, keepdims=True)
        loops = tl[t]
        self.tri = t
        self.poly = tp[t]
        self.P = (co[lv[loops]] * bw[..., None]).sum(1)
        n = (cn[loops] * bw[..., None]).sum(1)
        self.N = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        self.n = len(t)

    def image(self, rgb, fill=(0, 0, 0)):
        """Texel colours -> size x size x 4 array (row 0 = v 0, i.e. bottom-up like Blender)."""
        out = np.zeros((self.size, self.size, 4), dtype=np.float32)
        out[..., :3] = fill
        out[self.iy, self.ix, :3] = rgb
        out[..., 3] = 1.0
        return out

    def dilate(self, img, px):
        """Bleed island colours `px` texels outwards (mip/filter padding)."""
        filled = self.mask.copy()
        for _ in range(px):
            acc = np.zeros(img.shape[:2] + (3,), dtype=np.float32)
            cnt = np.zeros(img.shape[:2], dtype=np.float32)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                sh = np.roll(np.roll(filled, dy, 0), dx, 1)
                acc += np.roll(np.roll(img[..., :3], dy, 0), dx, 1) * sh[..., None]
                cnt += sh
            new = (~filled) & (cnt > 0)
            img[new, :3] = acc[new] / cnt[new][:, None]
            filled |= new
        return img


# ------------------------------------------------------------------------------------------------
# noise (numpy, deterministic)

def _hash(ix, iy, iz, seed):
    h = (ix.astype(np.uint32) * np.uint32(73856093)) ^ (iy.astype(np.uint32) * np.uint32(19349663)) \
        ^ (iz.astype(np.uint32) * np.uint32(83492791)) ^ np.uint32(seed * 2654435761 & 0xFFFFFFFF)
    h ^= h >> np.uint32(13)
    h *= np.uint32(1274126177)
    h ^= h >> np.uint32(16)
    return h


def value_noise(p, seed=0):
    """Smooth value noise in [0, 1] at points p (n x 3)."""
    f = np.floor(p)
    i = f.astype(np.int64)
    t = p - f
    t = t * t * (3 - 2 * t)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                h = _hash(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed).astype(np.float64) / 4294967295.0
                w = (t[:, 0] if dx else 1 - t[:, 0]) * (t[:, 1] if dy else 1 - t[:, 1]) * (t[:, 2] if dz else 1 - t[:, 2])
                out = out + h * w
    return out


def fbm(p, scale, octaves=4, seed=0):
    tot, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        tot = tot + amp * value_noise(p * scale * (2 ** o), seed + o * 17)
        norm += amp
        amp *= 0.5
    return tot / norm


def voronoi(p, scale, seed=0):
    """3D Voronoi at points p: (F1 distance, F2 - F1, random value in [0, 1] of the nearest cell)."""
    q = p * scale
    f = np.floor(q).astype(np.int64)
    d1 = np.full(len(q), 9.0)
    d2 = np.full(len(q), 9.0)
    rid = np.zeros(len(q))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = f + np.array([dx, dy, dz])
                fp = np.stack([_hash(c[:, 0], c[:, 1], c[:, 2], seed + k).astype(np.float64) / 4294967295.0
                               for k in range(4)], 1)
                d = np.linalg.norm(c + fp[:, :3] - q, axis=1)
                d2 = np.where(d < d1, d1, np.minimum(d2, d))
                rid = np.where(d < d1, fp[:, 3], rid)
                d1 = np.minimum(d1, d)
    return d1, d2 - d1, rid


def voronoi_edge(p, scale, seed=0):
    """F2 - F1 of a 3D Voronoi pattern (small near cell borders: crack lines)."""
    return voronoi(p, scale, seed)[1]


def rgb2hsv(c):
    mx, mn = c.max(1), c.min(1)
    d = mx - mn
    r, g, b = c[:, 0], c[:, 1], c[:, 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60.0
    h = np.where(d < 1e-9, 0.0, h)
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0.0)
    return np.stack([h, s, mx], 1)


def hsv2rgb(hsv):
    h, s, v = hsv[:, 0] % 360, np.clip(hsv[:, 1], 0, 1), np.clip(hsv[:, 2], 0, 1)
    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c
    z = np.zeros_like(h)
    k = (h // 60).astype(int)
    r = np.choose(k % 6, [c, x, z, z, x, c])
    g = np.choose(k % 6, [x, c, c, x, z, z])
    b = np.choose(k % 6, [z, z, x, c, c, x])
    return np.stack([r + m, g + m, b + m], 1)


def _hue_towards(h, target, amt):
    d = ((target - h + 180) % 360) - 180
    return h + d * amt


def ramp(base, l, r):
    """Painterly value ramp: l in [-1, 1] (shadow .. light) -> colour. Shadows darken and rotate hue
    towards r['shadow_hue'] (warm red/purple) with more saturation; lights brighten and rotate towards
    r['light_hue'] (yellow) with a bit less saturation. base: n x 3 or 3."""
    base = np.broadcast_to(np.asarray(base, dtype=np.float64), (len(l), 3))
    hsv = rgb2hsv(base)
    sh = np.clip(-l, 0, 1)
    li = np.clip(l, 0, 1)
    h = _hue_towards(hsv[:, 0], r["shadow_hue"], sh * r["shadow_hue_amt"])
    h = _hue_towards(h, r["light_hue"], li * r["light_hue_amt"])
    s = hsv[:, 1] * (1 + sh * (r["shadow_sat"] - 1)) * (1 + li * (r["light_sat"] - 1))
    v = hsv[:, 2] * (1 - sh * r["shadow_v"]) * (1 + li * r["light_v"])
    out = hsv2rgb(np.stack([h, s, np.minimum(v, 1)], 1))
    over = np.maximum(hsv[:, 2] * (1 + li * r["light_v"]) - 1, 0)   # past white: desaturate towards white
    return out + (1 - out) * np.clip(over, 0, 1)[:, None]


def smooth(a, lo, hi):
    t = np.clip((a - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


# ------------------------------------------------------------------------------------------------
# mesh features per texel

def crease_distances(obj, tm, min_deg=25.0):
    """Per texel: distance (m) to the nearest convex and nearest concave crease edge of its face
    (edges whose faces meet at more than `min_deg`, or open edges)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.faces.ensure_lookup_table()
    lim = math.radians(min_deg)
    convex = np.full(tm.n, 9.0)
    concave = np.full(tm.n, 9.0)
    order = np.argsort(tm.poly, kind="stable")
    polys = tm.poly[order]
    bounds = np.searchsorted(polys, np.arange(len(bm.faces) + 1))
    for fi, f in enumerate(bm.faces):
        sel = order[bounds[fi]:bounds[fi + 1]]
        if not len(sel):
            continue
        P = tm.P[sel]
        for e in f.edges:
            if len(e.link_faces) == 2:
                g = e.link_faces[0] if e.link_faces[1] is f else e.link_faces[1]
                ang = f.normal.angle(g.normal, 0.0)
                if ang < lim:
                    continue
                is_convex = f.normal.dot(g.calc_center_median() - f.calc_center_median()) < 0
            else:
                is_convex = True
            a, b = np.array(e.verts[0].co), np.array(e.verts[1].co)
            ab = b - a
            t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
            d = np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
            if is_convex:
                convex[sel] = np.minimum(convex[sel], d)
            else:
                concave[sel] = np.minimum(concave[sel], d)
    bm.free()
    return convex, concave


def bake_ao(obj, size, uv_name="Paint", distance=0.12, samples=48):
    """Cycles AO bake into the paint UVs -> texel AO values (1 = open, 0 = occluded)."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.light_settings.distance = distance
    img = bpy.data.images.new("_ao", size, size, alpha=False, float_buffer=True)
    mats = [m for m in obj.data.materials if m]
    if not mats:
        m = bpy.data.materials.new("_bake")
        obj.data.materials.append(m)
        mats = [m]
    nodes = []
    for m in mats:
        m.use_nodes = True
        n = m.node_tree.nodes.new("ShaderNodeTexImage")
        n.image = img
        m.node_tree.nodes.active = n
        nodes.append((m, n))
    obj.data.uv_layers.active = obj.data.uv_layers[uv_name]
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.bake(type="AO", margin=4, margin_type="EXTEND", use_clear=True)  # margin: border texels of the conservative raster sit just outside the faces
    px = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)
    for m, n in nodes:
        m.node_tree.nodes.remove(n)
    bpy.data.images.remove(img)
    return px  # bottom-up rows, like TexelMap


# ------------------------------------------------------------------------------------------------
# approaches

def role_names(obj):
    roles = S.load()["roles"]
    a = obj.data.attributes["role"]
    v = np.empty(len(obj.data.polygons), dtype=np.int64)
    a.data.foreach_get("value", v)
    return roles, v


def piece_ids(obj, tm):
    """Per texel: id of its connected piece (faces linked by shared edges), so every band, plate and
    dome gets its own top-to-bottom light gradient."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    pid = -np.ones(len(bm.faces), dtype=np.int64)
    n = 0
    for f in bm.faces:
        if pid[f.index] >= 0:
            continue
        stack = [f]
        pid[f.index] = n
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if pid[h.index] < 0:
                        pid[h.index] = n
                        stack.append(h)
        n += 1
    bm.free()
    return pid[tm.poly]


def glow_distance(P, src, radius, max_src=6000):
    """Per point: distance (m) to the nearest point of `src`, capped at `radius` (mathutils KD-tree)."""
    from mathutils.kdtree import KDTree
    out = np.full(len(P), radius)
    if not len(src):
        return out
    if len(src) > max_src:
        src = src[np.linspace(0, len(src) - 1, max_src).astype(int)]
    kd = KDTree(len(src))
    for i, q in enumerate(src):
        kd.insert(q.tolist(), i)
    kd.balance()
    lo, hi = src.min(0) - radius, src.max(0) + radius
    near = np.nonzero(((P >= lo) & (P <= hi)).all(1))[0]
    for i in near:
        _, _, d = kd.find(P[i].tolist())
        out[i] = min(d, radius)
    return out


def cast_shadow(obj, P, N, L, max_dist=0.6):
    """1 where the ray from a texel towards the light hits the mesh, else 0 (BVH ray cast, world space)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    bm.from_object(obj, dg)
    bm.transform(obj.matrix_world)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    d = Vector(L.tolist())
    O = P + N * 0.003
    out = np.zeros(len(P))
    facing = N @ L > -0.05          # texels facing away are dark from the key light anyway
    for i in np.nonzero(facing)[0]:
        hit = tree.ray_cast(Vector(O[i].tolist()), d, max_dist)
        if hit[0] is not None:
            out[i] = 1.0
    return out


def auto_paint(obj, tm, colors, cfg, seed=1):
    """Procedural paint. colors: {role: palette index}; cfg: style paint.auto.

    Light is a signed value l in [-1, 1] per texel (key light, part height gradient, AO, brush dabs,
    soft value bands); each role's base colour goes through a hue-shifted ramp (`ramp`), then the role
    treatments (mottle, rim light/shadow, dirt, rust, scratches, cracks, glow halo) are layered on top."""
    style = S.load()
    pal = style["palette"]["colors"]
    roles, prole = role_names(obj)
    trole = prole[tm.poly]
    P, N = tm.P, tm.N
    base = np.zeros((tm.n, 3))
    for i, r in enumerate(roles):
        sel = trole == i
        if sel.any():
            base[sel] = hexrgb(pal[colors.get(r, 51)])
    stats = {}
    treat = cfg["roles"]
    ramp_default = cfg["ramp"]

    # key light (wrapped lambert), height gradient per connected piece, AO
    L = np.array(cfg["light_dir"], dtype=np.float64)
    L /= np.linalg.norm(L)
    lw = cfg["light"]
    Nk = N
    if lw.get("facet"):  # part of the light from the flat face normal: painted planes, not a gradient
        fn = np.empty(len(obj.data.polygons) * 3)
        obj.data.polygons.foreach_get("normal", fn)
        fn = fn.reshape(-1, 3) @ np.array(obj.matrix_world.to_3x3().inverted().transposed()).T
        fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
        Nk = N * (1 - lw["facet"]) + fn[tm.poly] * lw["facet"]
        Nk /= np.linalg.norm(Nk, axis=1, keepdims=True) + 1e-12
    k = np.clip(Nk @ L * 0.5 + 0.5, 0, 1)
    if lw.get("shadow"):  # cast shadow from the key light (under bands, brows, cheekbones, teeth)
        sh = cast_shadow(obj, P, N, L)
        k = k * (1 - lw["shadow"] * sh)
        stats["shadow_frac"] = round(float(sh.mean()), 3)
    piece = piece_ids(obj, tm)
    g = np.zeros(tm.n)
    for sid in np.unique(piece):
        sel = piece == sid
        z = P[sel, 2]
        g[sel] = (z - z.min()) / max(z.max() - z.min(), 1e-6)
    ao_img = bake_ao(obj, tm.size, distance=cfg["ao_distance"])
    ao = ao_img[tm.iy, tm.ix, 0]
    stats["ao_mean"] = round(float(ao.mean()), 3)
    l = (k - 0.5) * 2 * lw["key"] + (g - 0.5) * 2 * lw["gradient"] + lw["bias"] - (1 - ao) * lw["ao"]

    # brush dabs: one random value per Voronoi cell (flat strokes), plus soft value bands whose
    # borders wander with noise (painted, not airbrushed)
    b = cfg["brush"]
    _, _, cell = voronoi(P * np.array(b["stretch"]), b["dab_scale"], seed + 21)
    wob = fbm(P, b["wobble_scale"], 3, seed)
    l = l + (cell - 0.5) * 2 * b["dab_amount"] + (wob - 0.5) * 2 * b["wobble_amount"]
    if b["bands"]:
        lq = np.round(l * b["bands"]) / b["bands"]
        l = l + (lq - l) * b["band_mix"]
    l = np.clip(l, -1, 1)

    # creases
    cvx, ccv = crease_distances(obj, tm, cfg["crease_min_deg"])
    edge = 1 - smooth(cvx, 0, cfg["edge_width"])
    dirt = 1 - smooth(ccv, 0, cfg["dirt_width"])

    col = np.zeros((tm.n, 3))
    glow_src = []
    for i, r in enumerate(roles):
        sel = trole == i
        if not sel.any():
            continue
        t = treat.get(r, {})
        rp = {**ramp_default, **t.get("ramp", {})}
        ls = l[sel]
        c = ramp(base[sel], ls, rp)
        Ps, d, ks = P[sel], dirt[sel], k[sel]
        e = 1 - smooth(cvx[sel], 0, t["edge_width"]) if "edge_width" in t else edge[sel]
        if t.get("mottle"):  # painterly colour blotches (hue shift, not just value)
            mn = fbm(Ps, t.get("mottle_scale", 5.0), 3, seed + 11)
            m = smooth(mn, 0.42, 0.72) * t["mottle"]
            tgt = ramp(hexrgb(t["mottle_color"]), ls, rp)
            c = c * (1 - m[:, None]) + tgt * m[:, None]
        if t.get("edge_highlight"):  # rim light on edges facing the light, rim shadow on the others
            chip = fbm(Ps, 40, 2, seed + 3)
            lit = smooth(ks, 0.35, 0.75)
            m = e * (0.6 + 0.4 * smooth(chip, 0.35, 0.6)) * t["edge_highlight"] * lit
            hl = hexrgb(t.get("highlight_color", "#FFFFFF"))
            c = c * (1 - m[:, None]) + hl * m[:, None]
            ms = e * t.get("edge_shadow", 0.0) * (1 - lit)
            c = c * (1 - 0.5 * ms[:, None])
        if t.get("dirt"):
            m = d * t["dirt"]
            c = c * (1 - m[:, None]) + hexrgb(t.get("dirt_color", "#2A1A14")) * m[:, None]
        if t.get("rust"):  # rust creeps in from edges, creases and the lower part of each piece
            rn = fbm(Ps, t.get("rust_scale", 6.0), 4, seed + 5)
            drive = rn + 0.3 * e + 0.3 * d + 0.25 * (1 - g[sel]) + 0.2 * (1 - ao[sel])
            m = smooth(drive, t.get("rust_lo", 0.8), t.get("rust_lo", 0.8) + 0.12) * t["rust"]
            rc = ramp(hexrgb(t.get("rust_color", "#C2602A")) * (0.8 + 0.4 * fbm(Ps, 30, 2, seed + 6))[:, None], ls, rp)
            c = c * (1 - m[:, None]) + rc * m[:, None]
        if t.get("scratches"):
            q = Ps * np.array([1.0, 1.0, 7.0])           # stretched noise -> short streaks
            sn = fbm(q, 22, 2, seed + 7)
            m = smooth(sn, 0.74, 0.8) * t["scratches"]
            c = c * (1 - m[:, None]) + np.minimum(c * 1.45, 1) * m[:, None]
        if t.get("cracks"):  # few, long, dark cracks with a lit lip on the lower side
            ve = voronoi_edge(Ps, t.get("crack_scale", 7.0), seed + 9)
            sparse = smooth(fbm(Ps, t.get("crack_density_scale", 3.0), 2, seed + 10),
                            t.get("crack_sparse", 0.6), t.get("crack_sparse", 0.6) + 0.06)
            w = t.get("crack_width", 0.035)
            line = (1 - smooth(ve, 0.0, w)) * sparse
            lip = np.clip((1 - smooth(ve, w, 2.2 * w)) * sparse - line, 0, 1)
            dark = hexrgb(t.get("crack_color", "#1E1218"))
            c = c * (1 - line[:, None] * t["cracks"]) + dark * (line[:, None] * t["cracks"])
            c = c + (np.minimum(c * 1.35, 1) - c) * (0.6 * lip[:, None] * t["cracks"])
        if t.get("glow"):  # emissive look: bright core, saturated rim
            core = smooth(ks, 0.3, 0.9)
            c = base[sel] * (1 + t["glow"])
            c = c + (hexrgb(t.get("core_color", "#E8FFFF")) - c) * (core ** 2)[:, None] * t.get("core", 0.6)
            glow_src.append((Ps, base[sel]))
        col[sel] = c

    # glow halo: light from `special` faces spills onto nearby surfaces (eye sockets, cheekbones)
    gh = cfg.get("glow_halo")
    if gh and glow_src:
        src = np.concatenate([p for p, _ in glow_src])
        gcol = np.concatenate([c for _, c in glow_src]).mean(0)
        is_src = np.isin(trole, [roles.index(r) for r in treat if treat[r].get("glow")])
        dist = glow_distance(P, src, gh["radius"])
        h = (1 - dist / gh["radius"]) ** gh["falloff"] * gh["amount"] * ~is_src
        gc = hexrgb(gh["color"]) if gh.get("color") else gcol
        col = col * (1 - h[:, None]) + (col * 0.3 + gc * 0.9) * h[:, None]
        stats["glow_halo_texels"] = int((h > 0.05).sum())
    stats["texels"] = int(tm.n)
    stats["light_mean"] = round(float(l.mean()), 3)
    return np.clip(col, 0, 1), stats


VIEW_DIRS = {"front": (0, -1, 0), "back": (0, 1, 0), "side": (1, 0, 0), "side_mirror": (-1, 0, 0)}


def _view_xy(P, view):
    """World point -> (horizontal metres, up metres) in the reference view (see lib/render.VIEWS)."""
    if view == "front":
        return P[:, 0], P[:, 2]
    if view == "back":
        return -P[:, 0], P[:, 2]
    return P[:, 1], P[:, 2]  # side (+X camera): screen right = +Y; mirror uses the same image


def near_mask(P, sel, dist):
    """Texels (positions P, n x 3) within ~dist (voxel hash: dist .. 2 dist) of any texel in `sel`."""
    if not sel.any():
        return np.zeros(len(P), dtype=bool)
    cells = np.floor(P / dist).astype(np.int64)
    lo = cells.min(0) - 1
    dims = cells.max(0) - lo + 2
    key = lambda c: ((c[:, 0] - lo[0]) * dims[1] + (c[:, 1] - lo[1])) * dims[2] + (c[:, 2] - lo[2])
    src = np.unique(cells[sel], axis=0)
    offs = np.array([(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)])
    near = np.unique(key((src[:, None, :] + offs[None]).reshape(-1, 3)))
    return np.isin(key(cells), near)


def zbuffer(obj, view, shape, to_px):
    """Orthographic depth buffer of the whole mesh for a view, at reference pixel resolution.
    Depth = distance towards the camera (bigger = closer)."""
    mesh = obj.data
    mesh.calc_loop_triangles()
    co = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", co)
    M = np.array(obj.matrix_world)
    co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
    tv = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", tv)
    tv = tv.reshape(-1, 3)
    d = np.array(VIEW_DIRS[view], dtype=np.float64)
    depth = co @ d
    col, row = to_px(*_view_xy(co, view))
    zb = np.full(shape, -9.0)
    H, W = shape
    for a, b, c in tv:
        xs3, ys3 = col[[a, b, c]], row[[a, b, c]]
        x0, x1 = max(int(np.floor(xs3.min())), 0), min(int(np.ceil(xs3.max())), W - 1)
        y0, y1 = max(int(np.floor(ys3.min())), 0), min(int(np.ceil(ys3.max())), H - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        (ax, bx, cx), (ay, by, cy) = xs3, ys3
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            continue
        l0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        l1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        l2 = 1 - l0 - l1
        ins = (l0 >= -0.01) & (l1 >= -0.01) & (l2 >= -0.01)
        z = l0 * depth[a] + l1 * depth[b] + l2 * depth[c]
        yy, xx, zz = ys[ins], xs[ins], z[ins]
        np.maximum.at(zb, (yy, xx), zz)
    return zb


def bilinear(img, x, y):
    H, W = img.shape[:2]
    x = np.clip(x, 0, W - 1.001)
    y = np.clip(y, 0, H - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def project_paint(obj, tm, ref, ref_img, fallback, cfg):
    """Project the reference views onto the texels. ref: reference.json dict; ref_img: top-down
    H x W x 4 source sheet. Returns (rgb, coverage, stats)."""
    mpp, floor = ref["m_per_px"], ref["floor_y"]
    bg = np.asarray(ref["background"][:3])
    fg = np.abs(ref_img[..., :3] - bg).sum(2) > cfg["bg_threshold"]
    # erode the foreground mask: silhouette pixels are anti-aliased with the background
    for _ in range(cfg["erode_px"]):
        fg = fg & np.roll(fg, 1, 0) & np.roll(fg, -1, 0) & np.roll(fg, 1, 1) & np.roll(fg, -1, 1)
    acc = np.zeros((tm.n, 3))
    wsum = np.zeros(tm.n)
    stats = {}
    views = [v for v in ("front", "side", "back") if v in ref["views"]]
    # the -X side: its own view if the sheet has one (stored flipped, screen right = +Y like `side`),
    # else the +X side reused mirrored (symmetric characters)
    if "side_mirror" in ref["views"]:
        jobs = [(v, v) for v in views] + [("side_mirror", "side_mirror")]
    else:
        jobs = [(v, v) for v in views] + ([("side_mirror", "side")] if "side" in views else [])
    for view, src in jobs:
        v = ref["views"][src]
        x0, x1 = v.get("x_range", [0, ref_img.shape[1]])
        cx = v["center_x"]

        def to_px(h, z, cx=cx):
            return cx + h / mpp, floor - z / mpp
        d = np.array(VIEW_DIRS[view], dtype=np.float64)
        facing = np.clip(tm.N @ d, 0, 1)
        h, z = _view_xy(tm.P, view)
        px, py = to_px(h, z)
        k = cfg.get("zbuffer_scale", 3)   # supersampled depth: clean occlusion edges
        H, W = ref_img.shape[:2]
        zb = zbuffer(obj, view, (H * k, W * k), lambda h, z, f=to_px: tuple(q * k + (k - 1) / 2 for q in f(h, z)))
        zix = np.clip(np.round(px * k + (k - 1) / 2).astype(int), 0, W * k - 1)
        ziy = np.clip(np.round(py * k + (k - 1) / 2).astype(int), 0, H * k - 1)
        ix = np.clip(np.round(px).astype(int), 0, W - 1)
        iy = np.clip(np.round(py).astype(int), 0, H - 1)
        depth = tm.P @ d
        # visible if no surface is clearly in front of the texel
        zmax = zb[ziy, zix]
        visible = depth >= zmax - cfg["depth_eps"]
        inside = (px >= x0) & (px < x1) & fg[iy, ix]
        w = facing ** cfg["facing_power"] * visible * inside
        c = bilinear(ref_img[..., :3], px, py)
        acc += c * w[:, None]
        wsum += w
        stats[view] = {"texels": int((w > 0.05).sum())}
    cov = np.clip(wsum / cfg["full_weight"], 0, 1)
    rgb = np.where(wsum[:, None] > 1e-6, acc / np.maximum(wsum, 1e-6)[:, None], fallback)
    rgb = rgb * cov[:, None] + fallback * (1 - cov[:, None])
    stats["coverage"] = round(float(cov.mean()), 3)
    return rgb, cov, stats


def painted_material(obj, image, name, unlit=False, uv_name="Paint"):
    """One material with the baked texture. unlit=True: texture -> Background shader -> output, which
    Blender's glTF exporter writes as KHR_materials_unlit (an Emission shader is exported as emissive
    instead). unlit=False: Principled BSDF, roughness 1, metallic 0. Every other UV layer is removed so
    the GLB carries exactly one TEXCOORD."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True  # closed shells: exported as doubleSided=false
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    tex.location = (-400, 0)
    if unlit:
        sh = nt.nodes.new("ShaderNodeBackground")
        nt.links.new(tex.outputs["Color"], sh.inputs["Color"])
    else:
        sh = nt.nodes.new("ShaderNodeBsdfPrincipled")
        sh.inputs["Roughness"].default_value = 1.0
        sh.inputs["Metallic"].default_value = 0.0
        nt.links.new(tex.outputs["Color"], sh.inputs["Base Color"])
    nt.links.new(sh.outputs[0], out.inputs["Surface"])
    mesh = obj.data
    for uv in [u for u in mesh.uv_layers if u.name != uv_name]:
        mesh.uv_layers.remove(uv)
    mesh.uv_layers.active = mesh.uv_layers[uv_name]
    mesh.uv_layers[uv_name].active_render = True
    mesh.materials.clear()
    mesh.materials.append(mat)
    return mat
