"""HQ beauty pass: chandelier, wainscot, specimen cases, live leaderboard board, clouds outside the windows,
plus a dressed-up parkour start deck. Called from genmap9 inside the right offsets."""
import math
import random

import genmap as G
import genmap3 as C3
import genmap5 as C5
import bsc_art as A
import hq

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(5151)
X, Z, H = hq.X, hq.Z, hq.H
PASTELS = hq.PASTELS
WOOD = (196, 150, 104)


def chandelier():
    """the five logo hexagons as a glowing ceiling light over the aisle"""
    cy = H - 4.0
    for (u, v), col, icon in A.HEXES:
        x, z = u * 5.2, -8 + v * 5.2
        A.floor_hex(x, cy, z, 4.6, col, name="HexLamp")
        G.part("HexGlow", (1, 1, 1), (x, cy - 0.6, z), col, "Neon", transp=1, collide=False, shadow=False,
               light=(1.1, 30, col))
        vcyl("HexCable", x, cy, H, z, 0.15, (70, 70, 76), "Metal", collide=False)


def wainscot():
    """warm wood panelling along the lower walls with a club-green trim"""
    for (x0, x1, z0, z1) in ((-X + 0.1, -X + 0.6, -Z, Z), (X - 0.6, X - 0.1, -Z, Z)):
        rect("Wainscot", x0, x1, 0, 5, z0, z1, WOOD, "WoodPlanks", collide=False)
        rect("Trim", x0 - 0.05, x1 + 0.05, 5, 5.5, z0, z1, hq.CLUB_GREEN, "SmoothPlastic", collide=False)
    for (z0, z1) in ((Z - 0.6, Z - 0.1),):
        rect("Wainscot", -X, X, 0, 5, z0, z1, WOOD, "WoodPlanks", collide=False)
        rect("Trim", -X, X, 5, 5.5, z0 - 0.05, z1 + 0.05, hq.CLUB_GREEN, "SmoothPlastic", collide=False)
    # skirting glow strip
    for x in (-X + 0.7, X - 0.7):
        rect("Skirting", x - 0.1, x + 0.1, 0.1, 0.4, -Z, Z, (120, 255, 200), "Neon", collide=False, shadow=False)


