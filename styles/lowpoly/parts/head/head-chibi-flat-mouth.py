# Chibi head (lowpoly) with a stern flat mouth: head-chibi-small-ears with the smile replaced by a short straight line
# (the shieldbearer sheet: "a stern flat mouth", no brows). Ears as on head-chibi-small-ears (hidden under helmets).
z0, z1 = lm["head_base"].z, lm["head_top"].z
# (z, half width, front y, back y, corner chamfer)
prof = [(z0, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (z1, 0.12, -0.11, 0.11, 0.05)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1) for z, sx, f, b, r in prof], "skin")
eye = P.loft([P.ring((0.075, -0.166, 0.965), 0.019, 0.034, n=8, axis="y"),
              P.ring((0.075, -0.186, 0.965), 0.019, 0.034, n=8, axis="y")], "eyes")
P.mirror_x(eye)
xs = [-0.026, 0.0, 0.026]
P.sweep([Vector((x, -0.181, 0.905)) for x in xs], P.strap_profile(0.01, 0.006, 0.002),
        "eyes", [Vector((0, -1, 0))] * len(xs))
# ear (as on the healer sheet): a flat rounded D-shaped plate lying against the side of the head, taller than wide,
# rounded at the back, straighter at the front; outer face bevelled with a shallow inner fold. From the front only
# its thin edge shows as a small bump beside the cheek; from the side it reads as a full ear in front of the hair.
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
