"""v61 Micro Racers layouts: each track is a list of pieces (straights and arcs) that closes exactly; the dense
centreline (one point every ~6 studs) is the single source for the server physics (RacerData.points), the bots,
the road ribbon, barriers, curbs and chevrons. Two straights per track are solved so the loop closes.
Heading convention = RacerMath: direction (sin h, cos h); a positive arc angle turns the kart LEFT on screen.
"""
import math

STEP = 6.0


def _walk(pieces, lengths):
    """returns dense points [(x, z, h)] and per-point piece index; '?n' straights take lengths[n]"""
    x, z, h = 0.0, 0.0, math.pi / 2   # start heading +X
    pts = [(x, z, h, 0)]
    for k, pc in enumerate(pieces):
        if pc[0] == "S":
            L = lengths[pc[1]] if isinstance(pc[1], str) else pc[1]
            n = max(1, int(round(L / STEP)))
            for i in range(1, n + 1):
                pts.append((x + math.sin(h) * L * i / n, z + math.cos(h) * L * i / n, h, k))
            x, z = pts[-1][0], pts[-1][1]
        else:
            ang, R = math.radians(pc[1]), pc[2]
            n = max(2, int(round(abs(ang) * R / STEP)))
            # centre on the turning side; heading increases for a positive angle
            sgn = 1 if ang > 0 else -1
            cx, cz = x - math.cos(h) * R * sgn, z + math.sin(h) * R * sgn
            for i in range(1, n + 1):
                hh = h + ang * i / n
                pts.append((cx + math.cos(hh) * R * sgn, cz - math.sin(hh) * R * sgn, hh, k))
            x, z, h = pts[-1][0], pts[-1][1], h + ang
    return pts


def solve(pieces):
    """find the two unknown straight lengths ('?a', '?b') that close the loop (linear in the lengths)"""
    names = sorted({pc[1] for pc in pieces if pc[0] == "S" and isinstance(pc[1], str)})
    assert len(names) == 2, names
    base = _walk(pieces, {names[0]: 0.0, names[1]: 0.0})
    ex, ez = base[-1][0], base[-1][1]
    cols = []
    for nm in names:
        p = _walk(pieces, {names[0]: 100.0 if nm == names[0] else 0.0, names[1]: 100.0 if nm == names[1] else 0.0})
        cols.append(((p[-1][0] - ex) / 100.0, (p[-1][1] - ez) / 100.0))
    (a, c), (b, d) = cols
    det = a * d - b * c
    la = (-ex * d + ez * b) / det
    lb = (-a * ez + c * ex) / det
    return {names[0]: la, names[1]: lb}


def build(pieces):
    lengths = solve(pieces)
    pts = _walk(pieces, lengths)
    if math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]) < 1.0:
        pts = pts[:-1]   # closed: the last point is the first
    return pts, lengths


def self_clearance(pts, window=30):
    """smallest distance between centreline points that are far apart along the track (no overlaps/crossings)"""
    n = len(pts)
    best = 1e9
    for i in range(0, n, 2):
        for j in range(i + window, n, 2):
            if n - (j - i) < window:
                continue
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            best = min(best, d)
    return best


def length(pts):
    return sum(math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) for i in range(len(pts)))


CLAMPED = []


def fillet(poly):
    """closed polygon [(x, z, radius)] -> dense centreline [(x, z, h)]: every corner is an arc of its radius,
    straights join the tangent points exactly (so the loop is closed and continuous by construction)"""
    n = len(poly)
    tans = []
    for i in range(n):
        px, pz, _ = poly[i - 1]
        vx, vz, R = poly[i]
        nx, nz, _ = poly[(i + 1) % n]
        ux, uz = vx - px, vz - pz
        lu = math.hypot(ux, uz)
        ux, uz = ux / lu, uz / lu
        wx, wz = nx - vx, nz - vz
        lw = math.hypot(wx, wz)
        wx, wz = wx / lw, wz / lw
        h1, h2 = math.atan2(ux, uz), math.atan2(wx, wz)
        turn = (h2 - h1 + math.pi) % (2 * math.pi) - math.pi
        t = R * math.tan(abs(turn) / 2)
        tmax = min(lu, lw) / 2 - 1
        if t > tmax:   # the radius does not fit between the neighbouring corners: use the largest that does
            R = tmax / math.tan(abs(turn) / 2)
            t = tmax
            CLAMPED.append((i, round(R)))
        tans.append(((vx - ux * t, vz - uz * t), h1, turn, R))
    pts = []
    for i in range(n):
        (sx, sz), h1, turn, R = tans[i]
        # arc from the in-tangent point, turning by `turn`
        sgn = 1 if turn > 0 else -1
        # forward along (sin h, cos h): the centre sits at +R*sgn*(cos h, -sin h) from the tangent point
        cx, cz = sx + math.cos(h1) * R * sgn, sz - math.sin(h1) * R * sgn
        m = max(2, int(round(abs(turn) * R / STEP)))
        for k in range(0, m + 1):
            hh = h1 + turn * k / m
            pts.append((cx - math.cos(hh) * R * sgn, cz + math.sin(hh) * R * sgn, hh))
        # straight to the next corner's in-tangent point
        ex, ez = pts[-1][0], pts[-1][1]
        (tx, tz), _, _, _ = tans[(i + 1) % n]
        L = math.hypot(tx - ex, tz - ez)
        q = max(1, int(round(L / STEP)))
        hh = math.atan2(tx - ex, tz - ez)
        for k in range(1, q):
            pts.append((ex + (tx - ex) * k / q, ez + (tz - ez) * k / q, hh))
    return pts


# ---- layouts: corner points (x, z, fillet radius), driven in this order ------------------------------------------
POLYS = {
    # beginner "Cell Circuit": long start straight, two big drift sweepers, a wiggle, an inward hairpin notch
    "cell": [(-200, -170, 60), (200, -170, 60), (300, -90, 70), (250, 10, 50), (310, 90, 45), (230, 180, 55),
             (60, 140, 40), (0, 40, 30), (-80, 150, 40), (-260, 170, 60), (-310, 60, 70), (-280, -90, 60)],
    # advanced "Helix": zig-zag technical sections, tighter radii
    "helix": [(-220, -180, 50), (120, -180, 45), (180, -120, 35), (100, -40, 30), (220, 30, 35), (160, 170, 45),
              (40, 110, 30), (-40, 190, 35), (-200, 150, 45), (-120, 40, 30), (-260, -20, 40), (-280, -140, 50)],
}

if __name__ == "__main__":
    for name, poly in POLYS.items():
        pts = fillet(poly)
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        print("clamped corners (index, radius):", CLAMPED); CLAMPED.clear()
        print("%s: length %.0f (lap ~%.0f s at 40), points %d, extent x %.0f..%.0f z %.0f..%.0f, self clearance %.1f"
              % (name, length(pts), length(pts) / 40, len(pts), min(xs), max(xs), min(zs), max(zs), self_clearance(pts)))
