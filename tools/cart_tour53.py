"""v53 Specialties Grand Tour: the Specialties Cart Ride as eight large OPEN worlds instead of one hall of glass rooms.

Layout (local coordinates, the world offset is cartride.CART_OFFSET):
  station (x ~ 0) -> tunnel -> stage 1 -> tunnel -> stage 2 ... -> stage 8 -> finish deck
Stages follow each other along -X. Every stage is a walled valley (CELLZ each side of the line z = 0) separated from the
next one by a rock ridge; the track crosses each ridge through a dark tunnel and comes out at the "reveal".
Inside a stage the track runs: a climb to a viewpoint -> an elevated hairpin over the whole valley -> a long leg back
across it (a low run through the hero set piece; molecular climbs the DNA helix instead) -> a hairpin -> back to z = 0.

Kept from cartride.py: the turtle, the locomotive/car models, stations(), the small props and the landmark builders.
New: the track is written to Shared/CartTrack.luau (no invisible waypoint parts), stage edges to Shared/CartRooms.luau.
Flags on track points:  s<k> stage k starts (caption)  t in a tunnel  e<n> ride event n (client: CartRide.client)
No speed limits, derailing or falling: the client moves the train kinematically and only eases speed in bends.
"""
import math
import random

import genmap as G
import genmap5 as C5
import cartride as CR

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign


def rect(name, x0, x1, y0, y1, z0, z1, *a, **k):
    """C5.rect with each pair sorted: the mirrored (-z) side passes its bounds high-to-low, which made negative sizes"""
    C5.rect(name, min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1), *a, **k)
rng = random.Random(53)

GROUND_Y = -14.0        # stage valley floor (the track runs at y -4 .. +44)
STATION_GROUND = -2.4   # the station cell floor = the station deck top
CELLZ = 780.0           # half width of every valley (v54: grand valleys)
LEGZ = 560.0            # how far each leg runs out from the centre line (hairpin centres)
TUNNEL_L = 160.0
RIDGE_T = 44.0
CR.STEP = 8.0           # longer track, fewer points: the client interpolates between them

# viewpoint climb and low-run height per stage
PATH = {
    "micro": (34, -4), "biochem": (28, -2), "animal": (30, -4), "plant": (24, -4),
    "molecular": (30, 0), "forensic": (20, -4), "agri": (26, -2), "biotech": (32, -2),
}
GROUND = {
    "micro": ((236, 214, 140), "SmoothPlastic"), "biochem": ((222, 216, 238), "Marble"),
    "animal": ((214, 188, 132), "Sand"), "plant": ((96, 156, 78), "Grass"),
    "molecular": ((24, 30, 60), "SmoothPlastic"), "forensic": ((70, 72, 84), "Slate"),
    "agri": ((140, 104, 66), "Ground"), "biotech": ((226, 236, 240), "SmoothPlastic"),
}
EVENT = {"micro": 1, "plant": 2, "forensic": 3}
ROCK = (198, 168, 128)   # Kuwait desert sandstone
BONE = (236, 230, 214)


# ====================================================================== track
def tunnel(t):
    i0 = len(t.pts)
    t.straight(TUNNEL_L / 2, flags=["t"])
    xm = t.p[0]
    t.straight(TUNNEL_L / 2, flags=["t"])
    t.tunnels.append((i0, len(t.pts), xm))
    return xm


def west(t):
    """turn sign whose centre lies on the -X side (spirals and S-bends never swing back toward the ridge behind)"""
    return -1 if math.cos(math.radians(t.yaw)) > 0 else 1


def s_bend(t, w, ang=24.0, R=200.0):
    t.turn(ang * w, R)
    t.turn(-2 * ang * w, R)
    t.turn(ang * w, R)


def stage_path(t, key, s):
    """v54 grand valley: four long legs across the valley (|z| up to LEGZ) joined by three hairpins.
    A: spiral climb + rise to the overlook | B: high bridge over the river, S-bend, the big drop, low run
    C: the hero set piece (straight ':low'), a tunnel through a mesa, S-bend, climb | D: double spiral down, exit.
    The last straight is computed so the path closes exactly on z = 0 at the exit tunnel."""
    h_top, low = PATH[key]
    h_top += 56   # the overlook bridge is high above the valley floor
    mid = 40.0
    R1, RH = 120.0, 140.0
    t.straight(40)
    t.turn(90 * s, R1)
    # ---- leg A: spiral climb, then up to the overlook
    t.straight(40)
    t.turn(360 * west(t), 50, dy=45)
    t.marks[key + ":spiralA"] = t.last_center
    t.straight(LEGZ - abs(t.p[2]), dy=h_top - 45)
    t.marks[key + ":view"] = tuple(t.p)
    t.turn(-180 * s, RH, flags=["e%d" % EVENT[key]] if key in ("micro",) else ())
    t.marks[key + ":overlook"] = t.last_center
    i_leg = len(t.pts)
    # ---- leg B: the high bridge over the river, an S-bend, the big drop, a low run
    i0 = len(t.pts)
    t.straight(360, dy=5)
    t.marks[key + ":bridge"] = (i0, len(t.pts))
    s_bend(t, west(t))
    t.straight(300, dy=low - (t.p[1]))
    t.straight(max(40.0, LEGZ - abs(t.p[2])))
    t.turn(180 * s, RH)
    # ---- leg C: hero set piece, mesa tunnel, S-bend, climb
    t.straight(120)
    i0 = len(t.pts)
    t.straight(280, flags=["e%d" % EVENT[key]] if key in ("plant", "forensic") else ())
    t.marks[key + ":low"] = (i0, len(t.pts))
    i0 = len(t.pts)
    t.straight(160, flags=["m"])
    t.marks[key + ":mesa"] = (i0, len(t.pts))
    s_bend(t, west(t))
    t.straight(max(40.0, LEGZ - abs(t.p[2])), dy=mid - t.p[1])
    t.marks[key + ":leg"] = (i_leg, len(t.pts))
    t.turn(-180 * s, RH)
    # ---- leg D: a double spiral down around the stage's tower, then home to z = 0
    t.straight(60)
    t.turn(720 * west(t), 46, dy=-(t.p[1]))
    t.marks["dna" if key == "molecular" else key + ":tower"] = t.last_center
    t.straight(max(10.0, abs(t.p[2]) - R1))
    t.turn(90 * s, R1)
    t.straight(40)


def build_track():
    t = CR.Turtle()
    t.yaw = -90.0                    # the ride heads along -X
    t.marks = {}
    t.tunnels = []
    t.emit(["s0"], "المحطة")
    t.straight(48)
    side = 1
    t.ridges = []
    for k, key in enumerate(CR.SECTION_KEYS, start=1):
        t.ridges.append(tunnel(t))
        t.section(CR.SECTIONS[k][0] + " " + CR.SECTIONS[k][1])
        stage_path(t, key, side)
        side = -side
    t.straight(60, dy=6)
    t.emit(["end"], "🎉 خلصت الرحلة! نادي العلوم البيولوجية يشكرك")
    return t


