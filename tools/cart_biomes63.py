"""v63 Specialties Train: each valley becomes its own world (owner: "change the environment radically, more creative,
the best of the best"). Until now every valley was a flat floor with props scattered on it inside themed walls, so the
eight stages still read as one template. Three layers per valley, all wordless:

  skyline   giant objects BEHIND the long walls, rising over the cliffs (the cliff tops are ~250 above the floor), so
            the valley's world is readable from anywhere on the ride: a microscope over the agar plate, glassware over
            the lab, a city skyline over the crime scene...  They stand outside the valley, never near the rails.
  ground    one designed floor pattern (agar rings, lab tiles, gel lanes, a street grid, centre-pivot crop circles...)
            instead of one flat colour. Thin, non-colliding, under the existing patches.
  midground a themed "forest" in the open floor (mould, molecules, acacias, dandelions, street lamps, hay bales...),
            kept clear of the track (Clear), the theory sculptures and the landmarks.

Local coordinates (cart_tour53 builds inside the cart world offset). Own RNG per valley: the shared rng is untouched,
so the track, the clearance results and the older scenery do not move.
"""
import math
import random

import genmap as G

box, vcyl, disc, ball = G.box, G.vcyl, G.disc, G.ball

CELLZ = 1120.0
BACK = CELLZ + 250.0          # centre line of the skyline objects behind each long wall
WHITE, BLACK, STEEL = (238, 240, 244), (36, 40, 48), (176, 184, 196)


def deco(name, size, pos, col, mat="SmoothPlastic", **kw):
    kw.setdefault("collide", False)
    box(name, size, pos, col, mat, **kw)


def free_spot(rnd, clear, hi, lo, r, taken, tries=40):
    """a spot in the valley's open floor, clear of the track and of everything listed in taken (x, z, r)"""
    for _ in range(tries):
        x, z = rnd.uniform(lo + r + 60, hi - r - 60), rnd.uniform(-CELLZ + r + 60, CELLZ - r - 60)
        if clear.ok(x, z, r) and all(math.hypot(x - a, z - b) > r + c + 8 for a, b, c in taken):
            taken.append((x, z, r))
            return x, z
    return None


def along(hi, lo, n, margin=260):
    """n evenly spaced x positions inside the valley, away from the ridges"""
    return [lo + margin + (hi - lo - 2 * margin) * (i + 0.5) / n for i in range(n)]


