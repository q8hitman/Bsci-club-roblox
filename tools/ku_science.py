"""v32: Kuwait University College of Science (Sabah Al-Salem University City, Shadadiya) - real-world likeness pass.

References (checked 2026-10-17, see docs/science_research_v32.md):
  * Gulf Consult project photos (real photographs of the finished building): long south block facing the parking, upper
    floors wrapped in a faceted bronze perforated metal screen with folded corners and a sloped top edge, a colonnade
    under it, a central bay of tall white columns in front of recessed glazing with horizontal louvres, a light stone
    plaza with a row of palms and the "114" stone sign; inside: white marble, steel-clad round columns, colourful study
    lounges (green/blue/orange sofas, red high-back booths, cube poufs), red auditorium seats, white labs.
  * NBBJ / Chicago Athenaeum: a raised faculty club nestled between the north and south buildings (curved stacked white
    balconies, roof garden), terracotta at the lower levels, laser-cut back-lit screens at the stairs.
Everything here is drawn ON TOP of the existing campus (genmap5 + campus9), whose interiors came from the user's own
memories (mezzanine, Old Friends / Burger King / Second Cup, club office 088, Red Corridor, Sail Plaza...).
Exact sizes and the faculty club's position are approximations; the south building is ~1:2 of real scale.
"""
import math

import genmap as G
import genmap5 as C5

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign

BRONZE = (188, 128, 86)
BRONZE_DK = (150, 98, 64)
CUT = (216, 168, 122)          # tone-on-tone glints of the laser-cut holes (photo 7)
COLUMN_WHITE = (240, 236, 226)
LOUVRE = (236, 236, 232)
GLASS_BLUE = (120, 160, 176)
TERRACOTTA = (214, 196, 168)

FRONT_Z = -178.0               # south facade line of the south building (genmap5.south_building ZF)
SCREEN_Z = FRONT_Z - 2.0       # the screen floats 2 studs in front of the wall
X0, X1 = -90.0, 90.0
CENTER = 40.0                  # |x| < CENTER: the tall-column entrance bay
Y_TOP = C5.Y_ROOF              # 88
Y_BAY_TOP = C5.Y_4             # the bay's glazing runs up to the top floor; the screen band covers 72..88

_in_south = [False]


def _hash(i, j):
    """stable pseudo-random 0..1 per grid cell (quasi-crystal-like scatter without consuming any shared RNG)"""
    v = math.sin(i * 12.9898 + j * 78.233) * 43758.5453
    return v - math.floor(v)


def _cutouts_x(x0, x1, y0, y1, z, step=4.0):
    """diamond cut-outs of varied size on a screen facing -z (south)"""
    nx = int((x1 - x0) / step)
    ny = int((y1 - y0) / step)
    for i in range(nx):
        for j in range(ny):
            h = _hash(i + int(x0), j + int(y0))
            if h < 0.35:
                continue
            s = 0.6 + h * 1.3
            x = x0 + (i + 0.5) * step + (step / 2 if j % 2 else 0)
            if x > x1 - 1:
                continue
            y = y0 + (j + 0.5) * step
            box("ScreenCut", (s, s, 0.2), (x, y, z), CUT, "SmoothPlastic", rot=(0, 0, 45), collide=False, shadow=False)


def _cutouts_z(z0, z1, y0, y1, x, step=6.0):
    nz = int((z1 - z0) / step)
    ny = int((y1 - y0) / step)
    for i in range(nz):
        for j in range(ny):
            h = _hash(i + int(z0), j + int(y0) + 7)
            if h < 0.35:
                continue
            s = 0.7 + h * 1.4
            z = z0 + (i + 0.5) * step + (step / 2 if j % 2 else 0)
            if z > z1 - 1:
                continue
            box("ScreenCut", (0.2, s, s), (x, y0 + (j + 0.5) * step, z), CUT, "SmoothPlastic", rot=(45, 0, 0), collide=False,
                shadow=False)


