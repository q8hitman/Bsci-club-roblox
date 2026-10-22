"""v9 campus dressing: the lobby gets furniture + the portal to the club HQ (the quiz/gates moved to the HQ),
Starbucks in the north building, cats and memory signs along the garden walk, parking, flags, a bus stop,
BSC logo boards on walls (never on the floor)."""
import math
import random

import genmap as G
import genmap3 as C3
import genmap5 as C5
import bsc_art as A
import hq

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(9119)

CLUB = (24, 80, 56)


# ---------------------------------------------------------------- hooks into the old campus builder
_orig_base = C5._base_part


def _base_part_v9(name, size, pos, *a, **k):
    """the old Challenge Hall sign points to the HQ portal; desert sand colour"""
    # v37: CampusSpawn (in the south building lobby) is THE start point again; the island pad is a destination only
    if name == "Desert":
        a = ((196, 166, 118), "Sand") + tuple(a[2:])   # same warm sand as the Terrain dunes around it
    if name == "ToHall" and k.get("text"):
        k["text"] = dict(k["text"], text="بوابة مقر النادي داخل البهو ←\nBSC HQ portal inside")
    return _orig_base(name, size, pos, *a, **k)


C5._base_part = _base_part_v9

_orig_floor_slab = C5.floor_slab


def _floor_slab_v9(y, x0, x1, z0, z1, voids, col, mat="Concrete", thick=1.2, name="Floor"):
    """cut the roofs open above the skylights (the solid roof hid them and left both atriums dark)"""
    if name == "Roof":
        voids = list(voids) + ([(-50, 50, -150, -110)] if y == C5.Y_ROOF else [(10, 70, 56, 104)])
    return _orig_floor_slab(y, x0, x1, z0, z1, voids, col, mat, thick, name)


C5.floor_slab = _floor_slab_v9

_orig_light_panel = C5.light_panel


def _light_panel_v9(x, y, z, sx, sz, intensity=1.1, rng_=34):
    """many ceiling lights were placed inside the floor slab above them (slabs are 1.2 thick, roofs 1.6),
    so the glowing panel was hidden; hang every one just under its slab"""
    for level in (24.0, 40.0, 56.0, 72.0):
        if level - 1.3 <= y <= level:
            y = level - 1.6
    for roof in (88.0, 64.0):
        if roof - 1.7 <= y <= roof:
            y = roof - 2.0
    return _orig_light_panel(x, y, z, sx, sz, intensity, rng_)


C5.light_panel = _light_panel_v9

_orig_panel_wall_z = C5.panel_wall_z


_orig_panel_wall_x = C5.panel_wall_x


def _ribbons_both_sides(axis, a0, a1, c, y0, y1, ribbons):
    """window ribbons on BOTH faces of the cladding (several facades had them only on the inside,
    which left big blank white walls outside), plus slim mullions so they read as windows"""
    for ya, yb in ribbons:
        bridge_gap = axis == "x" and (a0, a1, c, ya) == (-90, 90, -30, 30)
        for s_ in (-1, 1):
            if axis == "z":
                rect("Ribbon", c + s_ * 0.8, c + s_ * 1.05, ya, yb, a0 + 1, a1 - 1, C5.GLASS_DK, "Glass", transp=0.25,
                     collide=False)
            else:
                spans = ((a0 + 1, -50), (-30, a1 - 1)) if bridge_gap else ((a0 + 1, a1 - 1),)
                for xa, xb in spans:
                    rect("Ribbon", xa, xb, ya, yb, c + s_ * 0.8, c + s_ * 1.05, C5.GLASS_DK, "Glass", transp=0.25,
                         collide=False)
        for m in range(int(a0) + 6, int(a1) - 2, 9):
            if bridge_gap and -50 < m < -30:
                continue  # v44: the existing red corridor entrance, not a real-room claim
            for s_ in (-1, 1):
                if axis == "z":
                    rect("Mullion", c + s_ * 1.0, c + s_ * 1.2, ya, yb, m - 0.3, m + 0.3, (220, 222, 226), "SmoothPlastic",
                         collide=False)
                else:
                    rect("Mullion", m - 0.3, m + 0.3, ya, yb, c + s_ * 1.0, c + s_ * 1.2, (220, 222, 226), "SmoothPlastic",
                         collide=False)


