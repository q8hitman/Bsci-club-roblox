"""Shared art: the BSC logo built from parts (always upright on walls/arches, never on the floor),
campus cats and small props."""
import math
import random

import genmap as G

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rng = random.Random(4242)

# the five logo hexagons (pastel fill, icon) in the logo's own 2D layout (u right, v up, in units of R)
HEXES = [
    ((-0.866, 1.5), (250, 222, 170), "🧬"),   # DNA, beige
    ((0.866, 1.5), (205, 232, 60), "🍃"),     # leaf, lime
    ((-1.732, 0.0), (220, 165, 238), "⚗️"),   # molecule, lilac
    ((-0.866, -1.5), (160, 218, 236), "🐢"),  # turtle, light blue
    ((0.866, -1.5), (232, 150, 166), "🦠"),   # bacteria, pink
]


def _frame(nx, nz):
    """plate yaw so its +X (the 'Right' face) points along (nx, nz); returns yaw and the viewer's right vector"""
    yaw = math.degrees(math.atan2(-nz, nx))
    r = math.radians(yaw)
    zdir = (math.sin(r), math.cos(r))
    return yaw, (-zdir[0], -zdir[1])


def hexagon(name, cx, cy, cz, R, col, nx, nz, thick=0.8, mat="SmoothPlastic", pointy=True):
    yaw, _ = _frame(nx, nz)
    for q in range(3):
        spin = q * 60 + (30 if pointy else 0)
        G.part(name, (thick, R * math.sqrt(3), R), (cx, cy, cz), col, mat, rot=(spin, yaw, 0), collide=False)


def logo(cx, cy, cz, R=4.0, nx=0.0, nz=1.0, words=True, frame=True, name=True):
    """BSC logo upright, facing direction (nx, nz)"""
    yaw, (ux, uz) = _frame(nx, nz)
    with G.Group("BSCLogo", "Model"):
        for (u, v), col, icon in HEXES:
            x, y, z = cx + ux * u * R, cy + v * R, cz + uz * u * R
            if frame:
                hexagon("LogoHexRim", x - nx * 0.2, y, z - nz * 0.2, R * 0.98, (255, 255, 255), nx, nz, thick=0.6)
            hexagon("LogoHex", x, y, z, R * 0.9, col, nx, nz)
            s = R * 1.05
            G.part("LogoIcon", (0.2, s, s), (x + nx * 0.55, y, z + nz * 0.55), (0, 0, 0), "SmoothPlastic", transp=1,
                   rot=(0, yaw, 0), collide=False, shadow=False,
                   text=dict(face="Right", text=icon, color=(30, 30, 30), bg=None, bg_t=1.0))
        if words:
            tx, tz = cx + ux * 2.6 * R, cz + uz * 2.6 * R
            G.part("LogoBSC", (0.3, 2.2 * R, 4.2 * R), (tx + nx * 0.3, cy + 0.15 * R, tz + nz * 0.3), (255, 255, 255),
                   "SmoothPlastic", transp=1, rot=(0, yaw, 0), collide=False, shadow=False,
                   text=dict(face="Right", text="BSC", color=(20, 20, 24), bg=None, bg_t=1.0))
            kx, kz = cx + ux * 3.3 * R, cz + uz * 3.3 * R
            G.part("LogoKU", (0.3, 0.9 * R, 1.8 * R), (kx + nx * 0.3, cy - 1.2 * R, kz + nz * 0.3), (255, 255, 255),
                   "SmoothPlastic", transp=1, rot=(0, yaw, 0), collide=False, shadow=False,
                   text=dict(face="Right", text="KU", color=(20, 20, 24), bg=None, bg_t=1.0))
            if not name:
                return
            mx, mz = cx + ux * 0.9 * R, cz + uz * 0.9 * R
            G.part("LogoName", (0.3, 1.9 * R, 8.6 * R), (mx + nx * 0.3, cy - 3.6 * R, mz + nz * 0.3), (255, 255, 255),
                   "SmoothPlastic", transp=1, rot=(0, yaw, 0), collide=False, shadow=False,
                   text=dict(face="Right", text="Biological Sciences Club\nKuwait University", color=(20, 20, 24), bg=None,
                             bg_t=1.0))


def logo_board(cx, cy, cz, R=3.0, nx=0.0, nz=1.0, bg=(250, 250, 248)):
    """logo on a white backing board (for billboards/arches)"""
    yaw, (ux, uz) = _frame(nx, nz)
    G.part("LogoBoard", (0.6, 11.5 * R, 11.5 * R), (cx + ux * 0.9 * R - nx * 0.6, cy - 0.9 * R, cz + uz * 0.9 * R - nz * 0.6), bg,
           "SmoothPlastic", rot=(0, yaw, 0), collide=False)
    logo(cx - ux * 0.4 * R, cy + 0.6 * R, cz - uz * 0.4 * R, R, nx, nz, words=True, frame=False)


# ---------------------------------------------------------------- cats (the College of Science has many)
CAT_COATS = [((236, 150, 60), (250, 220, 180)), ((240, 240, 236), (250, 200, 200)), ((40, 40, 44), (230, 230, 230)),
             ((150, 150, 156), (240, 240, 240)), ((120, 84, 52), (220, 190, 150))]


