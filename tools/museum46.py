"""Fictional BSC museum; additive geometry only. No existing campus parts are modified."""
import math
import genmap as G

CREAM=(235,232,220)
DARK=(25,52,60)
TEAL=(56,208,190)
STATIONS=[
    ("micro","مين هذا الميكروب؟","Microbiology",235,-105,(70,205,170)),
    ("enzyme","ليش ناس ما يهضمون الحليب؟","Biochemistry",235,-55,(255,176,83)),
    ("animal","حيوان الصحراء وحيوان الثلج","Animal Biology",235,-5,(244,142,112)),
    ("plant","الورقة مصنع أكل","Plant Biology",270,25,(132,210,93)),
    ("dna","صلّح شريط DNA","Molecular Biology",320,25,(164,153,247)),
    ("evidence","مين صاحب العينة؟","Forensic Science",345,-25,(113,192,238)),
    ("farm","ازرع بالصحراء","Agriculture",345,-80,(222,200,100)),
    ("biotech","صنّع دوا بالخمائر","Biotechnology",290,-60,(77,232,220)),
]


def deco(name,size,pos,color,mat="SmoothPlastic",**kw):
    G.box(name,size,pos,color,mat,collide=False,shadow=False,
          extra='<bool name="CanTouch">false</bool><bool name="CanQuery">false</bool>',**kw)


def sphere(name,pos,d,color):
    G.part(name,(d,d,d),pos,color,"SmoothPlastic",shape="Ball",collide=False,shadow=False,
           extra='<bool name="CanTouch">false</bool><bool name="CanQuery">false</bool>')


def exhibit(kind,x,z,c):
    """Authored display model: cloneable into each player's interactive viewport."""
    with G.Group("Display","Model"):
        if kind=="micro":
            for dx in (-6,0,6):
                deco("Slide",(5,.3,8),(x+dx,4,z),DARK,"Glass",transp=.3)
            deco("Bacillus",(3,1.4,1.4),(x-6,5.2,z),c)
            sphere("Yeast",(x,5.3,z),3,(233,172,203))
            sphere("Bud",(x+1.5,6,z),1.6,(233,172,203))
            sphere("Nucleus",(x,6.5,z),.8,(111,72,125))
            deco("Paramecium",(4,1.5,2),(x+6,5,z),(140,192,242))
            for j in range(7):
                for side in (-1,1):
                    deco("Cilium",(.15,.15,.8),(x+4.5+j*.5,5,z+side*1.3),CREAM)
        elif kind=="enzyme":
            for dx in (-4,4):
                deco("Enzyme",(4,4,6),(x+dx,6,z),c)
            deco("ActiveSite",(4,1,6),(x,4.5,z),c)
            for dx in (-1,1): sphere("Substrate",(x+dx,9,z),2.1,TEAL)
        elif kind=="animal":
            deco("Desert",(9,.5,10),(x-5,4,z),(216,181,127),"Sand")
            deco("Arctic",(9,.5,10),(x+5,4,z),(216,235,242),"Ice")
            for dx,col in ((-5,(230,191,135)),(5,CREAM)):
                sphere("AnimalBody",(x+dx,6,z),3.8,col)
                sphere("AnimalHead",(x+dx,7,z-2),2.3,col)
                for side in (-1,1):
                    deco("Ear",(.9,2.8 if dx<0 else .8,.8),(x+dx+side*.7,8.3,z-2),col)
                    deco("Leg",(.8,2,.8),(x+dx+side,4.8,z),col)
        elif kind in ("plant","farm"):
            deco("Soil",(14,1,10),(x,4.3,z),(108,81,59),"Ground")
            for dx in (-4,0,4):
                deco("Stem",(.5,5,.5),(x+dx,7,z),(65,125,69))
                for side in (-1,1):
                    deco("Leaf",(3,.4,2),(x+dx+side,7.5,z),c,rot=(0,0,side*22))
            if kind=="farm":
                deco("WaterTank",(3,5,3),(x-7,6,z+4),(85,177,226),"Glass",transp=.3)
                deco("GrowLamp",(12,.5,3),(x,11,z),(255,235,162),"Neon")
        elif kind=="dna":
            for j in range(10):
                a=j*.65
                dx,dz=math.cos(a)*4,math.sin(a)*4
                for side in (-1,1): sphere("Backbone",(x+side*dx,4.5+j*.85,z+side*dz),.9,c if side==1 else TEAL)
                deco("BasePair",(8,.35,.35),(x,4.5+j*.85,z),(226,193,113),rot=(0,-math.degrees(a),0))
        elif kind=="evidence":
            for i,rows in enumerate(((1,3,5),(1,3,5),(1,2,5),(2,4,6))):
                dx=-7.5+i*5
                deco("Lane",(3,7,.4),(x+dx,7,z),DARK)
                for row in rows: deco("Band",(2,.35,.3),(x+dx,4.3+row,z-.4),c,"Neon")
        elif kind=="biotech":
            G.vcyl("ReactorBase",x,3.5,4.5,z,13,DARK,"Metal",collide=False)
            G.vcyl("ReactorGlass",x,4.5,17,z,10,(143,222,214),"Glass",collide=False,transp=.65)
            G.vcyl("Culture",x,4.5,10,z,9,TEAL,"Neon",collide=False,transp=.35,shadow=False)
            G.vcyl("ReactorLid",x,17,18,z,12,DARK,"Metal",collide=False)
            deco("Stirrer",(.5,12,.5),(x,10.5,z),CREAM,"Metal")
            for dy in (6,10,14): deco("Impeller",(6,.4,1),(x,dy,z),CREAM,"Metal")
            for j in range(10):
                a=j*2.4
                sphere("YeastCell",(x+math.sin(a)*3,6+j*.8,z+math.cos(a)*3),.7,CREAM)
            for side in (-1,1):
                deco("Pipe",(9,.8,.8),(x+side*10,5,z),DARK,"Metal")
                deco("ProcessUnit",(4,7,5),(x+side*15,7,z),c,"Metal")


