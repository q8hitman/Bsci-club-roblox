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

RunService.Heartbeat:Connect(function(dt)
	for _, z in ipairs(zones) do
		if z.kind == "Wind" then
			z.part.LocalTransparencyModifier = gusting(z) and 0 or 1 -- the haze only shows while it blows
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
				if gusting(z) then
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