def _panel_wall_z_v9(z0, z1, x, y0, y1, face, ribbons=()):
    _orig_panel_wall_z(z0, z1, x, y0, y1, face, ())
    _ribbons_both_sides("z", z0, z1, x, y0, y1, ribbons or [(30, 36), (46, 52)])


def _panel_wall_x_v9(x0, x1, z, y0, y1, face, holes=True, ribbons=()):
    _orig_panel_wall_x(x0, x1, z, y0, y1, face, holes, ())
    _ribbons_both_sides("x", x0, x1, z, y0, y1, ribbons or [(30, 36), (46, 52)])


C5.panel_wall_z = _panel_wall_z_v9
C5.panel_wall_x = _panel_wall_x_v9


# ---------------------------------------------------------------- south lobby
def sofa_set(x, z, col):
    rect("Sofa", x - 6, x + 6, 0, 2.2, z - 2, z + 2, col, "Fabric")
    rect("SofaBack", x - 6, x + 6, 2.2, 5, z - 2.6, z - 1.6, tuple(max(0, v - 20) for v in col), "Fabric", collide=False)
    for s_ in (-1, 1):
        rect("Armchair", x + s_ * 9 - 2, x + s_ * 9 + 2, 0, 2.2, z + 4, z + 8, col, "Fabric")
    rect("CoffeeTable", x - 3, x + 3, 0, 1.8, z + 4, z + 8, (240, 238, 232), "Marble")
    ball("Vase", x, 2.6, z + 6, 1.4, (250, 200, 80), "SmoothPlastic", collide=False)


def lobby():
    # portal to the club HQ where the quiz ring used to be
    hq.portal("Portal|HQ", 0, -106, 16, 15, (120, 255, 200), "🏠 مقر نادي العلوم البيولوجية", 0, -1,
              "الأسئلة • الباركور • قطار التخصصات")  # v30: Arabic only (mixed Arabic/English lines render scrambled)
    # a logo hanging in the atrium, facing the entrance
    for s_ in (-1, 1):
        vcyl("LogoCable", s_ * 5, 36, 38.8, -128, 0.2, (60, 60, 64), "Metal", collide=False)
    A.logo_board(0, 33, -128, R=0.95, nx=0.0, nz=-1.0)
    for x in (-40, 40):
        for z in (-150, -128, -110):
            C5.light_panel(x, 38.4, z, 10, 4, 1.6, 38)
    for x, col in ((-28, (60, 110, 86)), (28, (110, 70, 150))):
        sofa_set(x, -126, col)
    for x in (-14, 14):
        box("InfoScreen", (8, 5, 0.6), (x, 6.5, -140), (20, 24, 32), "SmoothPlastic",
            text=dict(face="Front", text="أهلاً بكم في كلية العلوم\nWelcome to the College of Science" if x < 0 else
                      "📅 فعاليات النادي تنزل على ديسكورد\ndiscord.gg/8hw9hBn27", color=(255, 255, 255), bg=(20, 50, 80), bg_t=0.0))
        vcyl("ScreenPole", x, 0, 4, -140, 0.6, (90, 90, 96), "Metal", collide=False)
    # v59 (owner): the memory wall, its title and the ten memory cards were removed
    for x in (-52, 52):
        for k in range(2):
            box("Vending", (4, 9, 3), (x + k * 4.4 * (1 if x < 0 else -1), 4.5, -96), [(200, 40, 40), (40, 90, 170)][k],
                "SmoothPlastic", collide=False)
            box("VendGlass", (3, 5, 0.2), (x + k * 4.4 * (1 if x < 0 else -1), 5.5, -97.6), (200, 230, 240), "Glass", transp=0.3,
                collide=False)
    for (x, z) in ((-44, -150), (44, -150), (-44, -112), (44, -112), (-20, -98), (20, -98)):
        C3.planter(x, 0, z, 6, 3)
    sign("TrainDirection", "🚋 محطة قطار الخلية: الحديقة الشرقية →", (56.6, 8, -120), (0.3, 2.6, 18), "Left", bg=(110, 50, 150))


