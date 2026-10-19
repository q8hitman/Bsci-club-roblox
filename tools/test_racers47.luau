local M=require("../kuwait-parkour/src/shared/RacerMath")
local D=require("../kuwait-parkour/src/shared/RacerData")
local P=require("../kuwait-parkour/src/server/PassportState")
for _,track in ipairs(D.Tracks) do
 local s=M.start(track,0)
 local startX,startZ=s.x,s.z
 for _=1,20 do M.step(s,{throttle=0,steer=0,brake=0},.05,track) end
 assert(s.x==startX and s.z==startZ,"no automatic human driving")
 for _=1,20 do M.step(s,{throttle=1,steer=0,brake=0},.05,track) end
 assert(s.speed>10,"throttle accelerates")
 local speed=s.speed
 M.step(s,{throttle=0,steer=0,brake=1},.05,track)
 assert(s.speed<speed,"brake slows")
 local h=s.heading
 M.step(s,{throttle=0,steer=1,brake=0},.05,track)
 assert(s.heading~=h,"real steering")
 local off=M.start(track,0)
 off.x,off.z=500,500
 M.step(off,{},.05,track)
 assert(M.road(track,off.x,off.z).excess<1e-6,"off-road fall prevented by authoritative corridor")
 local progress=s.gate
 M.step(s,{throttle=0/0,steer=math.huge,brake={}},.05,track)
 assert(s.x==s.x and s.heading==s.heading,"invalid input rejected")
 assert(s.gate==progress,"invalid input cannot forge progress")
	local forged=M.start(track,0)
	local last=track.points[track.gates[#track.gates]]
	forged.x,forged.z=last[1],last[2]
	M.step(forged,{lap=99,checkpoint=99,x=10000,z=10000},.05,track)
	assert(forged.gate==1 and forged.lap==1,"out-of-order gate and forged fields rejected")
	local lap,gate=forged.lap,forged.gate
	M.recover(forged,track)
	assert(forged.lap==lap and forged.gate==gate and forged.speed==0,"recovery cannot advance progress")
 local bot=M.start(track,0)
 for _=1,8000 do
  M.step(bot,M.botInput(bot,track),.05,track)
  if bot.done then break end
 end
 assert(bot.done and bot.lap==4,"AI completes three laps: "..track.id)
	assert(bot.finishedAt<=D.Duration,"AI finishes before time limit")
	print(track.id,"AI seconds",bot.finishedAt)
 if track.shortcut then
  local shortcut=M.start(track,0)
  for _=1,5000 do
   if shortcut.gate==2 and shortcut.botTarget==4 then shortcut.botTarget=5 end
   M.step(shortcut,M.botInput(shortcut,track),.05,track)
   if shortcut.done then break end
  end
  assert(shortcut.done and shortcut.finishedAt<D.Duration,"fair shortcut retains ordered gates")
  print("helix shortcut seconds",shortcut.finishedAt)
 end
 local boosted=M.start(track,0)
 M.step(boosted,{boost=true,throttle=1},.05,track)
 assert(boosted.boostUntil>boosted.time and boosted.boostReadyAt>boosted.boostUntil,"temporary boost")
 local untilTime=boosted.boostUntil
 M.step(boosted,{boost=true},.05,track)
 assert(boosted.boostUntil==untilTime,"boost cooldown")
 local shield=M.start(track,0)
 local pad=track.pickups[2]
 shield.x,shield.z=pad.x,pad.z
 M.step(shield,{},.05,track)
 assert(shield.shieldUntil>shield.time,"shield pickup")
 local hazard=track.hazards[1]
 shield.x,shield.z,shield.speed=hazard.x,hazard.z,30
 M.step(shield,{},.05,track)
 assert(shield.shieldUntil==0 and shield.slowUntil==0,"shield blocks one obstacle")
 shield.hazardAt=-10 shield.speed=30
 M.step(shield,{},.05,track)
 assert(shield.slowUntil>shield.time and shield.speed<18,"unshielded obstacle slows")
 local again=bot.finishedAt
 M.step(bot,{throttle=1,steer=1},.05,track)
 assert(bot.finishedAt==again,"finish immutable")
end
local s={passport={}}
P.record(s,"race","cell",1792368000)
P.record(s,"race","cell",1792368000)
P.record(s,"race","helix",1792368000)
P.record(s,"race","forged",1792368000)
assert(P.summary(s,1792368000).xp==40,"two one-time finish stamps")
assert(P.summary({passport=P.merge({},s.passport,1792368000)},1792368000).races==2,"race save merge")
print("PASS racers47: two manual controllers, safe inputs, AI three laps, immutable finish, Passport idempotent merge")
