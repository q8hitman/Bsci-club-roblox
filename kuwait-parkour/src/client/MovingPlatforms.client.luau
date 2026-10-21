-- v59 moving platforms (parts tagged BSCMover by Obstacles.server).
-- Every client moves each platform from the shared server clock, so all players see it in the same place, and the
-- platform under the local character carries it: each physics step the character gets the platform's own movement.
-- A jump keeps the carry for a short while, like jumping inside a moving train, so the player lands where they aimed.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer
local movers = {} -- [part] = { base, offset, period, phase }
local AIR_CARRY = 1.2 -- seconds a jump keeps riding the platform it left

local function add(part)
	if not part:IsA("BasePart") then
		return
	end
	movers[part] = {
		base = part.CFrame,
		offset = part:GetAttribute("MoveOffset") or Vector3.zero,
		period = part:GetAttribute("MovePeriod") or 4,
		phase = part:GetAttribute("MovePhase") or 0,
	}
end
CollectionService:GetInstanceAddedSignal("BSCMover"):Connect(add)
CollectionService:GetInstanceRemovedSignal("BSCMover"):Connect(function(part)
	movers[part] = nil
end)
for _, part in ipairs(CollectionService:GetTagged("BSCMover")) do
	add(part)
end

local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
local riding, leftAt = nil, 0

RunService.PreSimulation:Connect(function()
	if next(movers) == nil then
		return
	end
	local now = workspace:GetServerTimeNow()
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local under = nil
	if root and hum and hum.Health > 0 then
		params.FilterDescendantsInstances = { char }
		local hit =
			workspace:Raycast(root.Position, Vector3.new(0, -(hum.HipHeight + root.Size.Y / 2 + 1.2), 0), params)
		if hit and movers[hit.Instance] then
			under = hit.Instance
			riding, leftAt = under, now
		elseif riding and now - leftAt < AIR_CARRY then
			local state = hum:GetState()
			if state == Enum.HumanoidStateType.Jumping or state == Enum.HumanoidStateType.Freefall then
				under = riding
			else
				riding = nil
			end
		else
			riding = nil
		end
	end
	for part, m in pairs(movers) do
		local a = (1 - math.cos(2 * math.pi * (now - m.phase) / m.period)) / 2
		local pos = m.base.Position + m.offset * a
		if part == under and root then
			root.CFrame += pos - part.Position
		end
		part.CFrame = m.base.Rotation + pos
	end
end)
