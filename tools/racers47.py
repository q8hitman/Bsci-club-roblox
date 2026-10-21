"""Static fictional micro raceways and the canonical shared driving layout. No existing parts are modified."""
import json
import math
import genmap as G

TRACKS=[
 dict(id="cell",ar="حلبة الخلية",desc="حلبة سريعة بمنعطفات واسعة؛ مناسبة للبداية",origin=[-7800,300,-6000],width=28,
      points=[[0,-90],[80,-90],[120,-60],[120,60],[80,90],[-80,90],[-120,60],[-120,-60],[-80,-90]],gates=[3,5,7,9,1],
      pickups=[dict(id="b1",kind="boost",x=120,z=0),dict(id="s1",kind="shield",x=-120,z=0)],
      hazards=[dict(x=40,z=87,r=3.3),dict(x=-120,z=-40,r=3.3)]),
 dict(id="helix",ar="منعطفات الجزيئات",desc="منعطفات متتابعة واختصار ضيق بين البوابتين 1 و2",origin=[-7800,300,-6500],width=26,
      points=[[0,-120],[100,-120],[130,-90],[70,-30],[140,40],[100,110],[0,70],[-110,120],[-140,20],[-70,-40],[-130,-100],[-70,-120]],gates=[3,5,7,9,11,1],
      shortcut=dict(a=3,b=5,width=12),pickups=[dict(id="b1",kind="boost",x=70,z=-30),dict(id="s1",kind="shield",x=-110,z=120)],
      hazards=[dict(x=135,z=-10,r=2.2),dict(x=65,z=100,r=3.3),dict(x=-72,z=-40,r=3.3)])]
DARK=(29,43,67)
TEAL=(83,232,196)
PINK=(224,122,208)
YELLOW=(255,203,105)


def deco(name,size,pos,color,mat="SmoothPlastic",**kw):
    G.box(name,size,pos,color,mat,collide=False,shadow=False,
          extra='<bool name="CanQuery">false</bool><bool name="CanTouch">false</bool>',**kw)


def arch(name,x,y,z,color,text,width=22,yaw=0):
    with G.Group(name):
        a=math.radians(yaw)
        for side in (-1,1): deco("GatePost",(1,8,1),(x+side*width/2*math.cos(a),y+4,z-side*width/2*math.sin(a)),color,"Neon")
        deco("GateBeam",(width+1,.8,1),(x,y+8,z),color,"Neon",rot=(0,yaw,0))
        G.box("GateLabel",(width,3,.5),(x,y+10,z),DARK,rot=(0,yaw,0),collide=False,text=dict(face="Front",text=text,bg=DARK,bg_t=0))


AGAR=(222,178,92)        # nutrient agar: warm amber floor of the giant petri dish
ROAD=(54,58,66)
CURB_R=(214,64,58)
CURB_W=(236,236,232)
BARRIER=(232,236,240)
COLONY=[(246,228,170),(240,150,120),(170,206,120),(250,214,96),(214,168,226)]


