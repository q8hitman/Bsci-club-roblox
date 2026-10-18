import sys, math
sys.path.insert(0, '.')
import genmap8  # noqa
import cartride
from PIL import Image, ImageDraw
t = cartride.build_track()
pts = t.pts
xs=[p[0] for p in pts]; zs=[p[2] for p in pts]
x0,x1,z0,z1=min(xs)-40,max(xs)+40,min(zs)-40,max(zs)+40
S=1.0
img=Image.new("RGB",(int((x1-x0)*S),int((z1-z0)*S)+200),(30,30,40))
d=ImageDraw.Draw(img)
cols=[(255,255,255),(180,100,255),(100,220,100),(230,200,120),(250,150,170),(150,150,255),(80,255,160),(200,160,90),(255,220,60),(80,220,255)]
sec=0
starts={s:i+1 for i,(s,_) in enumerate(t.sections)}
for i,(a,b) in enumerate(zip(pts,pts[1:])):
    sec=starts.get(i,sec)
    c=cols[sec%10]
    w=4 if 'g' not in b[4] else 1
    d.line([((a[0]-x0)*S,(z1-a[2])*S),((b[0]-x0)*S,(z1-b[2])*S)],fill=c,width=w)
# profile
L=0
for i,(a,b) in enumerate(zip(pts,pts[1:])):
    L2=L+math.dist(a[:3],b[:3])
    H=img.size[1]
    d.line([(L/5,H-100-a[1]),(L2/5,H-100-b[1])],fill=(255,255,0),width=1)
    L=L2
d.line([(0,img.size[1]-100+70),(img.size[0],img.size[1]-100+70)],fill=(255,0,0))
img.save('../track_top.png'); print(img.size)