def lobby_light_and_banners():
    """light the dim lobby edges under the first floor; hang a banner per specialty in the atrium"""
    for x in (-70, -48, 48, 70):
        for z in (-150, -128, -108):
            C5.light_panel(x, 22.4, z, 8, 4, 1.6, 34)
    names = [("🌿 بيولوجيا نبات", (120, 190, 110)), ("🐢 بيولوجيا حيوان", (110, 170, 220)), ("🦠 مايكروبيولوجي", (230, 140, 170)),
             ("⚗️ بايوكيمستري", (200, 160, 230)), ("🧬 مولكلر", (90, 200, 160)), ("🌴 الزراعة", (220, 180, 90)),
             ("🔎 الأدلة الجنائية", (240, 200, 70)), ("🧪 البايوتكنولوجي", (100, 190, 240))]
    slots = [(-45, -152), (-27, -152), (27, -152), (45, -152), (-45, -112), (-27, -112), (27, -112), (45, -112)]
    for (x, z), (txt, col) in zip(slots, names):
        # the atrium is open from G up to the L2 slab (y 38.8): banners hang just under it
        box("BannerRod", (7, 0.4, 0.4), (x, 37.6, z), (70, 70, 76), "Metal", collide=False)
        vcyl("BannerCable", x, 37.6, 38.8, z, 0.15, (60, 60, 64), "Metal", collide=False)
        for face, dz in (("Front", -0.11), ("Back", 0.11)):
            box("Banner", (6, 11, 0.16), (x, 31.9, z + dz), col, "Fabric", collide=False,
                text=dict(face=face, text=txt, color=(255, 255, 255), bg=col, bg_t=0.0))


def club_office_portal():
    y = C5.Y_M
    G.part("Portal|HQ", (6, 9, 0.5), (85, y + 4.7, -128.7), (120, 255, 200), "Neon", transp=0.4, collide=False, shadow=False)
    sign("OfficePortalSign", "🏠 ادخل مقر النادي", (85, y + 10.2, -128.9), (7, 1.6, 0.3), "Front", bg=CLUB)
    A.logo_board(62.6, y + 22, -150, R=0.8, nx=-1.0, nz=0.0)


# ---------------------------------------------------------------- north building: BSC student lounge counter
def north_extra():
    C5._off[2] = C5.NB_SHIFT
    C5.counter(-5, 142, 0, 22, 4, (24, 80, 56), "نادي العلوم البيولوجية | BSC Lounge", "Front")
    C5._off[2] = 0.0


# ---------------------------------------------------------------- the garden walk: cats + pergolas
WALK_NOTES = []