# ====================================================================== rails
def _frame(a, b):
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    yaw = math.degrees(math.atan2(dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    ry = math.radians(yaw)
    return L, yaw, pitch, (math.cos(ry), -math.sin(ry))


def draw_track(t):
    """rails, spine, ties and guide lights. Straight runs are merged into long parts (part budget)."""
    pts = t.pts
    starts = [i for i, _ in t.sections]

    def stage_of(i):
        k = 0
        for q, st in enumerate(starts):
            if i >= st:
                k = q
        return k

    # v54: a run is merged while its total bend stays under 6 degrees (and slope under 3), so gentle curves use
    # 2-3 segments per part while tight spirals keep one segment each (part budget for the 48k-stud track)
    runs, i = [], 0
    while i < len(pts) - 1:
        j = i + 1
        _, y0, p0, _ = _frame(pts[i], pts[i + 1])
        while j < len(pts) - 1 and j - i < 8:
            _, y1, p1, _ = _frame(pts[j], pts[j + 1])
            dyaw = abs((y1 - y0 + 180) % 360 - 180)
            if dyaw > 6 or abs(p1 - p0) > 3 or ("t" in pts[j][4]) != ("t" in pts[i][4]):
                break
            j += 1
        runs.append((i, j))
        i = j
    with G.Group("CartTrack"):
        for n, (i, j) in enumerate(runs):
            a, b = pts[i], pts[j]
            L, yaw, pitch, (rx, rz) = _frame(a, b)
            mx, my, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
            glow = CR.SPEC_TRACK_COL[min(stage_of(i), 7)]
            for s_ in (-1, 1):
                box("Rail", (0.6, 0.6, L + 0.4), (mx + rx * s_ * 2.5, my - 0.3, mz + rz * s_ * 2.5), (215, 220, 228), "Metal",
                    rot=(pitch, yaw, 0), collide=False, shadow=False)
            box("TrackSpine", (1.8, 1.4, L + 0.4), (mx, my - 1.6, mz), (52, 58, 70), "Metal", rot=(pitch, yaw, 0),
                collide=False, shadow=False)
            # v54: high straight runs become bridges: a deck under the rails and railings on both sides
            ground = STATION_GROUND if a[0] > t.ridges[0] else GROUND_Y
            if j - i >= 3 and min(a[1], b[1]) - ground > 40 and "t" not in a[4]:
                box("BridgeDeck", (8.4, 0.7, L + 0.4), (mx, my - 2.6, mz), (120, 112, 104), "Concrete", rot=(pitch, yaw, 0),
                    collide=False, shadow=True)
                for s_ in (-1, 1):
                    box("BridgeRail", (0.35, 0.35, L + 0.4), (mx + rx * s_ * 4.1, my + 0.9, mz + rz * s_ * 4.1),
                        (230, 232, 236), "Metal", rot=(pitch, yaw, 0), collide=False, shadow=False)
            if n % 3 == 0:
                for s_ in (-1, 1):
                    box("GuideNeon", (0.22, 0.28, L + 0.2), (mx + rx * s_ * 3.35, my - 0.55, mz + rz * s_ * 3.35), glow,
                        "Neon", rot=(pitch, yaw, 0), collide=False, shadow=False)
        for i in range(0, len(pts) - 1, 3):   # v54: a tie every 24 studs (part budget for the 48k-stud track)
            a, b = pts[i], pts[i + 1]
            L, yaw, pitch, _ = _frame(a, b)
            box("Tie", (6.8, 0.45, 1.1), (a[0], a[1] - 0.85, a[2]), (85, 92, 108), "Metal", rot=(pitch, yaw, 0),
                collide=False, shadow=False)
            # supports down to the valley floor wherever the track is up in the air (never inside tunnels)
            if i % 9 == 0 and "t" not in a[4] and "m" not in a[4]:
                floor = STATION_GROUND if a[0] > t.ridges[0] else GROUND_Y
                if a[1] - floor > 7:
                    vcyl("Support", a[0], floor, a[1] - 1.8, a[2], 1.6 + (a[1] - floor) * 0.03, (70, 76, 88), "Metal",
                         collide=False, shadow=False)
        # a gate over the rails right after every tunnel: the stage's name, readable both ways
        for k, (st, title) in enumerate(t.sections):
            sx, sy, sz, syaw = pts[min(st + 3, len(pts) - 1)][:4]
            rx, rz = math.cos(math.radians(syaw)), -math.sin(math.radians(syaw))
            col = CR.SPEC_TRACK_COL[min(k, 7)]
            for s_ in (-1, 1):
                vcyl("SpecGateColumn", sx + rx * s_ * 8.5, GROUND_Y, sy + 16.5, sz + rz * s_ * 8.5, 2.0, (44, 50, 64), "Metal",
                     collide=False)
                ball("SpecGateOrb", sx + rx * s_ * 8.5, sy + 17.5, sz + rz * s_ * 8.5, 2.8, col, "Neon", collide=False,
                     shadow=False)
            for back in (0, 180):
                G.part("SpecGateBanner", (19.0, 3.8, 0.8), (sx, sy + 15.2, sz), (24, 30, 44), "SmoothPlastic",
                       rot=(0, syaw + back, 0), collide=False,
                       text=dict(face="Front", text="%d) %s" % (k + 1, title), color=(255, 255, 255), bg=(24, 30, 44),
                                 bg_t=0.0))


# ====================================================================== valleys, ridges, tunnels
def cell_ranges(t):
    """x range (hi, lo) of the station cell and every stage cell"""
    xs = [p[0] for p in t.pts]
    east, west = 110.0, min(xs) - 150.0
    edges = [east] + t.ridges + [west]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def ridge(xm, next_col):
    """a rock ridge across the valley at x = xm with the tunnel through it"""
    z = -CELLZ - 20
    while z < CELLZ + 20:
        w = rng.uniform(36, 60)
        z1 = min(z + w, CELLZ + 20)
        top = GROUND_Y + rng.uniform(210, 270)   # v54: taller than the highest bridge
        x0, x1 = xm - RIDGE_T / 2 - rng.uniform(0, 8), xm + RIDGE_T / 2 + rng.uniform(0, 8)
        if z1 < -14 or z > 14:
            rect("Ridge", x0, x1, GROUND_Y - 4, top, z, z1, ROCK, "Sandstone")
        else:
            for za, zb in ((z, -14), (14, z1)):
                if zb - za > 0.5:
                    rect("Ridge", x0, x1, GROUND_Y - 4, top, za, zb, ROCK, "Sandstone")
            rect("Ridge", x0, x1, 22, top, -14, 14, ROCK, "Sandstone")
        z = z1
    # a stepped crest so the skyline is not one flat line
    for q in range(10):
        zz = rng.uniform(-CELLZ, CELLZ)
        if abs(zz) > 40:
            box("RidgeCrag", (RIDGE_T * 0.7, rng.uniform(20, 50), rng.uniform(30, 60)), (xm, GROUND_Y + 265, zz),
                (184, 152, 114), "Sandstone", rot=(0, rng.uniform(-20, 20), rng.uniform(-8, 8)), collide=False)


def draw_tunnels(t, stage_cols):
    for n, (i0, i1, xm) in enumerate(t.tunnels):
        xa, xb = t.pts[i0][0], t.pts[i1 - 1][0]
        hi, lo = max(xa, xb) + 4, min(xa, xb) - 4
        col = stage_cols[n]
        rect("TunnelFloor", lo, hi, GROUND_Y - 4, -3, -14, 14, (60, 54, 50), "Rock")
        for s_ in (-1, 1):
            rect("TunnelWall", lo, hi, -3, 22, s_ * 12, s_ * 14, (66, 58, 52), "Rock")
        rect("TunnelRoof", lo, hi, 20, 22, -14, 14, (66, 58, 52), "Rock")
        x = hi - 10
        q = 0
        while x > lo + 6:
            rect("TunnelRing", x - 0.6, x + 0.6, 19.4, 20, -11, 11, col, "Neon", collide=False, shadow=False)
            for s_ in (-1, 1):
                rect("TunnelRing", x - 0.6, x + 0.6, 2, 19.4, s_ * 11.4, s_ * 12, col, "Neon", collide=False, shadow=False)
            x -= 22
            q += 1
        # the mouth facing the rider: a frame in the next stage's colour and its name
        rect("TunnelMouth", hi - 1, hi + 1, 20, 26, -16, 16, (44, 50, 64), "Metal")
        for s_ in (-1, 1):
            rect("TunnelMouth", hi - 1, hi + 1, -3, 26, s_ * 14, s_ * 16, (44, 50, 64), "Metal")
        G.part("TunnelSign", (0.6, 4.4, 26), (hi + 1.4, 23, 0), (24, 30, 44), "SmoothPlastic", collide=False,
               text=dict(face="Right", text="➜ %d) %s" % (n + 1, CR.SECTIONS[n + 1][0]), color=col, bg=(24, 30, 44),
                         bg_t=0.0))
        box("TunnelLamp", (2, 0.4, 2), (xm, 19.6, 0), col, "Neon", collide=False, shadow=False, light=(1.2, 30, col))


def valleys(t):
    cells = cell_ranges(t)
    xs_all = [c[0] for c in cells] + [cells[-1][1]]
    east, west = xs_all[0], xs_all[-1]
    with G.Group("CartValleys"):
        # station cell floor + every stage floor
        hi, lo = cells[0]
        rect("StationGround", lo, hi, STATION_GROUND - 3, STATION_GROUND, -CELLZ, CELLZ, (214, 206, 190), "Concrete")
        for k, key in enumerate(CR.SECTION_KEYS, start=1):
            hi, lo = cells[k]
            col, mat = GROUND[key]
            rect("ValleyFloor", lo, hi, GROUND_Y - 4, GROUND_Y, -CELLZ, CELLZ, col, mat)
        # outer cliffs along both sides and both ends
        for s_ in (-1, 1):
            x = east
            while x > west:
                w = rng.uniform(90, 160)
                x1 = max(x - w, west)
                top = GROUND_Y + rng.uniform(230, 290)
                rect("Cliff", x1, x, GROUND_Y - 4, top, s_ * CELLZ, s_ * (CELLZ + 40), ROCK, "Sandstone")
                x = x1
        for xe in (east, west):
            rect("Cliff", xe - 20, xe + 20, GROUND_Y - 4, GROUND_Y + 280, -CELLZ - 40, CELLZ + 40, ROCK, "Sandstone")
        for xm in t.ridges:
            ridge(xm, None)
        draw_tunnels(t, CR.SPEC_TRACK_COL)
    return cells


# ====================================================================== stage set pieces
def leg_x(t, key):
    i0, i1 = t.marks[key + ":low"]
    return t.pts[i0][0], t.pts[i0][2], t.pts[i1 - 1][2], t.pts[i0][1]


CAPTIONS = []   # (x, z, text): v54 no floating boards; the ride shows these as short captions when passing


def label(text, x, y, z, tx, tz, w=26):
    CAPTIONS.append((x, z, text))


def landmark(clear, seg, frac, dist, r, fn, text):
    """CR.landmark without the floating label board: the set piece beside the rails + a ride caption"""
    p = seg[min(len(seg) - 1, int(len(seg) * frac))]
    x, y, z, yaw = p[:4]
    rx, rz = math.cos(math.radians(yaw)), -math.sin(math.radians(yaw))
    for d in (dist, dist + 8, dist + 16, dist - 6, dist + 24):
        for s_ in (1, -1):
            lx, lz = x + rx * s_ * d, z + rz * s_ * d
            if clear.ok(lx, lz, r):
                fn(lx, lz, y)
                CAPTIONS.append((lx, lz, text))
                CR.LANDMARKS.append((fn.__name__, text, lx, lz))
                return True
    CR.LANDMARKS.append((fn.__name__, "NOT PLACED", x, z))
    return False


def apply_captions(t):
    """attach each caption to the track point ~40 studs before the closest one (flag c + label)"""
    for (x, z, text) in CAPTIONS:
        best, bd = 0, 1e18
        for i, q in enumerate(t.pts):
            d = (q[0] - x) ** 2 + (q[2] - z) ** 2
            if d < bd:
                best, bd = i, d
        i = max(1, best - 5)
        while i > 1 and t.pts[i][5]:
            i -= 1
        q = t.pts[i]
        t.pts[i] = (q[0], q[1], q[2], q[3], list(q[4]) + ["c"], text)


CELL = [0.0, 0.0]   # x range (hi, lo) of the valley being decorated (set by scenery())
DENSITY = 1.6       # v54 valleys are ~2.5x larger (kept below that for the part budget)


def place(clear, cx, cz, R, r, tries=60):
    """a free spot for a set piece anywhere in the current valley (cx/cz/R are kept for the old call sites)"""
    hi, lo = CELL
    for _ in range(tries):
        x, z = rng.uniform(lo + r + 30, hi - r - 30), rng.uniform(-CELLZ + r + 30, CELLZ - r - 30)
        if clear.ok(x, z, r):
            return x, z
    return None


def sc(clear, cx, n, r, fn):
    """CR.scatter over the whole valley (a grid of discs), DENSITY times as many"""
    hi, lo = CELL
    discs = []
    x = lo + 200
    while x < hi - 100:
        for z in (-520, -170, 170, 520):
            discs.append((x, z, 250))
        x += 330
    CR.scatter(clear, discs, max(1, round(n * DENSITY)), r, fn)


def _rod(x, y, z, yaw, col, L=44, D=14):
    G.part("GiantBacillus", (L, D, D), (x, y, z), col, "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0), collide=False)
    ry = math.radians(yaw)
    for e in (-1, 1):
        ball("BacillusCap", x + e * L / 2 * math.cos(ry), y, z - e * L / 2 * math.sin(ry), D, col, "SmoothPlastic",
             collide=False)
    for q in range(3):
        G.part("Flagellum", (18, 0.6, 0.6), (x - (L / 2 + 9) * math.cos(ry), y - 2 + q * 2, z + (L / 2 + 9) * math.sin(ry)),
               (190, 255, 200), "Neon", rot=(0, yaw, (-1) ** q * 14), collide=False, shadow=False)


def stage_micro(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "micro")
    vx, vy, vz = t.marks["micro:view"]
    COLS = [(250, 240, 205), (240, 190, 90), (230, 140, 170), (246, 246, 240), (176, 214, 140)]
    # giant colonies = the hills of the agar plate; the ones near the viewpoint grow while you watch (event 1)
    n = 0
    for q in range(22):
        d = rng.uniform(26, 84)
        spot = place(clear, cx, 0, CELLZ - 40, d / 2 + 6)
        if not spot:
            continue
        x, z = spot
        col = COLS[q % len(COLS)]
        grow = math.hypot(x - vx, z - vz) < 330 and n < 8
        n += grow
        name = "CartEvt1_Colony" if grow else "Colony"
        ball(name, x, Y, z, d, col, "SmoothPlastic", collide=False)
        ball(name, x, Y + d * 0.32, z, d * 0.42, tuple(max(0, c - 30) for c in col), "SmoothPlastic", collide=False)
        disc(name, x, Y + 0.3, z, d * 1.18, 0.4, tuple(min(255, c + 10) for c in col), "SmoothPlastic", collide=False)
    # an antibiotic disc with its clear inhibition zone, beside the low run
    for s_ in (1, -1):
        ax, az = lx + s_ * 70, (za + zb) / 2
        if clear.ok(ax, az, 46):
            disc("InhibitionZone", ax, Y + 0.25, az, 90, 0.3, (248, 236, 190), "SmoothPlastic", collide=False)
            disc("AntibioticDisc", ax, Y + 0.6, az, 12, 1.0, (252, 252, 252), "SmoothPlastic", collide=False)
            for q in range(10):
                a = q * math.pi / 5
                ball("Colony", ax + 58 * math.cos(a), Y, az + 58 * math.sin(a), 16, COLS[q % 3], "SmoothPlastic",
                     collide=False)
            label("🧫 منطقة التثبيط: المضاد الحيوي يمنع البكتيريا تنمو حوله", lx + s_ * 13, ly + 12, az, ax, az, 30)
            break
    # giant rod bacteria drifting over the plate
    for q in range(8):
        spot = place(clear, cx, 0, CELLZ - 60, 30)
        if spot:
            _rod(spot[0], Y + rng.uniform(40, 90), spot[1], rng.uniform(0, 180), COLS[q % len(COLS)])
    # the microscope objective hanging over the valley, its light beam on the viewpoint hairpin
    vcyl("ObjectiveBody", vx, Y + 170, Y + 320, vz, 70, (40, 44, 52), "Metal", collide=False)
    for q, c in enumerate(((220, 60, 60), (240, 240, 240))):
        vcyl("ObjectiveBand", vx, Y + 190 + q * 30, Y + 196 + q * 30, vz, 71, c, "Metal", collide=False)
    vcyl("ObjectiveLens", vx, Y + 164, Y + 170, vz, 40, (200, 230, 255), "Glass", transp=0.3, collide=False)
    vcyl("LightBeam", vx, Y + 60, Y + 164, vz, 38, (230, 245, 255), "Neon", transp=0.9, collide=False, shadow=False)
    sc(clear, cx, 50, 6, lambda x, z: disc("ColonyDot", x, Y + 0.2, z, rng.uniform(4, 10), 0.5,
               rng.choice(COLS), "SmoothPlastic", collide=False))
    landmark(clear, t.pts[slice(*t.marks["micro:leg"])], 0.15, 46, 22, CR._lm_microscope,
                "🔬 مجهر ضوئي: يكبّر حتى 1000 مرة")
    landmark(clear, t.pts[slice(*t.marks["micro:leg"])], 0.85, 50, 34, CR._lm_petri,
                "🧫 طبق بتري: مستعمرات بكتيرية تنمو على الآجار")


def stage_biochem(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "biochem")
    zm = (za + zb) / 2
    # the rider is the substrate: the low run goes right through an enzyme's active site
    for s_ in (-1, 1):
        ball("EnzymeLobe", lx + s_ * 44, Y + 30, zm, 66, (150, 90, 210), "SmoothPlastic", collide=False)
        ball("EnzymeLobe", lx + s_ * 30, Y + 64, zm, 40, (170, 110, 225), "SmoothPlastic", collide=False)
    ball("EnzymeLobe", lx, Y + 82, zm, 44, (150, 90, 210), "SmoothPlastic", collide=False)
    disc("ActiveSiteGlow", lx, ly + 24, zm, 26, 1.0, (255, 200, 90), "Neon", collide=False, shadow=False)
    label("⚗️ إنت الحين المادة المتفاعلة داخل الموقع النشط للإنزيم!", lx + 13, ly + 10, zm - 60, lx, zm - 120, 30)
    # a giant ATP molecule (adenine rings, ribose, three phosphates) beside the track
    for s_ in (1, -1):
        ax, az = lx + s_ * 130, zm
        if clear.ok(ax, az, 70):
            break
    def atom(name, x, y, z, d, col):
        ball(name, x, y, z, d, col, "SmoothPlastic", collide=False)
    def bond(p, q):
        dx, dy, dz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        box("Bond", (2, 2, L), ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2), (220, 220, 228),
            "SmoothPlastic", rot=(-math.degrees(math.atan2(dy, math.hypot(dx, dz))), math.degrees(math.atan2(dx, dz)), 0),
            collide=False)
    yb = Y + 46
    chain = []
    for q in range(6):   # adenine 6-ring
        a = q * math.pi / 3
        chain.append((ax + 14 * math.cos(a), yb + 14 * math.sin(a), az - 50))
    for q in range(6):
        atom("Adenine", *chain[q], 9, (70, 120, 230) if q % 2 else (90, 92, 100))
        bond(chain[q], chain[(q + 1) % 6])
    rib = [(ax + 10 * math.cos(q * 1.256), yb + 10 * math.sin(q * 1.256), az - 8) for q in range(5)]
    for q in range(5):
        atom("Ribose", *rib[q], 9, (90, 92, 100) if q else (224, 70, 70))
        bond(rib[q], rib[(q + 1) % 5])
    bond(chain[0], rib[2])
    prev = rib[0]
    for q in range(3):
        p = (ax, yb, az + 22 + q * 22)
        atom("Phosphate", *p, 15, (255, 210, 60))
        bond(prev, p)
        prev = p
    G.part("BondGlow", (2.4, 2.4, 22), (ax, yb, az + 55), (255, 240, 120), "Neon", collide=False, shadow=False)
    label("🔋 ATP: عملة الطاقة بالخلية. كسر رابطة الفوسفات الأخيرة يطلق طاقة", lx - (ax - lx) * 0.1, ly + 12, az + 30,
          ax, az, 30)
    sc(clear, cx, 22, 18, lambda x, z: CR._molecule(x, Y + rng.uniform(25, 70), z))
    sc(clear, cx, 18, 8, lambda x, z: CR._tube(x, Y, z))
    landmark(clear, t.pts[slice(*t.marks["biochem:leg"])], 0.15, 46, 22, CR._lm_enzyme,
                "🧩 إنزيم: المادة المتفاعلة تدخل الموقع النشط")
    landmark(clear, t.pts[slice(*t.marks["biochem:leg"])], 0.85, 46, 30, CR._lm_krebs, "🔄 دورة كربس: طاقة من الغذاء")


def stage_animal(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "animal")
    z0, z1 = min(za, zb), max(za, zb)
    # the low run passes INSIDE a blue whale's ribcage
    z = z0 + 10
    while z < z1 - 10:
        for s_ in (-1, 1):
            box("WhaleRib", (3, 30, 3.4), (lx + s_ * 19, Y + 15, z), BONE, "SmoothPlastic", rot=(0, 0, s_ * 6), collide=False)
            box("WhaleRib", (3, 22, 3.4), (lx + s_ * 12, ly + 26, z), BONE, "SmoothPlastic", rot=(0, 0, s_ * 48),
                collide=False)
        z += 16
    rect("WhaleSpine", lx - 2.5, lx + 2.5, ly + 31, ly + 35, z0, z1, BONE, "SmoothPlastic", collide=False)
    head = z0 - 18 if za < zb else z1 + 18
    box("WhaleSkull", (34, 16, 40), (lx, Y + 10, head), BONE, "SmoothPlastic", collide=False)
    box("WhaleJaw", (30, 4, 46), (lx, Y + 2, head), BONE, "SmoothPlastic", collide=False)
    label("🐋 داخل قفص أضلاع حوت أزرق: أكبر حيوان عاش على الأرض", lx + 13, ly + 10, head + (12 if za < zb else -12),
          lx, head + (60 if za < zb else -60), 30)
    sc(clear, cx, 12, 16, lambda x, z: CR._camel(x, Y, z))
    sc(clear, cx, 4, 26, lambda x, z: CR._turtle(x, Y, z))
    sc(clear, cx, 14, 10, lambda x, z: CR._falcon(x, Y + rng.uniform(40, 90), z))
    sc(clear, cx, 24, 6, lambda x, z: CR._cactus(x, Y, z))
    sc(clear, cx, 10, 10, lambda x, z: CR._palm(x, Y, z))
    landmark(clear, t.pts[slice(*t.marks["animal:leg"])], 0.88, 44, 16, CR._lm_heart, "❤️ قلب الإنسان: 4 حجرات")
    landmark(clear, t.pts[slice(*t.marks["animal:leg"])], 0.12, 50, 30, CR._lm_whale,
                "🦴 هيكل الحوت يحمي أعضاءه، والقلب لحاله بحجم سيارة صغيرة")


def stage_plant(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "plant")
    z0, z1 = min(za, zb), max(za, zb)
    # a canopy of giant leaves over the low run (the pollen storm, event 2, blows here)
    z = z0 + 20
    q = 0
    while z < z1 - 10:
        s_ = 1 if q % 2 else -1
        box("GiantLeaf", (54, 1.6, 26), (lx + s_ * 14, ly + 34 + (q % 3) * 4, z), (80, 170, 70), "Grass",
            rot=(0, rng.uniform(-25, 25), s_ * 10), collide=False)
        box("LeafVein", (52, 0.4, 1.2), (lx + s_ * 14, ly + 35 + (q % 3) * 4, z), (170, 240, 140), "Neon",
            rot=(0, 0, s_ * 10), collide=False, shadow=False)
        z += 34
        q += 1
    # the stomata gate at the end of the run: two guard cells around the track
    gz = z1 + 14 if za < zb else z0 - 14
    for s_ in (-1, 1):
        for k in range(4):
            box("GuardCell", (12, 16, 12), (lx + s_ * (17 - k * 1.2 + (2 if k in (1, 2) else 0)), ly + 2 + k * 13, gz),
                (100, 190, 90), "Grass", rot=(0, 0, s_ * (k * 8 - 10)), collide=False)
            ball("Chloro", lx + s_ * (16 - k), ly + 4 + k * 13, gz + 6, 3, (40, 140, 50), "SmoothPlastic", collide=False)
    label("🌿 الثغور: بوابات بالورقة يدخل منها CO₂ ويطلع O₂ وبخار الماء", lx + 13, ly + 10, gz + (-14 if za < zb else 14),
          lx, gz, 30)
    # two giant sunflowers looking at the track
    for frac in (0.3, 0.7):
        spot = place(clear, cx, (-1 if frac < 0.5 else 1) * 120, 160, 28)
        if not spot:
            continue
        x, z = spot
        vcyl("SunflowerStem", x, Y, Y + 120, z, 5, (80, 140, 60), "Grass", collide=False)
        yaw = math.degrees(math.atan2(-(0 - z), lx - x))
        G.part("SunflowerHead", (5, 46, 46), (x, Y + 122, z), (110, 70, 30), "SmoothPlastic", shape="Cylinder",
               rot=(0, yaw, 0), collide=False)
        ax_, az_ = math.cos(math.radians(yaw)), -math.sin(math.radians(yaw))
        ux, uz = -az_, ax_
        for p in range(14):
            a = p * 2 * math.pi / 14
            ball("SunPetal", x + ux * math.cos(a) * 29 + ax_ * 0.5, Y + 122 + math.sin(a) * 29, z + uz * math.cos(a) * 29 + az_ * 0.5,
                 12, (250, 200, 50), "SmoothPlastic", collide=False)
        for s_ in (-1, 1):
            box("SunLeaf", (24, 1, 10), (x + s_ * 12, Y + 50 + s_ * 6, z), (80, 160, 70), "Grass", rot=(0, 0, s_ * 20),
                collide=False)
    sc(clear, cx, 26, 16, lambda x, z: CR._leaf(x, Y, z))
    sc(clear, cx, 40, 6, lambda x, z: CR._flower(x, Y, z))
    sc(clear, cx, 4, 22, lambda x, z: CR._chloroplast(x, Y + 70, z))
    landmark(clear, t.pts[slice(*t.marks["plant:leg"])], 0.12, 46, 22, CR._lm_flower,
                "🌸 زهرة عملاقة: البتلات تجذب الملقّحات")
    landmark(clear, t.pts[slice(*t.marks["plant:leg"])], 0.9, 46, 20, CR._lm_roots,
                "🌱 الجذور تمتص الماء والأملاح من التربة")


def stage_molecular(t, clear, cx, Y):
    dx, dy, dz = t.marks["dna"]
    CR._dna(dx, Y, dz, 190, r=16, ball_d=5)
    label("🧬 الـ DNA: سلّم حلزوني، كل درجة زوج قواعد (A-T و G-C)", dx + 30, Y + 40, dz, dx, dz, 30)
    # the ribosome straddling the straight between the two helix turns, with mRNA running through it
    lx, za, zb, ly = leg_x(t, "molecular")
    zm = (za + zb) / 2
    for s_ in (-1, 1):
        ball("RibosomeLarge", lx + s_ * 34, ly + 14, zm, 50, (120, 100, 210), "SmoothPlastic", collide=False)
        ball("RibosomeSmall", lx + s_ * 26, ly - 10, zm, 32, (170, 150, 240), "SmoothPlastic", collide=False)
    ball("RibosomeLarge", lx, ly + 40, zm, 46, (120, 100, 210), "SmoothPlastic", collide=False)
    rect("mRNA", lx - 70, lx + 70, ly - 2.6, ly - 1.8, zm - 1.5, zm + 1.5, (255, 120, 80), "Neon", collide=False, shadow=False)
    for q in range(8):
        ball("AminoAcid", lx + 6 + q * 2, ly + 66 + q * 7, zm + math.sin(q) * 6, 7,
             [(250, 90, 90), (90, 200, 120), (250, 210, 70), (90, 150, 250)][q % 4], "SmoothPlastic", collide=False)
    label("🧬 الريبوسوم يقرأ mRNA ويبني البروتين حمض أميني بعد الثاني", lx + 13, ly + 8, zm + 50, lx, zm, 30)
    # neon grid on the dark floor
    hi, lo = max(p[0] for p in t.pts[slice(*t.marks["molecular:leg"])]) + 140, min(
        p[0] for p in t.pts[slice(*t.marks["molecular:leg"])]) - 140
    xg = lo
    while xg < hi:
        rect("GridLine", xg - 0.4, xg + 0.4, Y, Y + 0.15, -CELLZ, CELLZ, (60, 200, 140), "Neon", collide=False, shadow=False)
        xg += 80
    zg = -CELLZ + 40
    while zg < CELLZ:
        rect("GridLine", lo, hi, Y, Y + 0.15, zg - 0.4, zg + 0.4, (60, 200, 140), "Neon", collide=False, shadow=False)
        zg += 80
    sc(clear, cx, 4, 16, lambda x, z: CR._dna(x, Y, z, 80))
    sc(clear, cx, 14, 6, lambda x, z: sign("Codon",
               rng.choice(["AUG", "UUU", "GGC", "UGG", "TATA", "A-T", "G-C"]), (x, Y + rng.uniform(20, 60), z), (10, 4, 0.4),
               "Front", bg=(20, 60, 50), color=(120, 255, 180)))


def stage_forensic(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "forensic")
    z0, z1 = min(za, zb), max(za, zb)
    rect("Street", lx - 22, lx + 22, Y, Y + 0.3, z0 - 140, z1 + 140, (48, 50, 56), "Asphalt", collide=False)
    # a night street: buildings with lit windows on both sides; the UV event (3) reveals fingerprints on them
    z = z0 - 120
    uv = 0
    while z < z1 + 120:
        for s_ in (-1, 1):
            w, d, h = rng.uniform(30, 42), 30, rng.uniform(40, 86)
            bx = lx + s_ * (40 + d / 2)
            if not clear.ok(bx, z, 20):
                continue
            col = rng.choice([(96, 84, 80), (80, 82, 96), (110, 100, 90), (70, 70, 78)])
            box("Building", (d, h, w), (bx, Y + h / 2, z), col, rng.choice(["Brick", "Concrete"]))
            fx = bx - s_ * (d / 2 + 0.2)
            for row in range(int(h // 16)):
                for c in (-1, 1):
                    if rng.random() < 0.6:
                        box("Window", (0.4, 6, 6), (fx, Y + 10 + row * 16, z + c * w / 4), (255, 214, 140), "Neon",
                            collide=False, shadow=False)
            if uv < 6 and h > 50:
                for q, dd in enumerate((22, 16, 10, 4)):
                    G.part("CartEvt3_UV", (0.4 + q * 0.1, dd, dd), (fx - s_ * 0.3 * (q + 1), Y + h * 0.55, z), (150, 90, 255),
                           "Neon", shape="Cylinder", transp=1.0, collide=False, shadow=False)
                uv += 1
        z += rng.uniform(46, 60)
    for q in range(6):
        zz = z0 + (z1 - z0) * (q + 0.5) / 6
        s_ = 1 if q % 2 else -1
        vcyl("StreetLamp", lx + s_ * 20, Y, Y + 26, zz, 1.2, (40, 40, 46), "Metal", collide=False)
        box("LampHead", (4, 1, 4), (lx + s_ * 18, Y + 26, zz), (255, 230, 170), "Neon", collide=False, shadow=False,
            light=(1.4, 40, (255, 220, 160)) if q % 2 == 0 else None)
        G.part("EvidenceMarker", (5, 6, 0.6), (lx - s_ * 12, Y + 3, zz + 10), (250, 210, 40), "SmoothPlastic",
               rot=(0, 90, 0), collide=False,
               text=dict(face="Front", text=str(q + 1), color=(20, 20, 20), bg=(250, 210, 40), bg_t=0.0))
    label("🔦 ضوء UV يكشف بصمات ما تشوفها العين!", lx + 13, ly + 10, (z0 + z1) / 2, lx + 60, (z0 + z1) / 2, 28)
    sc(clear, cx, 10, 10, lambda x, z: CR._tape(x, Y, z))
    sc(clear, cx, 3, 12, lambda x, z: CR._magnifier(x, Y, z))
    landmark(clear, t.pts[slice(*t.marks["forensic:leg"])], 0.12, 44, 26, CR._lm_fingerprint,
                "🔎 البصمة: نمطها يختلف من شخص لشخص")
    landmark(clear, t.pts[slice(*t.marks["forensic:leg"])], 0.88, 44, 22, CR._lm_evidence_lab,
                "🧪 تحليل الأدلة: عيّنات وجهاز DNA")


def stage_agri(t, clear, cx, Y):
    # fields of crop rows, a date-palm grove, greenhouses and windmills
    for q in range(40):
        spot = place(clear, cx, 0, CELLZ - 40, 34)
        if not spot:
            continue
        x, z = spot
        for r in range(-2, 3):
            rect("CropRow", x + r * 12 - 2.5, x + r * 12 + 2.5, Y, Y + rng.uniform(2.5, 4), z - 30, z + 30,
                 (110, 170, 80) if (q + r) % 2 else (220, 190, 90), "Grass", collide=False)
    sc(clear, cx, 24, 10, lambda x, z: CR._palm(x, Y, z))
    sc(clear, cx, 3, 30, lambda x, z: CR._windmill(x, Y, z))
    for q in range(2):
        spot = place(clear, cx, 0, CELLZ - 80, 50)
        if spot:
            x, z = spot
            box("Greenhouse", (80, 30, 40), (x, Y + 15, z), (200, 235, 220), "Glass", transp=0.5, collide=False)
            for r in range(5):
                box("GreenhouseRib", (1, 31, 41), (x - 40 + r * 20, Y + 15.5, z), (230, 236, 240), "Metal", collide=False)
            for r in range(4):
                rect("Bed", x - 34 + r * 18, x - 26 + r * 18, Y, Y + 3, z - 15, z + 15, (90, 160, 80), "Grass", collide=False)
    lx, za, zb, ly = leg_x(t, "agri")
    label("🌴 النخيل يتحمّل الحر والملوحة، والتمر من أهم محاصيل الكويت", lx + 13, ly + 10, (za + zb) / 2, lx + 60,
          (za + zb) / 2, 30)
    landmark(clear, t.pts[slice(*t.marks["agri:leg"])], 0.12, 40, 12, CR._lm_pivot, "💧 ري محوري: يسقي الحقل بدائرة كاملة")
    landmark(clear, t.pts[slice(*t.marks["agri:leg"])], 0.88, 44, 22, CR._lm_silo_tractor, "🌾 صومعة الحبوب والجرار")


def stage_biotech(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "biotech")
    z0, z1 = min(za, zb), max(za, zb)
    # a bioreactor hall: giant fermenters along the low run, process pipes over the rails
    for q in range(6):
        s_ = 1 if q % 2 else -1
        x, z = lx + s_ * 46, z0 + 20 + (z1 - z0 - 40) * (q // 2) / 2
        if not clear.ok(x, z, 18):
            continue
        vcyl("Fermenter", x, Y, Y + 70, z, 30, (210, 236, 245), "Glass", transp=0.45, collide=False)
        vcyl("Culture", x, Y + 2, Y + 52, z, 26, rng.choice([(90, 255, 160), (90, 220, 255), (255, 210, 90)]), "Neon",
             transp=0.35, collide=False, shadow=False)
        ball("FermenterDome", x, Y + 70, z, 30, (225, 230, 236), "Metal", collide=False)
        for b in range(5):
            ball("Bubble", x + rng.uniform(-8, 8), Y + 10 + b * 9, z + rng.uniform(-8, 8), rng.uniform(2, 4), (240, 255, 250),
                 "Glass", transp=0.3, collide=False)
    for q in range(4):
        z = z0 + 30 + q * (z1 - z0 - 60) / 3
        G.part("ProcessPipe", (140, 4, 4), (lx, ly + 30 + (q % 2) * 4, z), (190, 196, 204), "Metal", shape="Cylinder",
               collide=False)
        G.part("PipeBand", (2, 4.4, 4.4), (lx, ly + 30 + (q % 2) * 4, z), (60, 220, 255), "Neon", shape="Cylinder",
               collide=False, shadow=False)
    label("🧫 المخمّرات الحيوية: خلايا تصنع أدوية مثل الإنسولين", lx + 13, ly + 10, (z0 + z1) / 2, lx + 60, (z0 + z1) / 2, 30)
    for q in range(10):
        spot = place(clear, cx, 0, CELLZ - 40, 10)
        if spot:
            CR._jelly(spot[0], Y + rng.uniform(30, 70), spot[1])
    vx, vy, vz = t.marks["biotech:view"]
    label("🪼 بروتين GFP المضيء أصله من قنديل البحر، ويستخدم لتعليم الخلايا", vx, vy + 12, vz, cx, vz, 30)
    landmark(clear, t.pts[slice(*t.marks["biotech:leg"])], 0.12, 46, 24, CR._lm_pcr, "🧬 جهاز PCR: ينسخ DNA ملايين المرات")
    landmark(clear, t.pts[slice(*t.marks["biotech:leg"])], 0.88, 46, 22, CR._lm_crispr, "✂️ كريسبر: مقص جيني يعدّل DNA بدقة")


STAGES = {"micro": stage_micro, "biochem": stage_biochem, "animal": stage_animal, "plant": stage_plant,
          "molecular": stage_molecular, "forensic": stage_forensic, "agri": stage_agri, "biotech": stage_biotech}


RAIL_PROPS = {
    "micro": lambda x, z: disc("ColonyDot", x, GROUND_Y + 0.2, z, rng.uniform(6, 14), 0.5,
                               rng.choice([(250, 240, 205), (240, 190, 90), (230, 140, 170)]), "SmoothPlastic", collide=False),
    "biochem": lambda x, z: CR._tube(x, GROUND_Y, z),
    "animal": lambda x, z: (CR._cactus if rng.random() < 0.6 else CR._palm)(x, GROUND_Y, z),
    "plant": lambda x, z: (CR._flower if rng.random() < 0.7 else CR._leaf)(x, GROUND_Y, z),
    "molecular": lambda x, z: sign("Codon", rng.choice(["AUG", "UAA", "GCC", "A-T", "G-C", "5'→3'"]),
                                   (x, GROUND_Y + rng.uniform(8, 22), z), (8, 3, 0.4), "Front", bg=(20, 60, 50),
                                   color=(120, 255, 180)),
    "forensic": lambda x, z: CR._tape(x, GROUND_Y, z),
    "agri": lambda x, z: CR._palm(x, GROUND_Y, z),
    "biotech": lambda x, z: CR._bioreactor(x, GROUND_Y, z),
}


def rail_props(t, clear, k, key):
    """v53: small themed props close to the rails (alternating sides, ~70 studs apart) so the valleys never feel empty
    from the train. Skips tunnels and the hero runs (they have their own set pieces)."""
    starts = [i for i, _ in t.sections] + [len(t.pts)]
    i0, i1 = starts[k - 1], starts[k]
    low = t.marks.get(key + ":low", (0, 0))
    side, acc = 1, 0.0
    for i in range(i0 + 1, i1):
        a, b = t.pts[i - 1], t.pts[i]
        acc += math.dist(a[:3], b[:3])
        if acc < 110 or "t" in b[4] or "m" in b[4] or low[0] - 4 <= i <= low[1] + 4:
            continue
        acc = 0.0
        rx, rz = math.cos(math.radians(b[3])), -math.sin(math.radians(b[3]))
        d = rng.uniform(22, 38)
        x, z = b[0] + rx * side * d, b[2] + rz * side * d
        if abs(z) < CELLZ - 20 and clear.ok(x, z, 6):
            RAIL_PROPS[key](x, z)
        side = -side


RIVERS = {"animal", "plant", "agri", "forensic"}
TERRAIN_BLOCKS = []   # (x, y, z, sx, sy, sz, material) for CartTerrain.server


def grand_features(t, clear, k, key):
    """v54 set pieces every valley shares: the overlook pavilion inside the top hairpin, the stage tower inside the
    double spiral, the mesa the track tunnels through, and a river under the high bridge (landscape worlds)."""
    col = CR.SPEC_TRACK_COL[k - 1]
    Y = GROUND_Y
    # overlook pavilion
    ox, oy, oz = t.marks[key + ":overlook"]
    rect("OverlookDeck", ox - 22, ox + 22, oy - 3, oy - 2, oz - 18, oz + 18, (226, 220, 206), "WoodPlanks")
    for dx in (-20, 20):
        for dz in (-16, 16):
            vcyl("OverlookPier", ox + dx, Y, oy - 3, oz + dz, 3, (150, 140, 128), "Concrete", collide=False)
            vcyl("OverlookPost", ox + dx, oy - 2, oy + 10, oz + dz, 1.2, (240, 240, 236), "Metal", collide=False)
    rect("OverlookRoof", ox - 23, ox + 23, oy + 10, oy + 11, oz - 19, oz + 19, col, "SmoothPlastic", transp=0.2,
         collide=False)
    vcyl("OverlookFlagpole", ox, oy - 2, oy + 30, oz, 0.6, (230, 230, 236), "Metal", collide=False)
    box("OverlookFlag", (0.3, 6, 10), (ox, oy + 26, oz + 5), col, "Fabric", collide=False)
    # stage tower in the middle of the double spiral (molecular already has its giant DNA there)
    if key != "molecular":
        tx, ty, tz = t.marks[key + ":tower"]
        vcyl("StageTower", tx, Y, Y + 120, tz, 16, (236, 236, 240), "SmoothPlastic", collide=False)
        for q in range(6):
            vcyl("TowerRing", tx, Y + 14 + q * 18, Y + 16 + q * 18, tz, 17, col, "Neon", collide=False, shadow=False)
        ball("TowerCrown", tx, Y + 126, tz, 22, col, "Neon", transp=0.15, collide=False, shadow=False,
             light=(1.5, 60, col))
    # mesa tunnel: rock walls and roof over the straight, a rocky mass on top
    i0, i1 = t.marks[key + ":mesa"]
    mx = t.pts[i0][0]
    my = t.pts[i0][1]
    z0, z1 = sorted((t.pts[i0][2], t.pts[i1 - 1][2]))
    rect("MesaWall", mx - 40, mx - 8, Y - 2, my + 30, z0 - 10, z1 + 10, ROCK, "Sandstone")
    rect("MesaWall", mx + 8, mx + 40, Y - 2, my + 30, z0 - 10, z1 + 10, ROCK, "Sandstone")
    rect("MesaRoof", mx - 40, mx + 40, my + 12, my + 30, z0 - 10, z1 + 10, ROCK, "Sandstone")
    rect("MesaCap", mx - 34, mx + 30, my + 30, my + 44, z0 + 10, z1 - 20, (184, 152, 114), "Sandstone")
    for z in (z0 - 10, z1 + 10):
        rect("MesaPortal", mx - 9, mx + 9, my + 10, my + 13, z - 1.5, z + 1.5, (90, 76, 60), "Slate", collide=False)
    TERRAIN.append((mx - 30, my + 40, (z0 + z1) / 2, 34, "Limestone"))
    TERRAIN.append((mx + 26, my + 36, z0 + 20, 26, "Limestone"))
    # river under the high bridge, the full width of the valley
    if key in RIVERS:
        b0, b1 = t.marks[key + ":bridge"]
        rx = t.pts[b0][0]
        TERRAIN_BLOCKS.append((rx, Y + 1.0, 0.0, 46.0, 4.0, CELLZ * 2 - 20, "Water"))
        for z in range(int(-CELLZ + 40), int(CELLZ - 40), 70):
            for s_ in (-1, 1):
                TERRAIN.append((rx + s_ * 30, Y - 4, z + rng.uniform(-15, 15), rng.uniform(9, 13), "Sand"))


def scenery(t, cells):
    CR.CUTS[:] = []
    CR.ISLAND_Y = GROUND_Y   # the landmark builders stand on CR.ISLAND_Y
    clear = CR.Clear(t.pts, 16)
    for k, key in enumerate(CR.SECTION_KEYS, start=1):
        hi, lo = cells[k]
        CELL[0], CELL[1] = hi, lo
        with G.Group("CartScene%d" % k):
            STAGES[key](t, clear, (hi + lo) / 2, GROUND_Y)
            grand_features(t, clear, k, key)
            rail_props(t, clear, k, key)


def station_hall(t):
    sx, sy, sz = t.pts[0][:3]
    with G.Group("CartStationHall"):
        for xx in range(-36, 37, 18):
            for zz in (-40, 18):
                vcyl("StationColumn", sx + xx, sy - 2.4, sy + 44, sz + zz, 3.4, (230, 226, 216), "Marble")
        rect("StationRoofBeam", sx - 40, sx + 40, sy + 44, sy + 46, sz - 42, sz + 20, (200, 196, 186), "Concrete")
        rect("StationGlassRoof", sx - 38, sx + 38, sy + 46, sy + 46.6, sz - 40, sz + 18, (190, 220, 240), "Glass", transp=0.5,
             collide=False)
        sign("Departures", "🚆 المحطة الرئيسية | Grand Station\n8 عوالم • مايكروبيولوجي ← البايوتكنولوجي",
             (sx, sy + 34, sz - 39.4), (44, 8, 0.6), "Back", color=(255, 220, 120), bg=(16, 18, 26))
        sign("HowTo", "▶ تشغيل  •  ＋ أسرع  •  － أبطأ  •  🎥 كاميرا\nما تحتاج تضغط W طول الوقت",
             (sx + 22, sy + 8, sz + 17.4), (26, 6, 0.6), "Front", color=(255, 255, 255), bg=(40, 60, 110))


# ====================================================================== runtime terrain (CartTerrain.server)
# Soft terrain under the box cliffs (scree slopes) in every valley, plus rolling hills where the theme is a landscape
# (dunes for animals, meadows for plants, field edges for agriculture). The petri dish, the lab floors and the night
# street stay flat on purpose. Every ball keeps clear of the track.
HILLS = {"animal": ("Sand", 16), "plant": ("LeafyGrass", 14), "agri": ("Ground", 8)}
TERRAIN = []


def terrain_plan(t, cells):
    clear = CR.Clear(t.pts, 24)
    tr = random.Random(5353)
    for k, key in enumerate(CR.SECTION_KEYS, start=1):
        hi, lo = cells[k]
        # scree along both long cliffs and both ridges of this valley
        x = lo + 20
        while x < hi - 20:
            for s_ in (-1, 1):
                r = tr.uniform(26, 44)
                if clear.ok(x, s_ * (CELLZ - r * 0.25), r * 0.7):
                    TERRAIN.append((x, GROUND_Y - r * 0.35, s_ * (CELLZ - r * 0.25), r, "Limestone"))
            x += tr.uniform(36, 52)
        for xr in (hi, lo):
            z = -CELLZ + 20
            while z < CELLZ - 20:
                if abs(z) > 46:
                    r = tr.uniform(24, 40)
                    xx = xr - r * 0.3 if xr == hi else xr + r * 0.3
                    if clear.ok(xx, z, r * 0.7):
                        TERRAIN.append((xx, GROUND_Y - r * 0.35, z, r, "Limestone"))
                z += tr.uniform(36, 52)
        if key in HILLS:
            mat, n = HILLS[key]
            n = n * 2   # v54 valleys are larger
            placed = 0
            for _ in range(n * 25):
                if placed >= n:
                    break
                r = tr.uniform(30, 70)
                x, z = tr.uniform(lo + r, hi - r), tr.uniform(-CELLZ + r, CELLZ - r)
                if clear.ok(x, z, r * 0.8):
                    TERRAIN.append((x, GROUND_Y - r * 0.6, z, r, mat))
                    placed += 1


# ====================================================================== data modules
TRACK = []
EDGES = []


def build():
    t = build_track()
    bad = CR.check(t)
    with G.Group("CartRide"):
        draw_track(t)
        cells = valleys(t)
        scenery(t, cells)
        apply_captions(t)
        terrain_plan(t, cells)
        CR.stations(t)
        station_hall(t)
    TRACK[:] = t.pts
    EDGES[:] = t.ridges
    zs = [abs(p[2]) for p in t.pts]
    missing = [lm for lm in CR.LANDMARKS if lm[1] == "NOT PLACED"]
    print("grand tour: %d points, length %.0f studs, |z| max %.0f, %d landmarks (%d not placed %s)" % (
        len(t.pts), sum(math.dist(a[:3], b[:3]) for a, b in zip(t.pts, t.pts[1:])), max(zs), len(CR.LANDMARKS) - len(missing),
        len(missing), [m[0] for m in missing]))
    return len(t.pts), bad


def write_modules(shared_dir):
    import os
    ox, oy, oz = CR.CART_OFFSET
    with open(os.path.join(shared_dir, "CartTrack.luau"), "w", encoding="utf-8", newline="\n") as f:
        f.write("-- Generated by tools/cart_tour53.py: the Specialties Cart Ride track in world space.\n")
        f.write("-- Each point: { x, y, z, rightX, rightZ, flags, label }. Flags: s<k> stage start, t tunnel, e<n> event.\n")
        f.write("return {\n")
        for (x, y, z, yaw, flags, lab) in TRACK:
            r = math.radians(yaw)
            f.write('\t{ %.2f, %.2f, %.2f, %.4f, %.4f, "%s", "%s" },\n' % (
                x + ox, y + oy, z + oz, math.cos(r), -math.sin(r), ",".join(flags), lab.replace('"', "'")))
        f.write("}\n")
    with open(os.path.join(shared_dir, "CartTerrain.luau"), "w", encoding="utf-8", newline="\n") as f:
        f.write("-- Generated by tools/cart_tour53.py: terrain balls for CartTerrain.server (world space).\n")
        f.write("-- Each: { x, y, z, radius, material }.\nreturn {\n")
        for (x, y, z, r, m) in TERRAIN:
            f.write('\t{ %.1f, %.1f, %.1f, %.1f, "%s" },\n' % (x + ox, y + oy, z + oz, r, m))
        # v54 blocks (rivers): { "block", x, y, z, sx, sy, sz, material }
        for (x, y, z, sx, sy, sz, m) in TERRAIN_BLOCKS:
            f.write('\t{ "block", %.1f, %.1f, %.1f, %.1f, %.1f, %.1f, "%s" },\n' % (x + ox, y + oy, z + oz, sx, sy, sz, m))
        f.write("}\n")
    with open(os.path.join(shared_dir, "CartRooms.luau"), "w", encoding="utf-8", newline="\n") as f:
        f.write("-- Generated by tools/cart_tour53.py: the Specialties Cart Ride valleys in ride order.\n")
        f.write("-- edges = world x where stage k begins (the ride heads to -X), zones = index into Shared/Zones for its look.\n")
        f.write("return {\n\tedges = { %s },\n" % ", ".join("%.1f" % (x + ox) for x in EDGES))
        f.write("\tzones = { %s },\n}\n" % ", ".join(str(CR.SECTION_ZONE[k]) for k in CR.SECTION_KEYS))
