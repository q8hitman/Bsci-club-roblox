"""Design pass after the first in-game look at v14: HQ (bigger logo, bright lounge, posters, real hex floor tiles,
DNA + mascot flanking the aisle), cart island rims, campus lobby lights and atrium banners."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def patch(name, pairs, append=""):
    p = os.path.join(HERE, name)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert a in s, (name, a[:70])
        s = s.replace(a, b, 1)
    s += append
    open(p, "w", encoding="utf-8").write(s)


patch("bsc_art.py", [
    ("def logo(cx, cy, cz, R=4.0, nx=0.0, nz=1.0, words=True, frame=True):",
     "def logo(cx, cy, cz, R=4.0, nx=0.0, nz=1.0, words=True, frame=True, name=True):"),
    ('            mx, mz = cx + ux * 0.9 * R, cz + uz * 0.9 * R\n',
     '            if not name:\n                return\n            mx, mz = cx + ux * 0.9 * R, cz + uz * 0.9 * R\n'),
], append='''

def floor_hex(x, y, z, R, col, name="FloorHex"):
    """flat hexagon tile (floor pattern only)"""
    for q in range(3):
        G.part(name, (R, 0.08, R * math.sqrt(3)), (x, y, z), col, "SmoothPlastic", rot=(0, q * 60, 0), collide=False,
               shadow=False)
''')

LOUNGE_OLD = '''def lounge():
    for sx in (-1, 1):
        x = sx * 22
        rect("Sofa", x - 2.5, x + 2.5, 0, 2.2, 22, 38, (60, 110, 86) if sx < 0 else (110, 70, 150), "Fabric")
        rect("SofaBack", x + sx * 2.5 - 0.8, x + sx * 2.5 + 0.8, 2.2, 5, 22, 38, (50, 92, 72) if sx < 0 else (92, 58, 126), "Fabric",
             collide=False)
        rect("CoffeeTable", x - sx * 6 - 2, x - sx * 6 + 2, 0, 2, 26, 34, (240, 238, 232), "Marble")
    G.mascot(14, 0, 4)
    sign("Welcome", "أهلاً فيكم في مقر النادي! 👋", (14, 26, 4), (22, 3, 0.4), "Back", bg=CLUB_GREEN)'''

LOUNGE_NEW = '''def lounge():
    """two bright seating corners by the south wall; the mascot greets players beside the main aisle"""
    for sx in (-1, 1):
        x = sx * 40
        col = (150, 205, 172) if sx < 0 else (200, 170, 232)
        dark = tuple(v - 30 for v in col)
        A.floor_hex(x, 0.05, 54, 9, (246, 240, 228), name="Rug")
        rect("Sofa", x - 8, x + 8, 0, 2.2, 60, 64, col, "SmoothPlastic")
        rect("SofaBack", x - 8, x + 8, 2.2, 5.4, 63.4, 64.6, dark, "SmoothPlastic", collide=False)
        for k in (-1, 1):
            rect("SofaArm", x + k * 8 - 0.7, x + k * 8 + 0.7, 2.2, 3.6, 60, 64.6, dark, "SmoothPlastic", collide=False)
            rect("Pouf", x + k * 9 - 1.8, x + k * 9 + 1.8, 0, 2.2, 47, 50.6, PASTELS[(k + 2) % 5], "SmoothPlastic")
        disc("CoffeeTable", x, 2.0, 53, 7, 0.5, (250, 250, 248), "Marble")
        vcyl("TableLeg", x, 0, 2, 53, 1.2, (180, 180, 186), "Metal", collide=False)
        ball("Vase", x, 3.0, 53, 1.6, PASTELS[2 if sx < 0 else 4], "SmoothPlastic", collide=False)
    G.mascot(26, 0, -22)
    sign("Welcome", "أهلاً فيكم في مقر النادي! 👋", (26, 25, -22), (22, 3, 0.4), "Back", bg=CLUB_GREEN)


SPECIALTY_POSTERS = [("🌿", "بيولوجيا النبات", "Plant Biology"), ("🐢", "بيولوجيا الحيوان", "Animal Biology"),
                     ("🦠", "الأحياء الدقيقة", "Microbiology"), ("⚗️", "الكيمياء الحيوية", "Biochemistry"),
                     ("🧬", "البيولوجيا الجزيئية", "Molecular Biology"), ("🌴", "النبات الزراعي", "Agricultural Botany"),
                     ("🔎", "الأدلة الجنائية", "Forensic Science"), ("🧪", "التقنية الحيوية", "Biotechnology")]


def posters():
    """a poster for every specialty on the side walls"""
    spots = [(-1, -30), (-1, 2), (-1, 34), (-1, 60), (1, -58), (1, 4), (1, 46), (1, 64)]
    for i, ((side, z), (icon, ar, en)) in enumerate(zip(spots, SPECIALTY_POSTERS)):
        x = side * (X - 0.6)
        box("PosterFrame", (0.3, 9.8, 10.8), (x + side * 0.1, 11, z), (250, 250, 248), "SmoothPlastic", collide=False)
        sign("Poster", "%s\\n%s\\n%s" % (icon, ar, en), (x, 11, z), (0.4, 9, 10), "Right" if side < 0 else "Left",
             color=(30, 30, 36), bg=PASTELS[i % 5])'''

patch("hq.py", [
    ("X, Z, H = 80.0, 72.0, 46.0", "X, Z, H = 80.0, 72.0, 52.0"),
    ('''    for i in range(18):
        a = i * 2 * math.pi / 18
        disc("FloorHex", 26 * math.sin(a), 0.03, 30 + 26 * math.cos(a), 6, 0.06, PASTELS[i % 5], "SmoothPlastic", collide=False,
             shadow=False)
    rect("Carpet", -18, 18, 0, 0.08, 14, 48, (60, 110, 86), "Fabric", collide=False)''',
     '''    for i in range(16):
        a = i * 2 * math.pi / 16
        A.floor_hex(22 * math.sin(a), 0.04, 30 + 22 * math.cos(a), 3.0, PASTELS[i % 5])
    rect("Carpet", -10, 10, 0, 0.06, 20, 42, (214, 232, 220), "SmoothPlastic", collide=False)
    rect("Aisle", -6, 6, 0, 0.05, -60, 20, (226, 236, 230), "SmoothPlastic", collide=False)'''),
    ('''    A.logo(-4, 33, -Z + 1.2, R=3.4, nx=0.0, nz=1.0)
    sign("ClubTitle", "مقر نادي العلوم البيولوجية  •  BSC Headquarters", (0, 42.6, -Z + 0.8), (80, 4.4, 0.5), "Back",
         bg=CLUB_GREEN)''',
     '''    A.logo(-5, 38, -Z + 1.2, R=5.0, nx=0.0, nz=1.0, name=False)
    sign("ClubTitle", "نادي العلوم البيولوجية\\nBiological Sciences Club\\nKuwait University", (46, 38, -Z + 0.8), (30, 10, 0.5),
         "Back", bg=CLUB_GREEN)
    sign("HQTitle", "مقر النادي 🏠\\nBSC Headquarters", (-52, 38, -Z + 0.8), (24, 8, 0.5), "Back", bg=(110, 70, 150))'''),
    (LOUNGE_OLD, LOUNGE_NEW),
    ("def dna_sculpture(cx=0.0, cz=-26.0, h=34.0):", "def dna_sculpture(cx=-26.0, cz=-22.0, h=34.0):"),
    ("        dna_sculpture()\n", "        dna_sculpture()\n        posters()\n"),
])

patch("cartride.py", [
    ('''            disc("IslandRim", px + ox, y + 2.02, pz + oz, rr * 2 + 0.6, 0.1, rim, "Neon", collide=False, shadow=False)''',
     '''            disc("IslandRim", px + ox, y + 1.5, pz + oz, rr * 2 + 0.8, 0.8, rim, "Neon", collide=False, shadow=False)'''),
])

patch("campus9.py", [
    ("def club_office_portal():", '''def lobby_light_and_banners():
    """light the dim lobby edges under the first floor; hang a banner per specialty in the atrium"""
    for x in (-70, -48, 48, 70):
        for z in (-150, -128, -108):
            C5.light_panel(x, 22.4, z, 8, 4, 1.6, 34)
    names = [("🌿 النبات", (120, 190, 110)), ("🐢 الحيوان", (110, 170, 220)), ("🦠 الدقيقة", (230, 140, 170)),
             ("⚗️ الكيمياء الحيوية", (200, 160, 230)), ("🧬 الجزيئية", (90, 200, 160)), ("🌴 الزراعي", (220, 180, 90)),
             ("🔎 الجنائية", (240, 200, 70)), ("🧪 التقنية الحيوية", (100, 190, 240))]
    slots = [(-45, -152), (-27, -152), (27, -152), (45, -152), (-45, -112), (-27, -112), (27, -112), (45, -112)]
    for (x, z), (txt, col) in zip(slots, names):
        box("BannerRod", (7, 0.4, 0.4), (x, 75, z), (70, 70, 76), "Metal", collide=False)
        vcyl("BannerCable", x, 75, 88, z, 0.15, (60, 60, 64), "Metal", collide=False)
        for face, dz in (("Front", 0.0), ("Back", 0.05)):
            box("Banner", (6, 24, 0.2), (x, 62.8, z + dz), col, "Fabric", collide=False,
                text=dict(face=face, text=txt, color=(255, 255, 255), bg=col, bg_t=0.0))


def club_office_portal():'''),
    ("def build():\n    desert_garden()", "def build():\n    lobby_light_and_banners()\n    desert_garden()"),
])
print("design pass applied")
