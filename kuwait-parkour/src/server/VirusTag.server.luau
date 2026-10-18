-- Virus Tag (لعبة الفيروس): rounds in the floating arena next to the HQ.
-- Needs 2+ players inside. One random player (two if 6+) starts infected; infected players spread it by
-- getting close to healthy ones. Vaccines appear around the arena and give a short shield.
-- Survivors at the end win coins; if the virus infects everyone, the starting virus wins.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local notify = ReplicatedStorage:WaitForChild("Notify")
local mapFolder = workspace:WaitForChild("Map")
local center = mapFolder:WaitForChild("VirusArena"):WaitForChild("VirusCenter")

local ARENA_RADIUS = 68
local ROUND_TIME = 75
local COUNTDOWN = 10
local TOUCH_DIST = 4.5
local SHIELD_TIME = 6
local HEALTHY_SPEED, VIRUS_SPEED = 16, 19
local FACTS = {
	"الفيروس ما يقدر يتكاثر إلا داخل خلية حيّة 🦠",
	"اللقاح يدرّب جهاز المناعة يتعرّف على الميكروب قبل لا يصيبك 💉",
	"غسل اليدين بالصابون من أقوى طرق منع العدوى 🧼",
	"المضادات الحيوية تقتل البكتيريا… بس ما تأثر على الفيروسات 💊",
}

local vaccineSpots = {}
for _, inst in ipairs(mapFolder.VirusArena:GetChildren()) do
	if inst.Name:match("^VaccineSpot|") then
		table.insert(vaccineSpots, inst)
	end
end

-- shared state for clients: workspace attributes "VirusPhase" (waiting/countdown/running) and "VirusEnds";
-- per player: attribute "Virus" = "healthy" | "infected" | nil
workspace:SetAttribute("VirusPhase", "waiting")

local function inArena(player)
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then
		return false
	end
	local d = root.Position - center.Position
	return Vector3.new(d.X, 0, d.Z).Magnitude < ARENA_RADIUS and math.abs(d.Y) < 40
end

local function arenaPlayers()
	local list = {}
	for _, p in ipairs(Players:GetPlayers()) do
		if inArena(p) then
			table.insert(list, p)
		end
	end
	return list
end

local function setLook(player, infected)
	local char = player.Character
	if not char then
		return
	end
	local hum = char:FindFirstChildOfClass("Humanoid")
	local old = char:FindFirstChild("VirusGlow")
	if old then
		old:Destroy()
	end
	if infected == nil then
		if hum then
			hum.WalkSpeed = HEALTHY_SPEED
		end
		return
	end
	local h = Instance.new("Highlight")
	h.Name = "VirusGlow"
	h.FillColor = infected and Color3.fromRGB(120, 255, 90) or Color3.fromRGB(120, 200, 255)
	h.FillTransparency = infected and 0.45 or 0.85
	h.OutlineColor = infected and Color3.fromRGB(60, 200, 40) or Color3.fromRGB(255, 255, 255)
	h.Parent = char
	if hum then
		hum.WalkSpeed = infected and VIRUS_SPEED or HEALTHY_SPEED
	end
end

local function clearPlayer(player)
	player:SetAttribute("Virus", nil)
	setLook(player, nil)
end

local shieldUntil = {}
local vaccines = {}