# ====================================================================== microbiology: the agar plate in the lab
def micro(rnd, clear, hi, lo, Y, taken):
    cx = (hi + lo) / 2
    # ground: honey-amber agar, lighter in the middle of the plate and darker to the rim (Glass/Ice layers reflected
    # the sky and washed it out to white; an `extra` Reflectance moved the discs out of the streamed valley)
    for d, col in ((2000, (168, 118, 62)), (1500, (178, 128, 70)), (1000, (188, 140, 80)), (520, (198, 152, 92))):
        disc("AgarGloss", cx, Y + 0.02 + d / 100000, 0, d, 0.05, col, "SmoothPlastic", collide=False, shadow=False)
    # colonies the way they really grow on a plate
    def dome(x, z, d, col):   # a flat colony with a lobed edge (no dome or centre bump: those read wrong)
        disc("Colony", x, Y + 0.5, z, d, 0.8, col, "SmoothPlastic", collide=False, shadow=False)
        for q in range(6):
            a = q * math.pi / 3 + rnd.uniform(-0.3, 0.3)
            disc("Colony", x + math.cos(a) * d * 0.4, Y + 0.45, z + math.sin(a) * d * 0.4, d * 0.3, 0.7, col,
                 "SmoothPlastic", collide=False, shadow=False)
    for _ in range(8):   # mould (Penicillium): white fuzzy rim, blue-green spores in the middle, a pale centre
        spot = free_spot(rnd, clear, hi, lo, 40, taken)
        if not spot:
            continue
        x, z = spot
        d = rnd.uniform(46, 78)
        disc("MouldRim", x, Y + 0.2, z, d, 0.4, (248, 248, 244), "SmoothPlastic", collide=False, shadow=False)
        disc("MouldSpores", x, Y + 0.3, z, d * 0.72, 0.4, (70, 140, 120), "SmoothPlastic", collide=False, shadow=False)
        for q in range(7):   # spores clump unevenly, so the green is patchy, not a target
            a = rnd.uniform(0, 2 * math.pi)
            disc("MouldSpores", x + math.cos(a) * d * 0.18, Y + 0.35, z + math.sin(a) * d * 0.18, d * rnd.uniform(0.2, 0.35),
                 0.4, (50, 116, 100), "SmoothPlastic", collide=False, shadow=False)
        for q in range(14):
            a = q * math.pi / 7
            ball("MouldFuzz", x + math.cos(a) * d / 2, Y + 0.6, z + math.sin(a) * d / 2, rnd.uniform(3, 5), WHITE,
                 "SmoothPlastic", collide=False, shadow=False)
    for _ in range(5):   # Proteus swarming: faint concentric waves spreading over the agar
        spot = free_spot(rnd, clear, hi, lo, 70, taken)
        if not spot:
            continue
        x, z = spot
        for k in range(5):   # each wave a little off-centre, like a real swarm front
            disc("SwarmWave", x + rnd.uniform(-6, 6), Y + 0.08 + k * 0.01, z + rnd.uniform(-6, 6), 150 - k * 26, 0.06,
                 (226, 196, 140) if k % 2 else (214, 176, 108), "SmoothPlastic", collide=False, shadow=False)
    for _ in range(4):   # quadrant streak plates: four zig-zag strokes, each thinner, ending in single colonies
        spot = free_spot(rnd, clear, hi, lo, 110, taken)
        if not spot:
            continue
        x0, z0 = spot
        col = rnd.choice([(244, 232, 196), (248, 246, 238), (236, 186, 70)])
        for stroke, (n, size) in enumerate(((60, 3.2), (36, 3.6), (18, 4.4), (7, 6.5))):
            a = stroke * math.pi / 2   # each stroke turns a quarter round the plate
            ox, oz = x0 + math.cos(a) * 55, z0 + math.sin(a) * 55
            ux, uz = -math.sin(a), math.cos(a)
            for i in range(n):
                f = i / max(1, n - 1)
                zig = (1 if int(f * 6) % 2 == 0 else -1) * (f * 6 % 1 - 0.5) * 40
                px = ox + ux * (f - 0.5) * 90 + math.cos(a) * zig
                pz = oz + uz * (f - 0.5) * 90 + math.sin(a) * zig
                disc("StreakColony", px + rnd.uniform(-2, 2), Y + 0.18, pz + rnd.uniform(-2, 2), size * rnd.uniform(0.8, 1.3),
                     0.3, col, "SmoothPlastic", collide=False, shadow=False)
    for _ in range(22):   # loose clusters of small colonies over the open agar (a real plate is never bare)
        spot = free_spot(rnd, clear, hi, lo, 40, taken)
        if not spot:
            continue
        x, z = spot
        col = rnd.choice([(244, 232, 196), (248, 246, 238), (236, 186, 70), (232, 214, 150), (204, 64, 70)])
        for q in range(rnd.randint(5, 9)):
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 34)
            d = rnd.uniform(4, 11)
            disc("SmallColony", x + math.cos(a) * r, Y + 0.3, z + math.sin(a) * r, d, 0.5, col, "SmoothPlastic",
                 collide=False, shadow=False)
    for _ in range(9):   # a big colony with small satellite colonies round it
        spot = free_spot(rnd, clear, hi, lo, 36, taken)
        if not spot:
            continue
        x, z = spot
        col = rnd.choice([(244, 232, 196), (236, 186, 70), (204, 64, 70), (248, 246, 238)])
        dome(x, z, rnd.uniform(22, 32), col)
        for q in range(7):
            a = rnd.uniform(0, 2 * math.pi)
            r = rnd.uniform(18, 32)
            dome(x + math.cos(a) * r, z + math.sin(a) * r, rnd.uniform(4, 8), col)
    # skyline +z: a giant light microscope over the wall (classic silhouette: foot, C-arm, inclined tube, stage + slide)
    z, DARK = BACK + 40, (44, 48, 58)
    deco("ScopeFoot", (300, 40, 230), (cx, Y + 260, z + 40), DARK)
    for k in range(9):   # the C-shaped arm, curving from the foot up and over towards the valley
        a = math.radians(-60 + k * 17)
        deco("ScopeArm", (70, 70, 90), (cx, Y + 470 + math.sin(a) * 190, z + 130 - math.cos(a) * 70), DARK,
             rot=(math.degrees(a), 0, 0))
    deco("ScopeStage", (260, 24, 200), (cx, Y + 420, z - 20), DARK)
    deco("ScopeSlide", (200, 3, 60), (cx, Y + 434, z - 40), (220, 240, 250), "Glass", transp=0.2)
    disc("ScopeSpecimen", cx, Y + 436, z - 40, 40, 1, (230, 120, 170), "Neon", collide=False, shadow=False)
    disc("ScopeLight", cx, Y + 408, z - 20, 70, 2, (255, 252, 220), "Neon", collide=False, shadow=False)
    vcyl("ScopeTurret", cx, Y + 520, Y + 560, z - 20, 120, STEEL, "Metal", collide=False)
    for k, ox in enumerate((-34, 0, 34)):
        vcyl("ScopeObjective", cx + ox, Y + 460, Y + 520, z - 20, 26 - k * 3, (230, 232, 236), "Metal", collide=False)
    # the body tube leans back at 40 degrees from the turret to the eyepiece (Rz*Ry*Rx: (0, 50, 90))
    G.part("ScopeTube", (300, 80, 80), (cx, Y + 660, z + 80), WHITE, "SmoothPlastic", shape="Cylinder",
           rot=(0, -50, 90), collide=False)
    G.part("ScopeEyepiece", (90, 44, 44), (cx, Y + 790, z + 190), DARK, "SmoothPlastic", shape="Cylinder",
           rot=(0, -50, 90), collide=False)
    for s_ in (-1, 1):
        G.part("ScopeKnob", (40, 90, 90), (cx + s_ * 60, Y + 400, z + 150), STEEL, "Metal", shape="Cylinder",
               collide=False)
    # skyline -z: stacked petri dishes, an inoculating loop over a Bunsen flame
    z = -BACK
    for k in range(5):
        disc("DishStack", cx - 380, Y + 200 + k * 34, z, 360, 26, (220, 236, 245), "Glass", transp=0.45, collide=False)
        disc("DishAgar", cx - 380, Y + 192 + k * 34, z, 340, 8, (236, 206, 130), "SmoothPlastic", collide=False)
    vcyl("BurnerBody", cx + 320, Y + 180, Y + 380, z, 60, STEEL, "Metal", collide=False)
    G.part("BurnerFlame", (120, 70, 70), (cx + 320, Y + 440, z), (90, 150, 255), "Neon", shape="Ball", transp=0.25,
           collide=False, shadow=False, light=(2, 120, (120, 170, 255)))
    G.part("LoopRod", (520, 10, 10), (cx + 160, Y + 520, z + 40), STEEL, "Metal", shape="Cylinder", rot=(0, 0, 25),
           collide=False)
    for q in range(16):
        a = q * math.pi / 8
        ball("LoopRing", cx + 400 + math.cos(a) * 40, Y + 640 + math.sin(a) * 40, z + 40, 12, STEEL, "Metal",
             collide=False)



