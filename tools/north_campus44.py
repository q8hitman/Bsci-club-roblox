"""Editable north-building kit. Visual references A; all module placements are C.

Coordinates are the inherited north local space (C5.NB_SHIFT is applied by caller).
No real room numbers, new stair positions, elevators, remotes or gameplay scripts.
"""
import math
from xml.sax.saxutils import escape

import genmap as G
import genmap5 as C5

STONE = (226, 221, 208)
WHITE = (241, 241, 235)
DARK = (44, 51, 55)
METAL = (143, 153, 155)
GLASS = (168, 201, 204)
WOOD = (198, 174, 132)
GREEN = (180, 193, 91)
CARPET = (72, 76, 75)
LEVELS = (0, 24, 40, 56)
CORES = ((-80, -60, 120, 148), (80, 100, 120, 148))
ATRIUM = (-14, 28, 40, 102)
ROOMS = {
    'FlatClassroom_Photo17': (-79.5, -20, 36, 88),
    'TieredLecture_Photo16': (38, 99.5, 36, 96),
}
REFERENCE = 'https://www.instagram.com/p/DCOOAtEtLBF/'


def evidence(details, source=REFERENCE):
    G.buf.append('<Item class="StringValue" referent="%s"><Properties>'
                 '<string name="Name">Evidence</string><string name="Value">%s</string>'
                 '</Properties></Item>' % (G.rid(), escape(details + '; placement=C; source=' + source)))


def box(name, size, pos, colour=WHITE, material='SmoothPlastic', collide=True, **kw):
    extra = kw.pop('extra', '')
    extra += '<bool name="CanTouch">false</bool>'
    if not collide:
        extra += '<bool name="CanQuery">false</bool>'
    G.box(name, size, pos, colour, material, collide=collide, extra=extra, **kw)


def rect(name, x0, x1, y0, y1, z0, z1, colour=WHITE, material='SmoothPlastic', **kw):
    box(name, (x1-x0, y1-y0, z1-z0), ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2), colour, material, **kw)


def plaque(name, text, pos, size, face='Front', colour=DARK):
    box(name, size, pos, colour, collide=False,
        text=dict(face=face, text=text, color=WHITE, bg=colour, bg_t=0))


def chair(x, y, z, colour, yaw=0, writing=False):
    a = math.radians(yaw)
    dx, dz = math.sin(a), math.cos(a)
    G.part('SeatBase', (2.8, .55, 2.8), (x, y+1.9, z), colour, 'SmoothPlastic', cls='Seat',
           collide=True, rot=(0, yaw, 0), extra='<bool name="CanTouch">true</bool>')
    box('SeatBack', (2.8, 2.5, .5), (x+dx*1.25, y+3.2, z+dz*1.25), colour, 'SmoothPlastic',
        collide=False, rot=(0, yaw, 0))
    box('SeatSupport', (1.2, 1.65, 1.6), (x, y+.82, z), DARK, 'Metal', collide=False, shadow=False)
    if writing:
        box('WritingPad', (1.15, .18, 1.8), (x+1.6, y+2.9, z-.35), WOOD, 'Wood', collide=False,
            rot=(0, yaw, 0), shadow=False)


def ceiling(x0, x1, z0, z1, y):
    # Light ceiling grid and long linear fittings, rather than one Instance per tile.
    for x in range(int(x0)+8, int(x1), 12):
        box('CeilingSeam', (.07, .05, z1-z0), (x, y-.05, (z0+z1)/2), METAL, collide=False, shadow=False)
    for z in range(int(z0)+7, int(z1), 10):
        box('CeilingSeam', (x1-x0, .05, .07), ((x0+x1)/2, y-.05, z), METAL, collide=False, shadow=False)
    for x in (x0+(x1-x0)*.28, x0+(x1-x0)*.72):
        for z in (z0+12, z1-12):
            box('LinearFitting', (1.1, .15, 8), (x, y-.22, z), (250, 245, 221), 'Neon',
                collide=False, shadow=False)
    box('Projector', (2.4, .8, 1.8), ((x0+x1)/2, y-1, (z0+z1)/2), DARK, collide=False)
    box('ProjectorStem', (.25, 1, .25), ((x0+x1)/2, y-.5, (z0+z1)/2), METAL, collide=False)
    for z in (z0+14, z1-14):
        box('RoomLight', (.2, .2, .2), ((x0+x1)/2, y-2, z), WHITE, collide=False, transp=1,
                light=(1.4, 48, (255, 249, 234)))


