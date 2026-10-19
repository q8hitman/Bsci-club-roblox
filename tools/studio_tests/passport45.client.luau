local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "Passport45" then return end
local player = game.Players.LocalPlayer
local rs = game.ReplicatedStorage
local remote = rs:WaitForChild("Passport45QA")
local shop = rs:WaitForChild("Shop")
local role
repeat task.wait(.1) role = player:GetAttribute("PassportQARole") until role
local initial = shop:InvokeServer("get")
shop:InvokeServer("xp", 999999)
task.wait(.35)
local denied = shop:InvokeServer("title", "passport5")
task.wait(.35)
shop:InvokeServer("week", "explore")
local guards = shop:InvokeServer("get")
if role == 1 then
	local lab = rs:WaitForChild("Lab")
	local q = lab:InvokeServer("slide")
	local answer
	for _, r in require(rs.Shared.LabData).SLIDES do if r[1] == q.text then answer = r[2] end end
	local result = lab:InvokeServer("answer", q.token, answer)
	assert(result.ok and result.gained > 0, "real lab token failed")
	assert(not lab:InvokeServer("answer", q.token, answer).ok, "token replay accepted")
end
local gui = player.PlayerGui:WaitForChild("ProfileMenu"):WaitForChild("ProfilePanel")
local tabs = 0 for _, v in gui:GetChildren() do if v.Name:match("^Tab%d+$") then tabs += 1 end end
remote.OnClientEvent:Connect(function(kind)
	if kind == "arcade" then
		if role == 2 then
			task.spawn(function()
				repeat task.wait(.1) until player:GetAttribute("InArcadeRound")
				task.wait(1)
				rs.Travel:FireServer("Campus")
				task.wait(2.3)
				remote:FireServer("departed")
			end)
		end
		rs.Travel:FireServer("Arcade")
	elseif kind == "final" then
		local s = shop:InvokeServer("get")
		remote:FireServer("final", { xp = s.passport.xp, arcade = s.ach.arcade_play == true,
			level = s.passport.level, activities = s.passport.weekly[3].progress })
	end
end)
remote:FireServer("ready", { xp = shop:InvokeServer("get").passport.xp, tabs = tabs,
	lockedDenied = denied.equip.title == nil, forgedDenied = guards.passport.xp == initial.passport.xp })
