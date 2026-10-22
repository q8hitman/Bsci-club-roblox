-- Run through execute_luau in a disposable Server playtest, after a fresh Play start.
-- Exercises the same handlers as the real prompts, without awarding research.
local player = game.Players:GetPlayers()[1]
local bench = workspace.Map:FindFirstChild("Bench|gel", true)
local qa = game.ServerStorage:WaitForChild("Labs54QA", 10)
local fluid = bench:FindFirstChild("Liquid|buffer", true)
local original = fluid.CFrame
local origin = player.Character:GetPivot()
player.Character:PivotTo(bench:GetPivot() * CFrame.new(9, 2, 0))
qa:Invoke(player, "ppe")
qa:Invoke(player, "gel|item|gel")
qa:Invoke(player, "gel|slot|tank")
qa:Invoke(player, "gel|item|buffer")
qa:Invoke(player, "gel|slot|tank")
task.wait(1.4)
local filled = fluid.Position
qa:Invoke(player, "gel|slot|tank")
task.wait(1.4)
local repeatRise = (fluid.Position - filled).Magnitude
player.Character:PivotTo(origin + Vector3.new(0, 0, 200))
task.wait(2.5)
local resetError = (fluid.Position - original.Position).Magnitude
local result = { repeatRise = repeatRise, resetError = resetError, height = fluid.Size.Y }
assert(repeatRise < 0.001 and resetError < 0.001 and math.abs(fluid.Size.Y - 0.02) < 0.001,
	game.HttpService:JSONEncode(result))
return result
