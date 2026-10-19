local test=game:GetService("StudioTestService")
if test:GetTestArgs()~="Museum46" then return end
local p=game.Players.LocalPlayer
local rs=game.ReplicatedStorage
local move=rs:WaitForChild("Museum46QAMove")
local done=rs:WaitForChild("Museum46QADone")
local remote=rs:WaitForChild("Museum")
local D=require(rs.Shared.MuseumData)
repeat task.wait(.1) until p:GetAttribute("MuseumQARole")
local role=p:GetAttribute("MuseumQARole")
local ok,result=pcall(function()
 local completed=0
 for _,d in ipairs(D.Exhibits) do
  if role==2 and d.id~="micro" then continue end
  assert(move:InvokeServer(d.id))
  local s=remote:InvokeServer("start",d.id)
  assert(s.token,"session did not start")
  local wrong=d.steps[1].options[1].id
  if wrong==d.steps[1].correct then wrong=d.steps[1].options[2].id end
  task.wait(.15)
  local no=remote:InvokeServer("act",d.id,s.token,1,wrong)
  assert(not no.ok and no.step==1,"wrong advanced")
  if role==2 then task.wait(2) assert(p:GetAttribute("PassportXP")==0,"other player XP leaked") end
  for i,step in ipairs(d.steps) do
   task.wait(.15)
   s=remote:InvokeServer("act",d.id,s.token,i,step.correct)
   assert(s.ok,"correct action denied")
  end
  assert(s.done,"incomplete") completed+=1
  task.wait(.15)
  local stale=remote:InvokeServer("act",d.id,s.token,#d.steps,d.steps[#d.steps].correct)
  assert(stale.error,"completed token replay accepted")
 end
 return {ok=true,completed=completed,xp=p:GetAttribute("PassportXP"),wrongRetry=true,replayDenied=true}
end)
done:FireServer(if ok then result else {ok=false,error=tostring(result)})