def cat(x, y, z, yaw=0.0, pose="sit", coat=None, s=1.0):
    col, light = coat or rng.choice(CAT_COATS)
    r = math.radians(yaw)
    fx, fz = math.sin(r), math.cos(r)       # facing

    def at(f, up, side=0.0):
        rx, rz = math.cos(r), -math.sin(r)
        return (x + fx * f * s + rx * side * s, y + up * s, z + fz * f * s + rz * side * s)
    with G.Group("Cat", "Model"):
        if pose == "loaf":
            G.part("CatBody", (2.0 * s, 1.6 * s, 1.6 * s), at(0, 0.8), col, "Fabric", shape="Cylinder", rot=(0, yaw + 90, 0),
                   collide=False)
            ball("CatHead", *at(1.2, 1.4), 1.4 * s, col, "Fabric", collide=False)
            head_f, head_up = 1.2, 1.4
        elif pose == "walk":
            G.part("CatBody", (2.4 * s, 1.3 * s, 1.3 * s), at(0, 1.5), col, "Fabric", shape="Cylinder", rot=(0, yaw + 90, 0),
                   collide=False)
            for f in (-0.8, 0.8):
                for sd in (-0.35, 0.35):
                    box("CatLeg", (0.35 * s, 1.0 * s, 0.35 * s), at(f, 0.5, sd), col, "Fabric", collide=False)
            ball("CatHead", *at(1.5, 2.1), 1.3 * s, col, "Fabric", collide=False)
            head_f, head_up = 1.5, 2.1
        else:  # sitting upright
            ball("CatBody", *at(0, 0.9), 1.8 * s, col, "Fabric", collide=False)
            ball("CatChest", *at(0.4, 1.4), 1.2 * s, light, "Fabric", collide=False)
            ball("CatHead", *at(0.25, 2.3), 1.35 * s, col, "Fabric", collide=False)
            head_f, head_up = 0.25, 2.3
        for sd in (-0.35, 0.35):
            G.part("CatEar", (0.15 * s, 0.5 * s, 0.5 * s), at(head_f, head_up + 0.6, sd), col, "Fabric",
                   rot=(45, yaw, 0), collide=False)
            ball("CatEye", *at(head_f + 0.6, head_up + 0.15, sd * 0.8), 0.22 * s, (120, 200, 90), "Neon", collide=False,
                 shadow=False)
        ball("CatNose", *at(head_f + 0.68, head_up - 0.15), 0.18 * s, (240, 140, 150), "SmoothPlastic", collide=False)
        # tail curling up
        G.part("CatTail", (0.3 * s, 1.6 * s, 0.3 * s), at(-1.1, 1.2), col, "Fabric", rot=(-35, yaw, 0), collide=False)


def cat_bowl(x, y, z):
    disc("Bowl", x, y + 0.2, z, 1.4, 0.4, (70, 140, 210), "SmoothPlastic", collide=False)
    disc("Food", x, y + 0.42, z, 1.0, 0.1, (150, 100, 60), "SmoothPlastic", collide=False)


def umbrella_table(x, y, z, col=(46, 160, 90)):
    disc("Table", x, y + 3.2, z, 5, 0.4, (240, 238, 232), "SmoothPlastic", collide=False)
    vcyl("Pole", x, y, y + 9, z, 0.4, (90, 90, 96), "Metal", collide=False)
    disc("Canopy", x, y + 9, z, 10, 0.5, col, "Fabric", collide=False)
    disc("CanopyTop", x, y + 9.4, z, 6, 0.4, (250, 250, 245), "Fabric", collide=False)
    for q in range(3):
        a = q * 2.1
        box("Chair", (1.8, 0.4, 1.8), (x + math.cos(a) * 3.6, y + 2.0, z + math.sin(a) * 3.6), (230, 230, 226), "SmoothPlastic",
            collide=False)


def car(x, y, z, yaw=0.0, col=None):
    col = col or rng.choice([(230, 230, 232), (40, 42, 48), (170, 30, 36), (60, 90, 150), (200, 200, 205), (230, 210, 170)])
    r = math.radians(yaw)
    fx, fz = math.sin(r), math.cos(r)
    G.part("CarBody", (6, 2.4, 13), (x, y + 1.9, z), col, "SmoothPlastic", rot=(0, yaw, 0), collide=False)
    G.part("CarCabin", (5.4, 2.0, 7), (x - fx * 0.6, y + 4.0, z - fz * 0.6), (150, 190, 210), "Glass", transp=0.2,
           rot=(0, yaw, 0), collide=False)
    for f in (-4.2, 4.2):
        for sd in (-3.0, 3.0):
            rx, rz = math.cos(r), -math.sin(r)
            G.part("Tyre", (1.0, 2.4, 2.4), (x + fx * f + rx * sd, y + 1.2, z + fz * f + rz * sd), (30, 30, 32), "SmoothPlastic",
                   shape="Cylinder", rot=(0, yaw, 0), collide=False)


def flag_pole(x, y, z, h=26):
    vcyl("FlagPole", x, y, y + h, z, 0.6, (220, 220, 225), "Metal", collide=False)
    cols = [(0, 122, 61), (255, 255, 255), (206, 17, 38)]
    for i, c in enumerate(cols):
        box("Flag", (0.2, 1.4, 6), (x, y + h - 1.0 - i * 1.4, z + 3.4), c, "Fabric", collide=False)
    G.part("FlagTri", (0.25, 4.2, 2.6), (x, y + h - 2.4, z + 0.9), (20, 20, 20), "Fabric", rot=(0, 0, 0), collide=False)


def floor_hex(x, y, z, R, col, name="FloorHex"):
    """flat hexagon tile (floor pattern only)"""
    for q in range(3):
        G.part(name, (R, 0.08, R * math.sqrt(3)), (x, y, z), col, "SmoothPlastic", rot=(0, q * 60, 0), collide=False,
               shadow=False)
