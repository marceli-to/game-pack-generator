# Dwarf hair (lowpoly, dwarf archetype): a ginger sheet behind the ears from under the helmet rim to the nape.
rows = []
for z, r in ((0.79, 0.285), (0.69, 0.295), (0.6, 0.27)):
    rows.append([Vector((r * math.sin(math.radians(a)), -r * 0.88 * math.cos(math.radians(a)) + 0.02, z))
                 for a in (105, 130, 155, 180, 205, 230, 255)])
P.shell(rows, 0.03, "hair")