def south_screen():
    """the bronze screen of the south building: flanks from L1 up, a band over the entrance bay, folded corners,
    side wraps and a sloped top edge"""
    with G.Group("BronzeScreen"):
        for (a, b) in ((X0, -CENTER), (CENTER, X1)):   # v33: runs on into the wings (no corner fold any more)
            C5.rect("Screen", a, b, C5.Y_1, Y_TOP, SCREEN_Z - 0.3, SCREEN_Z + 0.3, BRONZE, "Metal", collide=False)
            _cutouts_x(a, b, C5.Y_1 + 1, Y_TOP - 1, SCREEN_Z - 0.4)
        C5.rect("ScreenBand", -CENTER, CENTER, Y_BAY_TOP, Y_TOP, SCREEN_Z - 0.3, SCREEN_Z + 0.3, BRONZE, "Metal", collide=False)
        _cutouts_x(-CENTER, CENTER, Y_BAY_TOP + 1, Y_TOP - 1, SCREEN_Z - 0.4)
        C5.rect("ScreenEdge", -CENTER, CENTER, Y_BAY_TOP - 1.2, Y_BAY_TOP, SCREEN_Z - 1.2, SCREEN_Z + 0.4, BRONZE_DK, "Metal",
                collide=False)
        for s_ in (-1, 1):
            # side wraps (east / west), 2 studs outside the wall, starting behind the v33 wings (z > -143)
            sx = s_ * (X1 + 2)
            C5.rect("ScreenSide", sx - 0.3, sx + 0.3, C5.Y_1, Y_TOP, -142, -36, BRONZE, "Metal", collide=False)
            _cutouts_z(-142, -36, C5.Y_1 + 1, Y_TOP - 1, sx + s_ * 0.4)
            C5.rect("ScreenSideAbove", sx - 0.3, sx + 0.3, C5.Y_4, Y_TOP, FRONT_Z + 2, -142, BRONZE, "Metal", collide=False)
        # the crown: the screen folds back at the top on the front and both sides (the faceted "mansard" of photos 3/4)
        mansard(X0 + 4, X1 - 4, SCREEN_Z, Y_TOP)
        for s_ in (-1, 1):
            box("ScreenCrownSide", (12.8, 1.0, 136), (s_ * (X1 + 2 - 5), Y_TOP + 4, -104), BRONZE, "Metal",
                rot=(0, 0, -s_ * 38.7), collide=False)


def mansard(x0, x1, z, y):
    """a 12.8-stud band leaning back 38.7 degrees from the top of a south-facing screen"""
    box("ScreenCrown", (x1 - x0, 1.0, 12.8), ((x0 + x1) / 2, y + 4, z + 5), BRONZE, "Metal", rot=(-38.7, 0, 0),
        collide=False)


def south_wings():
    """the real south facade is long and low (~10:1). Shallow exterior wings carry the same colonnade + bronze screen
    east and west (not enterable; the college continues there in reality). West stops short of the desert garden walk."""
    with G.Group("SouthWings"):
        for (a, b) in ((X1, 150.0), (X0, -128.0)):
            s_ = 1 if b > 0 else -1
            lo, hi = min(a, b), max(a, b)
            zf, zb = FRONT_Z, FRONT_Z + 10
            C5.rect("WingMass", lo, hi, C5.Y_1, C5.Y_4, zf + 2, zb, TERRACOTTA, "Concrete")
            C5.rect("WingGround", lo, hi, 0, C5.Y_1, zb - 2, zb, (150, 186, 196), "Glass", transp=0.35)
            C5.rect("WingSoffit", lo, hi, C5.Y_1 - 1.2, C5.Y_1, zf, zb, (226, 218, 200), "Concrete")
            x = a + s_ * 9
            while (x - b) * s_ < -4:
                C5.column(x, FRONT_Z + 2, 0, C5.Y_1, 5.0, COLUMN_WHITE)
                x += s_ * 18
            sx0, sx1 = (lo, hi - 6) if s_ > 0 else (lo + 6, hi)   # leave the outer 6 studs for the folded end
            C5.rect("WingScreen", sx0, sx1, C5.Y_1, C5.Y_4, SCREEN_Z - 0.3, SCREEN_Z + 0.3, BRONZE, "Metal", collide=False)
            _cutouts_x(lo + (0 if s_ > 0 else 6), hi - (6 if s_ > 0 else 0), C5.Y_1 + 1, C5.Y_4 - 1, SCREEN_Z - 0.4)
            # folded outer end + end panel, and the crown
            ex = b - s_ * 3
            box("WingFold", (8.5, C5.Y_4 - C5.Y_1, 0.6), (ex, (C5.Y_1 + C5.Y_4) / 2, SCREEN_Z + 3), BRONZE, "Metal",
                rot=(0, -45 * s_, 0), collide=False)
            mansard(lo, hi, SCREEN_Z, C5.Y_4)


