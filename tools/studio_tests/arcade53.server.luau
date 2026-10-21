-- v53 arcade QA (2 clients): one forced Petri Floor round; both players must get a ranked results card.
-- Run from Edit: workspace:SetAttribute("ArcadeForce", "PetriFloor"); StudioTestService:ExecuteMultiplayerTestAsync(2, "Arcade53")
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "Arcade53" then
	return
end
local Players = game:GetService("Players")
local done = Instance.new("RemoteEvent")
done.Name = "Arcade53QADone"
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
task.delay(170, function()
	finish({ passed = false, error = "timeout", results = results })
end)
while #Players:GetPlayers() < 2 do
	task.wait(0.1)
end
local sp = workspace.Map:FindFirstChild("ArcadeSpawn", true)
for _, p in ipairs(Players:GetPlayers()) do
	while not p.Character or not p.Character:FindFirstChild("HumanoidRootPart") do
		task.wait(0.1)
	end
	p.Character:PivotTo(sp.CFrame + Vector3.new(math.random(-4, 4), 4, math.random(-4, 4)))
end
local players = Players:GetPlayers()
while not results[players[1]] or not results[players[2]] do
	task.wait(0.2)
end
local a, b = results[players[1]], results[players[2]]
local ok = a.n == 2 and b.n == 2 and a.rank ~= b.rank
finish({ passed = ok, a = a, b = b })
