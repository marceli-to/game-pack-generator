"""Preview renders (STYLE.md §11): front / side (left) / back orthographic + 3/4 perspective."""
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

from . import scene as SC
from . import style as S


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _hex(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def world_bbox(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        ev = o.evaluated_get(dg)
        m = ev.to_mesh()
        pts.extend(ev.matrix_world @ v.co for v in m.vertices)
        ev.to_mesh_clear()
    if not pts:
        return Vector((0, 0, 0)), Vector((1, 1, 1))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def setup(size, light=None):
    sc = bpy.context.scene
    pv = S.load()["preview"]
    sc.render.engine = pv["engine"]
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.view_settings.view_transform = "Standard"
    exposure = pv.get("exposure", 0.0)   # brighter previews for styles lit like their sheet (lowpoly)
    sc.view_settings.exposure = exposure
    sh = sc.display.shading
    sh.light = light or pv.get("light", "STUDIO")
    if sh.light == "STUDIO" and pv.get("studio_light"):   # e.g. lowpoly: paint.sl (bright, saturated, like its sheet)
        sh.studio_light = pv["studio_light"]
    sh.color_type = "TEXTURE"
    sh.show_shadows = False
    sh.show_specular_highlight = False
    sh.show_cavity = False
    sh.show_object_outline = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("Preview")
    sc.world.color = [_srgb_to_linear(c) / 2 ** exposure for c in _hex(pv["background"])]  # background stays as given
    for img in bpy.data.images:  # nearest filtering in the viewport/workbench too
        pass


def _camera():
    cam = bpy.data.objects.get("PreviewCam")
    if cam is None:
        cam = bpy.data.objects.new("PreviewCam", bpy.data.cameras.new("PreviewCam"))
        bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


VIEWS = {
    # name: (direction from target to camera, perspective?)
    "front": (Vector((0, -1, 0)), False),
    "side": (Vector((1, 0, 0)), False),     # character's left side (+X)
    "back": (Vector((0, 1, 0)), False),
    "three_quarter": (Vector((-0.7, -1, 0.35)), True),  # front-right, slightly from above
    # props (STYLE.md §9b): held items lie along +X (muzzle), top +Z; named like the sheets' views
    "item_side": (Vector((0, -1, 0)), False),           # the item's right side, muzzle to the right
    "item_top": (Vector((0, 0, 1)), False),             # from above, muzzle to the right
    "item_front": (Vector((1, 0, 0)), False),           # into the muzzle
    "item_bottom": (Vector((0, 0, -1)), False),         # from below (e.g. the grenade sheet)
    "item_three_quarter": (Vector((0.8, -1, 0.55)), True),  # front right, from above
}


def render_views(out_dir, views=None, size=None, prefix="view", frame=None, light=None):
    """Render each view to out_dir/<prefix>_<view>.png and a sheet out_dir/<prefix>_sheet.png.

    frame: optional {"center": [x, y, z], "extent": metres} for a fixed framing (e.g. to match a
    reference image's scale); default fits the bounding box. light: "STUDIO" (default) or "FLAT"."""
    pv = S.load()["preview"]
    size = size or pv["view_size"]
    views = views or pv["views"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    setup(size, light)
    cam = _camera()
    objs = SC.meshes()
    lo, hi = world_bbox(objs)
    center = (lo + hi) / 2
    extent = max((hi - lo).x, (hi - lo).y, (hi - lo).z) * 1.12
    if frame:
        center, extent = Vector(frame["center"]), frame["extent"]
    paths = []
    for v in views:
        d, persp = VIEWS[v]
        d = d.normalized()
        if persp:
            cam.data.type = "PERSP"
            cam.data.lens = 50
            fov = cam.data.angle
            dist = (extent / 2) / math.tan(fov / 2) * 1.05
        else:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = extent
            dist = extent * 3
        cam.data.clip_end = dist * 4
        cam.location = center + d * dist
        if abs(d.z) > 0.999:   # straight down: to_track_quat has no up reference (rolled 180 deg); +X right, +Y up
            cam.rotation_euler = (0.0, 0.0, 0.0) if d.z > 0 else (math.pi, 0.0, 0.0)
        else:
            cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        p = out_dir / f"{prefix}_{v}.png"
        bpy.context.scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        paths.append(str(p))
    sheet = out_dir / f"{prefix}_sheet.png"
    compose_row(paths, sheet, size)
    return paths, str(sheet)


def compose_row(paths, out, size):
    w, h = size * len(paths), size
    canvas = np.ones((h, w, 4), dtype=np.float32)
    for i, p in enumerate(paths):
        img = bpy.data.images.load(p)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], img.channels)
        if img.channels == 3:
            px = np.concatenate([px, np.ones(px.shape[:2] + (1,), dtype=np.float32)], axis=2)
        canvas[:, i * size:(i + 1) * size] = px
        bpy.data.images.remove(img)
    sheet = bpy.data.images.new("sheet", w, h, alpha=True)
    sheet.pixels = canvas.ravel()
    sheet.filepath_raw = str(out)
    sheet.file_format = "PNG"
    sheet.save()
    bpy.data.images.remove(sheet)


def load_rgba(path):
    """Image as a top-down H x W x 4 float array."""
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, img.channels)
    bpy.data.images.remove(img)
    if px.shape[2] == 3:
        px = np.concatenate([px, np.ones((h, w, 1), dtype=np.float32)], axis=2)
    return px[::-1].copy()


def save_rgba(arr, path):
    """Write a top-down H x W x 4 float array as PNG."""
    h, w = arr.shape[:2]
    img = bpy.data.images.new("out", w, h, alpha=True)
    img.pixels = np.ascontiguousarray(arr[::-1], dtype=np.float32).ravel()
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    return str(path)


def resample(arr, size):
    """Nearest-neighbour resample of a square H x W x C array to size x size."""
    h, w = arr.shape[:2]
    ys = (np.arange(size) * h / size).astype(int)
    xs = (np.arange(size) * w / size).astype(int)
    return arr[ys][:, xs]


def mask(arr, bg, threshold=0.12):
    """Foreground mask: pixels that differ from the background colour."""
    return np.abs(arr[..., :3] - np.asarray(bg, dtype=np.float32)[:3]).sum(axis=2) > threshold
