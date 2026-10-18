"""v34: College of Science - the south complex and the garden walk to the north, from the aerial view (Google Maps
satellite, 2026-10-18) and the six TikTok videos (ChatGPT reference frames V01-V06).

Evidence grades used in the comments and in docs/science_v34_plan.md:
  A = seen in a reference (satellite / video frame), B = inferred with reasonable confidence, C = game addition.

  * A: the triangle ring belongs to the SOUTH complex; the garden with the winding paths lies NORTH of it, between the
       south complex ("Department of Biological Sciences", "Guidance") and the north block ("Male College of Science").
  * A: in the garden: a light curved path bending around a dark planted mound (west), a straight paved band along the
       north block's south edge, and a white faceted roof (Google label: health club / gym) in the centre-east.
  * B: the triangle is smaller than v33 drew it (its top edge stops well short of the north block), so the garden
       strip is ~55 studs deep instead of ~20.
  * A (V01/V03/V06): light silver upper facade with small perforations, cream columns with horizontal joints, dark
       green/blue glazing, horizontal louvres, revolving doors with side doors.
  * C: everything's exact size and position (no measured plan; the kuwaitservices floor maps are too low-res to read).
Never consumes the shared genmap RNG: the old garden walk and its decorations still run (muted) so every later random
placement stays where it was tested.
"""
import math
import random

import genmap as G
import genmap3 as C3
import genmap5 as C5
import bsc_art as A
import campus9
import ku_science as K
import ku_science33 as K33

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
R = random.Random(3434)   # private RNG (v34 only)

# ---------------------------------------------------------------- palette (A: V01, V03, V06 frames)
SILVER = (222, 224, 224)        # light silver/grey perforated envelope
SILVER_DK = (168, 172, 174)
PERF = (104, 110, 114)          # the small dark perforations
CREAM = (232, 222, 198)         # big cylindrical columns
CREAM_JOINT = (196, 184, 160)
GLASS_DARK = (62, 104, 104)     # dark glazing tinted green/blue
PAVE = [(150, 150, 146), (214, 204, 184), (176, 120, 96), (190, 186, 178)]   # grey, beige, reddish, light grey
WHITE_ROOF = (246, 246, 242)

# ---------------------------------------------------------------- top-down plan (campus coordinates, 1 stud ~ 0.4 m)
TRI = [(0.0, -24.0), (66.0, 62.0), (-66.0, 62.0)]   # B: smaller triangle, top edge z 62 (outer face z ~72)
GARDEN_Z = (74.0, 128.0)                             # B: the garden strip between the triangle and the north block
NORTH_FRONT = 130.0                                  # existing north building front (unchanged)
# main walk: south building back -> under the ring's west side -> courtyard -> under the top edge -> garden -> north
# v36 (user correction, 2026-10-18): the TRIANGLE is the gym. The white folded roof covers the triangle itself; there
# is no separate ring building and no separate garden pavilion. Walks therefore go AROUND the gym, out of the two back
# doors of the south building (x -50..-34 and 34..50, genmap5; the east one is half blocked by the PhotoShop kiosk at
# x 40..64, so the east walk uses x 34..40), and meet at the north entrance. Their exact line: C.
MAIN = [(37, -30), (40, -4), (60, 28), (76, 56), (66, 80), (40, 96), (16, 110), (4, 122), (0, 131)]       # east side
WEST = [(-40, -30), (-40, 0), (-42, 18), (-52, 32), (-66, 50), (-72, 66), (-68, 86), (-58, 104), (-36, 114),
        (-14, 119), (-2, 124)]   # west side, then the curved path round the planted mound (A) to the north entrance
PROMENADE = (-100.0, 104.0, 112.0, 128.0)           # A: wide paved band with potted trees along the north block
# Gym = the triangle (A: user). Outline vertices follow the rounded triangle TRI (x, z, eave y); ridges (x, z, y). The
# folds, eave heights and ridge heights are B/C (read off the oblique aerial view, no drawing). Kept below the Red
# Corridor (floor y 23) where the bridge passes over the gym's west part.
GYM_EDGE = [(-6, -16, 1), (6, -16, 3), (22, 6, 10), (40, 30, 2), (54, 48, 9), (62, 58, 3), (54, 62, 8), (30, 62, 2),
            (8, 62, 11), (-14, 62, 3), (-38, 62, 9), (-54, 62, 2), (-62, 58, 8), (-54, 48, 3), (-40, 30, 10), (-22, 6, 2)]
GYM_RIDGES = [(0, 10, 15), (18, 32, 23), (2, 50, 17), (-16, 36, 20)]   # south, east, north, west (angle order)
EAST_PLAZA = (66.0, 108.0, 76.0, 110.0)              # A: light paving with a loose grid of small trees east of the gym
MOUND = (-46.0, 98.0, 13.0)                          # A: dark planted mass the curved path bends around
PICK_AT = (106.0, -100.0)                            # C: Pick back at its pre-v33 place (the triangle is the gym)
NORTH_LINK = (0.0, 131.0)   # v36: the north entrance opening is x -8..8 (glass both sides, checked in Studio)                            # extendable connection point to the north building


def _paths():
    return [(C5._catmull(MAIN, 10), 12.0), (C5._catmull(WEST, 10), 10.0)]


def _muted(fn):
    """run fn for its RNG consumption only: everything it emits is dropped"""
    def w(*a, **k):
        n = len(G.buf)
        r = fn(*a, **k)
        del G.buf[n:]
        return r
    return w


