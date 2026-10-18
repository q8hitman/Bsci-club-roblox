"""Generates kuwait-parkour/src/map/Map.rbxmx : the whole themed course as static parts.

World layout (studs):
  hub (club HQ + plaza)  z in [-72, -8]
  zone j (10 levels each) z in [140(j-1)-7, 140 j - 7],  x in [-56, 56]
  level k lane centre z = 14 (k-1), alternating direction, +1.5 stud rise per level
Run:  python tools/genmap.py kuwait-parkour/src/map/Map.rbxmx
"""
import math
import random
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
rng = random.Random(1114)

MAT = dict(Plastic=256, SmoothPlastic=272, Neon=288, Wood=512, WoodPlanks=528, Marble=784,
           Slate=800, Concrete=816, Granite=832, Pavement=836, Brick=848, Cobblestone=880,
           Metal=1088, DiamondPlate=1056, Pebble=864, Limestone=820, Sandstone=912, Rock=896, Basalt=788, Asphalt=1376, Ground=1360, Grass=1280, Sand=1296, Fabric=1312, Ice=1536, Glass=1568, ForceField=1584)
SURF = dict(Right=0, Top=1, Back=2, Left=3, Bottom=4, Front=5)
SHAPE = dict(Ball=0, Block=1, Cylinder=2)

# palette
CREAM = (226, 214, 190); TAN = (201, 168, 120); SAND = (214, 190, 150)
GLASSG = (110, 165, 145); SLATE = (78, 84, 94); DARK = (40, 44, 52); SILVER = (170, 175, 182)
RED = (176, 48, 44); WHITE = (240, 240, 238); WOOD = (160, 110, 70); GREEN = (46, 160, 90)
PURPLE = (110, 60, 160); BLUE = (60, 100, 170); YELLOW = (235, 190, 40); BRICK = (150, 72, 55)
LEAF = (60, 140, 60); ROCK = (150, 150, 145); PINK = (255, 90, 170); CYAN = (60, 220, 255)
GOLD = (230, 180, 50); ORANGE = (230, 120, 40); TAUPE = (150, 140, 135); BLACK = (25, 25, 28)

buf = []
cnt = [0]
check = []          # (kind, cx, cz, top_y, w) in walking order, for the jump validator
checkpoints = {}    # level -> (x, y, z)
nparts = [0]


def rid():
    cnt[0] += 1
    return "RBX%d" % cnt[0]


def fl(v):
    return format(float(v), ".4f")


def rotmat(rx=0, ry=0, rz=0):
    a, b, c = math.radians(rx), math.radians(ry), math.radians(rz)
    ca, sa, cb, sb, cc, sc = math.cos(a), math.sin(a), math.cos(b), math.sin(b), math.cos(c), math.sin(c)
    return [[cc * cb, cc * sb * sa - sc * ca, cc * sb * ca + sc * sa],
            [sc * cb, sc * sb * sa + cc * ca, sc * sb * ca - cc * sa],
            [-sb, cb * sa, cb * ca]]


def cfxml(x, y, z, rot):
    r = rotmat(*rot)
    return ('<CoordinateFrame name="CFrame"><X>%s</X><Y>%s</Y><Z>%s</Z>'
            '<R00>%s</R00><R01>%s</R01><R02>%s</R02><R10>%s</R10><R11>%s</R11><R12>%s</R12>'
            '<R20>%s</R20><R21>%s</R21><R22>%s</R22></CoordinateFrame>') % (
        fl(x), fl(y), fl(z), fl(r[0][0]), fl(r[0][1]), fl(r[0][2]), fl(r[1][0]), fl(r[1][1]),
        fl(r[1][2]), fl(r[2][0]), fl(r[2][1]), fl(r[2][2]))


def col32(c):
    return 4278190080 + (c[0] << 16) + (c[1] << 8) + c[2]


class Group:
    def __init__(self, name, cls="Folder"):
        self.name, self.cls = name, cls

    def __enter__(self):
        buf.append('<Item class="%s" referent="%s"><Properties><string name="Name">%s</string>'
                   '</Properties>' % (self.cls, rid(), escape(self.name)))

    def __exit__(self, *a):
        buf.append("</Item>")


def bidi_lines(text):
    """v35: "Arabic | English" on ONE line renders scrambled in Roblox (mixed directions); put each language on its own
    line. Lines that are only one script are left alone."""
    out = []
    for line in text.split("\n"):
        parts = [s.strip() for s in line.replace("  •  ", " | ").replace(" • ", " | ").split(" | ")]
        ar = any("؀" <= ch <= "ۿ" for ch in line)
        la = any("a" <= ch.lower() <= "z" for ch in line)
        out.extend(parts if (len(parts) > 1 and ar and la) else [line])
    return "\n".join(out)


