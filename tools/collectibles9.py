"""Collectibles + shop kiosk (absolute coordinates; call with every offset at 0).
  Collect|cat|cN   invisible touch box around a campus cat (+ Sparkle|cN marker the client hides once found)
  Collect|spec|sN  specimen card on a short optional side route next to each parkour zone
  ShopKiosk        HQ counter; Profile.client puts a ProximityPrompt on it
"""
import math
import re

import genmap as G
import genmap5 as C5
import bsc_art as A
import hq

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect

HX, HY, HZ = hq.HQ_OFFSET
# (id, x, y, z, yaw, pose) — y is the floor height under the cat
CATS = [
    ("c1", -24, 0.2, 96, 200, "sit"),                # garden, by the planted mound (v36: old spot is inside the gym)
    ("c2", 98, 0.2, 96, 160, "loaf"),                # under the sail plaza
    ("c3", -84, 40.0, -120, 90, "loaf"),             # library floor (L2)
    ("c4", 60, 72.0, -126, 0, "sit"),                # 4th floor, by the labs
    ("c5", 78.2, 15.4, -148.4, 270, "loaf"),         # club office 088, on the desk (v35 desk: top y 15.4)
    ("c6", -20, 24.0, 180, 180, "walk"),             # north building, games hall (L1)
    ("c7", 140, 3.0, 256, 180, "sit"),               # events plaza stage
    ("c8", -140, 0.2, 226, 0, "loaf"),               # desert garden shade
    ("c9", 130, 3.9, -47.6, 0, "sit"),               # cell train station bench
    ("c10", 205, 0.2, -214, 90, "loaf"),             # parking lot
    ("c11", HX - 72, HY + 4.4, HZ - 22, 90, "loaf"),  # HQ café counter
    ("c12", HX + 52, HY + 32.6, HZ + 14, 180, "sit"),  # top of the HQ mini-obby
]


def sparkle(id_, x, y, z):
    ball("Sparkle|" + id_, x, y, z, 1.0, (255, 240, 150), "Neon", collide=False, shadow=False, light=(0.8, 10, (255, 240, 150)))
    for q in range(3):
        a = q * 2.1
        ball("Sparkle|" + id_, x + math.cos(a) * 1.4, y - 0.5 + q * 0.4, z + math.sin(a) * 1.4, 0.4, (255, 255, 255), "Neon",
             collide=False, shadow=False)


def cats():
    with G.Group("CampusCats"):
        for id_, x, y, z, yaw, pose in CATS:
            A.cat(x, y, z, yaw, pose)
            G.part("Collect|cat|" + id_, (5, 5, 5), (x, y + 2, z), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
            sparkle(id_, x, y + 4.2, z)


CP_RE = re.compile(r'<string name="Name">Checkpoint_(\d+)</string><CoordinateFrame name="CFrame"><X>([-\d.]+)</X>'
                   r'<Y>([-\d.]+)</Y><Z>([-\d.]+)</Z>')


def checkpoint_positions():
    pos = {}
    for chunk in G.buf:
        if "Checkpoint_" in chunk:
            for m in CP_RE.finditer(chunk):
                pos[int(m.group(1))] = (float(m.group(2)), float(m.group(3)) + 0.5, float(m.group(4)))
    return pos


def specimens(zone_starts):
    """beside the 6th checkpoint of each zone: three hops sideways (and up) to a glowing specimen jar"""
    cps = checkpoint_positions()
    with G.Group("Specimens"):
        for i in range(len(zone_starts) - 1):
            level = zone_starts[i] + 6
            if level not in cps:
                continue
            x, y, z = cps[level]
            side = 1 if i % 2 == 0 else -1
            col = A.HEXES[i % 5][1]
            for k, (dx, dy) in enumerate(((13.5, 1.0), (21.0, 2.6), (28.5, 4.2))):
                px = x + side * dx
                G.part("SidePad", (1, 4.2, 4.2), (px, y + dy - 0.5, z + (k % 2) * 2.5 - 1.2), col, "SmoothPlastic", shape="Cylinder",
                       rot=(0, 0, 90))
            jx, jy, jz = x + side * 28.5, y + 4.2, z + 1.3
            vcyl("SpecJar", jx, jy, jy + 3.2, jz, 2.2, (210, 240, 230), "Glass", transp=0.35, collide=False)
            vcyl("SpecLiquid", jx, jy + 0.2, jy + 2.4, jz, 1.9, col, "Neon", transp=0.3, collide=False, shadow=False)
            disc("SpecLid", jx, jy + 3.3, jz, 2.4, 0.3, (60, 60, 66), "Metal", collide=False)
            G.part("Collect|spec|s%d" % (i + 1), (4, 6, 4), (jx, jy + 2, jz), (0, 0, 0), "SmoothPlastic", transp=1, collide=False,
                   shadow=False)
            sparkle("s%d" % (i + 1), jx, jy + 5, jz)


def shop_kiosk():
    x, z = HX + 20.0, HZ - 44.0     # between the mascot and the specimen cases, beside the aisle
    y = HY
    rect("KioskBase", x - 5, x + 5, y, y + 4, z - 2.5, z + 2.5, (200, 170, 232), "SmoothPlastic")
    rect("KioskTop", x - 5.4, x + 5.4, y + 4, y + 4.4, z - 2.9, z + 2.9, (250, 250, 248), "Marble")
    G.part("ShopKiosk", (10, 1, 5), (x, y + 4.9, z), (255, 255, 255), "SmoothPlastic", transp=1, collide=False)
    for s_ in (-1, 1):
        vcyl("KioskPole", x + s_ * 4.6, y + 4.4, y + 11, z + 2.2, 0.4, (90, 90, 96), "Metal", collide=False)
    sign("KioskSign", "✨ متجر الأثر والألقاب\nTrails & Titles", (x, y + 11.5, z + 2.2), (11, 3.2, 0.4), "Back", bg=(110, 70, 150))
    for q in range(4):
        disc("KioskOrb", x - 3 + q * 2, y + 5.2, z, 1.2, 1.2, A.HEXES[q][1], "Neon", collide=False, shadow=False)


def build(zone_starts):
    cats()
    specimens(zone_starts)
    shop_kiosk()