def pre():
    """before ku_science33.install(): the smaller triangle and the Pick move; palette for ku_science (read at call time)"""
    K33.TRI[:] = TRI
    K33.central_ring = lambda: None        # v36: the triangle is the gym (gym() below), not a ring building
    K33.crossings_at = lambda x: []        # so the Red Corridor keeps its glass, mullions and columns everywhere
    K33.PICK_AT = PICK_AT
    K33.GARDEN_R = 12.0
    pts = []
    for path, _w in _paths():
        pts.extend(path)
    K33._garden_pts[:] = pts
    K.BRONZE, K.BRONZE_DK, K.CUT = SILVER, SILVER_DK, PERF
    K.COLUMN_WHITE, K.GLASS_BLUE = CREAM, GLASS_DARK


PERF_IMAGE = "rbxassetid://15484649855"   # free Creator Store image "peg board" (regular round holes), tiled as a Texture
PERF_TILE = 12.0


def _perforate(faces=(5, 2, 0, 3, 1)):
    """v35: the perforation is a tiled Texture on the screen part (5 textures instead of ~1000 cut-out parts)"""
    if not G.buf or not G.buf[-1].endswith("</Item>"):
        return
    tex = "".join(
        '<Item class="Texture" referent="%s"><Properties><string name="Name">Perforation</string>'
        '<Content name="Texture"><url>%s</url></Content><token name="Face">%d</token>'
        '<float name="StudsPerTileU">%s</float><float name="StudsPerTileV">%s</float>'
        '<Color3 name="Color3"><R>0.63</R><G>0.64</G><B>0.66</B></Color3></Properties></Item>'
        % (G.rid(), PERF_IMAGE, f, G.fl(PERF_TILE), G.fl(PERF_TILE)) for f in faces)
    G.buf[-1] = G.buf[-1][:-len("</Item>")] + tex + "</Item>"


SCREEN_NAMES = ("Screen", "ScreenBand", "ScreenSide", "ScreenSideAbove", "WingScreen", "WingScreenEnd", "ScreenCrown",
                "ScreenCrownSide", "WingFold", "ScreenEdge")
CUT_NAMES = ("ScreenCut", "ScreenStar", "ScreenStarCore")


def install():
    """after ku_science33.install()"""
    orig_vcyl, orig_disc, orig_glass_x, orig_rect = C5.vcyl, C5.disc, C5.glass_x, C5.rect
    C5.winding_garden = _muted(C5.winding_garden)
    C5.club_room = _muted(C5.club_room)   # v35: rebuilt in club_office() with a 12-stud balcony in front of it
    K33.place_names = lambda: None   # v34 draws the names itself (south complex, not the north block)
    campus9.garden_life = _muted(campus9.garden_life)

    def vcylh(name, cx, y0, y1, cz, diam, *a, **kw):
        if name == "BridgeCol" and C5._off[2] == 0.0 and in_gym(cx, cz, 2.0):
            return None   # v37: no columns through the gym roof; the corridor spans the gym on girders (bridge_girders)
        r = orig_vcyl(name, cx, y0, y1, cz, diam, *a, **kw)
        if name == "Column" and C5._off[2] == 0.0 and cz < -170 and diam >= 4.4:
            y = y0 + 3.2   # A (V03): cream columns with horizontal joints
            while y < y1 - 1.5:
                orig_disc("ColumnJoint", cx, y, cz, diam + 0.1, 0.16, CREAM_JOINT, "Concrete", collide=False, shadow=False)
                y += 3.2
        return r

    def glass_x(x0, x1, z, y0, y1, step=8.0, gaps=(), tr=0.55, col=C5.GLASS):
        if C5._off[2] == 0.0 and abs(z - (-160)) < 0.01 and y0 == 0:
            col, tr = GLASS_DARK, 0.45   # A: dark green/blue ground glazing of the south building
        return orig_glass_x(x0, x1, z, y0, y1, step, gaps, tr, col)

    def recth(name, x0, x1, y0, y1, z0, z1, col, mat="SmoothPlastic", **kw):
        if name in SCREEN_NAMES and C5._off[2] == 0.0:
            r = orig_rect(name, x0, x1, y0, y1, z0, z1, col, "Metal", **kw)
            _perforate()   # v35: small regular holes (V01) as a tiled texture instead of scattered cut-out parts
            return r
        return orig_rect(name, x0, x1, y0, y1, z0, z1, col, mat, **kw)

    def boxer(orig):
        def h(name, size, pos, color, mat="Plastic", **kw):
            if name in CUT_NAMES:
                return None   # v35: the scattered large diamonds / stars read as random, not as fine perforation
            if name in SCREEN_NAMES:
                r = orig(name, size, pos, color, "Metal", **kw)
                _perforate()
                return r
            return orig(name, size, pos, color, mat, **kw)
        return h

    K.box, K33.box = boxer(K.box), boxer(K33.box)
    C5.vcyl, C5.glass_x, C5.rect = vcylh, glass_x, recth


# ---------------------------------------------------------------- the garden walk
def _strip(path, width, name="Paver"):
    """a path of short paver bands in grey / beige / reddish, with low curbs"""
    for i, (a, b) in enumerate(zip(path, path[1:])):
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        if L < 0.1:
            continue
        yaw = math.degrees(math.atan2(dx, dz))
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        h = (math.sin(mx * 3.1 + mz * 1.7) + 1) / 2
        col = PAVE[int(h * 4) % 4] if i % 3 else PAVE[0]
        box(name, (width, 0.4, L + 1.0), (mx, 0.22, mz), col, "Slate", rot=(0, yaw, 0), collide=False)
        for s_ in (-1, 1):
            nx, nz = math.cos(math.radians(yaw)) * s_ * (width / 2 + 0.4), -math.sin(math.radians(yaw)) * s_ * (width / 2 + 0.4)
            box("Curb", (0.8, 0.7, L + 0.8), (mx + nx, 0.35, mz + nz), (218, 212, 198), "Concrete", rot=(0, yaw, 0),
                collide=False)


def _normal(path, i):
    a, b = path[i], path[min(i + 1, len(path) - 1)]
    if a == b:
        a = path[i - 1]
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dz) or 1
    return dx / L, dz / L, dz / L, -dx / L


