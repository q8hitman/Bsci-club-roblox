-- Client: run after pcr63_setup, with a freshly started Play session so reward cooldown cannot hide a defect.
local player = game.Players.LocalPlayer
local before = player:GetAttribute("Research") or 0
local result = game.ReplicatedStorage.Bench54Fn:InvokeServer("pcr", 95, 55, 72)
assert(result and result.ok, "PCR failed to start")
player.Character:PivotTo(player.Character:GetPivot() + Vector3.new(0, 0, 200))
task.wait(14)
local screen = workspace.Map:FindFirstChild("Bench|pcr", true):FindFirstChild("Screen|cycler", true)
	:FindFirstChildWhichIsA("TextLabel", true)
local gained = (player:GetAttribute("Research") or 0) - before
assert(gained == 0, "abandoned PCR awarded " .. gained .. " research")
assert(screen.Text == "READY", "old PCR overwrote reset bench: " .. screen.Text)
return { passed = true, gained = gained, screen = screen.Text }
