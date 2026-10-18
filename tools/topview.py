import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap6 as G6  # noqa: E402
import genmap2 as M2  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

G6.C5.build_campus()
S = 2.6
x0, x1, z0, z1 = -180, 220, -340, 300
img = Image.new("RGB", (int((x1 - x0) * S), int((z1 - z0) * S)), (214, 196, 160))
d = ImageDraw.Draw(img)
items = [s for s in M2.scene if abs(s[3]) < 600]
for x, y, z, sx, sy, sz, col, tr, shp in sorted(items, key=lambda s: s[1] + s[4] / 2):
    if tr > 0.6 or sx > 700 or sz > 700 or y + sy / 2 < -0.5:
        continue
    c = tuple(int(v) for v in col)
    px0, px1 = (x - sx / 2 - x0) * S, (x + sx / 2 - x0) * S
    pz0, pz1 = (z1 - (z + sz / 2)) * S, (z1 - (z - sz / 2)) * S
    d.rectangle([px0, pz0, max(px1, px0 + 1), max(pz1, pz0 + 1)], fill=c)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "campus_top.png")
img.save(out)
print("saved", os.path.abspath(out), img.size)