def gui_text(face, text, size, color=WHITE, bg=None, bg_t=1.0):
    fw, fh = {"Right": (size[2], size[1]), "Left": (size[2], size[1]), "Top": (size[0], size[2]),
              "Bottom": (size[0], size[2]), "Front": (size[0], size[1]), "Back": (size[0], size[1])}[face]
    bgc = bg or (0, 0, 0)
    text = bidi_lines(text)
    return ('<Item class="SurfaceGui" referent="%s"><Properties><string name="Name">Label</string>'
            '<token name="Face">%d</token><token name="SizingMode">0</token>'
            '<Vector2 name="CanvasSize"><X>%d</X><Y>%d</Y></Vector2>'
            '<bool name="AlwaysOnTop">false</bool><float name="LightInfluence">0</float></Properties>'
            '<Item class="TextLabel" referent="%s"><Properties><string name="Name">T</string>'
            '<UDim2 name="Size"><XS>1</XS><XO>0</XO><YS>1</YS><YO>0</YO></UDim2>'
            '<string name="Text">%s</string><bool name="TextScaled">true</bool>'
            '<token name="Font">4</token>'
            '<Color3 name="TextColor3"><R>%s</R><G>%s</G><B>%s</B></Color3>'
            '<Color3 name="BackgroundColor3"><R>%s</R><G>%s</G><B>%s</B></Color3>'
            '<float name="BackgroundTransparency">%s</float><int name="BorderSizePixel">0</int>'
            '</Properties></Item></Item>') % (
        # fixed ~100px-tall canvas: TextScaled caps at 100px, so text now fills big boards instead of staying tiny
        rid(), SURF[face], max(int(100 * fw / max(fh, 0.1)), 20), 100, rid(), escape(text),
        fl(color[0] / 255), fl(color[1] / 255), fl(color[2] / 255),
        fl(bgc[0] / 255), fl(bgc[1] / 255), fl(bgc[2] / 255), fl(bg_t))


def part(name, size, pos, color, mat="Plastic", shape="Block", rot=(0, 0, 0), transp=0.0,
         collide=True, cls="Part", text=None, extra="", shadow=True, light=None):
    nparts[0] += 1
    p = ['<Item class="%s" referent="%s"><Properties><string name="Name">%s</string>' % (cls, rid(), escape(name)),
         cfxml(pos[0], pos[1], pos[2], rot),
         '<Vector3 name="size"><X>%s</X><Y>%s</Y><Z>%s</Z></Vector3>' % (fl(size[0]), fl(size[1]), fl(size[2])),
         '<Color3uint8 name="Color3uint8">%d</Color3uint8>' % col32(color),
         '<token name="Material">%d</token>' % MAT[mat],
         '<bool name="Anchored">true</bool>',
         '<bool name="CanCollide">%s</bool>' % ("true" if collide else "false"),
         '<bool name="CastShadow">%s</bool>' % ("true" if shadow else "false"),
         '<float name="Transparency">%s</float>' % fl(transp),
         '<token name="TopSurface">0</token><token name="BottomSurface">0</token>']
    if cls == "Part":
        p.append('<token name="shape">%d</token>' % SHAPE[shape])
    p.append(extra)
    p.append("</Properties>")
    if text:
        p.append(gui_text(text["face"], text["text"], size, text.get("color", WHITE),
                          text.get("bg"), text.get("bg_t", 1.0)))
    if light:
        lb, lr, lc = light
        p.append('<Item class="PointLight" referent="%s"><Properties><string name="Name">L</string>'
                 '<float name="Brightness">%s</float><float name="Range">%s</float>'
                 '<Color3 name="Color"><R>%s</R><G>%s</G><B>%s</B></Color3><bool name="Shadows">false</bool>'
                 '</Properties></Item>' % (rid(), fl(lb), fl(lr), fl(lc[0] / 255), fl(lc[1] / 255), fl(lc[2] / 255)))
    p.append("</Item>")
    buf.append("".join(p))


def box(name, size, pos, color, mat="Plastic", **kw):
    part(name, size, pos, color, mat, **kw)


def vcyl(name, cx, y0, y1, cz, diam, color, mat="Plastic", **kw):
    """vertical cylinder from y0 to y1"""
    h = max(y1 - y0, 0.2)
    part(name, (h, diam, diam), (cx, (y0 + y1) / 2, cz), color, mat, shape="Cylinder", rot=(0, 0, 90), **kw)


def disc(name, cx, cy, cz, diam, thick, color, mat="Plastic", **kw):
    part(name, (thick, diam, diam), (cx, cy, cz), color, mat, shape="Cylinder", rot=(0, 0, 90), **kw)


def ball(name, cx, cy, cz, d, color, mat="Plastic", **kw):
    part(name, (d, d, d), (cx, cy, cz), color, mat, shape="Ball", **kw)


def sign(name, text, pos, size, face, color=WHITE, bg=(30, 40, 50), mat="SmoothPlastic", frame=None):
    box(name, size, pos, bg, mat, text=dict(face=face, text=text, color=color, bg=bg, bg_t=0.0))


def tree(x, y, z, s=1.0):
    vcyl("Trunk", x, y, y + 6 * s, z, 0.9 * s, (95, 70, 45), "Wood", collide=False)
    ball("Leaves", x, y + 8 * s, z, 7 * s, LEAF, "Grass", collide=False)
    ball("Leaves", x + 1.5 * s, y + 6.2 * s, z + 1 * s, 4.5 * s, (70, 150, 70), "Grass", collide=False)


def rock(x, y, z, s=1.0):
    part("Rock", (3 * s, 1.8 * s, 2.4 * s), (x, y + 0.7 * s, z), ROCK, "Slate", shape="Ball",
         rot=(0, rng.uniform(0, 90), 0), collide=False)


def bench(x, y, z, along="z"):
    sx, sz = (1.6, 5) if along == "z" else (5, 1.6)
    box("Bench", (sx, 0.5, sz), (x, y + 1.4, z), (150, 100, 65), "Wood", collide=False)
    box("BenchLeg", (sx * 0.8, 1.4, sz * 0.8), (x, y + 0.7, z), DARK, "Metal", collide=False)


# ------------------------------------------------------------------ course math
ZONE_D = 140
LANE_DZ = 14
RISE = 1.5
GROUND = -34


def zone_of(k):
    return (k - 1) // 10 + 1


def floor_y(j):
    return RISE * (10 * (j - 1) + 1) - 14


