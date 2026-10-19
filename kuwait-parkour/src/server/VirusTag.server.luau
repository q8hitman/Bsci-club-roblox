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

local virusRng = Random.new()
local lastZero = {} -- [Player] = true if picked as Patient Zero in the immediately preceding round

local function runSoloDroneRound(player)
	workspace:SetAttribute("VirusPhase", "running")
	local soloTime = 40
	workspace:SetAttribute("VirusEnds", workspace:GetServerTimeNow() + soloTime)
	player:SetAttribute("Virus", "healthy")
	setLook(player, false)
	notify:FireClient(
		player,
		"🤖 جولة تدريب فردية! اهرب من كبسولة الفيروس الذكية وجمّع اللقاحات 💉",
		"info"
	)
	local drone = Instance.new("Part")
	drone.Name = "BioVirusDrone"
	drone.Shape = Enum.PartType.Ball
	drone.Size = Vector3.new(4.2, 4.2, 4.2)
	drone.Material = Enum.Material.Neon
	drone.Color = Color3.fromRGB(110, 255, 80)
	drone.Anchored = true
	drone.CanCollide = false
	drone.CFrame = center.CFrame + Vector3.new(0, 3.5, -28)
	drone.Parent = workspace
	spawnVaccine()
	local endsAt = os.clock() + soloTime
	local survived = true
	while os.clock() < endsAt do
		task.wait(0.1)
		if not (player.Parent and inArena(player)) then
			survived = false
			break
		end
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		if not root then
			survived = false
			break
		end
		local toPlayer = Vector3.new(root.Position.X - drone.Position.X, 0, root.Position.Z - drone.Position.Z)
		if toPlayer.Magnitude > 0.5 then
			local step = toPlayer.Unit * (14.5 * 0.1)
			drone.CFrame = CFrame.new(
				drone.Position.X + step.X,
				center.Position.Y + 3.2 + math.sin(os.clock() * 4) * 0.6,
				drone.Position.Z + step.Z
			)
		end
		if
			(root.Position - drone.Position).Magnitude < TOUCH_DIST
			and not (shieldUntil[player] and os.clock() < shieldUntil[player])
		then
			survived = false
			notify:FireClient(
				player,
				"🤢 لمستك كبسولة الفيروس! حاول مرة ثانية",
				"wrong"
			)
			break
		end
	end
	drone:Destroy()
	cleanupVaccines()
	table.clear(shieldUntil)
	if survived and player.Parent and inArena(player) then
		local s = Profiles.state[player]
		if s then
			s.coins += 15
			player:SetAttribute("Coins", s.coins)
		end
		notify:FireClient(player, "💪 نجيت في تدريب المناعة! +15 💰", "ach")
		if Profiles.award then
			Profiles.award(player, "virus_survive")
		end
	end
	clearPlayer(player)
end

local function runRound(players)
	workspace:SetAttribute("VirusPhase", "running")
	workspace:SetAttribute("VirusEnds", workspace:GetServerTimeNow() + ROUND_TIME)
	local fact = FACTS[virusRng:NextInteger(1, #FACTS)]
	local zeroCount = #players >= 6 and 2 or 1
	local fresh, repeaters = {}, {}
	for _, p in ipairs(players) do
		if lastZero[p] then
			table.insert(repeaters, p)
		else
			table.insert(fresh, p)
		end
	end
	for i = #fresh, 2, -1 do
		local j = virusRng:NextInteger(1, i)
		fresh[i], fresh[j] = fresh[j], fresh[i]
	end
	for i = #repeaters, 2, -1 do
		local j = virusRng:NextInteger(1, i)
		repeaters[i], repeaters[j] = repeaters[j], repeaters[i]
	end
	local shuffled = {}
	for _, p in ipairs(fresh) do
		table.insert(shuffled, p)
	end
	for _, p in ipairs(repeaters) do
		table.insert(shuffled, p)
	end
	local zero = {}
	table.clear(lastZero)
	for i, p in ipairs(shuffled) do
		local infected = i <= zeroCount
		p:SetAttribute("Virus", infected and "infected" or "healthy")
		setLook(p, infected)
		if infected then
			zero[p] = true
			lastZero[p] = true
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
	local nextSurge = os.clock() + 18
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
		if os.clock() > nextSurge then
			nextSurge = os.clock() + 20
			for _, p in ipairs(healthy) do
				local hum = p.Character and p.Character:FindFirstChildOfClass("Humanoid")
				if hum then
					hum.WalkSpeed = HEALTHY_SPEED + 4
					notify:FireClient(
						p,
						"⚡ دفعة أدرينالين! سرعة إضافية 4 ثواني",
						"collect"
					)
					task.delay(4, function()
						if hum.Parent and p:GetAttribute("Virus") == "healthy" then
							hum.WalkSpeed = HEALTHY_SPEED
						end
					end)
				end
			end
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
		if #list == 0 then
			workspace:SetAttribute("VirusPhase", "waiting")
			workspace:SetAttribute("VirusCount", 0)
		else
			workspace:SetAttribute("VirusPhase", "countdown")
			workspace:SetAttribute("VirusEnds", workspace:GetServerTimeNow() + COUNTDOWN)
			task.wait(COUNTDOWN)
			list = arenaPlayers()
			if #list >= 2 then
				runRound(list)
				task.wait(5)
			elseif #list == 1 then
				runSoloDroneRound(list[1])
				task.wait(5)
			end
		end
	end
end)

Players.PlayerRemoving:Connect(function(player)
	shieldUntil[player] = nil
	lastZero[player] = nil
end)
