-- v53 Cell Train world, alive: everything here is local and only runs while the camera is inside the cell world.
--   * vesicles ride the microtubules on the secretion route (rough ER -> Golgi cis -> trans -> plasma membrane),
--     each one carried by a two-footed motor protein (kinesin) that steps along the rail
--   * mitochondria drift and turn very slowly; the cytosol particles float
-- The route comes from the map ("CellPath|1..n" anchors written by tools/celltrain.py), never hard-coded here.
local RunService = game:GetService("RunService")

local mapFolder = workspace:WaitForChild("Map")
local cellFolder = mapFolder:WaitForChild("CellTrain", 30)
if not cellFolder then
	return
end

local route, mitos, cytosol = {}, {}, {}
for _, d in ipairs(cellFolder:GetDescendants()) do
	if d:IsA("BasePart") then
		local i = d.Name:match("^CellPath|(%d+)$")
		if i then
			route[tonumber(i)] = d.Position
		elseif d.Name == "Cytosol" then
			table.insert(cytosol, { part = d, home = d.Position, phase = math.random() * 6.28 })
		end
	elseif d:IsA("Model") and d.Name == "MitoModel" then
		table.insert(mitos, { model = d, home = d:GetPivot(), phase = math.random() * 6.28 })
	end
end
if #route < 2 then
	return
end

local routeDist = { 0 }
for i = 2, #route do
	routeDist[i] = routeDist[i - 1] + (route[i] - route[i - 1]).Magnitude
end
local routeLen = routeDist[#route]
local function along(d)
	for i = 2, #route do
		if routeDist[i] >= d then
			local a = (d - routeDist[i - 1]) / math.max(routeDist[i] - routeDist[i - 1], 1e-3)
			return route[i - 1]:Lerp(route[i], a), (route[i] - route[i - 1]).Unit
		end
	end
	return route[#route], (route[#route] - route[#route - 1]).Unit
end

local holder = Instance.new("Folder")
holder.Name = "CellLife"

local function part(shape, size, color, material, transparency)
	local p = Instance.new("Part")
	p.Shape = shape
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Transparency = transparency or 0
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Parent = holder
	return p
end

-- cargo colours: most vesicles carry secreted protein (gold); a few are membrane proteins (cyan)
local VESICLES = 9
local SPEED = 9 -- studs/s along the rail: slow enough to follow with your eyes
local carriers = {}
for k = 1, VESICLES do
	local gold = k % 3 ~= 0
	table.insert(carriers, {
		d = (k - 1) / VESICLES * routeLen,
		ves = part(
			Enum.PartType.Ball,
			Vector3.one * 6,
			gold and Color3.fromRGB(150, 220, 255) or Color3.fromRGB(120, 255, 220),
			Enum.Material.Glass,
			0.35
		),
		cargo = part(
			Enum.PartType.Ball,
			Vector3.one * 2.6,
			gold and Color3.fromRGB(255, 210, 90) or Color3.fromRGB(90, 255, 230),
			Enum.Material.Neon
		),
		footA = part(Enum.PartType.Ball, Vector3.one * 1.4, Color3.fromRGB(255, 120, 160), Enum.Material.Neon),
		footB = part(Enum.PartType.Ball, Vector3.one * 1.4, Color3.fromRGB(255, 120, 160), Enum.Material.Neon),
	})
end

local active = false
local t = 0
RunService.Heartbeat:Connect(function(dt)
	local cam = workspace.CurrentCamera
	local inCell = cam and cam.CFrame.Position.X < -11000 and math.abs(cam.CFrame.Position.Z) < 1000
	if inCell ~= active then
		active = inCell
		holder.Parent = active and workspace or nil
	end
	if not active then
		return
	end
	t += dt
	-- vesicle traffic; the motor protein's feet alternate one step (8 nm in real life) at a time
	for _, c in ipairs(carriers) do
		c.d = (c.d + SPEED * dt) % routeLen
		local pos, dir = along(c.d)
		local side = dir:Cross(Vector3.yAxis)
		if side.Magnitude < 0.1 then
			side = Vector3.xAxis
		end
		side = side.Unit
		local up = side:Cross(dir).Unit
		local fade = math.clamp(math.min(c.d, routeLen - c.d) / 12, 0, 1) -- appear at the ER, fuse at the membrane
		local center = pos + up * 4.2
		c.ves.CFrame = CFrame.new(center)
		c.cargo.CFrame = CFrame.new(center)
		c.ves.Transparency = 1 - 0.65 * fade
		c.cargo.Transparency = 1 - fade
		local stride = (c.d % 2) / 2
		local lift = math.sin(stride * math.pi) * 0.9
		c.footA.CFrame = CFrame.new(pos + dir * (stride - 0.5) + up * (0.6 + lift))
		c.footB.CFrame = CFrame.new(pos - dir * (stride - 0.5) + up * (0.6 + 0.9 - lift))
	end
	-- mitochondria drift and turn slowly (they really do move along microtubules)
	for _, m in ipairs(mitos) do
		local s = t * 0.25 + m.phase
		m.model:PivotTo(
			m.home
				* CFrame.new(math.sin(s) * 3, math.sin(s * 1.3) * 2, math.cos(s * 0.7) * 3)
				* CFrame.Angles(0, math.sin(s * 0.4) * 0.15, 0)
		)
	end
	-- cytosol: a gentle float (bulk move to keep it cheap)
	local parts, cfs = table.create(#cytosol), table.create(#cytosol)
	for i, c in ipairs(cytosol) do
		local s = t * 0.35 + c.phase
		parts[i] = c.part
		cfs[i] = CFrame.new(c.home + Vector3.new(math.sin(s) * 4, math.sin(s * 1.7) * 3, math.cos(s * 1.2) * 4))
	end
	workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged)
end)