# ---- v63 micro, second pass (owner: "the worst stage: bad floor, few details, nothing in the tunnel")
def _bacillus(x, y, z, yaw, L, D, col):
    """a rod bacterium: capsule body, a darker nucleoid inside, wavy flagella at one end"""
    ry = math.radians(yaw)
    ux, uz = math.cos(ry), -math.sin(ry)
    G.part("Bacillus", (L, D, D), (x, y, z), col, "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0), collide=False)
    for e in (-1, 1):
        ball("BacillusCap", x + ux * e * L / 2, y, z + uz * e * L / 2, D, col, "SmoothPlastic", collide=False)
    G.part("Nucleoid", (L * 0.5, D * 0.42, D * 0.42), (x, y + D * 0.12, z), tuple(max(0, c - 50) for c in col),
           "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0), collide=False, shadow=False)
    for f in (-1, 0, 1):   # flagella: three short segments each, alternating angle (a wave)
        bx, bz = x - ux * (L / 2 + D * 0.4), z - uz * (L / 2 + D * 0.4)
        for k in range(3):
            seg = D * 0.9
            px, pz = bx - ux * seg * (k + 0.5), bz - uz * seg * (k + 0.5)
            box("Flagellum", (seg * 1.1, D * 0.08, D * 0.08), (px, y + f * D * 0.3 + (0.2 if k % 2 else -0.2) * D, pz),
                (240, 236, 220), "SmoothPlastic", rot=(0, yaw, 25 if k % 2 else -25), collide=False, shadow=False)


def _coccus_chain(x, y, z, yaw, n, d, col):
    """Streptococcus: round cells in a gently curving chain"""
    ry = math.radians(yaw)
    for k in range(n):
        a = ry + 0.12 * k
        x += math.cos(a) * d * 0.92
        z -= math.sin(a) * d * 0.92
        ball("Streptococcus", x, y + math.sin(k * 0.8) * d * 0.15, z, d, col, "SmoothPlastic", collide=False)


def _coccus_cluster(rnd, x, y, z, d, col):
    """Staphylococcus: a grape-like bunch"""
    for k in range(11):
        ball("Staphylococcus", x + rnd.uniform(-1, 1) * d, y + rnd.uniform(-0.6, 1) * d, z + rnd.uniform(-1, 1) * d, d,
             col, "SmoothPlastic", collide=False)


def _spirillum(x, y, z, yaw, L, d, col):
    """a spiral bacterium: beads along a helix"""
    ry = math.radians(yaw)
    ux, uz = math.cos(ry), -math.sin(ry)
    n = int(L / (d * 0.55))
    for k in range(n):
        t = k / n
        a = t * math.pi * 6
        ball("Spirillum", x + ux * (t - 0.5) * L - uz * math.cos(a) * d * 1.4, y + math.sin(a) * d * 1.4,
             z + uz * (t - 0.5) * L + ux * math.cos(a) * d * 1.4, d, col, "SmoothPlastic", collide=False, shadow=False)


def micro_life(rnd, clear, hi, lo, Y, taken):
    """big readable bacteria of every shape over the plate, a biofilm and a petri-dish rim"""
    PASTEL = [(150, 210, 140), (240, 170, 120), (170, 150, 230), (120, 200, 220), (240, 140, 170), (230, 210, 120)]
    for q in range(24):   # resting on the agar: rods in small groups, chains, clusters, spirals (2.5x scale)
        spot = free_spot(rnd, clear, hi, lo, 70, taken)
        if not spot:
            continue
        x, z = spot
        col = PASTEL[q % len(PASTEL)]
        kind = q % 4
        if kind == 0:
            for k in range(rnd.randint(2, 4)):
                D = rnd.uniform(16, 24)
                _bacillus(x + rnd.uniform(-40, 40), Y + D / 2, z + rnd.uniform(-40, 40), rnd.uniform(0, 180),
                          D * 3, D, col)
        elif kind == 1:
            _coccus_chain(x - 50, Y + 9, z, rnd.uniform(0, 360), rnd.randint(7, 11), 18, col)
        elif kind == 2:
            _coccus_cluster(rnd, x, Y + 16, z, 18, col)
        else:
            _spirillum(x, Y + 14, z, rnd.uniform(0, 180), 120, 9, col)
    for q in range(16):   # swimming overhead, so the rider sees them against the sky
        spot = free_spot(rnd, clear, hi, lo, 60, taken)
        if not spot:
            continue
        x, z = spot
        y = Y + rnd.uniform(70, 150)
        col = PASTEL[(q + 2) % len(PASTEL)]
        if q % 3 == 0:
            _spirillum(x, y, z, rnd.uniform(0, 180), 160, 11, col)
        elif q % 3 == 1:
            _coccus_chain(x - 70, y, z, rnd.uniform(0, 360), 9, 22, col)
        else:
            _bacillus(x, y, z, rnd.uniform(0, 180), 90, 28, col)
    for _ in range(4):   # biofilm: a glossy green mat with slime bubbles and embedded rods
        spot = free_spot(rnd, clear, hi, lo, 60, taken)
        if not spot:
            continue
        x, z = spot
        for k in range(7):
            disc("Biofilm", x + rnd.uniform(-30, 30), Y + 0.5 + k * 0.05, z + rnd.uniform(-30, 30), rnd.uniform(36, 60), 1,
                 (110, 150, 90), "SmoothPlastic", collide=False, shadow=False)
        for k in range(10):
            ball("SlimeBubble", x + rnd.uniform(-34, 34), Y + 1.5, z + rnd.uniform(-34, 34), rnd.uniform(2, 5),
                 (200, 240, 200), "Glass", transp=0.3, collide=False, shadow=False)
        for k in range(5):
            _bacillus(x + rnd.uniform(-24, 24), Y + 2.5, z + rnd.uniform(-24, 24), rnd.uniform(0, 180), 12, 4,
                      (90, 130, 80))
    # the petri dish rim: a thick glass band on top of both long walls, glinting
    for s in (-1, 1):
        x = lo + 20
        while x < hi - 20:
            L = min(400.0, hi - 20 - x)
            box("DishRimGlass", (L, 14, 26), (x + L / 2, Y + 236, s * (CELLZ + 4)), (210, 236, 246), "Glass",
                transp=0.25, collide=False, shadow=False)
            box("DishRimShine", (L, 1.2, 1.2), (x + L / 2, Y + 243.5, s * (CELLZ - 9)), (255, 255, 255), "Neon",
                collide=False, shadow=False)
            x += L


def micro_tunnel(mx, my, z0, z1):
    """the micro mesa bore as the inside of a cell membrane: lipid heads lining the walls and roof, channel proteins
    glowing at intervals. Everything stays outside the rider envelope (|dx| > 5, or above my + 9.5)."""
    HEAD, TAIL = (255, 190, 214), (250, 226, 160)
    z = z0 - 8
    k = 0
    while z < z1 + 8:
        for s in (-1, 1):
            ball("LipidHead", mx + s * 7.1, my + 2 + (k % 2) * 3, z, 1.8, HEAD, "SmoothPlastic", collide=False,
                 shadow=False)
            ball("LipidHead", mx + s * 7.1, my + 8 + (k % 2) * 2, z, 1.8, HEAD, "SmoothPlastic", collide=False,
                 shadow=False)
        ball("LipidHead", mx - 4 + (k % 5) * 2, my + 11.1, z, 1.8, HEAD, "SmoothPlastic", collide=False, shadow=False)
        if k % 8 == 0:   # a channel protein: a glowing barrel in the membrane with a gate on top
            for s in (-1, 1):
                vcyl("ChannelProtein", mx + s * 6.8, my - 1, my + 11, z, 2.4, (120, 210, 255), "Neon", transp=0.15,
                     collide=False, shadow=False)
                ball("ChannelGate", mx + s * 6.8, my + 11.6, z, 2.8, (90, 140, 230), "SmoothPlastic", collide=False,
                     shadow=False)
            G.part("ChannelLight", (1, 1, 1), (mx, my + 10.5, z), (0, 0, 0), "SmoothPlastic", transp=1, collide=False,
                   shadow=False, light=(1.4, 18, (150, 210, 255)))
        if k % 3 == 1:
            for s in (-1, 1):
                box("LipidTail", (0.4, 3, 0.4), (mx + s * 7.6, my + 5, z), TAIL, "SmoothPlastic", collide=False,
                    shadow=False)
        z += 2.6
        k += 1


# ====================================================================== biochemistry: a giant glassware lab
def _flask(x, y, z, r, liquid):
    for k in range(6):   # an Erlenmeyer cone from stacked rings
        rr = r * (1 - k * 0.14)
        vcyl("FlaskGlass", x, y + k * r * 0.3, y + (k + 1) * r * 0.3, z, 2 * rr, (190, 226, 242), "Glass", transp=0.3,
             collide=False)
        if k < 4:
            vcyl("FlaskLiquid", x, y + k * r * 0.3, y + (k + 1) * r * 0.3, z, 2 * rr - 6, liquid, "Neon", transp=0.1,
                 collide=False, shadow=False)
    vcyl("FlaskNeck", x, y + 1.8 * r, y + 2.6 * r, z, r * 0.36, (215, 236, 245), "Glass", transp=0.5, collide=False)


def _cylinder(x, y, z, d, h, liquid):
    vcyl("GradCylinder", x, y, y + h, z, d, (190, 226, 242), "Glass", transp=0.3, collide=False)
    vcyl("GradLiquid", x, y + 4, y + h * 0.8, z, d - 6, liquid, "Neon", transp=0.1, collide=False, shadow=False)
    for k in range(6):
        vcyl("GradMark", x, y + h * (0.15 + k * 0.12), y + h * (0.15 + k * 0.12) + 2, z, d + 1, WHITE, "SmoothPlastic",
             collide=False, shadow=False)
    vcyl("GradFoot", x, y - 10, y, z, d * 1.8, (200, 210, 220), "Glass", transp=0.3, collide=False)


def biochem(rnd, clear, hi, lo, Y, taken):
    cx = (hi + lo) / 2
    # ground: lab floor tiles (thin grout lines every 60 studs)
    x = lo + 30
    while x < hi:
        for z0, z1 in ((-CELLZ, 0), (0, CELLZ)):
            deco("TileLine", (0.8, 0.05, z1 - z0), (x, Y + 0.03, (z0 + z1) / 2), (176, 168, 206), shadow=False)
        x += 60
    z = -CELLZ + 30
    while z < CELLZ:
        deco("TileLine", (hi - lo, 0.05, 0.8), (cx, Y + 0.03, z), (176, 168, 206), shadow=False)
        z += 60
    # skyline: flasks and graduated cylinders behind both walls, each liquid a colour of the pH scale
    LIQ = [(255, 90, 90), (255, 170, 70), (250, 230, 90), (110, 220, 110), (80, 180, 240), (150, 110, 240)]
    for s in (-1, 1):
        for i, x in enumerate(along(hi, lo, 5)):
            if i % 2 == 0:
                _flask(x, Y + 330, s * BACK, 150, LIQ[(i + (s > 0) * 3) % 6])
            else:
                _cylinder(x, Y + 320, s * BACK, 100, 460, LIQ[(i + (s > 0) * 3) % 6])
    # midground: floating molecules (water, carbon dioxide, a glucose ring)
    for q in range(18):
        spot = free_spot(rnd, clear, hi, lo, 16, taken)
        if not spot:
            continue
        x, z = spot
        y = Y + rnd.uniform(70, 150)
        kind = q % 3
        if kind == 0:   # H2O: one red oxygen, two white hydrogens at 104.5 degrees
            ball("WaterO", x, y, z, 7, (230, 60, 60), "SmoothPlastic", collide=False)
            for s in (-1, 1):
                ball("WaterH", x + s * 4.4, y - 3.2, z, 4.4, WHITE, "SmoothPlastic", collide=False)
        elif kind == 1:   # CO2: a straight O=C=O
            ball("CO2C", x, y, z, 6, (50, 50, 56), "SmoothPlastic", collide=False)
            for s in (-1, 1):
                ball("CO2O", x + s * 6, y, z, 6, (230, 60, 60), "SmoothPlastic", collide=False)
        else:   # glucose ring: five carbons and one oxygen
            for k in range(6):
                a = k * math.pi / 3
                ball("GlucoseAtom", x + math.cos(a) * 7, y, z + math.sin(a) * 7, 4.4,
                     (230, 60, 60) if k == 0 else (60, 60, 66), "SmoothPlastic", collide=False)


# ====================================================================== animal biology: the Kuwaiti desert
def animal(rnd, clear, hi, lo, Y, taken):
    SAND = [(222, 190, 132), (210, 176, 118), (232, 202, 146)]
    # skyline: giant dunes rising over both walls, and an oryx herd and a camel caravan on the crests
    for s in (-1, 1):
        for i, x in enumerate(along(hi, lo, 6, 120)):
            ball("BigDune", x + rnd.uniform(-40, 40), Y + 160, s * (BACK + 60), rnd.uniform(380, 520), SAND[i % 3], "Sand",
                 collide=False)
    for k, x in enumerate(along(hi, lo, 4)):   # oryx: white body, black face mask, long straight horns (2x scale)
        y, z, S = Y + 290, CELLZ + 140, 2.0
        deco("OryxBody", (40 * S, 18 * S, 14 * S), (x, y + 24 * S, z), (236, 232, 222))
        for lx in (-14, 14):
            for lz in (-5, 5):
                deco("OryxLeg", (3 * S, 18 * S, 3 * S), (x + lx * S, y + 8 * S, z + lz * S), (236, 232, 222))
        deco("OryxHead", (12 * S, 10 * S, 9 * S), (x + 24 * S, y + 34 * S, z), (40, 36, 34))
        for lz in (-2.4, 2.4):
            deco("OryxHorn", (1.4 * S, 34 * S, 1.4 * S), (x + 22 * S, y + 52 * S, z + lz * S), (30, 28, 26),
                 rot=(0, 0, -25))
    for k, x in enumerate(along(hi, lo, 5)):   # camels in a line on the far crest
        y, z = Y + 300, -CELLZ - 120
        deco("CamelBody", (46, 20, 16), (x, y + 30, z), (196, 150, 96))
        ball("CamelHump", x, y + 44, z, 20, (186, 140, 88), "SmoothPlastic", collide=False)
        deco("CamelNeck", (8, 30, 8), (x + 24, y + 44, z), (196, 150, 96), rot=(0, 0, -30))
        deco("CamelHead", (16, 8, 8), (x + 34, y + 58, z), (196, 150, 96))
        for lx in (-16, 16):
            for lz in (-5, 5):
                deco("CamelLeg", (4, 22, 4), (x + lx, y + 10, z + lz), (186, 140, 88))
    # midground: acacia trees (flat crowns) and flocks of birds over the valley
    for _ in range(16):
        spot = free_spot(rnd, clear, hi, lo, 22, taken)
        if not spot:
            continue
        x, z = spot
        h = rnd.uniform(26, 38)
        deco("AcaciaTrunk", (2.6, h, 2.6), (x, Y + h / 2, z), (110, 84, 60), rot=(0, 0, rnd.uniform(-8, 8)))
        disc("AcaciaCrown", x, Y + h + 2, z, rnd.uniform(30, 40), 4, (110, 140, 70), "Grass", collide=False)
        disc("AcaciaCrownTop", x + 3, Y + h + 5, z, rnd.uniform(18, 24), 3, (126, 156, 80), "Grass", collide=False)
    for f in range(6):
        spot = free_spot(rnd, clear, hi, lo, 40, taken)
        if not spot:
            continue
        x, z = spot
        y = Y + rnd.uniform(170, 230)
        for b in range(7):   # a V formation
            row = (b + 1) // 2
            side = 1 if b % 2 else -1
            bx, bz = x - row * 9, z + side * row * 7
            for s in (-1, 1):
                deco("BirdWing", (3, 0.5, 7), (bx, y, bz + s * 3.6), (60, 52, 46), rot=(s * 18, 0, 0), shadow=False)


# ====================================================================== plant biology: a giant garden
def plant(rnd, clear, hi, lo, Y, taken):
    GREENS = [(72, 150, 60), (90, 170, 70), (60, 130, 55), (110, 180, 80)]
    # skyline: a wall of giant grass blades and flowers rising over both cliffs
    for s in (-1, 1):
        x = lo + 40
        while x < hi - 40:
            h = rnd.uniform(380, 620)
            lean = rnd.uniform(-12, 12)
            deco("GiantBlade", (14, h, 4), (x, Y + 120 + h / 2, s * (BACK - 40 + rnd.uniform(-30, 30))),
                 GREENS[int(x) % 4], "Grass", rot=(s * rnd.uniform(4, 10), rnd.uniform(-30, 30), lean))
            x += rnd.uniform(20, 34)
        for x in along(hi, lo, 3):
            h = rnd.uniform(520, 640)
            vcyl("GiantStem", x, Y + 120, Y + h, s * BACK, 18, (80, 150, 60), "SmoothPlastic", collide=False)
            G.part("GiantBloomDisc", (16, 110, 110), (x, Y + h + 40, s * (BACK - 30)), (110, 70, 30), "SmoothPlastic",
                   shape="Cylinder", rot=(0, 90, 0), collide=False)
            for q in range(16):   # petals round the disc, facing the valley
                a = q * math.pi / 8
                deco("GiantPetal", (60, 26, 6), (x + math.cos(a) * 80, Y + h + 40 + math.sin(a) * 80, s * (BACK - 34)),
                     (255, 210, 50) if s > 0 else (250, 250, 252), rot=(0, 0, math.degrees(a)))
    # ground: flower meadows (soft colour patches)
    for _ in range(18):
        spot = free_spot(rnd, clear, hi, lo, 50, taken)
        if spot:
            disc("Meadow", spot[0], Y + 0.04, spot[1], rnd.uniform(80, 140), 0.06,
                 rnd.choice([(196, 140, 220), (250, 226, 110), (248, 248, 250), (240, 150, 170)]), "SmoothPlastic",
                 collide=False, shadow=False)
    # midground: dandelion clocks and seeds drifting in the air
    for _ in range(12):
        spot = free_spot(rnd, clear, hi, lo, 14, taken)
        if not spot:
            continue
        x, z = spot
        h = rnd.uniform(24, 36)
        vcyl("DandelionStem", x, Y, Y + h, z, 1.2, (110, 170, 80), "SmoothPlastic", collide=False)
        ball("DandelionClock", x, Y + h + 5, z, 12, (250, 250, 250), "SmoothPlastic", transp=0.35, collide=False)
        for k in range(3):
            ball("DandelionSeed", x + rnd.uniform(-30, 30), Y + h + rnd.uniform(20, 80), z + rnd.uniform(-30, 30), 3,
                 WHITE, "SmoothPlastic", transp=0.2, collide=False, shadow=False)


# ====================================================================== molecular biology: the genome city
def _chromosome(x, y, z, h, col, band):
    for s in (-1, 1):   # two sister chromatids crossing at the centromere
        G.part("Chromatid", (h, 46, 46), (x, y + h / 2, z), col, "SmoothPlastic", shape="Cylinder",
               rot=(0, 0, 90 + s * 22), collide=False)
        for e in (-1, 1):
            a = math.radians(90 + s * 22)
            ball("ChromatidEnd", x + e * math.cos(a) * h / 2, y + h / 2 + e * math.sin(a) * h / 2, z, 46, col,
                 "SmoothPlastic", collide=False)
    for k in range(5):
        deco("ChromosomeBand", (60, 6, 60), (x, y + h * (0.12 + k * 0.19), z), band, "Neon", shadow=False)
    ball("Centromere", x, y + h / 2, z, 40, band, "Neon", collide=False, shadow=False)


def molecular(rnd, clear, hi, lo, Y, taken):
    # skyline: giant chromosomes and DNA towers over both walls
    for s in (-1, 1):
        for i, x in enumerate(along(hi, lo, 4)):
            if i % 2 == 0:
                _chromosome(x, Y + 260, s * BACK, 440, (190, 70, 170) if s > 0 else (70, 150, 220), (255, 230, 120))
            else:
                for q in range(34):
                    a, y = q * 0.45, Y + 180 + q * 13
                    for e, col in ((1, (90, 170, 255)), (-1, (255, 120, 200))):
                        ball("TowerHelix", x + e * math.cos(a) * 30, y, s * BACK + e * math.sin(a) * 30, 14, col, "Neon",
                             collide=False, shadow=False)
    # ground: glowing gel lanes running along the valley, with DNA bands across them
    for k in range(8):
        z = -840 + k * 240
        deco("GelLane", (hi - lo - 120, 0.06, 26), ((hi + lo) / 2, Y + 0.05, z), (40, 60, 120), shadow=False)
        x = lo + 100
        while x < hi - 100:
            deco("GelBand", (6, 0.08, 22), (x, Y + 0.08, z), (140, 200, 255) if k % 2 else (255, 140, 220), "Neon",
                 shadow=False)
            x += rnd.uniform(40, 140)


# ====================================================================== forensic science: the city at night
def forensic(rnd, clear, hi, lo, Y, taken):
    # skyline: a night city behind both walls (lit window bands, red rooftop beacons)
    for s in (-1, 1):
        x = lo + 60
        while x < hi - 60:
            w, h, d = rnd.uniform(60, 130), rnd.uniform(300, 620), rnd.uniform(60, 110)
            z = s * (BACK + rnd.uniform(-40, 60))
            deco("Tower", (w, h, d), (x, Y + 140 + h / 2, z), rnd.choice([(40, 44, 58), (52, 56, 72), (34, 38, 50)]))
            for k in range(int((h - 140) // 34)):
                deco("WindowBand", (w - 8, 3, d + 0.4), (x, Y + 300 + k * 34, z),
                     rnd.choice([(255, 220, 140), (180, 210, 255), (255, 240, 200)]), "Neon",
                     transp=rnd.uniform(0.1, 0.6), shadow=False)
            ball("Beacon", x, Y + 140 + h + 3, z, 6, (255, 60, 60), "Neon", collide=False, shadow=False)
            x += w + rnd.uniform(10, 40)
    # ground: a street grid with sidewalks and centre lines
    cx = (hi + lo) / 2
    for z in (-560, 0, 560):
        deco("Street", (hi - lo - 80, 0.05, 34), (cx, Y + 0.04, z), (44, 46, 54), "Asphalt", shadow=False)
        deco("StreetLine", (hi - lo - 80, 0.07, 1), (cx, Y + 0.08, z), (240, 200, 60), shadow=False)
        for e in (-1, 1):
            deco("Sidewalk", (hi - lo - 80, 0.3, 6), (cx, Y + 0.15, z + e * 20), (120, 122, 132), "Concrete", shadow=False)
    for x in along(hi, lo, 4, 220):
        for z0, z1 in ((-CELLZ + 40, 0), (0, CELLZ - 40)):
            deco("Street", (34, 0.05, z1 - z0), (x, Y + 0.035, (z0 + z1) / 2), (44, 46, 54), "Asphalt", shadow=False)
    # midground: street lamps along the streets (a few real lights, glow everywhere)
    lit = 0
    for z in (-560, 0, 560):
        x = lo + 100
        while x < hi - 100:
            for e in (-1, 1):
                lz = z + e * 22
                if clear.ok(x, lz, 4):
                    vcyl("LampPost", x, Y, Y + 20, lz, 1, (60, 62, 70), "Metal", collide=False)
                    G.part("LampHead", (4, 1.6, 4), (x, Y + 20.6, lz), (255, 236, 180), "Neon", collide=False,
                           shadow=False, light=(1.2, 30, (255, 230, 170)) if lit % 4 == 0 else None)
                    lit += 1
            x += 90


# ====================================================================== agriculture: centre-pivot farms
def agri(rnd, clear, hi, lo, Y, taken):
    CROPS = [((96, 176, 64), (120, 196, 80)), ((228, 196, 96), (242, 214, 120)), ((70, 150, 60), (230, 200, 100))]
    # ground: centre-pivot crop circles (the round fields you see from a plane over desert farms)
    for _ in range(14):
        r = rnd.uniform(110, 160)
        spot = free_spot(rnd, clear, hi, lo, r * 0.6, taken)   # flat fields may run under the track
        if not spot:
            continue
        x, z = spot
        a, b = rnd.choice(CROPS)
        disc("CropCircle", x, Y + 0.03, z, 2 * r, 0.06, a, "Grass", collide=False, shadow=False)
        for k in range(1, 4):
            disc("CropRow", x, Y + 0.03 + k * 0.01, z, 2 * r * (1 - k * 0.22), 0.06, b if k % 2 else a, "Grass",
                 collide=False, shadow=False)
        if clear.ok(x, z, r + 10):   # the pivot arm only where it cannot reach the rails
            ang = rnd.uniform(0, 180)
            deco("PivotArm", (r, 2, 2), (x + math.cos(math.radians(ang)) * r / 2, Y + 8,
                 z - math.sin(math.radians(ang)) * r / 2), STEEL, "Metal", rot=(0, ang, 0))
            vcyl("PivotCentre", x, Y, Y + 10, z, 4, STEEL, "Metal", collide=False)
            for k in range(1, 4):
                px, pz = x + math.cos(math.radians(ang)) * r * k / 4, z - math.sin(math.radians(ang)) * r * k / 4
                deco("PivotTower", (2, 8, 6), (px, Y + 4, pz), STEEL, "Metal", rot=(0, ang, 0))
    # skyline: a palm line on the crests, grain silos and a water tower behind the walls
    for s in (-1, 1):
        x = lo + 50
        while x < hi - 50:
            h = rnd.uniform(70, 110)
            base = Y + 250
            z = s * (CELLZ + 90 + rnd.uniform(-20, 20))
            vcyl("CrestPalmTrunk", x, base, base + h, z, 5, (150, 118, 82), "Wood", collide=False)
            for a in range(8):
                yaw = a * 45 + rnd.uniform(-10, 10)
                deco("CrestPalmFrond", (8, 1, 36), (x + math.sin(math.radians(yaw)) * 15, base + h - 4,
                     z + math.cos(math.radians(yaw)) * 15), (78, 148, 72), "Grass", rot=(26, yaw, 0))
            x += rnd.uniform(46, 70)
        for i, x in enumerate(along(hi, lo, 3)):
            if i == 1:
                vcyl("WaterTowerLeg", x, Y + 160, Y + 470, s * BACK, 20, STEEL, "Metal", collide=False)
                ball("WaterTowerTank", x, Y + 500, s * BACK, 110, (90, 160, 220), "SmoothPlastic", collide=False)
            else:
                for k in range(2):
                    vcyl("Silo", x + k * 90, Y + 160, Y + 470, s * BACK, 80, (226, 228, 230), "Metal", collide=False)
                    ball("SiloDome", x + k * 90, Y + 470, s * BACK, 80, (196, 70, 60), "SmoothPlastic", collide=False)
    # midground: hay bales
    for _ in range(26):
        spot = free_spot(rnd, clear, hi, lo, 6, taken)
        if spot:
            G.part("HayBale", (6, 8, 8), (spot[0], Y + 4, spot[1]), (222, 196, 110), "Grass", shape="Cylinder",
                   rot=(0, rnd.uniform(0, 180), 0), collide=False)


# ====================================================================== biotechnology: the future bio-city
def biotech(rnd, clear, hi, lo, Y, taken):
    # skyline: white towers with roof gardens, wind turbines and a twisting DNA tower
    for s in (-1, 1):
        for i, x in enumerate(along(hi, lo, 6, 140)):
            z = s * (BACK + rnd.uniform(-30, 30))
            if i == 2 and s > 0:   # the landmark: a twisting DNA tower of stacked rotated slabs
                for k in range(40):
                    deco("DNATowerSlab", (80, 12, 26), (x, Y + 170 + k * 12, z), (60, 190, 200) if k % 4 == 0 else WHITE,
                         rot=(0, k * 12, 0))
                    for e in (-1, 1):
                        a = math.radians(k * 12)
                        ball("DNATowerBead", x + e * math.cos(a) * 44, Y + 170 + k * 12, z - e * math.sin(a) * 44, 16,
                             (90, 220, 200) if e > 0 else (120, 160, 255), "Neon", collide=False, shadow=False)
                continue
            if i % 2 == 0:
                h = rnd.uniform(480, 660)
                vcyl("BioTower", x, Y + 150, Y + h, z, rnd.uniform(70, 100), (236, 240, 244), "SmoothPlastic",
                     collide=False)
                for k in range(int((h - 200) // 40)):
                    vcyl("BioTowerGlass", x, Y + 200 + k * 40, Y + 218 + k * 40, z, 104, (40, 170, 190), "Glass",
                         transp=0.1, collide=False)
                disc("RoofGarden", x, Y + h + 2, z, 90, 4, (90, 170, 80), "Grass", collide=False)
                for q in range(5):
                    ball("RoofTree", x + rnd.uniform(-28, 28), Y + h + 10, z + rnd.uniform(-28, 28), 16,
                         (80, 160, 70), "Grass", collide=False)
            else:   # a wind turbine
                vcyl("TurbineMast", x, Y + 150, Y + 520, z, 12, WHITE, "SmoothPlastic", collide=False)
                ball("TurbineHub", x, Y + 524, z - s * 10, 16, WHITE, "SmoothPlastic", collide=False)
                spin = rnd.uniform(0, 120)
                for b in range(3):
                    deco("TurbineBlade", (8, 150, 2), (x + math.sin(math.radians(spin + b * 120)) * 75,
                         Y + 524 + math.cos(math.radians(spin + b * 120)) * 75, z - s * 14), WHITE,
                         rot=(0, 0, -(spin + b * 120)))
    # ground: clean white paths and lawns
    cx = (hi + lo) / 2
    for z in (-420, 420):
        deco("CampusPath", (hi - lo - 120, 0.06, 18), (cx, Y + 0.04, z), (236, 240, 244), "SmoothPlastic", shadow=False)
    for _ in range(18):
        spot = free_spot(rnd, clear, hi, lo, 50, taken)
        if spot:
            disc("Lawn", spot[0], Y + 0.03, spot[1], rnd.uniform(90, 140), 0.06, (110, 180, 90), "Grass", collide=False,
                 shadow=False)
    # midground: algae photobioreactors (stacked glowing green tubes in a frame)
    for _ in range(7):
        spot = free_spot(rnd, clear, hi, lo, 26, taken)
        if not spot:
            continue
        x, z = spot
        yaw = rnd.uniform(0, 180)
        for k in range(5):
            G.part("AlgaeTube", (40, 2.6, 2.6), (x, Y + 4 + k * 4, z), (90, 230, 120), "Neon", shape="Cylinder",
                   rot=(0, yaw, 0), transp=0.25, collide=False, shadow=False)
        for e in (-1, 1):
            deco("AlgaeFrame", (1.4, 24, 1.4), (x + math.cos(math.radians(yaw)) * e * 20, Y + 12,
                 z - math.sin(math.radians(yaw)) * e * 20), STEEL, "Metal")


BIOMES = {"micro": micro, "biochem": biochem, "animal": animal, "plant": plant, "molecular": molecular,
          "forensic": forensic, "agri": agri, "biotech": biotech}


def build(key, k, clear, hi, lo, Y, taken):
    BIOMES[key](random.Random(6300 + k), clear, hi, lo, Y, taken)
    if key == "micro":
        micro_life(random.Random(6400), clear, hi, lo, Y, taken)