def garden_life():
    ctrl = [(-40, -30), (-62, 4), (-34, 30), (14, 40), (58, 58), (74, 84), (44, 108), (10, 118), (8, 130)]
    path = C5._catmull(ctrl, 12)

    def near_path(x, z, d):
        return any(math.hypot(px - x, pz - z) < d for px, pz in path)
    # cats in little groups beside the path, each with a bowl
    for n, i in enumerate(range(6, len(path) - 4, 9)):
        px, pz = path[i]
        dx, dz = path[i + 1][0] - px, path[i + 1][1] - pz
        L = math.hypot(dx, dz) or 1
        nx, nz = dz / L, -dx / L
        s_ = 1 if n % 2 else -1
        cx, cz = px + nx * s_ * 9.2, pz + nz * s_ * 9.2
        face = math.degrees(math.atan2(-nx * s_, -nz * s_))
        A.cat(cx, 0.2, cz, face, ["sit", "loaf", "walk"][n % 3])
        if n % 2 == 0:
            A.cat(cx + dx / L * 3, 0.2, cz + dz / L * 3, face + 40, "loaf")
        A.cat_bowl(cx - dx / L * 2.6, 0.2, cz - dz / L * 2.6)
    # flowering pergolas over the walk
    for i in (20, 52, 84):
        if i >= len(path) - 1:
            continue
        px, pz = path[i]
        dx, dz = path[i + 1][0] - px, path[i + 1][1] - pz
        L = math.hypot(dx, dz) or 1
        nx, nz = dz / L, -dx / L
        yaw = math.degrees(math.atan2(dx, dz))
        for k in (-3, 0, 3):
            bx, bz = px + dx / L * k, pz + dz / L * k
            for s_ in (-1, 1):
                vcyl("PergolaPost", bx + nx * s_ * 7.4, 0, 11, bz + nz * s_ * 7.4, 0.8, (240, 236, 226), "Wood", collide=False)
            G.part("PergolaBeam", (16, 0.8, 0.8), (bx, 11.2, bz), (240, 236, 226), "Wood", rot=(0, yaw + 90, 0), collide=False)
        for q in range(10):
            ball("Bougainvillea", px + nx * rng.uniform(-7, 7) + dx / L * rng.uniform(-4, 4), 11.6 + rng.uniform(0, 1.4),
                 pz + nz * rng.uniform(-7, 7) + dz / L * rng.uniform(-4, 4), rng.uniform(1.6, 2.6),
                 rng.choice([(220, 70, 150), (240, 110, 180), (90, 160, 80)]), "Grass", collide=False)
    # butterflies over the flower beds
    for q in range(14):
        i = rng.randrange(len(path))
        px, pz = path[i]
        x, z = px + rng.uniform(-18, 18), pz + rng.uniform(-18, 18)
        if near_path(x, z, 7):
            continue
        col = rng.choice([(255, 200, 60), (180, 120, 255), (255, 140, 200), (120, 210, 255)])
        for s_ in (-1, 1):
            G.part("Butterfly", (0.1, 0.7, 0.7), (x + s_ * 0.35, rng.uniform(4, 7), z), col, "Neon", rot=(0, 0, s_ * 30),
                   collide=False, shadow=False)
    # a small fountain in the widest bend
    fx, fz = 28, 64
    if not near_path(fx, fz, 12):
        disc("FountainBasin", fx, 0.8, fz, 14, 1.6, (226, 220, 206), "Concrete")
        disc("FountainWater", fx, 1.5, fz, 12.6, 0.2, (120, 190, 230), "Glass", transp=0.3, collide=False)
        vcyl("FountainJet", fx, 1.6, 6, fz, 0.8, (200, 230, 255), "Neon", transp=0.3, collide=False, shadow=False)
        ball("FountainTop", fx, 6.2, fz, 2.2, (200, 230, 255), "Neon", transp=0.4, collide=False, shadow=False)