def track(d,index):
    """v59 owner: 'floating outlines in an empty void'. Each track now lies on amber agar inside a giant glass
    petri dish on a lab bench: a real road with barriers, red-white curbs at the corners, a chequered start line,
    colonies as scenery, and a microscope objective overhead as the landmark. Decorative only: the race itself
    runs on RacerData (server physics), so none of this collides with the camera."""
    ox,y,oz=d['origin']; pts=d['points']; color=TEAL if index==0 else PINK
    w=d['width']
    with G.Group("Track_"+d['id']):
        # bench + dish: no more void under the track
        G.box("LabBench",(560,6,560),(ox,y-12,oz),(196,200,204),"Marble")
        deco("BenchEdge",(562,1.2,562),(ox,y-8.6,oz),(70,76,86),"Metal")
        G.disc("DishBase",ox,y-6.5,oz,420,3,(205,226,232),"Glass",transp=.45)
        G.disc("Agar",ox,y-2.1,oz,412,3.2,AGAR,"SmoothPlastic")
        for k in range(48):
            a=k*math.pi*2/48
            deco("DishWall",(28,14,1.2),(ox+math.sin(a)*207,y+1,oz+math.cos(a)*207),(196,226,236),"Glass",
                 transp=.55,rot=(0,math.degrees(a),0))
        # colonies on the agar, outside the road corridors (a fixed pattern, no RNG)
        for k in range(26):
            a=k*2.39996
            r=60+(k*37)%140
            cx,cz=math.sin(a)*r,math.cos(a)*r
            near=min(math.hypot(cx-px,cz-pz) for px,pz in pts)
            on_road=any(_seg_dist(cx,cz,p,q)<w/2+14 for p,q in zip(pts,pts[1:]+pts[:1]))
            if on_road or near<w: continue
            dia=7+(k*13)%16
            G.disc("Colony",ox+cx,y-.35,oz+cz,dia,.9,COLONY[k%len(COLONY)],"SmoothPlastic",collide=False,shadow=False)
            deco("ColonyCore",(dia*.35,.9,dia*.35),(ox+cx,y+.05,oz+cz),tuple(max(0,c-40) for c in COLONY[k%len(COLONY)]))
        # road: segments + corner decks, white edge lines, low barriers, curbs at each corner
        edges=list(zip(pts,pts[1:]+pts[:1]))
        if d.get('shortcut'): edges.append((pts[d['shortcut']['a']-1],pts[d['shortcut']['b']-1]))
        for i,(a,b) in enumerate(edges):
            dx,dz=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dz)
            ww=d['shortcut']['width'] if i==len(pts) else w
            yaw=math.degrees(math.atan2(dx,dz))
            mx,mz=ox+(a[0]+b[0])/2,oz+(a[1]+b[1])/2
            G.box("Road",(ww,1,length+1),(mx,y-.5,mz),ROAD,"Asphalt",rot=(0,yaw,0))
            for side in (-1,1):
                nx,nz=side*dz/length,-side*dx/length
                deco("EdgeLine",(.6,.06,length-4),(mx+nx*(ww/2-1.6),y+.03,mz+nz*(ww/2-1.6)),CURB_W,rot=(0,yaw,0))
                G.box("Barrier",(1.4,1.6,length-ww*.6),(mx+nx*(ww/2+.4),y+.8,mz+nz*(ww/2+.4)),BARRIER,"SmoothPlastic",
                      rot=(0,yaw,0),collide=False)
                deco("BarrierStripe",(1.5,.35,length-ww*.6),(mx+nx*(ww/2+.4),y+1.2,mz+nz*(ww/2+.4)),color,rot=(0,yaw,0))
            for t in (.2,.4,.6,.8):
                deco("LaneDash",(.6,.06,4),(ox+a[0]+dx*t,y+.03,oz+a[1]+dz*t),CURB_W,rot=(0,yaw,0))
        for i,p in enumerate(pts,1):
            G.disc("CornerDeck",ox+p[0],y-.5,oz+p[1],w,1,ROAD,"Asphalt")
            G.part("Waypoint_"+str(i),(1,1,1),(ox+p[0],y+.5,oz+p[1]),DARK,transp=1,collide=False,shadow=False)
            # red-white curb arc on the corner's outer edge
            prv,nxt=pts[i-2],pts[i%len(pts)]
            hin=math.atan2(p[0]-prv[0],p[1]-prv[1]); hout=math.atan2(nxt[0]-p[0],nxt[1]-p[1])
            turn=math.atan2(math.sin(hout-hin),math.cos(hout-hin))
            if abs(turn)<.2: continue
            outer=-1 if turn>0 else 1   # outside of the bend
            mid=(hin+hout)/2+(math.pi if abs(hout-hin)>math.pi else 0)
            for k in range(-3,4):
                a=mid+outer*math.pi/2+k*.16
                deco("Curb",(3.2,.25,2.2),(ox+p[0]+math.sin(a)*(w/2-1),y+.08,oz+p[1]+math.cos(a)*(w/2-1)),
                     CURB_R if k%2 else CURB_W,rot=(0,math.degrees(a),0))
            # v60: tyre stacks behind the barrier on the outside of the bend, a club flag on every other bend
            for k in (-1,1):
                a=mid+outer*math.pi/2+k*.22
                tx,tz=ox+p[0]+math.sin(a)*(w/2+3.2),oz+p[1]+math.cos(a)*(w/2+3.2)
                for h in range(3):
                    G.part("TyreStack",(.9,2.2,2.2),(tx,y+.45+h*.9,tz),(28,30,34) if h!=1 else CURB_R,"SmoothPlastic",
                           shape="Cylinder",rot=(0,0,90),collide=False,shadow=False)
            if i%2==0:
                a=mid+outer*math.pi/2
                fx,fz=ox+p[0]+math.sin(a)*(w/2+7),oz+p[1]+math.cos(a)*(w/2+7)
                G.vcyl("FlagPole",fx,y,y+14,fz,.4,(220,222,226),"Metal",collide=False)
                deco("Flag",(.15,3,5),(fx,y+12.3,fz+2.6),(24,120,80) if (i//2)%2 else color,"Fabric")
        # start / finish: chequered line + a real arch (the last checkpoint is the finish, not "point 5")
        a,b=pts[0],pts[1]
        yaw=math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))
        hx,hz=math.cos(math.radians(yaw)),-math.sin(math.radians(yaw))
        for k in range(-int(w/2/2),int(w/2/2)):
            for r in (0,1):
                deco("StartChequer",(2,.07,2),(ox+a[0]+hx*(k*2+1)+(r*2-1)*math.sin(math.radians(yaw)),y+.04,
                     oz+a[1]+hz*(k*2+1)+(r*2-1)*math.cos(math.radians(yaw))),
                     (20,20,24) if (k+r)%2 else (240,240,240),rot=(0,yaw,0))
        # v60 start gantry: StartLight_1..3 are lit by Racers.client during the countdown (red, red, red, green)
        for sd in (-1,1):
            G.vcyl("GantryPost",ox+a[0]+hx*sd*(w/2+1.2),y,y+11,oz+a[1]+hz*sd*(w/2+1.2),1.0,(60,64,74),"Metal",collide=False)
        G.box("GantryBeam",(w+3.4,1.4,1.4),(ox+a[0],y+11,oz+a[1]),(60,64,74),"Metal",rot=(0,yaw,0),collide=False)
        for k in (1,2,3):
            G.part("StartLight_%d"%k,(1.6,1.6,1.6),(ox+a[0]+hx*(k-2)*2.6,y+9.6,oz+a[1]+hz*(k-2)*2.6),(50,20,20),
                   "SmoothPlastic",shape="Ball",collide=False,shadow=False)
        # grandstand on the outside of the start straight, facing the track
        gx,gz=ox+a[0]-hx*(w/2+12)+math.sin(math.radians(yaw))*30,oz+a[1]-hz*(w/2+12)+math.cos(math.radians(yaw))*30
        for t_ in range(3):
            G.box("Grandstand",(5,1.2+t_*1.4,34),(gx-hx*t_*4.2,y+(1.2+t_*1.4)/2,gz-hz*t_*4.2),
                  (70,76,90) if t_%2==0 else (90,96,110),"Concrete",rot=(0,yaw,0),collide=False)
            for q in range(6):
                fan=((240,180,80),(90,190,240),(230,110,140),(140,220,140))[(q+t_)%4]
                off=-14+q*5.6
                G.box("Fan",(1,1.6,1),(gx-hx*t_*4.2+math.sin(math.radians(yaw))*off,y+2+t_*1.4,
                      gz-hz*t_*4.2+math.cos(math.radians(yaw))*off),fan,"SmoothPlastic",collide=False,shadow=False)
        G.box("GrandstandRoof",(16,.5,36),(gx-hx*4.2,y+9,gz-hz*4.2),(236,238,242),"SmoothPlastic",rot=(0,yaw,0),
              collide=False)
        for i,g in enumerate(d['gates'],1):
            p=pts[g-1]
            nxt=pts[g%len(pts)]
            last=i==len(d['gates'])
            arch("Checkpoint_"+str(i),ox+p[0],y,oz+p[1],(240,240,240) if last else color,
                 "خط النهاية • FINISH" if last else "بوابة %d"%i,width=w,
                 yaw=math.degrees(math.atan2(nxt[0]-p[0],nxt[1]-p[1])))
        for p in d['pickups']:
            G.disc("Pickup_"+p['id'],ox+p['x'],y+.12,oz+p['z'],9,.2,(80,182,246) if p['kind']=='boost' else (173,146,246),"Neon",collide=False,shadow=False)
            if p['kind']=='boost':
                for k in (-1,0,1):
                    deco("PickupArrow",(1,.08,3),(ox+p['x']+k*2.2,y+.25,oz+p['z']),(255,255,255))
        for p in d['hazards']:
            G.ball("SporeObstacle",ox+p['x'],y+1.5,oz+p['z'],p['r']*2,(247,153,111),"SmoothPlastic",collide=False)
            for k in range(6):
                a=k*math.pi/3
                deco("SporeSpike",(.5,.5,p['r']*1.2),(ox+p['x']+math.sin(a)*p['r'],y+1.5,oz+p['z']+math.cos(a)*p['r']),
                     (200,100,80),rot=(0,math.degrees(a),0))
        if d.get('shortcut'):
            G.sign("ShortcutGuide","اختصار ضيق",(ox+110,y+7,oz-70),(14,3,.5),"Front",bg=DARK)
        # landmark: a microscope objective hanging over the dish (you are racing under the microscope)
        lx,lz=ox+120,oz+150
        G.vcyl("Objective",lx,y+70,y+130,lz,26,(226,228,232),"Metal",collide=False)
        G.vcyl("ObjectiveRing",lx,y+66,y+70,lz,22,color,"SmoothPlastic",collide=False)
        G.vcyl("ObjectiveLens",lx,y+64,y+66,lz,14,(150,205,230),"Glass",transp=.3,collide=False)
        G.sign("TrackTitle",d['ar']+"\nMICRO RACERS",(ox,y+16,oz-200),(46,8,.6),"Front",bg=DARK)