def lane_params(k):
    t = (k - 1) / 99.0
    g = 3.0 + 3.5 * t
    w0 = 10 - 5 * t
    n = int(round(80 / (w0 + g))) + 1
    step = 80.0 / (n - 1)
    w = max(4.6, min(10.0, step - g))
    dirn = 1 if k % 2 == 1 else -1
    return t, n, step, w, dirn


def pattern_dy(pat, i, n):
    if i == 0 or i == n - 1:
        return 0.0
    if pat == 1:
        return 0.0
    if pat == 2:
        return min(i * 1.0, 4.0)
    if pat == 3:
        return 1.6 * math.sin(i * 1.2)
    if pat == 4:
        return 2.0 if i % 2 == 0 else 0.0
    return 0.0


def pattern_dz(pat, i, n, A):
    if pat == 1 and 0 < i < n - 1:
        return A if i % 2 == 0 else -A
    return 0.0


# ------------------------------------------------------------------ platform styles
def style_platform(j, k, i, x, y, z, w, is_pad):
    fy = floor_y(j)
    nm = "L%d_P%d" % (k, i)
    if j == 1:      # colonnade: cream discs on tall columns
        disc(nm, x, y, z, w, 1, CREAM, "Concrete")
        vcyl("Col", x, fy, y - 0.5, z, max(2.0, w * 0.55), (210, 198, 172), "Concrete", collide=False)
    elif j == 2:    # lobby: polished granite slabs on silver pillars
        box(nm, (w, 1, w), (x, y, z), (62, 66, 74), "Granite")
        box("Trim", (w, 0.2, 0.3), (x, y + 0.55, z - w / 2 + 0.15), SILVER, "Metal", collide=False)
        vcyl("Pillar", x, fy, y - 0.5, z, 2.2, SILVER, "Metal", collide=False)
    elif j == 3:    # lecture hall: red seats on grey tiers
        box(nm, (w, 1, w), (x, y, z), RED, "Fabric")
        box("SeatBack", (w, 2.6, 0.8), (x, y + 1.8, z + w / 2 - 0.4), (150, 40, 38), "Fabric", collide=False)
        box("Tier", (w * 0.8, y - 0.5 - fy, w * 0.8), (x, (y - 0.5 + fy) / 2, z), (110, 112, 118), "Slate", collide=False)
    elif j == 4:    # library: white study tables, warm lamps
        box(nm, (w, 1, w), (x, y, z), (238, 238, 232), "Marble")
        box("Leg", (w * 0.9, y - 0.5 - fy, 1.0), (x, (y - 0.5 + fy) / 2, z), WOOD, "Wood", collide=False)
        if i % 3 == 1:
            vcyl("Lamp", x + w / 2 - 1, y + 0.5, y + 3.2, z + w / 2 - 1, 0.3, DARK, "Metal", collide=False)
            part("Shade", (1.6, 2.2, 2.2), (x + w / 2 - 1, y + 3.6, z + w / 2 - 1), (255, 226, 160), "Neon",
                 shape="Cylinder", rot=(0, 0, 90), collide=False)
    elif j == 5:    # labs: benches, microscopes, beakers
        box(nm, (w, 1, w), (x, y, z), (236, 240, 242), "SmoothPlastic")
        box("Cabinet", (w * 0.9, y - 0.5 - fy, w * 0.9), (x, (y - 0.5 + fy) / 2, z), (45, 95, 100), "Metal", collide=False)
        if i % 2 == 0:
            box("Scope", (1.2, 2.0, 1.0), (x + w / 4, y + 1.5, z), (200, 205, 210), "Metal", collide=False)
            vcyl("Lens", x + w / 4, y + 2.2, y + 3.4, z, 0.5, DARK, "Metal", collide=False)
        else:
            vcyl("Beaker", x - w / 4, y + 0.5, y + 2.2, z, 1.0, CYAN, "Glass", transp=0.4, collide=False)
    elif j == 6:    # cafeteria counters
        vend = [GREEN, PURPLE, ORANGE, (50, 55, 60)][(k + i) % 4]
        box(nm, (w, 1, w), (x, y, z), (200, 160, 110) if i % 2 else (240, 238, 232),
            "WoodPlanks" if i % 2 else "Marble")
        box("Front", (w, 3.0, 0.4), (x, y - 1.7, z - w / 2), vend, "SmoothPlastic", collide=False)
        vcyl("Stool", x, fy, y - 0.5, z, 1.4, DARK, "Metal", collide=False)
    elif j == 7:    # red corridor / garden bridge
        box(nm, (w, 1, w), (x, y, z), BRICK, "Brick")
        box("Stripe", (w, 0.1, 0.8), (x, y + 0.55, z), (210, 190, 160), "Concrete", collide=False)
        box("Rail", (w, 2.0, 0.2), (x, y + 1.5, z + w / 2 - 0.1), GLASSG, "Glass", transp=0.5, collide=False)
        vcyl("Post", x, fy, y - 0.5, z, 1.6, (70, 70, 72), "Concrete", collide=False)
    elif j == 8:    # north atrium: steel drums and colourful sofas
        if i % 2 == 0:
            disc(nm, x, y, z, w, 1, (74, 78, 84), "Metal")
            vcyl("Drum", x, fy, y - 0.5, z, max(2.4, w * 0.6), (92, 96, 104), "Metal", collide=False)
        else:
            c = YELLOW if (k + i) % 2 else BLUE
            box(nm, (w, 1, w), (x, y, z), c, "Fabric")
            box("Back", (w, 1.8, 0.8), (x, y + 1.3, z + w / 2 - 0.4), c, "Fabric", collide=False)
            box("Base", (w * 0.9, y - 0.5 - fy, w * 0.9), (x, (y - 0.5 + fy) / 2, z), (60, 64, 72), "Metal", collide=False)
    elif j == 9:    # computer labs: desks and monitors
        box(nm, (w, 1, w), (x, y, z), (232, 232, 228), "SmoothPlastic")
        box("Monitor", (2.6, 1.8, 0.2), (x, y + 1.6, z + w / 4), BLACK, "SmoothPlastic", collide=False,
            text=dict(face="Front", text="BSC", color=CYAN, bg=(10, 20, 40), bg_t=0.0))
        box("Keys", (2.2, 0.15, 0.8), (x, y + 0.6, z - w / 5), (50, 50, 55), "SmoothPlastic", collide=False)
        box("Leg", (w * 0.9, y - 0.5 - fy, 1.0), (x, (y - 0.5 + fy) / 2, z), SLATE, "Metal", collide=False)
    else:           # biotechnology: petri dishes over glowing test tubes
        c = [PINK, CYAN, (120, 255, 160), (255, 220, 90)][(k + i) % 4]
        disc(nm, x, y, z, w, 1, (200, 235, 240), "Glass", transp=0.35)
        disc("Agar", x, y + 0.2, z, w * 0.8, 0.4, c, "Neon", collide=False)
        vcyl("Tube", x, fy, y - 0.5, z, 2.2, (190, 230, 240), "Glass", transp=0.5, collide=False)
        vcyl("Liquid", x, fy, y - 0.5 - max(0, (y - fy) * 0.35), z, 1.5, c, "Neon", collide=False)


