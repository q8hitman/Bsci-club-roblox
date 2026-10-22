-- v54 lab QA (2 clients): bench locking and parallel benches through the same handlers the prompts use.
-- Run from Edit: game:GetService("StudioTestService"):ExecuteMultiplayerTestAsync(2, "Labs54")
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "Labs71" then
	return
end
local Players = game:GetService("Players")
local ended = false
local function finish(v)
	if not ended then
		ended = true
		test:EndTest(v)
	end
end
task.delay(90, function()
	finish({ passed = false, error = "timeout" })
end)
while #Players:GetPlayers() < 2 do
	task.wait(0.1)
end
local players = Players:GetPlayers()
for _, p in ipairs(players) do
	while not p.Character or not p.Character:FindFirstChild("HumanoidRootPart") do
		task.wait(0.1)
	end
end
task.wait(2)
local qa = game.ServerStorage:WaitForChild("Labs54QA", 20)
local a, b = players[1], players[2]
local gram = workspace.Map:FindFirstChild("Bench|gram", true)
local pcr = workspace.Map:FindFirstChild("Bench|pcr", true)
local ok, result = pcall(function()
	a.Character:PivotTo(CFrame.new(gram:GetPivot().Position + Vector3.new(9, 2, 0)))
	b.Character:PivotTo(CFrame.new(gram:GetPivot().Position + Vector3.new(9, 2, 6)))
	task.wait(0.5)
	qa:Invoke(a, "gram|item|slide")
	assert(a:GetAttribute("Carrying") == nil, "a picked up without a lab coat")
	qa:Invoke(a, "ppe")
	qa:Invoke(b, "ppe")
	assert(a:GetAttribute("LabPPE") and b:GetAttribute("LabPPE"), "PPE not applied")
	qa:Invoke(a, "gram|item|slide")
	assert(a:GetAttribute("Carrying") ~= nil, "a could not pick up the slide")
	qa:Invoke(b, "gram|item|cv")
	assert(b:GetAttribute("Carrying") == nil, "b used a bench a is working on")
	-- b works the PCR bench at the same time
	b.Character:PivotTo(CFrame.new(pcr:GetPivot().Position + Vector3.new(9, 2, 0)))
	task.wait(0.5)
	qa:Invoke(b, "pcr|item|pipette")
	assert(b:GetAttribute("Carrying") ~= nil, "b could not use a free bench")
	qa:Invoke(a, "gram|use|burner")
	qa:Invoke(a, "gram|slot|tray")
	local slide = gram:FindFirstChild("Item|slide", true).Handle
	assert((slide.Position - gram:FindFirstChild("Slot|tray", true).Position).Magnitude < 2, "slide not on the tray")
	-- a walks away: the bench frees itself and the slide goes home
	a.Character.HumanoidRootPart.Anchored = true
	a.Character:PivotTo(CFrame.new(0, 10, 0) + workspace.Map:FindFirstChild("LabSpawn", true).Position + Vector3.new(0, 0, -200))
	task.wait(5)
	b.Character:PivotTo(CFrame.new(gram:GetPivot().Position + Vector3.new(9, 2, 6)))
	task.wait(0.3)
	qa:Invoke(b, "gram|item|cv")
	assert(b:GetAttribute("Carrying") ~= nil, "bench did not free itself after a left")
	-- Switching freed b's PCR station, including its carried pipette.
	a.Character:PivotTo(pcr:GetPivot() * CFrame.new(9, 2, 0))
	a.Character.HumanoidRootPart.Anchored = false
	qa:Invoke(a, "ppe") -- the earlier off-map walk-away can respawn this test avatar
	assert(a:GetAttribute("LabPPE"), "test player missing PPE")
	qa:Invoke(a, "pcr|item|pipette")
	assert(a:GetAttribute("Carrying") ~= nil, "switch did not release previous station")
	-- Character replacement immediately invalidates the owned experiment.
	b:LoadCharacterAsync()
	while not b.Character or not b.Character:FindFirstChild("HumanoidRootPart") do task.wait(.1) end
	a.Character:PivotTo(gram:GetPivot() * CFrame.new(9, 2, 0))
	qa:Invoke(a, "gram|item|cv")
	assert(a:GetAttribute("Carrying") ~= nil, "respawn did not release station")
	assert(not b:GetAttribute("LabPPE"), "PPE survived character replacement")
	return { passed = true, lock = true, parallel = true, release = true, switch = true, respawn = true }
end)
finish(if ok then result else { passed = false, error = tostring(result) })