def showcase(kind, x, z, c):
    """v63 (owner: exhibits unclear): a big wordless sculpture behind each plinth, readable from the entrance, on a
    coloured floor zone in the exhibit's colour"""
    zz = z + 17
    G.disc("ZoneFloor", x, 0.26, z + 3, 40, 0.06, tuple(int(v * 0.55) for v in c), "SmoothPlastic", collide=False,
           shadow=False)
    G.disc("ZoneRing", x, 0.25, z + 3, 41.5, 0.05, c, "Neon", collide=False, shadow=False)
    if kind == "micro":   # a rod, a budding yeast and a slipper-shaped paramecium, giant
        G.part("BigBacillus", (12, 5, 5), (x - 8, 6, zz), (120, 200, 130), "SmoothPlastic", shape="Cylinder",
               rot=(0, 0, 20), collide=False)
        for e in (-1, 1):
            sphere("BigBacillusCap", (x - 8 + e * 5.6, 6 + e * 2.05, zz), 5, (120, 200, 130))
        sphere("BigYeast", (x, 8, zz), 8, (233, 172, 203))
        sphere("BigYeastBud", (x + 3.6, 12.4, zz), 4, (233, 172, 203))
        sphere("BigYeastNucleus", (x - 1, 8.6, zz - 3.6), 2.4, (111, 72, 125))
        deco("BigParamecium", (10, 4, 5), (x + 9, 6, zz), (140, 192, 242), rot=(0, 0, -15))
        for j in range(10):
            for side in (-1, 1):
                deco("BigCilium", (.3, 1.6, .3), (x + 5 + j * .9, 6 + (j - 5) * -.26 + side * 2.6, zz), CREAM)
    elif kind == "enzyme":   # lock and key: the enzyme with a lactose-shaped pocket, the sugar hovering above it
        deco("BigEnzyme", (16, 8, 6), (x, 6, zz), c)
        deco("BigEnzymeL", (5, 8, 6), (x - 5.5, 13, zz), c)
        deco("BigEnzymeR", (5, 8, 6), (x + 5.5, 13, zz), c)
        for k, col in ((-1.6, (120, 200, 255)), (1.6, (255, 220, 120))):   # glucose + galactose = lactose
            for q in range(6):
                a = q * math.pi / 3
                sphere("BigSugar", (x + k * 2 + math.cos(a) * 1.4, 19 + math.sin(a) * 1.4, zz), 1.3, col)
    elif kind == "animal":   # a sand dune with a fennec and an ice floe with a polar bear, back to back
        G.part("BigDune", (14, 6, 12), (x - 7, 3, zz), (226, 190, 130), "Sand", shape="Ball", collide=False)
        sphere("FennecBody", (x - 7, 8, zz), 5, (230, 190, 140))
        sphere("FennecHead", (x - 7, 11.4, zz - 2), 3.2, (230, 190, 140))
        for e in (-1, 1):
            deco("FennecEar", (1.2, 5, .6), (x - 7 + e * 1.5, 15, zz - 2), (230, 190, 140), rot=(0, 0, -e * 18))
        deco("IceFloe", (12, 3, 12), (x + 7, 1.8, zz), (220, 240, 250), "Ice")
        deco("BearBody", (9, 6, 5), (x + 7, 6.5, zz), (248, 248, 244))
        sphere("BearHead", (x + 7, 8.5, zz - 3.8), 4, (248, 248, 244))
        for e in (-1, 1):
            sphere("BearEar", (x + 7 + e * 1.4, 10.4, zz - 3.6), 1.2, (248, 248, 244))
    elif kind == "plant":   # a giant leaf under a sun, arrows of gas in and out
        deco("BigLeaf", (14, 1, 9), (x, 10, zz), (90, 170, 70), "Grass", rot=(0, 0, 18))
        deco("BigLeafVein", (14, .4, .6), (x, 10.6, zz), (150, 210, 110), rot=(0, 0, 18))
        G.vcyl("BigLeafStem", x + 6, 0, 8, zz, 1, (80, 140, 60), collide=False)
        G.part("BigSun", (6, 6, 6), (x - 8, 20, zz), (255, 220, 90), "Neon", shape="Ball", collide=False, shadow=False)
        for q in range(3):
            sphere("BigO2", (x + 4 + q * 1.5, 13 + q * 2.5, zz - 2), 1.4, (230, 70, 70))
    elif kind == "dna":   # a tall helix with one pair glowing (the repaired spot)
        for j in range(20):
            a = j * .55
            dx, dz = math.cos(a) * 4, math.sin(a) * 4
            for side in (-1, 1):
                sphere("BigBackbone", (x + side * dx, 3 + j * .95, zz + side * dz), 1.2, c if side == 1 else TEAL)
            deco("BigBasePair", (8, .45, .45), (x, 3 + j * .95, zz), (255, 230, 120) if j in (9, 10) else (226, 193, 113),
                 "Neon" if j in (9, 10) else "SmoothPlastic", rot=(0, -math.degrees(a), 0))
    elif kind == "evidence":   # a fingerprint under a magnifying glass, crime-scene tape
        G.part("PrintPad", (.4, 12, 12), (x, 9, zz), (40, 44, 54), "SmoothPlastic", shape="Cylinder",
               rot=(0, 90, 0), collide=False)
        for k in range(4):
            r = 1.5 + k * 1.3
            for q in range(10 + k * 4):
                a = q * 2 * math.pi / (10 + k * 4)
                deco("PrintRidge", (.4, .4, .3), (x + math.cos(a) * r, 9 + math.sin(a) * r * 1.2, zz - .3), (90, 200, 255),
                     "Neon")
        G.part("BigLensRim", (.8, 9, 9), (x + 4, 11, zz - 3), (200, 170, 60), "Metal", shape="Cylinder",
               rot=(0, 90, 0), collide=False)
        G.part("BigLens", (.4, 8, 8), (x + 4, 11, zz - 3.2), (200, 230, 250), "Glass", shape="Cylinder", rot=(0, 90, 0),
               transp=.5, collide=False)
        deco("BigLensHandle", (1, 7, 1), (x + 7, 5.4, zz - 3), (60, 40, 30), "Wood", rot=(0, 0, -30))
        deco("CrimeTape", (22, 1, .1), (x, 2.5, zz + 6), (250, 210, 40), rot=(0, 0, 4))
    elif kind == "farm":   # a small greenhouse with tomato plants and a drip line
        for e in (-1, 1):
            deco("GreenhouseWall", (.4, 8, 14), (x + e * 8, 4, zz), (200, 235, 220), "Glass", transp=.5)
            deco("GreenhouseRoof", (9, .4, 14), (x + e * 4, 9.4, zz), (200, 235, 220), "Glass", transp=.5,
                 rot=(0, 0, -e * 22))
        deco("GreenhouseShade", (16, .2, 14), (x, 10.8, zz), (40, 60, 40), transp=.4)
        for k in range(4):
            px = x - 5 + k * 3.4
            G.vcyl("TomatoStem", px, 0, 6, zz, .5, (70, 130, 60), collide=False)
            sphere("TomatoLeaves", (px, 6, zz), 3, (80, 150, 60))
            sphere("Tomato", (px + .8, 4.8, zz - 1), 1.2, (220, 50, 40))
        deco("DripLine", (14, .3, .3), (x, .6, zz - 1.5), (40, 40, 44))


