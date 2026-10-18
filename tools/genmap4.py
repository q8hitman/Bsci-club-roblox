"""Campus + course generator (v4).

* Campus: a walkable, scaled re-creation of the College of Science (south building 114, garden
  with the white sail, red bridge corridor, north building 113, cafes) around the origin.
* Course: the 100-stage obby from genmap3, shifted +700 studs east and entered via a portal.
Run: python tools/genmap4.py kuwait-parkour/src/map/Map.rbxmx
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap3 as C3  # noqa: E402  (also imports genmap2 / genmap)
import genmap2 as M  # noqa: E402
import genmap as G  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rng = random.Random(113114)

CREAM = (224, 214, 192)
STONE = (214, 206, 190)
PANEL = (158, 156, 154)
GLASS = (112, 168, 152)
TIMBER = (178, 136, 90)
RED_TILE = (150, 72, 55)
DARK = (52, 56, 64)
WHITE = (244, 244, 240)
COURSE_OFFSET = (700.0, 0.0, 0.0)

_base_part = G.part
_off = [0.0, 0.0, 0.0]


def _offset_part(name, size, pos, *a, **k):
    return _base_part(name, size, (pos[0] + _off[0], pos[1] + _off[1], pos[2] + _off[2]), *a, **k)


G.part = _offset_part


def slab(name, x0, x1, y0, y1, z0, z1, col, mat="Concrete", **kw):
    box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), col, mat, **kw)


def glass_x(x0, x1, z, y0, y1, step=9.0, gaps=()):
    """glass wall running along x at depth z, with mullions; gaps = [(xa, xb)] left open"""
    xs = [x0]
    for a, b in sorted(gaps):
        xs += [a, b]
    xs.append(x1)
    for i in range(0, len(xs), 2):
        a, b = xs[i], xs[i + 1]
        if b - a < 0.5:
            continue
        slab("Glass", a, b, y0, y1, z - 0.3, z + 0.3, GLASS, "Glass", transp=0.5)
        n = int((b - a) / step) + 1
        for q in range(n + 1):
            x = a + q * (b - a) / max(n, 1)
            box("Mull", (0.7, y1 - y0, 0.9), (x, (y0 + y1) / 2, z), (60, 66, 74), "Metal", collide=False)
        box("Rail", (b - a, 0.7, 0.9), (((a + b) / 2), y1 - 0.4, z), (60, 66, 74), "Metal", collide=False)


def glass_z(z0, z1, x, y0, y1, step=9.0, gaps=()):
    zs = [z0]
    for a, b in sorted(gaps):
        zs += [a, b]
    zs.append(z1)
    for i in range(0, len(zs), 2):
        a, b = zs[i], zs[i + 1]
        if b - a < 0.5:
            continue
        slab("Glass", x - 0.3, x + 0.3, y0, y1, a, b, GLASS, "Glass", transp=0.5)
        n = int((b - a) / step) + 1
        for q in range(n + 1):
            z = a + q * (b - a) / max(n, 1)
            box("Mull", (0.9, y1 - y0, 0.7), (x, (y0 + y1) / 2, z), (60, 66, 74), "Metal", collide=False)


def perforated_x(x0, x1, z, y0, y1, face):
    slab("Panel", x0, x1, y0, y1, z - 0.8, z + 0.8, PANEL, "Metal")
    area = (x1 - x0) * (y1 - y0)
    for _ in range(int(area / 55)):
        box("Hole", (2.0, 2.0, 0.3), (rng.uniform(x0 + 2, x1 - 2), rng.uniform(y0 + 2, y1 - 2), z + face * 0.9),
            (240, 240, 238), "SmoothPlastic", collide=False, rot=(0, 0, rng.uniform(0, 90)), shadow=False)


def perforated_z(z0, z1, x, y0, y1, face):
    slab("Panel", x - 0.8, x + 0.8, y0, y1, z0, z1, PANEL, "Metal")
    area = (z1 - z0) * (y1 - y0)
    for _ in range(int(area / 55)):
        box("Hole", (0.3, 2.0, 2.0), (x + face * 0.9, rng.uniform(y0 + 2, y1 - 2), rng.uniform(z0 + 2, z1 - 2)),
            (240, 240, 238), "SmoothPlastic", collide=False, rot=(rng.uniform(0, 90), 0, 0), shadow=False)


def column(x, z, h, d=5.0, y0=0.0, col=CREAM):
    C3.column(x, y0, z, h, d, col)


def louvers_x(x0, x1, z, y0, y1):
    n = int((y1 - y0) / 1.6)
    for q in range(n):
        box("Slat", (x1 - x0, 0.7, 1.2), ((x0 + x1) / 2, y0 + 0.8 + q * 1.6, z), TIMBER, "WoodPlanks", collide=False)


def revolving_door(x, z, y0=0.0, facing=1):
    disc("Ring", x, y0 + 12.5, z, 13, 0.8, (60, 64, 70), "Metal", collide=False)
    disc("Floor", x, y0 + 0.05, z, 12, 0.2, (40, 40, 44), "Metal", collide=False)
    for q in range(4):
        a = q * math.pi / 2 + 0.4
        box("Leaf", (5.6, 11, 0.25), (x + 2.8 * math.cos(a), y0 + 6, z + 2.8 * math.sin(a)), GLASS, "Glass", transp=0.5,
            collide=False, rot=(0, -math.degrees(a), 0))
    vcyl("Axis", x, y0, y0 + 12, z, 0.7, (80, 84, 90), "Metal", collide=False)


def stairs(x0, z0, dx, dz, n, rise, run, width, col=(205, 200, 190), mat="Concrete"):
    """n steps from (x0,z0) toward (dx,dz) unit direction"""
    for i in range(n):
        cx = x0 + dx * (i + 0.5) * run
        cz = z0 + dz * (i + 0.5) * run
        sx = run if dx else width
        sz = run if dz else width
        box("Step", (sx, rise * (i + 1), sz), (cx, rise * (i + 1) / 2, cz), col, mat)


def tree(x, z, s=1.0, g=0.0):
    C3.tree(x, g, z, s)


def counter(x, z, w, d, col, label, face, h=7.0, lab_col=(255, 255, 255), y=0.0, depth_dir=1):
    slab("Counter", x - w / 2, x + w / 2, y, y + 3.6, z - d / 2, z + d / 2, (244, 244, 240), "Marble")
    slab("CounterFront", x - w / 2, x + w / 2, y, y + 3.2, z - d / 2 - 0.1 * depth_dir, z - d / 2 + 0.5, col, "SmoothPlastic",
         collide=False)
    sign("Sign", label, (x, y + h + 4, z + (d / 2) * 0.0), (w, 5, 0.6), face, color=lab_col, bg=col)


# ------------------------------------------------------------------ campus
def surroundings():
    # forecourt (south of building 114), garden strip, parking
    slab("Plaza", -140, 140, -1, 0, -250, -30, STONE, "Concrete")
    for i in range(-23, 24):
        slab("Strip", i * 6 - 3, i * 6 + 3, 0, 0.06, -246, -178,
             [(186, 166, 138), (150, 148, 146), (214, 196, 168), (118, 116, 116)][i % 4], "Concrete", collide=False)
    slab("Lawn", -140, 140, -1, 0.15, -30, 24, (96, 150, 84), "Grass")
    slab("Road", -260, 260, -2, 0, -330, -250, (62, 64, 70), "Asphalt")
    for q in range(12):
        slab("Line", -250 + q * 45, -235 + q * 45, 0, 0.08, -291, -289, (240, 240, 235), "SmoothPlastic", collide=False)
    slab("Earth", -300, 300, -6, -1, -340, 220, (150, 140, 118), "Ground")
    slab("EastLawn", 90, 150, -1, 0.15, -170, 160, (92, 146, 82), "Grass")
    slab("WestLawn", -150, -90, -1, 0.15, -170, 160, (92, 146, 82), "Grass")
    # palms along the road and forecourt
    for x in range(-130, 131, 26):
        vcyl("Palm", x, 0, 15, -240, 1.4, (140, 108, 74), "Wood", collide=False)
        for a in range(6):
            ang = a * math.pi / 3
            box("Frond", (7, 0.4, 1.8), (x + math.cos(ang) * 3.4, 15.2, -240 + math.sin(ang) * 3.4), (70, 140, 70), "Grass",
                collide=False, rot=(0, -math.degrees(ang), 12))
    for x in (-110, -70, 70, 110):
        tree(x, -214, 1.2)
        C3.planter(x + 14, 0, -214, 9, 4)
        C3.lamp_post(x - 10, 0, -206)


def south_building():
    X0, X1, Z0, Z1 = -90, 90, -178, -30
    # structure
    slab("Floor", X0, X1, -1, 0, Z0, Z1, (232, 230, 224), "Marble")
    # ground-floor facade, recessed 18 behind the cantilever
    glass_x(X0, X1, -160, 0, 22, 9.0, gaps=[(-14, 14)])
    for x in range(-81, 82, 18):
        if abs(x) > 14:
            louvers_x(x - 3.5, x + 3.5, -160.8, 1, 21)
    revolving_door(0, -160)
    box("DoorL", (6, 11, 0.4), (-10, 5.5, -160), GLASS, "Glass", transp=0.5, collide=False)
    box("DoorR", (6, 11, 0.4), (10, 5.5, -160), GLASS, "Glass", transp=0.5, collide=False)
    for x in range(-81, 82, 18):
        column(x, -176, 22, 5.0)
    slab("Soffit", X0, X1, 22, 24, -178, -160, (214, 206, 186), "Concrete")
    # upper mass
    perforated_x(X0, X1, Z0, 24, 70, -1)
    slab("GlassBand", X0, X1, 22, 29, Z0 + 1, Z0 + 2, (74, 130, 110), "Glass", transp=0.35, collide=False)
    # sides and back
    for sx in (X0, X1):
        glass_z(-160, Z1, sx, 0, 22, 9.0)
        perforated_z(Z0, Z1, sx, 22, 70, 1 if sx == X0 else -1)
    glass_x(X0, X1, Z1, 0, 22, 9.0, gaps=[(-48, -32), (32, 48)])
    perforated_x(X0, X1, Z1, 22, 70, 1)
    # slabs: second floor (y 22), ceiling (y 44), roof (y 70), atrium hole x[-30,30] z[-128,-66]
    for yy, th in ((22, 1.2), (44, 1.2), (70, 2.0)):
        slab("Slab", X0, X1, yy - th, yy, Z0, -128, (226, 222, 214), "Concrete")
        slab("Slab", X0, X1, yy - th, yy, -66, Z1, (226, 222, 214), "Concrete")
        slab("Slab", X0, -30, yy - th, yy, -128, -66, (226, 222, 214), "Concrete")
        slab("Slab", 30, X1, yy - th, yy, -128, -66, (226, 222, 214), "Concrete")
    slab("Skylight", -30, 30, 70.2, 71, -128, -66, (200, 230, 240), "Glass", transp=0.5, collide=False)
    for q in range(-30, 31, 10):
        box("SkyMull", (0.8, 0.8, 62), (q, 70.6, -97), (70, 76, 84), "Metal", collide=False)
    # atrium: terraced steps going up on the north side + glass balustrades on the mezzanine
    for s in range(6):
        slab("Terrace", -30, 30, 22, 22 + (s + 1) * 3.2, -66 - s * 3.0, -66 - (s + 1) * 3.0 + 0.01, (210, 204, 190), "Concrete",
             collide=False)
    for x in (-30, 30):
        box("Balustrade", (0.5, 3.2, 62), (x, 23.6, -97), GLASS, "Glass", transp=0.5, collide=False)
    for z in (-128, -66):
        box("Balustrade", (60, 3.2, 0.5), (0, 23.6, z), GLASS, "Glass", transp=0.5, collide=False)
    # interior columns
    for x in range(-66, 67, 33):
        for z in (-148, -48):
            column(x, z, 44, 4.4, 0.0, (232, 226, 210))
    for x in (-30, 30):
        for z in (-128, -66):
            vcyl("AtriumCol", x, 0, 70, z, 3.4, (170, 175, 182), "Metal")
    # stairs / escalators up to the second floor (west and east sides of the atrium)
    stairs(-34, -140, 1, 0, 0, 0, 0, 0)  # placeholder (no steps)
    for sx, direction in ((-64, 1), (64, -1)):
        stairs(sx, -100, 0, 1, 11, 2.0, 3.2, 9)
        box("RailL", (0.4, 3, 35), (sx - 4.6, 12, -100 + 17.6), GLASS, "Glass", transp=0.5, collide=False)
        box("RailR", (0.4, 3, 35), (sx + 4.6, 12, -100 + 17.6), GLASS, "Glass", transp=0.5, collide=False)
        sign("EscSign", "الدور الأول  →", (sx, 18, -101), (8, 3, 0.4), "Front", bg=(40, 44, 52))
    # --- interior dressing: ground floor
    for q in range(-3, 4):
        box("CeilLight", (6, 0.3, 40), (q * 24, 19.5, -140), (255, 252, 240), "Neon", collide=False, shadow=False)
    sign("Lobby", "كلية العلوم\nCollege of Science", (0, 12, -158), (30, 8, 0.6), "Back", color=(255, 255, 255), bg=(24, 70, 48))
    for x in (-50, 50):
        C3.planter(x, 0, -150, 10, 4)
    # cafeteria wing (west): Old Friends + "العلوم" purple drop + Second Cup + Burger King
    sign("OldFriends", "Old Friends\nأولد فريندز\nكافتيريا العلوم الجنوبي", (-50, 12, -34.5), (26, 8, 0.6), "Front",
         color=(255, 255, 255), bg=(40, 40, 44))
    counter(-50, -42, 26, 4, (40, 40, 44), "Old Friends", "Back", y=0)
    sign("ScienceDrop", "العلوم", (-84.5, 10, -60), (0.6, 8, 14), "Right", color=(255, 255, 255), bg=(110, 60, 160))
    counter(-82, -70, 4, 18, (110, 60, 160), "العلوم", "Right", y=0)
    counter(-82, -100, 4, 12, (60, 40, 30), "Second Cup", "Right", y=0)
    counter(-82, -125, 4, 12, (200, 60, 50), "Burger King", "Right", y=0)
    for q in range(4):
        for r in range(2):
            disc("Table", -40 + q * 14, 3.4, -70 - r * 14, 6, 0.6, (240, 236, 226), "Marble")
            vcyl("TLeg", -40 + q * 14, 0, 3.2, -70 - r * 14, 1.0, (70, 70, 76), "Metal", collide=False)
            for a in range(3):
                ang = a * 2.1
                disc("Stool", -40 + q * 14 + math.cos(ang) * 4.6, 2.0, -70 - r * 14 + math.sin(ang) * 4.6, 2.0, 0.8,
                     [(220, 90, 70), (240, 190, 60), (70, 140, 100)][a], "SmoothPlastic", collide=False)
    # second floor: library, study area, computer rooms
    for q in range(-3, 4):
        if abs(q) < 2:
            continue
        for z in (-150, -140, -50, -40):
            box("StudyTable", (14, 0.8, 6), (q * 24, 25.4, z), (238, 238, 232), "Marble")
            box("TableLeg", (12, 3.4, 1), (q * 24, 23.8, z), (130, 92, 58), "Wood", collide=False)
            vcyl("Lamp", q * 24 + 5, 26, 28.6, z, 0.3, (40, 40, 44), "Metal", collide=False)
            ball("Shade", q * 24 + 5, 29.2, z, 2.4, (255, 226, 160), "Neon", collide=False, shadow=False)
    for x in range(-80, 81, 8):
        for zz in (-152, -44):
            box("Book", (3, 14, 3), (x, 30.0, zz), (130, 90, 55), "Wood", collide=False) if x % 16 == 0 else None
    sign("Library", "المكتبة | Library", (0, 38, -158), (28, 5, 0.6), "Back", color=(255, 255, 255), bg=(96, 66, 42))
    # exterior sign stone "114" at the entrance
    box("StoneSign", (16, 6, 2), (-26, 3, -192), (220, 212, 192), "Concrete",
        text=dict(face="Front", text="114\nكلية العلوم\nCOLLEGE OF SCIENCE", color=(70, 62, 50), bg=(220, 212, 192), bg_t=0.0))
    box("StoneSign2", (16, 6, 2), (26, 3, -192), (70, 76, 84), "Concrete",
        text=dict(face="Front", text="114\nكلية العلوم\nCOLLEGE OF SCIENCE", color=(210, 190, 140), bg=(70, 76, 84), bg_t=0.0))


def garden():
    # red brick path to the bridge and a stone path through the middle
    slab("BrickPath", -50, -30, 0.1, 0.4, -30, 24, RED_TILE, "Brick", collide=False)
    slab("StonePath", -6, 6, 0.1, 0.4, -30, 24, (190, 186, 178), "Concrete", collide=False)
    for _ in range(26):
        x = rng.uniform(-120, 120)
        z = rng.uniform(-24, 18)
        if -54 < x < -26 or -10 < x < 10 or 18 < x < 66:
            continue
        tree(x, z, rng.uniform(0.8, 1.3))
    for _ in range(18):
        x, z = rng.uniform(-120, 120), rng.uniform(-26, 20)
        if -54 < x < -26 or 18 < x < 66:
            continue
        ball("Rock", x, 1.0, z, rng.uniform(2.5, 5), (156, 154, 148), "Slate", collide=False)
    for x in (-18, 14):
        C3.bench(x, 0, -10, "z")
    for x in (-70, 80, -100, 110):
        C3.lamp_post(x, 0, -4)
    # the white tensile "sail" pavilion (centre-right in the satellite view)
    cx, cz = 42, -6
    for dx, dz in ((-14, -10), (14, -10), (-14, 10), (14, 10)):
        vcyl("Mast", cx + dx, 0, 26, cz + dz, 1.0, (70, 74, 80), "Metal")
    for k, (rx, rz) in enumerate(((22, 0), (-22, 0), (0, 22), (0, -22))):
        box("Sail", (30, 0.5, 26), (cx + (-rz and 0) + (rx and 0) , 18 - k * 0.0, cz), (248, 248, 244), "Fabric",
            collide=False, transp=0.1, rot=(rx, 0, rz)) if False else None
    box("SailA", (34, 0.6, 24), (cx, 22, cz - 6), (248, 248, 244), "Fabric", collide=False, transp=0.1, rot=(14, 0, 8))
    box("SailB", (30, 0.6, 22), (cx + 2, 20, cz + 8), (240, 240, 236), "Fabric", collide=False, transp=0.1, rot=(-12, 0, -6))
    for q in range(7):
        box("Bench", (10, 1.2, 2.6), (cx - 18 + q * 6, 1.0, cz + 18), (170, 120, 76), "WoodPlanks", collide=False) if q % 2 == 0 else None
    sign("SailSign", "ساحة الاستراحة\nThe Sail Plaza", (cx, 3, cz + 20), (14, 2.6, 0.5), "Back", bg=(40, 60, 70))


def bridge():
    # red corridor on the second floor between the buildings (x -48..-32, y 22..34)
    z0, z1 = -30, 20
    slab("BridgeFloor", -50, -30, 21, 22.6, z0, z1, RED_TILE, "Brick")
    slab("BridgeRoof", -50, -30, 33, 34, z0, z1, (220, 214, 200), "Concrete")
    for x in (-50, -30):
        slab("BridgeGlass", x - 0.3, x + 0.3, 22.6, 33, z0, z1, GLASS, "Glass", transp=0.5)
        for z in range(int(z0), int(z1) + 1, 6):
            box("Mull", (0.7, 10.4, 0.7), (x, 27.8, z), (60, 66, 74), "Metal", collide=False)
    for z in (-24, 14):
        for x in (-48, -32):
            vcyl("BridgeCol", x, 0, 21, z, 2.4, CREAM, "Concrete")
    sign("BridgeSign", "الممر الأحمر | Red Corridor", (-40, 31, -29.4), (16, 2.4, 0.4), "Back", bg=(110, 50, 38))


def north_building():
    X0, X1, Z0, Z1 = -80, 100, 20, 150
    slab("Floor", X0, X1, -1, 0, Z0, Z1, (222, 224, 226), "Marble")
    # faceted glass facade facing the garden
    glass_x(X0, X1, Z0, 0, 22, 8.0, gaps=[(-8, 8), (12, 28)])
    revolving_door(0, Z0)
    revolving_door(20, Z0)
    for i, x in enumerate(range(X0, X1, 6)):
        box("Fin", (1.0, 44, 4), (x, 22 + 22, Z0 - 2.0), (52, 56, 64), "Metal", collide=False,
            rot=(0, 18 if i % 2 else -18, 0))
    slab("UpperGlass", X0, X1, 22, 64, Z0 - 0.3, Z0 + 0.3, (92, 150, 160), "Glass", transp=0.45, collide=False)
    for x in range(X0 + 6, X1, 24):
        column(x, Z0 - 3, 22, 4.4, 0.0, (232, 226, 210))
    for sx in (X0, X1):
        glass_z(Z0, Z1, sx, 0, 22, 9.0)
        slab("SideUpper", sx - 0.8, sx + 0.8, 22, 64, Z0, Z1, (170, 176, 182), "Metal")
    slab("Back", X0, X1, 0, 64, Z1 - 0.8, Z1 + 0.8, (170, 176, 182), "Metal")
    for yy, th in ((22, 1.2), (44, 1.2), (64, 2.0)):
        slab("Slab", X0, X1, yy - th, yy, Z0, 66, (226, 222, 214), "Concrete")
        slab("Slab", X0, X1, yy - th, yy, 104, Z1, (226, 222, 214), "Concrete")
        slab("Slab", X0, 10, yy - th, yy, 66, 104, (226, 222, 214), "Concrete")
        slab("Slab", 70, X1, yy - th, yy, 66, 104, (226, 222, 214), "Concrete")
    slab("Skylight", 10, 70, 64.2, 65, 66, 104, (200, 230, 240), "Glass", transp=0.5, collide=False)
    # atrium of metal cylinders (the big steel drums in the photos)
    for x in (10, 70):
        for z in (66, 85, 104):
            vcyl("Drum", x, 0, 64, z, 7.0, (90, 94, 102), "Metal")
            for q in range(3):
                box("Slit", (7.4, 0.9, 1.2), (x, 12 + q * 18, z), (24, 26, 32), "Metal", collide=False)
    for x in (-60, -30, 90):
        for z in (45, 130):
            column(x, z, 44, 4.4, 0.0, (232, 226, 210))
    for yy in (22.6,):
        for x in (10, 70):
            box("Balustrade", (0.5, 3.2, 38), (x, 24, 85), GLASS, "Glass", transp=0.5, collide=False)
    stairs(-60, 40, 0, 1, 11, 2.0, 3.2, 9)
    stairs(86, 40, 0, 1, 11, 2.0, 3.2, 9)
    # cafeteria wing: Salad Creations + Larich
    counter(-45, 140, 32, 5, (46, 140, 90), "Salad Creations\nسالاد كريشنز", "Front", y=0)
    counter(40, 140, 32, 5, (40, 70, 150), "Larich", "Front", y=0)
    for q in range(5):
        for r in range(2):
            disc("Table", -50 + q * 22, 3.4, 110 - r * 16, 6.4, 0.6, (240, 236, 226), "Marble")
            vcyl("TLeg", -50 + q * 22, 0, 3.2, 110 - r * 16, 1.0, (70, 70, 76), "Metal", collide=False)
            for a in range(3):
                ang = a * 2.1
                disc("Stool", -50 + q * 22 + math.cos(ang) * 5, 2.0, 110 - r * 16 + math.sin(ang) * 5, 2.0, 0.8,
                     [(60, 130, 90), (60, 100, 170), (230, 190, 60)][a], "SmoothPlastic", collide=False)
    for q in range(-3, 5):
        box("CeilLight", (6, 0.3, 80), (q * 22 + 10, 19.6, 85), (255, 252, 240), "Neon", collide=False, shadow=False)
    box("StoneSign", (12, 6, 2), (-30, 3, 8), (220, 212, 192), "Concrete",
        text=dict(face="Front", text="113\nكلية العلوم\nCOLLEGE OF SCIENCE", color=(70, 62, 50), bg=(220, 212, 192), bg_t=0.0))
    sign("NorthBoard", "الحرم الشمالي | North Campus", (0, 16, Z0 + 1.2), (24, 4, 0.5), "Back", bg=(30, 90, 150))
    sign("Gallery", "المعامل والأقسام | Labs & Departments", (40, 38, 25), (30, 4, 0.5), "Back", bg=(60, 70, 80))


def cafes():
    def kiosk(x, z, w, d, col, name, facing_dir):
        slab("Base", x - w / 2, x + w / 2, 0, 12, z - d / 2, z + d / 2, col, "SmoothPlastic")
        slab("Roof", x - w / 2 - 1, x + w / 2 + 1, 12, 13, z - d / 2 - 1, z + d / 2 + 1, (60, 60, 66), "Metal")
        sign("CafeSign", name, (x, 9, z - d / 2 - 0.4), (w - 2, 4, 0.5), "Front", color=(255, 255, 255), bg=tuple(max(0, v - 30) for v in col))
        for k in range(3):
            disc("OutTable", x - w / 2 + 5 + k * 6, 3.0, z - d / 2 - 6, 4, 0.5, (240, 236, 226), "Marble")
            vcyl("OutLeg", x - w / 2 + 5 + k * 6, 0, 2.8, z - d / 2 - 6, 0.7, (70, 70, 76), "Metal", collide=False)
    kiosk(106, -100, 18, 12, (130, 80, 170), "Pick", 1)
    kiosk(110, -160, 18, 12, (70, 52, 40), "Toby's Estate", 1)
    kiosk(115, 70, 20, 12, (60, 120, 70), "Caribou Coffee", 1)


def club_room():
    """room 088 in the south building ground floor, west wing, door facing east"""
    x0, x1, z0, z1 = -88, -64, -150, -126
    wall = (150, 140, 135)
    slab("RoomFloor", x0, x1, 0, 0.3, z0, z1, (110, 100, 96), "Fabric", collide=False)
    slab("WallW", x0 - 1, x0, 0, 14, z0, z1, wall, "Fabric")
    slab("WallN", x0, x1, 0, 14, z1, z1 + 1, wall, "Fabric")
    slab("WallS", x0, x1, 0, 14, z0 - 1, z0, wall, "Fabric")
    slab("WallEa", x1, x1 + 1, 0, 14, z0, -141, wall, "Fabric")
    slab("WallEb", x1, x1 + 1, 0, 14, -133, z1, wall, "Fabric")
    slab("Lintel", x1, x1 + 1, 11, 14, -141, -133, wall, "Fabric")
    slab("Roof", x0 - 1, x1 + 1, 14, 15, z0 - 1, z1 + 1, (220, 220, 215), "SmoothPlastic")
    box("Plate", (0.4, 2, 7), (x1 + 1.3, 12.6, -137), (60, 60, 64), "SmoothPlastic",
        text=dict(face="Right", text="088\nنادي العلوم البيولوجية", color=(255, 255, 255), bg=(60, 60, 64), bg_t=0.0))
    box("DoorFrame", (1.4, 11, 0.8), (x1 + 0.5, 5.5, -141.4), (205, 140, 55), "Wood", collide=False)
    box("DoorFrame", (1.4, 11, 0.8), (x1 + 0.5, 5.5, -132.6), (205, 140, 55), "Wood", collide=False)
    box("Desk", (6, 1, 14), (-78, 3.5, -138), (160, 112, 70), "Wood")
    box("DeskSide", (5, 3, 1), (-78, 1.5, -131.5), (130, 90, 55), "Wood", collide=False)
    box("DeskSide", (5, 3, 1), (-78, 1.5, -144.5), (130, 90, 55), "Wood", collide=False)
    box("Chair", (3, 1, 3), (-83, 2, -138), (60, 62, 66), "Fabric", collide=False)
    box("ChairBack", (0.5, 4, 3), (-84.6, 4.4, -138), (60, 62, 66), "Fabric", collide=False)
    box("Shelf", (3, 10, 20), (-86, 5, -138), (150, 100, 62), "Wood", collide=False)
    disc("Plaque", -84.3, 7.5, -138, 3, 0.4, (230, 180, 50), "Metal", collide=False)
    box("DNABoard", (20, 9, 0.4), (-74, 6, z1 - 0.2), (245, 245, 245), "SmoothPlastic", collide=False)
    for q in range(24):
        a = q * 0.5
        ball("StrandA", -74 + math.sin(a) * 3.5, 2.2 + q * 0.3, z1 - 0.6 - math.cos(a) * 0.5, 0.7, (255, 90, 170), "Neon",
             collide=False, shadow=False)
        ball("StrandB", -74 - math.sin(a) * 3.5, 2.2 + q * 0.3, z1 - 0.6 + math.cos(a) * 0.5, 0.7, (60, 220, 255), "Neon",
             collide=False, shadow=False)
    box("Case", (10, 8, 2), (-74, 4, z0 + 1.5), (200, 225, 235), "Glass", transp=0.55, collide=False)
    for q in range(3):
        vcyl("Trophy", -77 + q * 3, 1, 3.8, z0 + 1.5, 1.4, (230, 180, 50), "Metal", collide=False)
    # mascot beside the door (arm points west toward the door), discord board on the lobby column
    G.mascot(-56, 0, -137)
    sign("DiscordBoard", "انضموا لمجتمعنا على Discord\ndiscord.gg/8hw9hBn27", (-56, 7, -150), (10, 5, 0.4), "Front",
         color=(255, 255, 255), bg=(88, 101, 242))
    box("PostD", (0.6, 8, 0.6), (-61, 4, -150), (60, 60, 66), "Metal", collide=False)
    box("PostD", (0.6, 8, 0.6), (-51, 4, -150), (60, 60, 66), "Metal", collide=False)


def portals_and_spawn():
    # spawn on the forecourt, facing the entrance
    _base_part("CampusSpawn", (10, 1, 10), (0, 0.5, -215), (64, 140, 108), "SmoothPlastic", cls="SpawnLocation",
               extra='<bool name="Neutral">true</bool><int name="Duration">0</int>',
               text=dict(face="Top", text="BSC", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
    # course portal: a glowing arch on the forecourt
    for s in (-1, 1):
        box("PortalPost", (3, 18, 3), (70 + s * 9, 9, -214), (46, 70, 66), "Metal", collide=False)
    sign("PortalSign", "ابدأ التحدي\n100 Level Parkour", (70, 20, -214), (24, 6, 1.2), "Front", color=(255, 255, 255), bg=(24, 70, 48))
    box("Portal|Course", (15, 16, 2), (70, 8.5, -214), (120, 255, 200), "Neon", transp=0.55, collide=False, shadow=False)
    sign("PortalHint", "تكمل من آخر Checkpoint", (70, 1.5, -218), (20, 2.4, 0.4), "Front", bg=(40, 60, 54))


def build_campus():
    with G.Group("Campus"):
        surroundings()
        south_building()
        garden()
        bridge()
        north_building()
        cafes()
        club_room()
        portals_and_spawn()


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    build_campus()
    _off[0], _off[1], _off[2] = COURSE_OFFSET
    G.part = _offset_part
    # course hub: back-portal to campus
    C3.build()
    # return portal inside the course lobby (hub deck)
    _base_part("Portal|Campus", (12, 16, 2), (-26 + _off[0] - 18, 8.5, -20), (255, 190, 120), "Neon", transp=0.55,
               collide=False, shadow=False)
    _base_part("PortalCampusSign", (22, 5, 1.2), (-26 + _off[0] - 18, 20, -20), (24, 70, 48), "SmoothPlastic",
               text=dict(face="Front", text="العودة للحرم\nBack to Campus", color=(255, 255, 255), bg=(24, 70, 48), bg_t=0.0))
    gap, rise, bad, n = M.validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (G.rid(), "".join(G.buf))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("parts:", G.nparts[0], "| steps:", n, "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad),
          "| KB:", len(xml) // 1024)