def specimen_case(x, z, items):
    rect("CaseBase", x - 3.5, x + 3.5, 0, 3.4, z - 3.5, z + 3.5, (250, 250, 248), "SmoothPlastic")
    rect("CaseGlass", x - 3.4, x + 3.4, 3.4, 9.4, z - 3.4, z + 3.4, (210, 235, 245), "Glass", transp=0.7)
    rect("CaseTop", x - 3.5, x + 3.5, 9.4, 9.8, z - 3.5, z + 3.5, (250, 250, 248), "SmoothPlastic")
    box("CaseLight", (5, 0.2, 5), (x, 9.3, z), (255, 250, 230), "Neon", collide=False, shadow=False, light=(0.6, 10, (255, 250, 230)))
    kind, label = items
    y = 3.4
    if kind == "microscope":
        box("ScopeBase", (2.4, 0.5, 3), (x, y + 0.25, z), (40, 40, 46), "Metal", collide=False)
        box("ScopeArm", (0.6, 3.4, 0.6), (x, y + 2, z + 1.0), (40, 40, 46), "Metal", collide=False)
        G.part("ScopeTube", (0.8, 3.0, 0.8), (x, y + 3.4, z + 0.2), (230, 230, 236), "Metal", shape="Cylinder",
               rot=(0, 0, 70), collide=False)
        box("ScopeStage", (1.8, 0.2, 1.8), (x, y + 1.6, z), (40, 40, 46), "Metal", collide=False)
    elif kind == "skull":
        ball("Skull", x, y + 1.6, z, 2.6, (240, 234, 220), "SmoothPlastic", collide=False)
        box("Jaw", (1.8, 0.8, 1.4), (x, y + 0.5, z + 0.4), (240, 234, 220), "SmoothPlastic", collide=False)
        for s_ in (-0.5, 0.5):
            ball("Eye", x + s_, y + 1.7, z + 1.1, 0.7, (30, 30, 34), "SmoothPlastic", collide=False)
    elif kind == "jar":
        vcyl("Jar", x, y, y + 4.2, z, 2.6, (200, 230, 210), "Glass", transp=0.4, collide=False)
        vcyl("JarLiquid", x, y + 0.2, y + 3.4, z, 2.3, (200, 230, 120), "Glass", transp=0.5, collide=False)
        ball("Specimen", x, y + 1.8, z, 1.3, (230, 170, 130), "SmoothPlastic", collide=False)
        disc("JarLid", x, y + 4.3, z, 2.8, 0.3, (60, 60, 66), "Metal", collide=False)
    elif kind == "tubes":
        box("Rack", (4, 0.4, 1.6), (x, y + 1.0, z), (180, 140, 100), "Wood", collide=False)
        for q in range(5):
            vcyl("Tube", x - 1.6 + q * 0.8, y, y + 2.8, z, 0.5, (220, 240, 248), "Glass", transp=0.4, collide=False)
            vcyl("TubeLiquid", x - 1.6 + q * 0.8, y, y + 1.6, z, 0.4, PASTELS[q], "Neon", collide=False, shadow=False)
    elif kind == "dna":
        for q in range(10):
            a = q * 0.6
            ball("A", x + math.cos(a) * 1.1, y + 0.4 + q * 0.5, z + math.sin(a) * 1.1, 0.45, (255, 90, 170), "Neon",
                 collide=False, shadow=False)
            ball("B", x - math.cos(a) * 1.1, y + 0.4 + q * 0.5, z - math.sin(a) * 1.1, 0.45, (60, 220, 255), "Neon",
                 collide=False, shadow=False)
    elif kind == "plant":
        vcyl("Pot", x, y, y + 1.4, z, 1.8, (200, 120, 80), "SmoothPlastic", collide=False)
        for q in range(4):
            ball("Leaf", x + (q % 2 - 0.5), y + 2 + q * 0.5, z + (q // 2 - 0.5), 1.4, (90, 170, 80), "Grass", collide=False)
    sign("CaseLabel", label, (x, 1.8, z - 3.56), (6, 1.4, 0.1), "Front", color=(40, 40, 40), bg=(250, 246, 236))


def specimens():
    items = [("microscope", "مجهر ضوئي 🔬"), ("skull", "جمجمة (تشريح) 💀"), ("jar", "عيّنة محفوظة 🫙"),
             ("tubes", "أنابيب اختبار 🧪"), ("dna", "نموذج DNA 🧬"), ("plant", "نبات النفل 🌱")]
    for i, it in enumerate(items):
        x = -60 + i * 9.2 if i < 3 else 33 + (i - 3) * 9.2
        specimen_case(x, -50, it)


def leaderboard():
    """east wall board; Leaderboard.server.luau rewrites its text with the players' stages"""
    G.part("LeaderboardFrame", (0.4, 15, 19), (X - 0.9, 12, 2), (40, 44, 54), "SmoothPlastic", collide=False)
    G.part("Leaderboard", (0.3, 14, 18), (X - 1.2, 12, 2), (20, 24, 34), "SmoothPlastic", collide=False,
           text=dict(face="Left", text="🏆 الأبطال الحين\n—", color=(255, 236, 160), bg=(20, 28, 44), bg_t=0.0))


def clouds():
    """soft clouds drifting past the windows (the HQ floats high above Kuwait)"""
    for q in range(46):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(130, 260)
        x, z = r * math.cos(a), r * math.sin(a)
        y = rng.uniform(-30, 40)
        for k in range(rng.randint(3, 5)):
            ball("Cloud", x + rng.uniform(-14, 14), y + rng.uniform(-3, 4), z + rng.uniform(-14, 14), rng.uniform(14, 26),
                 (250, 250, 252), "SmoothPlastic", transp=0.15, collide=False, shadow=False)


def floor_polish():
    """replace the dull planks look with a light polished floor + hexagon inlay border"""
    rect("HQFloorPolish", -X, X, 0, 0.02, -Z, Z, (252, 246, 236), "SmoothPlastic", collide=False)
    for i in range(-7, 8):
        A.floor_hex(i * 10.4, 0.05, -Z + 4, 2.6, PASTELS[(i + 7) % 5])
        A.floor_hex(i * 10.4, 0.05, Z - 4, 2.6, PASTELS[(i + 3) % 5])


def build():
    with G.Group("HQBeauty"):
        floor_polish()
        chandelier()
        wainscot()
        specimens()
        leaderboard()
        clouds()


def start_deck():
    """parkour start deck: logo, zone banners, hex tiles (course offset)"""
    with G.Group("StartDeckBeauty"):
        A.logo_board(0, 33, -62.6, R=1.2, nx=0.0, nz=1.0)
        for i in range(10):
            a = i * 2 * math.pi / 10
            A.floor_hex(14 * math.sin(a), 0.05, -26 + 14 * math.cos(a), 2.4, PASTELS[i % 5])
        import genmap8 as G8
        for i, z in enumerate(G8.ZONES):
            side = -1 if i < 4 else 1
            zz = -60 + (i % 4) * 13
            col = z[2]["edge"]
            vcyl("FlagPole", side * 30, 0, 14, zz, 0.4, (220, 220, 226), "Metal", collide=False)
            box("ZoneFlag", (0.2, 5, 7), (side * 30, 11, zz + 3.6), col, "Fabric", collide=False,
                text=dict(face="Right" if side < 0 else "Left", text="%d\n%s" % (i + 1, z[0]), color=(30, 30, 30), bg=col,
                          bg_t=0.0))
