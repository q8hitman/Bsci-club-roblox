"""v34: top-down render of the built campus straight from Map.rbxmx (rotated boxes drawn as polygons),
with the plan overlay (A/B/C labels). Usage: python tools/topview34.py <Map.rbxmx> <out.png> [plain]"""
import re
import sys

from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
plain = len(sys.argv) > 3
x0, x1, z0, z1 = -180.0, 200.0, -260.0, 290.0
S = 3.0
W, H = int((x1 - x0) * S), int((z1 - z0) * S)
img = Image.new("RGB", (W, H), (214, 196, 160))
d = ImageDraw.Draw(img)
xml = open(src, encoding="utf-8").read()
pat = re.compile(r'<Item class="(Part|SpawnLocation|WedgePart)"[^>]*><Properties><string name="Name">([^<]*)</string>'
                 r'<CoordinateFrame name="CFrame"><X>([-\d.]+)</X><Y>([-\d.]+)</Y><Z>([-\d.]+)</Z>'
                 r'<R00>([-\d.]+)</R00><R01>([-\d.]+)</R01><R02>([-\d.]+)</R02><R10>([-\d.]+)</R10><R11>([-\d.]+)</R11>'
                 r'<R12>([-\d.]+)</R12><R20>([-\d.]+)</R20><R21>([-\d.]+)</R21><R22>([-\d.]+)</R22></CoordinateFrame>'
                 r'<Vector3 name="size"><X>([-\d.]+)</X><Y>([-\d.]+)</Y><Z>([-\d.]+)</Z></Vector3>'
                 r'<Color3uint8 name="Color3uint8">(\d+)</Color3uint8>.*?<float name="Transparency">([-\d.]+)</float>', re.S)
items = []
for m in pat.finditer(xml):
    g = m.groups()
    x, y, z = float(g[2]), float(g[3]), float(g[4])
    if not (x0 - 50 < x < x1 + 50 and z0 - 50 < z < z1 + 50 and -5 < y < 140):
        continue
    r = [float(v) for v in g[5:14]]
    sx, sy, sz = float(g[14]), float(g[15]), float(g[16])
    if sx > 600 or sz > 600 or float(g[18]) > 0.7:
        continue
    c = int(g[17])
    col = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    # top y of the rotated box
    ty = y + abs(r[3]) * sx / 2 + abs(r[4]) * sy / 2 + abs(r[5]) * sz / 2
    corners = []
    for ex, ez in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        wx = x + r[0] * ex * sx / 2 + r[2] * ez * sz / 2
        wz = z + r[6] * ex * sx / 2 + r[8] * ez * sz / 2
        corners.append(((wx - x0) * S, (z1 - wz) * S))
    items.append((ty, corners, col))
items.sort(key=lambda t: t[0])
for ty, corners, col in items:
    shade = min(1.0, 0.75 + ty / 400)
    d.polygon(corners, fill=tuple(int(v * shade) for v in col))
if not plain:
    try:
        f = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        f = ImageFont.load_default()

    def P(x, z):
        return ((x - x0) * S, (z1 - z) * S)

    def label(x, z, t, col=(20, 20, 20)):
        px, pz = P(x, z)
        tw = d.textlength(t, font=f)
        d.rectangle([px - 4, pz - 3, px + tw + 4, pz + 25], fill=(255, 255, 255))
        d.text((px, pz), t, fill=col, font=f)

    label(-60, -220, "A  SOUTH building (plaza + 114 stone + main entrance)", (120, 30, 30))
    label(-40, 140, "A  NORTH building (unchanged)", (30, 30, 120))
    label(-70, 20, "B  triangle ring (south complex)")
    label(-170, 104, "A  garden strip: winding paths")
    label(30, 82, "A  white faceted roof (gym)")
    label(-110, 70, "A  mound + curved path")
    label(-60, 123, "A  straight band")
    label(14, 134, "connection -> north")
    label(-178, -150, "C  BSC office (mezzanine, unverified)", (24, 80, 56))
    label(36, 40, "C  Pick")
    d.rectangle([*P(60, -128), *P(92, -162)], outline=(24, 160, 90), width=4)
img.save(out)
print("saved", out, img.size, len(items))