# ---------------------------------------------------------------- outdoors
def outdoors_extra():
    # parking lots east/west of the forecourt
    for sx in (-1, 1):
        x0, x1 = (150, 250) if sx > 0 else (-250, -150)
        rect("Parking", x0, x1, -1, 0.02, -248, -176, (78, 80, 86), "Asphalt")
        for q in range(9):
            x = x0 + 6 + q * 11
            rect("ParkLine", x - 0.25, x + 0.25, 0.02, 0.06, -248, -232, (240, 240, 235), "SmoothPlastic", collide=False)
            rect("ParkLine", x - 0.25, x + 0.25, 0.02, 0.06, -192, -176, (240, 240, 235), "SmoothPlastic", collide=False)
            if rng.random() < 0.75:
                A.car(x + 5.5, 0.02, -240, 0)
            if rng.random() < 0.6:
                A.car(x + 5.5, 0.02, -184, 180)
    # Kuwait flags at the forecourt
    for x in (-50, -42, 42, 50):
        A.flag_pole(x, 0, -236)
    # bus stop
    rect("BusShelterRoof", -132, -112, 9, 9.6, -262, -254, (40, 90, 150), "SmoothPlastic")
    for x in (-131, -113):
        vcyl("BusPost", x, 0, 9, -261, 0.6, (90, 90, 96), "Metal", collide=False)
    rect("BusBench", -128, -116, 1.6, 2.2, -261, -259, (150, 100, 62), "WoodPlanks", collide=False)
    sign("BusSign", "🚌 باص الجامعة | KU Shuttle", (-122, 11.2, -262), (14, 2.2, 0.3), "Front", bg=(40, 90, 150))
    # umbrella tables by the outdoor cafes
    for (x, z, col) in ((96, -120, (140, 90, 180)), (96, -134, (140, 90, 180)), (100, -178, (96, 70, 56)),
                        (104, 50 + C5.NB_SHIFT, (70, 130, 80)), (126, 50 + C5.NB_SHIFT, (70, 130, 80))):
        A.umbrella_table(x, 0, z, col)
    # logo boards: on the south building's garden facade and at the train station
    A.logo_board(0, 70, -29.2, R=2.0, nx=0.0, nz=1.0)
    A.logo_board(171.4, 26, -40, R=1.0, nx=-1.0, nz=0.0)
    G.part("TrainSpawnPoint", (6, 1, 6), (138, 1.9, -47), (0, 0, 0), "SmoothPlastic", rot=(0, 180, 0), transp=1,
           collide=False)   # v63: face the train (+z)
    # more shade trees along the lawns (kept clear of paths and the station)
    for (x, z) in ((140, 120), (-100, 250)):
        C3.tree(x, 0.0, z, 1.2)


DESERT_PLANTS = [("العرفج", "Rhanterium", "نبتة الكويت الوطنية 🌼"), ("السدر", "Ziziphus", "شجرة معمّرة وتتحمل الحر"),
                 ("الطلح", "Acacia", "تثبّت النيتروجين بالتربة"), ("الرمث", "Haloxylon", "تتحمل الملوحة"),
                 ("النخيل", "Phoenix dactylifera", "رمز الخليج 🌴"), ("الحمض", "Salsola", "نبات ملحي"),
                 ("الثمام", "Panicum turgidum", "عشب يثبّت الرمال"), ("الأرطى", "Calligonum", "جذوره تمسك الكثبان")]


def desert_garden():
    """west lawn: a walk through Kuwait's desert plants, each bed labelled"""
    # v52 (owner: exactly ONE south-north connection = the Red Corridor): the trail stays inside the desert garden and
    # no longer runs on to the north building; its link into the north promenade was removed.
    rect("GardenWalk", -146, -134, 0.15, 0.4, -182, 100, (214, 200, 170), "Pebble", collide=False)
    sign("DesertGardenSign", "🌵 حديقة نباتات الكويت الصحراوية | Desert Plants Garden", (-140, 6, -166), (26, 3.4, 0.4), "Front",
         bg=(120, 90, 40))
    for i, (ar, sci, note) in enumerate(DESERT_PLANTS):
        z = -150 + i * 58           # east-side beds fall between the lawn trees
        x = -160 if i % 2 else -120
        rect("Bed", x - 8, x + 8, 0.15, 1.0, z - 6, z + 6, (200, 176, 130), "Sand")
        rect("BedEdge", x - 8.4, x + 8.4, 0.15, 1.2, z - 6.4, z - 6.0, (150, 130, 100), "Limestone", collide=False)
        if ar == "النخيل":
            C5.palm(x, z, 15)
        elif ar in ("السدر", "الطلح"):
            vcyl("Trunk", x, 1, 8, z, 1.2, (110, 80, 50), "Wood", collide=False)
            ball("Crown", x, 11, z, 11, (110, 140, 70), "Grass", collide=False)
            ball("Crown", x + 3, 9.5, z + 2, 7, (100, 130, 64), "Grass", collide=False)
        else:
            for q in range(5):
                ball("Shrub", x + rng.uniform(-5, 5), 2.2, z + rng.uniform(-3.5, 3.5), rng.uniform(2.4, 4),
                     (rng.randint(120, 160), rng.randint(140, 170), rng.randint(70, 90)), "Grass", collide=False)
            if ar == "العرفج":
                for q in range(10):
                    ball("Bloom", x + rng.uniform(-5, 5), 4.0, z + rng.uniform(-3.5, 3.5), 0.9, (250, 220, 60), "SmoothPlastic",
                         collide=False)
        # label on the walk side of the bed, facing the walk
        px = x + (8.6 if x < -140 else -8.6)
        vcyl("LabelPost", px, 0, 3.2, z, 0.4, (90, 70, 50), "Wood", collide=False)
        sign("PlantLabel", "\n".join((ar, sci, note)), (px, 4.6, z), (0.3, 3.4, 8), "Right" if x < -140 else "Left",
             color=(40, 40, 30), bg=(250, 244, 226))
    # a shaded reading corner
    rect("ShadeRoof", -150, -130, 10, 10.6, 214, 236, (240, 236, 226), "WoodPlanks")
    for (x, z) in ((-149, 215), (-131, 215), (-149, 235), (-131, 235)):
        vcyl("ShadePost", x, 0, 10, z, 0.8, (200, 190, 170), "Wood", collide=False)
    for z in (219, 231):
        C3.bench(-140, 0.0, z, along="x")


