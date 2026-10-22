-- Client: run after pcr63_setup, with no recent successful PCR reward.
local player = game.Players.LocalPlayer
local before = player:GetAttribute("Research") or 0
local remote = game.ReplicatedStorage.Bench54Fn
local result = remote:InvokeServer("pcr", 95, 55, 72)
assert(result and result.ok, "PCR failed to start")
task.wait(12)
local gained = (player:GetAttribute("Research") or 0) - before
assert(gained == 8, "expected 8 research, got " .. gained)
local repeated = remote:InvokeServer("pcr", 95, 55, 72)
assert(repeated and not repeated.ok, "completed PCR restarted")
return { passed = true, gained = gained, restartRejected = true }
