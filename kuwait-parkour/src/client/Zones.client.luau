-- Local physics zones (client-side so movement stays smooth):
--   LowGrav|g            inside the box, gravity becomes g (moon jumps)
--   Updraft|vy           inside the box, the player is lifted at vy studs/s (fans)
--   Wind|vx,vz|on|off    inside the box, gusts push sideways for `on` seconds every on+off seconds
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")
local DEFAULT_GRAVITY = workspace.Gravity
local Lighting = game:GetService("Lighting")
local wasInSpace, saved = false, nil

local zones = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local args = string.split(inst.Name, "|")
		if args[1] == "LowGrav" or args[1] == "Updraft" then
			table.insert(zones, { part = inst, kind = args[1], value = tonumber(args[2]) or 0 })
		elseif args[1] == "Wind" then
			local v = string.split(args[2] or "0,0", ",")
			table.insert(zones, {
				part = inst,
				kind = "Wind",
				push = Vector3.new(tonumber(v[1]) or 0, 0, tonumber(v[2]) or 0),
				on = tonumber(args[3]) or 1.5,
				off = tonumber(args[4]) or 2,
			})
		end
	end
end

local function inside(part, pos)
	local p = part.CFrame:PointToObjectSpace(pos)
	local h = part.Size / 2
	return math.abs(p.X) <= h.X and math.abs(p.Y) <= h.Y and math.abs(p.Z) <= h.Z
end

-- every client sees the same gust timing because it follows the server clock
local function gusting(z)
	return workspace:GetServerTimeNow() % (z.on + z.off) < z.on
end

-- v59 fan stage: each fan's light shows the rhythm (green calm, amber just before, red while it blows), streaks
-- show which way the air goes, and a glass WindShield on the fan side shelters whoever stands behind it
local CALM, WARN, GUST = Color3.fromRGB(90, 220, 120), Color3.fromRGB(255, 190, 60), Color3.fromRGB(255, 70, 60)
local WARN_TIME = 0.7
local shields = {}
local fanLights = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		if inst.Name == "WindShield" then
			table.insert(shields, inst)
		elseif inst.Name == "FanLight" then
			table.insert(fanLights, inst)
		end
	end
end
local shelterParams = RaycastParams.new()
shelterParams.FilterType = Enum.RaycastFilterType.Include
shelterParams.FilterDescendantsInstances = shields
for _, z in ipairs(zones) do
	if z.kind == "Wind" then
		z.lights = {}
		local h = z.part.Size / 2 + Vector3.new(4, 0, 0)
		for _, light in ipairs(fanLights) do
			local q = z.part.CFrame:PointToObjectSpace(light.Position)
			if math.abs(q.X) <= h.X and math.abs(q.Y) <= h.Y and math.abs(q.Z) <= h.Z then
				table.insert(z.lights, light)
			end
		end
		local streaks = Instance.new("ParticleEmitter")
		streaks.Name = "WindStreaks"
		streaks.EmissionDirection = z.push.X >= 0 and Enum.NormalId.Right or Enum.NormalId.Left
		streaks.Shape = Enum.ParticleEmitterShape.Box
		streaks.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
		streaks.Speed = NumberRange.new(38, 48)
		streaks.Lifetime = NumberRange.new(0.5, 0.7)
		streaks.Rate = 70
		streaks.Size = NumberSequence.new(0.25)
		streaks.Squash = NumberSequence.new(-2.5)
		streaks.Transparency = NumberSequence.new(0.35, 1)
		streaks.LightEmission = 0.6
		streaks.Enabled = false
		streaks.Parent = z.part
		z.streaks = streaks
	end
end
local function windState(z)
	local t = workspace:GetServerTimeNow() % (z.on + z.off)
	if t < z.on then
		return "gust"
	end
	return t > z.on + z.off - WARN_TIME and "warn" or "calm"
end
local function sheltered(root, push)
	if #shields == 0 or push.Magnitude < 0.01 then
		return false
	end
	return workspace:Raycast(root.Position, -push.Unit * 6, shelterParams) ~= nil
end

RunService.Heartbeat:Connect(function(dt)
	for _, z in ipairs(zones) do
		if z.kind == "Wind" then
			local state = windState(z)
			z.part.LocalTransparencyModifier = state == "gust" and 0 or 1 -- the haze only shows while it blows
			if z.state ~= state then
				z.state = state
				local color = state == "gust" and GUST or state == "warn" and WARN or CALM
				for _, light in ipairs(z.lights) do
					light.Color = color
				end
				z.streaks.Enabled = state == "gust"
			end
		end
	end

	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then
		return
	end
	local gravity = DEFAULT_GRAVITY
	if player:GetAttribute("Mutation") == "moon" then
		gravity = 60 -- arcade "moon" mutation (per player)
	end
	for _, z in ipairs(zones) do
		if inside(z.part, root.Position) then
			if z.kind == "LowGrav" then
				gravity = z.value
			elseif z.kind == "Wind" then
				if gusting(z) and not sheltered(root, z.push) then
					-- shift the character directly: velocity nudges are cancelled by ground friction.
					-- ~8-11 studs/s: standing still blows you off, walking into the wind holds you
					root.CFrame += z.push * 0.35 * dt
				end
			else
				local v = root.AssemblyLinearVelocity
				if v.Y < z.value then
					root.AssemblyLinearVelocity = Vector3.new(v.X, z.value, v.Z)
				end
			end
		end
	end
	if workspace.Gravity ~= gravity then
		workspace.Gravity = gravity
	end
	-- "space" stages: inside a LowGrav zone the sky turns to a starry night (local to this player only)
	local inSpace = false
	for _, z in ipairs(zones) do
		if z.kind == "LowGrav" and inside(z.part, root.Position) then
			inSpace = true
			break
		end
	end
	if inSpace ~= wasInSpace then
		wasInSpace = inSpace
		local atmosphere = Lighting:FindFirstChildOfClass("Atmosphere")
		if inSpace then
			saved = { clock = Lighting.ClockTime, density = atmosphere and atmosphere.Density }
			Lighting.ClockTime = 0
			if atmosphere then
				atmosphere.Density = 0.05
			end
		elseif saved then
			Lighting.ClockTime = saved.clock
			if atmosphere and saved.density then
				atmosphere.Density = saved.density
			end
			saved = nil
		end
	end
end)