# ------------------------------------------------------------------ zone dressing
ZONES = [
    dict(ar="الساحة الأمامية", en="The Courtyard", sub="College of Science • 114", c=CREAM),
    dict(ar="بهو الجنوبي", en="South Lobby", sub="Revolving doors & escalators", c=(62, 66, 74)),
    dict(ar="المدرج الأحمر", en="The Red Lecture Hall", sub="Take your seat", c=RED),
    dict(ar="المكتبة", en="The Library", sub="Quiet… and a little dangerous", c=(238, 238, 232)),
    dict(ar="المختبرات", en="Labs & Electron Microscopy", sub="Handle with care", c=(45, 95, 100)),
    dict(ar="الكافتيريا", en="The Cafeteria", sub="Salad • Larich • Old Friends • العلوم", c=ORANGE),
    dict(ar="الممر الأحمر والحديقة", en="Red Corridor & Garden", sub="Between South and North", c=BRICK),
    dict(ar="بهو الشمالي", en="North Atrium", sub="Skylights and steel", c=(90, 96, 104)),
    dict(ar="صالات الحاسوب", en="Computer Labs", sub="Level up", c=BLUE),
    dict(ar="البايوتكنولوجي", en="Biotechnology", sub="The final frontier", c=PINK),
]


FLOOR = [  # (colour, material): chosen so each zone's platforms contrast with its floor
    ((92, 96, 102), "Slate"), ((214, 210, 200), "Marble"), ((105, 104, 106), "Slate"),
    ((112, 86, 62), "WoodPlanks"), ((32, 58, 64), "Slate"), ((84, 58, 40), "WoodPlanks"),
    ((68, 108, 68), "Grass"), ((218, 218, 212), "Marble"), ((46, 52, 68), "Slate"), ((18, 22, 40), "Slate"),
]


def zone_frame(j):
    z0 = ZONE_D * (j - 1) - 7
    zc = z0 + ZONE_D / 2
    fy = floor_y(j)
    top = RISE * 10 * j + 22
    z = ZONES[j - 1]
    # building body + floor slab
    box("Body", (114, fy - GROUND - 2, ZONE_D + 2), (0, (fy - 2 + GROUND) / 2, zc), (205, 195, 175), "Concrete")
    box("Floor", (112, 2, ZONE_D), (0, fy - 1, zc), FLOOR[j - 1][0], FLOOR[j - 1][1])
    # glass walls + mullions
    for side in (-1, 1):
        for s in range(5):
            zz = z0 + 14 + s * 28
            box("Glass", (0.6, top - fy, 27), (side * 56, (top + fy) / 2, zz), GLASSG, "Glass", transp=0.55, collide=False)
            box("Mullion", (1.0, top - fy, 1.0), (side * 56, (top + fy) / 2, zz - 14), (50, 55, 62), "Metal", collide=False)
        box("Beam", (1.6, 1.4, ZONE_D), (side * 56, top, zc), (60, 66, 74), "Metal", collide=False)
    # title board (inside, facing the course) and range board
    sign("Title", "%s\n%s" % (z["ar"], z["en"]), (-55.2, fy + 24, z0 + 26), (0.6, 9, 34), "Right",
         color=WHITE, bg=tuple(max(0, v - 70) for v in z["c"]))
    sign("Sub", "%s  |  Levels %d-%d" % (z["sub"], 10 * (j - 1) + 1, 10 * j), (55.2, fy + 24, z0 + 26),
         (0.6, 5, 40), "Left", color=WHITE, bg=(30, 40, 50))


