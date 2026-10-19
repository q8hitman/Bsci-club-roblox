local test=game:GetService("StudioTestService")
if test:GetTestArgs()~="Museum46" then return end
local Players=game:GetService("Players")
local Profiles=require(game.ServerScriptService.Server.Profiles)
local Passport=require(game.ServerScriptService.Server.PassportService)
local move=Instance.new("RemoteFunction") move.Name="Museum46QAMove" move.Parent=game.ReplicatedStorage
local done=Instance.new("RemoteEvent") done.Name="Museum46QADone" done.Parent=game.ReplicatedStorage
local results={}
move.OnServerInvoke=function(p,id)
 local console=workspace.Map.Campus.Museum46:FindFirstChild("Exhibit_"..tostring(id))
 if not console then return false end
 p.Character:PivotTo(CFrame.new(console.Console.Position+Vector3.new(0,2,-4)))
 task.wait(.4) return true
end
done.OnServerEvent:Connect(function(p,data) results[p]=data end)
local ended=false
local function finish(v) if not ended then ended=true test:EndTest(v) end end
task.delay(90,function()finish({passed=false,error="Museum46 timeout"})end)
while #Players:GetPlayers()<2 do task.wait(.1) end
local players=Players:GetPlayers()
for i,p in ipairs(players) do
 while not Profiles.state[p] or not p.Character do task.wait(.1) end
 p:SetAttribute("MuseumQARole",i)
end
while not results[players[1]] or not results[players[2]] do task.wait(.1) end
local ok,result=pcall(function()
 assert(results[players[1]].ok and results[players[2]].ok,"client assertion failed")
 assert(Passport.refresh(players[1]).xp==80,"all-eight client XP")
 assert(Passport.refresh(players[2]).xp==10,"single-exhibit client XP")
 assert(Profiles.state[players[1]]~=Profiles.state[players[2]],"shared state")
 assert(Profiles.state[players[1]].ach.museum8 and not Profiles.state[players[2]].ach.museum8,"achievement leakage")
 return {passed=true,clients=2,results={results[players[1]],results[players[2]]},mode="normal museum sessions, no accelerated logic"}
end)
finish(if ok then result else {passed=false,error=tostring(result)})
