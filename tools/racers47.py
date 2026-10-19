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


def track(d,index):
    ox,y,oz=d['origin']; pts=d['points']; color=TEAL if index==0 else PINK
    with G.Group("Track_"+d['id']):
        G.box("CytoplasmBase",(340,3,300),(ox,y-5,oz),(40,62,82),"Slate")
        # Broad overlapping deck segments follow exactly the same corridors used by server physics.
        edges=list(zip(pts,pts[1:]+pts[:1]))
        if d.get('shortcut'): edges.append((pts[d['shortcut']['a']-1],pts[d['shortcut']['b']-1]))
        for i,(a,b) in enumerate(edges):
            dx,dz=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dz)
            w=d['shortcut']['width'] if i==len(pts) else d['width']
            yaw=math.degrees(math.atan2(dx,dz))
            G.box("Road",(w,1,length+1),(ox+(a[0]+b[0])/2,y-.5,oz+(a[1]+b[1])/2),DARK,"Asphalt",rot=(0,yaw,0))
            for side in (-1,1):
                x=ox+(a[0]+b[0])/2+side*dz/length*w/2
                z=oz+(a[1]+b[1])/2-side*dx/length*w/2
                deco("MembraneRail",(.6,1.6,length+1),(x,y+.8,z),color,"Neon",rot=(0,yaw,0))
            for t in (.25,.5,.75):
                deco("LaneGuide",(.7,.08,3),(ox+a[0]+dx*t,y+.03,oz+a[1]+dz*t),(210,220,227),rot=(0,yaw,0))
        for i,p in enumerate(pts,1):
            G.disc("CornerDeck",ox+p[0],y-.5,oz+p[1],d["width"],1,DARK,"Asphalt")
            G.part("Waypoint_"+str(i),(1,1,1),(ox+p[0],y+.5,oz+p[1]),DARK,transp=1,collide=False,shadow=False)
        for i,g in enumerate(d['gates'],1):
            p=pts[g-1]
            nxt=pts[g%len(pts)]
            arch("Checkpoint_"+str(i),ox+p[0],y,oz+p[1],color,"نقطة %d"%i,width=d['width'],yaw=math.degrees(math.atan2(nxt[0]-p[0],nxt[1]-p[1])))
        for p in d['pickups']:
            G.disc("Pickup_"+p['id'],ox+p['x'],y+.12,oz+p['z'],9,.2,(80,182,246) if p['kind']=='boost' else (173,146,246),"Neon",collide=False,shadow=False)
            G.sign("PickupGuide","سرعة ↑" if p['kind']=='boost' else "درع ◇",(ox+p['x'],y+5,oz+p['z']),(8,2,.4),"Front",bg=DARK)
        for p in d['hazards']:
            G.ball("SporeObstacle",ox+p['x'],y+1.5,oz+p['z'],p['r']*2,(247,153,111),"SmoothPlastic",collide=False)
        if d.get('shortcut'):
            G.sign("ShortcutGuide","اختصار ضيق ↗\nالبوابات بالترتيب",(ox+110,y+9,oz-70),(22,5,.5),"Front",bg=DARK)
        # Large cells and molecular structures outside the drivable lanes, all original primitives.
        for j,(x,z) in enumerate(((0,0),(-155,-140),(155,140),(-155,140),(155,-140))):
            diam=25 if j==0 else 16
            G.ball("Cell",ox+x,y+diam*.55,oz+z,diam,(90,151,156) if index==0 else (137,107,160),"Glass",transp=.35,collide=False,shadow=False)
            G.ball("CellNucleus",ox+x,y+diam*.55,oz+z,diam*.35,color,"SmoothPlastic",collide=False,shadow=False)
        for j in range(12):
            a=j*.65
            for side in (-1,1): G.ball("DNA_Node",ox+side*math.cos(a)*6,y+5+j*1.8,oz+side*math.sin(a)*6,.9,color if side==1 else YELLOW,"Neon",collide=False,shadow=False)
        G.sign("TrackTitle",d['ar']+"\nMICRO RACERS",(ox,y+18,oz-150),(50,8,.6),"Front",bg=DARK)


def build():
    with G.Group("Racers47"):
        # Entrance fits inside the existing Arcade floor; the racing lobby is outside random-round selection.
        with G.Group("Entry"):
            arch("ArcadeRaceGate",-5972,300,-5982,TEAL,"سباق العالم المجهري",width=10)
            G.part("RaceEntrance",(8,9,2),(-5972,304.5,-5982),TEAL,"Neon",transp=.55,collide=False,shadow=False)
        with G.Group("Lobby"):
            G.box("LobbyFloor",(100,2,80),(-7400,299,-6000),DARK,"Concrete")
            G.part("RaceLobbySpawn",(8,1,8),(-7400,300.5,-6000),TEAL,transp=1,collide=False)
            arch("ReturnGate",-7400,300,-5970,PINK,"العودة للأركيد",width=12)
            G.part("RaceExit",(10,9,2),(-7400,304.5,-5970),PINK,"Neon",transp=.6,collide=False)
            G.sign("RaceRules","سباق مركبات في عالم مجهري خيالي\n3 لفات • وجّه وسرّع وفرمل\nالدرع يحمي من عائق واحد • السرعة مؤقتة",(-7400,309,-6026),(48,11,.5),"Back",bg=DARK)
            G.part("RaceConsole",(10,4,4),(-7400,302,-6014),TEAL,"Metal")
        with G.Group("VehicleTemplate","Model"):
            x,y,z=-7400,250,-6000
            deco("Body",(5.5,1.1,7),(x,y+1.3,z),TEAL,"Metal")
            deco("Nose",(4,1,2),(x,y+1.4,z+3.5),YELLOW)
            G.ball("CellCockpit",x,y+2.6,z,3.4,(133,216,225),"Glass",transp=.35,collide=False,shadow=False)
            G.ball("DriverNucleus",x,y+2.6,z,1.3,(54,69,91),collide=False,shadow=False)
            for side in (-1,1):
                for dz in (-2.1,2.1):
                    G.part("Wheel",(1,1.8,1.8),(x+side*3,y+.9,z+dz),(29,34,44),"Rubber" if "Rubber" in G.MAT else "SmoothPlastic",shape="Cylinder",collide=False,shadow=False)
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
