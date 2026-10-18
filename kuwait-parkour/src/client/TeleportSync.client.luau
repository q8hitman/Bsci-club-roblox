-- Client half of the safe teleport (server/Teleport.luau): end any local ride, put the character at the exact CFrame
-- the server chose (the client owns its character's physics), clear velocity and give the camera back.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local event = ReplicatedStorage:WaitForChild("TeleportSync", 60)
if not event then
	return
end

event.OnClientEvent:Connect(function(cf)
	if typeof(cf) ~= "CFrame" then
		return
	end
	-- rides register these hooks (CartRide.client / CellTrain.client)
	for _, name in ipairs({ "BSCEndCart", "BSCStopCellTrain" }) do
		local fn = _G[name]
		if typeof(fn) == "function" then
			pcall(fn)
		end
	end
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not (hum and root) then
		return
	end
	root.Anchored = false
	hum.Sit = false
	for _, part in ipairs(char:GetDescendants()) do
		if part:IsA("BasePart") then
			part.AssemblyLinearVelocity = Vector3.zero
			part.AssemblyAngularVelocity = Vector3.zero
		end
	end
	char:PivotTo(cf)
	local cam = workspace.CurrentCamera
	if cam.CameraType ~= Enum.CameraType.Custom then
		cam.CameraType = Enum.CameraType.Custom
	end
	cam.CameraSubject = hum
end)
