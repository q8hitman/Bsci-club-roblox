-- Studio-only temporary test fixture. Install for ExecuteMultiplayerTestAsync(2, "Passport45"); remove afterwards.
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "Passport45" then return end
local Players = game:GetService("Players")
local Profiles = require(game.ServerScriptService.Server.Profiles)
local Passport = require(game.ServerScriptService.Server.PassportService)
local remote = Instance.new("RemoteEvent")
remote.Name = "Passport45QA"
remote.Parent = game.ReplicatedStorage
local ready, final, departed, done = {}, {}, false, false
local function finish(value)
	if done then return end
	done = true
	test:EndTest(value)
end
task.delay(90, function() finish({ passed = false, error = "multiplayer QA timeout" }) end)
remote.OnServerEvent:Connect(function(p, kind, data)
	if kind == "ready" then ready[p] = data end
	if kind == "final" then final[p] = data end
	if kind == "departed" and p:GetAttribute("PassportQARole") == 2 then departed = true end
end)
-- Shorten only this ephemeral server's rounds; source files and shipped durations are unchanged.
for _, module in game.ServerScriptService.Server.Minigames:GetChildren() do
	if module:IsA("ModuleScript") then local def = require(module) def.duration = 6 end
end
while #Players:GetPlayers() < 2 do task.wait(.1) end
local players = Players:GetPlayers()
for i, p in ipairs(players) do p:SetAttribute("PassportQARole", i) end
while not ready[players[1]] or not ready[players[2]] do task.wait(.1) end
local ok, result = pcall(function()
	for _, p in ipairs(players) do
		assert(ready[p].lockedDenied and ready[p].forgedDenied and ready[p].tabs == 7, "client guards/UI failed")
	end
	assert(ready[players[1]].xp == 40 and ready[players[2]].xp == 0, "profiles leaked or lab completion failed")
	remote:FireAllClients("arcade")
	while workspace:GetAttribute("ArcadePhase") ~= "results" do task.wait(.1) end
	task.wait(.3)
	assert(departed, "departure did not run")
	remote:FireAllClients("final")
	while not final[players[1]] or not final[players[2]] do task.wait(.1) end
	assert(final[players[1]].arcade == true, "finisher missing arcade credit")
	assert(not final[players[2]].arcade and final[players[2]].xp == 0, "departing client received completion credit")
	assert(final[players[1]].xp == 80, "one-time lab+arcade XP mismatch")
	assert(Profiles.state[players[1]] ~= Profiles.state[players[2]], "shared profiles")
	local before = Passport.refresh(players[1]).xp
	Passport.refresh(players[1])
	assert(Passport.refresh(players[1]).xp == before, "refresh duplicated XP")
	return { passed = true, clients = 2, ready = { ready[players[1]], ready[players[2]] },
		final = { final[players[1]], final[players[2]] }, departed = departed, mode = "accelerated six-second round" }
end)
finish(if ok then result else { passed = false, error = tostring(result) })
