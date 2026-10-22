"""Static fictional micro raceways and the canonical shared driving layout. No existing parts are modified."""
import json
import math
import genmap as G

import racetrack61 as RT

WIDTH = 28


def _rotate_to_start(pts):
    """start a third of the way down the longest straight, so the grid (4 rows behind) sits on the straight"""
    best, run, start = 0, 0, 0
    for i in range(len(pts)):
        dh = abs((pts[i][2] - pts[i - 1][2] + math.pi) % (2 * math.pi) - math.pi)
        run = run + 1 if dh < 1e-3 else 0
        if run > best:
            best, start = run, i - run + 1
    k = (start + best // 3) % len(pts)
    return pts[k:] + pts[:k]


def _shortcut(pts, w):
    """a narrow risky cut: two points far apart along the track but close in space, whose straight link stays clear
    of every other part of the road; saves ~1.5 s if you thread it"""
    n = len(pts)
    best = None
    for i in range(0, n, 2):
        for j in range(i + 20, min(n, i + 130), 2):
            d = math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
            saving = (j - i) * RT.STEP - d
            if d < 36 or saving < 35 or saving > 200:
                continue
            ok = True
            for k in range(n):
                if i - 4 <= k <= j + 4:
                    continue
                ax, az, bx, bz = pts[i][0], pts[i][1], pts[j][0], pts[j][1]
                t = max(0, min(1, ((pts[k][0] - ax) * (bx - ax) + (pts[k][1] - az) * (bz - az)) / (d * d)))
                if math.hypot(pts[k][0] - (ax + (bx - ax) * t), pts[k][1] - (az + (bz - az) * t)) < w + 8:
                    ok = False
                    break
            if ok and (best is None or abs(saving - 80) < abs(best[2] - 80)):
                best = (i, j, saving)
    return best


def _make_track(tid, ar, desc, origin, n_gates, shortcut):
    pts = _rotate_to_start(RT.fillet(RT.POLYS[tid]))
    n = len(pts)
    gates = [int(round(n * (g + 1) / n_gates)) % n + 1 for g in range(n_gates)]   # 1-based; the last one is the line
    gates[-1] = 1
    d = dict(id=tid, ar=ar, desc=desc, origin=origin, width=WIDTH,
             points=[[round(p[0], 2), round(p[1], 2)] for p in pts], gates=gates)

    def at(frac, lateral=0.0):
        p = pts[int(n * frac) % n]
        return p[0] + math.cos(p[2]) * lateral, p[1] - math.sin(p[2]) * lateral

    bx, bz = at(0.36)
    sx, sz = at(0.72, 4)
    d['pickups'] = [dict(id="b1", kind="boost", x=round(bx, 1), z=round(bz, 1)),
                    dict(id="s1", kind="shield", x=round(sx, 1), z=round(sz, 1))]
    d['hazards'] = [dict(x=round(at(f, lat)[0], 1), z=round(at(f, lat)[1], 1), r=3.0)
                    for f, lat in ((0.22, 5), (0.55, -5), (0.86, 4))]
    if shortcut:
        sc = _shortcut(pts, WIDTH)
        if sc:
            d['shortcut'] = dict(a=sc[0] + 1, b=sc[1] + 1, width=12)
            SHORTCUT_INFO[tid] = sc
    return d


SHORTCUT_INFO = {}
TRACKS = [
    _make_track("cell", "حلبة الخلية", "منعطفات طويلة للانجراف ومستقيم كبير للتجاوز؛ مناسبة للبداية",
                [-8200, 300, -6000], 6, False),
    _make_track("helix", "منعطفات الجزيئات", "منعطفات متعرجة ودبابيس شعر للمحترفين",
                [-8200, 300, -6800], 6, True),
]
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
    """v61 (owner: "extra pieces, not closed, lanes not lined up"): the road, edges, barriers and curbs are built from the
    same dense centreline the physics uses (racetrack61), segment by segment with small overlaps, so the ribbon is
    closed and every barrier follows the drivable edge exactly. Corners get curbs + chevrons, each sector a landmark."""
    ox,y,oz=d['origin']; pts=d['points']; n=len(pts); color=TEAL if index==0 else PINK
    w=d['width']; hw=w/2
    head=[math.atan2(pts[(i+1)%n][0]-pts[i][0],pts[(i+1)%n][1]-pts[i][1]) for i in range(n)]
    def turn(i):
        return (head[i]-head[i-1]+math.pi)%(2*math.pi)-math.pi
    R=max(math.hypot(p[0],p[1]) for p in pts)+45
    with G.Group("Track_"+d['id']):
        # bench + dish sized to the circuit
        G.box("LabBench",(2*R+160,6,2*R+160),(ox,y-12,oz),(196,200,204),"Marble")
        deco("BenchEdge",(2*R+162,1.2,2*R+162),(ox,y-8.6,oz),(70,76,86),"Metal")
        G.disc("DishBase",ox,y-6.5,oz,2*R+8,3,(205,226,232),"Glass",transp=.45)
        G.disc("Agar",ox,y-2.1,oz,2*R,3.2,AGAR,"SmoothPlastic")
        segs=int(2*math.pi*R/24)
        for k in range(segs):
            a=k*math.pi*2/segs
            deco("DishWall",(2*math.pi*R/segs+1,14,1.2),(ox+math.sin(a)*(R+3),y+1,oz+math.cos(a)*(R+3)),(196,226,236),"Glass",
                 transp=.55,rot=(0,math.degrees(a),0))
        # the ribbon: road, edge lines and barriers per piece (straight runs merged, bends per 6-stud segment,
        # overlap 0.8 studs: no seams, no gaps)
        pieces=[]
        i=0
        while i<n:
            j=i+1
            while j<n and abs(turn(j))<1e-3 and abs(turn(i+1 if i+1<n else 0))<1e-3:
                j+=1
            pieces.append((i,j))
            i=j
        for (i,j) in pieces:
            a_,b_=pts[i],pts[j%n]
            dx,dz=b_[0]-a_[0],b_[1]-a_[1]
            L=math.hypot(dx,dz)
            yaw=math.degrees(head[i])
            mx,mz=ox+(a_[0]+b_[0])/2,oz+(a_[1]+b_[1])/2
            nx,nz=dz/L,-dx/L
            # the outer edge of a bend opens by (half width x angle): extend each piece by that much so it stays closed
            ext=(hw+2.5)*max(abs(turn(i)),abs(turn(j%n)))+0.8
            G.box("Road",(w,1,L+ext),(mx,y-.5,mz),ROAD,"Asphalt",rot=(0,yaw,0))
            bend=abs(turn(i))>0.02 or (j-i==1 and abs(turn(j%n))>0.02)
            for side in (-1,1):
                if not bend:
                    deco("EdgeLine",(.6,.06,L+0.6),(mx+side*nx*(hw-1.6),y+.03,mz+side*nz*(hw-1.6)),CURB_W,rot=(0,yaw,0))
                G.box("Barrier",(1.4,1.6,L+ext+0.1),(mx+side*nx*(hw+.7),y+.8,mz+side*nz*(hw+.7)),BARRIER,"SmoothPlastic",
                      rot=(0,yaw,0),collide=False)
                if not bend or i%2==0:
                    deco("BarrierStripe",(1.5,.35,L+ext+0.1),(mx+side*nx*(hw+.7),y+1.2,mz+side*nz*(hw+.7)),color,rot=(0,yaw,0))
                if bend:   # curbs on both edges through every bend, alternating red/white
                    deco("Curb",(2.6,.22,L+0.4),(mx+side*nx*(hw-0.4),y+.07,mz+side*nz*(hw-0.4)),
                         CURB_R if i%2 else CURB_W,rot=(0,yaw,0))
            if not bend:
                for q in range(int(L//24)):
                    f=(q+0.5)/max(1,int(L//24))
                    deco("LaneDash",(.6,.06,3.2),(ox+a_[0]+dx*f,y+.03,oz+a_[1]+dz*f),CURB_W,rot=(0,yaw,0))
        # chevrons outside the sharp bends, facing the drivers coming in
        i=0
        while i<n:
            if abs(turn(i))>0.02:
                j=i
                total=0.0
                while j<n and abs(turn(j))>0.02:
                    total+=turn(j); j+=1
                if abs(total)>math.radians(55):
                    side=-1 if total>0 else 1   # outside of the bend
                    for k in range(i,j,max(1,(j-i)//4)):
                        p=pts[k]; hk=head[k]
                        nx,nz=math.cos(hk),-math.sin(hk)
                        cx,cz=ox+p[0]+side*nx*(hw+3.2),oz+p[1]+side*nz*(hw+3.2)
                        G.box("Chevron",(3.2,2.2,.3),(cx,y+2.2,cz),(255,214,60),"SmoothPlastic",rot=(0,math.degrees(hk)+180,0),
                              collide=False,text=dict(face="Front",text="»" if side<0 else "«",color=(30,30,30),bg=(255,214,60),bg_t=0))
                        G.vcyl("ChevronPost",cx,y,y+1.2,cz,.3,(60,64,74),"Metal",collide=False)
                    mid=pts[(i+j)//2]; hm=head[(i+j)//2]
                    tx,tz=ox+mid[0]+side*math.cos(hm)*(hw+9),oz+mid[1]-side*math.sin(hm)*(hw+9)
                    for h_ in range(3):
                        G.part("TyreStack",(.9,2.2,2.2),(tx,y+.45+h_*.9,tz),(28,30,34) if h_!=1 else CURB_R,"SmoothPlastic",
                               shape="Cylinder",rot=(0,0,90),collide=False,shadow=False)
                i=j
            else:
                i+=1
        # start/finish: chequered line + gantry with StartLight_1..3 + grandstand beside the straight
        p0,p1=pts[0],pts[1]
        yaw=math.degrees(head[0])
        hx,hz=math.cos(head[0]),-math.sin(head[0])
        for k in range(-int(hw/2),int(hw/2)):
            for r in (0,1):
                deco("StartChequer",(2,.07,2),(ox+p0[0]+hx*(k*2+1)+(r*2-1)*math.sin(head[0]),y+.04,
                     oz+p0[1]+hz*(k*2+1)+(r*2-1)*math.cos(head[0])),(20,20,24) if (k+r)%2 else (240,240,240),rot=(0,yaw,0))
        for sd in (-1,1):
            G.vcyl("GantryPost",ox+p0[0]+hx*sd*(hw+2.4),y,y+11,oz+p0[1]+hz*sd*(hw+2.4),1.0,(60,64,74),"Metal",collide=False)
        G.box("GantryBeam",(w+5.8,1.4,1.4),(ox+p0[0],y+11,oz+p0[1]),(60,64,74),"Metal",rot=(0,yaw,0),collide=False)
        for k in (1,2,3):
            G.part("StartLight_%d"%k,(1.6,1.6,1.6),(ox+p0[0]+hx*(k-2)*2.6,y+9.6,oz+p0[1]+hz*(k-2)*2.6),(50,20,20),
                   "SmoothPlastic",shape="Ball",collide=False,shadow=False)
        gp=pts[int(n*0.06)]; gh=head[int(n*0.06)]
        gx,gz=ox+gp[0]-math.cos(gh)*(hw+14),oz+gp[1]+math.sin(gh)*(hw+14)
        for t_ in range(3):
            G.box("Grandstand",(5,1.2+t_*1.4,40),(gx-math.cos(gh)*t_*4.2,y+(1.2+t_*1.4)/2,gz+math.sin(gh)*t_*4.2),
                  (70,76,90) if t_%2==0 else (90,96,110),"Concrete",rot=(0,math.degrees(gh),0),collide=False)
            for q in range(7):
                fan=((240,180,80),(90,190,240),(230,110,140),(140,220,140))[(q+t_)%4]
                off=-16+q*5.4
                G.box("Fan",(1,1.6,1),(gx-math.cos(gh)*t_*4.2+math.sin(gh)*off,y+2+t_*1.4,gz+math.sin(gh)*t_*4.2+math.cos(gh)*off),
                      fan,"SmoothPlastic",collide=False,shadow=False)
        G.box("GrandstandRoof",(16,.5,42),(gx-math.cos(gh)*4.2,y+9,gz+math.sin(gh)*4.2),(236,238,242),"SmoothPlastic",
              rot=(0,math.degrees(gh),0),collide=False)
        # checkpoint arches: posts outside the barriers, the last one is the finish
        for i_,g in enumerate(d['gates'],1):
            p=pts[g-1]
            last=i_==len(d['gates'])
            if last:
                continue   # the gantry is the finish line
            arch("Checkpoint_"+str(i_),ox+p[0],y,oz+p[1],color,"بوابة %d"%i_,width=w+5,yaw=math.degrees(head[g-1]))
        for pk in d['pickups']:
            G.disc("Pickup_"+pk['id'],ox+pk['x'],y+.12,oz+pk['z'],9,.2,(80,182,246) if pk['kind']=='boost' else (173,146,246),"Neon",collide=False,shadow=False)
        for hz_ in d['hazards']:
            G.ball("SporeObstacle",ox+hz_['x'],y+1.5,oz+hz_['z'],hz_['r']*2,(247,153,111),"SmoothPlastic",collide=False)
        if d.get('shortcut'):
            sc=d['shortcut']; a_,b_=pts[sc['a']-1],pts[sc['b']-1]
            dx,dz=b_[0]-a_[0],b_[1]-a_[1]; L=math.hypot(dx,dz); yaw=math.degrees(math.atan2(dx,dz))
            G.box("ShortcutRoad",(sc['width'],1,L),(ox+(a_[0]+b_[0])/2,y-.45,oz+(a_[1]+b_[1])/2),(84,64,56),"Ground",rot=(0,yaw,0))
            for side in (-1,1):
                nx,nz=dz/L,-dx/L
                deco("ShortcutEdge",(.5,.3,L-28),(ox+(a_[0]+b_[0])/2+side*nx*(sc['width']/2),y+.15,oz+(a_[1]+b_[1])/2+side*nz*(sc['width']/2)),
                     (255,214,60),rot=(0,yaw,0))
        # colonies on the agar (outside every road corridor), sector landmarks: big organelles off the road
        def clear(x,z,m):
            return all(math.hypot(x-p[0],z-p[1])>hw+m for p in pts[::2])
        for k in range(60):
            a=k*2.39996; r=40+(k*53)%int(R-40)
            cx,cz=math.sin(a)*r,math.cos(a)*r
            if not clear(cx,cz,14): continue
            dia=7+(k*13)%18
            G.disc("Colony",ox+cx,y-.35,oz+cz,dia,.9,COLONY[k%len(COLONY)],"SmoothPlastic",collide=False,shadow=False)
            deco("ColonyCore",(dia*.35,.9,dia*.35),(ox+cx,y+.05,oz+cz),tuple(max(0,c-40) for c in COLONY[k%len(COLONY)]))
        marks=0
        for k,(fn,frac) in enumerate(((_mito,0.15),(_nucleus,0.45),(_ribosomes,0.75))):
            p=pts[int(n*frac)]; hk=head[int(n*frac)]
            for dist in (60,80,100,-60,-80,-100):
                cx,cz=p[0]+math.cos(hk)*dist,p[1]-math.sin(hk)*dist
                if clear(cx,cz,34) and math.hypot(cx,cz)<R-30:
                    fn(ox+cx,y,oz+cz,color); marks+=1; break
        G.sign("TrackTitle",d['ar']+"\nMICRO RACERS",(ox,y+16,oz-R-10),(46,8,.6),"Front",bg=DARK)
        LANDMARKS_PLACED[d['id']]=marks


LANDMARKS_PLACED={}


def _mito(x,y,z,col):
    """sector landmark: a giant mitochondrion lying on the agar"""
    G.part("MitoBody",(36,14,14),(x,y+7,z),(240,130,70),"SmoothPlastic",shape="Cylinder",collide=False)
    for e in (-1,1): G.ball("MitoEnd",x+e*18,y+7,z,14,(240,130,70),"SmoothPlastic",collide=False)
    for q in (-12,-4,4,12): deco("MitoCrista",(1,11,12),(x+q,y+7,z),(255,210,120),"Neon")


def _nucleus(x,y,z,col):
    """sector landmark: a nucleus dome with a glowing nucleolus"""
    G.ball("NucleusDome",x,y+4,z,40,(150,110,220),"Glass",transp=.35,collide=False,shadow=False)
    G.ball("Nucleolus",x,y+8,z,13,(90,50,170),"Neon",collide=False,shadow=False)


def _ribosomes(x,y,z,col):
    """sector landmark: a cluster of ribosomes on a strand of mRNA"""
    for q in range(6):
        G.ball("RiboLarge",x-25+q*10,y+6,z,7,(110,200,150),"SmoothPlastic",collide=False)
        G.ball("RiboSmall",x-25+q*10,y+11,z,4.5,(90,170,130),"SmoothPlastic",collide=False)
    deco("mRNA",(64,.8,.8),(x,y+3.5,z),(255,214,60),"Neon")


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


def pit_lobby():
    """v63 (owner audit: "a dark, empty floor with only a text board"): the lobby is a racing pit. A three-bay garage
    with a display kart in the side bays, a glowing mini map of each track on either side of the console, an asphalt
    pit lane with a chequered start line, floodlight towers, tyre stacks, flags and a podium. The long rules board is
    gone (the help button and the race HUD explain the controls). Scripted parts (RaceConsole, RaceExit,
    RaceLobbySpawn) are untouched."""
    cx, y, cz = -7400.0, 300.0, -6000.0
    ASPH, LINE, WHITE, BLACK = (80, 84, 94), (236, 236, 232), (240, 240, 236), (24, 24, 28)
    G.box("PitAsphalt", (96, 0.1, 76), (cx, y + 0.05, cz), ASPH, "Asphalt", collide=False, shadow=False)
    for k in (-1, 1):
        deco("PitLaneLine", (0.6, 0.06, 60), (cx + k * 24, y + 0.12, cz + 4), LINE)
    for i in range(20):   # chequered start line between the spawn and the console
        for j in range(2):
            deco("StartChequer", (2, 0.06, 2), (cx - 19 + i * 2, y + 0.13, cz - 8 + j * 2), WHITE if (i + j) % 2 else BLACK)
    for sx in (-1, 1):   # neon edge round the pit
        deco("PitEdge", (0.5, 0.12, 78), (cx + sx * 49.5, y + 0.14, cz), TEAL, "Neon")
    deco("PitEdge", (100, 0.12, 0.5), (cx, y + 0.14, cz + 39.5), TEAL, "Neon")
    # the garage: back wall, roof, three bays; a display kart on a lit turntable in the two side bays
    G.box("GarageBack", (90, 18, 2), (cx, y + 9, cz - 39), (40, 46, 60), "SmoothPlastic")
    G.box("GarageRoof", (92, 1.4, 14), (cx, y + 18.6, cz - 33), (30, 34, 46), "Metal")
    deco("GarageRoofGlow", (92, 0.3, 0.4), (cx, y + 17.8, cz - 26.2), TEAL, "Neon")
    for k, (bx, col) in enumerate(((-30, TEAL), (0, PINK), (30, YELLOW))):
        x = cx + bx
        if k < 2:
            G.box("BayDivider", (1.2, 18, 12), (x + 15, y + 9, cz - 33), (60, 66, 82), "SmoothPlastic")
        deco("BayAccent", (26, 2, 0.4), (x, y + 13, cz - 37.8), col, "Neon")
        G.part("BayLamp", (1, 1, 1), (x, y + 16, cz - 31), (0, 0, 0), "SmoothPlastic", transp=1, collide=False,
               shadow=False, light=(1.4, 26, (255, 246, 230)))
        # raised turntables so the karts show over the map tables in front
        G.vcyl("TurntableBase", x, y, y + 3.4, cz - 31, 14, (50, 56, 72), "SmoothPlastic")
        G.disc("Turntable", x, y + 3.5, cz - 31, 13, 0.3, (70, 76, 92), "Metal", collide=False, shadow=False)
        G.disc("TurntableRing", x, y + 3.45, cz - 31, 14.4, 0.2, col, "Neon", collide=False, shadow=False)
        if bx != 0:   # the middle bay stays open behind the console
            with G.Group("DisplayKart", "Model"):
                kart(x, y + 3.7, cz - 31)
    G.sign("RaceTitle", "سباق الميكرو | Micro Racers", (cx, y + 22, cz - 25.8), (44, 5, 0.5), "Back", bg=(20, 26, 40))
    # the two tracks as glowing mini maps on tables either side of the console
    for side, d in ((-1, TRACKS[0]), (1, TRACKS[1])):
        tx, tz = cx + side * 16, cz - 15
        G.box("MapTable", (16, 3, 12), (tx, y + 1.5, tz), (40, 46, 60), "SmoothPlastic")
        deco("MapTop", (15, 0.2, 11), (tx, y + 3.1, tz), (20, 24, 34))
        pts = d["points"]
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        mx, mz = (max(xs) + min(xs)) / 2, (max(zs) + min(zs)) / 2
        sc = min(13.0 / max(1.0, max(xs) - min(xs)), 9.0 / max(1.0, max(zs) - min(zs)))
        col = TEAL if side < 0 else PINK
        step = max(1, len(pts) // 90)
        for i in range(0, len(pts), step):
            px, pz = pts[i]
            deco("MapTrack", (0.5, 0.15, 0.5), (tx + (px - mx) * sc, y + 3.3, tz + (pz - mz) * sc), col, "Neon")
    # floodlight towers at the corners: the lobby lights itself (the arcade sky is dusk)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = cx + sx * 46, cz + sz * 30
            G.vcyl("FloodPole", x, y, y + 22, z, 1, (70, 74, 86), "Metal", collide=False)
            G.box("Floodlight", (5, 2, 2), (x, y + 22, z), (250, 248, 236), "Neon", collide=False, shadow=False,
                  light=(1.6, 60, (255, 250, 236)))
    # tyre stacks, chequered flags and the podium along the sides
    for sx in (-1, 1):
        for k in range(3):
            x, z = cx + sx * 44, cz - 12 + k * 14
            for h in range(3):
                G.part("TyreStack", (1.4, 4, 4), (x, y + 0.7 + h * 1.4, z), (28, 30, 34), "SmoothPlastic", shape="Cylinder",
                       rot=(0, 0, 90), collide=False)
            deco("TyreBand", (4.1, 0.3, 4.1), (x, y + 2.1, z), CURB_R if k % 2 else CURB_W)
        x = cx + sx * 36
        G.vcyl("FlagPole", x, y, y + 14, cz + 26, 0.4, (220, 222, 226), "Metal", collide=False)
        for i in range(4):
            for j in range(3):
                deco("Flag", (0.2, 1.2, 1.2), (x, y + 13 - j * 1.2, cz + 26.8 + i * 1.2), WHITE if (i + j) % 2 else BLACK)
    for place, (h, col) in enumerate(((5, (255, 205, 60)), (3.5, (200, 205, 214)), (2.4, (205, 130, 70)))):
        px = cx - 34 + (0, -6, 6)[place]
        G.box("Podium", (6, h, 6), (px, y + h / 2, cz + 6), col, "SmoothPlastic")


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
            G.part("RaceConsole",(10,4,4),(-7400,302,-6014),TEAL,"Metal")
            pit_lobby()
        with G.Group("VehicleTemplate","Model"):
            kart(-7400,250,-6000)
        for i,d in enumerate(TRACKS): track(d,i)


def write_data(path):
    """Keep visible roads, AI and authoritative collision/checkpoint data generated from one definition."""
    def lua(v):
        if isinstance(v,dict): return '{'+','.join('['+json.dumps(k,ensure_ascii=False)+']='+lua(x) for k,x in v.items())+'}'
        if isinstance(v,list): return '{'+','.join(lua(x) for x in v)+'}'
        return json.dumps(v,ensure_ascii=False)
    data=dict(Laps=3,Duration=300,MaxPlayers=8,Lobby=[-7400,303,-6000],Tracks=TRACKS)
    with open(path,'w',encoding='utf-8') as f:
        f.write('-- Generated by tools/racers47.py; canonical geometry and driving data.\nlocal D='+lua(data)+'\n')
        f.write('function D.get(id)\n\tfor _, track in ipairs(D.Tracks) do\n\t\tif track.id == id then\n\t\t\treturn track\n\t\tend\n\tend\n\treturn nil\nend\nreturn D\n')
