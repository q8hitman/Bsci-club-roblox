"""HQ: no dead floor or walls (map-design rule: players should always see something interesting).
  - a lobby mini-obby spiralling up a glowing pillar (something to do while waiting)
  - BSC Café corner with counter, menu, stools
  - seated student NPCs on the sofas / café stools
  - big planters with small trees, wood ceiling baffles, pastel hexagon frieze on the south wall
"""
import math
import random

import genmap as G
import genmap5 as C5
import bsc_art as A
import hq

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(6262)
X, Z, H = hq.X, hq.Z, hq.H
PASTELS = hq.PASTELS
SKIN = [(255, 214, 170), (226, 176, 130), (190, 140, 100), (140, 100, 70)]
SHIRTS = [(60, 110, 86), (110, 70, 150), (230, 120, 90), (70, 120, 200), (240, 200, 80), (250, 250, 248)]


def mini_obby(cx=50.0, cz=14.0):
    """hex stepping pads spiralling up a glowing pillar to a lookout platform"""
    vcyl("ObbyPillar", cx, 0, 36, cz, 4, (250, 250, 248), "SmoothPlastic")
    vcyl("ObbyPillarGlow", cx, 0, 36, cz, 4.3, (120, 255, 200), "Neon", transp=0.6, collide=False, shadow=False)
    n = 12
    for i in range(n):
        a = i * 0.62
        r = 8.5
        x, z = cx + r * math.cos(a), cz + r * math.sin(a)
        y = 2.6 + i * 2.5
        col = PASTELS[i % 5]
        G.part("ObbyPad", (1.2, 5, 5), (x, y - 0.6, z), col, "SmoothPlastic", shape="Cylinder", rot=(0, 0, 90))
        disc("ObbyPadGlow", x, y + 0.02, z, 4.6, 0.08, (255, 255, 255), "Neon", transp=0.5, collide=False, shadow=False)
    top = 2.6 + n * 2.5
    disc("ObbyTop", cx, top - 0.5, cz, 14, 1, (24, 80, 56), "SmoothPlastic")
    disc("ObbyTopRim", cx, top + 0.02, cz, 14.4, 0.1, (120, 255, 200), "Neon", collide=False, shadow=False)
    sign("ObbyWin", "🏆 وصلت للقمة!", (cx, top + 4, cz), (10, 2.6, 0.4), "Back", bg=(150, 110, 20))
    sign("ObbyStart", "🧗 تحدّي المقر: اطلع للقمة!", (cx - 11, 4.5, cz + 8), (11, 2.4, 0.4), "Back", bg=(110, 70, 150))
    for q in range(10):
        a = q * 0.63
        ball("Confetti", cx + 5 * math.cos(a), top + 0.6, cz + 5 * math.sin(a), 0.6, PASTELS[q % 5], "Neon", collide=False,
             shadow=False)


def cafe(x0=-76.0, z0=-34.0):
    """BSC Café: counter, coffee machine, menu board, high tables and stools"""
    rect("CafeRug", x0 + 2, x0 + 36, 0, 0.06, z0, z0 + 26, (238, 222, 196), "SmoothPlastic", collide=False)
    rect("CafeCounter", x0 + 2, x0 + 6, 0, 4, z0 + 2, z0 + 24, (196, 150, 104), "WoodPlanks")
    rect("CafeTop", x0 + 1.6, x0 + 6.4, 4, 4.4, z0 + 1.6, z0 + 24.4, (250, 250, 248), "Marble")
    box("CoffeeMachine", (2.4, 3, 3), (x0 + 3.5, 5.9, z0 + 6), (60, 60, 66), "Metal", collide=False)
    for q in range(4):
        vcyl("Cup", x0 + 3.5, 4.4, 5.6, z0 + 12 + q * 2, 1.0, PASTELS[q], "SmoothPlastic", collide=False)
    # v31: the old board advertised "100 fils" but nothing could be bought. Now it is a real (free) club café:
    # FoodStreet.server serves the four items from ShopOrder|10..13 along the counter, and the sofas are real Seats.
    sign("CafeMenu", "☕ مقهى النادي | BSC Café\nكرك • قهوة عربية • شاي • كوكيز DNA 🍪\nاطلب من الكاونتر (مجاناً)",
         (x0 + 0.8, 12, z0 + 13), (0.4, 7, 14), "Right", color=(255, 240, 210), bg=(60, 40, 30))
    for q in range(4):
        G.part("ShopOrder|%d" % (10 + q), (1, 1, 1), (x0 + 6.8, 4.9, z0 + 5 + q * 5), (0, 0, 0), "SmoothPlastic", transp=1,
               collide=False, shadow=False)
    for (sx, sz) in ((x0 + 22, z0 + 25), (x0 + 34, z0 + 13.5)):
        along_x = sz > z0 + 20
        size = (10, 1.2, 3) if along_x else (3, 1.2, 10)
        G.part("CafeSofa", size, (sx, 1.6, sz), (110, 170, 140), "Fabric", cls="Seat")
        back = (10, 3, 0.8) if along_x else (0.8, 3, 10)
        box("CafeSofaBack", back, (sx + (0 if along_x else 1.5), 3.4, sz + (1.5 if along_x else 0)), (90, 150, 120), "Fabric",
            collide=False)
    for (tx, tz) in ((x0 + 16, z0 + 8), (x0 + 28, z0 + 8), (x0 + 16, z0 + 19), (x0 + 28, z0 + 19)):
        disc("HighTable", tx, 4.2, tz, 4.4, 0.4, (250, 250, 248), "Marble")
        vcyl("HighLeg", tx, 0, 4.2, tz, 0.6, (60, 60, 66), "Metal", collide=False)
        for k in range(2):
            sx = tx + (-3.2 if k == 0 else 3.2)
            disc("Stool", sx, 3.0, tz, 2.2, 0.5, PASTELS[(k + int(tx)) % 5], "SmoothPlastic")
            vcyl("StoolLeg", sx, 0, 3.0, tz, 0.4, (60, 60, 66), "Metal", collide=False)
    return [(x0 + 12.8, 3.0, z0 + 8, 90), (x0 + 31.2, 3.0, z0 + 19, -90)]


