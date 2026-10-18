-- BSC Island: the game's main world, built from the official Roblox Synty packs.
-- Run from the project root:  tools/lune/lune.exe run tools/world/island.luau
-- Writes kuwait-parkour/src/world/Island.rbxm (mapped to Workspace.Island by Rojo).
-- Terrain (grass, beach, sea, lake, paths) is painted at server start by IslandTerrain.server.luau,
-- gameplay parts (portals, signs, pads) come from tools/island11.py.
local roblox = require("@lune/roblox")
local L = require("./lib")
local Instance, Vector3 = roblox.Instance, roblox.Vector3

L.origin = Vector3.new(0, 0, 9000) -- island centre (far from every other world)
-- yaw that turns a pack building's front that way. Synty fronts point along the part's LookVector
-- (verified with screenshots: shop windows / the city-hall portico are on the LookVector side).
-- LookVector at yaw θ is (-sin θ, 0, -cos θ): north (-Z) = 0, south (+Z) = 180, east (+X) = -90, west (-X) = 90.
local FACE = { north = 0, south = 180, east = -90, west = 90 }

local root = Instance.new("Folder")
root.Name = "Island"
local B = L.folder(root, "Buildings")
local N = L.folder(root, "Nature")
local P = L.folder(root, "Props")

-- tiny deterministic RNG (Lune has no Random): same island every build
local seed = 2026
local rng = {}
function rng:NextNumber(a, b)
	seed = (seed * 1103515245 + 12345) % 2147483648
	return a + (b - a) * seed / 2147483648
end
function rng:NextInteger(a, b)
	return math.floor(self:NextNumber(a, b + 1 - 1e-9))
end
local function jitter(a)
	return rng:NextNumber(-a, a)
end

-- ------------------------------------------------------------------ landmarks
L.place(B, "Bld_CityHall_01", 0, -100, FACE.south, { name = "ClubHQBuilding" })
L.place(B, "Bld_OfficeRound_Base_01", 112, -20, FACE.west, { name = "ExamHallBase" })
L.place(B, "Bld_OfficeRound_02", 112, -20, FACE.west, { y = 19, name = "ExamHallFloor" })
L.place(B, "Bld_OfficeRound_Roof_01", 112, -20, FACE.west, { y = 52, name = "ExamHallRoof" })
L.place(B, "Bld_Station_01", -108, -20, FACE.east, { name = "MinigameStation" })
L.place(B, "Bld_OfficeRound_01", 0, -230, FACE.south, { name = "ParkourTower" })
L.place(B, "Bld_Station_03", -95, 150, FACE.east, { name = "CartStation" })
L.place(B, "Env_SubwayEntrance_01", 82, 150, FACE.west, { name = "CellSubway" })
L.place(B, "Bld_Station_02", -175, 55, FACE.east, { name = "VirusLab" })
L.place(B, "Prop_Water_Tower_01", -200, 30, 0, { name = "VirusTank" })
-- v29: Research Institute (portal into the BSC research lab world)
L.place(B, "Bld_OfficeSquare_02", 168, 45, FACE.west, { name = "ResearchInstitute" })
-- v30: Science Challenge Center (classic old-campus building, portal into the quiz world)
L.place(B, "Bld_OfficeOld_Small_Base_01", 172, 108, FACE.west, { name = "ChallengeCenter" })
L.place(B, "Bld_OfficeOld_Small_Floor_01", 172, 108, FACE.west, { y = 19.9 })
L.place(B, "Bld_OfficeOld_Small_Roof_01", 172, 108, FACE.west, { y = 30.8 })

-- ------------------------------------------------------------------ food street (south avenue)
-- A continuous two-sided high street: shop at street level, 1-2 apartment floors + roof above (mixed-use
-- silhouette), giant food sign on each roof, sidewalk tiles, street trees between lamps, café tables.
-- Shop centres must match the name boards in tools/island11.py (SHOPS there).
local ROOF_SIGN = { coffee = "LargeSign_Coffee_01", donut = "LargeSign_Donut_01", shake = "LargeSign_Milkshake_01",
	ice = "LargeSign_Icecream_01", burger = "LargeSign_Burger_01", pizza = "LargeSign_Pizza_01" }