def garden_extra():
    """v31: the desert garden beds were a few identical green balls. Each bed now shows its plant's real character and a
    carpet of spring wildflowers (Kuwait's desert blooms after the winter rains). Uses its own RNG, so every other random
    placement in the campus stays exactly where it was tested."""
    r = random.Random(4242)
    WILD = [(250, 220, 60), (190, 120, 230), (250, 250, 245), (240, 140, 180)]
    for i, (ar, sci, note) in enumerate(DESERT_PLANTS):
        z = -150 + i * 58
        x = -160 if i % 2 else -120
        rect("BedMulch", x - 7.6, x + 7.6, 1.0, 1.08, z - 5.6, z + 5.6, (176, 150, 112), "Pebble", collide=False)
        if ar == "الرمث":      # Haloxylon: leafless, jointed green stems
            for q in range(14):
                bx, bz = x + r.uniform(-5, 5), z + r.uniform(-3.5, 3.5)
                h = r.uniform(2.5, 5)
                vcyl("JointedStem", bx, 1, 1 + h, bz, 0.35, (120, 150, 90), "Grass", collide=False)
                ball("Joint", bx, 1 + h * 0.6, bz, 0.6, (140, 170, 100), "Grass", collide=False, shadow=False)
        elif ar == "الثمام":    # Panicum: tall grass tufts
            for q in range(8):
                bx, bz = x + r.uniform(-5, 5), z + r.uniform(-3.5, 3.5)
                for b in range(6):
                    box("GrassBlade", (0.25, r.uniform(3, 5), 0.25), (bx, 2.8, bz), (160, 180, 100), "Grass",
                        rot=(r.uniform(-18, 18), r.uniform(0, 180), r.uniform(-18, 18)), collide=False, shadow=False)
        elif ar == "الأرطى":    # Calligonum: wiry broom shrubs with red-pink fruits
            for q in range(4):
                bx, bz = x + r.uniform(-4, 4), z + r.uniform(-3, 3)
                for b in range(7):
                    box("Twig", (0.2, 4, 0.2), (bx, 3, bz), (150, 160, 110), "Wood",
                        rot=(r.uniform(-30, 30), r.uniform(0, 180), r.uniform(-30, 30)), collide=False, shadow=False)
                for b in range(5):
                    ball("CalligonumFruit", bx + r.uniform(-1.4, 1.4), r.uniform(3.4, 5), bz + r.uniform(-1.4, 1.4), 0.7,
                         (230, 90, 110), "SmoothPlastic", collide=False, shadow=False)
        elif ar == "الحمض":     # Salsola: rounded grey-green salt bushes with pinkish tips
            for q in range(5):
                bx, bz = x + r.uniform(-4.5, 4.5), z + r.uniform(-3, 3)
                ball("SaltBush", bx, 2.4, bz, r.uniform(2.6, 3.6), (150, 170, 130), "Grass", collide=False)
                ball("SaltTip", bx, 3.8, bz, 1.2, (220, 160, 170), "Grass", collide=False, shadow=False)
        # spring wildflowers around every bed edge
        for q in range(16):
            side = q % 4
            fx = x + (r.uniform(-7, 7) if side < 2 else (7.2 if side == 2 else -7.2))
            fz = z + ((5.2 if side == 0 else -5.2) if side < 2 else r.uniform(-5, 5))
            vcyl("FlowerStem", fx, 1.05, 1.9, fz, 0.15, (90, 150, 70), "Grass", collide=False, shadow=False)
            ball("WildFlower", fx, 2.0, fz, 0.7, r.choice(WILD), "SmoothPlastic", collide=False, shadow=False)


