local test=game:GetService("StudioTestService")
if not game:GetService("RunService"):IsStudio() or test:GetTestArgs()~="Racers47" then return end
local p=game.Players.LocalPlayer
local rs=game.ReplicatedStorage
local req=rs:WaitForChild("RaceRequest")
local move=rs:WaitForChild("Racers47QA")
local done=rs:WaitForChild("Racers47QADone")
local M=require(rs.Shared.RacerMath)
local D=require(rs.Shared.RacerData)
local latest
rs.RaceState.OnClientEvent:Connect(function(s) if s.kind=="state" or s.kind=="results" then latest=s end end)
repeat task.wait(.1) until p:GetAttribute("RaceQARole")
local role=p:GetAttribute("RaceQARole")
local function request(a,b) task.wait(.18) local r=req:InvokeServer(a,b) assert(not r.error,r.error) return r end
local function finishTrack(id)
 local track=D.get(id)
 latest=nil
 local join=request("join",id)
 local target,seq=2,1000000
 local started=os.clock()
 repeat
  task.wait(.08)
  if latest and latest.raceId==join.raceId then
   local own
   for _,c in latest.cars do if c.id==tostring(p.UserId) then own=c end end
   if own and latest.phase=="running" and not own.finished then
    local s=table.clone(own) s.botTarget=target
    local input=M.botInput(s,track) target=s.botTarget seq+=1
    rs.RaceInput:FireServer(join.raceId,seq,input)
   end
  end
  assert(os.clock()-started<195,"race timeout")
 until latest and latest.raceId==join.raceId and latest.phase=="results"
 local own,bots
 bots=0
 for _,c in latest.cars do if c.id==tostring(p.UserId) then own=c elseif c.bot and c.finished then bots+=1 end end
 assert(own and own.finished,"human did not finish")
 assert(bots>=2,"AI did not finish")
 assert(not p.Character.HumanoidRootPart.Anchored,"results anchor")
 assert(require(p.PlayerScripts.PlayerModule):GetControls().controlsEnabled,"results controls")
 return {track=id,seconds=own.finishTime,rank=own.rank,bots=bots,xp=p:GetAttribute("PassportXP")}
end
local ok,result=pcall(function()
 assert(move:InvokeServer("entry"))
 request("enter")
 local results={finishTrack("cell")}
 assert(p:GetAttribute("PassportXP")==20,"first finish xp")
 move:InvokeServer("barrier",1)
 if role==1 then
  table.insert(results,finishTrack("cell"))
  assert(p:GetAttribute("PassportXP")==20,"replay XP duplicated")
 else
  request("join","cell")
  move:InvokeServer("die")
  local old=p.Character
  repeat task.wait(.1) until p.Character and p.Character~=old and p.Character:FindFirstChild("HumanoidRootPart")
  task.wait(1)
  assert(not p:GetAttribute("InMicroRace") and not p:GetAttribute("RacePhase"),"death session remained")
  assert(not p.PlayerGui.MicroRacersUI.RaceHUD.Visible and workspace.CurrentCamera.CameraType==Enum.CameraType.Custom,"death UI/camera")
 end
 move:InvokeServer("barrier",2)
 if role==2 then assert(move:InvokeServer("entry")) request("enter") end
 table.insert(results,finishTrack("helix"))
 assert(p:GetAttribute("PassportXP")==40,"two track XP")
 move:InvokeServer("barrier",3)
 request("menu")
 if role==2 then
  request("join","cell")
  request("leave")
  assert(move:InvokeServer("entry")) request("enter") request("join","cell")
  task.wait(.4)
  move:InvokeServer("disconnect")
  return {ok=true,disconnected=true,results=results}
 else
  task.wait(1.6)
  request("join","cell")
  task.wait(6)
  local count=0 for _,c in latest.cars do count+=1 end
  assert(count==4,"departed queue blocked AI fill")
  request("recover")
  local lap=p:GetAttribute("RaceLap") local gate=p:GetAttribute("RaceGate")
  rs.RaceInput:FireServer(latest.raceId,100000,{lap=99,checkpoint=99,x=10000,z=10000,throttle=0/0,steer=math.huge})
  task.wait(.2)
  assert(p:GetAttribute("RaceLap")==lap and p:GetAttribute("RaceGate")==gate,"forged progress")
  move:InvokeServer("expire") task.wait(.5)
  assert(p:GetAttribute("RacePhase")=="results" and not p.Character.HumanoidRootPart.Anchored,"timeout release")
  assert(require(p.PlayerScripts.PlayerModule):GetControls().controlsEnabled,"timeout controls")
  request("leave")
  assert(not p.Character.HumanoidRootPart.Anchored and not p:GetAttribute("InMicroRace"),"exit cleanup")
  return {ok=true,results=results,xp=p:GetAttribute("PassportXP"),replayNoXP=true,queueDeparture=true,forgeryDenied=true}
 end
end)
done:FireServer(if ok then result else {ok=false,error=tostring(result),role=role})
