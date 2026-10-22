"""Additive fictional five-room timing facility. Original primitive geometry, no campus changes."""
import json
import genmap as G
ORIGIN=(-6000,300,-8000)
ROOMS=[
 dict(id=1,ar="التوقيت",hint="الكهرماني تحذير • الأحمر خطر • انتظر الأزرق",cycle=6.5,safe=3.4,warning=1.3,kind="timing"),
 dict(id=2,ar="الشبكة المتحركة",hint="راقب الحركة • الممران الجانبيان آمنان",cycle=7,safe=3.9,warning=1.3,kind="moving"),
 dict(id=3,ar="الباب الأمني",hint="قف على اللوح الأيسر لفتح الباب لنفسك ولزميلك",cycle=7,safe=3.9,warning=1.3,kind="door"),
 dict(id=4,ar="جسر المنصات",hint="انتظر الجسر ثم اعبر • السقوط يعيدك لنقطة الحفظ",cycle=7.5,safe=4.4,warning=1.3,kind="platform"),
 dict(id=5,ar="الهروب الأخير",hint="فعّل اللوح الأيمن • راقب الشعاعين ثم اعبر إلى الخروج",cycle=8,safe=4.9,warning=1.3,kind="final")]
NAVY=(29,49,65); WHITE=(202,218,223); CYAN=(68,202,209)
FLOOR=(128,136,148); WALL=(84,96,116); CEIL=(60,66,80)   # v59 facility palette: dark surfaces make the beams read
COLORS=[CYAN,(130,164,228),(234,184,89),(131,202,166),(180,151,223)]
def deco(n,size,p,c,mat="SmoothPlastic",**kw):
 G.box(n,size,p,c,mat,collide=False,shadow=False,extra='<bool name="CanQuery">false</bool><bool name="CanTouch">false</bool>',**kw)
def gate(name,x,y,z,text,color):
 with G.Group(name):
  for side in (-1,1):G.box("Column",(2,14,2),(x+side*27,y+7,z),NAVY,"Metal")
  G.box("Lintel",(56,2,2),(x,y+14,z),WHITE,"Metal")
  G.sign("RoomLabel",text,(x,y+11,z+.1),(47,4,.4),"Back",bg=NAVY)
  deco("Guide",(50,.12,1),(x,y+.06,z),color,"Neon")
def beam(parent,x,y,z,width=52):
 with G.Group(parent):
  for h in (1.5,5,8.5):deco("Beam",(width,.32,.5),(x,y+h,z),CYAN,"Neon",transp=.8)
  deco("BeamFloorMark",(width,.06,3),(x,y+.04,z),(190,60,72))   # v59: where the beams cross the floor
  for side in (-1,1):G.box("Emitter",(1.2,10,1.2),(x+side*width/2,y+5,z),NAVY,"Metal",collide=False)
