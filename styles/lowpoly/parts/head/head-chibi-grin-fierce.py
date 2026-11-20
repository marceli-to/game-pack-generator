# Chibi head (lowpoly) with a fierce open grin, from specs/berserker/reference: head-chibi-flat-mouth's head, eyes and
# ears; thick angry brows (hair colour) sloping down to the nose; an open grin (dark D-shaped mouth, a white top row of
# teeth with two fangs), sitting between the moustache and the beard (face slot); two war-paint stripes on each cheek
# (`primary`, the team cell: blue on the enemy side, as on the sheet), inner end lower, running onto the cheek facet.
z0, z1 = lm["head_base"].z, lm["head_top"].z
# (z, half width, front y, back y, corner chamfer)
prof = [(z0, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (z1, 0.12, -0.11, 0.11, 0.05)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1) for z, sx, f, b, r in prof], "skin")
def dims(z):
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a[1:], b[1:])]
def face(x, z, out=0.0):
    """point on the head's front (flat face + corner chamfer) at x, z, pushed `out` along the facet normal"""
    sx, f, b, r = dims(z)
    e = abs(x) - (sx - r)
    if e <= 0:
        return Vector((x, f - out, z)), Vector((0, -1, 0))
    n = Vector((math.copysign(1, x), -1, 0)).normalized()
    return Vector((x, f + e, z)) + n * out, n
eye = P.loft([P.ring((0.075, -0.166, 0.965), 0.019, 0.034, n=8, axis="y"),
              P.ring((0.075, -0.186, 0.965), 0.019, 0.034, n=8, axis="y")], "eyes")
P.mirror_x(eye)
# brows: thick wedges, inner end low (angry), hair colour
bp = [(0.035, 1.0), (0.075, 1.016), (0.112, 1.03)]
brow = P.sweep([face(x, z, 0.002)[0] for x, z in bp], P.strap_profile(0.024, 0.012, 0.004), "hair",
               [face(x, z)[1] for x, z in bp])
P.mirror_x(brow)
# open grin: a dark D (flat top, round bottom) standing 4 mm proud of the face
zt, zb, hw = 0.877, 0.832, 0.068
D = [(-hw, zt), (hw, zt), (hw * 0.9, zt - 0.018), (hw * 0.6, zb + 0.006), (0.0, zb), (-hw * 0.6, zb + 0.006),
     (-hw * 0.9, zt - 0.018)]
f = dims(0.855)[1]
P.loft([[Vector((x, f + 0.01, z)) for x, z in D], [Vector((x, f - 0.004, z)) for x, z in D]], "eyes")
# top teeth: a white bar under the top edge, two fangs pointing down near the corners
P.rbox((-hw * 0.82, f - 0.008, zt - 0.016), (hw * 0.82, f + 0.004, zt - 0.002), "accent", r=0.003, bevel=0, seg=1,
       axis="y")
for s in (1, -1):
    xf = s * hw * 0.55
    P.loft([[Vector((xf - 0.011, f - 0.008, zt - 0.014)), Vector((xf + 0.011, f - 0.008, zt - 0.014)),
             Vector((xf, f + 0.004, zt - 0.014))], [Vector((xf, f - 0.006, zt - 0.034))]], "accent")
# war paint: two stripes per cheek, from beside the nose up and out onto the cheek facet
for dz in (0.0, -0.028):
    pts = [(0.09, 0.906 + dz), (0.125, 0.918 + dz), (0.165, 0.932 + dz)]
    st = P.sweep([face(x, z, 0.001)[0] for x, z in pts], P.strap_profile(0.012, 0.004, 0.001), "primary",
                 [face(x, z)[1] for x, z in pts])
    P.mirror_x(st)
# ear (as on head-chibi-small-ears): a flat rounded D-shaped plate lying against the side of the head
c = Vector((0.0, 0.004, 0.935))
D = [(-0.03, 0.0), (-0.026, 0.03), (-0.008, 0.046), (0.016, 0.042), (0.031, 0.022), (0.035, -0.004),
     (0.026, -0.03), (0.006, -0.046), (-0.016, -0.04), (-0.028, -0.022)]   # (y, z) outline, front at -y
def ering(x, s, dy=0.0, dz=0.0):
    return [Vector((x, c.y + dy + 1.2 * y * s, c.z + dz + 1.2 * z * s)) for y, z in D]
ear = P.loft([ering(0.175, 0.92), ering(0.22, 1.0), ering(0.232, 0.86), ering(0.23, 0.5, 0.004, -0.004),
              [Vector((0.222, c.y + 0.004, c.z - 0.004))]], "skin")
tilt = Matrix.Translation(c + Vector((0.2, 0, 0))) @ Matrix.Rotation(math.radians(-10), 4, "X") \
    @ Matrix.Translation(-(c + Vector((0.2, 0, 0))))
P.transform(ear, tilt)
P.mirror_x(ear)