def entrance_bay():
    """centre bay: recessed glazing with horizontal white louvres behind tall white columns (columns via the hook)"""
    with G.Group("EntranceBay"):
        gz = FRONT_Z + 6.0
        C5.rect("BayGlass", -CENTER, CENTER, C5.Y_1, Y_BAY_TOP, gz - 0.2, gz + 0.2, GLASS_BLUE, "Glass", transp=0.35, collide=False)
        y = C5.Y_1 + 1.5
        while y < Y_BAY_TOP - 0.5:
            C5.rect("Louvre", -CENTER + 0.5, CENTER - 0.5, y, y + 0.35, gz - 1.6, gz - 0.4, LOUVRE, "SmoothPlastic", collide=False)
            y += 2.4
        for x in range(int(-CENTER), int(CENTER) + 1, 8):
            C5.rect("BayMullion", x - 0.25, x + 0.25, C5.Y_1, Y_BAY_TOP, gz - 0.5, gz + 0.3, (200, 204, 208), "Metal", collide=False)
        # the ground-floor porch keeps the old revolving doors; give it a wide entrance sign like the real canopy
        sign("EntranceSign", "كلية العلوم  •  College of Science", (0, 20.5, FRONT_Z + 1.5), (30, 3, 0.4), "Front",
             color=(70, 52, 36), bg=(236, 226, 206))


def plaza():
    """light stone plaza details: planters with stone blocks like the photos, bollard lights, and the warm brown pavers
    under the colonnade (photo 7)"""
    with G.Group("SciencePlaza"):
        C5.rect("ColonnadePaving", X0, X1, 0.02, 0.08, FRONT_Z, -160, (172, 134, 100), "Slate", collide=False)
        C5.rect("ColonnadePavingE", X1, 150, 0.02, 0.08, FRONT_Z, FRONT_Z + 8, (172, 134, 100), "Slate", collide=False)
        C5.rect("ColonnadePavingW", -128, X0, 0.02, 0.08, FRONT_Z, FRONT_Z + 8, (172, 134, 100), "Slate", collide=False)
        for x in (-64, -20, 20, 64):
            C5.rect("PlanterStone", x - 5, x + 5, 0, 1.6, -200, -196, (222, 212, 192), "Limestone")
            for q in range(3):
                ball("PlanterShrub", x - 3 + q * 3, 2.2, -198, 2.6, (96, 140, 80), "Grass", collide=False)
        for x in range(-84, 85, 12):
            vcyl("Bollard", x, 0, 2.2, -186, 0.8, (60, 62, 66), "Metal", collide=False)
            ball("BollardLight", x, 2.4, -186, 0.6, (255, 236, 200), "Neon", collide=False, shadow=False)


CLUB_X, CLUB_Z = 10.0, 80.0


def faculty_club(cx=CLUB_X, cz=CLUB_Z):
    """the raised faculty club between the two buildings: stacked curved white balconies over glass on slim columns,
    a roof garden with round planters and a curved glass pavilion on top (shape from photos 11 and 23; position approx)"""
    oz = C5._off[2]
    with G.Group("FacultyClub"):
        # v32b: wider and lower than a first try (it read as a round tower): two balcony levels + roof garden
        for k in range(10):
            a = k * math.pi / 5 + math.pi / 10
            px, pz = cx + 28 * math.cos(a), cz + 28 * math.sin(a)
            if math.hypot(px - 14, pz - 107) < 7:
                continue   # a garden lamp post (genmap5.winding_garden) stands there
            vcyl("ClubColumn", px, 0, 26, pz, 3.4, COLUMN_WHITE, "Concrete")
        vcyl("ClubGlass", cx, 26, 42, cz, 66, (150, 196, 210), "Glass", transp=0.55, collide=False)
        for i, (y, r) in enumerate(((26, 37), (34, 35.5))):
            disc("ClubFloor", cx, y, cz, 2 * r - 6, 1.2, (230, 228, 222), "Concrete")
            n = 28
            for q in range(n):
                a0 = q * 2 * math.pi / n
                a1 = (q + 1) * 2 * math.pi / n
                am = (a0 + a1) / 2
                L = 2 * r * math.sin(math.pi / n) + 0.4
                box("Balcony", (L, 1.8, 2.6), (cx + r * math.cos(am), y + 0.9, cz + r * math.sin(am)), (246, 244, 238),
                    "SmoothPlastic", rot=(0, -math.degrees(am) + 90, 0), collide=False)
        disc("ClubRoof", cx, 42, cz, 72, 1.4, (226, 224, 218), "Concrete")
        disc("RoofTurf", cx, 42.8, cz, 64, 0.3, (70, 130, 70), "Grass", collide=False)
        for k in range(6):
            a = k * 2 * math.pi / 6
            px, pz = cx + 22 * math.cos(a), cz + 22 * math.sin(a)
            disc("RoofPlanter", px, 43.6, pz, 6, 1.4, (232, 230, 224), "Concrete", collide=False)
            ball("RoofShrub", px, 45, pz, 4.6, (96, 150, 80), "Grass", collide=False)
        vcyl("RoofPavilion", cx, 43, 49, cz, 16, (110, 140, 170), "Glass", transp=0.3, collide=False)
        disc("RoofPavilionTop", cx, 49.4, cz, 17, 0.8, (236, 236, 232), "SmoothPlastic", collide=False)
        sign("ClubSign", "نادي أعضاء هيئة التدريس | Faculty Club", (cx, 22, cz - 29.6), (22, 2.6, 0.4), "Front", bg=(60, 70, 80))
    return oz