local street = {
	-- side, shop mesh, centre z, upper floors, roof sign
	{ -1, "Bld_Shop_01", 66, 2, "coffee" },
	{ -1, "Bld_Shop_Corner_01", 84.5, 1, nil },
	{ -1, "Bld_Shop_05", 103, 2, "donut" },
	{ -1, "Bld_Shop_02", 121, 1, nil },
	{ -1, "Bld_Shop_06", 139, 2, "shake" },
	{ 1, "Bld_Shop_03", 75.5, 1, "ice" },
	{ 1, "Bld_Shop_04", 102.5, 2, "burger" },
	{ 1, "Bld_Shop_01", 120.5, 1, "pizza" },
	{ 1, "Bld_Shop_05", 138.5, 2, nil },
}
local APTS = { "Bld_Apartment_01", "Bld_Apartment_02", "Bld_Apartment_03" }
for i, s in street do
	local side, mesh, z, floors, roofSign = s[1], s[2], s[3], s[4], s[5]
	local x = side * 30
	local yaw = side < 0 and FACE.east or FACE.west
	local shop = L.place(B, mesh, x, z, yaw)
	local top = shop.Size.Y - 0.05
	local width = shop.Size.X
	local bays = width > 25 and { -width / 4, width / 4 } or { 0 }
	for f = 1, floors do
		for _, dz in bays do
			local apt = L.place(B, APTS[(i + f) % #APTS + 1], x, z + dz, yaw, { y = top })
			if f == floors then
				L.place(B, "Bld_Apartment_Roof_01", x, z + dz, yaw, { y = top + apt.Size.Y - 0.05 })
			end
		end
		top += 11 - 0.05
	end
	if roofSign then
		L.place(P, ROOF_SIGN[roofSign], x, z, yaw, { y = top + 2, collide = false })
	end
end
-- v31: café tables moved off the sidewalks (they stood right in front of the shop windows) into the middle of the
-- pedestrian street, leaving the shop fronts and their order windows clear
for _, z in { 72, 97, 122, 147 } do
	L.place(P, "Prop_Table_Round_01", 0, z, 0, { collide = false, y = 0.4 })
	for _, dx in { -3, 3 } do
		L.place(P, "Prop_Stool_02", dx, z, 0, { collide = false, y = 0.4 })
	end
	L.place(P, "Prop_Umbrella_01", 0, z, 0, { y = 3.3, collide = false })
end
-- sidewalks are terrain (Concrete strips in IslandTerrain.server.luau)
for _, side in { -1, 1 } do
	-- lamps and street trees alternate along the curb
	for k, z in { 58, 70, 82, 94, 106, 118, 130, 142, 154 } do
		if k % 2 == 1 then
			L.place(P, "Prop_LightPole_Base_02", side * 12, z, side < 0 and FACE.east or FACE.west, { collide = false })
		else
			L.place(N, "Tree_Round_03", side * 12.5, z, jitter(180), { collide = false, scale = 0.8 })
		end
	end
	L.place(P, "Prop_Trashbin_01", side * 11.5, 100, 0, { collide = false })
	L.place(P, "Prop_Hydrant_01", side * 11.5, 88, 0, { collide = false })
end
-- the avenue opens into a small food court before the beach
L.place(P, "Prop_HotdogStand_01", 14, 170, FACE.west)
for _, t in { { -9, 168 }, { -2, 182 }, { 10, 188 } } do
	L.place(P, "Prop_PicnicTable_01", t[1], t[2], 90)
	L.place(P, "Prop_Umbrella_01", t[1], t[2], 0, { y = 3, collide = false })
end
L.place(P, "Prop_BusStop_01", 52, 38, FACE.west, { name = "CampusBusStop" })
L.place(P, "Veh_Car_Taxi_01", 62, 52, 0, { collide = true })
-- trees frame the short walk from the plaza into the street
for _, x in { -13, 13 } do
	L.place(N, "Tree_Round_03", x, 50, jitter(180), { collide = false, scale = 0.9 })
end

-- ------------------------------------------------------------------ plaza dressing
-- Calm, readable plaza: a ring of 8 lamps, 4 planted beds on the diagonals with a bench facing the monument,
-- open axes to the four gateways, and tree-lined walks to the HQ, the exam hall and the arcade.
for i = 0, 7 do
	local a = i * math.pi / 4 + math.pi / 8
	L.place(P, "Prop_LightPole_Base_02", math.cos(a) * 44, math.sin(a) * 44, 90 - math.deg(a), { collide = false })
end
for i = 0, 3 do
	local a = i * math.pi / 2 + math.pi / 4
	local cx, cz = math.cos(a) * 31, math.sin(a) * 31
	L.place(N, "Tree_Round_04", cx, cz, jitter(180), { collide = false, scale = 0.75 })
	L.place(N, "Plant_Bush_02", cx + 3, cz - 2, jitter(180), { collide = false, scale = 1.4 })
	for k = 0, 4 do
		local b = a + (k - 2) * 0.12
		L.place(N, k % 2 == 0 and "Plant_Flowers_01" or "PurpleFlower", math.cos(b) * 26, math.sin(b) * 26, jitter(180),
			{ collide = false, scale = 1.5 })
	end
	-- bench in front of the bed, facing the monument (LookVector toward the centre)
	L.place(P, "Prop_ParkBench_01", math.cos(a) * 21, math.sin(a) * 21, 90 - math.deg(a), { collide = false })
end
-- formal front garden of the HQ: trees stand back from the walk (|x| 18+) so the portico stays readable,
-- flower beds fill the lawns either side
for _, x in { -20, 20 } do
	L.place(N, "Tree_Round_03", x, -50, jitter(180), { collide = false, scale = 0.85 })
	for k = 0, 5 do
		L.place(N, k % 2 == 0 and "Plant_Flowers_01" or "PurpleFlower", x + (x > 0 and 6 or -6) + (k % 3) * (x > 0 and 4 or -4),
			-60 - math.floor(k / 3) * 5, jitter(180), { collide = false, scale = 1.5 })
	end
	L.place(N, "Plant_Bush_01", x + (x > 0 and 14 or -14), -66, jitter(180), { collide = false, scale = 1.6 })
end
for _, x in { 50, 62 } do -- walks to the exam hall (east) and the arcade (west)
	L.place(N, "Tree_Round_03", x, -32, jitter(180), { collide = false, scale = 0.85 })
	L.place(N, "Tree_Round_03", -x, -32, jitter(180), { collide = false, scale = 0.85 })
end

-- ------------------------------------------------------------------ park + lake (north-east)
local trees = { "Tree_Round_01", "Tree_Round_02", "Tree_Round_05", "Tree_TallRound_01", "Tree_04" }
local parkSpots = { { 70, -70 }, { 95, -110 }, { 180, -40 }, { 200, -100 }, { 175, -150 }, { 120, -165 }, { 60, -150 },
	{ 215, -10 }, { 205, 0 } } -- v29: (150,20)/(200,60) cleared for the research institute
for i, s in parkSpots do
	L.place(N, trees[(i - 1) % #trees + 1], s[1] + jitter(4), s[2] + jitter(4), jitter(180), { collide = false })
	L.place(N, "Plant_Bush_0" .. (i % 3 + 1), s[1] + 9, s[2] + 6, jitter(180), { collide = false })
end
L.place(P, "Prop_Bridge_Curved_01", 145, -85, 90, { y = -1.5, name = "LakeBridge" })
for _, s in { { 115, -60 }, { 175, -110 }, { 130, -120 } } do
	L.place(P, "Prop_ParkBench_01", s[1], s[2], jitter(180), { collide = false })
end
L.place(P, "Prop_PicnicTable_01", 185, -60, 30)
L.place(N, "Prop_CampFire_01", 190, -30, 0, { collide = false }) -- v29: moved off the institute plot
for i = 1, 6 do
	L.place(N, "Plant_Reeds_0" .. (i % 2 + 1), 145 + math.cos(i) * 33, -85 + math.sin(i) * 33, jitter(180), { collide = false, scale = 2 })
end
for i = 1, 5 do
	L.place(N, "Plant_Lillypad_Large_0" .. (i % 3 + 1), 140 + jitter(18), -85 + jitter(18), jitter(180), { y = -0.6, collide = false })
end

-- ------------------------------------------------------------------ groves (fill the open lawns south of the plaza)
-- small natural clusters (3 trees + bushes + a rock), kept off the walking paths and the street block
local groveTrees = { "Tree_Round_01", "Tree_Round_02", "Tree_Round_05", "Tree_04", "Tree_TallRound_01" }
local groves = { { -62, 98 }, { -128, 112 }, { -112, 198 }, { -178, 150 }, { -56, 196 }, { 78, 96 }, { 132, 84 }, { 140, 196 },
	{ 202, 146 }, { 96, 208 }, { -205, 100 } }
for g, c in groves do
	for t = 0, 2 do
		local a = g * 1.3 + t * 2.1
		L.place(N, groveTrees[(g + t) % #groveTrees + 1], c[1] + math.cos(a) * 9, c[2] + math.sin(a) * 9, jitter(180),
			{ collide = false, scale = 0.8 + ((g + t) % 3) * 0.15 })
	end
	L.place(N, "Plant_Bush_0" .. (g % 3 + 1), c[1] + 6, c[2] - 7, jitter(180), { collide = false, scale = 1.5 })
	L.place(N, "Plant_Bush_0" .. ((g + 1) % 3 + 1), c[1] - 8, c[2] + 5, jitter(180), { collide = false, scale = 1.2 })
	if g % 2 == 0 then
		L.place(N, "Rock_Boulder_01", c[1] + 2, c[2] + 9, jitter(180), { scale = 0.6, sink = 1 })
	end
end

-- ------------------------------------------------------------------ forest + rocks (north-west), mountains behind
local pines = { "Tree_PolyPine_01", "Pine_Tree_Pine_01", "Pine_Tree_Pine_Large_01", "Tree_PolyPine_02", "Tree_01", "Tree_02" }
for i = 1, 34 do
	local x = rng:NextNumber(-270, -80)
	local z = rng:NextNumber(-260, -60)
	if not (x > -140 and z > -60) then
		L.place(N, pines[rng:NextInteger(1, #pines)], x, z, jitter(180), { collide = false, scale = rng:NextNumber(0.9, 1.3) })
	end
end
for _, r in { { "Rock_Cluster_Large_01", -150, -150 }, { "Rock_Cluster_Large_04", -230, -90 }, { "Rock_Cluster_Large_02", -90, -190 },
	{ "Rock_Pile_01", -60, -60 }, { "Rock_Boulder_01", 60, 60 }, { "Rock_Pile_Curved_01", 230, 100 } } do
	L.place(N, r[1], r[2], r[3], jitter(180))
end
for _, m in { { "Terrain_Mountain_01", -330, -280, 1.6 }, { "Terrain_Mountain_03", -60, -380, 1.8 }, { "Terrain_Mountain_02", 260, -330, 2.0 },
	{ "Terrain_Mountain_01", 380, -120, 1.4 }, { "Terrain_Mountain_02", -380, 40, 1.6 } } do
	L.place(N, m[1], m[2], m[3], jitter(180), { scale = m[4], sink = 4 })
end

-- ------------------------------------------------------------------ beach (south)
for i = 1, 9 do
	local x = -120 + i * 26
	L.place(P, "Prop_Deckchair_01", x, 238, 180 + jitter(15), { collide = false })
	if i % 2 == 1 then
		L.place(P, "Prop_Umbrella_01", x + 4, 236, 0, { y = 3, collide = false })
	end
	L.place(N, "Plant_PalmBush_01", x + 10, 218, jitter(180), { collide = false, scale = 2.2 })
end
L.place(P, "Prop_Bridge_Curved_01", 150, 262, 0, { y = -2, scale = 1.4, name = "Pier" })

-- ------------------------------------------------------------------ sky dressing
for i = 1, 9 do
	local a = i * 2 * math.pi / 9
	L.place(N, "Env_Cloud_0" .. (i % 3 + 1), math.cos(a) * rng:NextNumber(350, 650), math.sin(a) * rng:NextNumber(350, 650),
		math.deg(a), { y = rng:NextNumber(160, 260), collide = false, shadow = false, scale = rng:NextNumber(0.8, 1.3) })
end

L.save(root, "kuwait-parkour/src/world/Island.rbxm")
print("island written")