def envelope():
    with G.Group('Envelope'):
        evidence('visual=A/B: curtain wall, vertical fins, limestone/terracotta; dimensions=C')
        C5.glass_x(-80, 100, 20, 0, 24, 9, gaps=[(-8, 8), (12, 28)])
        C5.revolving_door(0, 20)
        C5.revolving_door(20, 20)
        for xa, xb, ya, yb in ((-80, -50, 24.5, 63), (-30, 100, 24.5, 63), (-50, -30, 36.5, 63)):
            rect('UpperCurtainWall', xa, xb, ya, yb, 19.75, 20.25, GLASS, 'Glass', transp=.42, collide=False)
        for x in range(-80, 101, 10):
            if -50 <= x <= -30:
                box('FacadeFin', (.65, 26, 3.6), (x, 50, 18.5), METAL, 'Metal', collide=False)
            else:
                box('FacadeFin', (.65, 38, 3.6), (x, 44, 18.5), METAL, 'Metal', collide=False)
        for xa, xb in ((-80, -50), (-30, 100)):
            rect('FacadeBand', xa, xb, 23.5, 24.3, 19, 21, STONE, 'Limestone', collide=False)
        for y in (40, 56, 64):
            rect('FacadeBand', -80, 100, y-.5, y+.3, 19, 21, STONE, 'Limestone', collide=False)
        for x in (-80, 100):
            C5.glass_z(20, 150, x, 0, 24, 10)
            for y in (24, 40, 56):
                top = min(y+16, 64)
                rect('LimestoneSpandrel', x-.7, x+.7, y, y+4, 20, 150, STONE, 'Limestone')
                rect('RibbonWindow', x-.3, x+.3, y+4, top-.7, 20, 150, GLASS, 'Glass', transp=.35)
                for z in range(20, 151, 10):
                    box('WindowFrame', (1.1, top-y-4, .3), (x, (y+4+top)/2, z), METAL, 'Metal', collide=False)
        rect('RearWall', -80, 100, 0, 64, 149.5, 150.5, STONE, 'Limestone')
        for y in (8, 32, 48, 60):
            rect('RearWindow', -56, 76, y, y+3, 149.1, 149.4, GLASS, 'Glass', transp=.35, collide=False)
        with G.Group('FacetedGlazing_Photo01'):
            evidence('visual=A: photo01 paired angled glazed masses; orientation, scale and attachment=C')
            for cx in (-42, 62):
                box('AngledGlass', (62, 36, .6), (cx, 44, 154.5), (132, 183, 192), 'Glass',
                    transp=.23, collide=False, rot=(-6, 0, 0))
                for x in (cx-32, cx+32):
                    box('AngledStonePier', (3, 41, 3.4), (x, 44, 154.5), STONE, 'Limestone',
                        collide=False, rot=(-6, 0, 0))
                for dx in range(-24, 25, 8):
                    box('GlazingMullion', (.2, 36, .5), (cx+dx, 44, 154.9), METAL, 'Metal',
                        collide=False, rot=(-6, 0, 0), shadow=False)
                for y in (26, 38, 50, 62):
                    z = 154.9-math.sin(math.radians(6))*(y-44)
                    box('GlazingTransom', (62, .22, .5), (cx, y, z), METAL, 'Metal',
                        collide=False, rot=(-6, 0, 0), shadow=False)
        # Two bays leave the inherited first-floor red bridge entrance unobstructed.
        for xa, xb in ((-80, -52), (-28, 100)):
            rect('EntryCanopy', xa, xb, 21.7, 22.3, 13, 20, WHITE, 'Concrete')
        for x in (-72, 44, 88):
            C5.column(x, 15, 0, 21.7, 3.2, STONE, 'Concrete')
        plaque('NorthName', 'المبنى الشمالي\nNorth Building', (52, 16.2, 19.3), (34, 4.4, .4))
        plaque('PrototypeNotice', 'نسخة تطويرية\nالتوزيع الداخلي تقديري', (-16, 7, 23), (12, 4, .3), 'Back')


