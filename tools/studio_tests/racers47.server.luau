local test=game:GetService("StudioTestService")
if not game:GetService("RunService"):IsStudio() or test:GetTestArgs()~="Racers47" then return end
local Players=game:GetService("Players")
local Profiles=require(game.ServerScriptService.Server.Profiles)
local Passport=require(game.ServerScriptService.Server.PassportService)
local qa=Instance.new("RemoteFunction") qa.Name="Racers47QA" qa.Parent=game.ReplicatedStorage
local done=Instance.new("RemoteEvent") done.Name="Racers47QADone" done.Parent=game.ReplicatedStorage
local results,barriers={},{}
local disconnected=false
qa.OnServerInvoke=function(p,action,n)
 if action=="entry" then require(game.ServerScriptService.Server.Teleport).to(p,workspace.Map.Racers47.Entry.RaceEntrance) task.wait(.8) return true end
 if action=="die" then p.Character.Humanoid.Health=0 return true end
 if action=="barrier" then
  barriers[n]=barriers[n] or {} barriers[n][p]=true
  repeat task.wait(.1) until #Players:GetPlayers()<2 or (function()local c=0 for _ in barriers[n] do c+=1 end return c==2 end)()
  return true
 end
 if action=="expire" then require(game.ReplicatedStorage.Shared.RacerData).Duration=0 return true end
 if action=="disconnect" then disconnected=true p:Kick("Studio QA disconnect") return true end
end
done.OnServerEvent:Connect(function(p,result) results[p]=result end)
local ended=false
local function finish(result) if not ended then ended=true test:EndTest(result) end end
task.delay(310,function()finish({passed=false,error="Racers47 timeout",results=results})end)
while #Players:GetPlayers()<2 do task.wait(.1) end
local ps=Players:GetPlayers()
for i,p in ps do while not Profiles.state[p] or not p.Character do task.wait(.1) end task.wait(2) p:SetAttribute("RaceQARole",i) end
while not results[ps[1]] and not results[ps[2]] do task.wait(.1) end
for _,r in results do if not r.ok then finish({passed=false,error=r.error,results=results}) return end end
while not results[ps[1]] do task.wait(.1) end
local p=ps[1]
finish({passed=results[p].ok and disconnected and Passport.refresh(p).xp==40 and Profiles.state[p].ach.racer2==true,clients=2,results=results[p],deathRespawn=true,disconnect=disconnected,timeoutAccelerated=true,mode="normal durations; real clients; test emits only driving intents; no position/lap injection"})
