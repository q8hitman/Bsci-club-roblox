-- Paints soft desert dunes around the College of Science campus when the server starts, so the campus
-- no longer sits on a flat sand sheet. Runtime version of tools/terrain_dunes.luau (kept in code so a
-- rebuilt place never loses it). It never clears terrain outside this radius (v52: the old island terrain
-- and IslandTerrain.server.luau were removed).
local T = workspace.Terrain
local CELL = 10
local RADIUS = 700
-- flat areas: the campus inside its hedges, and the wider strip with the road + parking in front
-- v59: + the museum grounds (tools/museum46.py lawn x 150..430, z -220..100); the dunes used to bury the museum
local FLAT = { { -184, 184, -170, 280 }, { -262, 262, -350, -170 }, { 146, 434, -226, 104 } }

local function rectDist(r, x, z)
	local dx = math.max(r[1] - x, 0, x - r[2])
	local dz = math.max(r[3] - z, 0, z - r[4])
	return math.sqrt(dx * dx + dz * dz)
end

local function outside(x, z)
	local d = math.huge
	for _, r in ipairs(FLAT) do
		d = math.min(d, rectDist(r, x, z))
	end
	return d
end

task.wait(2) -- let the map finish loading first
for x = -RADIUS, RADIUS, CELL do
	for z = -RADIUS, RADIUS, CELL do
		local d = outside(x, z)
		if d > 4 then
			local rise = math.clamp((d - 4) / 90, 0, 1)
			rise = rise * rise * (3 - 2 * rise) -- smoothstep: dunes start gently at the campus edge
			local big = math.noise(x / 260, z / 260, 1.7) * 0.5 + 0.5
			local ripple = math.noise(x / 70, z / 70, 9.1) * 0.5 + 0.5
			local h = rise * (6 + 46 * big + 8 * ripple)
			if h > 0.6 then
				local mat = Enum.Material.Sand
				if ripple > 0.8 and rise > 0.6 then
					mat = Enum.Material.Sandstone
				elseif d < 50 and ripple < 0.3 then
					mat = Enum.Material.Ground
				end
				T:FillBlock(CFrame.new(x, -2 + h / 2, z), Vector3.new(CELL, h + 2, CELL), mat)
			end
		end
	end
	task.wait() -- one yield per column keeps the server responsive
end
workspace:SetAttribute("CampusDunesReady", true)
