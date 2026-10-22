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
    x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    # v56: Roblox parts stop at 2048 studs; the enormous valleys need floors and walls longer than that -> tile
    if x1 - x0 > 2000 or z1 - z0 > 2000:
        nx, nz = int((x1 - x0) // 2000) + 1, int((z1 - z0) // 2000) + 1
        for i in range(nx):
            for j in range(nz):
                C5.rect(name, x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx, y0, y1,
                        z0 + (z1 - z0) * j / nz, z0 + (z1 - z0) * (j + 1) / nz, *a, **k)
        return
    C5.rect(name, x0, x1, y0, y1, z0, z1, *a, **k)
rng = random.Random(53)

GROUND_Y = -14.0        # stage valley floor (the track runs at y -4 .. +44)
STATION_GROUND = -2.4   # the station cell floor = the station deck top
CELLZ = 1120.0          # half width of every valley (v56: enormous valleys)
LEGZ = 900.0            # how far each leg runs out from the centre line (hairpin centres)
TUNNEL_L = 160.0
RIDGE_T = 44.0
CR.STEP = 8.0           # longer track, fewer points: the client interpolates between them

# viewpoint climb and low-run height per stage
PATH = {
    "micro": (34, -4), "biochem": (28, -2), "animal": (30, -4), "plant": (24, -4),
    "molecular": (30, 0), "forensic": (20, -4), "agri": (26, -2), "biotech": (32, -2),
}
GROUND = {
    "micro": ((182, 128, 52), "SmoothPlastic"), "biochem": ((222, 216, 238), "Marble"),   # v63: amber agar (rim colour)
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


# v56 pacing per world (so the eight valleys do not repeat one rhythm): turns in the opening spiral, number of hills
# in leg C and their height
VARIANT = {
    "micro": (1, 3, 16), "biochem": (2, 2, 14), "animal": (1, 4, 24), "plant": (1, 4, 14),
    "molecular": (3, 2, 12), "forensic": (1, 2, 10), "agri": (1, 4, 10), "biotech": (2, 3, 18),
}


# v59 (owner: "less predictable track geometry"): each specialty gets its own track signature on top of the shared
# five-leg layout. b1/b2: S-bend slaloms after the bridge and before the drop (angle, radius) - every (a, -2a, a)
# S keeps the line, so legs still end at the edge; c: leg C profile ("hills", n, h) / ("camel", [h..]) uneven humps /
# ("drop", depth) a dramatic but safe dive and climb; d: after the mesa, S-bends or ("helix", deg, R, dy) a scenic spiral.
SIG = {
    "micro": dict(b1=[(24, 200)], b2=[(18, 260), (18, 260)], c=("hills", 3, 16), d=[(30, 140)]),
    "biochem": dict(b1=[(30, 100), (30, 100), (30, 100)], b2=[(20, 200)], c=("camel", [10, 22, 14]),
                    d=("helix", 360, 60, 24)),
    "animal": dict(b1=[(16, 320)], b2=[(28, 160), (28, 160)], c=("drop", 34), d=[(36, 120)]),
    "plant": dict(b1=[(22, 220), (22, 220)], b2=[(32, 130)], c=("hills", 4, 14), d=("helix", 360, 70, 20)),
    "molecular": dict(b1=[(26, 150)], b2=[(26, 130), (26, 130), (26, 130)], c=("camel", [8, 16, 24, 12]),
                      d=[(20, 240)]),
    "forensic": dict(b1=[(34, 100), (34, 100)], b2=[(14, 320)], c=("drop", 28), d=("helix", 360, 55, 20)),
    "agri": dict(b1=[(12, 400)], b2=[(20, 240), (20, 240)], c=("hills", 4, 10), d=[(28, 150), (28, 150)]),
    "biotech": dict(b1=[(30, 130), (30, 130)], b2=[(24, 180)], c=("drop", 40), d=("helix", 360, 65, 28)),
}


# v61 (owner: "every stage is the same template"): each valley ends differently. ("spiral", deg, R) circles the giant,
# ("through", len) rides through it at THROUGH_Y, ("beside", angle, R) swings past it on a descending S-bend.
FINALE = {
    "micro": ("spiral", 720, 50),
    "biochem": ("spiral", 360, 85),
    "animal": ("beside", 30, 170),
    "plant": ("spiral", 1080, 44),
    "molecular": ("spiral", 720, 50),
    "forensic": ("through", 90),
    "agri": ("beside", 24, 220),
    "biotech": ("through", 130),
}
THROUGH_Y = 26.0


def zadv(bends):
    """distance an S-bend list advances along the leg"""
    return sum(4 * R * math.sin(math.radians(a)) for a, R in bends)


def slalom(t, bends, w):
    """right-left S-bends; the side alternates so the rider feels right, left, right..."""
    for i, (a, R) in enumerate(bends):
        s_bend(t, w if i % 2 == 0 else -w, a, R)


def to_edge(t):
    """distance from here to the valley edge (z = +-LEGZ) in the direction the turtle is heading along z"""
    hz = math.cos(math.radians(t.yaw))
    return abs((LEGZ if hz > 0 else -LEGZ) - t.p[2])


def stage_path(t, key, s):
    """v56 enormous valley: five legs across the valley (|z| up to LEGZ) joined by four hairpins.
    A (half): spiral climb + rise to the overlook | B: the highline, a long bridge over the river with two S-bends
    C: drop into a slot canyon (':canyon'), then rolling hills | D: the hero set piece (':low'), a tunnel through a
    mesa, an S-bend, a climb | E (half): double spiral down around the stage tower, home to z = 0 at the exit tunnel.
    Leg remainders are measured to the edge in the heading direction, so every leg ends exactly at the edge."""
    h_top, low = PATH[key]
    h_top += 76   # the highline is far above the valley floor
    mid = 50.0
    R1, RH = 130.0, 150.0
    hp = [0]

    def hairpin(flags=()):
        t.turn(180 * (-s if hp[0] % 2 == 0 else s), RH, flags=flags)
        hp[0] += 1

    t.straight(40)
    t.turn(90 * s, R1)
    # ---- A: spiral climb, then up to the overlook
    spirals, hills, hill_h = VARIANT[key]
    t.straight(40)
    t.turn(360 * spirals * west(t), 55, dy=40 * spirals + 10)
    t.marks[key + ":spiralA"] = t.last_center
    t.straight(to_edge(t), dy=h_top - t.p[1])
    t.marks[key + ":view"] = tuple(t.p)
    hairpin(["e%d" % EVENT[key]] if key in ("micro",) else ())
    t.marks[key + ":overlook"] = t.last_center
    i_leg = len(t.pts)
    # ---- B: the highline
    sig = SIG[key]
    # the bridge gives way when the slaloms are long, so the descent after them always has >= ~330 studs
    bridge = max(300.0, min(520.0, 2 * LEGZ - zadv(sig["b1"]) - zadv(sig["b2"]) - 160 - 330))
    i0 = len(t.pts)
    t.straight(bridge, dy=8)
    t.marks[key + ":bridge"] = (i0, len(t.pts))
    slalom(t, sig["b1"], west(t))
    t.straight(160)
    slalom(t, sig["b2"], -west(t))
    t.straight(to_edge(t), dy=mid + 10 - t.p[1])
    hairpin()
    # ---- C: the slot canyon, then rolling hills
    t.straight(260, dy=low - t.p[1])
    i0 = len(t.pts)
    t.straight(380, flags=["k"])
    t.marks[key + ":canyon"] = (i0, len(t.pts))
    prof = sig["c"]
    if prof[0] == "camel":          # uneven humps: the rhythm never settles
        for h in prof[1]:
            t.straight(120, dy=h)
            t.straight(120, dy=-h)
    elif prof[0] == "drop":         # v61: a lift hill, then a dive back to the canyon floor level (the v59 dip went
        t.straight(220, dy=prof[1])  # below the valley floor with no tunnel: "the track sinks into the ground")
        t.straight(40)
        t.straight(130, dy=-prof[1])
        t.straight(130)
    else:
        for _ in range(prof[1]):
            t.straight(120, dy=prof[2])
            t.straight(120, dy=-prof[2])
    t.straight(to_edge(t))
    hairpin()
    # ---- D: hero set piece, mesa tunnel, S-bend, climb
    t.straight(120)
    i0 = len(t.pts)
    t.straight(280, flags=["e%d" % EVENT[key]] if key in ("plant", "forensic") else ())
    t.marks[key + ":low"] = (i0, len(t.pts))
    i0 = len(t.pts)
    t.straight(160, flags=["m"])
    t.marks[key + ":mesa"] = (i0, len(t.pts))
    if sig["d"][0] == "helix":      # a scenic spiral: one full turn that climbs or dips, the leg carries on in line
        t.straight(110)   # v61: clear of the mesa first (the turn swung back through its walls)
        t.turn(sig["d"][1] * west(t), sig["d"][2], dy=sig["d"][3])
    else:
        slalom(t, sig["d"], west(t))
    t.straight(to_edge(t), dy=mid - t.p[1])
    t.marks[key + ":leg"] = (i_leg, len(t.pts))
    hairpin()
    # ---- E: the valley's finale around (or through) its giant, then home to z = 0 at y 0
    t.straight(60)
    fin = FINALE.get(key, ("spiral", 720, 50))
    if fin[0] == "spiral":
        t.turn(fin[1] * west(t), fin[2], dy=-(t.p[1]))
        t.marks["dna" if key == "molecular" else key + ":tower"] = t.last_center
    elif fin[0] == "through":       # v61: ride straight through the giant (magnifier ring, bioreactor tube)
        t.straight(220, dy=THROUGH_Y - t.p[1])
        i0 = len(t.pts)
        t.straight(fin[1])
        p = t.pts[(i0 + len(t.pts)) // 2]
        t.marks[key + ":tower"] = (p[0], p[1], p[2], p[3])
        t.straight(220, dy=-t.p[1])
    else:                           # "beside": a descending S-bend that swings past the giant
        t.straight(160, dy=-t.p[1] / 2)
        i0 = len(t.pts)
        s_bend(t, west(t), fin[1], fin[2])
        p = t.pts[(i0 + len(t.pts)) // 2]
        rx, rz = math.cos(math.radians(p[3])), -math.sin(math.radians(p[3]))
        t.marks[key + ":tower"] = (p[0] - rx * west(t) * 70, p[1], p[2] - rz * west(t) * 70)
        t.straight(160, dy=-t.p[1])
    t.straight(max(10.0, abs(t.p[2]) - R1))
    t.turn(90 * s * (1 if hp[0] % 2 else -1), R1)
    t.straight(40)


def underground_points(t):
    """v61 rule: outside tunnels ('t') and the mesa bore ('m') the rails stay above the valley floor"""
    bad = 0
    for p in t.pts:
        floor = STATION_GROUND if p[0] > t.ridges[0] else GROUND_Y
        if p[1] < floor + 1.5 and not any(f in ("t", "m") for f in p[4]):
            bad += 1
    return bad


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


_COLUMN_HASH = {}


def column_blocked(a, floor):
    """v61 (owner: "a pillar in the middle of the track"): a support under point a must not pass through the rider
    envelope of any other stretch of track below it (spirals and crossings stack the track)."""
    for cx in (int(a[0] // 16) - 1, int(a[0] // 16), int(a[0] // 16) + 1):
        for cz in (int(a[2] // 16) - 1, int(a[2] // 16), int(a[2] // 16) + 1):
            for q in _COLUMN_HASH.get((cx, cz), ()):
                if floor - 1 < q[1] + 10 and q[1] < a[1] - 6 and (q[0] - a[0]) ** 2 + (q[2] - a[2]) ** 2 < 6.5 ** 2:
                    return True
    return False


def draw_track(t):
    _COLUMN_HASH.clear()
    for q in t.pts:
        _COLUMN_HASH.setdefault((int(q[0] // 16), int(q[2] // 16)), []).append(q)
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
                if a[1] - floor > 7 and not column_blocked(a, floor):
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
            # v61 (owner: "no primitive writing on the track"): the stage name is a title card on screen now
            G.part("SpecGateBeam", (19.0, 1.2, 1.2), (sx, sy + 17.5, sz), col, "Neon", rot=(0, syaw, 0), collide=False,
                   shadow=False)


# ====================================================================== valleys, ridges, tunnels
def cell_ranges(t):
    """x range (hi, lo) of the station cell and every stage cell"""
    xs = [p[0] for p in t.pts]
    east, west = 110.0, min(xs) - 150.0
    edges = [east] + t.ridges + [west]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


STRATA = [(205, 176, 136), (188, 156, 118), (214, 188, 150)]   # canyon rock layers (v56)

# v62 (owner: "change the theme"): every valley was walled by the same desert sandstone, so the stages read as one
# template. Each specialty now has its own walls, ridge faces and scree: (three layer colours, part material, scree
# terrain material). Same rng calls as before, so the track and the layout do not move.
WALLS = {
    "station": (STRATA, "Sandstone", "Limestone"),
    "micro": ([(238, 228, 200), (226, 214, 182), (246, 238, 216)], "SmoothPlastic", "Salt"),        # agar plate rim
    "biochem": ([(204, 196, 232), (186, 178, 220), (222, 216, 242)], "Marble", "Slate"),            # lab tiles
    "animal": (STRATA, "Sandstone", "Limestone"),                                                     # Kuwait desert
    "plant": ([(92, 138, 72), (74, 116, 60), (108, 154, 84)], "Grass", "LeafyGrass"),                # green hills
    "molecular": ([(34, 40, 78), (26, 30, 62), (46, 54, 100)], "SmoothPlastic", "Basalt"),           # dark gel lab
    "forensic": ([(74, 76, 88), (62, 64, 74), (88, 90, 102)], "Concrete", "Asphalt"),                # night city
    "agri": ([(156, 116, 74), (136, 100, 62), (172, 132, 88)], "Ground", "Ground"),                   # farm earth
    "biotech": ([(222, 230, 236), (204, 212, 220), (236, 240, 244)], "Metal", "Concrete"),          # clean lab
}
CELLS = []   # x ranges (hi, lo) of the station and the eight valleys, set by valleys()


def key_at(x):
    """which world the x position belongs to ("station" for the station cell and outside)"""
    for k, (hi, lo) in enumerate(CELLS):
        if lo <= x <= hi:
            return "station" if k == 0 else CR.SECTION_KEYS[k - 1]
    return "station"



def canyon_wall_x(x1, x, s_, top):
    """a long side wall facing the valley (+-z), built as three stepped rock layers with a crag on top"""
    h0, h1 = GROUND_Y + (top - GROUND_Y) * 0.42, GROUND_Y + (top - GROUND_Y) * 0.74
    cx, L = (x1 + x) / 2, x - x1 + 2
    for tier, (ya, yb, setback) in enumerate(((GROUND_Y - 4, h0, 0), (h0, h1, 12), (h1, top, 26))):
        zf = s_ * (CELLZ + setback)
        cols, mat, _ = WALLS[key_at(cx)]
        box("Cliff", (L, yb - ya, 44), (cx, (ya + yb) / 2, zf + s_ * 22), cols[tier], mat,
            rot=(0, rng.uniform(-2.5, 2.5), 0))
    cols, mat, _ = WALLS[key_at(cx)]
    box("CliffCrag", (rng.uniform(24, 46), rng.uniform(16, 34), rng.uniform(20, 34)),
        (cx + rng.uniform(-20, 20), top + 6, s_ * (CELLZ + 34)), cols[rng.randrange(3)], mat,
        rot=(rng.uniform(-10, 10), rng.uniform(0, 90), rng.uniform(-10, 10)), collide=False)


def ridge(xm, next_col):
    """a rock ridge across the valley at x = xm with the tunnel through it"""
    z = -CELLZ - 20
    while z < CELLZ + 20:
        w = rng.uniform(36, 60)
        z1 = min(z + w, CELLZ + 20)
        top = GROUND_Y + rng.uniform(210, 270)   # v54: taller than the highest bridge
        # v56: three layers narrowing upward (a weathered ridge, not a slab), tunnel opening kept at the bottom
        h0, h1 = GROUND_Y + (top - GROUND_Y) * 0.42, GROUND_Y + (top - GROUND_Y) * 0.74
        for tier, (ya, yb, half) in enumerate(((GROUND_Y - 4, h0, RIDGE_T / 2 + 14), (h0, h1, RIDGE_T / 2 + 4),
                                               (h1, top, RIDGE_T / 2 - 6))):
            x0, x1 = xm - half - rng.uniform(0, 6), xm + half + rng.uniform(0, 6)
            for xa, xb, side in ((x0, xm, key_at(xm - 60)), (xm, x1, key_at(xm + 60))):   # west face, east face
                cols, mat, _ = WALLS[side]
                if z1 < -14 or z > 14 or ya >= 22:
                    rect("Ridge", xa, xb, ya, yb, z, z1, cols[tier], mat)
                else:
                    for za, zb in ((z, -14), (14, z1)):
                        if zb - za > 0.5:
                            rect("Ridge", xa, xb, ya, yb, za, zb, cols[tier], mat)
                    rect("Ridge", xa, xb, 22, yb, -14, 14, cols[tier], mat)
        z = z1
    # a stepped crest so the skyline is not one flat line
    for q in range(10):
        zz = rng.uniform(-CELLZ, CELLZ)
        if abs(zz) > 40:
            cols, mat, _ = WALLS[key_at(xm - 60)]
            box("RidgeCrag", (RIDGE_T * 0.7, rng.uniform(20, 50), rng.uniform(30, 60)), (xm, GROUND_Y + 265, zz),
                cols[2], mat, rot=(0, rng.uniform(-20, 20), rng.uniform(-8, 8)), collide=False)


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
    CELLS[:] = cells
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
                canyon_wall_x(x1, x, s_, top)
                x = x1
        for xe, side in ((east, "station"), (west, CR.SECTION_KEYS[-1])):
            cols, mat, _ = WALLS[side]
            rect("Cliff", xe - 20, xe + 20, GROUND_Y - 4, GROUND_Y + 280, -CELLZ - 40, CELLZ + 40, cols[0], mat)
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
DENSITY = 2.6       # v56 valleys stream on the client, so density is limited per valley, not by the whole map


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
        z = -CELLZ + 220
        while z < CELLZ - 150:
            discs.append((x, z, 250))
            z += 350
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


def flat_colony(name, x, z, d, col, Y):
    """v63 (owner: the round domes with a bump on top looked wrong): a colony as it really sits on agar: flat, a little
    raised, with a wavy lobed edge and a faint halo; no dome, no centre bump. Own RNG per spot (the shared rng is
    untouched). The grow event scales every part named CartEvt1_Colony, so the lobes share the name."""
    r = random.Random(int(x * 13 + z * 7))
    disc(name, x, Y + 0.12, z, d * 1.22, 0.12, tuple(min(255, c + 18) for c in col), "SmoothPlastic", collide=False,
         shadow=False, transp=0.45)                                          # the faint halo round the colony
    disc(name, x, Y + 0.7, z, d, 1.2, col, "SmoothPlastic", collide=False, shadow=False)
    for q in range(9):                                                         # lobed, organic margin
        a = q * 2 * math.pi / 9 + r.uniform(-0.25, 0.25)
        rr = d * r.uniform(0.36, 0.46)
        disc(name, x + math.cos(a) * rr, Y + 0.65, z + math.sin(a) * rr, d * r.uniform(0.22, 0.34), 1.1, col,
             "SmoothPlastic", collide=False, shadow=False)


def stage_micro(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "micro")
    vx, vy, vz = t.marks["micro:view"]
    # v63 real colony colours: cream, golden (S. aureus), red (Serratia), white, yellow-cream (same count: same rng)
    COLS = [(244, 232, 196), (236, 186, 70), (204, 64, 70), (248, 246, 238), (232, 214, 150)]
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
        flat_colony(name, x, z, d, col, Y)
    # an antibiotic disc with its clear inhibition zone, beside the low run
    for s_ in (1, -1):
        ax, az = lx + s_ * 70, (za + zb) / 2
        if clear.ok(ax, az, 46):
            disc("InhibitionZone", ax, Y + 0.25, az, 90, 0.3, (248, 236, 190), "SmoothPlastic", collide=False)
            disc("AntibioticDisc", ax, Y + 0.6, az, 12, 1.0, (252, 252, 252), "SmoothPlastic", collide=False)
            for q in range(10):
                a = q * math.pi / 5
                flat_colony("Colony", ax + 58 * math.cos(a), az + 58 * math.sin(a), 14, COLS[q % 3], Y)
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


def low_run(t, key):
    """v61: z range of the straight hero run (':low'), where the whale ribcage / leaf canopy belong (the rest of the
    leg now ends in S-bends or a spiral, which the set pieces used to cut through)"""
    i0, i1 = t.marks[key + ":low"]
    zs = [p[2] for p in t.pts[i0:i1]]
    return min(zs), max(zs)


def stage_animal(t, clear, cx, Y):
    lx, za, zb, ly = leg_x(t, "animal")
    z0, z1 = low_run(t, "animal")
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
    # v61: the skull is a hollow mouth the train rides into (the solid block sat on the rails)
    for s_ in (-1, 1):
        box("WhaleSkull", (11, 16, 40), (lx + s_ * 11.5, Y + 10, head), BONE, "SmoothPlastic", collide=False)
    box("WhaleSkull", (34, 5, 40), (lx, ly + 13.5, head), BONE, "SmoothPlastic", collide=False)
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
    z0, z1 = low_run(t, "plant")
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
    sc(clear, cx, 14, 6, lambda x, z: _base_pair(   # v62: floating base pairs (were text boards)
        x, z, rng.choice([((255, 90, 90), (255, 220, 80)), ((90, 200, 110), (90, 150, 255))]), Y + rng.uniform(20, 60)))


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


def _base_pair(x, z, cols, y):
    """a floating base pair (A-T red/yellow or G-C green/blue): two glowing bases joined by a bond"""
    for s_, col in ((-1, cols[0]), (1, cols[1])):
        ball("BasePair", x + s_ * 3, y, z, 3.2, col, "Neon", collide=False, shadow=False)
    box("BaseBond", (3, 0.5, 0.5), (x, y, z), (240, 240, 250), "SmoothPlastic", collide=False, shadow=False)


RAIL_PROPS = {
    "micro": lambda x, z: disc("ColonyDot", x, GROUND_Y + 0.2, z, rng.uniform(6, 14), 0.5,
                               rng.choice([(244, 232, 196), (236, 186, 70), (248, 246, 238)]), "SmoothPlastic", collide=False),
    "biochem": lambda x, z: CR._tube(x, GROUND_Y, z),
    "animal": lambda x, z: CR._cactus(x, GROUND_Y, z) if rng.random() < 0.6 else _bigpalm(x, z),
    "plant": lambda x, z: (CR._flower if rng.random() < 0.7 else CR._leaf)(x, GROUND_Y, z),
    "molecular": lambda x, z: _base_pair(x, z, rng.choice([((255, 90, 90), (255, 220, 80)), ((90, 200, 110), (90, 150, 255))]),
                                         GROUND_Y + rng.uniform(8, 22)),   # v62: a glowing base pair, no text
    "forensic": lambda x, z: CR._tape(x, GROUND_Y, z),
    "agri": lambda x, z: _bigpalm(x, z),
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


# (wall colour, wall material, cap colour, cap material, portal colour, wall transparency)
TUNNEL_STYLE = {
    "micro": ((236, 168, 196), "SmoothPlastic", (250, 205, 222), "SmoothPlastic", (255, 120, 180), 0),   # cell membrane
    "biochem": ((120, 150, 230), "SmoothPlastic", (160, 190, 250), "SmoothPlastic", (255, 210, 90), 0),  # folded protein
    "plant": ((112, 82, 52), "Wood", (80, 140, 60), "Grass", (70, 50, 32), 0),                          # hollow log
    "molecular": ((120, 70, 170), "SmoothPlastic", (170, 120, 220), "SmoothPlastic", (255, 230, 120), 0),  # chromosome
    "forensic": ((60, 62, 72), "Concrete", (80, 82, 96), "Concrete", (255, 214, 60), 0),                # evidence vault
    "agri": ((190, 232, 200), "Glass", (90, 160, 80), "Grass", (230, 236, 240), 0.45),                 # greenhouse
    "biotech": ((170, 178, 190), "DiamondPlate", (200, 206, 214), "Metal", (80, 220, 255), 0),          # steel bore
}


def _phage(x, z, Y, col):
    """micro: a bacteriophage standing on its tail fibres; the spiral circles its tail"""
    vcyl("PhageTail", x, Y + 14, Y + 74, z, 7, (190, 196, 206), "Metal", collide=False)
    vcyl("PhageCollar", x, Y + 74, Y + 78, z, 14, (150, 156, 170), "Metal", collide=False)
    ball("PhageHead", x, Y + 96, z, 36, (205, 120, 230), "Glass", transp=0.15, collide=False)
    ball("PhageDNA", x, Y + 96, z, 20, (255, 210, 90), "Neon", collide=False, shadow=False)
    for a in range(6):
        ang = math.radians(a * 60)
        box("PhageFibre", (1.4, 22, 1.4), (x + math.sin(ang) * 9, Y + 8, z + math.cos(ang) * 9), (170, 176, 190), "Metal",
            rot=(math.degrees(math.cos(ang)) * 0.6, 0, -math.degrees(math.sin(ang)) * 0.6), collide=False)


def _atp_synthase(x, z, Y, col):
    """biochem: ATP synthase - a membrane rotor stack with the catalytic head on top"""
    for q in range(6):
        vcyl("RotorDisc", x, Y + q * 9, Y + q * 9 + 7, z, 26 - q, (120 + q * 12, 150, 230), "SmoothPlastic", collide=False)
    vcyl("Stalk", x, Y + 54, Y + 80, z, 5, (255, 210, 90), "SmoothPlastic", collide=False)
    for a in range(3):
        ang = math.radians(a * 120)
        ball("AlphaBeta", x + math.sin(ang) * 9, Y + 90, z + math.cos(ang) * 9, 18, (230, 110, 120) if a % 2 else (250, 170, 90),
             "SmoothPlastic", collide=False)


def _turtle(x, z, Y, col):
    """animal: a giant hawksbill turtle (Kuwait's islands) resting on a rock"""
    ball("TurtleRock", x, Y + 6, z, 34, (150, 140, 128), "Slate", collide=False)
    vcyl("TurtleShellRim", x, Y + 20, Y + 26, z, 38, (120, 84, 50), "SmoothPlastic", collide=False)
    ball("TurtleShell", x, Y + 26, z, 32, (150, 108, 60), "SmoothPlastic", collide=False)
    for q in range(5):
        ang = math.radians(q * 72)
        ball("ShellScute", x + math.sin(ang) * 9, Y + 38, z + math.cos(ang) * 9, 8, (175, 130, 75), "SmoothPlastic", collide=False)
    ball("TurtleHead", x, Y + 24, z + 22, 10, (110, 140, 100), "SmoothPlastic", collide=False)
    for sx, sz in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        box("TurtleFlipper", (14, 2, 6), (x + sx * 20, Y + 20, z + sz * 10), (110, 140, 100), "SmoothPlastic",
            rot=(0, sx * sz * 25, -sx * 15), collide=False)


def _sunflower(x, z, Y, col):
    """plant: a giant sunflower; the head faces the riders on the spiral"""
    vcyl("FlowerStem", x, Y, Y + 92, z, 5, (80, 150, 60), "SmoothPlastic", collide=False)
    for q, h in enumerate((30, 52)):
        box("FlowerLeaf", (22, 1.2, 9), (x + (12 if q else -12), Y + h, z), (90, 170, 70), "Grass",
            rot=(0, 0, 20 if q else -20), collide=False)
    G.part("FlowerHead", (4, 30, 30), (x, Y + 104, z), (110, 70, 30), "SmoothPlastic", shape="Cylinder", collide=False)
    for q in range(14):
        ang = math.radians(q * 360 / 14)
        box("FlowerPetal", (2, 9, 5), (x, Y + 104 + math.cos(ang) * 19, z + math.sin(ang) * 19), (255, 205, 40),
            "SmoothPlastic", rot=(math.degrees(ang), 0, 0), collide=False)


def _magnifier(x, z, Y, col):
    """forensic: a giant magnifying glass over a glowing fingerprint"""
    for q in range(5):
        vcyl("FingerprintRidge", x, Y - 0.6, Y - 0.2 + q * 0.01, z, 40 - q * 7, (60, 200, 255) if q % 2 == 0 else (30, 40, 60),
             "Neon" if q % 2 == 0 else "SmoothPlastic", collide=False, shadow=False)
    vcyl("MagnifierHandle", x, Y, Y + 56, z, 6, (60, 40, 30), "Wood", collide=False)
    for q in range(18):
        ang = math.radians(q * 20)
        box("MagnifierRim", (2.6, 8.2, 3), (x, Y + 82 + math.cos(ang) * 24, z + math.sin(ang) * 24), (200, 170, 60), "Metal",
            rot=(math.degrees(ang), 0, 0), collide=False)
    G.part("MagnifierLens", (1, 46, 46), (x, Y + 82, z), (190, 230, 250), "Glass", shape="Cylinder", transp=0.55,
           collide=False, shadow=False)


def _datepalm(x, z, Y, col):
    """agri: a giant date palm heavy with dates"""
    vcyl("GiantPalmTrunk", x, Y, Y + 100, z, 7, (150, 118, 82), "Wood", collide=False)
    for q in range(7):
        vcyl("GiantPalmRing", x, Y + 10 + q * 13, Y + 11.5 + q * 13, z, 8, (128, 98, 66), "Wood", collide=False)
    for a in range(10):
        ang = math.radians(a * 36)
        box("GiantFrond", (34, 1, 5), (x + math.sin(ang) * 17, Y + 98, z + math.cos(ang) * 17), (70, 140, 60), "Grass",
            rot=(0, math.degrees(ang) + 90, -18), collide=False)
    for a in range(5):
        ang = math.radians(a * 72 + 20)
        ball("DateBunch", x + math.sin(ang) * 6, Y + 88, z + math.cos(ang) * 6, 6, (210, 120, 40), "SmoothPlastic", collide=False)


def _bioreactor(x, z, Y, col):
    """biotech: a glass bioreactor with glowing culture and rising bubbles"""
    vcyl("ReactorGlass", x, Y, Y + 84, z, 36, (200, 235, 245), "Glass", transp=0.55, collide=False)
    vcyl("ReactorCulture", x, Y + 2, Y + 62, z, 33, (90, 230, 140), "Neon", transp=0.35, collide=False, shadow=False)
    ball("ReactorDome", x, Y + 84, z, 36, (190, 198, 210), "Metal", collide=False)
    for q in range(8):
        ball("Bubble", x + math.sin(q * 2.4) * 9, Y + 10 + q * 7, z + math.cos(q * 2.4) * 9, 3, (230, 255, 240), "Glass",
             transp=0.3, collide=False, shadow=False)
    for s_ in (-1, 1):
        box("ReactorPipe", (2.4, 2.4, 26), (x + s_ * 20, Y + 70, z), (170, 178, 190), "Metal", collide=False)


def _ring(name, x, cy, z, R, n, size, colr, mat):
    """a vertical ring across a z-running track: n tangent blocks (size = tangent, radial, depth)"""
    for q in range(n):
        a = math.radians(q * 360 / n)
        box(name, size, (x + math.sin(a) * R, cy + math.cos(a) * R, z), colr, mat, rot=(0, 0, -math.degrees(a)),
            collide=False)


def _magnifier_through(m, Y):
    """forensic finale: the train rides straight through the lens ring of a giant magnifying glass, a glowing
    fingerprint on the ground below"""
    x, ry, z = m[0], m[1], m[2]
    cy = ry + 4.5
    _ring("MagnifierRim", x, cy, z, 24, 18, (9, 5, 3.5), (210, 175, 60), "Metal")
    _ring("MagnifierGlow", x, cy, z, 21, 18, (7.6, 0.8, 1), (255, 230, 120), "Neon")
    box("MagnifierHandle", (6, 44, 6), (x + math.sin(math.radians(140)) * 46, cy + math.cos(math.radians(140)) * 46, z),
        (70, 45, 30), "Wood", rot=(0, 0, -140), collide=False)
    for q in range(5):
        vcyl("FingerprintRidge", x, Y - 0.6, Y - 0.2 + q * 0.01, z, 40 - q * 7, (60, 200, 255) if q % 2 == 0 else (30, 40, 60),
             "Neon" if q % 2 == 0 else "SmoothPlastic", collide=False, shadow=False)


def _bioreactor_through(m, Y, L):
    """biotech finale: the train runs through a horizontal glass bioreactor full of glowing culture"""
    x, ry, z = m[0], m[1], m[2]
    cy, R = ry + 4.5, 15.0
    for q in range(16):
        a = math.radians(q * 22.5)
        box("ReactorGlass", (6.2, 0.6, L), (x + math.sin(a) * R, cy + math.cos(a) * R, z), (200, 235, 245), "Glass",
            transp=0.55, rot=(0, 0, -q * 22.5), collide=False, shadow=False)
    box("ReactorCulture", (20, 7, L), (x, ry - 6, z), (90, 230, 140), "Neon", transp=0.35, collide=False, shadow=False)
    for dz in (-L / 2, L / 2):
        _ring("ReactorCap", x, cy, z + dz, R + 1, 16, (6.8, 3, 4), (180, 188, 200), "Metal")
        for sx in (-1, 1):
            box("ReactorLeg", (3, cy - R - Y, 3), (x + sx * 10, (Y + cy - R) / 2, z + dz), (150, 158, 170), "Metal",
                collide=False)
    for q in range(10):
        sx = -1 if q % 2 else 1
        ball("Bubble", x + sx * rng.uniform(7, 11), ry - 1 + rng.uniform(0, 14), z + rng.uniform(-L / 2 + 6, L / 2 - 6), 2.4,
             (230, 255, 240), "Glass", transp=0.3, collide=False, shadow=False)
    for sx in (-1, 1):
        box("ReactorPipe", (2.4, 2.4, L + 20), (x + sx * 9, cy + R + 2, z), (170, 178, 190), "Metal", collide=False)


CENTREPIECE = {"micro": _phage, "biochem": _atp_synthase, "animal": _turtle, "plant": _sunflower,
               "forensic": _magnifier, "agri": _datepalm, "biotech": _bioreactor}


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
    if key == "forensic":
        _magnifier_through(t.marks[key + ":tower"], Y)
    elif key == "biotech":
        _bioreactor_through(t.marks[key + ":tower"], Y, FINALE[key][1] - 20)
    elif key != "molecular":
        tx, tz = t.marks[key + ":tower"][0], t.marks[key + ":tower"][2]
        CENTREPIECE[key](tx, tz, Y, col)   # v61: every valley's spiral circles its own giant (was one white tower)
    # mesa tunnel: rock walls and roof over the straight, a rocky mass on top
    i0, i1 = t.marks[key + ":mesa"]
    mx = t.pts[i0][0]
    my = t.pts[i0][1]
    z0, z1 = sorted((t.pts[i0][2], t.pts[i1 - 1][2]))
    # v61: each specialty bores through its own material (was the same sandstone mesa in all eight valleys)
    wc, wm, cc, cm, pc, tr = TUNNEL_STYLE.get(key, (ROCK, "Sandstone", (184, 152, 114), "Sandstone", (90, 76, 60), 0))
    rect("MesaWall", mx - 40, mx - 8, Y - 2, my + 30, z0 - 10, z1 + 10, wc, wm, transp=tr)
    rect("MesaWall", mx + 8, mx + 40, Y - 2, my + 30, z0 - 10, z1 + 10, wc, wm, transp=tr)
    rect("MesaRoof", mx - 40, mx + 40, my + 12, my + 30, z0 - 10, z1 + 10, wc, wm, transp=tr)
    rect("MesaCap", mx - 34, mx + 30, my + 30, my + 44, z0 + 10, z1 - 20, cc, cm)
    for z in (z0 - 10, z1 + 10):
        rect("MesaPortal", mx - 9, mx + 9, my + 10, my + 13, z - 1.5, z + 1.5, pc, "Neon" if key in ("forensic", "micro") else "Slate",
             collide=False)
        for s_ in (-1, 1):
            rect("MesaPortalPost", mx + s_ * 9 - 1, mx + s_ * 9 + 1, Y - 1, my + 13, z - 1.5, z + 1.5, pc, "Metal", collide=False)
    if key in ("animal", "agri"):
        TERRAIN.append((mx - 30, my + 40, (z0 + z1) / 2, 34, "Limestone"))
        TERRAIN.append((mx + 26, my + 36, z0 + 20, 26, "Limestone"))
    # v56 slot canyon: tall rock walls close on both sides of the track, chockstones wedged across the top
    c0, c1 = t.marks[key + ":canyon"]
    kx, ky = t.pts[c0][0], t.pts[c0][1]
    za, zb = sorted((t.pts[c0][2], t.pts[c1 - 1][2]))
    z = za - 20
    while z < zb + 20:
        L = rng.uniform(30, 50)
        for s_ in (-1, 1):
            h = rng.uniform(55, 95)
            inner = rng.uniform(9, 13)
            cols, mat, _ = WALLS[key]   # v62: the canyon is in the valley's own material too
            rect("CanyonWall", kx + s_ * inner, kx + s_ * (inner + 34), Y - 2, Y + h, z, z + L, cols[rng.randrange(3)],
                 mat)
        if rng.random() < 0.35:
            box("Chockstone", (30, rng.uniform(8, 14), rng.uniform(10, 16)), (kx, ky + rng.uniform(32, 46), z + L / 2),
                WALLS[key][0][1], WALLS[key][1], rot=(rng.uniform(-8, 8), rng.uniform(-10, 10), rng.uniform(-6, 6)),
                collide=False)
        z += L
    for s_ in (-1, 1):
        TERRAIN.append((kx + s_ * 36, Y + 70, (za + zb) / 2, 30, WALLS[key][2]))
    # river under the high bridge, the full width of the valley
    if key in RIVERS:
        b0, b1 = t.marks[key + ":bridge"]
        rx = t.pts[b0][0]
        TERRAIN_BLOCKS.append((rx, Y + 1.0, 0.0, 46.0, 4.0, CELLZ * 2 - 20, "Water"))
        for z in range(int(-CELLZ + 40), int(CELLZ - 40), 70):
            for s_ in (-1, 1):
                TERRAIN.append((rx + s_ * 30, Y - 4, z + rng.uniform(-15, 15), rng.uniform(9, 13), "Sand"))


PATCH = {   # ground patch colours per world: breaks the flat floor into readable zones
    "micro": [(184, 134, 72), (170, 120, 62)], "biochem": [(210, 200, 232), (232, 226, 246)],
    "animal": [(226, 200, 146), (196, 168, 116)], "plant": [(110, 170, 86), (84, 140, 66)],
    "molecular": [(32, 40, 78), (20, 26, 52)], "forensic": [(80, 82, 96), (60, 62, 72)],
    "agri": [(156, 118, 76), (120, 92, 58)], "biotech": [(214, 230, 236), (236, 244, 248)],
}


def _bigpalm(x, z, h=None):
    """a date palm at the valley's scale (CR._palm is 14-20 tall: invisible from the bridges)"""
    h = h or rng.uniform(40, 56)
    lean = rng.uniform(-6, 6)
    if _ENV and in_envelope((h, 3.2, 3.2), (x + CR.CART_OFFSET[0], GROUND_Y + h / 2 + CR.CART_OFFSET[1], z + CR.CART_OFFSET[2]), (0, 0, 90)):
        return   # v61: never a palm trunk in the riders' path
    vcyl("PalmTrunk", x, GROUND_Y, GROUND_Y + h, z, 3.2, (150, 118, 82), "Wood", collide=False)
    for q in range(3):
        vcyl("PalmRing", x, GROUND_Y + h * (0.3 + q * 0.22), GROUND_Y + h * (0.3 + q * 0.22) + 1, z, 3.6,
             (128, 98, 66), "Wood", collide=False)
    for a in range(9):
        yaw = a * 40.0 + lean
        L = 20.0
        dx = math.sin(math.radians(yaw)) * L * 0.42
        dz = math.cos(math.radians(yaw)) * L * 0.42
        box("Frond", (5, 0.5, L), (x + dx, GROUND_Y + h - 2.5, z + dz), (78, 148, 72), "Grass", collide=False,
            rot=(28, yaw, 0))
    ball("Dates", x, GROUND_Y + h - 3.5, z, 3.4, (170, 100, 40), "SmoothPlastic", collide=False)


def _tree(x, z, h, crown, col):
    vcyl("GiantTrunk", x, GROUND_Y, GROUND_Y + h, z, h * 0.09, (110, 80, 52), "Wood", collide=False)
    for q in range(3):
        a = q * 2.1
        ball("GiantCrown", x + math.cos(a) * crown * 0.3, GROUND_Y + h + q * 3, z + math.sin(a) * crown * 0.3,
             crown * (1 - q * 0.15), col, "Grass", collide=False)


def districts(t, clear, k, key):
    """v55: a second themed area in every valley + ground patches (cheap, big shapes that read from the train)"""
    Y = GROUND_Y
    for q in range(5):
        spot = place(clear, 0, 0, 0, 90)
        if spot:
            disc("GroundPatch", spot[0], Y + 0.12, spot[1], rng.uniform(160, 260), 0.2, PATCH[key][q % 2],
                 GROUND[key][1], collide=False, shadow=False)
    spot = place(clear, 0, 0, 0, 110)
    if not spot:
        return
    x, z = spot
    if key == "micro":
        # a streak plate: zig-zag lines of colonies thinning out (how microbiologists isolate one colony)
        for line in range(4):
            for q in range(10 - line * 2):
                px = x - 90 + line * 55 + (q % 2) * 18
                pz = z - 80 + q * 18
                d = 9 - line * 1.8
                disc("StreakColony", px, Y + 0.4, pz, d, 0.8, (250, 236, 200) if line < 3 else (240, 190, 90),
                     "SmoothPlastic", collide=False, shadow=False)
        label("🧫 تخطيط الطبق: نخفف البكتيريا عشان نعزل مستعمرة وحدة", x, Y + 10, z, x, z)
    elif key == "biochem":
        for q in range(9):
            a = q * math.pi * 2 / 9
            bx, bz = x + math.cos(a) * 60, z + math.sin(a) * 60
            vcyl("GiantBeaker", bx, Y, Y + 34, bz, 22, (220, 236, 245), "Glass", transp=0.5, collide=False)
            vcyl("BeakerLiquid", bx, Y + 0.5, Y + 18, bz, 20,
                 [(255, 90, 90), (255, 170, 80), (250, 230, 90), (120, 220, 110), (90, 190, 240), (120, 120, 240),
                  (180, 110, 230), (230, 110, 200), (200, 200, 200)][q], "Neon", transp=0.35, collide=False,
                 shadow=False)
        label("🧪 مقياس الأس الهيدروجيني: من حمضي (أحمر) إلى قاعدي (بنفسجي)", x, Y + 10, z, x, z)
    elif key == "animal":
        TERRAIN_BLOCKS.append((x, Y + 1.0, z, 120.0, 4.0, 90.0, "Water"))
        for q in range(16):   # soft sand banks round the pond
            a = q * math.pi * 2 / 16
            TERRAIN.append((x + math.cos(a) * 64, Y - 5, z + math.sin(a) * 50, rng.uniform(12, 16), "Sand"))
        for q in range(12):
            a = q * math.pi * 2 / 12
            _bigpalm(x + math.cos(a) * 86, z + math.sin(a) * 68)
        for q in range(4):
            CR._camel(x + rng.uniform(-40, 40), Y, z + 70 + rng.uniform(-6, 6))
        label("🐪 الواحة: الجمل يتحمّل العطش أيام لأنه يحافظ على الماي بجسمه", x, Y + 10, z, x, z)
    elif key == "plant":
        for q in range(12):
            tx, tz = x + rng.uniform(-100, 100), z + rng.uniform(-100, 100)
            if clear.ok(tx, tz, 20):
                _tree(tx, tz, rng.uniform(50, 90), rng.uniform(24, 34), rng.choice([(70, 150, 60), (90, 170, 70),
                                                                                       (60, 130, 55)]))
        label("🌳 الغابة: الأشجار تخزّن الكربون وتطلق الأكسجين", x, Y + 10, z, x, z)
    elif key == "molecular":
        for q in range(5):
            cx_, cz_ = x + rng.uniform(-80, 80), z + rng.uniform(-80, 80)
            col = [(255, 120, 200), (120, 220, 255), (180, 255, 140), (255, 210, 110), (190, 150, 255)][q]
            for s in range(14):   # an alpha helix: a coiled ribbon of beads
                a = s * 0.7
                ball("ProteinHelix", cx_ + math.cos(a) * 6, Y + 40 + s * 2.6, cz_ + math.sin(a) * 6, 5, col, "Neon",
                     collide=False, shadow=False)
        label("🧬 البروتينات تلتف كلوالب ألفا: شكلها يحدد وظيفتها", x, Y + 10, z, x, z)
    elif key == "forensic":
        for q in range(4):
            a = q * math.pi / 2 + 0.4
            px, pz = x + math.cos(a) * 70, z + math.sin(a) * 70
            vcyl("LightTower", px, Y, Y + 46, pz, 2.2, (60, 62, 70), "Metal", collide=False)
            box("Floodlight", (6, 3, 3), (px, Y + 47, pz), (255, 250, 220), "Neon", collide=False, shadow=False,
                light=(2, 70, (255, 246, 220)))
        for q in range(3):
            box("PoliceCar", (8, 3.4, 15), (x - 20 + q * 20, Y + 1.7, z + 30), (240, 240, 245), "SmoothPlastic",
                collide=False)
            box("PoliceStripe", (8.1, 1, 15.1), (x - 20 + q * 20, Y + 2.2, z + 30), (30, 60, 160), "SmoothPlastic",
                collide=False)
            box("Siren", (3, 0.8, 1.4), (x - 20 + q * 20, Y + 3.8, z + 30), (230, 50, 50) if q % 2 else (50, 90, 240),
                "Neon", collide=False, shadow=False)
        label("🚨 مسرح الجريمة: أول شي نحمي الأدلة من التلوث", x, Y + 10, z, x, z)
    elif key == "agri":
        for r_ in range(4):
            for c_ in range(6):
                _bigpalm(x - 80 + c_ * 32, z - 48 + r_ * 32)
        box("Barn", (40, 24, 30), (x + 110, Y + 12, z), (170, 60, 50), "WoodPlanks", collide=False)
        box("BarnRoof", (42, 4, 32), (x + 110, Y + 26, z), (90, 40, 34), "WoodPlanks", collide=False)
        label("🌴 مزرعة نخيل: النخلة الوحدة ممكن تعطي أكثر من 100 كيلو تمر بالسنة", x, Y + 10, z, x, z)
    elif key == "biotech":
        ox, oy, oz = CR.CART_OFFSET
        for q in range(3):
            if _ENV and in_envelope((56, 56, 56), (x - 70 + q * 70 + ox, Y + oy, z + oz), (0, 0, 0)):
                continue   # v62: never a dome across the riders' path
            ball("GreenDome", x - 70 + q * 70, Y, z, 56, (200, 240, 220), "Glass", transp=0.45, collide=False)
            disc("DomeGarden", x - 70 + q * 70, Y + 0.3, z, 50, 0.6, (90, 170, 80), "Grass", collide=False)
        for q in range(6):
            box("SolarPanel", (14, 0.4, 8), (x - 60 + q * 24, Y + 4, z + 60), (30, 50, 110), "Glass", rot=(-25, 0, 0),
                collide=False)
        label("🌱 بيوت محمية: نزرع نباتات معدّلة وراثياً تتحمّل الحر والملوحة", x, Y + 10, z, x, z)


CONCEPT_SPOTS = []   # (x, z, r) of the v62 theory sculptures: hills and later props keep away from them


def concepts(t, clear, k, key):
    """v62: four theory sculptures per valley (tools/cart_concepts62.py), beside the low parts of the ride so they
    are at eye level, facing the rails, each with one on-screen caption"""
    import cart_concepts62 as CC
    starts = [i for i, _ in t.sections] + [len(t.pts)]
    i0, i1 = starts[k - 1], starts[k]
    canyon = t.marks[key + ":canyon"]
    low = [i for i in range(i0 + 4, i1 - 4)
           if t.pts[i][1] < GROUND_Y + 30 and not any(f in ("t", "m") for f in t.pts[i][4])
           and min(abs(t.pts[i][0] - xr) for xr in t.ridges + [CELL[1]]) > 130   # not jammed against a ridge
           and not (canyon[0] - 12 <= i <= canyon[1] + 12)]                       # nor inside the slot canyon
    hi, lo = CELL
    plan = CC.CONCEPTS[key]
    for j, (fn, r, text) in enumerate(plan):
        if not low:
            break
        placed = False
        for shift in (0, 12, -12, 24, -24, 40, -40, 60, -60):
            ii = low[min(len(low) - 1, max(0, int(len(low) * (j + 0.5) / len(plan)) + shift))]
            p = t.pts[ii]
            fx, fz = math.sin(math.radians(p[3])), math.cos(math.radians(p[3]))
            rx, rz = fz, -fx
            for dist in (r + 26, r + 40, r + 56):
                for side in (1, -1):
                    x, z = p[0] + rx * side * dist, p[2] + rz * side * dist
                    if not (lo + r + 20 < x < hi - r - 20 and abs(z) < CELLZ - r - 30):
                        continue
                    if not clear.ok(x, z, r):
                        continue
                    if any(math.hypot(x - cx, z - cz) < r + cr + 12 for cx, cz, cr in CONCEPT_SPOTS):
                        continue
                    if any(math.hypot(x - lm[2], z - lm[3]) < r + 30 for lm in CR.LANDMARKS if lm[1] != "NOT PLACED"):
                        continue
                    nx, nz = p[0] - x, p[2] - z
                    nl = math.hypot(nx, nz) or 1.0
                    with G.Group("Concept_" + fn.__name__, "Model"):
                        fn(CC.F(x, z, GROUND_Y, (fx, fz), (nx / nl, nz / nl), key))
                    CONCEPT_SPOTS.append((x, z, r))
                    label(text, x, GROUND_Y + 10, z, x, z)
                    placed = True
                    break
                if placed:
                    break
            if placed:
                break
        if not placed:
            CR.LANDMARKS.append((fn.__name__, "NOT PLACED", 0, 0))


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
            districts(t, clear, k, key)
            rail_props(t, clear, k, key)
            concepts(t, clear, k, key)
            # v63: each valley's own world (skyline behind the walls, a designed ground, a themed midground)
            import cart_biomes63 as CB
            taken = [(x, z, r) for x, z, r in CONCEPT_SPOTS] + [(lm[2], lm[3], 40) for lm in CR.LANDMARKS
                                                             if lm[1] != "NOT PLACED"]
            with G.Group("Biome_" + key):
                CB.build(key, k, clear, hi, lo, GROUND_Y, taken)


def station_hall(t):
    sx, sy, sz = t.pts[0][:3]
    with G.Group("CartStationHall"):
        for xx in range(-36, 37, 18):
            for zz in (-40, 18):
                vcyl("StationColumn", sx + xx, sy - 2.4, sy + 44, sz + zz, 3.4, (230, 226, 216), "Marble")
        rect("StationRoofBeam", sx - 40, sx + 40, sy + 44, sy + 46, sz - 42, sz + 20, (200, 196, 186), "Concrete")
        rect("StationGlassRoof", sx - 38, sx + 38, sy + 46, sy + 46.6, sz - 40, sz + 18, (190, 220, 240), "Glass", transp=0.5,
             collide=False)
        # v56: one short station name; the controls are in the ؟ help button and the ride's own one-line hint
        sign("Departures", "🚆 المحطة الرئيسية | Grand Station", (sx, sy + 34, sz - 39.4), (30, 4, 0.6), "Back",
             color=(255, 220, 120), bg=(16, 18, 26))


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
                    TERRAIN.append((x, GROUND_Y - r * 0.35, s_ * (CELLZ - r * 0.25), r, WALLS[key][2]))
            x += tr.uniform(36, 52)
        for xr in (hi, lo):
            z = -CELLZ + 20
            while z < CELLZ - 20:
                if abs(z) > 46:
                    r = tr.uniform(24, 40)
                    xx = xr - r * 0.3 if xr == hi else xr + r * 0.3
                    if clear.ok(xx, z, r * 0.7):
                        TERRAIN.append((xx, GROUND_Y - r * 0.35, z, r, WALLS[key][2]))
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
                if clear.ok(x, z, r * 0.8) and not any(math.hypot(x - cx, z - cz) < r + cr for cx, cz, cr in CONCEPT_SPOTS):
                    TERRAIN.append((x, GROUND_Y - r * 0.6, z, r, mat))
                    placed += 1


# ====================================================================== data modules
TRACK = []
EDGES = []


VALLEY_PARTS = {}   # k -> [part record]: v56 the eight valleys stream on the client (CartScenery.client)
SERVER_KEEP = ("Portal|", "CartFinishPoint", "FinishDeck", "CartStart", "CartSpawnPoint")


import re as _re

# the ride's own pieces may sit in the rider envelope; everything else may not (v61 clearance rule)
TRACK_PART = _re.compile(r"^(Rail|TrackSpine|BridgeDeck|BridgeRail|GuideNeon|Tie|Tunnel|Portal|Spec|Gate|Caption)")
CLEARANCE = {"dropped": {}, "big": []}
_ENV = {}


def _env_hash(t):
    ox, oy, oz = CR.CART_OFFSET
    _ENV.clear()
    for q in t.pts:
        _ENV.setdefault((int((q[0] + ox) // 24), int((q[2] + oz) // 24)), []).append((q[0] + ox, q[1] + oy, q[2] + oz))


def in_envelope(size, pos, rot):
    """True when the part's (conservative) box reaches into the space a seated rider passes through:
    4.5 studs either side of the rails, from 0.6 to 9 studs above them"""
    rx, ry, rz = rot
    if rx == 0 and rz == 0:   # yaw only: exact footprint of the turned box
        c, sn = abs(math.cos(math.radians(ry))), abs(math.sin(math.radians(ry)))
        ext = ((size[0] * c + size[2] * sn) / 2, size[1] / 2, (size[0] * sn + size[2] * c) / 2)
    elif rx == 0 and ry == 0 and abs(abs(rz) - 90) < 1e-6:   # upright cylinder / column
        ext = (size[1] / 2, size[0] / 2, size[2] / 2)
    else:   # any rotation: axis-aligned extents of the rotated box (|R| * half size), Roblox Angles order X*Y*Z
        ax, ay, az = (math.radians(v) for v in rot)
        cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
        R = [[cy * cz, -cy * sz, sy],
             [cx * sz + sx * sy * cz, cx * cz - sx * sy * sz, -sx * cy],
             [sx * sz - cx * sy * cz, sx * cz + cx * sy * sz, cx * cy]]
        ext = tuple(sum(abs(R[i][j]) * size[j] / 2 for j in range(3)) for i in range(3))
    lo = [pos[i] - ext[i] for i in range(3)]
    hi = [pos[i] + ext[i] for i in range(3)]
    for cx in range(int((lo[0] - 5) // 24), int((hi[0] + 5) // 24) + 1):
        for cz in range(int((lo[2] - 5) // 24), int((hi[2] + 5) // 24) + 1):
            for (x, y, z) in _ENV.get((cx, cz), ()):
                if lo[0] - 4.5 <= x <= hi[0] + 4.5 and lo[2] - 4.5 <= z <= hi[2] + 4.5 and lo[1] <= y + 9 and hi[1] >= y + 0.6:
                    return True
    return False


TRACK_REF = [None]


def route_parts(t):
    TRACK_REF[0] = t
    """swap the low-level part writer: valley parts become records for Shared/CartScenery/V<k>; the station cell,
    portals and the finish deck stay real parts in the Map (the server needs them)."""
    base = C5._base_part
    ox = CR.CART_OFFSET[0]
    edges = list(t.ridges)

    def rec(name, size, pos, color, mat="Plastic", shape="Block", rot=(0, 0, 0), transp=0.0, collide=True, cls="Part",
            text=None, extra="", shadow=True, light=None):
        lx = pos[0] - ox
        k = 0
        for i, e in enumerate(edges):
            if lx <= e:
                k = i + 1
        if k == 0 or cls != "Part" or extra or name.startswith(SERVER_KEEP):
            return base(name, size, pos, color, mat, shape=shape, rot=rot, transp=transp, collide=collide, cls=cls,
                        text=text, extra=extra, shadow=shadow, light=light)
        if transp < 0.9 and not TRACK_PART.match(name) and in_envelope(size, pos, rot):
            if max(size) < 24:
                CLEARANCE["dropped"][name] = CLEARANCE["dropped"].get(name, 0) + 1
                return None
            CLEARANCE["big"].append((name, tuple(round(v) for v in pos)))
        VALLEY_PARTS.setdefault(k, []).append((name, size, pos, color, mat, shape, rot, transp, collide, text, shadow,
                                               light))

    _env_hash(t)
    C5._base_part = rec
    return base


def build():
    t = build_track()
    bad = CR.check(t)
    base = route_parts(t)
    try:
        with G.Group("CartRide"):
            draw_track(t)
            cells = valleys(t)
            scenery(t, cells)
            apply_captions(t)
            terrain_plan(t, cells)
            CR.stations(t)
            station_hall(t)
    finally:
        C5._base_part = base
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
    write_scenery(os.path.join(shared_dir, "CartScenery"))


def write_scenery(folder):
    """v56: one ModuleScript per valley returning a string, one line per part, fields separated by tabs:
    name shape(B/S/C) sx sy sz x y z rx ry rz(deg) colour(hex) material(enum value) transp flags(c=collide,s=shadow)
    face textHex bgHex bgT text light(b;range;hex). CartScenery.client builds a valley when the rider gets close."""
    import os
    os.makedirs(folder, exist_ok=True)
    for old in os.listdir(folder):
        if old.endswith(".luau"):
            os.remove(os.path.join(folder, old))
    shapes = {"Block": "B", "Ball": "S", "Cylinder": "C"}

    def hx(c):
        return "%02x%02x%02x" % (int(c[0]), int(c[1]), int(c[2]))

    total = 0
    for k, recs in sorted(VALLEY_PARTS.items()):
        lines = []
        for (name, size, pos, color, mat, shape, rot, transp, collide, text, shadow, light) in recs:
            f = [name.replace("\t", " "), shapes.get(shape, "B"), "%.2f" % size[0], "%.2f" % size[1], "%.2f" % size[2],
                 "%.2f" % pos[0], "%.2f" % pos[1], "%.2f" % pos[2], "%.1f" % rot[0], "%.1f" % rot[1], "%.1f" % rot[2],
                 hx(color), str(G.MAT[mat]), "%.2f" % transp, ("c" if collide else "") + ("s" if shadow else "")]
            if text:
                f += [text["face"], hx(text.get("color", (255, 255, 255))), hx(text.get("bg") or (0, 0, 0)),
                      "%.2f" % text.get("bg_t", 1.0), G.bidi_lines(text["text"]).replace("\n", "\\n").replace("\t", " ")]
            else:
                f += ["", "", "", "", ""]
            f.append("%.2f;%.1f;%s" % (light[0], light[1], hx(light[2])) if light else "")
            lines.append("\t".join(f))
        body = "\n".join(lines)
        assert "]==]" not in body
        with open(os.path.join(folder, "V%d.luau" % k), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("-- Generated by tools/cart_tour53.py: valley %d of the Specialties Cart Ride (%d parts), built on\n"
                     "-- the client by CartScenery.client when a rider is near. Do not edit by hand.\n" % (k, len(recs)))
            fh.write("return [==[\n%s\n]==]\n" % body)
        total += len(recs)
    print("cart underground points outside tunnels: %d" % underground_points(TRACK_REF[0]))
    print("cart clearance: dropped %s | big intruders %d %s" % (
        sorted(CLEARANCE["dropped"].items(), key=lambda kv: -kv[1])[:12], len(CLEARANCE["big"]),
        sorted({n for n, _ in CLEARANCE["big"]})))
    print("cart scenery: %d client-side parts in %d valleys (%s)" % (
        total, len(VALLEY_PARTS), ", ".join(str(len(v)) for _, v in sorted(VALLEY_PARTS.items()))))
