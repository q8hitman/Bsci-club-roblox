"""v6: campus (genmap5) + specialty-themed obby (10 biology specialties, new mechanics).
Run: python tools/genmap6.py kuwait-parkour/src/map/Map.rbxmx
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap5 as C5  # noqa: E402
import genmap3 as C3  # noqa: E402
import genmap2 as M2  # noqa: E402
import genmap as G  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rng = random.Random(6006)


# ------------------------------------------------------------------ themes per specialty
def T(main, alt, edge, pillar):
    return dict(main=main, alt=alt, edge=edge, pillar=pillar)


M2.THEMES[:] = [
    T(((126, 176, 96), "Grass"), ((150, 108, 70), "Wood"), (255, 240, 150), ((120, 84, 54), "Wood")),                 # botany
    T(((222, 202, 160), "Sand"), ((240, 234, 218), "Marble"), (255, 190, 120), ((190, 170, 130), "Sandstone")),       # zoology
    T(((150, 222, 204), "SmoothPlastic"), ((160, 130, 210), "SmoothPlastic"), (200, 255, 120), ((120, 190, 180), "Glass")),  # micro
    T(((244, 176, 190), "SmoothPlastic"), ((210, 140, 170), "SmoothPlastic"), (255, 255, 255), ((230, 170, 200), "Glass")),   # cell
    T(((86, 112, 186), "SmoothPlastic"), ((46, 62, 120), "SmoothPlastic"), (255, 130, 200), ((70, 90, 160), "Glass")),        # genetics
    T(((232, 240, 242), "SmoothPlastic"), ((240, 150, 60), "SmoothPlastic"), (80, 230, 190), ((60, 130, 138), "Metal")),     # biochem
    T(((126, 160, 112), "Grass"), ((100, 160, 210), "Glass"), (200, 240, 255), ((100, 84, 64), "Wood")),                     # ecology
    T(((214, 100, 108), "Fabric"), ((246, 236, 232), "SmoothPlastic"), (255, 220, 120), ((190, 70, 84), "Fabric")),          # physiology
    T(((244, 246, 248), "SmoothPlastic"), ((200, 210, 220), "Metal"), (60, 220, 255), ((170, 200, 215), "Glass")),           # biotech
    T(((46, 56, 88), "SmoothPlastic"), ((24, 30, 52), "SmoothPlastic"), (90, 255, 150), ((60, 76, 120), "Metal")),           # bioinfo
]
M2.ZONE_NAMES[:] = [
    ("علم النبات", "Botany"), ("علم الحيوان", "Zoology"), ("مايكروبيولوجي", "Microbiology"),
    ("بيولوجيا الخلية", "Cell Biology"), ("علم الوراثة", "Genetics"), ("بايوكيمستري", "Biochemistry"),
    ("علم البيئة", "Ecology"), ("الفسيولوجيا", "Physiology"), ("البايوتكنولوجي", "Biotechnology"),
    ("المعلوماتية الحيوية", "Bioinformatics"),
]
M2.SEQ[:] = [
    ["hops", "leaves", "beam", "zigzag", "blink", "pillars", "spinner", "crumble", "sliders", ("leaves", "blink", "spinner")],
    ["hops", "ferry", "conveyor", "pillars", "glass", "sweeper", "crumble", "elevator", "zigzag", ("ferry", "conveyor", "sweeper")],
    ["zigzag", "blink", "spinner", "leaves", "crumble", "carousel", "sliders", "laser", "hops", ("blink", "carousel", "laser")],
    ["hops", "glass", "elevator", "molecule", "switch", "pillars", "sliders", "blink", "sweeper", ("glass", "molecule", "elevator")],
    ["stairs", "helix", "zigzag", "spinner", "glass", "switch", "blink", "crumble", "carousel", ("helix", "spinner", "blink")],
    ["molecule", "gel", "hops", "conveyor", "switch", "laser", "bounce", "glass", "carousel", ("molecule", "gel", "laser")],
    ["hops", "ferry", "conveyor", "leaves", "beam", "pillars", "elevator", "crumble", "sweeper", ("ferry", "leaves", "conveyor")],
    ["heartbeat", "laser", "sliders", "elevator", "blink", "switch", "carousel", "zigzag", "crumble", ("heartbeat", "laser", "carousel")],
    ["gel", "bounce", "laser", "glass", "helix", "switch", "crumble", "carousel", "sweeper", ("gel", "helix", "laser")],
    ["blink", "molecule", "gel", "laser", "helix", "heartbeat", "glass", "carousel", "sliders",
     ("blink", "laser", "helix", "heartbeat")],
]


# ------------------------------------------------------------------ new stage kinds
def k_blink(c, th, t, k):
    n, w, gap = 6, 7.0 - 1.5 * t, 3.0 + 2.0 * t
    on, off = 3.0 - 0.8 * t, 1.4
    for i in range(n):
        z = M2.cursor_gap(c, w, gap)
        x = M2.clampx(c["x"] * 0.5 + (4.0 if i % 2 else -4.0))
        phase = (i % 2) * (on + off) / 2
        col, mat = th["main"] if i % 2 == 0 else th["alt"]
        box("Blink|%.1f|%.1f|%.2f" % (on, off, phase), (w, 1, w), (x, c["y"] - 0.5, z), col, mat)
        box("Rim", (w, 0.12, w), (x, c["y"] + 0.02, z), th["edge"], "Neon", collide=False, shadow=False)
        M2.walk.append(("r", x, z, c["y"], w, w))
        M2.set_c(c, x, c["y"], z, w)


def k_heartbeat(c, th, t, k):
    n, w, gap = 4, 8.0, 3.0
    amp, period = 3.0 + 1.2 * t, 2.6
    col, mat = th["main"]
    M2.walk.append(("brk",))
    for i in range(n):
        z = M2.cursor_gap(c, w, gap)
        box("Move|0,%.1f,0|%.1f|%.2f" % (amp, period, i * period / 4), (w, 1, w), (c["x"], c["y"] - 0.5, z), col, mat)
        M2.set_c(c, c["x"], c["y"], z, w)
    M2.walk.append(("brk",))
    M2._land(c, th, 10, 3.0)


def k_laser(c, th, t, k):
    L = 40
    z0 = M2.cursor_gap(c, L, 2)
    M2.slab(th, c["x"], c["y"], z0, 14, L)
    beams = 3 + int(t * 2)
    gap = L / (beams + 1)
    for i in range(beams):
        bz = z0 - L / 2 + (i + 1) * gap
        on, off, phase = 1.4, 1.9 - 0.6 * t, i * 0.9
        # v31: a full-height laser curtain (was a 0.5-stud beam anyone could hop over); cross it while it is off
        box("KillBlink|%.1f|%.1f|%.2f" % (on, off, phase), (14, 10, 0.3), (c["x"], c["y"] + 5, bz), (255, 60, 90), "Neon",
            transp=0.35)
        for s_ in (-1, 1):
            box("Post", (0.8, 11, 0.8), (c["x"] + s_ * 7.6, c["y"] + 5.5, bz), (50, 54, 62), "SmoothPlastic", collide=False)
            box("Emitter", (1.2, 1.2, 1.2), (c["x"] + s_ * 7.6, c["y"] + 10.6, bz), (255, 60, 90), "Neon", collide=False,
                shadow=False)
    # green safe zones between the curtains (always laser-free: stand here and wait for the next gap)
    for i in range(beams + 1):
        sz_ = z0 - L / 2 + (i + 0.5) * gap
        box("SafeZone", (13, 0.08, gap - 2.4), (c["x"], c["y"] + 0.04, sz_), (90, 230, 130), "Neon", transp=0.45,
            collide=False, shadow=False)
    M2.set_c(c, c["x"], c["y"], z0, L)


def k_gel(c, th, t, k):
    lanes, lw, gx, L = 3, 5.0, 1.0, 26
    z0 = M2.cursor_gap(c, L, 2)
    fwd = rng.randint(0, 2)
    M2.walk.append(("brk",))
    for ln in range(lanes):
        x = c["x"] + (ln - 1) * (lw + gx)
        spd = (14.0 if ln == fwd else -(7.0 + 4 * t))
        col, mat = (th["alt"] if ln != fwd else th["main"])
        box("Conv|0,0,%.1f" % spd, (lw, 1, L), (x, c["y"] - 0.5, z0), col, mat)
        for a in range(4):
            box("Arrow", (lw - 1.6, 0.1, 0.7), (x, c["y"] + 0.03, z0 - L / 2 + 4 + a * 6), th["edge"], "Neon", collide=False, shadow=False)
        box("Well", (lw, 0.2, 1.2), (x, c["y"] + 0.05, z0 - L / 2 + 0.8), (30, 34, 44), "SmoothPlastic", collide=False)
    M2.walk.append(("brk",))
    z_end = z0 + L / 2 + 2 + 5
    M2.slab(th, c["x"], c["y"], z_end, 14, 10)
    M2.walk.append(("brk",))
    M2.set_c(c, c["x"], c["y"], z_end, 10)


def k_helix(c, th, t, k):
    R, w = 10.0, 5.5
    cx = c["x"]
    cz = c["z"] + c["sz"] / 2 + R + 2.0
    vcyl("Core", cx, M2.SEA, c["y"] + 16, cz, 1.6, (255, 255, 255), "Neon", collide=False, shadow=False)
    for i in range(5):
        a_ = math.radians(180 - i * 45)
        x, z = cx + R * math.sin(a_), cz + R * math.cos(a_)
        y = c["y"] + 2.2 * (i + 1)
        col, mat = th["main"] if i % 2 == 0 else th["alt"]
        disc("Rung", x, y - 0.5, z, w, 1, col, mat)
        disc("RungEdge", x, y + 0.02, z, w + 0.2, 0.12, th["edge"], "Neon", collide=False, shadow=False)
        M2.walk.append(("c", x, z, y, w, w))
    top = c["y"] + 11.0
    z_l = cz + R + 8.5
    M2.slab(th, cx, top, z_l, 10, 10)
    M2.walk.append(("brk",))
    M2.set_c(c, cx, top, z_l, 10)


def k_molecule(c, th, t, k):
    n, d = 6, 5.6
    cols = [(224, 70, 70), (244, 244, 244), (80, 82, 92)]
    prev = None
    M2.walk.append(("brk",))
    for i in range(n):
        z = M2.cursor_gap(c, d, 3.2 + 2.2 * t)
        for _t in range(30):
            x = M2.clampx(c["x"] * 0.3 + rng.uniform(-6, 6))
            if M2.shape_gap(("c", c["x"], c["z"], 0, c["sz"], c["sz"]), ("c", x, z, 0, d, d)) <= 6.0:
                break
        top = c["y"] + rng.choice([0, 1, 2, -1, 0])
        disc("Atom", x, top - 0.5, z, d, 1, cols[i % 3], "SmoothPlastic")
        disc("AtomRing", x, top + 0.02, z, d + 0.2, 0.12, th["edge"], "Neon", collide=False, shadow=False)
        if prev:
            dx, dz = x - prev[0], z - prev[1]
            ln = math.hypot(dx, dz)
            box("Bond", (0.7, 0.7, ln), ((x + prev[0]) / 2, top - 0.9, (z + prev[1]) / 2), (190, 194, 200), "SmoothPlastic",
                collide=False, rot=(0, math.degrees(math.atan2(dx, dz)), 0))
        M2.walk.append(("c", x, z, top, d, d))
        M2.set_c(c, x, top, z, d)
        prev = (x, z)
    M2.walk.append(("brk",))


def k_leaves(c, th, t, k):
    n, d = 5, 8.0
    M2.walk.append(("brk",))
    z = c["z"] + c["sz"] / 2 + 5.0 + d / 2
    for i in range(n):
        x = (4.0 if i % 2 else -4.0)
        box("Bounce|58", (0.7, d, d), (x, c["y"] - 0.35, z), (104, 196, 104), "Grass", shape="Cylinder", rot=(0, 0, 90))
        vcyl("Stem", x, M2.SEA, c["y"] - 0.7, z, 1.0, (86, 130, 70), "Grass", collide=False)
        disc("Vein", x, c["y"] + 0.02, z, d - 2, 0.1, (200, 250, 190), "Neon", collide=False, shadow=False)
        z += 13.0
    z_end = z - 13.0 + d / 2 + 2.2 + 5
    M2.slab(th, 0, c["y"], z_end, 12, 10)
    M2.walk.append(("brk",))
    M2.set_c(c, 0.0, c["y"], z_end, 10)


def k_carousel(c, th, t, k):
    R = 16.0
    cx = c["x"]
    cz = c["z"] + c["sz"] / 2 + 3.0 + R
    gid = "c%d" % k
    spd = (0.42 + 0.25 * t) * (1 if k % 2 else -1)
    col, mat = th["alt"]
    M2.walk.append(("brk",))
    box("Roto|%.2f|%s" % (spd, gid), (2 * R, 1, 5), (cx, c["y"] - 0.5, cz), col, mat)
    box("Roto|%.2f|%s" % (spd, gid), (5, 1, 2 * R), (cx, c["y"] - 0.5, cz), col, mat)
    disc("Hub", cx, c["y"] + 0.1, cz, 8, 0.4, th["edge"], "Neon", collide=False, shadow=False)
    vcyl("Mast", cx, M2.SEA, c["y"] - 1.0, cz, 3.0, th["pillar"][0], th["pillar"][1], collide=False)
    z_end = cz + R + 3.0 + 5
    M2.slab(th, cx, c["y"], z_end, 12, 10)
    M2.walk.append(("brk",))
    M2.set_c(c, cx, c["y"], z_end, 10)


M2.KINDS.update(dict(blink=k_blink, heartbeat=k_heartbeat, laser=k_laser, gel=k_gel, helix=k_helix,
                     molecule=k_molecule, leaves=k_leaves, carousel=k_carousel))


# ------------------------------------------------------------------ specialty environments
def ribs(x, g, z, h):
    for i in range(7):
        a0, a1 = -0.2 + i * 0.5, -0.2 + (i + 1) * 0.5
        box("Rib", (1.2, 1.2, 5.0), (x, g + h * (0.5 + 0.5 * math.sin(a0 + 0.25)), z + math.cos(a0 + 0.25) * h * 0.4),
            (240, 234, 220), "SmoothPlastic", collide=False, rot=(math.degrees(a0), 0, 0))


def env6(j, z0, z1, g):
    th = M2.THEMES[j - 1]
    ar, en = M2.ZONE_NAMES[j - 1]
    L = z1 - z0
    zc = (z0 + z1) / 2
    FLOOR = [((92, 138, 78), "Grass"), ((226, 206, 164), "Sand"), ((40, 36, 60), "SmoothPlastic"), ((226, 160, 176), "SmoothPlastic"),
             ((24, 30, 64), "SmoothPlastic"), ((236, 240, 242), "SmoothPlastic"), ((86, 128, 80), "Grass"),
             ((196, 96, 104), "Fabric"), ((240, 244, 246), "SmoothPlastic"), ((16, 20, 34), "SmoothPlastic")]
    WALL = [((190, 226, 200), "Glass", 0.55), ((120, 170, 190), "Glass", 0.5), ((60, 40, 90), "SmoothPlastic", 0.0),
            ((240, 184, 196), "SmoothPlastic", 0.0), ((40, 52, 110), "SmoothPlastic", 0.0), ((230, 238, 240), "SmoothPlastic", 0.0),
            ((150, 190, 220), "Glass", 0.6), ((170, 60, 76), "Fabric", 0.0), ((226, 232, 238), "SmoothPlastic", 0.0),
            ((20, 26, 44), "SmoothPlastic", 0.0)]
    wc, wm, wa = WALL[j - 1]
    C3.hall(g, z0, z1, FLOOR[j - 1], (wc, wm), wa, trim=th["edge"])
    ed = th["edge"]
    step = 30
    if j == 1:      # botany greenhouse
        for z in range(int(z0) + 20, int(z1), 22):
            for s in (-1, 1):
                C3.tree(s * rng.uniform(34, 62), g, z + rng.uniform(-6, 6), rng.uniform(1.0, 1.5), (70 + rng.randint(0, 30), 150, 76))
                vcyl("Stem", s * rng.uniform(26, 50), g, g + 14, z + 8, 0.9, (80, 140, 70), "Grass", collide=False)
                disc("Leaf", s * 40, g + 14, z + 8, 16, 0.5, (96, 180, 96), "Grass", collide=False)
                ball("Flower", s * 56, g + 6, z - 8, 7, [(244, 120, 160), (250, 214, 80), (190, 130, 230)][int(z / 22) % 3],
                     "SmoothPlastic", collide=False)
        for z in range(int(z0) + 10, int(z1), 24):
            box("Rib", (WALL_X2 * 2, 0.8, 1.2), (0, g + 112, z), (230, 240, 236), "SmoothPlastic", collide=False)
    elif j == 2:    # zoology
        for z in range(int(z0) + 30, int(z1), 80):
            ribs(-52, g, z, 26)
            ribs(52, g, z + 40, 26)
            box("Spine", (1.6, 1.6, 36), (-52, g + 18, z), (240, 234, 220), "SmoothPlastic", collide=False)
            ball("Skull", -52, g + 8, z - 22, 8, (240, 234, 220), "SmoothPlastic", collide=False)
        box("Tank", (2, 50, L), (-70, g + 25, zc), (110, 170, 220), "Glass", transp=0.7, collide=False)
        for z in range(int(z0) + 14, int(z1), 20):
            ball("Fish", -66 + rng.uniform(-3, 3), g + rng.uniform(10, 40), z, rng.uniform(3, 5),
                 [(250, 140, 50), (250, 220, 70), (90, 170, 250)][int(z / 20) % 3], "SmoothPlastic", collide=False)
    elif j == 3:    # microbiology
        for z in range(int(z0) + 30, int(z1), 46):
            for s in (-1, 1):
                disc("Dish", s * 46, g + 0.6, z, 34, 1.2, (210, 236, 236), "Glass", transp=0.5, collide=False)
                disc("Agar", s * 46, g + 0.9, z, 30, 0.6, (140, 220, 180), "Neon", collide=False, shadow=False)
                for _ in range(6):
                    ball("Colony", s * 46 + rng.uniform(-11, 11), g + 1.4, z + rng.uniform(-11, 11), rng.uniform(2, 4),
                         [(250, 240, 120), (240, 130, 190), (250, 255, 255)][rng.randint(0, 2)], "SmoothPlastic", collide=False)
            vcyl("Bact", rng.choice([-1, 1]) * 62, g + 6, g + 14, z, 6, (160, 230, 120), "SmoothPlastic", collide=False)
    elif j == 4:    # cell biology
        for z in range(int(z0) + 28, int(z1), 52):
            ball("Nucleus", -52, g + 22, z, 30, (200, 150, 210), "SmoothPlastic", transp=0.2, collide=False)
            ball("Nucleolus", -52, g + 22, z, 12, (120, 70, 150), "SmoothPlastic", collide=False)
            vcyl("Mito", 54, g, g + 20, z, 12, (250, 170, 90), "SmoothPlastic", collide=False)
            for q in range(5):
                box("Crista", (13, 0.8, 1.2), (54, g + 4 + q * 3.4, z), (200, 110, 50), "SmoothPlastic", collide=False)
            for q in range(5):
                disc("Golgi", -30, g + 4 + q * 2.4, z + 20, 18 - q * 1.2, 1.4, (250, 210, 120), "SmoothPlastic", collide=False)
    elif j == 5:    # genetics
        for z in range(int(z0) + 10, int(z1), 10):   # v57: every 10 studs (was 5): half the Neon beads, same helix
            a = z * 0.22
            for s in (-1, 1):
                ball("A", s * 58 + math.cos(a) * 7, g + 16 + 18 * math.sin(z * 0.02), z, 4.0, (255, 110, 190), "Neon",
                     collide=False, shadow=False)
                ball("B", s * 58 - math.cos(a) * 7, g + 16 + 18 * math.sin(z * 0.02), z, 4.0, (80, 220, 255), "Neon",
                     collide=False, shadow=False)
        for z in range(int(z0) + 40, int(z1), 120):
            for q in range(4):
                sign("Punnett", ["AA", "Aa", "Aa", "aa"][q], (-12 + (q % 2) * 24, g + 0.15, z + (q // 2) * 24), (22, 0.2, 22), "Top",
                     bg=[(70, 90, 170), (110, 70, 170), (110, 70, 170), (60, 130, 120)][q])
    elif j == 6:    # biochemistry
        names = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar"]
        for q, nm in enumerate(names):
            sign("Elem", nm, (-WALL_X2 + 1.2, g + 60 - (q // 6) * 12, z0 + 40 + (q % 6) * 12), (0.4, 10, 10), "Right",
                 bg=[(240, 150, 60), (80, 190, 220), (150, 210, 110)][q % 3])
        for z in range(int(z0) + 40, int(z1), 70):
            ball("O", 52, g + 14, z, 12, (224, 70, 70), "SmoothPlastic", collide=False)
            ball("H", 52 + 9, g + 20, z + 6, 7, (245, 245, 245), "SmoothPlastic", collide=False)
            ball("H", 52 - 9, g + 20, z + 6, 7, (245, 245, 245), "SmoothPlastic", collide=False)
            for k2 in range(6):
                ang = k2 * math.pi / 3
                ball("C", -50 + math.cos(ang) * 10, g + 16, z + 20 + math.sin(ang) * 10, 6, (80, 82, 92), "SmoothPlastic", collide=False)
    elif j == 7:    # ecology
        box("River", (24, 0.4, L), (0, g + 0.2, zc), (96, 160, 220), "Glass", transp=0.35, collide=False)
        for z in range(int(z0) + 20, int(z1), 20):
            for s in (-1, 1):
                C3.tree(s * rng.uniform(34, 66), g, z + rng.uniform(-6, 6), rng.uniform(1.1, 1.7), (60 + rng.randint(0, 24), 140, 70))
                ball("Rock", s * rng.uniform(16, 30), g + 1.4, z + rng.uniform(-6, 6), rng.uniform(3, 7), (160, 160, 154), "Slate",
                     collide=False)
    elif j == 8:    # physiology
        for z in range(int(z0) + 60, int(z1), 110):
            ball("Heart", -52, g + 28, z, 26, (210, 50, 66), "SmoothPlastic", collide=False)
            vcyl("Aorta", -52, g + 36, g + 70, z, 6, (230, 70, 80), "SmoothPlastic", collide=False)
            vcyl("Vena", -44, g + 36, g + 70, z + 4, 5, (80, 100, 190), "SmoothPlastic", collide=False)
            ball("LungL", 52, g + 30, z - 10, 24, (244, 160, 170), "SmoothPlastic", collide=False)
            ball("LungR", 52, g + 30, z + 14, 24, (244, 160, 170), "SmoothPlastic", collide=False)
        for q in range(int(L / 6)):
            y = g + 40 + (12 if q % 6 in (2, 3) else (-10 if q % 6 == 4 else 0))
            box("ECG", (0.8, 1.0, 6.4), (-WALL_X2 + 1.4, y, z0 + 4 + q * 6), (80, 255, 140), "Neon", collide=False, shadow=False)
    elif j == 9:    # biotech
        for z in range(int(z0) + 30, int(z1), 50):
            for s in (-1, 1):
                vcyl("Reactor", s * 56, g, g + 50, z, 14, (200, 230, 240), "Glass", transp=0.5)
                vcyl("Media", s * 56, g + 1, g + 34, z, 11, [(120, 255, 170), (255, 220, 90)][int(z / 50) % 2], "Neon",
                     collide=False, shadow=False)
                vcyl("Pipe", s * 56, g + 50, g + 80, z, 2, (150, 160, 170), "Metal", collide=False)
            vcyl("Pipette", 0, g + 80, g + 110, z, 1.6, (230, 240, 250), "Glass", transp=0.4, collide=False)
    else:           # bioinformatics
        for z in range(int(z0) + 14, int(z1), 16):
            for s in (-1, 1):
                box("Rack", (6, 36, 8), (s * 64, g + 18, z), (20, 24, 34), "SmoothPlastic")
                for q in range(6):
                    box("Led", (0.4, 0.8, 6), (s * 60.8, g + 4 + q * 5.6, z), [(80, 255, 140), (80, 200, 255)][(q + int(z / 16)) % 2],
                        "Neon", collide=False, shadow=False)
        for z in range(int(z0) + 30, int(z1), 60):
            sign("Seq", "ATGGCC TAGCTA\nGGATCC AATTCG", (-48, g + 30, z), (22, 10, 0.6), "Back", color=(90, 255, 150), bg=(10, 24, 30))
    C3.zone_sign("%s\n%s" % (ar, en), 0, g, z0 + 14, 40, 9, y=g + 50, bg=tuple(max(0, v - 70) for v in th["edge"]) if False else (30, 40, 60))


WALL_X2 = 72.0
C3.env = env6

# ------------------------------------------------------------------ main
if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    C5.build_campus()
    C5._off[0], C5._off[1], C5._off[2] = C5.COURSE_OFFSET
    C3.build()
    C5._base_part("Portal|Campus", (12, 16, 2), (-26 + C5._off[0] - 18, 8.5, -20), (255, 190, 120), "Neon", transp=0.55,
                  collide=False, shadow=False)
    C5._base_part("PortalCampusSign", (22, 5, 1.2), (-26 + C5._off[0] - 18, 20, -20), (24, 70, 48), "SmoothPlastic",
                  text=dict(face="Front", text="العودة للحرم\nBack to Campus", color=(255, 255, 255), bg=(24, 70, 48), bg_t=0.0))
    gap, rise, bad, n = M2.validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (G.rid(), "".join(G.buf))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("parts:", G.nparts[0], "| steps:", n, "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad), "| KB:", len(xml) // 1024)
    for v in bad[:6]:
        print("  BAD", v)
