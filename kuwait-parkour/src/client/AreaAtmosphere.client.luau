-- Per-area look (local to this player): every world gets its own time of day, ambient light, haze and colour grade,
-- blended over ~1.2 s when the player moves between worlds. The haze is also what keeps the far-away worlds
-- (all built thousands of studs apart) from ever showing up on the horizon.
-- Space stages (LowGrav) are handled by Zones.client: it switches to night on entry and restores this script's values.
local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local Zones = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Zones"))
local okRooms, CartRooms = pcall(function()
	return require(ReplicatedStorage.Shared:WaitForChild("CartRooms", 5))
end)
CartRooms = okRooms and type(CartRooms) == "table" and CartRooms.tops and CartRooms or { tops = {}, zones = {} }
local atmosphere = Lighting:FindFirstChildOfClass("Atmosphere")
local grade = Lighting:FindFirstChildOfClass("ColorCorrectionEffect")

local function rgb(r, g, b)
	return Color3.fromRGB(r, g, b)
end

-- clock, ambient, outdoor, atmosphere {density, haze, color, decay}, grade {tint, saturation, contrast}
local PRESETS = {
	island = {
		16.3,
		rgb(118, 118, 122),
		rgb(128, 128, 133),
		{ 0.24, 1.1, rgb(219, 217, 209), rgb(235, 194, 153) },
		{ rgb(255, 249, 240), 0.14, 0.1 },
	},
	campus = {
		13.2,
		rgb(130, 122, 110),
		rgb(150, 140, 124),
		{ 0.34, 2.2, rgb(232, 214, 182), rgb(222, 190, 140) },
		{ rgb(255, 246, 228), 0.08, 0.08 },
	}, -- Kuwait midday: warm dust haze
	campus_in = {
		13.2,
		rgb(112, 106, 98),
		rgb(122, 116, 106),
		{ 0.3, 1.2, rgb(232, 220, 200), rgb(222, 196, 156) },
		{ rgb(255, 248, 236), 0.04, 0.12 },
	}, -- v35: inside the south building: lower ambient so the white marble and lights don't glare
	hq = {
		17.4,
		rgb(140, 128, 112),
		rgb(150, 138, 120),
		{ 0.4, 0.2, rgb(240, 232, 220), rgb(240, 214, 180) },
		{ rgb(255, 244, 228), 0.12, 0.06 },
	}, -- warm club interior; dense haze hides the void outside
	exam = {
		14,
		rgb(130, 130, 134),
		rgb(140, 140, 146),
		{ 0.45, 0.2, rgb(236, 236, 240), rgb(220, 220, 230) },
		{ rgb(250, 250, 255), 0.02, 0.05 },
	},
	arcade = {
		19.6,
		rgb(120, 96, 140),
		rgb(140, 110, 160),
		{ 0.3, 1.6, rgb(230, 190, 235), rgb(255, 160, 220) },
		{ rgb(255, 238, 255), 0.25, 0.12 },
	}, -- inside a giant cell, neon dusk
	racing = {
		13.5,
		rgb(156, 166, 178),
		rgb(168, 182, 196),
		{ 0.4, 1.4, rgb(210, 230, 242), rgb(170, 200, 228) },
		{ rgb(245, 252, 255), 0.08, 0.06 },
	}, -- daylight racing: silhouettes and road edges remain readable
	virus = {
		18.5,
		rgb(100, 120, 96),
		rgb(110, 132, 104),
		{ 0.38, 1.4, rgb(196, 226, 186), rgb(150, 220, 120) },
		{ rgb(236, 255, 232), 0.05, 0.12 },
	},
	cell = {
		13.5,
		rgb(160, 132, 190),
		rgb(170, 140, 200),
		{ 0.28, 1.0, rgb(214, 180, 236), rgb(230, 170, 255) },
		{ rgb(250, 240, 255), 0.16, 0.08 },
	}, -- the Cell Train world: bright violet cytoplasm, organelles readable
	cart = {
		20,
		rgb(120, 90, 130),
		rgb(140, 104, 150),
		{ 0.32, 1.6, rgb(210, 170, 230), rgb(255, 170, 230) },
		{ rgb(255, 238, 250), 0.2, 0.1 },
	},
	lab = {
		12,
		rgb(150, 154, 160),
		rgb(160, 164, 170),
		{ 0.45, 0, rgb(240, 244, 248), rgb(220, 230, 240) },
		{ rgb(248, 252, 255), 0.04, 0.06 },
	}, -- research institute: clean, bright, neutral
	quiz = {
		14.5,
		rgb(150, 136, 118),
		rgb(160, 146, 128),
		{ 0.4, 0.15, rgb(244, 234, 216), rgb(240, 214, 170) },
		{ rgb(255, 246, 232), 0.08, 0.06 },
	}, -- challenge center: warm old library
	-- parkour, one look per specialty (index = zone)
	z1 = {
		9.5,
		rgb(118, 128, 112),
		rgb(132, 146, 124),
		{ 0.26, 1.2, rgb(214, 232, 206), rgb(200, 236, 170) },
		{ rgb(246, 255, 240), 0.16, 0.06 },
	}, -- plants: fresh green morning
	z2 = {
		15.8,
		rgb(132, 120, 102),
		rgb(150, 134, 110),
		{ 0.3, 1.8, rgb(236, 214, 176), rgb(240, 196, 130) },
		{ rgb(255, 246, 226), 0.12, 0.08 },
	}, -- animals: savanna afternoon
	z3 = {
		12,
		rgb(112, 128, 136),
		rgb(124, 142, 152),
		{ 0.28, 0.8, rgb(206, 228, 236), rgb(170, 220, 240) },
		{ rgb(240, 252, 255), 0.06, 0.1 },
	}, -- micro: clean lab light
	z4 = {
		11,
		rgb(130, 112, 132),
		rgb(146, 124, 148),
		{ 0.28, 1.0, rgb(232, 210, 236), rgb(240, 170, 230) },
		{ rgb(255, 242, 255), 0.18, 0.08 },
	}, -- biochem: reactive pinks
	z5 = {
		18.2,
		rgb(96, 106, 140),
		rgb(108, 118, 156),
		{ 0.3, 1.4, rgb(186, 200, 236), rgb(150, 170, 255) },
		{ rgb(238, 242, 255), 0.12, 0.12 },
	}, -- molecular: blue twilight
	z6 = {
		10.2,
		rgb(130, 126, 104),
		rgb(150, 144, 116),
		{ 0.26, 1.6, rgb(236, 226, 190), rgb(240, 214, 140) },
		{ rgb(255, 250, 230), 0.14, 0.06 },
	}, -- agriculture: sunny fields
	z7 = {
		18.9,
		rgb(104, 100, 108),
		rgb(116, 110, 120),
		{ 0.34, 2.0, rgb(200, 196, 210), rgb(190, 170, 200) },
		{ rgb(244, 240, 255), -0.15, 0.16 },
	}, -- forensics: desaturated dusk noir
	z8 = {
		20.3,
		rgb(90, 110, 130),
		rgb(100, 124, 150),
		{ 0.3, 1.2, rgb(170, 220, 236), rgb(120, 255, 230) },
		{ rgb(236, 255, 252), 0.2, 0.12 },
	}, -- biotech: teal neon evening
}