def student(x, y, z, yaw, seated=True):
    """a simple blocky student NPC (seated or standing)"""
    r = math.radians(yaw)
    fx, fz = math.sin(r), math.cos(r)
    rx, rz = math.cos(r), -math.sin(r)
    shirt, skin = rng.choice(SHIRTS), rng.choice(SKIN)
    pants = rng.choice([(40, 50, 80), (60, 60, 66), (120, 100, 80)])
    with G.Group("Student", "Model"):
        hip = y + (0.6 if seated else 3.0)
        box("Torso", (2, 2.4, 1), (x, hip + 1.6, z), shirt, "SmoothPlastic", rot=(0, yaw, 0), collide=False)
        box("Head", (1.4, 1.4, 1.4), (x, hip + 3.5, z), skin, "SmoothPlastic", rot=(0, yaw, 0), collide=False)
        box("Hair", (1.5, 0.5, 1.5), (x, hip + 4.3, z), rng.choice([(30, 24, 20), (70, 50, 30), (20, 20, 22)]), "SmoothPlastic",
            rot=(0, yaw, 0), collide=False)
        for s_ in (-1, 1):
            box("Arm", (0.8, 2.2, 0.8), (x + rx * s_ * 1.4, hip + 1.6, z + rz * s_ * 1.4), shirt, "SmoothPlastic", rot=(0, yaw, 0),
                collide=False)
            if seated:
                box("Thigh", (0.9, 0.9, 2.0), (x + rx * s_ * 0.5 + fx * 0.9, hip + 0.3, z + rz * s_ * 0.5 + fz * 0.9), pants,
                    "SmoothPlastic", rot=(0, yaw, 0), collide=False)
                box("Shin", (0.9, 2.0, 0.9), (x + rx * s_ * 0.5 + fx * 1.7, hip - 0.8, z + rz * s_ * 0.5 + fz * 1.7), pants,
                    "SmoothPlastic", rot=(0, yaw, 0), collide=False)
            else:
                box("Leg", (0.9, 3.0, 0.9), (x + rx * s_ * 0.5, hip - 1.5, z + rz * s_ * 0.5), pants, "SmoothPlastic",
                    rot=(0, yaw, 0), collide=False)


def planters():
    for (x, z) in ((-30, 4), (30, 4), (64, 44)):
        vcyl("BigPlanter", x, 0, 2.6, z, 7, (250, 250, 248), "SmoothPlastic")
        disc("Soil", x, 2.65, z, 6.4, 0.1, (90, 70, 50), "Ground", collide=False)
        vcyl("PlanterTrunk", x, 2.6, 10, z, 0.7, (130, 96, 64), "Wood", collide=False)
        for q in range(4):
            ball("PlanterCrown", x + rng.uniform(-1.5, 1.5), 10.5 + rng.uniform(-1, 1.5), z + rng.uniform(-1.5, 1.5),
                 rng.uniform(4, 5.5), (rng.randint(80, 110), rng.randint(150, 180), 90), "Grass", collide=False)


def ceiling_and_frieze():
    for z in range(-60, 65, 8):   # between the light panels
        box("CeilingBaffle", (2 * X - 4, 1.6, 0.8), (0, H - 0.8, z), (206, 160, 112), "WoodPlanks", collide=False, shadow=False)
    # pastel hexagon frieze on the bare south wall band (above the windows' height)
    for i in range(-11, 12):
        col = PASTELS[(i + 11) % 5]
        A.hexagon("WallHex", i * 7.0, 44 + (i % 2) * 3.0, Z - 0.5, 3.0, col, 0.0, -1.0, thick=0.4)


def build():
    with G.Group("HQFill"):
        mini_obby()
        stools = cafe()
        planters()
        ceiling_and_frieze()
        # students: two on each sofa, two at the café, two chatting near the quiz corner
        for sx in (-1, 1):
            student(sx * 40 - 4, 2.2, 61.5, 180)
            student(sx * 40 + 4, 2.2, 61.5, 180)
        for (x, y, z, yaw) in stools:
            student(x, y + 0.3, z, yaw)
        student(-24, 0, 40, 120, seated=False)
        student(-21, 0, 43, 300, seated=False)