local function spawnVaccine()
	if #vaccineSpots == 0 then
		return
	end
	local spot = vaccineSpots[math.random(1, #vaccineSpots)]
	local v = Instance.new("Part")
	v.Name = "Vaccine"
	v.Shape = Enum.PartType.Ball
	v.Size = Vector3.new(2.4, 2.4, 2.4)
	v.Material = Enum.Material.Neon
	v.Color = Color3.fromRGB(110, 200, 255)
	v.Anchored = true
	v.CanCollide = false
	v.CFrame = spot.CFrame
	v.Parent = workspace
	local light = Instance.new("PointLight")
	light.Color = v.Color
	light.Range = 12
	light.Parent = v
	table.insert(vaccines, v)
	v.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if player and player:GetAttribute("Virus") == "healthy" and v.Parent then
			v:Destroy()
			shieldUntil[player] = os.clock() + SHIELD_TIME
			local char = player.Character
			if char and not char:FindFirstChild("VaccineShield") then
				local ff = Instance.new("ForceField")
				ff.Name = "VaccineShield"
				ff.Parent = char
				task.delay(SHIELD_TIME, function()
					ff:Destroy()
				end)
			end
			notify:FireClient(player, "💉 لقاح! محمي " .. SHIELD_TIME .. " ثواني", "collect")
		end
	end)
end

local function cleanupVaccines()
	for _, v in ipairs(vaccines) do
		if v.Parent then
			v:Destroy()
		end
	end
	vaccines = {}
end

local function broadcast(list, text, kind)
	for _, p in ipairs(list) do
		notify:FireClient(p, text, kind)
	end
end

local function runRound(players)
	workspace:SetAttribute("VirusPhase", "running")
	workspace:SetAttribute("VirusEnds", workspace:GetServerTimeNow() + ROUND_TIME)
	local fact = FACTS[math.random(1, #FACTS)]
	local zeroCount = #players >= 6 and 2 or 1
	local shuffled = table.clone(players)
	for i = #shuffled, 2, -1 do
		local j = math.random(1, i)
		shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
	end
	local zero = {}
	for i, p in ipairs(shuffled) do
		local infected = i <= zeroCount
		p:SetAttribute("Virus", infected and "infected" or "healthy")
		setLook(p, infected)
		if infected then
			zero[p] = true
			notify:FireClient(
				p,
				"🦠 أنت الفيروس! المس الكل قبل لا يخلص الوقت",
				"wrong"
			)
		else
			notify:FireClient(p, "🏃 اهرب! وجمّع اللقاح 💉\n" .. fact, "info")
		end
	end
	local endsAt = os.clock() + ROUND_TIME
	local nextVaccine = os.clock() + 8
	while os.clock() < endsAt do
		task.wait(0.1)
		local live, sick, healthy = {}, {}, {}
		for _, p in ipairs(players) do
			if p.Parent and p:GetAttribute("Virus") and inArena(p) then
				table.insert(live, p)
				if p:GetAttribute("Virus") == "infected" then
					table.insert(sick, p)
				else
					table.insert(healthy, p)
				end
			elseif p:GetAttribute("Virus") then
				clearPlayer(p) -- left the arena or the game: out of this round
			end
		end
		if #healthy == 0 or #sick == 0 then
			break
		end
		for _, v in ipairs(sick) do
			local vr = v.Character and v.Character:FindFirstChild("HumanoidRootPart")
			for _, h in ipairs(healthy) do
				local hr = h.Character and h.Character:FindFirstChild("HumanoidRootPart")
				if
					vr
					and hr
					and h:GetAttribute("Virus") == "healthy"
					and (vr.Position - hr.Position).Magnitude < TOUCH_DIST
					and not (shieldUntil[h] and os.clock() < shieldUntil[h])
				then
					h:SetAttribute("Virus", "infected")
					setLook(h, true)
					notify:FireClient(
						h,
						"🤢 انصبت! الحين أنت فيروس… عدِ الباقين",
						"wrong"
					)
					broadcast(live, ("🦠 %s انصاب!"):format(h.DisplayName), "info")
				end
			end
		end
		if os.clock() > nextVaccine then
			nextVaccine = os.clock() + 12
			spawnVaccine()
		end
	end
	-- results
	local survivors, everyone = {}, {}
	for _, p in ipairs(players) do
		if p.Parent and p:GetAttribute("Virus") then
			table.insert(everyone, p)
			if p:GetAttribute("Virus") == "healthy" then
				table.insert(survivors, p)
			end
		end
	end
	for _, p in ipairs(everyone) do
		local s = Profiles.state[p]
		if #survivors > 0 and p:GetAttribute("Virus") == "healthy" then
			if s then
				s.coins += 15
				p:SetAttribute("Coins", s.coins)
			end
			notify:FireClient(p, "💪 نجيت من العدوى! +15 💰", "ach")
			if Profiles.award then
				Profiles.award(p, "virus_survive")
			end
		elseif #survivors == 0 and zero[p] then
			if s then
				s.coins += 15
				p:SetAttribute("Coins", s.coins)
			end
			notify:FireClient(p, "🦠 عديت الكل! +15 💰", "ach")
			if Profiles.award then
				Profiles.award(p, "virus_zero")
			end
		else
			notify:FireClient(
				p,
				#survivors > 0 and ("🏁 انتهت الجولة: نجا %d"):format(#survivors)
					or "🏁 الفيروس فاز هالمرة!",
				"info"
			)
		end
		clearPlayer(p)
	end
	cleanupVaccines()
	table.clear(shieldUntil)
end

task.spawn(function()
	while true do
		task.wait(1)
		local list = arenaPlayers()
		if #list < 2 then
			workspace:SetAttribute("VirusPhase", "waiting")
			workspace:SetAttribute("VirusCount", #list)
		else
			workspace:SetAttribute("VirusPhase", "countdown")
			workspace:SetAttribute("VirusEnds", workspace:GetServerTimeNow() + COUNTDOWN)
			task.wait(COUNTDOWN)
			list = arenaPlayers()
			if #list >= 2 then
				runRound(list)
				task.wait(5)
			end
		end
	end
end)

Players.PlayerRemoving:Connect(function(player)
	shieldUntil[player] = nil
end)
