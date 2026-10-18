"""top-view renders of v9 areas (for layout review)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap9 as V  # noqa
import genmap2 as M2
import genmap5 as C5
import hq
from PIL import Image, ImageDraw

def render(name, x0, x1, z0, z1, S, ymax=1e9, ymin=-1e9):
    img = Image.new("RGB", (int((x1 - x0) * S), int((z1 - z0) * S)), (20, 20, 26))
    d = ImageDraw.Draw(img)
    items = [s for s in M2.scene if x0 - 50 < s[0] < x1 + 50 and z0 - 50 < s[2] < z1 + 50 and ymin <= s[1] <= ymax]
    for x, y, z, sx, sy, sz, col, tr, shp in sorted(items, key=lambda s: s[1] + s[4] / 2):
        if tr > 0.7 or sx > 900 or sz > 900:
            continue
        c = tuple(int(v) for v in col)
        px0, px1 = (x - sx / 2 - x0) * S, (x + sx / 2 - x0) * S
        pz0, pz1 = (z1 - (z + sz / 2)) * S, (z1 - (z - sz / 2)) * S
        if shp == "Ball" or shp == "Cylinder":
            d.ellipse([px0, pz0, max(px1, px0 + 1), max(pz1, pz0 + 1)], fill=c)
        else:
            d.rectangle([px0, pz0, max(px1, px0 + 1), max(pz1, pz0 + 1)], fill=c)
    img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", name)); print(name, img.size)

V.build_campus()
V.at(hq.HQ_OFFSET, hq.build)
ox, oy, oz = hq.HQ_OFFSET
render("hq_top.png", ox - 85, ox + 85, oz - 78, oz + 78, 5, ymax=oy + 30)
render("lobby_top.png", -95, 95, -185, -25, 4, ymax=20)
render("campus9_top.png", -260, 260, -340, 300, 1.6)
