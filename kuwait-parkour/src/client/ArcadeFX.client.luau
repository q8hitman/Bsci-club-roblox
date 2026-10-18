-- Arcade pushes (Last Cell Standing spores / cilia waves): the server decides who is hit, the client applies the
-- velocity to its own character because it owns that physics. Capped so a bad value can't fling anyone away.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local knock = ReplicatedStorage:WaitForChild("ArcadeKnock")

knock.OnClientEvent:Connect(function(vel)
	if typeof(vel) ~= "Vector3" or vel.Magnitude > 120 then
		return
	end
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not (root and hum) or hum.Health <= 0 then
		return
	end
	hum:ChangeState(Enum.HumanoidStateType.Freefall)
	root.AssemblyLinearVelocity = vel
end)