def study_lounge():
    """L1 east wing of the south building: the colourful study lounge of the photos. The old wing loungers (genmap7) are
    restyled by the hook below; here: a row of red high-back booths against the east side and cube poufs by the void."""
    y = C5.Y_1
    BLUE, GREEN, RED, TAN = (58, 70, 140), (112, 172, 72), (196, 44, 56), (210, 180, 120)
    with G.Group("StudyLounge"):
        for z in (-152, -141, -130, -119):
            C5.rect("BoothSeat", 83, 86, y, y + 1.8, z - 3, z + 3, RED, "Fabric")
            C5.rect("BoothBack", 86, 87, y + 1.8, y + 6.4, z - 3, z + 3, RED, "Fabric", collide=False)
            for s_ in (-1, 1):
                C5.rect("BoothSide", 83, 87, y + 1.8, y + 5.4, z + s_ * 3 - 0.3, z + s_ * 3 + 0.3, RED, "Fabric", collide=False)
            disc("BoothTable", 80.5, y + 2.8, z, 3.6, 0.3, (150, 104, 70), "WoodPlanks", collide=False)
        cols = [BLUE, GREEN, RED, TAN]
        for q, z in enumerate((-152, -149, -138, -135, -124, -121)):   # between the wing planters (z -144/-130/-116)
            box("CubePouf", (2.2, 2.0, 2.2), (59.2, y + 1.0, z), cols[q % 4], "Fabric")
        sign("LoungeSign", "منطقة الدراسة | Study Lounge", (73, y + 11, -159.4), (18, 2.4, 0.4), "Back", bg=(40, 60, 90))


def auditorium_details():
    """lecture hall: wood back wall with vertical light strips + curved white ceiling bands (photo 18)"""
    y = C5.Y_1
    with G.Group("AuditoriumDetails"):
        C5.rect("HallWoodWall", -67.6, -40.4, y + 1, y + 14, -36.8, -36.3, (176, 126, 84), "WoodPlanks", collide=False)
        for x in range(-64, -42, 4):
            C5.rect("HallLightStrip", x - 0.2, x + 0.2, y + 2, y + 13, -37.0, -36.8, (255, 236, 200), "Neon", collide=False,
                    shadow=False)
        for z in (-88, -72, -56):
            box("CeilingBand", (27, 0.8, 4), (-54, y + 14.2, z), (246, 246, 242), "SmoothPlastic", rot=(8, 0, 0), collide=False)


def north_details():
    """north building: the low limestone 'College of Science' wall seen at the north entrance (TikTok frame)"""
    oz = C5.NB_SHIFT
    with G.Group("NorthEntrance"):
        box("ScienceWall", (26, 3.4, 2.2), (44, 1.7, 20 + oz - 16), (226, 214, 190), "Limestone",
            text=dict(face="Front", text="كلية العلوم\nCOLLEGE OF SCIENCE", color=(90, 76, 56), bg=(226, 214, 190), bg_t=0.0))
        for x in range(-76, 100, 12):
            C5.rect("Terracotta", x - 5.5, x + 5.5, 0.2, 3, 20 + oz - 0.6, 20 + oz - 0.2, TERRACOTTA, "Brick", collide=False)


