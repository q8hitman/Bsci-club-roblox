-- Paints BSC Island's terrain when the server starts (kept in code so a rebuilt place never loses it):
-- grassy island with a noisy coastline, beaches sloping into the sea, a park lake, cobblestone paths.
-- Island origin matches tools/world/island.luau.
local Terrain = workspace.Terrain
local O = Vector3.new(0, 0, 9000)
local CELL = 6

Terrain:SetMaterialColor(Enum.Material.Grass, Color3.fromRGB(116, 178, 82))
Terrain:SetMaterialColor(Enum.Material.Sand, Color3.fromRGB(236, 212, 158))
Terrain:SetMaterialColor(Enum.Material.Cobblestone, Color3.fromRGB(196, 186, 170))
Terrain:SetMaterialColor(Enum.Material.Pavement, Color3.fromRGB(176, 172, 168))
Terrain:SetMaterialColor(Enum.Material.Ground, Color3.fromRGB(150, 120, 86))
Terrain:SetMaterialColor(Enum.Material.Concrete, Color3.fromRGB(214, 206, 192))
Terrain.WaterColor = Color3.fromRGB(46, 178, 196)
Terrain.WaterTransparency = 0.55
Terrain.WaterReflectance = 0.4
Terrain.WaterWaveSize = 0.12
Terrain.WaterWaveSpeed = 8
if not Terrain:FindFirstChildOfClass("Clouds") then
	local clouds = Instance.new("Clouds") -- soft volumetric clouds (big visual upgrade over an empty sky)
	clouds.Cover = 0.55
	clouds.Density = 0.6
	clouds.Color = Color3.fromRGB(255, 255, 255)
	clouds.Parent = Terrain
end
pcall(function()
	Terrain.Decoration = true -- animated grass blades (ignored where not supported)
end)

local function radiusAt(angle)
	-- coastline: an ellipse roughened with noise
	local base = 300 + 20 * math.cos(angle * 2) + 14 * math.sin(angle * 3)
	return base + 18 * math.noise(math.cos(angle) * 2, math.sin(angle) * 2, 3.3)
end

-- sea first (sand seabed + water), the island is filled on top of it
Terrain:FillBlock(CFrame.new(O + Vector3.new(0, -26, 0)), Vector3.new(1700, 8, 1700), Enum.Material.Sand)
Terrain:FillBlock(CFrame.new(O + Vector3.new(0, -12.5, 0)), Vector3.new(1700, 21, 1700), Enum.Material.Water) -- sea surface at y -2, below the land

local R = 360
for x = -R, R, CELL do
	for z = -R, R, CELL do
		local d = math.sqrt(x * x + z * z)
		local edge = radiusAt(math.atan2(z, x))
		if d < edge then
			local inland = edge - d
			local top, mat
			if inland < 26 then -- beach slope down to the water
				top = -5 + inland / 26 * 6
				mat = Enum.Material.Sand
			else
				top = d > 240 and 1 + math.max(0, math.noise(x / 90, z / 90, 1.1)) * 3 or 0.4 -- flat where things stand, gentle hills near the coast
				mat = Enum.Material.Grass
			end
			local bottom = -24
			Terrain:FillBlock(
				CFrame.new(O + Vector3.new(x, (top + bottom) / 2, z)),
				Vector3.new(CELL, top - bottom, CELL),
				mat
			)
		end
	end
	if x % 60 == 0 then
		task.wait()
	end
end

-- park lake
Terrain:FillBall(O + Vector3.new(145, -4, -85), 30, Enum.Material.Sand)
Terrain:FillBlock(CFrame.new(O + Vector3.new(145, -2, -85)), Vector3.new(52, 4, 52), Enum.Material.Air)
Terrain:FillCylinder(CFrame.new(O + Vector3.new(145, -2.5, -85)), 3, 26, Enum.Material.Water)

-- paths (cobblestone) and the plaza / avenue (pavement)
local function path(a, b, w, mat)
	local mid = (a + b) / 2
	local len = (b - a).Magnitude
	local cf = CFrame.lookAt(O + Vector3.new(mid.X, 0, mid.Y), O + Vector3.new(b.X, 0, b.Y))
	-- 4 studs deep (top at y 1): a thin fill only partly covers the grass voxels and may not replace their material
	Terrain:FillBlock(cf * CFrame.new(0, -1, 0), Vector3.new(w, 4, len), mat)
end
Terrain:FillCylinder(CFrame.new(O + Vector3.new(0, -1, 0)), 4, 46, Enum.Material.Cobblestone)
-- food street sidewalks (between the curb |x| 11 and the shop fronts |x| 20.5)
path(Vector2.new(-15.75, 55), Vector2.new(-15.75, 156), 9.5, Enum.Material.Concrete)
path(Vector2.new(15.75, 55), Vector2.new(15.75, 156), 9.5, Enum.Material.Concrete)
path(Vector2.new(0, 40), Vector2.new(0, 205), 22, Enum.Material.Pavement)
path(Vector2.new(0, -40), Vector2.new(0, -72), 16, Enum.Material.Cobblestone)
path(Vector2.new(40, -6), Vector2.new(78, -16), 14, Enum.Material.Cobblestone)
path(Vector2.new(-40, -6), Vector2.new(-88, -16), 14, Enum.Material.Cobblestone)
path(Vector2.new(0, -130), Vector2.new(0, -192), 14, Enum.Material.Cobblestone)
path(Vector2.new(30, -30), Vector2.new(110, -90), 8, Enum.Material.Cobblestone)
path(Vector2.new(-14, 150), Vector2.new(-76, 150), 12, Enum.Material.Cobblestone)
path(Vector2.new(14, 150), Vector2.new(66, 150), 12, Enum.Material.Cobblestone)
path(Vector2.new(-40, 20), Vector2.new(-150, 55), 10, Enum.Material.Cobblestone)
path(Vector2.new(36, 28), Vector2.new(50, 38), 8, Enum.Material.Cobblestone)

workspace:SetAttribute("IslandReady", true)