def entrance_hall():
 """v63 briefing hall in front of room 1 (outside the arcade lobby): LaserSpawn at the south end facing the door,
 LaserEntrance (the start prompt) in the armoured door to room 1, Portal|Arcade back behind the spawn. Facility
 palette, warning stripes, red alarm lamps, lockers and five room lights that preview the course."""
 x,y=ORIGIN[0],ORIGIN[1]
 z0,z1=ORIGIN[2]+42,ORIGIN[2]+100     # -7958 .. -7900 (room 1 starts at -7960)
 zc=(z0+z1)/2
 G.box("HallFloor",(60,1,z1-z0),(x,y-.5,zc),FLOOR,"DiamondPlate")
 G.box("HallCeiling",(62,.6,z1-z0),(x,y+12.7,zc),CEIL,"SmoothPlastic")
 for side in (-1,1):
  G.box("HallWallBase",(2,3,z1-z0),(x+side*30,y+1.5,zc),NAVY,"Metal")
  G.box("HallWall",(.8,9,z1-z0),(x+side*30.2,y+7.5,zc),WALL,"SmoothPlastic")
  G.box("HallRail",(2,1,z1-z0),(x+side*30,y+12,zc),WHITE,"Metal")
  deco("HallStrip",(.3,.2,z1-z0-2),(x+side*28.8,y+11,zc),(255,90,90),"Neon")
  for k in range(4):   # lockers along both walls
   G.box("Locker",(2,8,4.4),(x+side*28.4,y+4,z1-12-k*5),(70,84,104),"Metal",collide=False)
   deco("LockerVent",(.1,.6,3),(x+side*27.35,y+6.6,z1-12-k*5),(40,48,60))
 G.box("HallBackWall",(60,13,1),(x,y+6.5,z1+.5),WALL,"SmoothPlastic")
 for dz in (12,30,48):
  deco("HallLight",(18,.2,3),(x,y+12.3,z0+dz),(235,244,255),"Neon")
  G.part("HallLamp",(1,1,1),(x,y+10.5,z0+dz),(235,244,255),transp=1,collide=False,shadow=False,light=(2,30,(225,238,255)))
 # the armoured door into room 1: frame, hazard stripes, red alarm lamps; the doorway is the start prompt
 for side in (-1,1):
  G.box("DoorFrame",(3,13,3),(x+side*8,y+6.5,z0+1.5),NAVY,"Metal")
  G.part("AlarmLamp",(1.6,1.6,1.6),(x+side*8,y+14,z0+1.5),(255,60,60),"Neon",shape="Ball",collide=False,shadow=False,
         light=(1.2,20,(255,80,80)))
 G.box("DoorLintel",(19,2,3),(x,y+12,z0+1.5),NAVY,"Metal")
 for k in range(8):   # yellow/black hazard stripes on the floor in front of the door
  deco("HazardStripe",(1.6,.06,4),(x-6.3+k*1.8,y+.06,z0+5),(250,200,40) if k%2 else (30,30,34))
 G.part("LaserEntrance",(13,11,.6),(x,y+6,z0+1),(255,90,90),"Neon",transp=.55,collide=False,shadow=False)
 # the hall is sealed from room 1: you go in through the start prompt (the server moves you to your checkpoint)
 for side in (-1,1):
  G.box("HallFrontWall",(20.5,13,1),(x+side*19.75,y+6.5,z0-.2),WALL,"SmoothPlastic")
 G.box("HallFrontWall",(19,2,1),(x,y+12,z0-.2),WALL,"SmoothPlastic")
 G.box("DoorGlass",(13,11,.4),(x,y+5.5,z0+.3),(255,140,140),"Glass",transp=.6)
 # hangs from the ceiling in front of the door (above the lintel it was hidden by the ceiling)
 G.sign("HallTitle","هروب الليزر | LASER ESCAPE",(x,y+10.8,z0+14),(24,2.6,.4),"Back",bg=NAVY)
 for side in (-1,1):deco("TitleHanger",(.2,1.3,.2),(x+side*10,y+12.1,z0+14),WHITE,"Metal")
 # five lights above the door: the five rooms, in their colours
 for i,c in enumerate(COLORS):
  G.part("RoomPreview",(2.2,2.2,.4),(x-8+i*4,y+9.6,z0+3.4),c,"Neon",collide=False,shadow=False)
 # beams sweeping a glass case on the side: a taste of what is inside
 G.box("DemoCase",(10,6,6),(x-18,y+3,zc-6),(200,230,245),"Glass",transp=.7,collide=False)
 for h in (1.5,3,4.5):deco("DemoBeam",(9.4,.2,.2),(x-18,y+h,zc-6),(255,70,80),"Neon")
 G.box("DemoPlinth",(11,1,7),(x-18,y+.5,zc-6.5),NAVY,"Metal")
 # arrival and the way back
 # spawn 20 in front of the back wall: the follow camera must stay in front of the return portal
 G.part("LaserSpawn",(8,1,8),(x,y+.5,z1-20),CYAN,transp=1,collide=False,shadow=False)
 G.part("Portal|Arcade",(10,11,.6),(x,y+6,z1-.6),(255,200,120),"Neon",transp=.45,collide=False,shadow=False)
 G.sign("HallBack","↩ الأركيد",(x,y+13,z1-.2),(10,2,.4),"Front",bg=NAVY)