# ---------------------------------------------------------------- hooks into the old south building
def install():
    orig_pwx = C5.panel_wall_x
    orig_pwz = C5.panel_wall_z
    orig_col = C5.column
    orig_rect = C5.rect
    orig_south = C5.south_building

    def pwx(x0, x1, z, y0, y1, face, holes=True, ribbons=()):
        if _in_south[0] and abs(z - FRONT_Z) < 0.01:
            # the front wall behind the screen: flanks keep their cladding, the bay is glazing (entrance_bay)
            orig_pwx(x0, -CENTER, z, y0, y1, face, False, ribbons)
            orig_pwx(CENTER, x1, z, y0, y1, face, False, ribbons)
            orig_pwx(-CENTER, CENTER, z, Y_BAY_TOP, y1, face, False, ())
            return
        return orig_pwx(x0, x1, z, y0, y1, face, holes, ribbons)

    def pwz(z0, z1, x, y0, y1, face, ribbons=()):
        if _in_south[0] and abs(z0 - FRONT_Z) < 0.01:
            # the side walls stay, without perforations (the bronze side wrap carries the pattern)
            orig_rect("Cladding", x - 0.8, x + 0.8, y0, y1, z0, z1, C5.PANEL, "Concrete")
            return
        return orig_pwz(z0, z1, x, y0, y1, face, ribbons)

    def col(x, z, y0, y1, d=5.0, col_=C5.CREAM, mat="Concrete"):
        if _in_south[0] and abs(z - (FRONT_Z + 2)) < 0.01 and abs(x) < CENTER:
            return orig_col(x, z, y0, Y_BAY_TOP, 6.4, COLUMN_WHITE, mat)   # tall white columns of the entrance bay
        if _in_south[0] and abs(z - (FRONT_Z + 2)) < 0.01:
            return orig_col(x, z, y0, y1, d, COLUMN_WHITE, mat)
        return orig_col(x, z, y0, y1, d, col_, mat)

    def rect(name, x0, x1, y0, y1, z0, z1, colour, mat="SmoothPlastic", **kw):
        if _in_south[0] and name in ("Soffit", "Timber") and x0 < -CENTER and x1 > CENTER:
            orig_rect(name, x0, -CENTER, y0, y1, z0, z1, colour, mat, **kw)
            orig_rect(name, CENTER, x1, y0, y1, z0, z1, colour, mat, **kw)
            return None
        if name == "Strip" and z1 <= FRONT_Z + 0.01 and z0 < FRONT_Z:
            # plaza stripes: the real plaza is light limestone in close beige tones, not multicoloured
            pal = [(226, 216, 200), (214, 204, 186), (232, 224, 210), (206, 194, 176)]
            colour = pal[int((x0 + 300) / 6) % 4]
        return orig_rect(name, x0, x1, y0, y1, z0, z1, colour, mat, **kw)

    def south():
        _in_south[0] = True
        try:
            orig_south()
        finally:
            _in_south[0] = False
        south_screen()
        entrance_bay()   # v33: wings are built by ku_science33.wings() (enterable)

    import genmap7 as G7
    orig_g7_box, orig_g7_sign = G7.box, G7.sign
    LOUNGE_COLS = [(112, 172, 72), (58, 70, 140), (232, 112, 58)]
    lounge_n = [0]

    def g7_box(name, size, pos, colour, mat="Plastic", **kw):
        if name == "Lounge" and abs(pos[1] - (C5.Y_1 + 1)) < 0.01:
            # the plain wing loungers become the green / blue / orange sofa modules of the real study lounge
            c = LOUNGE_COLS[lounge_n[0] % 3]
            lounge_n[0] += 1
            orig_g7_box("Lounge", size, pos, c, "Fabric", **kw)
            back = (pos[0] + (1.6 if pos[0] > 0 else -1.6), pos[1] + 1.8, pos[2])
            return orig_g7_box("LoungeBack", (0.8, 1.8, size[2]), back, c, "Fabric", collide=False)
        return orig_g7_box(name, size, pos, colour, mat, **kw)

    def g7_sign(name, *a, **kw):
        if name == "FacadeName":
            return None   # the real facade has no lettering band; the name sits over the entrance (entrance_bay)
        return orig_g7_sign(name, *a, **kw)

    G7.box, G7.sign = g7_box, g7_sign

    C5.panel_wall_x = pwx
    C5.panel_wall_z = pwz
    C5.column = col
    C5.rect = rect
    C5.south_building = south


def build():
    """everything that is added after the old campus (call with no offset)"""
    plaza()   # v33: the round faculty_club() is replaced by ku_science33.central_ring()
    study_lounge()
    auditorium_details()
    north_details()
