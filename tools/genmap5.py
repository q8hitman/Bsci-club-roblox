"""Campus v2 (bright, multi-floor) + course. Floors: G=0, M=12, 1=24, 2=40, 3=56, 4=72, roof=88.

South building (114): x[-90,90] z[-178,-30]; north building (113): x[-80,100] z[20,150].
Run: python tools/genmap5.py kuwait-parkour/src/map/Map.rbxmx
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap3 as C3  # noqa: E402
import genmap2 as M2  # noqa: E402
import genmap as G  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rng = random.Random(113114)

# ---- palette (bright, warm)
WHITE = (243, 241, 235)
TERRAZZO = (236, 232, 222)
CREAM = (232, 222, 200)
PANEL = (206, 199, 187)
HOLE = (104, 112, 118)  # v30: perforation shadow (was bright white)
GLASS = (176, 214, 220)
GLASS_DK = (96, 150, 160)
TIMBER = (186, 140, 92)
RED_TILE = (162, 80, 62)
SILVER = (170, 174, 180)
STEEL = (118, 124, 132)
CARPET = (122, 112, 104)
WARM = (255, 240, 205)
Y_G, Y_M, Y_1, Y_2, Y_3, Y_4, Y_ROOF = 0.0, 12.0, 24.0, 40.0, 56.0, 72.0, 88.0
LEVELS = [Y_G, Y_1, Y_2, Y_3, Y_4]
COURSE_OFFSET = (12000.0, 0.0, 0.0)   # far away: not visible from the campus
NB_SHIFT = 110.0   # north building sits this far north so the garden walk can wind

_base_part = G.part
_off = [0.0, 0.0, 0.0]


def _offset_part(name, size, pos, *a, **k):
    return _base_part(name, size, (pos[0] + _off[0], pos[1] + _off[1], pos[2] + _off[2]), *a, **k)


G.part = _offset_part


def rect(name, x0, x1, y0, y1, z0, z1, col, mat="SmoothPlastic", **kw):
    # v59: sort the bounds; mirrored callers (s_ = -1) gave 134 Mullion + 15 Ribbon parts negative sizes = no glass
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), col, mat, **kw)


def light_panel(x, y, z, sx, sz, intensity=1.1, rng_=34):
    intensity, rng_ = intensity * 0.55, rng_ * 1.0
    box("Light", (sx, 0.3, sz), (x, y, z), WARM, "Neon", collide=False, shadow=False, light=(intensity, rng_, WARM))


def floor_slab(y, x0, x1, z0, z1, voids, col, mat="Concrete", thick=1.2, name="Floor"):
    xs = {x0, x1}
    zs = {z0, z1}
    for v in voids:
        for xv in (v[0], v[1]):
            if x0 < xv < x1:
                xs.add(xv)
        for zv in (v[2], v[3]):
            if z0 < zv < z1:
                zs.add(zv)
    xs, zs = sorted(xs), sorted(zs)
    for xa, xb in zip(xs, xs[1:]):
        for za, zb in zip(zs, zs[1:]):
            cx, cz = (xa + xb) / 2, (za + zb) / 2
            if any(v[0] < cx < v[1] and v[2] < cz < v[3] for v in voids):
                continue
            rect(name, xa, xb, y - thick, y, za, zb, col, mat)


def glass_x(x0, x1, z, y0, y1, step=8.0, gaps=(), tr=0.55, col=GLASS):
    xs = [x0]
    for a, b in sorted(gaps):
        xs += [a, b]
    xs.append(x1)
    for i in range(0, len(xs), 2):
        a, b = xs[i], xs[i + 1]
        if b - a < 0.5:
            continue
        rect("Glass", a, b, y0, y1, z - 0.25, z + 0.25, col, "Glass", transp=tr)
        n = max(1, int((b - a) / step))
        for q in range(n + 1):
            box("Mull", (0.6, y1 - y0, 0.8), (a + q * (b - a) / n, (y0 + y1) / 2, z), (88, 92, 98), "SmoothPlastic", collide=False)
        box("Head", (b - a, 0.6, 0.8), ((a + b) / 2, y1 - 0.3, z), (88, 92, 98), "SmoothPlastic", collide=False)


def glass_z(z0, z1, x, y0, y1, step=8.0, gaps=(), tr=0.55, col=GLASS):
    zs = [z0]
    for a, b in sorted(gaps):
        zs += [a, b]
    zs.append(z1)
    for i in range(0, len(zs), 2):
        a, b = zs[i], zs[i + 1]
        if b - a < 0.5:
            continue
        rect("Glass", x - 0.25, x + 0.25, y0, y1, a, b, col, "Glass", transp=tr)
        n = max(1, int((b - a) / step))
        for q in range(n + 1):
            box("Mull", (0.8, y1 - y0, 0.6), (x, (y0 + y1) / 2, a + q * (b - a) / n), (88, 92, 98), "SmoothPlastic", collide=False)


def wall_x(x0, x1, z, y0, y1, col=WHITE, mat="Concrete", gaps=(), t=1.0):
    xs = [x0]
    for a, b in sorted(gaps):
        xs += [a, b]
    xs.append(x1)
    for i in range(0, len(xs), 2):
        if xs[i + 1] - xs[i] > 0.2:
            rect("Wall", xs[i], xs[i + 1], y0, y1, z - t / 2, z + t / 2, col, mat)
    for a, b in gaps:
        rect("Lintel", a, b, y1 - 2.5, y1, z - t / 2, z + t / 2, col, mat)


def wall_z(z0, z1, x, y0, y1, col=WHITE, mat="Concrete", gaps=(), t=1.0):
    zs = [z0]
    for a, b in sorted(gaps):
        zs += [a, b]
    zs.append(z1)
    for i in range(0, len(zs), 2):
        if zs[i + 1] - zs[i] > 0.2:
            rect("Wall", x - t / 2, x + t / 2, y0, y1, zs[i], zs[i + 1], col, mat)
    for a, b in gaps:
        rect("Lintel", x - t / 2, x + t / 2, y1 - 2.5, y1, a, b, col, mat)


def panel_wall_x(x0, x1, z, y0, y1, face, holes=True, ribbons=()):
    """perforated cladding facing +/-z (face=+1 / -1); ribbons = [(ya, yb)] window strips"""
    bridge_gap = (x0, x1, z, y0, face) == (-90, 90, -30, 24, 1)
    if bridge_gap:
        # v44: only the existing red corridor's south junction; game placement C.
        rect("Cladding", x0, -50, y0, y1, z - 0.8, z + 0.8, PANEL, "Concrete")
        rect("Cladding", -30, x1, y0, y1, z - 0.8, z + 0.8, PANEL, "Concrete")
        rect("Cladding", -50, -30, 36, y1, z - 0.8, z + 0.8, PANEL, "Concrete")
    else:
        rect("Cladding", x0, x1, y0, y1, z - 0.8, z + 0.8, PANEL, "Concrete")
    for ya, yb in ribbons:
        rect("Ribbon", x0 + 1, x1 - 1, ya, yb, z + face * 0.5, z + face * 0.95, GLASS_DK, "Glass", transp=0.35, collide=False)
    if holes:
        # v30: perforations snapped to a staggered 7-stud grid, all at 45 degrees and darker than the panel, so the
        # facade reads as one architectural pattern instead of random confetti. The rng is consumed exactly as
        # before so every later random placement in the campus stays where it was tested.
        used = set()
        for _ in range(int((x1 - x0) * (y1 - y0) / 90)):
            y = rng.uniform(y0 + 2, y1 - 2)
            if any(ya - 1 < y < yb + 1 for ya, yb in ribbons):
                continue
            x = rng.uniform(x0 + 2, x1 - 2)
            rng.uniform(0, 90)
            gy = round((y - y0) / 7)
            gx = round((x - x0 - (3.5 if gy % 2 else 0)) / 7)
            px, py = x0 + gx * 7 + (3.5 if gy % 2 else 0), y0 + gy * 7
            if (gx, gy) in used or not (x0 + 2 <= px <= x1 - 2 and y0 + 2 <= py <= y1 - 2) or                     any(ya - 1 < py < yb + 1 for ya, yb in ribbons):
                continue
            used.add((gx, gy))
            box("Hole", (1.6, 1.6, 0.3), (px, py, z + face * 0.9), HOLE, "SmoothPlastic", collide=False, shadow=False,
                rot=(0, 0, 45))


def panel_wall_z(z0, z1, x, y0, y1, face, ribbons=()):
    rect("Cladding", x - 0.8, x + 0.8, y0, y1, z0, z1, PANEL, "Concrete")
    for ya, yb in ribbons:
        rect("Ribbon", x + face * 0.5, x + face * 0.95, ya, yb, z0 + 1, z1 - 1, GLASS_DK, "Glass", transp=0.35, collide=False)
    used = set()  # v30: same staggered grid as panel_wall_x (rng consumption unchanged)
    for _ in range(int((z1 - z0) * (y1 - y0) / 90)):
        y = rng.uniform(y0 + 2, y1 - 2)
        if any(ya - 1 < y < yb + 1 for ya, yb in ribbons):
            continue
        zz = rng.uniform(z0 + 2, z1 - 2)
        rng.uniform(0, 90)
        gy = round((y - y0) / 7)
        gz = round((zz - z0 - (3.5 if gy % 2 else 0)) / 7)
        pz, py = z0 + gz * 7 + (3.5 if gy % 2 else 0), y0 + gy * 7
        if (gz, gy) in used or not (z0 + 2 <= pz <= z1 - 2 and y0 + 2 <= py <= y1 - 2) or                 any(ya - 1 < py < yb + 1 for ya, yb in ribbons):
            continue
        used.add((gz, gy))
        box("Hole", (0.3, 1.6, 1.6), (x + face * 0.9, py, pz), HOLE, "SmoothPlastic", collide=False, shadow=False,
            rot=(45, 0, 0))


def column(x, z, y0, y1, d=5.0, col=CREAM, mat="Concrete"):
    vcyl("Column", x, y0, y1, z, d, col, mat)
    disc("Base", x, y0 + 0.5, z, d + 1.2, 1.0, tuple(max(0, v - 14) for v in col), mat, collide=False)
    disc("Cap", x, y1 - 0.6, z, d + 1.2, 1.2, tuple(max(0, v - 8) for v in col), mat, collide=False)


def steel_drum(x, z, y0, y1, d=6.0):
    vcyl("Drum", x, y0, y1, z, d, SILVER, "SmoothPlastic", extra='<float name="Reflectance">0.25</float>')
    disc("Collar", x, y0 + 0.4, z, d + 0.6, 0.8, STEEL, "SmoothPlastic", collide=False)
    for q in range(3):
        box("Slit", (d + 0.3, 0.7, 1.0), (x, y0 + (y1 - y0) * (0.35 + 0.18 * q), z), (40, 44, 52), "SmoothPlastic", collide=False)


def stair_core(x0, x1, z0, z1, ys, col=(226, 222, 212)):
    """U-shaped stairs stacked through the levels in ys; entrance at z0 side"""
    w = (x1 - x0 - 0.6) / 2
    landing = 6.0
    for ya, yb in zip(ys, ys[1:]):
        R = yb - ya
        half = R / 2
        n = max(2, int(round(half / 2.0)))
        sh = half / n
        run = (z1 - z0 - landing) / n
        for i in range(n):                                   # flight A (up, +z)
            top = ya + (i + 1) * sh
            # v27: 1-stud treads (were solid blocks from ya, which sealed the exit of the flight below)
            rect("StepA", x0, x0 + w, max(ya, top - 1.0), top, z0 + i * run, z0 + (i + 1) * run, col, "Concrete")
        rect("Landing", x0, x1, ya + half - 1.0, ya + half, z0 + n * run, z1, col, "Concrete")
        for i in range(n):                                   # flight B (up, -z)
            top = ya + half + (i + 1) * sh
            zb = z0 + n * run - i * run
            rect("StepB", x1 - w, x1, max(ya, top - 1.0), top, zb - run, zb, col, "Concrete")
        rect("CoreGlass", x0 + w + 0.1, x0 + w + 0.5, ya + half, ya + half + 3, z0, z0 + n * run, GLASS, "Glass", transp=0.5,
             collide=False)


def escalator(x, zs, ze, y0, y1, w=5.0):
    n = int((y1 - y0) / 2.0)
    run = (ze - zs) / n
    for i in range(n):
        top = y0 + (i + 1) * 2.0
        rect("Esc", x - w / 2, x + w / 2, y0, top, zs + i * run, zs + (i + 1) * run, (60, 64, 70), "SmoothPlastic")
        rect("EscTread", x - w / 2, x + w / 2, top - 0.05, top, zs + i * run, zs + i * run + 0.5, (200, 205, 210), "SmoothPlastic",
             collide=False)
    for s in (-1, 1):
        rect("EscRail", x + s * (w / 2 + 0.3) - 0.15, x + s * (w / 2 + 0.3) + 0.15, y0 + 3, y1 + 3.4, zs, ze, GLASS, "Glass",
             transp=0.5, collide=False)
        box("Hand", (0.4, 0.4, ze - zs), (x + s * (w / 2 + 0.3), (y0 + y1) / 2 + 3.4, (zs + ze) / 2), (30, 30, 34), "SmoothPlastic",
            collide=False, rot=(-math.degrees(math.atan2(y1 - y0, ze - zs)), 0, 0))


def revolving_door(x, z, y0=0.0):
    disc("RingTop", x, y0 + 11.6, z, 12.5, 0.7, (88, 92, 98), "SmoothPlastic", collide=False)
    disc("RingBase", x, y0 + 0.1, z, 11.8, 0.2, (46, 48, 54), "SmoothPlastic", collide=False)
    for q in range(4):
        a = q * math.pi / 2 + 0.4
        box("Leaf", (5.4, 11, 0.2), (x + 2.7 * math.cos(a), y0 + 5.9, z + 2.7 * math.sin(a)), GLASS, "Glass", transp=0.5,
            collide=False, rot=(0, -math.degrees(a), 0))
    vcyl("Axis", x, y0, y0 + 11.6, z, 0.6, (88, 92, 98), "SmoothPlastic", collide=False)


def palm(x, z, h=17.0):
    vcyl("PalmTrunk", x, 0, h, z, 1.6, (150, 118, 82), "Wood", collide=False)
    for a in range(8):
        yaw = a * 45.0 + rng.uniform(-8, 8)
        pitch = 24 + rng.uniform(-6, 10)
        L = 8.0
        dx = math.sin(math.radians(yaw)) * (L / 2) * math.cos(math.radians(pitch))
        dz = math.cos(math.radians(yaw)) * (L / 2) * math.cos(math.radians(pitch))
        dy = -(L / 2) * math.sin(math.radians(pitch))
        box("Frond", (2.4, 0.25, L), (x + dx, h + dy, z + dz), (82, 150, 78), "Grass", collide=False,
            rot=(pitch, yaw, 0))
    ball("Coconut", x, h - 0.6, z, 1.6, (120, 92, 58), "Wood", collide=False)


def table_set(x, z, y, seats=4, top=(240, 236, 226), seat_cols=None):
    disc("TableTop", x, y + 3.4, z, 6.4, 0.6, top, "Marble")
    vcyl("TableLeg", x, y, y + 3.2, z, 1.0, (86, 90, 96), "SmoothPlastic", collide=False)
    seat_cols = seat_cols or [(220, 92, 70), (240, 190, 60), (70, 150, 104), (90, 126, 200)]
    for a in range(seats):
        ang = a * 2 * math.pi / seats + 0.4
        disc("Stool", x + math.cos(ang) * 5.0, y + 2.0, z + math.sin(ang) * 5.0, 2.2, 0.8, seat_cols[a % len(seat_cols)],
             "SmoothPlastic", collide=False)


def counter(x, z, y, w, d, col, label, face, signh=7.0):
    rect("Counter", x - w / 2, x + w / 2, y, y + 3.6, z - d / 2, z + d / 2, WHITE, "Marble")
    rect("CounterFront", x - w / 2, x + w / 2, y, y + 3.2, z - d / 2 - 0.1, z - d / 2 + 0.4, col, "SmoothPlastic", collide=False)
    sign("Sign", label, (x, y + signh + 2.5, z + d / 2 + 0.3), (w, 4.6, 0.5), face, color=(255, 255, 255), bg=col)


def study_table(x, z, y, w=14, d=6):
    box("Table", (w, 0.8, d), (x, y + 3.4, z), (240, 238, 232), "Marble")
    box("Legs", (w - 2, 3.0, 1.0), (x, y + 1.5, z), (150, 108, 70), "Wood", collide=False)
    vcyl("LampStem", x + w / 2 - 2, y + 3.8, y + 6.4, z, 0.3, (50, 52, 58), "SmoothPlastic", collide=False)
    ball("Shade", x + w / 2 - 2, y + 7.0, z, 2.4, WARM, "Neon", collide=False, shadow=False, light=(0.6, 16, WARM))
    for k in (-1, 1):
        box("Chair", (2.6, 0.6, 2.6), (x + k * 4, y + 2.2, z + d / 2 + 2.2), (178, 60, 54), "Fabric", collide=False)


def tree(x, z, s=1.0):
    C3.tree(x, 0.0, z, s)


# ====================================================================== SOUTH BUILDING
def south_building():
    X0, X1, ZF, ZW, ZB = -90.0, 90.0, -178.0, -160.0, -30.0   # ZF = upper facade, ZW = ground glass, ZB = back
    # ---- ground floor
    rect("GroundFloor", X0, X1, -1, 0, ZF, ZB, TERRAZZO, "Marble")
    for q in range(-9, 9):
        rect("Strip", q * 10 + 4.5, q * 10 + 5.5, 0, 0.05, ZW, ZB, (212, 204, 188), "Marble", collide=False)
    glass_x(X0, X1, ZW, 0, 24, 9.0, gaps=[(-12, 12)])
    revolving_door(0, ZW)
    for x in (-8.5, 8.5):
        rect("DoorLeaf", x - 2.5, x + 2.5, 0, 10, ZW - 0.1, ZW + 0.1, GLASS, "Glass", transp=0.5, collide=False)
    for x in range(-81, 82, 18):
        column(x, ZF + 2, 0, 24, 5.0)
    rect("Soffit", X0, X1, 23, 24.4, ZF, ZW, (214, 206, 186), "Concrete")
    rect("Timber", X0, X1, 20.4, 22.6, ZW - 0.2, ZW + 0.6, TIMBER, "WoodPlanks", collide=False)
    # upper mass: cladding + ribbon windows
    ribbons = [(30, 36), (46, 52), (62, 68), (78, 84)]
    panel_wall_x(X0, X1, ZF, 24, Y_ROOF, -1, True, ribbons)
    for sx, face in ((X0, 1), (X1, -1)):
        glass_z(ZW, ZB, sx, 0, 24, 9.0)
        panel_wall_z(ZF, ZB, sx, 24, Y_ROOF, face, ribbons)
    glass_x(X0, X1, ZB, 0, 24, 9.0, gaps=[(-50, -34), (34, 50)])
    panel_wall_x(X0, X1, ZB, 24, Y_ROOF, 1, False, ribbons)
    rect("Parapet", X0 - 1, X1 + 1, Y_ROOF, Y_ROOF + 2.4, ZF - 1, ZB + 1, PANEL, "Concrete", collide=False)
    # ---- floor slabs
    core_w = (-90.0, -70.0, -62.0, -34.0)
    core_e = (70.0, 90.0, -62.0, -34.0)
    front_void = (-56.0, 56.0, -160.0, -104.0)
    # M (mezzanine wings) and L1
    floor_slab(Y_M, X0, -56, -160, -104, [], TERRAZZO, "Marble", name="MezzW")
    floor_slab(Y_M, 56, X1, -160, -104, [], TERRAZZO, "Marble", name="MezzE")
    floor_slab(Y_1, X0, X1, ZF, ZB, [front_void, core_w, core_e], TERRAZZO, "Marble", name="L1")
    floor_slab(Y_2, X0, X1, ZF, ZB, [core_w, core_e], (228, 224, 214), "Concrete", name="L2")
    floor_slab(Y_3, X0, X1, ZF, ZB, [core_w, core_e], (228, 224, 214), "Concrete", name="L3")
    floor_slab(Y_4, X0, X1, ZF, ZB, [core_w, core_e], (232, 230, 224), "Concrete", name="L4")
    floor_slab(Y_ROOF, X0, X1, ZF, ZB, [], (222, 216, 204), "Concrete", thick=1.6, name="Roof")
    # skylights over the lobby: a strip of the roof is glass
    rect("Skylight", -50, 50, Y_ROOF - 2.0, Y_ROOF - 1.6, -150, -110, (210, 232, 238), "Glass", transp=0.45, collide=False)
    # cores + vertical circulation
    for core in (core_w, core_e):
        x0, x1, z0, z1 = core
        stair_core(x0, x1, z0, z1, LEVELS)
        for yy in LEVELS[:-1]:
            wall_z(z0, z1, x1 if x0 < 0 else x0, yy, yy + 15.5, WHITE, "Concrete", gaps=[])
        sign("CoreSign", "السلالم\nStairs", (x1 + (0.7 if x0 < 0 else -0.7), 8, z0 + 4), (0.4, 3.6, 8), "Right" if x0 < 0 else "Left",
             bg=(40, 60, 70))
    escalator(-48, -140, -104, 0, Y_1)
    escalator(48, -140, -104, 0, Y_1)
    for ex in (-48, 48):
        sign("EscLabel", "الدور الأول ↑", (ex, 15, -143), (10, 2.6, 0.4), "Back", bg=(40, 60, 70))
    # access stairs from G up to the mezzanine wings
    for sx in (-73, 73):
        for i in range(6):
            top = (i + 1) * 2.0
            rect("MStep", sx - 4, sx + 4, 0, top, -92 - i * 2.2 - 2.2, -92 - i * 2.2, (226, 222, 212), "Concrete")
    # railings (balustrades) around the open lobby edges
    for y in (Y_M, Y_1):
        for x in (-56, 56):
            box("Balustrade", (0.4, 3.4, 56), (x, y + 1.7, -132), GLASS, "Glass", transp=0.5, collide=False)
    box("Balustrade", (112, 3.4, 0.4), (0, Y_1 + 1.7, -104), GLASS, "Glass", transp=0.5, collide=False)
    # lobby: silver drums + planters + lights + signs
    for x in (-34, 34):
        for z in (-152,):
            steel_drum(x, z, 0, Y_2, 6.0)
    for x in (-20, 0, 20):
        for z in (-150, -128, -110):
            light_panel(x, Y_2 - 0.5, z, 8, 4, 1.4, 38)
    for x in (-72, 72):
        C3.planter(x, 0, -168, 12, 4)
    sign("Lobby", "كلية العلوم  |  College of Science", (0, 20, -158.4), (36, 6, 0.5), "Back", color=(255, 255, 255), bg=(24, 80, 56))
    # ---- G rear: student study lounge (west), bio science gallery (east)
    wall_x(-90, -56, -92, 0, 24, WHITE, "Concrete", gaps=[(-84, -62)])  # back-of-lobby partition with big opening
    counter(-77, -46, 0, 20, 4, (24, 80, 56), "استراحة طلبة العلوم | Science Lounge", "Back")
    counter(-57, -46, 0, 16, 4, (40, 110, 90), "ركن القهوة الطلابي | Study Coffee", "Back")
    counter(-26, -46, 0, 16, 4, (50, 90, 120), "ركن المذكرات العلمية | Bio Notes", "Back")
    rect("DropWall", -90.5, -89.5, 0, 22, -86, -62, (112, 62, 164), "SmoothPlastic",
         text=dict(face="Right", text="العلوم", color=(255, 255, 255), bg=(112, 62, 164), bg_t=0.0))
    for tx in (-80, -64, -26, -12):
        for r in range(2):
            table_set(tx, -64 - r * 12, 0)
    sign("BioGallery", "معرض الصور العلمية | Bio Science Gallery", (60, 10, -34.5), (18, 4, 0.4), "Front", bg=(24, 80, 56))
    rect("BioGalleryBooth", 51, 69, 0, 14, -44, -34, (230, 230, 226), "SmoothPlastic", transp=0.0)
    # lobby ground lighting + a few warm point lights in the rear hall
    for x in range(-70, 71, 35):
        for z in (-80, -50):
            light_panel(x, 23.0, z, 10, 4, 1.4, 40)
    # ---- M: club office 088 (east wing, door facing the lobby void)
    club_room()
    # ---- L1: lecture hall (west), lounge, trophy case, labs signage
    lecture_hall()
    for q in range(5):
        box("FloorSeat", (6, 1.4, 6), (30 + q * 8, Y_1 + 0.7, -70 - (q % 2) * 4), (200, 60, 54), "Fabric", collide=False)
    # v27: the case stood on the east stair flight (core x 70..90, z -62..-34); now it stands in front of the core
    box("Case", (3, 8, 14), (66, Y_1 + 4, -84), (200, 226, 232), "Glass", transp=0.55)
    for q in range(4):
        vcyl("Trophy", 66, Y_1 + 0.6 + (q // 2) * 4, Y_1 + 3.0 + (q // 2) * 4, -88 + (q % 2) * 8, 1.6, (232, 184, 56), "SmoothPlastic",
             collide=False)
    sign("Achievements", "إنجازات طلبة الكلية", (66, Y_1 + 9.5, -84), (0.4, 2.4, 14), "Left", bg=(70, 50, 20), color=(240, 200, 90))
    sign("EM", "المجهر الإلكتروني | Electron Microscopy", (60, Y_1 + 9, -34.5), (26, 3, 0.4), "Front", bg=(30, 110, 70))
    sign("Museum", "متحف العلوم | Science Museum", (20, Y_1 + 9, -34.5), (26, 3, 0.4), "Front", bg=(90, 60, 40))
    # ---- L2: library
    library()
    # ---- L3: departments
    departments()
    # ---- L4: laboratories
    labs()


def club_room():
    """BSC club office 088 on the mezzanine (M), east wing; door opens onto the balcony"""
    y = Y_M
    x0, x1, z0, z1 = 62.0, 90.0, -160.0, -128.0
    rect("RoomFloor", x0, x1, y, y + 0.25, z0, z1, CARPET, "Fabric", collide=False)
    wall_z(z0, z1, x1, y, y + 11.5, (236, 232, 222), "Concrete")
    wall_x(x0, x1, z0, y, y + 11.5, (236, 232, 222), "Concrete")
    wall_x(x0, x1, z1, y, y + 11.5, (236, 232, 222), "Concrete")
    wall_z(z0, z1, x0, y, y + 11.5, (236, 232, 222), "Concrete", gaps=[(-148, -140)])
    rect("DoorFrame", x0 - 0.5, x0 + 0.5, y, y + 9.6, -148.6, -148.0, (210, 144, 56), "Wood", collide=False)
    rect("DoorFrame", x0 - 0.5, x0 + 0.5, y, y + 9.6, -140.0, -139.4, (210, 144, 56), "Wood", collide=False)
    sign("Plate", "088\nنادي العلوم البيولوجية", (x0 - 0.7, y + 9.0, -144), (0.4, 2.6, 7), "Left", bg=(50, 50, 56))
    # furniture (in the photos: wood desk, black shelf unit, DNA art, mirror, orange display)
    rect("Desk", 76, 82, y + 3, y + 3.9, -156, -142, (158, 110, 70), "Wood")
    rect("DeskBody", 76, 82, y, y + 3, -156, -149, (120, 84, 54), "Wood", collide=False)
    box("Chair", (3, 0.8, 3), (73.5, y + 2.2, -149), (70, 72, 78), "Fabric", collide=False)
    box("ChairBack", (0.5, 4, 3), (72, y + 4.4, -149), (70, 72, 78), "Fabric", collide=False)
    box("Shelf", (3, 10, 18), (x1 - 2, y + 5, -144), (150, 104, 66), "Wood", collide=False)
    disc("Plaque", x1 - 3.6, y + 7.6, -140, 3, 0.4, (232, 184, 56), "SmoothPlastic", collide=False)
    box("DNABoard", (0.4, 8, 12), (x0 + 12, y + 6, z1 - 0.3), (248, 248, 246), "SmoothPlastic", collide=False,
        rot=(0, 90, 0))
    for q in range(22):
        a = q * 0.5
        ball("A", x0 + 12 + math.sin(a) * 3.2, y + 2.4 + q * 0.28, z1 - 0.7, 0.7, (255, 90, 170), "Neon", collide=False, shadow=False)
        ball("B", x0 + 12 - math.sin(a) * 3.2, y + 2.4 + q * 0.28, z1 - 0.7, 0.7, (60, 220, 255), "Neon", collide=False, shadow=False)
    box("Orange", (6, 3.4, 4), (x0 + 5, y + 1.7, z0 + 4), (232, 104, 40), "SmoothPlastic", collide=False)
    light_panel(76, y + 11.0, -144, 10, 5, 1.2, 28)
    # welcome mascot on the balcony facing the door + discord board
    G.mascot(x0 - 6, y, -144)
    sign("Discord", "انضموا لمجتمعنا على Discord\ndiscord.gg/8hw9hBn27", (x0 - 6, y + 7, -156), (10, 5, 0.4), "Back", bg=(88, 101, 242))


def lecture_hall():
    y = Y_1
    # v27: x0 was -88, which pushed the raked tiers into the west stair core (x -90..-70) and blocked floors 2-4
    x0, x1, z0, z1 = -68.0, -40.0, -100.0, -36.0
    wall_x(x0, x1, z0, y, y + 15, WHITE, "Concrete", gaps=[(-62, -52)])
    wall_z(z0, z1, x1, y, y + 15, WHITE, "Concrete", gaps=[(-70, -62)])
    rect("HallCarpet", x0, x1, y, y + 0.2, z0, z1, (150, 60, 56), "Fabric", collide=False)
    for r in range(8):                       # stepped red seating rising toward the back wall
        zz = z0 + 6 + r * 6.5
        rect("Tier", x0 + 4, x1 - 4, y, y + 1.2 + r * 1.3, zz - 3.25, zz + 3.25, (110, 112, 118), "Slate")
        for k in range(4):
            box("Seat", (3.4, 2.4, 3.0), (x0 + 6 + k * 5.4, y + 1.2 + r * 1.3 + 1.2, zz), (190, 54, 50), "Fabric", collide=False)
    sign("HallSign", "المدرج الكبير | Main Lecture Hall", (-54, y + 12, z0 + 0.6), (22, 3, 0.4), "Back", bg=(100, 32, 30))
    light_panel(-54, y + 14.4, -68, 22, 8, 1.2, 40)


def library():
    y = Y_2
    for q in range(-3, 4):
        for z in (-150, -140, -60, -48):
            if abs(q) == 3 and z > -100:
                continue
            study_table(q * 22, z, y)
    for x in range(-84, 85, 7):
        for z in (-172, -36):
            if abs(x) < 60 or True:
                box("Shelf", (6, 12, 2.4), (x, y + 6, z + (2 if z < 0 and z > -100 else 1.5)), (146, 100, 62), "Wood", collide=False)
                box("Spines", (5.4, 0.8, 0.3), (x, y + 3 + (x % 4), z + (0.8 if z > -100 else 2.4)),
                    [(196, 70, 64), (70, 110, 190), (70, 150, 96), (232, 188, 60)][(x // 7) % 4], "SmoothPlastic", collide=False)
    for q in range(5):
        for r in range(3):
            C3.lamp_post(0, y, 0) if False else None
    sign("Lib", "المكتبة | Library", (0, y + 10, -176.6), (30, 4, 0.4), "Back", bg=(100, 70, 44))
    for x in range(-60, 61, 30):
        for z in (-150, -100, -50):
            light_panel(x, Y_3 - 1.0, z, 10, 4, 1.2, 36)


def departments():
    y = Y_3
    names = ["بيولوجيا النبات | Plant Biology", "بيولوجيا الحيوان | Animal Biology",
             "الميكروبيولوجيا | Microbiology", "الكيمياء الحيوية | Biochemistry",
             "البيولوجيا الجزيئية | Molecular Biology", "العلوم الزراعية | Agricultural Science",
             "الأدلة الجنائية | Forensic Biology", "التقنية الحيوية | Biotechnology"]
    for i, nm in enumerate(names):
        x = -76 + i * 22
        wall_z(-100, -96, x, y, y + 15, WHITE, "Concrete", gaps=[(-99.5, -96.5)]) if False else None
        sign("Door", nm, (x, y + 8, -90), (18, 2.6, 0.4), "Back", bg=(24, 80, 56))
        box("DoorLeaf", (6, 10, 0.4), (x, y + 5, -89.5), (205, 140, 55), "Wood", collide=False)
    for x in range(-70, 71, 35):
        light_panel(x, Y_4 - 1.0, -100, 12, 4, 1.2, 36)
        box("Bench", (8, 1.6, 2.4), (x, y + 0.8, -120), (170, 120, 76), "WoodPlanks", collide=False)
    sign("Dept", "تخصصات العلوم البيولوجية | Biological Sciences", (0, y + 11, -176.6), (34, 4, 0.4), "Back", bg=(24, 80, 56))


def labs():
    y = Y_4
    names = ["مختبر مايكروبيولوجي | Microbiology Lab", "مختبر بايوكيمستري | Biochemistry Lab",
             "مختبر مولكلر | Molecular Biology Lab", "مختبر الكيمياء التحليلية | Analytical Chemistry Lab",
             "مختبر بيولوجيا نبات | Plant Biology Lab", "المجهر الإلكتروني | Electron Microscopy"]
    for i, nm in enumerate(names):
        x = -72 + i * 29
        rect("LabFront", x - 12, x + 12, y, y + 13, -100.5, -99.5, GLASS, "Glass", transp=0.5, collide=False)
        rect("LabBase", x - 12, x + 12, y, y + 3, -100.8, -99.2, (60, 130, 138), "SmoothPlastic", collide=False)
        sign("LabSign", nm, (x, y + 11, -100.7), (22, 2.8, 0.4), "Back", bg=(30, 100, 110))
        box("Bench", (16, 0.8, 5), (x, y + 3.6, -112), (240, 244, 245), "SmoothPlastic")
        box("Cab", (15, 3.4, 4.4), (x, y + 1.7, -112), (44, 126, 132), "SmoothPlastic", collide=False)
        C3.flask(x - 4, y + 4.0, -112, 6, [(80, 220, 150), (255, 130, 190), (110, 190, 255)][i % 3])
        box("Scope", (2.0, 3.0, 1.6), (x + 4, y + 5.5, -112), (210, 214, 218), "SmoothPlastic", collide=False)
    # analytical chemistry: the portal to the friend's map will live here
    sign("AnalyticalPortal", "→ مختبر الكيمياء التحليلية (قريباً)", (46, y + 6, -100.9), (16, 2, 0.4), "Back",
         bg=(120, 60, 160))
    for x in range(-70, 71, 35):
        light_panel(x, Y_ROOF - 1.0, -112, 12, 4, 1.4, 38)


# ====================================================================== NORTH BUILDING
def north_building():
    X0, X1, Z0, Z1 = -80.0, 100.0, 20.0, 150.0
    rect("GroundFloor", X0, X1, -1, 0, Z0, Z1, TERRAZZO, "Marble")
    glass_x(X0, X1, Z0, 0, 24, 8.0, gaps=[(-8, 8), (12, 28)])
    revolving_door(0, Z0)
    revolving_door(20, Z0)
    for i, x in enumerate(range(int(X0), int(X1), 6)):
        box("Fin", (0.9, 40, 3.6), (x, 44, Z0 - 1.6), (92, 98, 106), "SmoothPlastic", collide=False, rot=(0, 20 if i % 2 else -20, 0))
    rect("UpperGlass", X0, X1, 24, 64, Z0 - 0.25, Z0 + 0.25, (150, 196, 204), "Glass", transp=0.45, collide=False)
    for sx, face in ((X0, 1), (X1, -1)):
        glass_z(Z0, Z1, sx, 0, 24, 9.0)
        panel_wall_z(Z0, Z1, sx, 24, 64, face, [(30, 36), (46, 52)])
    panel_wall_x(X0, X1, Z1, 0, 64, -1, True, [(30, 36), (46, 52)])
    core_w = (X0, X0 + 20, 120.0, 148.0)
    core_e = (X1 - 20, X1, 120.0, 148.0)
    floor_slab(24, X0, X1, Z0, Z1, [(10, 70, 56, 104), core_w, core_e], TERRAZZO, "Marble", name="L1")
    floor_slab(40, X0, X1, Z0, Z1, [(10, 70, 56, 104), core_w, core_e], (228, 224, 214), "Concrete", name="L2")
    floor_slab(56, X0, X1, Z0, Z1, [core_w, core_e], (228, 224, 214), "Concrete", name="L3")
    floor_slab(64, X0, X1, Z0, Z1, [], (222, 216, 204), "Concrete", thick=1.6, name="Roof")
    rect("Skylight", 10, 70, 62, 62.4, 56, 104, (210, 232, 238), "Glass", transp=0.45, collide=False)
    for core in (core_w, core_e):
        stair_core(core[0], core[1], core[2], core[3], [0, 24, 40, 56], )
    for x in (10, 70):
        for z in (60, 80, 100):
            steel_drum(x, z, 0, 56, 7.0)
    for x in (-60, -30, 90):
        for z in (45, 135):
            # v27: never stand a column on a staircase (x 90 / -60 at z 135 blocked both cores)
            if any(c[0] - 3 <= x <= c[1] + 3 and c[2] - 3 <= z <= c[3] + 3 for c in (core_w, core_e)):
                continue
            column(x, z, 0, 24, 4.4)
    # student lounge wing: study & club counters + green sofas
    counter(-38, 142, 0, 30, 4, (24, 80, 56), "استراحة الحرم الشمالي | North Study Lounge", "Front")
    counter(40, 142, 0, 30, 4, (36, 96, 110), "ركن النادي العلمي | BSC Info Desk", "Front")
    for q in range(5):
        for r in range(2):
            table_set(-54 + q * 22, 112 - r * 16, 0, 3, seat_cols=[(60, 130, 90), (60, 100, 170), (230, 190, 60)])
    # L1: games & drawing hall; L2: computer classes
    for q in range(3):
        box("Foosball", (7, 2.6, 3.4), (-60 + q * 20, 24 + 1.3, 60), (60, 62, 68), "SmoothPlastic", collide=False)
    for q in range(6):
        box("Puff", (3.2, 1.8, 3.2), (-62 + q * 5, 24 + 0.9, 90), [(120, 190, 90), (240, 190, 60), (220, 90, 70)][q % 3],
            "Fabric", collide=False)
    sign("Games", "صالة الألعاب والرسم | Games & Drawing Hall", (-40, 32, 21), (30, 3.6, 0.4), "Back", bg=(60, 100, 60))
    for q in range(4):
        for r in range(2):
            box("Desk", (14, 0.8, 5), (-50 + q * 26, 40 + 3.4, 60 + r * 20), (232, 232, 228), "SmoothPlastic")
            box("Mon", (3.4, 2.2, 0.3), (-50 + q * 26, 40 + 5.2, 58 + r * 20), (20, 24, 30), "SmoothPlastic", collide=False,
                text=dict(face="Front", text="BSC", color=(110, 220, 255), bg=(10, 28, 52), bg_t=0.0))
    sign("Computers", "قاعات الحاسوب | Computer Classes", (-30, 48, 21), (30, 3.6, 0.4), "Back", bg=(40, 70, 130))
    sign("North", "الحرم الشمالي | North Campus", (0, 17, Z0 + 0.7), (26, 4, 0.4), "Back", bg=(30, 90, 150))
    for x in range(-60, 100, 24):
        for z in (40, 80, 120):
            light_panel(x, 23.0, z, 10, 4, 1.4, 38)
    # stone sign "113"
    box("StoneSign", (12, 6, 2), (-30, 3, 8), (222, 214, 194), "Concrete",
        text=dict(face="Front", text="113\nكلية العلوم\nCOLLEGE OF SCIENCE", color=(70, 62, 50), bg=(222, 214, 194), bg_t=0.0))



def _catmull(pts, per=14):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def winding_garden():
    """long meandering stone path between the two buildings, planted like the photos"""
    ctrl = [(-40, -30), (-62, 4), (-34, 30), (14, 40), (58, 58), (74, 84), (44, 108), (10, 118), (8, 130)]
    path = _catmull(ctrl, 12)
    for a, b in zip(path, path[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        if L < 0.1:
            continue
        yaw = math.degrees(math.atan2(dx, dz))
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        box("PathStone", (13, 0.5, L + 1.2), (mx, 0.2, mz), (152, 150, 146), "Slate", rot=(0, yaw, 0), collide=False)
        for s_ in (-1, 1):
            nx, nz = math.cos(math.radians(yaw)) * s_ * 6.8, -math.sin(math.radians(yaw)) * s_ * 6.8
            box("Curb", (0.9, 0.9, L + 1.0), (mx + nx, 0.4, mz + nz), (214, 208, 196), "Concrete", rot=(0, yaw, 0), collide=False)
    for i in range(0, len(path), 3):
        px, pz = path[i]
        if i + 1 < len(path):
            dx, dz = path[i + 1][0] - px, path[i + 1][1] - pz
        else:
            dx, dz = 0, 1
        L = math.hypot(dx, dz) or 1
        nx, nz = dz / L, -dx / L
        for s_ in (-1, 1):
            off = rng.uniform(10, 24)
            bx, bz = px + nx * s_ * off, pz + nz * s_ * off
            r = rng.random()
            if r < 0.30:
                tree(bx, bz, rng.uniform(0.9, 1.4))
            elif r < 0.55:
                for _ in range(3):
                    ball("Shrub", bx + rng.uniform(-3, 3), 1.6, bz + rng.uniform(-3, 3), rng.uniform(3, 5.5),
                         (rng.randint(66, 92), rng.randint(128, 160), rng.randint(70, 90)), "Grass", collide=False)
                for _ in range(4):
                    ball("Bloom", bx + rng.uniform(-3, 3), 3.4, bz + rng.uniform(-3, 3), 1.0,
                         [(170, 110, 200), (236, 120, 170), (250, 220, 90)][rng.randint(0, 2)], "SmoothPlastic", collide=False)
            elif r < 0.80:
                for _ in range(3):
                    gray = rng.randint(170, 205)
                    ball("Rock", bx + rng.uniform(-4, 4), 1.0, bz + rng.uniform(-4, 4), rng.uniform(2.5, 6.0),
                         (gray, gray, gray - 4), "Slate", collide=False)
                box("Gravel", (9, 0.15, 7), (bx, 0.2, bz), (200, 196, 188), "Pebble", collide=False)
            else:
                yaw = math.degrees(math.atan2(dx, dz)) + (90 if s_ > 0 else -90)
                box("BenchSeat", (7, 0.6, 2.2), (px + nx * s_ * 8.4, 1.9, pz + nz * s_ * 8.4), (150, 100, 62), "WoodPlanks",
                    rot=(0, yaw, 0), collide=False)
                box("BenchBack", (7, 1.8, 0.4), (px + nx * s_ * 9.4, 3.0, pz + nz * s_ * 9.4), (140, 94, 58), "WoodPlanks",
                    rot=(0, yaw, 0), collide=False)
                box("BenchBase", (6, 1.6, 1.4), (px + nx * s_ * 8.4, 0.8, pz + nz * s_ * 8.4), (46, 48, 54), "SmoothPlastic",
                    rot=(0, yaw, 0), collide=False)
        if i % 9 == 0:
            for s_ in (-1, 1):
                C3.lamp_post(px + nx * s_ * 8.0, 0, pz + nz * s_ * 8.0, 10)
    cx, cz = 92, 70
    for dx, dz in ((-16, -12), (16, -12), (-16, 12), (16, 12)):
        vcyl("Mast", cx + dx, 0, 30, cz + dz, 1.0, (130, 134, 140), "SmoothPlastic")
    box("SailA", (44, 0.5, 30), (cx - 2, 27, cz - 6), (250, 250, 247), "Fabric", collide=False, transp=0.05, rot=(16, 0, 9))
    box("SailB", (40, 0.5, 26), (cx + 6, 24, cz + 10), (244, 244, 241), "Fabric", collide=False, transp=0.05, rot=(-14, 0, -7))
    box("SailC", (30, 0.5, 22), (cx - 14, 21, cz + 2), (248, 248, 245), "Fabric", collide=False, transp=0.05, rot=(6, 0, -12))
    sign("SailSign", "ساحة الاستراحة\nThe Sail Plaza", (cx, 3.2, cz + 24), (14, 2.6, 0.5), "Back", bg=(50, 70, 80))
    box("RedBlock", (60, 30, 26), (150, 15, 62), (178, 92, 62), "Brick")
    for q in range(24):
        box("Louver", (0.5, 26, 1.2), (119.4, 15, 50 + q * 1.1), (150, 66, 44), "SmoothPlastic", collide=False)
    box("GlassPav", (26, 22, 24), (-92, 11, 70), (170, 210, 216), "Glass", transp=0.45)
    for q in range(10):
        box("Slats", (0.5, 22, 1.0), (-78.6, 11, 60 + q * 2.4), TIMBER, "WoodPlanks", collide=False)
    sign("WalkSign", "الممشى بين الحرمين | The Garden Walk", (-40, 5, -26), (16, 3, 0.5), "Back", bg=(40, 90, 70))


# ====================================================================== OUTDOORS
def outdoors():
    rect("Plaza", -140, 140, -1, 0, -250, -30, (222, 214, 198), "Concrete")
    for i in range(-23, 24):
        rect("Strip", i * 6 - 3, i * 6 + 3, 0, 0.06, -246, -178,
             [(196, 176, 148), (160, 158, 156), (222, 204, 176), (128, 126, 126)][i % 4], "Concrete", collide=False)
    rect("Lawn", -160, 160, -1, 0.15, -30, 24 + NB_SHIFT + 6, (112, 164, 98), "Grass")
    rect("Road", -260, 260, -2, 0, -330, -250, (70, 72, 78), "Asphalt")
    for q in range(12):
        rect("Line", -250 + q * 45, -235 + q * 45, 0, 0.08, -291, -289, (240, 240, 235), "SmoothPlastic", collide=False)
    for ex in (-1000, 1000):
        for ez in (-1000, 1000):
            rect("CampusSurround", ex - 1000, ex + 1000, -9, -1.5, ez - 1000, ez + 1000, (124, 162, 108), "Grass")
    rect("EastLawn", 90, 430, -1, 0.15, -250, 160 + NB_SHIFT, (100, 156, 88), "Grass")
    rect("WestLawn", -240, -90, -1, 0.15, -250, 160 + NB_SHIFT, (100, 156, 88), "Grass")
    for x in range(-130, 131, 26):
        palm(x, -240)
    for x in (-110, -70, 70, 110):
        tree(x, -214, 1.2)
        C3.planter(x + 14, 0, -214, 9, 4)
        C3.lamp_post(x - 10, 0, -206)
    for x in (-120, 120):
        for z in (-60, 0, 60, 120, 180, 240):
            if x > 0 and z in (-60, 0):
                continue  # keep the Cell Train station clear
            tree(x, z, 1.1)
    # stone signs 114
    box("Stone114", (16, 6, 2), (-26, 3, -192), (222, 214, 194), "Concrete",
        text=dict(face="Front", text="114\nكلية العلوم\nCOLLEGE OF SCIENCE", color=(70, 62, 50), bg=(222, 214, 194), bg_t=0.0))
    # v30: the second, identical "114" stone (Stone114b) was removed: one entrance stone is enough
    winding_garden()
    # red first-floor bridge between the buildings (y 24)
    z0, z1 = -30.0, 20.0 + NB_SHIFT
    rect("BridgeFloor", -50, -30, 23, 24.4, z0, z1, RED_TILE, "Brick")
    # v59: concrete soffit + edge fascias, so from below it reads as a glazed bridge, not a brick roof
    rect("BridgeSoffit", -50.4, -29.6, 22.4, 23.0, z0, z1, (226, 220, 206), "Concrete")
    rect("BridgeRoof", -50, -30, 36, 37, z0, z1, (226, 220, 206), "Concrete")
    for x in (-50, -30):
        # v59: owner saw "no glass": 0.55 Glass read as empty from outside; a clearer tint + a sill rail
        rect("BridgeGlass", x - 0.25, x + 0.25, 24.4, 36, z0, z1, (150, 200, 215), "Glass", transp=0.38)
        rect("BridgeSill", x - 0.45, x + 0.45, 24.4, 25.2, z0, z1, (88, 92, 98), "Metal")
        for z in range(int(z0), int(z1) + 1, 8):
            box("Mull", (0.6, 11.6, 0.6), (x, 30.2, z), (88, 92, 98), "SmoothPlastic", collide=False)
    for z in range(-24, int(z1), 36):
        for x in (-48, -32):
            vcyl("BridgeCol", x, 0, 23, z, 2.4, CREAM, "Concrete")
    for z in range(-20, int(z1), 16):
        box("BridgeLamp", (6, 0.3, 1.5), (-40, 35.2, z), WARM, "Neon", collide=False, shadow=False)
    sign("BridgeSign", "الممر الأحمر | Red Corridor", (-40, 34.6, -29.4), (16, 2.2, 0.4), "Back", bg=(120, 54, 40))
    # student garden pavilions
    def kiosk(x, z, w, d, col, name):
        rect("Base", x - w / 2, x + w / 2, 0, 12, z - d / 2, z + d / 2, col, "SmoothPlastic")
        rect("Roof", x - w / 2 - 1, x + w / 2 + 1, 12, 13, z - d / 2 - 1, z + d / 2 + 1, (70, 72, 78), "SmoothPlastic")
        rect("Window", x - w / 2 + 2, x + w / 2 - 2, 3, 8, z - d / 2 - 0.1, z - d / 2 + 0.1, GLASS, "Glass", transp=0.4, collide=False)
        sign("CafeSign", name, (x, 10, z - d / 2 - 0.3), (w - 2, 3.4, 0.5), "Front", bg=tuple(max(0, v - 30) for v in col))
        for k in range(3):
            table_set(x - w / 2 + 5 + k * 6.5, z - d / 2 - 7, 0, 3)
    kiosk(106, -100, 18, 12, (24, 96, 74), "مظلة الدراسة | Study Pavilion")
    kiosk(110, -160, 18, 12, (44, 110, 96), "استراحة الحديقة | Garden Pavilion")
    kiosk(115, 70 + NB_SHIFT, 20, 12, (36, 90, 115), "نقطة إرشاد الطلبة | Student Hub")
    # spawn + course portal
    _base_part("CampusSpawn", (10, 1, 10), (0, 0.5, -151), (64, 140, 108), "SmoothPlastic", cls="SpawnLocation",
               extra='<bool name="Neutral">true</bool><int name="Duration">0</int>',
               text=dict(face="Top", text="BSC", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
    # the challenge gates now live inside the building (Challenge Hall, ground floor)
    sign("ToHall", "قاعة التحديات داخل المبنى ←\nChallenge Hall inside (G)", (40, 5, -200), (16, 4, 0.5), "Front",
         bg=(24, 80, 56))
    for s_ in (-1, 1):
        box("SignPost", (0.6, 3, 0.6), (40 + s_ * 7, 1.5, -200), (60, 64, 70), "SmoothPlastic", collide=False)


def build_campus():
    with G.Group("Campus"):
        outdoors()
        south_building()
        _off[2] = NB_SHIFT
        north_building()
        _off[2] = 0.0


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    build_campus()
    _off[0], _off[1], _off[2] = COURSE_OFFSET
    C3.build()
    _base_part("Portal|Campus", (12, 16, 2), (-26 + _off[0] - 18, 8.5, -20), (255, 190, 120), "Neon", transp=0.55,
               collide=False, shadow=False)
    _base_part("PortalCampusSign", (22, 5, 1.2), (-26 + _off[0] - 18, 20, -20), (24, 70, 48), "SmoothPlastic",
               text=dict(face="Front", text="العودة للحرم\nBack to Campus", color=(255, 255, 255), bg=(24, 70, 48), bg_t=0.0))
    gap, rise, bad, n = M2.validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (G.rid(), "".join(G.buf))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("parts:", G.nparts[0], "| steps:", n, "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad),
          "| KB:", len(xml) // 1024)