-- z boundaries of the 8 parkour zones (from their first checkpoints)
local zoneZ = {}
do
	local mapFolder = workspace:WaitForChild("Map")
	local cps = {}
	for _, d in ipairs(mapFolder:GetDescendants()) do
		local n = d:IsA("BasePart") and d.Name:match("^Checkpoint_(%d+)$")
		if n then
			cps[tonumber(n)] = d.Position.Z
		end
	end
	for i, z in ipairs(Zones) do
		zoneZ[i] = cps[z.start] or (i - 1) * 1100
	end
end

local function areaAt(p)
	if player:GetAttribute("InMicroRace") or player:GetAttribute("InLaserEscape") then
		return "racing"
	end
	if p.X > 10000 then
		local zone = 1
		for i, z0 in ipairs(zoneZ) do
			if p.Z >= z0 - 20 then
				zone = i
			end
		end
		return "z" .. zone
	elseif p.X < -10000 then
		return "cell"
	elseif p.X < -7000 and p.Z > 7000 then
		-- rail hall (v31): one room per specialty in ride order; each room reuses that specialty's parkour-zone look
		local room = 1
		for i, zTop in ipairs(CartRooms.tops) do
			if p.Z <= zTop then
				room = i
			end
		end
		return "z" .. (CartRooms.zones[room] or 1)
	elseif math.abs(p.X) < 1000 and p.Z < -5000 and p.Z > -7100 then
		return "quiz"
	elseif p.Z < -12300 then
		return "virus"
	elseif p.Z < -10000 then
		return "hq"
	elseif p.X > 4000 and p.Z < -4000 then
		return "exam"
	elseif p.X < -4000 and p.Z < -4000 then
		return "arcade"
	elseif p.X > 4000 and p.Z > 4000 then
		return "lab"
	elseif p.Z > 7000 then
		return "island"
	end
	if p.X > -90 and p.X < 90 and p.Z > -160 and p.Z < -30 and p.Y < 90 then
		return "campus_in"
	end
	return "campus"
end

local current = nil
local function apply(name)
	local pr = PRESETS[name]
	if not pr then
		return
	end
	current = name
	local info = TweenInfo.new(1.2, Enum.EasingStyle.Sine)
	TweenService:Create(Lighting, info, { ClockTime = pr[1], Ambient = pr[2], OutdoorAmbient = pr[3] }):Play()
	if atmosphere then
		local a = pr[4]
		TweenService:Create(atmosphere, info, { Density = a[1], Haze = a[2], Color = a[3], Decay = a[4] }):Play()
	end
	if grade then
		local g = pr[5]
		TweenService:Create(grade, info, { TintColor = g[1], Saturation = g[2], Contrast = g[3] }):Play()
	end
end

task.spawn(function()
	while true do
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		-- the character's own position (the Cell Train also carries the root along with the train)
		local p = root and root.Position or (root and root.Position)
		if p and workspace.Gravity > 100 then -- leave the look alone while a space stage has it (Zones.client)
			local area = areaAt(p)
			if area ~= current then
				apply(area)
			end
		end
		task.wait(0.4)
	end
end)