def build():
    with G.Group("Museum46"):
        with G.Group("Architecture"):
            # Lush botanical garden terrace surrounding the museum so no flat sand is ever visible
            G.box("MuseumBotanicalLawn",(280,1.0,320),(290,-.55,-60),(96,154,88),"Grass")
            G.box("MuseumPlazaBorder",(184,0.8,224),(290,-.3,-50),(214,208,194),"Concrete")
            for gx in (190, 230, 350, 390):
                for gz in (-185, -120, -40, 35, 80):
                    G.tree(gx, 0, gz, 1.25)
            for hx in (196, 384):
                G.box("MuseumHedge",(3.5,3.2,216),(hx,1.6,-50),(68,128,68),"Grass",collide=False)
            G.box("MuseumRearHedge",(188,3.2,3.5),(290,1.6,62),(68,128,68),"Grass",collide=False)
            G.box("MuseumFloor",(160,1.2,200),(290,-.4,-50),(92,100,110),"Slate")   # v63: mid-value floor, the exhibits pop
            G.part("MuseumSpawn",(8,1,8),(290,.8,-142),TEAL,rot=(0,180,0),transp=1,collide=False,shadow=False)  # v63: face the museum (+z), not the exit
            # Wide route around the existing parking, not through it or the train station.
            G.box("MuseumApproach",(151,.5,12),(217.5,-.05,-205),CREAM,"Concrete")
            G.box("MuseumApproach",(12,.5,61),(290,-.05,-177),CREAM,"Concrete")
            for x in (165,200,235,270):
                deco("GuideLight",(6,.08,.6),(x,.23,-205),TEAL,"Neon")
            for z in (-190,-175,-160): deco("GuideLight",(.6,.08,6),(290,.23,z),TEAL,"Neon")
            for x in (210,370):
                G.box("LowWall",(1.2,3,200),(x,1.7,-50),DARK,"Concrete")
                G.box("GalleryGlass",(.5,17,200),(x,11.7,-50),(154,206,211),"Glass",transp=.65)
                for z in (-148,-100,-50,0,48): G.box("Column",(1.5,26,1.5),(x,13,z),DARK,"Metal")
            G.box("RearWall",(160,6,1.2),(290,3.2,50),DARK,"Concrete")
            G.box("RearGlass",(160,16,.5),(290,14,50),(154,206,211),"Glass",transp=.6)
            for x in (244,336):
                G.box("EntryWall",(68,18,1),(x,9.2,-150),DARK,"Concrete")
                deco("EntryRib",(68,.4,.3),(x,5,-150.6),TEAL,"Neon")
            for x in (230,350): G.box("RoofWing",(40,1.5,202),(x,26,-50),CREAM,"Concrete")
            G.box("Skylight",(80,.4,200),(290,26,-50),(40,60,70),"Glass",transp=.35)   # v63: tinted, softer light
            for z in (-150,-100,-50,0,50): deco("RoofBeam",(160,.7,1.5),(290,25.1,z),DARK,"Metal")
            G.box("EntryCanopy",(58,1.2,18),(290,20,-155),DARK,"Metal")
            G.sign("MuseumTitle","متحف اكتشاف الأحياء\nBSC BIOLOGY DISCOVERY",(290,15,-151.2),(30,7,.5),"Front",bg=DARK)
            G.sign("ExitGuide","الخروج إلى الجامعة ↓\nCampus Exit",(290,13,-149),(22,4,.5),"Back",bg=DARK)
            G.sign("RouteGuide","المتحف ← حول المواقف\nMuseum via lit path",(145,5,-199),(18,5,.5),"Front",bg=DARK)
            deco("MainAisle",(14,.05,190),(290,.23,-50),(60,66,76))
            for z in range(-140, 45, 12): deco("AisleLight",(1,.06,4),(290,.27,z),TEAL,"Neon")
            for x,z in ((257,-115),(325,-120),(265,5),(320,0)):
                G.box("Bench",(10,1,3),(x,1.5,z),DARK,"Wood")
            # Two gentle lights cover the gallery; most accents are unlit Neon.
            for z in (-100,0):
                G.box("GalleryLight",(20,.3,4),(290,24,z),(255,240,215),"Neon",collide=False,shadow=False,light=(1,55,(255,240,215)))
        for index,(kind,ar,en,x,z,c) in enumerate(STATIONS,1):
            with G.Group("Exhibit_"+kind,"Model"):
                G.box("DisplayPlinth",(23,3,19),(x,1.7,z),DARK,"Concrete")
                deco("AccentRim",(23.2,.25,19.2),(x,3.3,z),c,"Neon")
                exhibit(kind,x,z,c)
                if kind!="biotech": showcase(kind,x,z,c)
                G.box("Console",(6,3.5,3),(x,2,z-13),c,"Metal")
                G.sign("StationName",f"{index:02d}  {ar}\n{en}",(x,5,z-13),(18,3.5,.4),"Front",bg=DARK)
                if kind=="biotech":
                    G.sign("HeroTitle","التقنية الحيوية\nفكرة → خلية → منتج",(x,21,z),(32,5,.5),"Front",bg=DARK)
                    for side in (-1,1): deco("HeroFin",(1,20,3),(x+side*20,10,z),c,"Neon")