def _near_any(x, z, d):
    for path, w in _paths():
        if any(math.hypot(px - x, pz - z) < d + w / 2 for px, pz in path):
            return True
    return False


def two_tier_planter(x, z, r=5.0):
    """B (V01, V03): stepped stone planters with shrubs and purple / yellow flowers"""
    disc("PlanterLow", x, 0.8, z, r * 2, 1.6, (222, 212, 192), "Limestone")
    disc("PlanterSoil", x, 1.62, z, r * 2 - 1, 0.1, (96, 76, 56), "Ground", collide=False)
    disc("PlanterHigh", x + 0.6, 2.2, z - 0.4, r * 1.1, 1.4, (212, 202, 182), "Limestone", collide=False)
    for q in range(6):
        a = q * math.pi / 3 + R.uniform(-0.2, 0.2)
        ball("PlanterShrub", x + math.cos(a) * r * 0.7, 2.6, z + math.sin(a) * r * 0.7, R.uniform(2.2, 3.2),
             (R.randint(70, 96), R.randint(124, 150), R.randint(66, 86)), "Grass", collide=False)
        ball("PlanterFlower", x + math.cos(a + 0.5) * r * 0.75, 3.4, z + math.sin(a + 0.5) * r * 0.75, 0.9,
             [(160, 100, 200), (250, 214, 80), (236, 120, 170)][q % 3], "SmoothPlastic", collide=False, shadow=False)
    ball("PlanterCrown", x + 0.6, 4.4, z - 0.4, 4.2, (64, 120, 70), "Grass", collide=False)


def rock_group(x, z, n=3):
    """A (V01): pale rocks between the shrubs"""
    for _ in range(n):
        g = R.randint(176, 210)
        ball("Rock", x + R.uniform(-3, 3), 0.9, z + R.uniform(-3, 3), R.uniform(2.2, 4.6), (g, g - 4, g - 10), "Slate",
             collide=False)


def bench(x, z, yaw):
    box("BenchSeat", (7, 0.5, 2.2), (x, 1.9, z), (150, 100, 62), "WoodPlanks", rot=(0, yaw, 0), collide=False)
    box("BenchBase", (6, 1.6, 1.4), (x, 0.9, z), (200, 196, 188), "Concrete", rot=(0, yaw, 0), collide=False)


def bollard(x, z):
    vcyl("PathBollard", x, 0, 2.0, z, 0.7, (64, 66, 70), "Metal", collide=False)
    ball("PathBollardLight", x, 2.2, z, 0.55, (255, 236, 200), "Neon", collide=False, shadow=False)


def mound():
    """A: the dark planted mound the west path bends around (dense shrubs, rocks, trees)"""
    mx, mz, r = MOUND
    with G.Group("GardenMound"):
        for k, (rr, y) in enumerate(((r, 0.6), (r * 0.72, 1.6), (r * 0.42, 2.5))):
            disc("MoundTier", mx, y, mz, rr * 2, 1.2, (82 - k * 6, 124 - k * 6, 72), "Grass", collide=False)
        for q in range(16):
            a = R.uniform(0, 2 * math.pi)
            d = R.uniform(2, r - 1.5)
            ball("MoundShrub", mx + math.cos(a) * d, 2.6, mz + math.sin(a) * d, R.uniform(2.6, 4.4),
                 (R.randint(54, 80), R.randint(104, 136), R.randint(56, 76)), "Grass", collide=False)
        for q in range(14):
            a = R.uniform(0, 2 * math.pi)
            ball("MoundFlower", mx + math.cos(a) * (r - 1.2), 1.6, mz + math.sin(a) * (r - 1.2), 1.0,
                 [(160, 100, 200), (250, 214, 80), (240, 240, 236)][q % 3], "SmoothPlastic", collide=False, shadow=False)
        rock_group(mx - 4, mz + 5, 4)
        rock_group(mx + 6, mz - 4, 3)
        K33.varied_tree(mx + 2, mz + 1, 1.2)
        K33.varied_tree(mx - 6, mz - 5, 1.0)


