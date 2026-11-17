# Black gloves with fingers (tinfox, hero-m), fitted to specs/guard/reference: an oversized palm block ending at
# the knuckles, four thick fingers curling down in three faceted segments (relaxed, as on the sheet; the little
# finger shorter), a separate thumb forward, a short flared cuff over the wrist. (v1 was a mitten + thumb.)
wr = lm["wrist.l"]
z = wr.z - 0.004
palm = [(-0.005, 0.062, 0.05, 0.035), (0.02, 0.07, 0.056, 0.04), (0.098, 0.07, 0.054, 0.04), (0.118, 0.064, 0.046, 0.034)]
faces = P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, r, seg=2, axis="x") for dx, sy, sz, r in palm], "leather")
for y, s in ((-0.051, 1.0), (-0.017, 1.06), (0.017, 1.0), (0.05, 0.86)):
    k0 = Vector((wr.x + 0.1, y, z + 0.01))
    k1 = Vector((wr.x + 0.1 + 0.048 * s, y, z + 0.006))
    k2 = Vector((wr.x + 0.1 + 0.072 * s, y, z - 0.034 * s))
    k3 = Vector((wr.x + 0.1 + 0.052 * s, y, z - 0.068 * s))
    for a, b, r in ((k0, k1, 0.022), (k1, k2, 0.021), (k2, k3, 0.02)):
        faces += P.cylinder(a, b, r, n=6, role="leather")
tx, tz = wr.x + 0.045, z - 0.018
thumb = [(-0.04, 0.034, 0.03, 0.022), (-0.09, 0.034, 0.03, 0.022), (-0.112, 0.027, 0.024, 0.018),
         (-0.124, 0.014, 0.013, 0.009)]
faces += P.loft([P.rrect((tx, y, tz), sx, sz, r, seg=2, axis="y") for y, sx, sz, r in thumb], "leather")
faces += P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, 0.03, seg=1, axis="x")
                 for dx, sy, sz in ((-0.045, 0.068, 0.062), (-0.005, 0.075, 0.066), (0.012, 0.07, 0.06))], "leather")
P.mirror_x(faces)
