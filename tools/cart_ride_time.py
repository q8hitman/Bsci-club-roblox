"""Ride duration of the Specialties Cart Ride at each cruise step, using the same speed model as CartRide.client
(bend comfort limit v^2/R <= 70 looked up 12/24/40 studs ahead, downhill +45% / uphill -20%, accel 14, decel 20).
Run: python tools/cart_ride_time.py"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import cart_tour53 as T  # noqa: E402

LATERAL, ACCEL, DECEL, DT = 70.0, 14.0, 20.0, 1 / 30


def main():
    t = T.build_track()
    pts = [p[:3] for p in t.pts]
    dist = [0.0]
    for a, b in zip(pts, pts[1:]):
        dist.append(dist[-1] + math.dist(a, b))
    total = dist[-1]

    def sample(d):
        lo, hi = 0, len(pts) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if dist[mid] < d:
                lo = mid
            else:
                hi = mid
        a, b = pts[lo], pts[hi]
        f = (d - dist[lo]) / max(dist[hi] - dist[lo], 1e-3)
        return [a[i] + (b[i] - a[i]) * f for i in range(3)]

    def direction(d):
        a, b = sample(max(d - 3, 0)), sample(min(d + 3, total))
        v = [b[i] - a[i] for i in range(3)]
        n = math.sqrt(sum(c * c for c in v)) or 1
        return [c / n for c in v]

    def bend_limit(d):
        d0 = direction(d)
        lim = math.inf
        for ahead in (12, 24, 40):
            d1 = direction(min(d + ahead, total))
            ang = math.acos(max(-1, min(1, sum(x * y for x, y in zip(d0, d1)))))
            if ang > 0.05:
                lim = min(lim, math.sqrt(LATERAL * ahead / ang))
        return max(lim, 15)

    sections = [i for i, _ in t.sections]
    print("track %.0f studs, %d points, %d stages" % (total, len(pts), len(sections)))
    for cruise in (35, 45, 60, 90, 120):
        d = v = time = 0.0
        while d < total - 0.5:
            target = cruise * (1 + max(-0.2, min(0.45, -direction(d)[1] * 3)))
            target = min(target, bend_limit(d), math.sqrt(2 * DECEL * max(total - d, 0)))
            v = min(target, v + ACCEL * DT) if v < target else max(target, v - DECEL * DT)
            d += max(v, 0.5) * DT
            time += DT
        print("cruise %3d studs/s -> %5.1f min (avg %.0f studs/s)" % (cruise, time / 60, total / time))


if __name__ == "__main__":
    main()