def floors():
    with G.Group('Floors'):
        evidence('geometry=C: inherited footprint and levels, modular atrium cutout')
        rect('GroundFloor', -80, 100, -1, .3, 20, 150, STONE, 'Marble')
        for y in LEVELS[1:]:
            C5.floor_slab(y, -80, 100, 20, 150, [ATRIUM, *CORES], STONE, 'Marble', name=f'Level{y}')
        # Distinct name avoids campus9's legacy north-skylight cutout hook.
        C5.floor_slab(64, -80, 100, 20, 150, [ATRIUM], STONE, 'Concrete', name='ModularRoof')
        rect('Skylight', ATRIUM[0], ATRIUM[1], 64.1, 64.4, ATRIUM[2], ATRIUM[3],
             (211, 230, 230), 'Glass', transp=.35, collide=False)


def atrium():
    with G.Group('Atrium'):
        evidence('visual=A/B: skylit tall atrium, silver columns, coloured study islands; plan=C')
        for x in (-16, 30):
            for z in (46, 94):
                C5.steel_drum(x, z, 0, 62, 3.6)
        for y in LEVELS[1:]:
            for x in (ATRIUM[0], ATRIUM[1]):
                rect('AtriumGuardGlass', x-.15, x+.15, y+.3, y+3.8, ATRIUM[2], ATRIUM[3],
                     GLASS, 'Glass', transp=.3)
                box('AtriumHandrail', (.55, .45, ATRIUM[3]-ATRIUM[2]), (x, y+4, (ATRIUM[2]+ATRIUM[3])/2),
                    DARK, 'Metal', collide=False)
            for z in (ATRIUM[2], ATRIUM[3]):
                rect('AtriumGuardGlass', ATRIUM[0], ATRIUM[1], y+.3, y+3.8, z-.15, z+.15,
                     GLASS, 'Glass', transp=.3)
                box('AtriumHandrail', (ATRIUM[1]-ATRIUM[0], .45, .55), ((ATRIUM[0]+ATRIUM[1])/2, y+4, z),
                    DARK, 'Metal', collide=False)
        for x in (-5, 19):
            box('SkylightBeam', (.6, .8, 62), (x, 63.6, 71), WHITE, 'Metal', collide=False)
        for z in (48, 71, 94):
            box('SkylightBeam', (42, .8, .6), (7, 63.6, z), WHITE, 'Metal', collide=False)
        for za, zb in ((40, 71), (71, 102)):
            for xa, xb in ((-14, 28), (28, -14)):
                length = math.hypot(xb-xa, zb-za)
                box('LatticeBeam_Photo15', (.5, .6, length), ((xa+xb)/2, 63.1, (za+zb)/2),
                    WHITE, 'Metal', collide=False, rot=(0, math.degrees(math.atan2(xb-xa, zb-za)), 0))
        for z in (52, 92):
            box('AtriumLight', (.2, .2, .2), (7, 18, z), WHITE, collide=False, transp=1,
                light=(1.5, 48, (247, 248, 244)))
        for z in (35, 108):
            rect('WayfindingInlay', -5, 15, .01, .03, z-1, z+1, (159, 165, 145), 'Marble', collide=False)
        plaque('GroundWayfinding', 'قاعات وجلسات', (37.4, 8, 57), (.35, 2.5, 12), 'Left')
        for x, z, colour in ((-58, 112, (62, 118, 110)), (51, 112, (110, 147, 81))):
            box('StudyBoothSeat', (10, 1, 3.5), (x, 2, z), colour, 'Fabric', collide=False)
            box('StudyBoothBack', (10, 5, .6), (x, 4, z+1.6), colour, 'Fabric', collide=False)
            box('StudyTable', (7, .4, 4), (x, 3, z-4), WOOD, 'Wood', collide=False)


def circulation():
    with G.Group('Circulation'):
        evidence('placement=C: keep both inherited stair footprints; not a verified real stair plan')
        for core in CORES:
            C5.stair_core(*core, list(LEVELS))
        for y in LEVELS:
            for x in (-66, 86):
                plaque('LevelSign', ('الأرضي' if y == 0 else 'الطابق '+str(LEVELS.index(y))),
                       (x, y+5, 119), (9, 2.4, .3))
        # Keep the bridge route open at x=-50..-30, z=20, floor24.
        plaque('BridgeDirection', 'الممر الأحمر\nإلى الجنوبي', (-40, 34.4, 21.2), (16, 2.6, .3), 'Back')


