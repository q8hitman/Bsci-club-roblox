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
def build():
 with G.Group("Laser48"):
  with G.Group("Entry"):
   import arcade59   # v59: was a dark frame with its title facing away from the lobby (owner could not find it)
   arcade59.gateway("Laser","LaserEntrance")
   lx,lz,_=arcade59.spot("Laser")
   G.part("LaserSpawn",(8,1,8),(lx,300.5,lz-7),CYAN,transp=1,collide=False,shadow=False)
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
