local R=require("../kuwait-parkour/src/shared/LaserRules")
local D=require("../kuwait-parkour/src/shared/LaserData")
local P=require("../kuwait-parkour/src/server/PassportState")
for _,room in D.Rooms do
 local warned=false
 for i=0,300 do local phase=R.phase(i*.05,room) if phase=="warning" then warned=true end if phase=="danger" then assert(warned,"unannounced danger") end end
end
local s=R.start(1,0)
assert(not R.visit(s,-31,10,false),"cannot skip physical route")
assert(R.visit(s,10,1,false)==false and s.zone==1,"first route zone")
assert(R.visit(s,-10,2,false)==false and s.zone==2,"second route zone")
assert(R.visit(s,-31,4,false)==true,"ordered physical room finish")
local keyed=R.start(3,0)
R.visit(keyed,10,1,false) R.visit(keyed,-10,2,false)
assert(not R.visit(keyed,-31,4,false),"door room needs own plate evidence")
assert(R.visit(keyed,-31,4,true),"personal plate evidence permits finish")
assert(not R.motion(100,0, .1,16,0),"teleport rejected")
assert(R.motion(1.6,0,.1,16,0),"normal walk accepted")
assert(R.motion(2.1,0,.1,16,.5),"platform carry allowed")
local p={passport={}}
P.record(p,"escape","laser48",1792368000) P.record(p,"escape","laser48",1792368000)
assert(P.summary(p,1792368000).xp==40,"escape one-time stamp")
assert(P.summary({passport=P.merge({},p.passport,1792368000)},1792368000).xp==40,"escape persistence merge")
print("PASS laser48 phases/order/plate/motion/carry/duplicate reward")