def flat_classroom():
    x0, x1, z0, z1 = ROOMS['FlatClassroom_Photo17']
    with G.Group('FlatClassroom_Photo17'):
        evidence('visual=A: photo17 flat dark floor, long pale desks, separate dark chairs, side glazing, whiteboards')
        rect('RoomFloor', x0, x1, .32, .4, z0, z1, CARPET, 'SmoothPlastic')
        C5.wall_x(x0, x1, z0, 0, 22, WHITE, 'SmoothPlastic')
        C5.wall_x(x0, x1, z1, 0, 22, WHITE, 'SmoothPlastic')
        C5.wall_z(z0, z1, x1, 0, 12, WHITE, 'SmoothPlastic', gaps=[(43, 53)])
        rect('CorridorClerestory', x1-.2, x1+.2, 12, 22, z0, z1, GLASS, 'Glass', transp=.3)
        rect('DoorHeader', x1-.5, x1+.5, 10, 12, 43, 53, WHITE)
        for z in (43, 53):
            box('DoorJamb', (1.1, 10, .4), (x1, 5, z), METAL, 'Metal', collide=False)
        # Existing external glazing supplies daylight along the west side.
        rect('WindowSill', -79.8, -79.3, 2, 3.5, z0, z1, DARK)
        box('BoardTrim', (40, 6.6, .25), (-48, 8, z1-.65), METAL, collide=False)
        box('Whiteboard', (39, 5.8, .15), (-48, 8, z1-.85), WHITE, collide=False)
        for z in (46, 58, 70):
            for x in (-63, -35):
                box('LongTable', (19, .65, 4), (x, 3.4, z), WOOD, 'Wood')
                for dx in (-7.5, 7.5):
                    box('TableSupport', (.65, 3.1, 3), (x+dx, 1.55, z), DARK, 'Metal', collide=False)
                for dx in (-6, 0, 6):
                    chair(x+dx, .4, z-3.7, (41, 57, 61), 180)
        box('LecturerDesk', (9, .7, 4), (-48, 3.5, 81), WOOD, 'Wood')
        box('LecturerPedestal', (2.5, 3.2, 2.5), (-48, 1.6, 81), DARK, 'Metal', collide=False)
        rect('Ceiling', x0, x1, 22, 22.4, z0, z1, WHITE)
        ceiling(x0, x1, z0, z1, 21.95)
        plaque('RoomType', 'قاعة دراسية\nنموذج مستوٍ', (x1+.7, 12.2, 48), (.35, 3.8, 8), 'Right')