def build():
 with G.Group("Laser48"):
  with G.Group("Entry"):
   import arcade59   # v59: was a dark frame with its title facing away from the lobby (owner could not find it)
   # v63 (owner audit): the entrance and LaserSpawn sat inside the arcade lobby, so anyone arriving was pulled into an
   # arcade round. The arcade gateway is now a portal to the facility's own briefing hall (entrance_hall below).
   arcade59.gateway("Laser","Portal|Laser")
   entrance_hall()
  for d in ROOMS:
   i=d['id'];x,y,z=ORIGIN[0],ORIGIN[1],ORIGIN[2]-(i-1)*100;c=COLORS[i-1]
   with G.Group("Room_"+str(i)):
    if i==4:
     for side in (-1,1):G.box("SafeFloor",(60,1,28),(x,y-.5,z+side*26),FLOOR,"DiamondPlate")
     G.box("MovingBridge",(10,1,28),(x,y-.25,z),c,"DiamondPlate")
     deco("GapBasin",(60,.4,24),(x,y-12,z),NAVY,"Metal")
    else:G.box("Floor",(60,1,80),(x,y-.5,z),FLOOR,"DiamondPlate")
    for side in (-1,1):
     G.box("WallBase",(2,3,80),(x+side*30,y+1.5,z),NAVY,"Metal")
     G.box("Wall",(.8,9,80),(x+side*30.2,y+7.5,z),WALL,"SmoothPlastic")   # v59: opaque: an indoor facility, not a sky deck
     G.box("UpperRail",(2,1,80),(x+side*30,y+12,z),WHITE,"Metal")
     deco("LightStrip",(.3,.2,78),(x+side*28.8,y+11,z),c,"Neon")
     for dz in (-35,0,35):G.box("FramePost",(1.4,12,1.4),(x+side*30,y+6,z+dz),NAVY,"Metal")
    for dz in (-35,35):G.box("CeilingRib",(60,.7,1.4),(x,y+12,z+dz),NAVY,"Metal")
    G.box("Ceiling",(62,.6,80),(x,y+12.7,z),CEIL,"SmoothPlastic")
    for dz in (-30,-10,10,30):
     deco("CeilingLight",(18,.2,3),(x,y+12.3,z+dz),(235,244,255),"Neon")
     G.part("CeilingLamp",(1,1,1),(x,y+10.5,z+dz),(235,244,255),transp=1,collide=False,shadow=False,light=(2.2,30,(225,238,255)))
    gate("StartGate",x,y,z+38,str(i)+" / 5 • "+d['ar'],c)
    gate("FinishGate",x,y,z-33,"نقطة حفظ ✓" if i<5 else "الخروج • أحسنت",c)
    G.part("Checkpoint",(8,.2,6),(x,y+.1,z+32),c,"Neon",transp=.3,collide=False,shadow=False)
    G.sign("Instructions",d['hint'],(x,y+9.5,z+27),(26,2.2,.4),"Back",bg=NAVY)  # v54: a slim plate above the door
    for dz in (20,-22):deco("SafeStripe",(52,.1,1),(x,y+.07,z+dz),c)
    if i==2:beam("Hazard",x,y,z,20)
    elif i==3:beam("Hazard",x+15,y,z,16)
    elif i==5:
     beam("Hazard",x-10,y,z+1,32);beam("HazardB",x+10,y,z-18,32)
    else:beam("Hazard",x,y,z)
    if i in (3,5):
     px=x+(-16 if i==3 else 16)
     G.box("PressurePlate",(8,.4,8),(px,y+.2,z+12),c,"Metal")
     G.sign("PlateLabel","قف هنا • فتح المسار",(px,y+8,z+17),(18,3,.3),"Back",bg=NAVY)  # above head height: never blocks the walk to the plate
    if i==3:
     G.box("SecurityDoor",(57.8,10,1),(x,y+5,z-18),NAVY,"Metal")  # wall to wall: no side gap around the door
     deco("DoorWindow",(30,4,.15),(x,y+6,z-17.4),CYAN,"Neon")
    if i<5:
     G.box("Vestibule",(60,1,20),(x,y-.5,z-50),FLOOR,"DiamondPlate")
     for side in (-1,1):G.box("VestibuleWall",(.8,12,20),(x+side*30.2,y+6,z-50),WALL,"SmoothPlastic")
     G.box("VestibuleCeiling",(62,.6,20),(x,y+12.7,z-50),CEIL,"SmoothPlastic")
    else:
     G.box("ExitPlatform",(60,1,24),(x,y-.5,z-52),WHITE,"Concrete")
     G.part("ReturnConsole",(8,4,3),(x,y+2,z-56),c,"Metal")
     G.sign("EscapeTitle","منشأة خيالية • نجحت في الهروب",(x,y+8,z-61),(50,5,.5),"Back",bg=NAVY)
def write_data(path):
 def lua(v):
  if isinstance(v,dict):return '{'+','.join('['+json.dumps(k,ensure_ascii=False)+']='+lua(x) for k,x in v.items())+'}'
  if isinstance(v,(list,tuple)):return '{'+','.join(lua(x) for x in v)+'}'
  return json.dumps(v,ensure_ascii=False)
 with open(path,'w',encoding='utf-8')as f:
  f.write('-- Generated by tools/laser48.py. Fictional facility.\nlocal D='+lua(dict(Origin=ORIGIN,Spacing=100,XP=40,Rooms=ROOMS))+'\n')
  f.write('function D.center(i) return D.Origin[1],D.Origin[2],D.Origin[3]-(i-1)*D.Spacing end\nreturn D\n')