def zone_decor(j):
    z0 = ZONE_D * (j - 1) - 7
    fy = floor_y(j)
    topy = RISE * 10 * j + 18
    if j == 1:
        for zz in range(int(z0) + 10, int(z0) + ZONE_D, 20):
            for side in (-1, 1):
                vcyl("Col", side * 50, fy, topy, zz, 6.5, CREAM, "Concrete")
        # perforated facade band
        for side in (-1, 1):
            box("Facade", (3, 14, ZONE_D), (side * 52, topy + 8, z0 + ZONE_D / 2), (150, 148, 150), "Metal")
            for _ in range(70):
                box("Hole", (0.2, 1.4, 1.4), (side * 50.4, topy + 8 + rng.uniform(-5, 5), z0 + rng.uniform(2, ZONE_D - 2)),
                    (245, 245, 245), "SmoothPlastic", collide=False, rot=(rng.uniform(0, 90), 0, 0))
        sign("Plaque114", "114\nكلية العلوم\nCollege of Science", (-30, fy + 5, z0 + 6), (14, 8, 1.2), "Front",
             color=(60, 55, 45), bg=(220, 210, 190))
        for k in range(8):
            box("Planter", (10, 2, 6), (-44 + k * 12.5, fy + 1, z0 + 130), (60, 70, 62), "Concrete")
            for q in range(3):
                ball("Bush", -44 + k * 12.5 + q * 3 - 3, fy + 3, z0 + 130, 3, (80, 150, 80) if q % 2 else (190, 90, 150), "Grass", collide=False)
    elif j == 2:
        for zz in range(int(z0) + 14, int(z0) + ZONE_D, 28):
            for side in (-1, 1):
                vcyl("Pillar", side * 48, fy, topy + 6, zz, 5, SILVER, "Metal")
                box("Vent", (0.4, 2.2, 3.2), (side * 45.4, fy + 12, zz), DARK, "Metal", collide=False)
        # revolving door set piece
        disc("DoorRing", 0, fy + 8, z0 + 4, 14, 0.8, DARK, "Metal", collide=False)
        for q in range(4):
            a = q * math.pi / 2 + 0.5
            box("DoorGlass", (6, 14, 0.2), (3 * math.cos(a), fy + 7, z0 + 4 + 3 * math.sin(a)), GLASSG, "Glass",
                transp=0.5, collide=False, rot=(0, math.degrees(-a), 0))
        # escalator
        part("Escalator", (6, 14, 34), (-46, fy + 7, z0 + 100), (70, 74, 80), "Metal", cls="WedgePart", collide=False)
    elif j == 3:
        for r in range(8):   # tiered seating backdrop on both sides
            for side in (-1, 1):
                box("Tier", (3, 3 + r * 1.2, ZONE_D - 8), (side * (49 - r * 0.0), fy + (3 + r * 1.2) / 2, z0 + ZONE_D / 2),
                    (110, 112, 118), "Slate", collide=False) if r == 0 else None
        for q in range(26):
            for side in (-1, 1):
                box("Seat", (2.4, 2, 2.4), (side * 49, fy + 5, z0 + 6 + q * 5), RED, "Fabric", collide=False)
        for q in range(7):
            box("RingLight", (110, 0.5, 1.5), (0, topy + q * 0.6, z0 + 10 + q * 20), (255, 236, 190), "Neon", collide=False)
    elif j == 4:
        for q in range(14):
            for side in (-1, 1):
                box("Shelf", (3, 24, 8), (side * 51, fy + 12, z0 + 8 + q * 10), (130, 90, 55), "Wood")
                for b in range(10):
                    box("Books", (0.3, 2.2, 6), (side * 49.3, fy + 3 + b * 2.2, z0 + 8 + q * 10),
                        [RED, BLUE, GREEN, YELLOW, PURPLE][(b + q) % 5], "SmoothPlastic", collide=False)
        for q in range(6):
            vcyl("Lamp", -30 + q * 12, topy - 6, topy + 6, z0 + 70, 0.3, DARK, "Metal", collide=False)
            ball("Glow", -30 + q * 12, topy - 6, z0 + 70, 4, (255, 220, 150), "Neon", collide=False)
    elif j == 5:
        sign("EM", "المجهر الإلكتروني\nElectron Microscopy", (55.2 - 2, fy + 8, z0 + 80), (0.8, 6, 28), "Left",
             color=(30, 120, 60), bg=(240, 244, 244))
        part("GiantScope", (14, 22, 10), (50, fy + 11, z0 + 110), (205, 210, 215), "Metal", collide=False)
        vcyl("GiantLens", 50, fy + 22, fy + 34, z0 + 110, 5, DARK, "Metal", collide=False)
        for q in range(10):
            c = [CYAN, PINK, (120, 255, 160)][q % 3]
            vcyl("Flask", -50 + q * 3, fy, fy + 5, z0 + 120, 2.2, c, "Glass", transp=0.35, collide=False)
            ball("FlaskTop", -50 + q * 3, fy + 5.5, z0 + 120, 2.6, c, "Neon", collide=False)
    elif j == 6:
        names = [("Salad Creations\nسالاد كريشنز", GREEN), ("Larich", (30, 60, 140)),
                 ("Old Friends\nأولد فريندز", (40, 40, 44)), ("العلوم", PURPLE)]
        for q, (t, c) in enumerate(names):
            sign("Vendor", t, (-54.0, fy + 8, z0 + 18 + q * 30), (0.8, 7, 22), "Right", color=WHITE, bg=c)
        for q in range(8):
            ball("Drop", 50, fy + 6 + (q % 2) * 4, z0 + 12 + q * 16, 5, PURPLE, "SmoothPlastic", collide=False)
    elif j == 7:
        for q in range(9):
            for side in (-1, 1):
                tree(side * 49, fy, z0 + 10 + q * 15, 1.3)
                rock(side * 44, fy, z0 + 16 + q * 15, 1.5)
        for q in range(5):
            bench(-38 + q * 20, fy, z0 + ZONE_D - 6, "x")
        part("Sail", (1, 34, 60), (0, fy + 36, z0 + 100), (245, 245, 242), "Fabric", cls="WedgePart", collide=False, transp=0.15)
        part("Sail", (1, 28, 50), (-30, fy + 40, z0 + 40), (240, 240, 238), "Fabric", cls="WedgePart", collide=False, transp=0.15)
    elif j == 8:
        for zz in range(int(z0) + 14, int(z0) + ZONE_D, 24):
            for side in (-1, 1):
                vcyl("Column", side * 46, fy, topy + 10, zz, 5.5, (96, 100, 108), "Metal")
                box("Slit", (0.3, 1, 3.6), (side * 43.2, fy + 14, zz), DARK, "Metal", collide=False)
        for q in range(5):
            box("Skylight", (60, 0.4, 5), (0, topy + 14, z0 + 15 + q * 28), (255, 255, 250), "Neon", collide=False)
        for q in range(6):
            box("Sofa", (7, 2, 3), (-20 + (q % 3) * 20, fy + 1, z0 + 30 + (q // 3) * 70), YELLOW if q % 2 else BLUE, "Fabric", collide=False)
    elif j == 9:
        for q in range(10):
            for side in (-1, 1):
                box("Desk", (6, 2.6, 3), (side * 48, fy + 1.3, z0 + 8 + q * 13), (230, 230, 226), "SmoothPlastic", collide=False)
                box("Screen", (0.3, 2.6, 4), (side * 46.5, fy + 4.6, z0 + 8 + q * 13), BLACK, "SmoothPlastic", collide=False,
                    text=dict(face="Left" if side > 0 else "Right", text="</>", color=CYAN, bg=(10, 20, 40), bg_t=0.0))
        for q in range(22):   # skyline beyond the glass
            h = rng.uniform(20, 90)
            for side in (-1, 1):
                box("Tower", (rng.uniform(10, 24), h, rng.uniform(10, 24)), (side * rng.uniform(66, 120), fy + h / 2,
                    z0 + rng.uniform(0, ZONE_D)), (150, 175, 190), "Glass", transp=0.2, collide=False)
    else:
        # giant DNA helix on both sides + cells
        for side in (-1, 1):
            for q in range(60):
                a = q * 0.35
                zz = z0 + 8 + q * 2.1
                ball("StrandA", side * 49 + math.cos(a) * 3, fy + 6 + q * 0.7, zz + math.sin(a) * 3, 1.8, PINK, "Neon", collide=False)
                ball("StrandB", side * 49 - math.cos(a) * 3, fy + 6 + q * 0.7, zz - math.sin(a) * 3, 1.8, CYAN, "Neon", collide=False)
                if q % 3 == 0:
                    box("Rung", (6, 0.4, 0.4), (side * 49, fy + 6 + q * 0.7, zz), (255, 255, 255), "Neon", collide=False,
                        rot=(0, 0, 0))
        ball("Cell", 0, fy + 30, z0 + 118, 30, (120, 255, 160), "Glass", transp=0.7, collide=False)
        ball("Nucleus", 0, fy + 30, z0 + 118, 11, (255, 120, 190), "Neon", collide=False)
        sign("Biotech", "BIOTECHNOLOGY\nالبايوتكنولوجي", (0, fy + 54, z0 + 138), (46, 12, 1), "Front",
             color=WHITE, bg=(20, 20, 40))


# ------------------------------------------------------------------ hub (club HQ)
def hub():
    y_floor = 0
    with Group("Hub"):
        box("Deck", (98, 1, 64), (0, -0.5, -40), (205, 198, 186), "Concrete")
        box("HubBody", (100, 33, 66), (0, -17.5, -40), (190, 180, 160), "Concrete")
        for q in range(8):   # striped paving
            box("Stripe", (98, 0.1, 2), (0, 0.05, -12 - q * 4), (180, 165, 140) if q % 2 else (150, 150, 150),
                "Concrete", collide=False)
        # room 088
        box("RoomFloor", (40, 1, 42), (-26, -0.45, -51), (110, 100, 96), "Fabric")
        wall = (150, 140, 135)
        box("WallL", (1, 12, 42), (-46, 6, -51), wall, "Fabric")
        box("WallR", (1, 12, 42), (-6, 6, -51), wall, "Fabric")
        box("WallFrontA", (16, 12, 1), (-38, 6, -30), wall, "Fabric")
        box("WallFrontB", (16, 12, 1), (-14, 6, -30), wall, "Fabric")
        box("Lintel", (8, 2, 1), (-26, 11, -30), wall, "Fabric")
        box("WallBackLow", (40, 3, 1), (-26, 1.5, -72), wall, "Fabric")
        box("Window", (40, 7, 0.5), (-26, 6.5, -72), (120, 170, 190), "Glass", transp=0.55, collide=False)
        box("WindowBeam", (40, 2, 1), (-26, 11, -72), wall, "Fabric")
        box("DoorFrameL", (1.2, 10, 1.4), (-30.6, 5, -30), (205, 140, 55), "Wood")
        box("DoorFrameR", (1.2, 10, 1.4), (-21.4, 5, -30), (205, 140, 55), "Wood")
        box("DoorLeaf", (0.4, 10, 5.4), (-21.2, 5, -33), (205, 140, 55), "Wood", collide=False)
        sign("RoomPlate", "088\nنادي العلوم البيولوجية", (-26, 9.2, -29.3), (7, 1.8, 0.3), "Back",
             color=WHITE, bg=(60, 60, 64))
        # desk + chair + shelves
        box("Desk", (14, 1, 6), (-26, 3.5, -64), (160, 112, 70), "Wood")
        box("DeskSideL", (1, 3, 6), (-32.5, 1.5, -64), (130, 90, 55), "Wood", collide=False)
        box("DeskSideR", (1, 3, 6), (-19.5, 1.5, -64), (130, 90, 55), "Wood", collide=False)
        box("Chair", (3, 1, 3), (-26, 2, -67.5), (60, 62, 66), "Fabric", collide=False)
        box("ChairBack", (3, 4, 0.5), (-26, 4.4, -69), (60, 62, 66), "Fabric", collide=False)
        box("Shelf", (3, 10, 20), (-44, 5, -58), (150, 100, 62), "Wood")
        box("ShelfInset", (0.2, 9, 18.5), (-42.4, 5, -58), (30, 30, 34), "SmoothPlastic", collide=False)
        disc("Plaque", -42.2, 7.5, -62, 3, 0.4, GOLD, "Metal", collide=False)
        for q in range(6):
            box("File", (1.2, 2, 0.5), (-42.2, 3.2, -52 + q * 0.7), [RED, BLUE, GREEN][q % 3], "SmoothPlastic", collide=False)
        # achievements case (trophies)
        box("Case", (2, 8, 12), (-8, 4, -46), (200, 225, 235), "Glass", transp=0.55)
        for q in range(4):
            vcyl("Trophy", -8, 1 + (q // 2) * 4, 3.6 + (q // 2) * 4, -49 + (q % 2) * 6, 1.6, GOLD, "Metal", collide=False)
            ball("TrophyTop", -8, 4.2 + (q // 2) * 4, -49 + (q % 2) * 6, 2.2, GOLD, "Metal", collide=False)
        sign("CaseLabel", "الإنجازات | Achievements", (-6.8, 9.5, -46), (0.3, 1.6, 12), "Left", color=GOLD, bg=(30, 30, 34))
        # DNA board
        box("DNABoard", (0.4, 9, 12), (-6.8, 6, -62), (245, 245, 245), "SmoothPlastic")
        for q in range(24):
            a = q * 0.5
            yy = 2.2 + q * 0.3
            ball("StrandA", -6.4 - math.cos(a) * 0.5, yy, -62 + math.sin(a) * 3.5, 0.7, PINK, "Neon", collide=False)
            ball("StrandB", -6.4 + math.cos(a) * 0.5, yy, -62 - math.sin(a) * 3.5, 0.7, CYAN, "Neon", collide=False)
        # poster, mirror, display, cart
        sign("Poster", "The Birth of\nChemical Medicine", (-33, 5.5, -70.8), (9, 6, 0.3), "Front",
             color=(40, 40, 44), bg=(250, 250, 248))
        box("Mirror", (3, 9, 0.3), (-41, 5, -70.8), (170, 195, 215), "Glass", transp=0.25, collide=False)
        box("DisplayA", (6, 2, 5), (-12, 1, -68), ORANGE, "SmoothPlastic", collide=False)
        box("DisplayB", (6, 4, 3), (-12, 2, -69.4), (235, 100, 40), "SmoothPlastic", collide=False)
        box("Cart", (3, 4, 2), (-11, 2, -56), WHITE, "SmoothPlastic", collide=False)
        # spawn
        part("Checkpoint_0", (10, 1, 10), (-26, 0.5, -48), GREEN, "SmoothPlastic",
             text=dict(face="Top", text="BSC", color=WHITE, bg=GREEN, bg_t=0.0))
        checkpoints[0] = (-26, 0.5, -48)
        # mascot + discord board outside the door
        mascot(-14, 0, -23)
        sign("DiscordBoard", "انضموا لمجتمعنا على Discord\ndiscord.gg/8hw9hBn27", (-14, 6.5, -29.0), (9.5, 5, 0.4), "Back",
             color=WHITE, bg=(88, 101, 242))
        sign("Welcome", "نادي العلوم البيولوجية\nBiological Sciences Club\n100 Level Parkour", (22, 9, -26),
             (24, 12, 0.6), "Back", color=WHITE, bg=(24, 70, 48))


def mascot(cx, cy, cz):
    s = 1.45
    with Group("ProfessorBioSciClub", "Model"):
        def b(n, sx, sy, sz, ox, oy, oz, c, mat="SmoothPlastic", rot=(0, 0, 0)):
            part(n, (sx * s, sy * s, sz * s), (cx + ox * s, cy + oy * s, cz + oz * s), c, mat, rot=rot, collide=False)
        skin = (255, 214, 170)
        b("LegL", 1.7, 3.2, 1.8, -1.0, 1.6, 0, (30, 30, 34))
        b("LegR", 1.7, 3.2, 1.8, 1.0, 1.6, 0, (30, 30, 34))
        b("Coat", 4.6, 5.4, 2.6, 0, 5.9, 0, (248, 248, 246))
        b("CoatSkirt", 4.8, 1.6, 2.7, 0, 3.5, 0, (248, 248, 246))
        b("Tie", 0.8, 3.4, 0.2, 0, 6.6, 1.35, (20, 20, 22))
        b("Collar", 2.0, 0.8, 2.7, 0, 8.4, 0, (255, 255, 255))
        b("ArmL", 1.4, 4.2, 1.5, 3.2, 6.0, 0, (248, 248, 246), rot=(0, 0, 8))
        b("HandL", 1.3, 1.2, 1.3, 3.5, 3.5, 0, skin)
        b("ArmR", 4.2, 1.5, 1.5, -4.3, 7.2, 0, (248, 248, 246), rot=(0, 0, -12))
        b("HandR", 1.5, 1.2, 1.4, -6.8, 6.6, 0, skin)
        b("Head", 3.4, 3.6, 3.0, 0, 10.6, 0, skin)
        b("Hair", 3.8, 1.6, 3.4, 0, 12.6, -0.1, (18, 18, 20))
        b("Fringe", 3.4, 0.9, 0.6, 0, 11.8, 1.5, (18, 18, 20))
        b("EyeL", 0.9, 0.18, 0.1, -0.8, 10.9, 1.52, (20, 20, 22))
        b("EyeR", 0.9, 0.18, 0.1, 0.8, 10.9, 1.52, (20, 20, 22))
        b("Smile", 1.2, 0.18, 0.1, 0, 9.8, 1.52, (120, 50, 50))
        b("Badge", 1.1, 1.1, 0.15, -1.3, 7.2, 1.35, GREEN, "Neon")
        b("QR", 1.0, 1.0, 0.1, 1.3, 7.4, 1.35, (255, 255, 255))
        b("QRDots", 0.5, 0.5, 0.12, 1.3, 7.4, 1.4, (10, 10, 10))
        part("NameTag", (9 * s, 1.6 * s, 0.3), (cx, cy + 14.2 * s, cz), (24, 70, 48), "SmoothPlastic", collide=False,
             text=dict(face="Back", text="Professor BioSci Club", color=WHITE, bg=(24, 70, 48), bg_t=0.0))
        part("NameTagFront", (9 * s, 1.6 * s, 0.3), (cx, cy + 14.2 * s, cz - 0.2), (24, 70, 48), "SmoothPlastic",
             collide=False, text=dict(face="Front", text="Professor BioSci Club", color=WHITE, bg=(24, 70, 48), bg_t=0.0))


# ------------------------------------------------------------------ build everything
def build():
    pad_prev = ("deck", 0.0, -40.0, 0.0, 96.0)       # kind, cx, cz, top_y, w (walkable end of hub)
    check.append(("hub", -26.0, -8.0, 0.0, 12.0))
    with Group("Zones"):
        for j in range(1, 11):
            with Group("Zone%02d_%s" % (j, ZONES[j - 1]["en"].replace(" ", "").replace("&", "and"))):
                zone_frame(j)
                with Group("Decor"):
                    zone_decor(j)
    with Group("Course"):
        for k in range(1, 101):
            j = zone_of(k)
            t, n, step, w, dirn = lane_params(k)
            pat = [0, 1, 2, 3, 4][(k * 3 + k // 7) % 5] if k > 1 else 0
            A = max(0.0, min(3.0, 6.5 - w / 2.0))
            if j in (1, 8, 10):
                A = min(A, 1.2)   # round platforms: keep diagonal gaps short
            x0 = -40.0 * dirn
            zk = LANE_DZ * (k - 1)
            yk = RISE * k
            with Group("Level%03d" % k):
                for i in range(n):
                    x = x0 + dirn * step * i
                    last = (i == n - 1)
                    z = zk + pattern_dz(pat, i, n, A)
                    y = yk + pattern_dy(pat, i, n)
                    if last:
                        final = (k == 100)
                        size = 20 if final else 12
                        part("Checkpoint_%d" % k, (size, 1, size), (x, y, z), GOLD if final else GREEN,
                             "Neon" if final else "SmoothPlastic",
                             text=dict(face="Top", text=("FINISH\n100" if final else "%d" % k), color=WHITE,
                                       bg=GOLD if final else GREEN, bg_t=0.0))
                        checkpoints[k] = (x, y, z)
                        check.append(("pad", x, z, y + 0.5, float(size)))
                        if final:
                            vcyl("TrophyStem", x, y + 0.5, y + 7, z, 1.6, GOLD, "Metal", collide=False)
                            ball("TrophyCup", x, y + 9, z, 6, GOLD, "Metal", collide=False)
                            sign("FinishSign", "مبروك! أكملت المراحل المئة\nYou finished all 100 levels!",
                                 (x, y + 16, z + 9), (26, 6, 0.6), "Front", color=GOLD, bg=(20, 30, 28))
                    else:
                        style_platform(j, k, i, x, y, z, w, False)
                        circ = j in (1, 10) or (j == 8 and i % 2 == 0)
                        check.append(("circ" if circ else "plat", x, z, y + 0.5, w))
    hub()


def shape_gap(a, b):
    ca, cb = a[0] == "circ", b[0] == "circ"
    ra, rb = a[4] / 2, b[4] / 2
    dxc, dzc = abs(a[1] - b[1]), abs(a[2] - b[2])
    if ca and cb:
        return max(0.0, math.hypot(dxc, dzc) - ra - rb)
    if ca or cb:   # circle centre to rectangle
        rad, rr = (ra, rb) if ca else (rb, ra)
        dx = max(0.0, dxc - rr)
        dz = max(0.0, dzc - rr)
        return max(0.0, math.hypot(dx, dz) - rad)
    return math.hypot(max(0.0, dxc - ra - rb), max(0.0, dzc - ra - rb))


def validate():
    worst_gap = worst_rise = 0.0
    bad = []
    for a, b in zip(check, check[1:]):
        gap = shape_gap(a, b)
        rise = b[3] - a[3]
        worst_gap, worst_rise = max(worst_gap, gap), max(worst_rise, rise)
        if gap > 7.0 or rise > 2.8:
            bad.append((a, b, round(gap, 2), round(rise, 2)))
    return worst_gap, worst_rise, bad, len(check)


if __name__ == "__main__":
    build()
    gap, rise, bad, n = validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (rid(), "".join(buf))
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(xml)
    print("parts:", nparts[0], "| walkable steps:", n, "| worst gap: %.2f" % gap, "| worst rise: %.2f" % rise,
          "| violations:", len(bad))
    for v in bad[:5]:
        print("  BAD", v)
    print("checkpoints:", len(checkpoints), "| size KB:", len(xml) // 1024)
