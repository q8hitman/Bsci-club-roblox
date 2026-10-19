"""v9: the club HQ is the lobby (own world, players spawn there), harder puzzle parkour, the Cart Ride,
a furnished campus with cats along the garden walk, and the Cell Train.
Run: python tools/genmap9.py kuwait-parkour/src/map/Map.rbxmx
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap8 as G8  # noqa: E402  (zones, environments, cell train world, previous mechanics)
import genmap7 as G7  # noqa: E402
import genmap5 as C5  # noqa: E402
import genmap3 as C3  # noqa: E402
import genmap2 as M2  # noqa: E402
import genmap as G  # noqa: E402
import parkour9  # noqa: E402
import campus9  # noqa: E402
import hq  # noqa: E402
import cartride  # noqa: E402
import celltrain  # noqa: E402
import hq_beauty  # noqa: E402
import hq_fill  # noqa: E402
import collectibles9  # noqa: E402
import extras10  # noqa: E402
import island11  # noqa: E402
import ku_science  # noqa: E402  (v32: real-world College of Science likeness)
import ku_science33  # noqa: E402  (v33: satellite corrections)
import ku_science34  # noqa: E402  (v34: south complex + garden walk from the aerial view)
import north_campus44  # noqa: E402  (v44: modular north prototype; photo16/17 room types)
import museum46  # noqa: E402  (v46: fictional additive museum pavilion)

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect

# ---- new stage lists (same level counts per zone as before, so progress/saves stay valid)
parkour9.register()
for i, seq in enumerate(parkour9.SEQS):
    z = G8.ZONES[i]
    assert len(seq) == len(z[4]), (z[1], len(seq), len(z[4]))
    G8.ZONES[i] = (z[0], z[1], z[2], z[3], seq)
M2.SEQ[:] = [z[4] for z in G8.ZONES]
assert sum(len(s) for s in M2.SEQ) == 100


def course_start():
    """bright start deck of the obby; the exit portal goes back to the club HQ"""
    with G.Group("CourseStart"):
        rect("StartDeck", -32, 32, -1, 0, -66, -8, (234, 230, 220), "Marble")
        for zz in (-66, -8):
            rect("DeckEdge", -32, 32, 0, 0.08, zz - 0.4, zz + 0.4, (90, 230, 160), "Neon", collide=False)
        for x in (-28, 28):
            for z in (-62, -12):
                vcyl("DeckLeg", x, -24, -1, z, 3, (226, 220, 206), "Concrete", collide=False)
        G.part("Checkpoint_0", (12, 1, 12), (0, 0.5, -26), (64, 140, 108), "SmoothPlastic",
               text=dict(face="Top", text="START", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
        sign("StartTitle", "100 Level Parkour\nابدأ من هنا ↑", (0, 13, -62), (30, 7, 0.6), "Back", bg=(24, 70, 48))
        names = "\n".join("%d) %s" % (i + 1, z[0]) for i, z in enumerate(G8.ZONES))
        sign("ZoneList", names, (-31.4, 9, -40), (0.5, 15, 18), "Right", bg=(30, 40, 56))
        sign("Tips", "نصايح:\n• السقوط يرجّعك لآخر نقطة\n• كل 5 مراحل سؤال\n• الألغاز: اقرأ اللوحة قبل لا تضغط\n• الأبواب: الجواب الغلط يطيّحك",
             (31.4, 9, -40), (0.5, 13, 18), "Left", bg=(30, 40, 56))
        for s_ in (-1, 1):
            box("ExitPost", (1.2, 14, 1.2), (s_ * 7, 7, -57), (60, 64, 74), "SmoothPlastic", collide=False)
        G.part("Portal|HQ", (12.6, 12.5, 0.5), (0, 6.4, -57), (120, 255, 200), "Neon", transp=0.5, collide=False, shadow=False)
        sign("BackSign", "العودة لمقر النادي\nBack to the Club HQ", (0, 15.6, -57.3), (15, 3.2, 0.5), "Back", bg=(24, 80, 56))
        for x in (-22, 22):
            C3.planter(x, 0, -14, 10, 4)
            C3.lamp_post(x, 0, -50, 10)


def build_campus():
    ku_science.install()   # v32: hooks the old south building (bronze screen, entrance bay, plaza stone)
    ku_science34.pre()       # v34: smaller triangle, silver facade palette (before the v33 hooks read them)
    ku_science33.install()   # v33: ring vs Red Corridor, kiosk moves, wing doorways, varied trees
    ku_science34.install()   # v34: mutes the old garden walk, column joints, club office window/door
    with G.Group("Campus"):
        C5.outdoors()
        C5.south_building()
        G7.department_offices()
        G7.lounges()
        G7.building_details()
        celltrain.train_station()
        campus9.build()
        ku_science.build()
        ku_science33.build()
        ku_science34.build()
        C5._off[2] = C5.NB_SHIFT
        north_campus44.build()
        C5._off[2] = 0.0
        museum46.build()


def at(offset, fn):
    C5._off[0], C5._off[1], C5._off[2] = offset
    try:
        return fn()
    finally:
        C5._off[0], C5._off[1], C5._off[2] = 0.0, 0.0, 0.0


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    build_campus()
    at(hq.HQ_OFFSET, hq.build)
    at(hq.HQ_OFFSET, hq_beauty.build)
    at(hq.HQ_OFFSET, hq_fill.build)
    at(C5.COURSE_OFFSET, hq_beauty.start_deck)
    G.hub = course_start
    at(C5.COURSE_OFFSET, C3.build)
    at(celltrain.CELL_OFFSET, celltrain.cell_world)
    n_cart, cart_bad = at(cartride.CART_OFFSET, cartride.build)
    collectibles9.build(G8.zone_starts())   # absolute coordinates (needs the course already written)
    extras10.build()   # virus arena, graduation stage, secret roof, daily board (absolute coordinates)
    island11.build()   # BSC Island gameplay layer, exam hall, arcade (absolute coordinates)
    gap, rise, bad, n = M2.validate()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    size = 0
    with open(out_path, "w", encoding="utf-8") as f:   # stream: the joined string can exhaust memory
        f.write('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
                '<string name="Name">Map</string></Properties>' % G.rid())
        for chunk in G.buf:
            f.write(chunk)
            size += len(chunk)
        f.write("</Item></roblox>")
    G8.write_zones_module(os.path.join(os.path.dirname(os.path.dirname(out_path)), "shared", "Zones.luau"))
    cartride.write_rooms_module(cartride.ROOMS, os.path.join(os.path.dirname(os.path.dirname(out_path)), "shared", "CartRooms.luau"))
    print("parts:", G.nparts[0], "| steps:", n, "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad),
          "| KB:", size // 1024, "| zone starts:", G8.zone_starts(), "| cart points:", n_cart, "clashes:", cart_bad)
    for v in bad[:8]:
        print("  BAD", v)
