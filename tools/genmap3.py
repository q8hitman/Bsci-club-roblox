"""Map generator v3: same course logic as genmap2, but every zone sits inside a real themed
environment (floor, walls, props, lighting) instead of floating in a void.
Run: python tools/genmap3.py kuwait-parkour/src/map/Map.rbxmx
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap2 as M  # noqa: E402
import genmap as G  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rng = random.Random(4242)
WALL_X = 72.0        # half-width of every hall
WALL_H = 120.0

# softer, cohesive edge trims for platforms (instead of neon yellow/cyan)
SOFT_EDGE = [(246, 214, 120), (190, 226, 240), (255, 190, 140), (255, 226, 170), (170, 235, 205),
             (226, 190, 255), (255, 170, 140), (235, 240, 250), (170, 215, 255), (255, 170, 215)]
for i, th in enumerate(M.THEMES):
    th["edge"] = SOFT_EDGE[i]


# ------------------------------------------------------------------ prop helpers
def tree(x, g, z, s=1.0, col=(74, 140, 78)):
    vcyl("Trunk", x, g, g + 9 * s, z, 1.4 * s, (110, 80, 52), "Wood")
    ball("Crown", x, g + 13 * s, z, 11 * s, col, "Grass", collide=False)
    ball("Crown", x + 3 * s, g + 10.5 * s, z + 1.5 * s, 7 * s, (col[0] + 12, col[1] + 14, col[2] + 8), "Grass", collide=False)
    ball("Crown", x - 2.5 * s, g + 11 * s, z - 2 * s, 7 * s, (col[0] - 8, col[1] + 6, col[2]), "Grass", collide=False)


def bench(x, g, z, along="z"):
    sx, sz = (2.4, 8) if along == "z" else (8, 2.4)
    box("Seat", (sx, 0.6, sz), (x, g + 1.9, z), (170, 120, 76), "WoodPlanks")
    box("Back", (sx if along == "x" else 0.5, 1.8, 0.5 if along == "x" else sz), (x - (0 if along == "x" else 1.0),
        g + 3.1, z - (1.0 if along == "x" else 0)), (150, 104, 66), "WoodPlanks", collide=False)
    for s in (-1, 1):
        box("Leg", (0.5, 1.8, 0.5) if along == "z" else (0.5, 1.8, 0.5),
            (x + (0 if along == "z" else s * sx * 0.4), g + 0.9, z + (s * sz * 0.4 if along == "z" else 0)),
            (50, 50, 56), "Metal", collide=False)


def planter(x, g, z, sx=8, sz=4, flowers=True):
    box("Planter", (sx, 2.2, sz), (x, g + 1.1, z), (215, 205, 188), "Concrete")
    n = max(2, int(sx / 2.6))
    for i in range(n):
        px = x - sx / 2 + (i + 0.5) * sx / n
        ball("Bush", px, g + 3.0, z, 3.2, (70, 140, 76), "Grass", collide=False)
        if flowers:
            ball("Flower", px + 0.6, g + 4.0, z + 0.4, 1.1, [(240, 120, 170), (250, 210, 70), (250, 250, 250)][i % 3],
                 "SmoothPlastic", collide=False)


def lamp_post(x, g, z, h=11, glow=(255, 232, 180)):
    vcyl("Post", x, g, g + h, z, 0.7, (60, 64, 70), "Metal")
    ball("Lamp", x, g + h + 0.8, z, 2.0, glow, "Neon", collide=False, shadow=False)


def column(x, g, z, h, d=5.0, col=(228, 218, 196), mat="Concrete", rings=True):
    vcyl("Column", x, g, g + h, z, d, col, mat)
    disc("Base", x, g + 0.6, z, d + 1.4, 1.2, tuple(max(0, v - 18) for v in col), mat, collide=False)
    disc("Cap", x, g + h - 0.7, z, d + 1.4, 1.4, tuple(max(0, v - 10) for v in col), mat, collide=False)
    if rings:
        for q in (0.33, 0.66):
            disc("Ring", x, g + h * q, z, d + 0.3, 0.35, tuple(max(0, v - 30) for v in col), mat, collide=False)


def hall(g, z0, z1, floor, wall, wall_alpha=0.0, trim=(60, 60, 66), floor_extra=None):
    L = z1 - z0
    zc = (z0 + z1) / 2
    box("Ground", (WALL_X * 2, 4, L), (0, g - 2, zc), floor[0], floor[1])
    for s in (-1, 1):
        box("Wall", (2, WALL_H, L), (s * (WALL_X + 1), g + WALL_H / 2, zc), wall[0], wall[1], transp=wall_alpha)
        box("Skirting", (1.2, 2.4, L), (s * (WALL_X - 0.1), g + 1.2, zc), trim, "Concrete", collide=False)
        box("Cornice", (1.6, 2.0, L), (s * (WALL_X - 0.2), g + 56, zc), trim, "Concrete", collide=False)


def stripes(g, z0, z1, cols, width=6.0, y=0.06):
    n = int(2 * WALL_X / width)
    L = z1 - z0
    for i in range(n):
        box("Stripe", (width, 0.12, L), (-WALL_X + (i + 0.5) * width, g + y, (z0 + z1) / 2), cols[i % len(cols)],
            "Concrete", collide=False)


def zone_sign(text, x, g, z, w=34, h=9, y=None, bg=(30, 40, 50), face="Back"):
    sign("ZoneBoard", text, (x, (y if y is not None else g + 20), z), (w, h, 1.2), face, color=(255, 255, 255), bg=bg)


def book_shelf(x, g, z, side, h=44, d=6.0):
    box("Shelf", (d, h, 14), (x, g + h / 2, z), (124, 86, 54), "Wood")
    cols = [(196, 70, 64), (70, 110, 190), (70, 150, 96), (232, 188, 60), (140, 80, 170), (230, 230, 225)]
    for q in range(int(h / 4.6)):
        for k in range(3):
            box("Books", (d * 0.55, 3.6, 3.6), (x - side * (d / 2 - 0.15), g + 3 + q * 4.6, z - 4.4 + k * 4.4),
                cols[(q + k + int(z)) % 6], "SmoothPlastic", collide=False)


def desk_row(x, g, z, mon=True, col=(236, 236, 232)):
    box("Desk", (14, 0.8, 5), (x, g + 3.6, z), col, "SmoothPlastic")
    for sx in (-6, 6):
        box("Leg", (0.8, 3.6, 4.4), (x + sx, g + 1.8, z), (60, 64, 72), "Metal", collide=False)
    if mon:
        for k in (-4, 0, 4):
            box("Mon", (3.4, 2.2, 0.3), (x + k, g + 5.3, z - 1.2), (14, 18, 24), "SmoothPlastic", collide=False,
                text=dict(face="Front", text="BSC", color=(110, 220, 255), bg=(10, 28, 52), bg_t=0.0))
            box("Key", (2.6, 0.2, 0.9), (x + k, g + 4.1, z + 0.6), (46, 48, 54), "SmoothPlastic", collide=False)
    for k in (-4, 4):
        box("Chair", (2.4, 0.6, 2.4), (x + k, g + 2.4, z + 4.2), (52, 90, 150), "Fabric", collide=False)


def flask(x, g, z, h=12, col=(80, 220, 150)):
    vcyl("Neck", x, g + h * 0.55, g + h, z, h * 0.18, (205, 235, 240), "Glass", transp=0.45, collide=False)
    ball("Body", x, g + h * 0.4, z, h * 0.8, (205, 235, 240), "Glass", transp=0.5, collide=False)
    ball("Liquid", x, g + h * 0.32, z, h * 0.56, col, "Neon", collide=False, shadow=False)


# ------------------------------------------------------------------ zone environments
def env(j, z0, z1, g):
    th = M.THEMES[j - 1]
    ar, en = M.ZONE_NAMES[j - 1]
    L = z1 - z0
    step = 26
    if j == 1:      # courtyard, golden hour
        hall(g, z0, z1, ((206, 188, 160), "Concrete"), ((206, 194, 172), "Concrete"))
        stripes(g, z0, z1, [(186, 166, 138), (150, 148, 146), (214, 196, 168), (120, 118, 118)], 6.0)
        for z in range(int(z0) + 20, int(z1), 20):       # facade colonnade + perforated band
            for s in (-1, 1):
                column(s * 64, g, z, 62, 6.0)
        for s in (-1, 1):
            box("Facade", (3, 40, L), (s * 68, g + 84, (z0 + z1) / 2), (150, 148, 150), "Metal")
            box("GlassBand", (2, 14, L), (s * 68, g + 70, (z0 + z1) / 2), (110, 170, 150), "Glass", transp=0.5, collide=False)
            for q in range(int(L / 7)):
                box("Hole", (0.3, 2.2, 2.2), (s * 66.4, g + 80 + rng.uniform(0, 18), z0 + 4 + q * 7 + rng.uniform(-2, 2)),
                    (240, 240, 238), "SmoothPlastic", collide=False, rot=(rng.uniform(0, 90), 0, 0))
        for z in range(int(z0) + 30, int(z1), 36):
            for s in (-1, 1):
                tree(s * rng.uniform(40, 56), g, z + rng.uniform(-5, 5), rng.uniform(0.9, 1.3))
                planter(s * rng.uniform(26, 36), g, z + 12, 9, 4)
                bench(s * 30, g, z - 8, "z")
                lamp_post(s * 22, g, z + 4)
        zone_sign("114\nكلية العلوم\nCollege of Science", -44, g, z0 + 26, 18, 10, y=g + 6, bg=(222, 212, 190), face="Back")
    elif j == 2:    # south lobby
        hall(g, z0, z1, ((52, 56, 64), "Granite"), ((90, 140, 140), "Glass"), 0.45, trim=(150, 154, 160))
        stripes(g, z0, z1, [(60, 64, 72), (46, 50, 58)], 12.0, 0.04)
        for z in range(int(z0) + 14, int(z1), 28):
            for s in (-1, 1):
                column(s * 56, g, z, 70, 7.0, (172, 178, 186), "Metal", rings=False)
                for q in range(4):
                    box("Vent", (7.4, 1.0, 1.2), (s * 56, g + 14 + q * 14, z), (28, 32, 38), "Metal", collide=False)
                box("Mullion", (1.2, WALL_H, 1.2), (s * (WALL_X - 0.5), g + WALL_H / 2, z + 14), (60, 66, 74), "Metal", collide=False)
            for k in (-1, 1):
                box("Sofa", (9, 2.4, 3.6), (k * 36, g + 1.2, z + 5), (230, 190, 50) if (z // 28) % 2 else (60, 100, 170), "Fabric")
                box("SofaBack", (9, 2.6, 1.0), (k * 36, g + 3.4, z + 6.9), (200, 160, 40) if (z // 28) % 2 else (46, 80, 140), "Fabric", collide=False)
        for q in range(int(L / 30)):
            box("Skylight", (WALL_X * 2, 0.6, 3), (0, g + 108, z0 + 10 + q * 30), (250, 250, 245), "Neon", collide=False, shadow=False)
        zone_sign("بهو الجنوبي\nSouth Lobby", 0, g, z0 + 14, 40, 9, y=g + 46, bg=(40, 60, 62))
    elif j == 3:    # red lecture hall
        hall(g, z0, z1, ((88, 88, 92), "Slate"), ((120, 76, 50), "WoodPlanks"), trim=(70, 46, 32))
        for z in range(int(z0) + 10, int(z1), 12):       # raked seating on both sides
            for s in (-1, 1):
                row = int(((z - z0) / 12) % 6)
                box("Tier", (22, 4 + row * 2.4, 10), (s * 60, g + (4 + row * 2.4) / 2, z), (110, 112, 118), "Slate")
                for k in range(3):
                    box("Seat", (3.2, 3.0, 3.0), (s * (52 + k * 3.6), g + 4 + row * 2.4 + 1.5, z + 2),
                        (178, 50, 46), "Fabric", collide=False)
        for q in range(int(L / 30)):
            box("RingLight", (WALL_X * 2, 0.5, 2.2), (0, g + 100 - (q % 3) * 3, z0 + 12 + q * 30), (255, 238, 196), "Neon",
                collide=False, shadow=False)
        zone_sign("المدرج الأحمر\nThe Red Lecture Hall", 0, g, z0 + 14, 40, 9, y=g + 46, bg=(110, 36, 34))
    elif j == 4:    # library
        hall(g, z0, z1, ((128, 98, 70), "WoodPlanks"), ((236, 228, 212), "SmoothPlastic"), trim=(120, 84, 54))
        for z in range(int(z0) + 14, int(z1), 16):
            for s in (-1, 1):
                book_shelf(s * 66, g, z, s, 50)
        for z in range(int(z0) + 30, int(z1), 44):
            for s in (-1, 1):
                box("Table", (16, 0.8, 7), (s * 40, g + 3.4, z), (238, 238, 232), "Marble")
                box("TableLeg", (14, 3.4, 1.0), (s * 40, g + 1.7, z), (130, 92, 58), "Wood", collide=False)
                vcyl("LampStem", s * 40 + 6, g + 3.8, g + 7, z, 0.3, (40, 40, 44), "Metal", collide=False)
                ball("Shade", s * 40 + 6, g + 7.6, z, 2.6, (255, 226, 160), "Neon", collide=False, shadow=False)
                for k in (-4, 4):
                    box("Chair", (2.4, 0.6, 2.4), (s * 40 + k, g + 2.2, z + 5), (170, 60, 56), "Fabric", collide=False)
        for q in range(int(L / 40)):
            vcyl("Cord", ((q % 2) * 2 - 1) * 20, g + 92, g + 110, z0 + 20 + q * 40, 0.25, (40, 40, 44), "Metal", collide=False)
            ball("Pendant", ((q % 2) * 2 - 1) * 20, g + 90, z0 + 20 + q * 40, 6, (255, 220, 150), "Neon", collide=False, shadow=False)
        zone_sign("المكتبة\nThe Library", 0, g, z0 + 14, 34, 8, y=g + 46, bg=(96, 66, 42))
    elif j == 5:    # labs
        hall(g, z0, z1, ((226, 230, 232), "SmoothPlastic"), ((244, 246, 246), "SmoothPlastic"), trim=(60, 130, 136))
        for s in (-1, 1):
            box("TealBand", (0.6, 20, L), (s * (WALL_X - 0.2), g + 10, (z0 + z1) / 2), (46, 132, 138), "SmoothPlastic", collide=False)
            box("Window", (0.5, 24, L), (s * (WALL_X - 0.3), g + 76, (z0 + z1) / 2), (150, 200, 220), "Glass", transp=0.5, collide=False)
        for z in range(int(z0) + 16, int(z1), 30):
            for s in (-1, 1):
                box("Bench", (16, 0.8, 6), (s * 44, g + 4.0, z), (240, 244, 245), "SmoothPlastic")
                box("Cab", (15, 3.6, 5.4), (s * 44, g + 1.8, z), (44, 126, 132), "Metal")
                flask(s * 44 - 4, g + 4.4, z, 6, [(80, 220, 150), (255, 130, 190), (110, 190, 255)][int(z / 30) % 3])
                box("Scope", (2.0, 3.0, 1.6), (s * 44 + 4, g + 5.9, z), (206, 210, 214), "Metal", collide=False)
                vcyl("Lens", s * 44 + 4, g + 7.0, g + 8.6, z, 0.8, (30, 32, 38), "Metal", collide=False)
            flask(rng.choice([-1, 1]) * 62, g, z + 10, 22, [(80, 220, 150), (255, 130, 190), (110, 190, 255)][int(z / 30) % 3])
        zone_sign("المختبرات\nElectron Microscopy", 0, g, z0 + 14, 40, 9, y=g + 46, bg=(36, 100, 106))
    elif j == 6:    # cafeteria
        hall(g, z0, z1, ((152, 112, 76), "WoodPlanks"), ((246, 236, 220), "SmoothPlastic"), trim=(120, 84, 54))
        vend = [("Salad Creations\nسالاد كريشنز", (46, 140, 90)), ("Larich", (40, 70, 150)),
                ("Old Friends\nأولد فريندز", (50, 50, 54)), ("العلوم", (120, 70, 180))]
        for q, z in enumerate(range(int(z0) + 22, int(z1), 70)):
            nm, c = vend[q % 4]
            for s in (-1, 1):
                box("Counter", (8, 6, 36), (s * 64, g + 3, z), (244, 244, 240), "Marble")
                box("CounterFront", (0.8, 6, 36), (s * 60, g + 3, z), c, "SmoothPlastic", collide=False)
                sign("Vendor", nm, (s * 66, g + 17, z), (1.2, 8, 32), "Left" if s > 0 else "Right", color=(255, 255, 255), bg=c)
        for z in range(int(z0) + 18, int(z1), 28):
            for s in (-1, 1):
                disc("TableTop", s * 40, g + 4.2, z, 9, 0.8, (240, 236, 226), "Marble")
                vcyl("TableLeg", s * 40, g, g + 4.0, z, 1.2, (70, 70, 76), "Metal", collide=False)
                for a in range(4):
                    ang = a * math.pi / 2 + 0.4
                    disc("Stool", s * 40 + math.cos(ang) * 6.5, g + 2.4, z + math.sin(ang) * 6.5, 2.4, 0.9,
                         [(220, 90, 70), (240, 190, 60), (70, 140, 100), (90, 120, 200)][a], "SmoothPlastic", collide=False)
        for z in range(int(z0) + 10, int(z1), 20):
            vcyl("Cord", 0, g + 96, g + 110, z, 0.25, (40, 40, 44), "Metal", collide=False)
            ball("Pendant", 0, g + 94, z, 4.6, [(255, 150, 90), (255, 210, 110)][int(z / 20) % 2], "Neon", collide=False, shadow=False)
        zone_sign("الكافتيريا\nThe Cafeteria", 0, g, z0 + 14, 34, 8, y=g + 46, bg=(160, 84, 30))
    elif j == 7:    # red corridor + garden
        hall(g, z0, z1, ((92, 140, 80), "Grass"), ((170, 90, 66), "Brick"), 0.0, trim=(110, 60, 44))
        box("Path", (30, 0.3, L), (0, g + 0.15, (z0 + z1) / 2), (150, 72, 55), "Brick", collide=False)
        for z in range(int(z0) + 20, int(z1), 24):
            for s in (-1, 1):
                tree(s * rng.uniform(38, 58), g, z + rng.uniform(-6, 6), rng.uniform(1.0, 1.5), (68, 150, 82))
                for _ in range(2):
                    px, pz = s * rng.uniform(22, 62), z + rng.uniform(-10, 10)
                    ball("Rock", px, g + 1.1, pz, rng.uniform(3, 6), (150, 150, 146), "Slate", collide=False)
                bench(s * 24, g, z + 6, "z")
        for z in range(int(z0) + 40, int(z1), 110):
            for s in (-1, 1):                                       # pergola frames
                for k in (-1, 1):
                    vcyl("Post", s * 20 + k * 5, g, g + 40, z, 1.6, (240, 238, 232), "Concrete")
                box("Beam", (12, 1.4, 1.6), (s * 20, g + 40, z), (240, 238, 232), "Concrete", collide=False)
        zone_sign("الممر الأحمر والحديقة\nRed Corridor & Garden", 0, g, z0 + 14, 40, 9, y=g + 46, bg=(130, 56, 40))
    elif j == 8:    # north atrium
        hall(g, z0, z1, ((210, 212, 214), "Marble"), ((120, 170, 180), "Glass"), 0.5, trim=(110, 116, 124))
        for z in range(int(z0) + 16, int(z1), 28):
            for s in (-1, 1):
                column(s * 50, g, z, 86, 8.0, (96, 102, 110), "Metal", rings=False)
                box("Slit", (8.4, 1.2, 1.4), (s * 50, g + 30, z), (230, 240, 255), "Neon", collide=False, shadow=False)
                box("Balcony", (10, 1.0, 20), (s * 64, g + 40, z + 6), (235, 238, 240), "Marble")
                box("Rail", (0.4, 3.0, 20), (s * 59, g + 41.5, z + 6), (150, 200, 210), "Glass", transp=0.5, collide=False)
        for q in range(int(L / 28)):
            box("Skylight", (WALL_X * 2, 0.6, 5), (0, g + 112, z0 + 12 + q * 28), (255, 255, 250), "Neon", collide=False, shadow=False)
        for z in range(int(z0) + 30, int(z1), 56):
            planter(rng.choice([-1, 1]) * 32, g, z, 12, 5)
            box("Sofa", (10, 2.4, 4), (rng.choice([-1, 1]) * 40, g + 1.2, z + 12), [(230, 190, 50), (60, 100, 170)][int(z / 56) % 2], "Fabric")
        zone_sign("بهو الشمالي\nNorth Atrium", 0, g, z0 + 14, 40, 9, y=g + 50, bg=(60, 70, 80))
    elif j == 9:    # computer labs
        hall(g, z0, z1, ((44, 48, 62), "SmoothPlastic"), ((58, 66, 88), "SmoothPlastic"), trim=(30, 34, 46))
        for z in range(int(z0) + 14, int(z1), 24):
            for s in (-1, 1):
                desk_row(s * 46, g, z)
        for s in (-1, 1):
            for z in range(int(z0) + 10, int(z1), 16):
                box("Rack", (4, 20, 8), (s * 68, g + 10, z), (24, 26, 32), "Metal")
                for q in range(5):
                    box("Led", (0.3, 0.6, 5), (s * 65.8, g + 4 + q * 3.4, z), [(80, 255, 140), (80, 200, 255)][(q + int(z / 16)) % 2], "Neon",
                        collide=False, shadow=False)
        for q in range(int(L / 24)):
            box("Strip", (WALL_X * 2, 0.5, 1.4), (0, g + 100, z0 + 10 + q * 24), (120, 210, 255), "Neon", collide=False, shadow=False)
        zone_sign("صالات الحاسوب\nComputer Labs", 0, g, z0 + 14, 40, 9, y=g + 46, bg=(26, 40, 80))
    else:           # biotechnology
        hall(g, z0, z1, ((16, 20, 34), "Granite"), ((24, 34, 62), "SmoothPlastic"), trim=(60, 220, 255))
        for q in range(int(2 * WALL_X / 12)):
            box("Grid", (0.4, 0.1, L), (-WALL_X + 6 + q * 12, g + 0.06, (z0 + z1) / 2), (40, 160, 220), "Neon", collide=False, shadow=False)
        for z in range(int(z0) + 16, int(z1), 28):
            for s in (-1, 1):
                x = s * 60
                vcyl("Tube", x, g, g + 70, z, 9, (180, 225, 240), "Glass", transp=0.55)
                vcyl("Liquid", x, g + 1, g + 40, z, 7, [(255, 90, 170), (60, 220, 255), (120, 255, 160)][int(z / 28) % 3], "Neon",
                     collide=False, shadow=False)
                for a in range(14):
                    ang = a * 0.55
                    ball("A", s * 46 + math.cos(ang) * 4, g + 6 + a * 4.5, z + 12 + math.sin(ang) * 4, 2.2, (255, 90, 170), "Neon", collide=False, shadow=False)
                    ball("B", s * 46 - math.cos(ang) * 4, g + 6 + a * 4.5, z + 12 - math.sin(ang) * 4, 2.2, (60, 220, 255), "Neon", collide=False, shadow=False)
        zone_sign("البايوتكنولوجي\nBiotechnology", 0, g, z0 + 14, 40, 9, y=g + 50, bg=(20, 28, 60))


# ------------------------------------------------------------------ build
def build():
    M.G.hub()
    c = dict(x=0.0, y=0.0, z=-15.0, sz=14.0)
    M.walk.append(("r", 0.0, -15.0, 0.0, 14.0, 14.0))
    k = 0
    zones = []
    prev_end = 0.0
    with G.Group("Course"):
        for j in range(1, len(M.SEQ) + 1):
            th = M.THEMES[j - 1]
            g = c["y"] - 24
            M.SEA = g
            z_begin = prev_end if j > 1 else -80
            with G.Group("Zone%02d" % j):
                if j > 1:
                    M.zone_gate(j, c)
                for entry in M.SEQ[j - 1]:
                    k += 1
                    t = (k - 1) / 99.0
                    with G.Group("Level%03d" % k):
                        kinds = entry if isinstance(entry, tuple) else (entry,)
                        for kn in kinds:
                            M.KINDS[kn](c, th, t, k)
                            if len(kinds) > 1:
                                M._land(c, th, 8, 2.0)
                        final = k == 100
                        size = 20 if final else 14
                        pz = M.cursor_gap(c, size, 3.0)
                        px, py = c["x"], c["y"]
                        G.part("Checkpoint_%d" % k, (size, 1, size), (px, py - 0.5, pz),
                               (230, 180, 50) if final else (64, 140, 108), "SmoothPlastic",
                               text=dict(face="Top", text="FINISH" if final else "%d" % k, color=(255, 255, 255),
                                         bg=(150, 110, 20) if final else (36, 96, 74), bg_t=0.0))
                        M.walk.append(("r", px, pz, py, size, size))
                        M.set_c(c, px, py, pz, size)
                        M.level_arch(k, c, final)
                        if final:
                            vcyl("TrophyStem", px, py, py + 8, pz, 1.8, (230, 180, 50), "Metal", collide=False)
                            ball("TrophyCup", px, py + 11, pz, 8, (230, 180, 50), "Metal", collide=False)
                z_end = c["z"] + c["sz"] / 2 + 8
                prev_end = z_end
            with G.Group("Env%02d" % j):
                env(j, z_begin, z_end, g)
            zones.append((z_begin, z_end, g))
    global ZONES_OUT
    ZONES_OUT = zones
    return c


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    c_end = build()
    gap, rise, bad, n = M.validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (G.rid(), "".join(G.buf))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    for i, (a, b, g) in enumerate(ZONES_OUT, 1):
        print("zone", i, "z %.0f..%.0f" % (a, b), "ground y %.1f" % g)
    print("parts:", G.nparts[0], "| length: %.0f" % c_end["z"], "| top y: %.0f" % c_end["y"], "| steps:", n,
          "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad), "| KB:", len(xml) // 1024)
