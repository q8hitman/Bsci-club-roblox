import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap9 as V  # noqa
import genmap2 as M2, genmap3 as C3, genmap5 as C5, genmap as G
from PIL import Image, ImageDraw
G.hub = V.course_start
V.at(C5.COURSE_OFFSET, C3.build)
cps = {}
import re
# checkpoints from scene: find by matching parts is hard; use C3.ZONES_OUT
print(C3.ZONES_OUT[:3])
def render(name, z0, z1, S=3.0, x0=2920, x1=3080):
    img = Image.new("RGB", (int((x1 - x0) * S), int((z1 - z0) * S)), (20, 20, 26))
    d = ImageDraw.Draw(img)
    items = [s for s in M2.scene if x0 - 30 < s[0] < x1 + 30 and z0 - 30 < s[2] < z1 + 30]
    for x, y, z, sx, sy, sz, col, tr, shp in sorted(items, key=lambda s: s[1] + s[4] / 2):
        if tr > 0.8 or sx > 140 or sz > 300 or sy > 60:
            continue
        c = tuple(int(v) for v in col)
        px0, px1 = (x - sx / 2 - x0) * S, (x + sx / 2 - x0) * S
        pz0, pz1 = (z1 - (z + sz / 2)) * S, (z1 - (z - sz / 2)) * S
        (d.ellipse if shp in ("Ball", "Cylinder") else d.rectangle)([px0, pz0, max(px1, px0 + 1), max(pz1, pz0 + 1)], fill=c)
    img = img.rotate(90, expand=True)
    img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", name)); print(name, img.size)
a, b, g = C3.ZONES_OUT[0]
render("zone1_top.png", a, b, 1.6)
a, b, g = C3.ZONES_OUT[6]
render("zone7_top.png", a, b, 1.6)