def _v(a, b):
    return (b[0] - a[0], b[1] - a[1], b[2] - a[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    L = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / L, a[1] / L, a[2] / L)


def _wedge(name, pos, size, right, up, back, color, mat, transp=0.0, collide=True):
    G.nparts[0] += 1
    m = (right[0], up[0], back[0], right[1], up[1], back[1], right[2], up[2], back[2])
    G.buf.append(
        '<Item class="WedgePart" referent="%s"><Properties><string name="Name">%s</string>'
        '<CoordinateFrame name="CFrame"><X>%s</X><Y>%s</Y><Z>%s</Z>' % (G.rid(), G.escape(name), G.fl(pos[0]), G.fl(pos[1]),
                                                                      G.fl(pos[2]))
        + "".join('<R%d%d>%s</R%d%d>' % (i // 3, i % 3, G.fl(m[i]), i // 3, i % 3) for i in range(9))
        + '</CoordinateFrame><Vector3 name="size"><X>%s</X><Y>%s</Y><Z>%s</Z></Vector3>' % (G.fl(size[0]), G.fl(size[1]),
                                                                                             G.fl(size[2]))
        + '<Color3uint8 name="Color3uint8">%d</Color3uint8><token name="Material">%d</token>' % (G.col32(color), G.MAT[mat])
        + '<bool name="Anchored">true</bool><bool name="CanCollide">%s</bool><bool name="CastShadow">true</bool>'
          '<float name="Transparency">%s</float><token name="TopSurface">0</token><token name="BottomSurface">0</token>'
          '</Properties></Item>' % ("true" if collide else "false", G.fl(transp)))


def triangle(name, a, b, c, color, mat="SmoothPlastic", th=0.6, transp=0.0, collide=True):
    """a flat triangle (a, b, c are (x, y, z)) from two WedgeParts"""
    ab, ac, bc = _v(a, b), _v(a, c), _v(b, c)
    abd, acd, bcd = _dot(ab, ab), _dot(ac, ac), _dot(bc, bc)
    if abd > acd and abd > bcd:
        a, c = c, a
    elif acd > bcd and acd > abd:
        a, b = b, a
    ab, ac, bc = _v(a, b), _v(a, c), _v(b, c)
    cr = _cross(ac, ab)
    if _dot(cr, cr) < 1e-4:
        return
    right = _unit(cr)
    up = _unit(_cross(bc, right))
    back = _unit(bc)
    h = abs(_dot(ab, up))
    if h < 0.05:
        return
    d1, d2 = abs(_dot(ab, back)), abs(_dot(ac, back))
    if d1 > 0.05:
        _wedge(name, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2), (th, h, d1), right, up, back, color, mat,
               transp, collide)
    if d2 > 0.05:
        neg = lambda v: (-v[0], -v[1], -v[2])   # noqa: E731
        _wedge(name, ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2, (a[2] + c[2]) / 2), (th, h, d2), neg(right), up, neg(back), color,
               mat, transp, collide)


def in_gym(x, z, m=0.0):
    """point inside the gym outline (grown by m)"""
    pts = [(px, pz) for (px, pz, _y) in GYM_EDGE]
    inside = False
    for i in range(len(pts)):
        (x1, z1), (x2, z2) = pts[i - 1], pts[i]
        if (z1 > z) != (z2 > z) and x < x1 + (z - z1) * (x2 - x1) / (z2 - z1):
            inside = not inside
    if inside or m <= 0:
        return inside
    for i in range(len(pts)):
        (x1, z1), (x2, z2) = pts[i - 1], pts[i]
        dx, dz = x2 - x1, z2 - z1
        t_ = max(0.0, min(1.0, ((x - x1) * dx + (z - z1) * dz) / (dx * dx + dz * dz)))
        if math.hypot(x - (x1 + dx * t_), z - (z1 + dz * t_)) < m:
            return True
    return False


def gym():
    """The gym: a closed white folded roof over the whole triangle (A: user correction; folds B/C). It comes down low
    at some eave points; dark glass fills under the higher eaves. Nothing inside is modelled and it is not enterable."""
    cx = sum(p[0] for p in GYM_EDGE) / len(GYM_EDGE)
    cz = sum(p[1] for p in GYM_EDGE) / len(GYM_EDGE)
    R = [(x, y, z) for (x, z, y) in GYM_RIDGES]
    ang = [math.atan2(r[2] - cz, r[0] - cx) for r in R]

    def nearest(mx, mz):
        a = math.atan2(mz - cz, mx - cx)
        return min(range(len(R)), key=lambda k: abs((a - ang[k] + math.pi) % (2 * math.pi) - math.pi))
    P = [(x, y, z) for (x, z, y) in GYM_EDGE]
    shades = [(248, 248, 244), (236, 238, 236), (244, 244, 240), (228, 230, 228)]
    with G.Group("Gym"):
        fan = [nearest((P[i][0] + P[(i + 1) % len(P)][0]) / 2, (P[i][2] + P[(i + 1) % len(P)][2]) / 2) for i in range(len(P))]
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            triangle("GymRoof", a, b, R[fan[i]], shades[i % 4])
            nxt = fan[(i + 1) % len(P)]
            if nxt != fan[i]:
                triangle("GymRoof", b, R[fan[i]], R[nxt], shades[(i + 1) % 4])
            if a[1] > 0.5 or b[1] > 0.5:   # dark tinted glass under the eave (opaque: the interior is not modelled)
                ga, gb = (a[0], 0.0, a[2]), (b[0], 0.0, b[2])
                triangle("GymGlass", ga, gb, b, (44, 70, 72), "Glass", th=0.3, transp=0.0)
                triangle("GymGlass", ga, b, a, (44, 70, 72), "Glass", th=0.3, transp=0.0)
        triangle("GymRoof", R[0], R[1], R[2], shades[0])
        triangle("GymRoof", R[0], R[2], R[3], shades[2])
        # invisible 20-stud fence along the outline (top stays under the Red Corridor floor, y 23; 9 studs was not enough:
        # the humanoid still hopped onto the 8-stud eave): the low eaves made the roof a ramp (tested: a humanoid walked up to
        # y 25), and nobody should be able to drop into the closed, unmodelled interior through a seam
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            dx, dz = b[0] - a[0], b[2] - a[2]
            L = math.hypot(dx, dz)
            yaw = math.degrees(math.atan2(dx, dz))
            nx, nz = dz / L, -dx / L   # outward for a clockwise-in-plan outline is checked below
            mx, mz = (a[0] + b[0]) / 2, (a[2] + b[2]) / 2
            if in_gym(mx + nx * 1.0, mz + nz * 1.0):
                nx, nz = -nx, -nz
            G.part("GymBoundary", (1.0, 20.0, L + 1.0), (mx + nx * 0.8, 10.0, mz + nz * 0.8), (255, 255, 255), "SmoothPlastic",
                   rot=(0, yaw, 0), transp=1.0, shadow=False)
        # the name on a low freestanding sign at the north side (the Google label: health club / gym)
        box("GymSign", (6.0, 3.2, 0.4), (20.0, 1.6, 66.5), (60, 70, 80), "SmoothPlastic", collide=False,
            text=dict(face="Back", text="صالة رياضية\nGym", color=(255, 255, 255), bg=(60, 70, 80), bg_t=0.0))


def garden_walk():
    with G.Group("GardenWalkV34"):
        for path, w in _paths():
            _strip(path, w)
        # A: wide paved band along the north block (alternating grey / beige courses) with trees in square planters
        x0, x1, z0, z1 = PROMENADE
        n = int((x1 - x0) / 4)
        for i in range(n):
            box("Promenade", (4.0, 0.4, z1 - z0), (x0 + 2 + i * 4, 0.22, (z0 + z1) / 2), PAVE[0] if i % 2 else PAVE[3], "Slate",
                collide=False)
        for x in range(-92, 101, 16):
            if -54 < x < -26 or abs(x - NORTH_LINK[0]) < 16:
                continue   # Red Corridor columns / the north entrance
            C5.rect("BandPlanter", x - 2.6, x + 2.6, 0, 1.6, 117.4, 122.6, (222, 212, 192), "Limestone")
            K33.varied_tree(x, 120.0, 0.9)
        # A: light paved plaza with a loose grid of small trees east of the gym
        ex0, ex1, ez0, ez1 = EAST_PLAZA
        for i in range(int((ex1 - ex0) / 6)):
            box("EastPaving", (6.0, 0.4, ez1 - ez0), (ex0 + 3 + i * 6, 0.22, (ez0 + ez1) / 2), PAVE[1] if i % 2 else PAVE[3],
                "Slate", collide=False)
        for x in (74, 88, 102):
            for z in (84, 98):
                disc("TreeGrate", x + (z % 7), 0.45, z, 4.4, 0.1, (90, 90, 92), "Metal", collide=False)
                K33.varied_tree(x + (z % 7), z, 0.8)
        mound()
        gym()
        # lamp posts along the main walk + low bollards along the curved path (A: low lighting and lamp posts)
        main = C5._catmull(MAIN, 10)
        for i in range(4, len(main) - 2, 9):
            fx, fz, nx, nz = _normal(main, i)
            s_ = 1 if (i // 9) % 2 else -1
            lx, lz = main[i][0] + nx * s_ * 8.5, main[i][1] + nz * s_ * 8.5
            if not in_gym(lx, lz, 3):
                C3.lamp_post(lx, 0, lz, 11)
        arc = [q for q in C5._catmull(WEST, 10) if q[1] > 70]   # the curved stretch round the mound
        for i in range(2, len(arc) - 1, 5):
            fx, fz, nx, nz = _normal(arc, i)
            for s_ in (-1, 1):
                bollard(arc[i][0] + nx * s_ * 5.6, arc[i][1] + nz * s_ * 5.6)
        # A (satellite): the west half is a dense dark-green planted mass between the paths; lighter to the east
        for q in range(150):
            x, z = R.uniform(-104, 64), R.uniform(GARDEN_Z[0] + 2, PROMENADE[2] - 2)
            if _near_any(x, z, 2.5) or in_gym(x, z, 4) or math.hypot(x - MOUND[0], z - MOUND[1]) < MOUND[2]:
                continue
            if math.hypot(x + 15, z - 80) < 8:
                continue   # keep the department sign readable from the garden
            if -52 < x < -28 and (abs(z - 84) < 3 or abs(z - 120) < 3):
                continue   # Red Corridor columns
            if x > 0 and q % 2:
                continue   # sparser east of the main walk
            kind = q % 6
            if kind == 0:
                K33.varied_tree(x, z, R.uniform(0.8, 1.2))
            elif kind == 5:
                rock_group(x, z, 2)
            else:
                for _ in range(3):
                    ball("GardenShrub", x + R.uniform(-2.5, 2.5), 1.4, z + R.uniform(-2.5, 2.5), R.uniform(2.6, 4.4),
                         (R.randint(46, 76), R.randint(96, 132), R.randint(52, 72)), "Grass", collide=False)
                if kind == 1:
                    for _ in range(3):
                        ball("GardenBloom", x + R.uniform(-3, 3), 2.6, z + R.uniform(-3, 3), 0.9,
                             [(160, 100, 200), (250, 214, 80), (236, 120, 170)][R.randint(0, 2)], "SmoothPlastic",
                             collide=False, shadow=False)
        for (x, z, yaw) in ((-26, 104, 90), (-60, 88, 45), (-84, 104, 0)):
            if not _near_any(x, z, 1.5):
                bench(x, z, yaw)
        # cats + memory notes along the main walk (moved from the old walk; user memories, private RNG)
        for n, i in enumerate(range(8, len(main) - 4, 14)):
            fx_, fz_, nx, nz = _normal(main, i)
            s_ = -1 if main[i][1] > 70 else (1 if n % 2 else -1)   # in the garden: west of the walk (the gym is east)
            cx, cz = main[i][0] + nx * s_ * 9.0, main[i][1] + nz * s_ * 9.0
            if in_gym(cx, cz, 3):
                cx, cz = main[i][0] - nx * s_ * 9.0, main[i][1] - nz * s_ * 9.0
            A.cat(cx, 0.2, cz, math.degrees(math.atan2(-nx * s_, -nz * s_)), ["sit", "loaf", "walk"][n % 3])
            A.cat_bowl(cx - fx_ * 2.6, 0.2, cz - fz_ * 2.6)
        for n, i in enumerate(range(5, len(main) - 3, 10)):
            if n >= len(campus9.WALK_NOTES):
                break
            fx_, fz_, nx, nz = _normal(main, i)
            s_ = -1 if (main[i][1] > 70 or n % 2) else 1
            sx, sz = main[i][0] + nx * s_ * 8.4, main[i][1] + nz * s_ * 8.4
            if in_gym(sx, sz, 3):
                sx, sz = main[i][0] - nx * s_ * 8.4, main[i][1] - nz * s_ * 8.4
            yaw = math.degrees(math.atan2(fx_, fz_))
            vcyl("NotePost", sx, 0, 6, sz, 0.5, (90, 70, 50), "Wood", collide=False)
            for face in ("Back", "Front"):
                G.part("WalkNote", (9, 3.2, 0.3), (sx, 7.4, sz), (250, 246, 236), "SmoothPlastic", rot=(0, yaw, 0),
                       collide=False, text=dict(face=face, text=campus9.WALK_NOTES[n], color=(50, 40, 30), bg=(250, 246, 236),
                                                bg_t=0.0))
        north_link()


def north_link():
    """an extendable joint to the north building: small paved forecourt, a direction sign and a named anchor part"""
    x, z = NORTH_LINK
    box("NorthForecourt", (24, 0.4, 8), (x, 0.24, z - 6), PAVE[1], "Slate", collide=False)
    G.part("Connect|North", (12, 1, 2), (x, 0.5, z - 1), (255, 255, 255), "SmoothPlastic", transp=1.0, collide=False,
           shadow=False)
    vcyl("WaySignPost", x + 9, 0, 9, z - 8, 0.6, (40, 44, 50), "Metal", collide=False)
    # A (V03): dark vertical wayfinding sign with a yellow stripe
    box("WaySign", (3.2, 7, 0.4), (x + 9, 5, z - 8), (36, 40, 46), "SmoothPlastic", collide=False,
        text=dict(face="Front", text="↑\nالمبنى الشمالي\nNorth Building", color=(255, 255, 255), bg=(36, 40, 46), bg_t=0.0))
    box("WaySignStripe", (3.2, 0.5, 0.45), (x + 9, 1.9, z - 8), (240, 196, 40), "SmoothPlastic", collide=False)


# ---------------------------------------------------------------- names on the south complex
def place_names():
    """A: the map labels "Department of Biological Sciences" and "Guidance" sit on the south complex at the garden's
    south-west (not on the north block, as v33 had it). v35: the ring's outer face is an open colonnade / rail, so a
    sign there floated in the air: the department name is a freestanding wayfinding sign (dark, yellow stripe: V03) at
    the triangle's north edge (B). "Guidance" is dropped: its block lies WEST of the triangle and is not built (no
    reference for its shape). Physics stays on the south back.
    v36: the department sign is removed too: standing at the triangle it now labelled the gym, and the department's own
    block (west of the triangle) is not built yet."""
    with G.Group("PlaceNames"):
        sign("DeptPhysics", "قسم الفيزياء | Department of Physics", (40, 16, -29.4), (30, 3, 0.4), "Back", bg=(40, 50, 90))


# ---------------------------------------------------------------- south building facade + lobby details
def facade_details():
    """A (V03): side doors beside the revolving door; round lights in the white soffit; B: deep overhang edge"""
    with G.Group("SouthFacadeV34"):
        zw = -160.0
        for x in (-17.0, 17.0):   # side swing doors (glass in a dark metal frame), open so players pass
            C5.rect("SideDoorFrame", x - 3, x + 3, 10, 10.6, zw - 0.3, zw + 0.3, (60, 64, 70), "Metal", collide=False)
            for e in (-3, 3):
                C5.rect("SideDoorFrame", x + e - 0.3, x + e + 0.3, 0, 10.6, zw - 0.3, zw + 0.3, (60, 64, 70), "Metal",
                        collide=False)
            sign("SideDoorSign", "↔", (x, 11.6, zw - 0.5), (2, 1.2, 0.2), "Front", bg=(60, 64, 70))
        disc("RevolvingCrown", 0, 12.4, zw, 13, 1.0, (200, 204, 208), "Metal", collide=False)   # A: silver crown
        for x in range(-81, 82, 18):   # round lights between the colonnade columns
            for z in (-174.0, -166.0):
                disc("SoffitLight", x + 9, 22.9, z, 2.6, 0.15, (255, 246, 226), "SmoothPlastic", collide=False, shadow=False)
        C5.rect("OverhangEdge", -92, 92, 22.2, 24.6, -180.6, -179.6, (236, 236, 232), "SmoothPlastic", collide=False)


def lobby_details():
    """A (V02, V04): white ceiling with round lights, silver columns with dark bands (already there), seating islands"""
    with G.Group("LobbyV34"):
        for x in range(-48, 49, 16):
            for z in (-154, -140, -126, -112):
                disc("RoundLight", x, 38.6, z, 3.0, 0.2, (255, 248, 232), "SmoothPlastic", collide=False, shadow=False)
        for (x, z, col) in ((-24, -112, (70, 120, 170)), (24, -112, (200, 70, 60))):   # round tables with chairs
            C5.table_set(x, z, 0, 4, seat_cols=[col, (240, 190, 60)])


# ---------------------------------------------------------------- the BSC club office (one room in the south building)
def club_office():
    """The BSC office as ONE room on the mezzanine where earlier versions put office 088 (number + floor from the
    user's memory; position NOT verified with a plan: grade C). Contents follow the user's description (A).
    v35: the room starts at x 68 (was 62), so the balcony in front of the door is 12 studs wide instead of 6; heights
    follow the campus furniture (tables 3.4, seats 2) so the character fits the desk."""
    y = C5.Y_M
    x0, x1, z0, z1 = 68.0, 90.0, -160.0, -128.0
    H = 11.5
    wallc = (236, 232, 222)
    door = (-148.0, -141.0)
    side = (-139.6, -136.6)
    win = (-142.0, -130.0)
    with G.Group("BSCOffice"):
        C5.rect("RoomFloor", x0, x1, y, y + 0.25, z0, z1, C5.CARPET, "Fabric", collide=False)
        C5.wall_x(x0, x1, z0, y, y + H, wallc, "Concrete")
        C5.wall_x(x0, x1, z1, y, y + H, wallc, "Concrete")
        C5.wall_z(z0, z1, x0, y, y + H, wallc, "Concrete", gaps=[door, side])
        C5.wall_z(z0, z1, x1, y, y + H, wallc, "Concrete", gaps=[win])
        C5.light_panel(79, y + H - 0.4, -144, 10, 5, 1.0, 26)
        # wooden door (open, against the inside wall) + glass side panel; name plate outside
        for zz in door:
            C5.rect("DoorFrame", x0 - 0.5, x0 + 0.5, y, y + 9.0, zz - 0.3, zz + 0.3, (160, 106, 60), "Wood", collide=False)
        box("WoodDoor", (6.4, 8.6, 0.35), (x0 + 3.4, y + 4.3, door[0] + 0.4), (160, 106, 60), "WoodPlanks", collide=False)
        box("DoorHandle", (0.3, 0.3, 0.8), (x0 + 6.0, y + 4.2, door[0] + 0.7), (200, 200, 204), "Metal", collide=False)
        C5.rect("SidePanelGlass", x0 - 0.15, x0 + 0.15, y, y + 9.0, side[0], side[1], (190, 220, 226), "Glass", transp=0.45)
        C5.rect("SidePanelFrame", x0 - 0.5, x0 + 0.5, y, y + 9.0, side[1] - 0.3, side[1] + 0.3, (160, 106, 60), "Wood",
                collide=False)
        sign("Plate", "088\nنادي العلوم البيولوجية", (x0 - 0.7, y + 10.0, -144.5), (0.3, 1.6, 6), "Left", bg=(50, 50, 56))
        # large window onto the east lawn
        C5.rect("WindowSill", x1 - 0.6, x1 + 0.6, y, y + 3.0, win[0], win[1], (226, 222, 212), "Concrete")
        C5.rect("WindowGlass", x1 - 0.1, x1 + 0.1, y + 3.0, y + 9.0, win[0], win[1], (190, 220, 226), "Glass", transp=0.5)
        for zz in (win[0], (win[0] + win[1]) / 2, win[1]):
            C5.rect("WindowMullion", x1 - 0.3, x1 + 0.3, y + 3.0, y + 9.0, zz - 0.2, zz + 0.2, (60, 64, 70), "Metal",
                    collide=False)
        # large wooden desk (facing the door) + mesh office chair behind it
        C5.rect("Desk", 76, 80, y + 3.0, y + 3.4, -156, -144, (158, 110, 70), "Wood")
        C5.rect("DeskBody", 78.6, 80, y, y + 3.0, -156, -144, (120, 84, 54), "Wood")
        C5.rect("DeskDrawers", 76.2, 78.6, y, y + 3.0, -156, -152, (130, 92, 60), "Wood", collide=False)
        cx, cz = 82.6, -150.0
        for q in range(5):
            a = q * 72
            box("ChairStar", (0.35, 0.25, 2.0), (cx + math.sin(math.radians(a)) * 0.9, y + 0.4,
                                                 cz + math.cos(math.radians(a)) * 0.9), (30, 30, 34), "Metal",
                rot=(0, a, 0), collide=False)
        vcyl("ChairLift", cx, y + 0.4, y + 1.7, cz, 0.45, (90, 90, 96), "Metal", collide=False)
        box("ChairSeat", (2.4, 0.5, 2.4), (cx, y + 1.95, cz), (34, 34, 38), "Fabric", collide=False)
        box("ChairMesh", (0.3, 3.2, 2.2), (cx + 1.25, y + 3.9, cz), (24, 24, 28), "Fabric", transp=0.25, collide=False,
            rot=(0, 0, 8))
        for s_ in (-1, 1):
            box("ChairArm", (1.8, 0.25, 0.35), (cx, y + 2.9, cz + s_ * 1.2), (30, 30, 34), "SmoothPlastic", collide=False)
        box("Monitor", (0.3, 2.0, 3.2), (79.2, y + 4.6, -151), (24, 24, 28), "SmoothPlastic", collide=False)
        box("Papers", (1.8, 0.12, 2.4), (77.4, y + 3.47, -145.4), (250, 250, 246), "SmoothPlastic", collide=False)
        vcyl("PenCup", 77.2, y + 3.4, y + 4.3, -154.5, 0.6, (24, 80, 56), "SmoothPlastic", collide=False)
        # wooden cabinets + shelves with binders on the south wall
        C5.rect("Cabinet", 70, 80, y, y + 3.6, z0 + 0.5, z0 + 2.7, (150, 104, 66), "Wood")
        for xx in range(70, 81, 2):
            box("CabinetLine", (0.12, 3.2, 0.1), (xx, y + 1.8, z0 + 2.75), (110, 76, 48), "Wood", collide=False)
        for k in range(3):
            C5.rect("WallShelf", 70, 80, y + 5.2 + k * 1.9, y + 5.45 + k * 1.9, z0 + 0.5, z0 + 2.1, (160, 112, 70), "Wood",
                    collide=False)
            for q in range(5):
                box("Binder", (0.9, 1.5, 1.4), (71 + q * 2.0 + k * 0.5, y + 6.25 + k * 1.9, z0 + 1.3),
                    [(24, 80, 56), (230, 230, 226), (200, 70, 60), (70, 110, 190), (240, 190, 60)][(q + k) % 5],
                    "SmoothPlastic", collide=False)
        # tall shelf on the east wall (south of the window) with the club trophy
        C5.rect("ShelfBack", x1 - 0.8, x1 - 0.5, y, y + 8.5, -158.5, -146.5, (130, 90, 58), "Wood")
        for zz in (-158.5, -146.5):
            C5.rect("ShelfSide", x1 - 2.7, x1 - 0.5, y, y + 8.5, zz - 0.15, zz + 0.15, (150, 104, 66), "Wood")
        for k in range(0, 5):
            C5.rect("ShelfBoard", x1 - 2.7, x1 - 0.5, y + k * 2.1, y + k * 2.1 + 0.2, -158.5, -146.5, (176, 126, 82), "Wood",
                    collide=False)
        for k in range(1, 3):
            for q in range(4):
                box("ShelfBook", (1.2, 1.5, 0.8), (x1 - 1.7, y + k * 2.1 + 0.95, -157.4 + q * 1.1 + k * 0.4),
                    [(24, 80, 56), (200, 70, 60), (70, 110, 190), (240, 190, 60)][(q + k) % 4], "SmoothPlastic", collide=False)
        box("Trophy", (1.0, 1.8, 1.0), (x1 - 1.5, y + 7.3, -152), (232, 184, 56), "SmoothPlastic", collide=False)
        # mirror with a wavy frame (east wall between shelf and window)
        mx, my, mz = x1 - 0.6, y + 6.0, -144.3
        box("Mirror", (0.15, 3.8, 1.8), (mx, my, mz), (220, 232, 236), "Glass", collide=False,
            extra='<float name="Reflectance">0.6</float>')
        for q in range(24):
            a = q * 2 * math.pi / 24
            rr = 1.0 + 0.16 * math.sin(6 * a)
            ball("MirrorWave", mx - 0.1, my + math.sin(a) * 2.2 * rr, mz + math.cos(a) * 1.2 * rr, 0.45, (214, 170, 96),
                 "SmoothPlastic", collide=False, shadow=False)
        # science boards and posters. The DNA board from the earlier office hangs on the west wall: on the north wall
        # the default camera sat inside its helix balls (seen in a play capture)
        box("DNABoard", (0.4, 7, 8), (x0 + 0.3, y + 5.6, -155.0), (248, 248, 246), "SmoothPlastic", collide=False)
        for q in range(18):
            a = q * 0.55
            ball("A", x0 + 0.7, y + 2.6 + q * 0.32, -155.0 + math.sin(a) * 2.4, 0.5, (255, 90, 170), "SmoothPlastic",
                 collide=False, shadow=False)
            ball("B", x0 + 0.7, y + 2.6 + q * 0.32, -155.0 - math.sin(a) * 2.4, 0.5, (60, 200, 240), "SmoothPlastic",
                 collide=False, shadow=False)
        box("Poster", (4.4, 5.6, 0.2), (x0 + 13.5, y + 6.2, z1 - 0.65), (70, 110, 190), "SmoothPlastic", collide=False,
            text=dict(face="Front", text="🔬 الخلية\nThe Cell", color=(255, 255, 255), bg=(70, 110, 190), bg_t=0.0))
        box("Poster", (4.4, 5.6, 0.2), (x0 + 6.5, y + 6.2, z1 - 0.65), (240, 236, 226), "SmoothPlastic", collide=False,
            text=dict(face="Front", text="🌿 علم النبات\nPlant Biology", color=(40, 60, 40), bg=(240, 236, 226), bg_t=0.0))
        box("Poster", (0.2, 4.6, 5.2), (x0 + 0.65, y + 6.2, -132.5), (24, 80, 56), "SmoothPlastic", collide=False,
            text=dict(face="Right", text="🧬 فعاليات النادي\nBSC Events", color=(255, 255, 255), bg=(24, 80, 56), bg_t=0.0))
        # storage + office items (north-west corner, clear of the door swing and the HQ portal at x 85)
        for q in range(3):
            box("StorageBox", (2.6, 1.8, 2.6), (x0 + 2.0, y + 0.9 + q * 1.8, z1 - 3.0 + (q % 2) * 0.3), (190, 150, 100),
                "SmoothPlastic", collide=False)
        box("OrangeDisplay", (4.0, 2.6, 2.6), (x0 + 6.0, y + 1.3, z1 - 2.0), (232, 104, 40), "SmoothPlastic", collide=False)
        vcyl("WaterBottle", x0 + 10, y, y + 3.6, z1 - 2.0, 1.2, (150, 200, 230), "Glass", transp=0.3, collide=False)
        vcyl("PlantPot", x1 - 2.2, y, y + 1.8, -139.0, 1.8, (230, 230, 226), "SmoothPlastic", collide=False)
        ball("Plant", x1 - 2.2, y + 3.0, -139.0, 3.0, (70, 140, 80), "Grass", collide=False)
        # outside: the cartoon scientist holding the BSC logo at the balcony's quiet south end, facing the walkway
        G.mascot(62.5, y, -156.0)
        A.logo_board(62.5, y + 7.0, -153.8, R=0.5, nx=0.0, nz=1.0)
        sign("Discord", "انضموا لمجتمعنا على ديسكورد\ndiscord.gg/8hw9hBn27", (x0 - 0.35, y + 6.0, -132.5), (0.3, 3.6, 6.4),
             "Left", bg=(88, 101, 242))


def step_ramps():
    """the mezzanine access steps (genmap5, 2-stud risers) need a jump: an invisible ramp over them lets players walk up
    (tested: a humanoid MoveTo stalled on the first riser)"""
    for sx in (-73.0, 73.0):
        zs, ze, rise = -92.0, -92.0 - 6 * 2.2, C5.Y_M
        L = math.hypot(ze - zs, rise)
        ang = math.degrees(math.atan2(rise, zs - ze))
        G.part("StepRamp", (8, 0.6, L + 0.6), (sx, rise / 2 + 0.3, (zs + ze) / 2), (226, 222, 212), "SmoothPlastic",
               rot=(ang, 0, 0), transp=1.0, shadow=False)


def bridge_girders():
    """v37: the Red Corridor crosses the gym's west part. Its columns inside the gym outline are dropped (they pierced
    the roof); two deep edge girders carry the floor from the last column south of the gym (z 12) to the first north of
    it (z 84). Their underside (y 20.6) stays above the gym roof there (max ~17 at x -31)."""
    with G.Group("BridgeGirders"):
        for x in (-48.0, -32.0):
            C5.rect("BridgeGirder", x - 1.1, x + 1.1, 20.6, 23.0, 12.0, 84.0, C5.CREAM, "Concrete")


def build():
    step_ramps()
    bridge_girders()
    garden_walk()
    place_names()
    facade_details()
    lobby_details()
    club_office()
