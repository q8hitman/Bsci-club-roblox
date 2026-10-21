"""Obby map generator v2: one long linear course, 100 stages, 10 themed zones.

Each stage is a short self-contained challenge (hops, beams, ferries, spinners, glass bridges...)
ending in a checkpoint pad. Behaviour of moving/killing parts is encoded in part names and
executed by src/server/Obstacles.server.luau:
    Move|dx,dy,dz|period|phase      KillMove|dx,dy,dz|period|phase
    Kill                            Bounce|vy
    Crumble|delay|respawn           Conv|vx,vy,vz
    Spin|speed                      Ghost|id      Button|id
Run: python tools/genmap2.py kuwait-parkour/src/map/Map.rbxmx [--preview out_prefix]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap as G  # noqa: E402  (reuses XML helpers and the club hub)

rng = random.Random(2026)
scene = []          # for the preview renderer
walk = []           # ordered walkable surfaces for the jump validator
_orig_part = G.part


def _logged(name, size, pos, color, mat="Plastic", shape="Block", rot=(0, 0, 0), transp=0.0,
            collide=True, cls="Part", text=None, extra="", shadow=True, light=None):
    sx, sy, sz = size
    if tuple(rot) == (0, 0, 90):
        sx, sy = sy, sx
    scene.append((pos[0], pos[1], pos[2], sx, sy, sz, color, transp, shape))
    _orig_part(name, size, pos, color, mat, shape, rot, transp, collide, cls, text, extra, shadow, light)


G.part = _logged
box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign

SEA = -92.0  # top of the cloud sea; towers rise from it

# ------------------------------------------------------------------ themes
def T(main, alt, edge, pillar):
    return dict(main=main, alt=alt, edge=edge, pillar=pillar)


THEMES = [
    T(((226, 214, 190), "Concrete"), ((196, 160, 112), "Concrete"), (255, 200, 60), ((236, 226, 204), "Concrete")),
    T(((62, 66, 74), "Granite"), ((170, 175, 182), "Metal"), (60, 220, 255), ((90, 96, 108), "Metal")),
    T(((176, 48, 44), "Fabric"), ((110, 112, 118), "Slate"), (255, 140, 40), ((130, 40, 38), "Fabric")),
    T(((238, 238, 232), "Marble"), ((150, 105, 65), "Wood"), (255, 190, 70), ((120, 82, 50), "Wood")),
    T(((236, 240, 242), "SmoothPlastic"), ((45, 95, 100), "Metal"), (80, 255, 150), ((60, 120, 125), "Metal")),
    T(((205, 160, 110), "WoodPlanks"), ((240, 238, 232), "Marble"), (170, 90, 255), ((110, 60, 160), "SmoothPlastic")),
    T(((150, 72, 55), "Brick"), ((210, 190, 160), "Concrete"), (255, 110, 60), ((92, 62, 44), "Wood")),
    T(((74, 78, 84), "Metal"), ((235, 190, 40), "Fabric"), (255, 255, 255), ((96, 100, 108), "Metal")),
    T(((232, 232, 228), "SmoothPlastic"), ((30, 34, 44), "SmoothPlastic"), (60, 220, 255), ((50, 56, 70), "Metal")),
    T(((200, 235, 240), "Glass"), ((30, 40, 70), "SmoothPlastic"), (255, 90, 170), ((120, 220, 235), "Glass")),
]
ZONE_NAMES = [("الساحة الأمامية", "The Courtyard"), ("بهو الجنوبي", "South Lobby"), ("المدرج الأحمر", "The Red Lecture Hall"),
              ("المكتبة", "The Library"), ("المختبرات", "Labs & Electron Microscopy"), ("الكافتيريا", "The Cafeteria"),
              ("الممر الأحمر والحديقة", "Red Corridor & Garden"), ("بهو الشمالي", "North Atrium"),
              ("صالات الحاسوب", "Computer Labs"), ("البايوتكنولوجي", "Biotechnology")]

SEQ = [
    ["hops", "zigzag", "pillars", "beam", "stairs", "crumble", "bounce", "pillars", "zigzag", ("hops", "beam", "pillars")],
    ["hops", "conveyor", "spinner", "ferry", "glass", "stairs", "sliders", "sweeper", "elevator", ("conveyor", "spinner", "ferry")],
    ["stairs", "crumble", "pillars", "spinner", "zigzag", "bounce", "sliders", "switch", "sweeper", ("stairs", "crumble", "spinner")],
    ["beam", "hops", "elevator", "switch", "zigzag", "sliders", "glass", "bounce", "crumble", ("beam", "elevator", "sliders")],
    ["sweeper", "conveyor", "glass", "spinner", "pillars", "switch", "ferry", "crumble", "zigzag", ("sweeper", "glass", "conveyor")],
    ["sliders", "ferry", "hops", "conveyor", "switch", "bounce", "spinner", "beam", "glass", ("sliders", "ferry", "spinner")],
    ["pillars", "beam", "zigzag", "stairs", "spinner", "bounce", "ferry", "crumble", "sweeper", ("beam", "spinner", "bounce")],
    ["elevator", "glass", "sliders", "switch", "conveyor", "pillars", "stairs", "sweeper", "ferry", ("elevator", "glass", "sweeper")],
    ["zigzag", "crumble", "switch", "spinner", "conveyor", "bounce", "glass", "sliders", "elevator", ("crumble", "switch", "spinner")],
    ["pillars", "bounce", "spinner", "glass", "sweeper", "ferry", "crumble", "elevator", "sliders", ("glass", "spinner", "bounce", "sweeper")],
]


# ------------------------------------------------------------------ primitives
def slab(th, x, top, z, sx, sz, alt=False, name="Plat", record=True):
    col, mat = th["alt"] if alt else th["main"]
    box(name, (sx, 1, sz), (x, top - 0.5, z), col, mat)
    box("Edge", (sx, 0.14, 0.35), (x, top + 0.02, z - sz / 2 + 0.2), th["edge"], "Neon", collide=False, shadow=False)
    box("Edge", (sx, 0.14, 0.35), (x, top + 0.02, z + sz / 2 - 0.2), th["edge"], "Neon", collide=False, shadow=False)
    if record:
        walk.append(("r", x, z, top, sx, sz))


def cursor_gap(c, nsz, gap):
    return c["z"] + c["sz"] / 2 + gap + nsz / 2


def set_c(c, x, y, z, sz):
    c["x"], c["y"], c["z"], c["sz"] = x, y, z, sz


def clampx(v, lim=9):
    return max(-lim, min(lim, v))


# ------------------------------------------------------------------ stage kinds
def k_hops(c, th, t, k):
    n, w, gap = 5 + int(t * 3), 8 - 3 * t, 3.0 + 3 * t
    for i in range(n):
        z = cursor_gap(c, w, gap)
        x = clampx(c["x"] * 0.4 + rng.uniform(-4, 4))
        top = c["y"] + rng.choice([0, 0, 1, 2, 0, -1])
        slab(th, x, top, z, w, w, alt=i % 2 == 1)
        set_c(c, x, top, z, w)


def k_zigzag(c, th, t, k):
    n, w, side = 6 + int(t * 2), 7 - 2 * t, rng.choice([-1, 1])
    for i in range(n):
        z = cursor_gap(c, w, 1.6)
        slab(th, side * 5.5, c["y"], z, w, w, alt=i % 2 == 1)
        set_c(c, side * 5.5, c["y"], z, w)
        side = -side


def k_stairs(c, th, t, k):
    for i in range(5):
        z = cursor_gap(c, 6, 1.6)
        top = c["y"] + 2.2
        slab(th, c["x"] * 0.5, top, z, 8, 6, alt=i % 2 == 1)
        set_c(c, c["x"] * 0.5, top, z, 6)
    # the first step must also be reachable from the pad: handled by 1.6 gap + 2.2 rise


def k_beam(c, th, t, k):
    L, bw = 22 + 10 * t, 3.4 - 1.7 * t
    z0 = c["z"] + c["sz"] / 2 + 2
    col, mat = th["alt"]
    walk.append(("brk",))
    box("Beam", (bw, 1, L), (c["x"], c["y"] - 0.5, z0 + L / 2), col, mat)
    for s in (-1, 1):
        box("BeamEdge", (0.2, 0.14, L), (c["x"] + s * (bw / 2 - 0.1), c["y"] + 0.02, z0 + L / 2), th["edge"], "Neon",
            collide=False, shadow=False)
    walk.append(("r", c["x"], z0 + L / 2, c["y"], bw, L))
    z = z0 + L + 1.5 + 4
    slab(th, c["x"], c["y"], z, 8, 8)
    set_c(c, c["x"], c["y"], z, 8)


def k_pillars(c, th, t, k):
    n, d, gap = 6, 4.6 - 0.8 * t, 3.4 + 2.4 * t
    col, mat = th["pillar"]
    for i in range(n):
        z = cursor_gap(c, d, gap)
        for _try in range(30):
            x = clampx(c["x"] * 0.3 + rng.uniform(-5, 5))
            if shape_gap(("c", c["x"], c["z"], 0, c["sz"], c["sz"]), ("c", x, z, 0, d, d)) <= 6.0:
                break
        top = c["y"] + rng.choice([0, 1, 2, -1, -2, 0])
        vcyl("Pillar", x, SEA, top, z, d, col, mat)
        disc("Cap", x, top + 0.05, z, d + 0.6, 0.3, th["edge"], "Neon", collide=False, shadow=False)
        walk.append(("c", x, z, top, d, d))
        set_c(c, x, top, z, d)


def _land(c, th, sz=10, gap=2.0):
    z = cursor_gap(c, sz, gap)
    slab(th, c["x"], c["y"], z, 10, sz)
    set_c(c, c["x"], c["y"], z, sz)


def k_ferry(c, th, t, k):
    L, w = 22 + 6 * t, 8
    period = 7.0 - 2 * t
    z = cursor_gap(c, w, 2)
    col, mat = th["alt"]
    box("Rail", (0.5, 0.3, L + w), (c["x"], c["y"] - 1.2, z + L / 2), th["edge"], "Neon", collide=False, shadow=False)
    box("Move|0,0,%.1f|%.1f|0" % (L, period), (w, 1, w), (c["x"], c["y"] - 0.5, z), col, mat)
    walk.append(("brk",))
    z_end = z + L + w / 2 + 2 + 5
    slab(th, c["x"], c["y"], z_end, 10, 10)
    walk.append(("brk",))
    set_c(c, c["x"], c["y"], z_end, 10)


def k_sliders(c, th, t, k):
    n, amp, w = 3, 6 + 3 * t, 7
    period = 4.2 - 1.2 * t
    col, mat = th["alt"]
    walk.append(("brk",))
    z = c["z"] + c["sz"] / 2
    for i in range(n):
        z = z + 3.4 + w / 2
        box("Move|%.1f,0,0|%.1f|%.2f" % (2 * amp, period, i * period / 3.0), (w, 1, w),
            (c["x"] - amp, c["y"] - 0.5, z), col, mat)
        z += w / 2
    z_end = cursor_gap({"z": z, "sz": 0}, 10, 3.4)
    slab(th, c["x"], c["y"], z_end, 12, 10)
    walk.append(("brk",))
    set_c(c, c["x"], c["y"], z_end, 10)


def k_elevator(c, th, t, k):
    H, w = 8.0, 8
    period = 5.0 - 1.5 * t
    z = cursor_gap(c, w, 2.5)
    col, mat = th["alt"]
    box("Move|0,%.1f,0|%.1f|0" % (H, period), (w, 1, w), (c["x"], c["y"] - 0.5, z), col, mat)
    box("Shaft", (0.5, H + 2, 0.5), (c["x"], c["y"] + H / 2 - 1, z), th["edge"], "Neon", collide=False, shadow=False)
    walk.append(("brk",))
    z_end = z + w / 2 + 2.5 + 5
    slab(th, c["x"], c["y"] + H, z_end, 10, 10)
    walk.append(("brk",))
    set_c(c, c["x"], c["y"] + H, z_end, 10)


def k_spinner(c, th, t, k):
    z_len = 26 if t < 0.4 else 40
    z0 = cursor_gap(c, z_len, 2)
    slab(th, c["x"], c["y"], z0, 14, z_len)
    speeds = [1.5 + 1.4 * t]
    bars = [z0]
    if z_len > 30:
        bars = [z0 - 9, z0 + 9]
        speeds = [speeds[0], -speeds[0] * 1.15]
    for bz, sp in zip(bars, speeds):
        box("Spin|%.2f" % sp, (18, 1.2, 1.4), (c["x"], c["y"] + 1.7, bz), (255, 60, 60), "Neon")
        vcyl("Axle", c["x"], c["y"], c["y"] + 1.7, bz, 1.0, th["pillar"][0], th["pillar"][1], collide=False)
    set_c(c, c["x"], c["y"], z0, z_len)


def k_crumble(c, th, t, k):
    rows, tile, gap = 5 + int(t * 3), 5.0, 1.6
    delay = 0.55 - 0.25 * t
    col, mat = th["alt"]
    z = c["z"] + c["sz"] / 2 + 2 - tile / 2 - gap
    prev_hole = -1
    walk.append(("brk",))
    for r in range(rows):
        z += tile + gap
        hole = rng.choice([h for h in range(3) if h != prev_hole])
        prev_hole = hole
        for ci in range(3):
            if ci == hole:
                continue
            box("Crumble|%.2f|4" % delay, (tile, 1, tile), (c["x"] + (ci - 1) * (tile + gap), c["y"] - 0.5, z), col, mat)
    z_end = z + tile / 2 + 2 + 5
    slab(th, c["x"], c["y"], z_end, 12, 10)
    walk.append(("brk",))
    set_c(c, c["x"], c["y"], z_end, 10)


def k_bounce(c, th, t, k):
    z = cursor_gap(c, 9, 3.0)
    box("Bounce|90", (9, 1, 9), (c["x"], c["y"] - 0.5, z), th["edge"], "Neon")
    box("Spring", (6, 0.3, 6), (c["x"], c["y"] + 0.1, z), (255, 255, 255), "Neon", collide=False, shadow=False)
    zl = z + 15
    walk.append(("brk",))
    slab(th, c["x"], c["y"] + 14, zl, 12, 12)
    set_c(c, c["x"], c["y"] + 14, zl, 12)


def k_sweeper(c, th, t, k):
    z_len = 36
    z0 = cursor_gap(c, z_len, 2)
    slab(th, c["x"], c["y"], z0, 14, z_len)
    period = 4.4 - 1.2 * t
    box("KillMove|0,0,22|%.1f|0" % period, (12.5, 3.2, 1.2), (c["x"], c["y"] + 1.6, z0 - 11), (255, 50, 50), "Neon")
    if t > 0.45:
        box("KillMove|0,0,-22|%.1f|0" % period, (12.5, 3.2, 1.2), (c["x"], c["y"] + 1.6, z0 + 11), (255, 120, 40), "Neon")
    set_c(c, c["x"], c["y"], z0, z_len)


def k_conveyor(c, th, t, k):
    L = 30
    z0 = cursor_gap(c, L, 2)
    spd = 8 + 4 * t
    col, mat = th["alt"]
    box("Conv|0,0,%.1f" % -spd, (10, 1, L), (c["x"], c["y"] - 0.5, z0), col, mat)
    for q in range(6):
        box("Arrow", (8, 0.12, 0.8), (c["x"], c["y"] + 0.02, z0 - L / 2 + 3 + q * 5), th["edge"], "Neon", collide=False, shadow=False)
    walk.append(("brk",))
    walk.append(("r", c["x"], z0, c["y"], 10, L))
    set_c(c, c["x"], c["y"], z0, L)
    _land(c, th)


def k_glass(c, th, t, k):
    rows = 6 + int(t * 3)
    walk.append(("brk",))
    z = c["z"] + c["sz"] / 2 + 3
    for r in range(rows):
        z += 6 + 3.2
        fake = rng.choice([-1, 1])
        for side in (-1, 1):
            is_fake = side == fake
            nm = "Crumble|0.08|8" if is_fake else "Glass"
            box(nm, (6, 0.8, 6), (c["x"] + side * 4, c["y"] - 0.4, z - 3), (150, 225, 245), "Glass", transp=0.35)
    z_end = z + 3 + 2.5 + 5
    slab(th, c["x"], c["y"], z_end, 12, 10)
    walk.append(("brk",))
    set_c(c, c["x"], c["y"], z_end, 10)


def k_switch(c, th, t, k):
    sid = "S%d" % k
    walk.append(("brk",))
    # side stubs to the button (right side of the pad)
    slab(th, c["x"] + 12.5, c["y"], c["z"], 5, 5, record=False)
    slab(th, c["x"] + 20.5, c["y"], c["z"], 6, 6, alt=True, record=False)
    box("Button|%s" % sid, (4, 0.6, 4), (c["x"] + 20.5, c["y"] + 0.3, c["z"]), (255, 220, 60), "Neon")
    box("Hint", (6.4, 0.1, 6.4), (c["x"] + 20.5, c["y"] + 0.05, c["z"]), (255, 255, 255), "Neon", collide=False, shadow=False)
    z = c["z"] + c["sz"] / 2 + 1.5
    for i in range(6):
        z += 3.5 + 3.5
        box("Ghost|%s" % sid, (7, 1, 7), (c["x"], c["y"] - 0.5, z), th["edge"], "Neon", transp=0.75, collide=False)
        z += 3.5
    z_end = z + 1.5 + 5
    slab(th, c["x"], c["y"], z_end, 12, 10)
    walk.append(("brk",))
    set_c(c, c["x"], c["y"], z_end, 10)


KINDS = dict(hops=k_hops, zigzag=k_zigzag, stairs=k_stairs, beam=k_beam, pillars=k_pillars, ferry=k_ferry,
             sliders=k_sliders, elevator=k_elevator, spinner=k_spinner, crumble=k_crumble, bounce=k_bounce,
             sweeper=k_sweeper, conveyor=k_conveyor, glass=k_glass, switch=k_switch)


# ------------------------------------------------------------------ landmarks and gates
def landmark(j, x, z, top):
    th = THEMES[j - 1]
    side = 1 if x > 0 else -1
    h = top - SEA
    mid = SEA + h / 2
    if j == 1:
        vcyl("Column", x, SEA, top, z, 9, (236, 226, 204), "Concrete")
        for q in range(3):
            disc("Ring", x, top - 4 - q * 9, z, 10.4, 0.8, th["edge"], "Neon", collide=False)
        disc("Capital", x, top + 0.5, z, 14, 1.4, (214, 202, 178), "Concrete")
    elif j == 2:
        vcyl("Pillar", x, SEA, top, z, 7, (170, 175, 182), "Metal")
        for q in range(4):
            disc("Band", x, top - 3 - q * 12, z, 7.6, 1.2, (60, 220, 255), "Neon", collide=False)
    elif j == 3:
        box("SeatTower", (11, h, 11), (x, mid, z), (176, 48, 44), "Fabric")
        for q in range(4):
            box("Stripe", (11.4, 1.2, 11.4), (x, top - 4 - q * 10, z), (235, 235, 235), "SmoothPlastic", collide=False)
    elif j == 4:
        box("Shelf", (12, h, 12), (x, mid, z), (130, 90, 55), "Wood")
        cols = [(200, 60, 60), (60, 110, 200), (60, 160, 90), (230, 190, 50), (130, 70, 170)]
        for q in range(8):
            box("Book", (12.6, 2.4, 9), (x, top - 3 - q * 4.2, z), cols[q % 5], "SmoothPlastic", collide=False)
    elif j == 5:
        vcyl("Tube", x, SEA, top - 10, z, 8, (190, 230, 240), "Glass", transp=0.45)
        vcyl("Liquid", x, top - 36, top - 12, z, 6, (80, 255, 150), "Neon", collide=False)
        ball("Flask", x, top, z, 18, (200, 240, 245), "Glass", transp=0.5, collide=False)
        ball("Core", x, top, z, 9, (80, 255, 150), "Neon", collide=False)
    elif j == 6:
        box("Counter", (11, h, 11), (x, mid, z), (240, 238, 232), "Marble")
        ball("Drop", x, top + 6, z, 16, (150, 90, 230), "SmoothPlastic", collide=False)
        box("Band", (11.4, 2.4, 11.4), (x, top - 5, z), (46, 160, 90), "SmoothPlastic", collide=False)
    elif j == 7:
        vcyl("Trunk", x, SEA, top, z, 7, (95, 70, 45), "Wood")
        ball("Leaves", x, top + 8, z, 26, (60, 140, 60), "Grass", collide=False)
        ball("Leaves", x + side * 8, top + 1, z + 5, 16, (80, 160, 70), "Grass", collide=False)
    elif j == 8:
        vcyl("Column", x, SEA, top, z, 8, (96, 100, 108), "Metal")
        for q in range(5):
            box("Slit", (8.4, 1.0, 1.2), (x, top - 4 - q * 11, z), (255, 255, 255), "Neon", collide=False)
    elif j == 9:
        vcyl("Stem", x, SEA, top - 8, z, 3, (50, 56, 70), "Metal")
        box("Monitor", (22, 14, 2), (x, top, z), (20, 24, 32), "SmoothPlastic",
            text=dict(face="Front" if side > 0 else "Back", text="</>  01101", color=(60, 220, 255), bg=(10, 20, 40), bg_t=0.0))
    else:
        vcyl("Core", x, SEA, top, z, 4, (200, 235, 240), "Glass", transp=0.4)
        for q in range(26):
            a = q * 0.55
            yy = top - q * 3.2
            ball("A", x + math.cos(a) * 6, yy, z + math.sin(a) * 6, 2.6, (255, 90, 170), "Neon", collide=False)
            ball("B", x - math.cos(a) * 6, yy, z - math.sin(a) * 6, 2.6, (60, 220, 255), "Neon", collide=False)


def level_arch(k, c, final=False):
    z = c["z"]
    y = c["y"]
    # v54: a small number plate on one post instead of a wide board (the owner dislikes sign clutter); FINISH stays big
    if final:
        for s in (-1, 1):
            box("Post", (0.6, 9, 0.6), (c["x"] + s * 7.4, y + 4.5, z), (60, 60, 66), "Metal", collide=False)
        sign("LevelSign", "FINISH", (c["x"], y + 9.5, z), (15.6, 3.2, 0.5), "Front", color=(255, 255, 255),
             bg=(150, 110, 20))
        return
    box("Post", (0.5, 5.5, 0.5), (c["x"] + 7.4, y + 2.75, z), (60, 60, 66), "Metal", collide=False)
    sign("LevelSign", str(k), (c["x"] + 7.4, y + 6.4, z), (2.6, 1.8, 0.3), "Front", color=(255, 255, 255),
         bg=(24, 70, 48))


def zone_gate(j, c):
    z = c["z"] + c["sz"] / 2 + 10
    y = c["y"]
    ar, en = ZONE_NAMES[j - 1]
    for s in (-1, 1):
        box("GatePost", (3, 28, 3), (s * 17, y + 14, z), (45, 50, 58), "Metal", collide=False)
    sign("ZoneGate", "%s\n%s" % (ar, en), (0, y + 27, z), (40, 10, 1.6), "Front", color=(255, 255, 255),
         bg=tuple(max(0, v - 60) for v in THEMES[j - 1]["edge"]))
    for s in (-1, 1):
        box("GateGlow", (0.5, 26, 0.5), (s * 15.4, y + 13, z), THEMES[j - 1]["edge"], "Neon", collide=False, shadow=False)
    c["z"] += 0  # gate stands beside the path, never blocks it


# ------------------------------------------------------------------ build
def build_course():
    c = dict(x=0.0, y=0.0, z=-15.0, sz=14.0)
    walk.append(("r", 0.0, -15.0, 0.0, 14.0, 14.0))
    checkpoint_data = {}
    k = 0
    with G.Group("Course"):
        for j in range(1, 11):
            th = THEMES[j - 1]
            with G.Group("Zone%02d" % j):
                if j > 1:
                    zone_gate(j, c)
                for entry in SEQ[j - 1]:
                    k += 1
                    t = (k - 1) / 99.0
                    z_start = c["z"]
                    with G.Group("Level%03d" % k):
                        kinds = entry if isinstance(entry, tuple) else (entry,)
                        for kn in kinds:
                            KINDS[kn](c, th, t, k)
                            if len(kinds) > 1:
                                _land(c, th, 8, 2.0)
                        final = k == 100
                        size = 20 if final else 14
                        pz = cursor_gap(c, size, 3.0)
                        px, py = c["x"], c["y"]
                        G.part("Checkpoint_%d" % k, (size, 1, size), (px, py - 0.5, pz),
                               (230, 180, 50) if final else (46, 160, 90), "Neon" if final else "SmoothPlastic",
                               text=dict(face="Top", text="FINISH" if final else "%d" % k, color=(255, 255, 255),
                                         bg=(150, 110, 20) if final else (30, 110, 60), bg_t=0.0))
                        walk.append(("r", px, pz, py, size, size))
                        set_c(c, px, py, pz, size)
                        level_arch(k, c, final)
                        if final:
                            vcyl("TrophyStem", px, py, py + 8, pz, 1.8, (230, 180, 50), "Metal", collide=False)
                            ball("TrophyCup", px, py + 11, pz, 8, (230, 180, 50), "Metal", collide=False)
                        # landmarks on both sides, mid-stage
                        zm = (z_start + pz) / 2
                        for s in (-1, 1):
                            landmark(j, s * rng.uniform(36, 52), zm + rng.uniform(-14, 14), py + rng.uniform(-6, 22))
                        checkpoint_data[k] = (px, py, pz)
    return c, checkpoint_data


def cloud_sea(z_end):
    with G.Group("CloudSea"):
        z = -400
        while z < z_end + 600:
            box("Cloud", (2000, 6, 2000), (0, SEA - 3, z + 1000), (255, 255, 255), "SmoothPlastic",
                transp=0.1, collide=False, shadow=False)
            z += 2000


def shape_gap(a, b):
    ca, cb = a[0] == "c", b[0] == "c"
    ax, az, asx, asz = a[1], a[2], a[4], a[5]
    bx, bz, bsx, bsz = b[1], b[2], b[4], b[5]
    dxc, dzc = abs(ax - bx), abs(az - bz)
    if ca and cb:
        return max(0.0, math.hypot(dxc, dzc) - asx / 2 - bsx / 2)
    if ca or cb:
        r = asx / 2 if ca else bsx / 2
        hx = bsx / 2 if ca else asx / 2
        hz = bsz / 2 if ca else asz / 2
        return max(0.0, math.hypot(max(0, dxc - hx), max(0, dzc - hz)) - r)
    return math.hypot(max(0, dxc - (asx + bsx) / 2), max(0, dzc - (asz + bsz) / 2))


def validate():
    worst_gap = worst_rise = 0.0
    bad = []
    n = 0
    prev = None
    for e in walk:
        if e[0] == "brk":
            prev = None
            continue
        if prev is not None:
            n += 1
            gap = shape_gap(prev, e)
            rise = e[3] - prev[3]
            worst_gap, worst_rise = max(worst_gap, gap), max(worst_rise, rise)
            if gap > 7.0 or rise > 2.6:
                bad.append((prev, e, round(gap, 2), round(rise, 2)))
        prev = e
    return worst_gap, worst_rise, bad, n


def preview(prefix, z0, z1, yaw=35, pitch=32, scale=3.2, ymin=-30):
    from PIL import Image, ImageDraw
    a, b = math.radians(yaw), math.radians(pitch)
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)

    def proj(x, y, z):
        u = x * ca - z * sa
        w = x * sa + z * ca
        v = y * cb - w * sb
        return u, v, w

    items = [s for s in scene if z0 - 60 <= s[2] <= z1 + 60]
    pts = []
    for s in items:
        for dx in (-1, 1):
            for dy in (-1, 1):
                for dz in (-1, 1):
                    u, v, w = proj(s[0] + dx * s[3] / 2, max(s[1] + dy * s[4] / 2, ymin), s[2] + dz * s[5] / 2)
                    pts.append((u, v))
    us, vs = [p[0] for p in pts], [p[1] for p in pts]
    W, H = int((max(us) - min(us)) * scale) + 20, int((max(vs) - min(vs)) * scale) + 20
    img = Image.new("RGB", (W, H), (190, 220, 245))
    d = ImageDraw.Draw(img)

    def P(x, y, z):
        u, v, w = proj(x, max(y, ymin), z)
        return ((u - min(us)) * scale + 10, (max(vs) - v) * scale + 10)

    for s in sorted(items, key=lambda s: -(proj(s[0], s[1], s[2])[2])):
        x, y, z, sx, sy, sz, col, tr, shp = s
        if tr > 0.6:
            continue
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        y_lo = max(y - hy, ymin)
        if y_lo >= y + hy:
            continue
        c0 = tuple(int(v) for v in col)
        top = tuple(min(255, int(v * 1.15)) for v in c0)
        left = tuple(int(v * 0.72) for v in c0)
        right = tuple(int(v * 0.88) for v in c0)
        yt, yb = y + hy, y_lo
        d.polygon([P(x - hx, yt, z - hz), P(x + hx, yt, z - hz), P(x + hx, yt, z + hz), P(x - hx, yt, z + hz)], fill=top)
        d.polygon([P(x - hx, yt, z - hz), P(x - hx, yt, z + hz), P(x - hx, yb, z + hz), P(x - hx, yb, z - hz)], fill=left)
        d.polygon([P(x - hx, yt, z - hz), P(x + hx, yt, z - hz), P(x + hx, yb, z - hz), P(x - hx, yb, z - hz)], fill=right)
        d.polygon([P(x + hx, yt, z - hz), P(x + hx, yt, z + hz), P(x + hx, yb, z + hz), P(x + hx, yb, z - hz)], fill=left)
        d.polygon([P(x - hx, yt, z + hz), P(x + hx, yt, z + hz), P(x + hx, yb, z + hz), P(x - hx, yb, z + hz)], fill=right)
    out = "%s_%d_%d.png" % (prefix, z0, z1)
    img.save(out)
    return out


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    prev_prefix = None
    if "--preview" in sys.argv:
        prev_prefix = sys.argv[sys.argv.index("--preview") + 1]
    G.hub()
    c_end, cps = build_course()
    cloud_sea(c_end["z"])
    gap, rise, bad, n = validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (G.rid(), "".join(G.buf))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("parts:", G.nparts[0], "| course length: %.0f studs" % c_end["z"], "| top y: %.0f" % c_end["y"],
          "| steps checked:", n, "| worst gap: %.2f" % gap, "| worst rise: %.2f" % rise, "| violations:", len(bad),
          "| KB:", len(xml) // 1024)
    for v in bad[:6]:
        print("  BAD", v)
    if prev_prefix:
        for z0, z1 in ((-80, 160), (700, 900)):
            print(preview(prev_prefix, z0, z1))
