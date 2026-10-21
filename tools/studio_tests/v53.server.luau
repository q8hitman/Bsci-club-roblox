-- v53 multiplayer QA (2 clients): Cart Ride for both at once, Gram stain for both at once, First Day progress.
-- Run from Edit: game:GetService("StudioTestService"):ExecuteMultiplayerTestAsync(2, "V53")
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "V53" then
	return
end
local Players = game:GetService("Players")
local Profiles = require(game.ServerScriptService.Server.Profiles)
local done = Instance.new("RemoteEvent")
done.Name = "V53QADone"
done.Parent = game.ReplicatedStorage
local results = {}
done.OnServerEvent:Connect(function(p, data)
	results[p] = data
end)
local ended = false
local function finish(v)
	if not ended then
		ended = true
		test:EndTest(v)
	end
end
task.delay(150, function()
	finish({ passed = false, error = "V53 timeout", results = results })
end)
while #Players:GetPlayers() < 2 do
	task.wait(0.1)
end
local players = Players:GetPlayers()
for i, p in ipairs(players) do
	while not Profiles.state[p] or not p.Character or not p.Character:FindFirstChild("HumanoidRootPart") do
		task.wait(0.1)
	end
	p:SetAttribute("V53Role", i)
end
-- both players board the cart, a few seconds apart, by touching the real start pad
local pad = workspace.Map:FindFirstChild("CartStart", true)
for _, p in ipairs(players) do
	p.Character:PivotTo(pad.CFrame + Vector3.new(0, 3, 0))
	task.wait(4)
end
local carts = {}
for _, p in ipairs(players) do
	carts[p] = workspace:FindFirstChild("Cart_" .. p.UserId)
end
for _, p in ipairs(players) do
	p:SetAttribute("V53Go", true)
end
task.wait(12)
local moved = {}
for _, p in ipairs(players) do
	local c = carts[p]
	moved[p] = c and c.PrimaryPart and (c.PrimaryPart.Position - pad.Position).Magnitude or -1
end
for _, p in ipairs(players) do
	p:SetAttribute("V53Lab", true)
end
while not results[players[1]] or not results[players[2]] do
	task.wait(0.2)
end
local ok, result = pcall(function()
	local a, b = players[1], players[2]
	assert(carts[a] and carts[b] and carts[a] ~= carts[b], "each player must get their own cart")
	assert(moved[a] > 60 and moved[b] > 60, ("both carts must leave the station (%.0f, %.0f)"):format(moved[a], moved[b]))
	for _, p in ipairs(players) do
		local r = results[p]
		assert(r.ok, "client " .. p.Name .. ": " .. tostring(r.error))
		assert(r.sawOtherCart, p.Name .. " did not see the other player's cart move")
		assert(r.gramOk and r.gained > 0, p.Name .. " gram not rewarded")
		assert(r.firstDay:sub(3, 3) == "1", p.Name .. " FirstDay lab step not ticked: " .. r.firstDay)
	end
	assert(Profiles.state[a] ~= Profiles.state[b], "shared state")
	return { passed = true, moved = { moved[a], moved[b] }, results = { results[a], results[b] } }
end)
finish(if ok then result else { passed = false, error = tostring(result), moved = moved, results = results })