def events_plaza():
    """east lawn behind the north building: the club's events corner with a booth and a stage"""
    rect("EventsPaving", 104, 170, 0.15, 0.35, 196, 266, (226, 220, 206), "Concrete", collide=False)
    rect("Stage", 120, 160, 0.35, 3.0, 250, 264, (60, 64, 74), "WoodPlanks")
    rect("StageBack", 120, 160, 3.0, 20, 263.4, 264, (24, 80, 56), "SmoothPlastic")
    A.logo_board(146, 16.5, 263.2, R=0.9, nx=0.0, nz=-1.0)
    sign("StageSign", "نادي العلوم البيولوجية • فعاليات", (130, 16, 263.2), (16, 3, 0.3), "Front", bg=(24, 80, 56))
    for x in (122, 158):
        box("Speaker", (3, 6, 3), (x, 6, 252), (30, 30, 34), "SmoothPlastic", collide=False)
    # booth with pastel hex banner
    rect("BoothTable", 108, 124, 0.35, 3.6, 204, 208, (250, 250, 248), "SmoothPlastic")
    rect("BoothCloth", 108, 124, 0.35, 3.2, 203.8, 204.2, (24, 80, 56), "Fabric", collide=False)
    for x in (108.5, 123.5):
        vcyl("BoothPole", x, 0.35, 12, 208, 0.5, (90, 90, 96), "Metal", collide=False)
    sign("BoothBanner", "🧬 سجّل بالنادي | Join BSC 🦠", (116, 11, 208.2), (15, 2.6, 0.3), "Front", bg=(110, 70, 150))
    for q in range(5):
        hexx = 110 + q * 3.2
        A.hexagon("BoothHex", hexx, 4.6, 205.6, 1.2, A.HEXES[q][1], 0.0, -1.0, thick=0.3)
    for (x, z) in ((116, 228), (134, 222), (152, 230), (126, 240)):
        A.umbrella_table(x, 0.35, z, (24, 80, 56))
    A.cat(112, 0.35, 214, 200, "loaf")


def surroundings():
    """frame the campus: palm avenues and a low hedge on its edges (the dunes beyond are Terrain,
    painted by tools/terrain_dunes.luau)"""
    for x in (-180, 180):
        rect("EdgeHedge", x - 2, x + 2, 0, 2.6, -170, 270, (70, 130, 70), "Grass", collide=False)
        for z in range(-160, 270, 26):   # starts after the parking lots
            C5.palm(x + (6 if x < 0 else -6), z, 16 + (z % 3))
    rect("BackHedge", -178, 178, 0, 2.6, 274, 278, (70, 130, 70), "Grass", collide=False)
    for x in range(-170, 171, 26):
        C5.palm(x, 268, 16)


def build():
    surroundings()
    lobby_light_and_banners()
    desert_garden()
    garden_extra()
    events_plaza()
    lobby()
    club_office_portal()
    north_extra()
    garden_life()
    outdoors_extra()
