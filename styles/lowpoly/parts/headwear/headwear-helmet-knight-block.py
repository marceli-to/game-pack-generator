# Knight helmet (lowpoly chibi), fitted to specs/knight-lowpoly/reference: a wide low dome (8-sided chamfered
# rings) with a gold brow band and a gold V point at the front, a steel ridge up the front, one cheek-and-neck guard
# shell wrapped close round the face down to the jaw, and a big red brush crest (wider at the top) sweeping back.
def rr(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1)
# first ring: a flange that closes the rim in towards the forehead, so the band sits on the brow instead of
# showing its underside above the face
prof = [(0.978, 0.205, -0.193, 0.2, 0.08), (0.985, 0.262, -0.248, 0.248, 0.1), (0.993, 0.276, -0.262, 0.262, 0.105), (1.03, 0.276, -0.262, 0.262, 0.105),
        (1.04, 0.258, -0.248, 0.248, 0.1), (1.1, 0.24, -0.238, 0.238, 0.095), (1.16, 0.2, -0.2, 0.2, 0.08),
        (1.215, 0.138, -0.14, 0.14, 0.055), (1.245, 0.07, -0.07, 0.07, 0.03)]
P.loft([rr(*p) for p in prof], ["accent"] * 4 + ["metal"] * 4, cap_roles=("dark", "metal"))
# gold V point on the band
tri = lambda y: [Vector((-0.06, y, 1.025)), Vector((0.06, y, 1.025)), Vector((0, y, 1.085))]
P.loft([tri(-0.236), tri(-0.268)], "accent")
# ridge up the front of the dome
c = Vector((0, 0, 1.0))
path = [Vector((0, -0.246, 1.04)), Vector((0, -0.232, 1.1)), Vector((0, -0.195, 1.16)), Vector((0, -0.134, 1.215))]
P.sweep(path, P.strap_profile(0.05, 0.01, 0.004), "metal", [Vector((0, -1, 0.35)), Vector((0, -1, 0.6)),
        Vector((0, -1, 1.1)), Vector((0, -0.6, 1.4))])
# cheek + neck guard, plain steel: from the wearer's left cheek (46 deg, close to the face) round the back to the
# right cheek (314 deg), down to the jaw
rows = []
for z, r in ((0.99, 0.258), (0.9, 0.25), (0.81, 0.238)):
    rows.append([Vector((r * math.sin(math.radians(a)), -r * 0.93 * math.cos(math.radians(a)), z))
                 for a in (46 + 268 * k / 10 for k in range(11))])
P.shell(rows, 0.024, "metal")
# brush crest: sections along Y, narrow at the base and wide at the top (a rounded brush), sweeping back
def sec(y, lo, hi, w):
    h = hi - lo
    xz = [(0.45 * w, lo), (w, lo + 0.4 * h), (w, hi - 0.28 * h), (0.55 * w, hi), (-0.55 * w, hi), (-w, hi - 0.28 * h),
          (-w, lo + 0.4 * h), (-0.45 * w, lo)]
    return [Vector((x, y, z)) for x, z in xz]
st = [(-0.085, 1.22, 1.33, 0.06), (-0.03, 1.2, 1.41, 0.09), (0.05, 1.2, 1.44, 0.1), (0.14, 1.18, 1.43, 0.095),
      (0.23, 1.14, 1.37, 0.08), (0.31, 1.2, 1.28, 0.045)]
P.loft([sec(*t) for t in st], "secondary")
