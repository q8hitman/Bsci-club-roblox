-- Paints soft desert dunes (Terrain) around the College of Science campus so the map never "just stops".
-- Terrain is not part of the Rojo project: run this once in Studio's command bar in Edit mode, then save the place.
local T = workspace.Terrain
local CELL = 8
local RADIUS = 1000
-- flat areas: the campus inside its hedges, and the wider strip with the road + parking in front
local FLAT = { { -184, 184, -170, 280 }, { -262, 262, -350, -170 } }

local function rectDist(r, x, z)
	local dx = math.max(r[1] - x, 0, x - r[2])
	local dz = math.max(r[3] - z, 0, z - r[4])
	return math.sqrt(dx * dx + dz * dz)
end

local function outside(x, z)
	return math.min(rectDist(FLAT[1], x, z), rectDist(FLAT[2], x, z))
end

T:Clear()
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
	if x % 80 == 0 then
		task.wait()
	end
end
print("dunes painted")
