-- Safe teleport used by every server-side move of a character (portals, "back to the island", fall recovery, arcade,
-- exam pit). v31: a plain PivotTo could leave the player welded to a cart seat (the ride dragged them back), keep the
-- falling velocity (client-owned physics replays it), or land them in/under geometry. This:
--   1. unseats the humanoid and removes seat welds,
--   2. raycasts down at the target for solid ground (ignoring characters and carts) and stands the player on it,
--   3. zeroes every part's velocity, pivots, and tells the client to pivot to the same CFrame (TeleportSync.client
--      also ends any local ride and restores the camera),
--   4. re-checks after 0.6 s and puts the player back if they still dropped below the ground.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Teleport = {}

local event = ReplicatedStorage:FindFirstChild("TeleportSync")
if not event then
	event = Instance.new("RemoteEvent")
	event.Name = "TeleportSync"
	event.Parent = ReplicatedStorage
end

local function ignoreList()
	local list = {}
	for _, p in ipairs(Players:GetPlayers()) do
		if p.Character then
			table.insert(list, p.Character)
		end
	end
	for _, c in ipairs(workspace:GetChildren()) do
		if c.Name:match("^Cart_") or c.Name:match("^LocalCart") or c.Name == "LocalCellTrain" then
			table.insert(list, c)
		end
	end
	return list
end

-- returns the y of the first solid, collidable surface under `pos` (searching from 4 studs above), or nil
function Teleport.groundY(pos)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignoreList()
	params.RespectCanCollide = true
	-- start just above the target so a roof or ceiling over a spawn is never mistaken for the ground
	local hit = workspace:Raycast(pos + Vector3.new(0, 4, 0), Vector3.new(0, -60, 0), params)
	return hit and hit.Position.Y
end

-- target: a CFrame or a BasePart (its top centre is used). offset: optional Vector3 added before the ground search.
function Teleport.to(player, target, offset)
	local char = player and player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not (hum and root and char.Parent) or not target then
		return false
	end
	local cf = typeof(target) == "Instance" and (target.CFrame * CFrame.new(0, target.Size.Y / 2, 0)) or target
	if offset then
		cf = cf + offset
	end
	-- 1. off any seat (cart / train / chair)
	if hum.SeatPart then
		local seat = hum.SeatPart
		hum.Sit = false
		for _, w in ipairs(seat:GetChildren()) do
			if w:IsA("Weld") and w.Name == "SeatWeld" then
				w:Destroy()
			end
		end
	end
	root.Anchored = false
	-- 2. stand on real ground at the target
	local feetY = Teleport.groundY(cf.Position) or cf.Position.Y
	local standY = feetY + hum.HipHeight + root.Size.Y / 2 + 0.3
	local look = cf.LookVector
	local flat = Vector3.new(look.X, 0, look.Z)
	local pos = Vector3.new(cf.Position.X, standY, cf.Position.Z)
	local final = flat.Magnitude > 0.01 and CFrame.lookAt(pos, pos + flat) or CFrame.new(pos)
	-- 3. no leftover velocity, move, and let the owning client do the same
	player:SetAttribute("TeleportRevision", (player:GetAttribute("TeleportRevision") or 0) + 1)
	for _, part in ipairs(char:GetDescendants()) do
		if part:IsA("BasePart") then
			part.AssemblyLinearVelocity = Vector3.zero
			part.AssemblyAngularVelocity = Vector3.zero
		end
	end
	char:PivotTo(final)
	event:FireClient(player, final)
	-- 4. safety net (client-owned physics can still replay a stale frame)
	task.delay(0.6, function()
		if root.Parent and hum.Health > 0 and root.Position.Y < feetY - 6 then
			char:PivotTo(final)
			event:FireClient(player, final)
		end
	end)
	return true
end

return Teleport