def _seg_dist(x,z,a,b):
    dx,dz=b[0]-a[0],b[1]-a[1]
    t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)))
    return math.hypot(x-(a[0]+dx*t),z-(a[1]+dz*t))


def kart(x,y,z):
    """v60 original lab go-kart (front = +Z, ground = y). Racers.client animates parts by name:
    Body/Paint* = car colour, Liquid = accent, Wheel_<FL|FR|RL|RR>[_Hub] spin (front ones steer), SteeringWheel turns,
    Exhaust_L/R carry the turbo flames. Chibi proportions: big wheels (rear 1.3x front), low rounded tub, a big-headed
    scientist driver, a glass bioreactor flask as the engine."""
    DARK_=(40,44,52); GREY=(214,218,224); RUBBER=(30,32,38)
    def d(name,size,pos,col,mat="SmoothPlastic",**kw):
        deco(name,size,(x+pos[0],y+pos[1],z+pos[2]),col,mat,**kw)
    def cyl(name,size,pos,col,mat="SmoothPlastic",rot=(0,0,0),**kw):
        G.part(name,size,(x+pos[0],y+pos[1],z+pos[2]),col,mat,shape="Cylinder",rot=rot,collide=False,shadow=False,**kw)
    def ball(name,dia,pos,col,mat="SmoothPlastic",**kw):
        G.part(name,(dia,dia,dia),(x+pos[0],y+pos[1],z+pos[2]),col,mat,shape="Ball",collide=False,shadow=False,**kw)
    # chassis: low tub, rounded side pods, ball nose, bumper, floor pan
    d("Floor",(4.6,.3,7.4),(0,.55,0),DARK_)
    d("Body",(3.8,.9,6.4),(0,1.15,0),TEAL)
    for sx in (-1,1):
        cyl("PaintPod",(6.0,1.5,1.5),(sx*2.0,1.1,.1),TEAL,rot=(0,90,0))
    ball("PaintNose",2.5,(0,1.15,3.3),TEAL)
    cyl("Bumper",(5.4,.8,.8),(0,.8,4.35),GREY)
    G.box("Plate",(2.2,.7,.1),(x,y+1.55,z+4.55),DARK_,collide=False,shadow=False,
          text=dict(face="Back",text="BSC",color=(255,255,255),bg=DARK_,bg_t=0.0))
    d("Dash",(3.4,.7,.6),(0,2.0,1.4),DARK_)
    cyl("SteeringColumn",(1.2,.3,.3),(0,2.45,1.0),DARK_,rot=(0,90,0))
    cyl("SteeringWheel",(.25,1.5,1.5),(0,2.9,.45),DARK_,rot=(0,90,0))
    # seat + scientist driver (lab coat, big head, helmet in the car colour, goggles)
    d("Seat",(2.4,.6,2.2),(0,1.75,-.9),DARK_)
    d("SeatBack",(2.4,2.2,.5),(0,2.65,-2.05),DARK_)
    d("Coat",(1.9,1.7,1.3),(0,2.85,-1.1),(244,246,248))
    for sx in (-1,1):
        d("Arm",(.45,.45,1.5),(sx*.8,3.05,-.2),(244,246,248))
    ball("Head",1.7,(0,4.3,-1.05),(234,192,160))
    ball("PaintHelmet",1.86,(0,4.55,-1.2),TEAL)
    d("Goggles",(1.75,.38,.25),(0,4.4,-.25),(70,180,230),"Glass",transp=.15)
    # rear: engine block, glass bioreactor with coloured medium, twin exhausts, spoiler
    d("Engine",(3.0,1.2,1.6),(0,1.6,-3.0),(120,126,136),"Metal")
    cyl("Flask",(2.2,1.7,1.7),(0,2.95,-3.1),(200,235,245),"Glass",rot=(0,0,90),transp=.35)
    cyl("Liquid",(1.5,1.35,1.35),(0,2.8,-3.1),YELLOW,rot=(0,0,90))
    ball("FlaskCap",.8,(0,4.15,-3.1),GREY,"Metal")
    for sx,tag in ((-1,"L"),(1,"R")):
        cyl("Exhaust_"+tag,(1.6,.6,.6),(sx*1.0,1.4,-4.0),(90,94,104),"Metal",rot=(0,90,0))
        d("SpoilerPost",(.3,1.4,.3),(sx*1.6,3.2,-3.9),DARK_)
    d("PaintSpoiler",(5.0,.25,1.3),(0,3.95,-4.0),TEAL)
    # wheels: cylinders spin about their own X axis; hubs ride with them
    for tag,sx,zz,dia,w in (("FL",-1,2.7,2.0,1.1),("FR",1,2.7,2.0,1.1),("RL",-1,-2.6,2.6,1.4),("RR",1,-2.6,2.6,1.4)):
        px=sx*(2.75 if tag[0]=="F" else 2.95)
        cyl("Wheel_"+tag,(w,dia,dia),(px,dia/2,zz),RUBBER)
        cyl("Wheel_"+tag+"_Hub",(w+.06,dia*.5,dia*.5),(px,dia/2,zz),GREY,"Metal")
        d("Wheel_"+tag+"_Spoke",(w+.1,dia*.62,.25),(px,dia/2,zz),GREY,"Metal")