def tiered_lecture():
    x0, x1, z0, z1 = ROOMS['TieredLecture_Photo16']
    with G.Group('TieredLecture_Photo16'):
        evidence('visual=A: photo16 green curved seating, tiered floor, low lecturer zone, whiteboards')
        rect('RoomFloor', x0, x1, .32, .4, z0, z1, CARPET, 'SmoothPlastic')
        C5.wall_x(x0, x1, z0, 0, 22, WHITE, 'SmoothPlastic')
        C5.wall_x(x0, x1, z1, 0, 22, WHITE, 'SmoothPlastic')
        C5.wall_z(z0, z1, x0, 0, 12, WHITE, 'SmoothPlastic', gaps=[(39, 49)])
        rect('CorridorClerestory', x0-.2, x0+.2, 12, 22, z0, z1, GLASS, 'Glass', transp=.3)
        rect('DoorHeader', x0-.5, x0+.5, 10, 12, 39, 49, WHITE)
        for z in (39, 49):
            box('DoorJamb', (1.1, 10, .4), (x0, 5, z), METAL, 'Metal', collide=False)
        rect('DarkAcousticWall', x1-.3, x1, 0, 8, z0, z1, DARK, 'Fabric', collide=False)
        box('BoardTrim', (44, 6.6, .3), (67, 8.2, z0+.7), METAL, collide=False)
        box('Whiteboard', (43, 5.8, .15), (67, 8.2, z0+.9), WHITE, collide=False)
        box('LecturerConsole', (9, 3.5, 3.5), (67, 1.85, 44), (194, 199, 198))
        for row in range(5):
            za = 52+row*7
            y = (row+1)*1.2
            rect('Tier', x0+6, x1-6, .1, y, za, za+7, CARPET, 'SmoothPlastic')
            rect('TierEdge', x0+6, x1-6, y+.01, y+.04, za, za+.12, (146, 151, 148), 'Metal', collide=False)
            # Shallow .6-stud steps on both sides; no invisible ramp or jump requirement.
            for xa, xb in ((x0, x0+6), (x1-6, x1)):
                for half in range(2):
                    top = row*1.2+(half+1)*.6
                    rect('AisleStep', xa, xb, .1, top, za+half*3.5, za+(half+1)*3.5, CARPET, 'SmoothPlastic')
            for x in (47, 53, 59, 65, 73, 79, 85):
                curve = (x-67)**2/180
                yaw = math.degrees(math.atan2(x-67, 75))
                chair(x, y, za+2+curve, GREEN, yaw, writing=True)
        rect('BackLanding', x0, x1, .1, 6, 87, z1-.5, CARPET, 'SmoothPlastic')
        rect('BackAcousticPanel', x0+.5, x1-.5, 6, 12, z1-.55, z1-.3, DARK, 'Fabric', collide=False)
        rect('Ceiling', x0, x1, 22, 22.4, z0, z1, WHITE)
        ceiling(x0, x1, z0, z1, 21.95)
        plaque('RoomType', 'قاعة محاضرات\nنموذج مدرّج', (x0-.7, 12.2, 44), (.35, 3.8, 8), 'Left')


def amenities():
    with G.Group('ExistingAmenities'):
        evidence('legacy=C: existing cafes, games, study furniture and computer displays retained')
        C5.counter(-38, 142, 0, 30, 4, (46, 140, 90), 'Salad Creations | سالاد كريشنز', 'Front')
        C5.counter(40, 142, 0, 30, 4, (40, 70, 150), 'Larich', 'Front')
        for q in range(5):
            for r in range(2):
                C5.table_set(-54+q*22, 112-r*16, 0, 3, seat_cols=[(60, 130, 90), (60, 100, 170), (230, 190, 60)])
        for q in range(3):
            box('Foosball', (7, 2.6, 3.4), (-60+q*20, 25.3, 60), (60, 62, 68), collide=False)
        for q in range(6):
            box('Puff', (3.2, 1.8, 3.2), (-62+q*5, 24.9, 90),
                [(120, 190, 90), (240, 190, 60), (220, 90, 70)][q % 3], 'Fabric', collide=False)
        for x in (-50, -24, 48, 74):
            for z in (60, 80):
                box('Desk', (14, .8, 5), (x, 43.4, z), (232, 232, 228))
                box('Mon', (3.4, 2.2, .3), (x, 45.2, z-2), DARK, collide=False,
                    text=dict(face='Front', text='BSC', color=(110, 220, 255), bg=(10, 28, 52), bg_t=0))
        plaque('Games', 'جلسات وألعاب\nStudy and Games', (-64, 32, 21.2), (22, 3.4, .4), 'Back')
        plaque('Computers', 'منطقة الحاسوب\nComputer Area', (-30, 48, 21), (30, 3.6, .4), 'Back')
        for y in (22.5, 38.5, 54.5):
            for x, z in ((-44, 28), (58, 28), (-44, 112), (58, 112)):
                C5.light_panel(x, y, z, 8, 2, 1.5, 34)
        G.box('StoneSign', (12, 6, 2), (-24, 3, -2), (222, 214, 194), 'Concrete',
              text=dict(face='Front', text='113\nكلية العلوم\nCOLLEGE OF SCIENCE',
                        color=(70, 62, 50), bg=(222, 214, 194), bg_t=0))


def build():
    # Consume the legacy north's RNG calls, then replace only its generated geometry.
    # Subsequent world generation keeps exactly the pre-v44 random state.
    start, counter, parts = len(G.buf), G.cnt[0], G.nparts[0]
    C5.north_building()
    del G.buf[start:]
    G.cnt[0], G.nparts[0] = counter, parts
    with G.Group('NorthBuilding'):
        envelope()
        floors()
        atrium()
        circulation()
        flat_classroom()
        tiered_lecture()
        amenities()