def build():
    with G.Group("Racers47"):
        # Entrance fits inside the existing Arcade floor; the racing lobby is outside random-round selection.
        with G.Group("Entry"):
            import arcade59   # v59: a matching gateway on the lobby arc
            arcade59.gateway("Racers","RaceEntrance")
        with G.Group("Lobby"):
            G.box("LobbyFloor",(100,2,80),(-7400,299,-6000),DARK,"Concrete")
            G.part("RaceLobbySpawn",(8,1,8),(-7400,300.5,-6000),TEAL,transp=1,collide=False)
            arch("ReturnGate",-7400,300,-5970,PINK,"العودة للأركيد",width=12)
            G.part("RaceExit",(10,9,2),(-7400,304.5,-5970),PINK,"Neon",transp=.6,collide=False)
            G.sign("RaceRules","سباق مركبات في عالم مجهري خيالي\n3 لفات • وجّه وسرّع وفرمل\nالدرع يحمي من عائق واحد • السرعة مؤقتة",(-7400,309,-6026),(48,11,.5),"Back",bg=DARK)
            G.part("RaceConsole",(10,4,4),(-7400,302,-6014),TEAL,"Metal")
        with G.Group("VehicleTemplate","Model"):
            kart(-7400,250,-6000)
        for i,d in enumerate(TRACKS): track(d,i)


def write_data(path):
    """Keep visible roads, AI and authoritative collision/checkpoint data generated from one definition."""
    def lua(v):
        if isinstance(v,dict): return '{'+','.join('['+json.dumps(k,ensure_ascii=False)+']='+lua(x) for k,x in v.items())+'}'
        if isinstance(v,list): return '{'+','.join(lua(x) for x in v)+'}'
        return json.dumps(v,ensure_ascii=False)
    data=dict(Laps=3,Duration=180,MaxPlayers=8,Lobby=[-7400,303,-6000],Tracks=TRACKS)
    with open(path,'w',encoding='utf-8') as f:
        f.write('-- Generated by tools/racers47.py; canonical geometry and driving data.\nlocal D='+lua(data)+'\n')
        f.write('function D.get(id) for _,track in ipairs(D.Tracks) do if track.id==id then return track end end return nil end\nreturn D\n')
