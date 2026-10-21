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

-- v55 solo practice opponent: a virus particle (capsid + spike proteins) that hunts the lone player.
-- It aims where you are going, telegraphs a red dash, replicates into a second particle halfway through (viruses
-- multiply inside hosts), and bounces off a vaccinated player. Survive the whole round for the full reward.
local SOLO_TIME = 45
local function makeVirusParticle()
	local m = Instance.new("Model")
	m.Name = "BioVirusDrone"
	local core = Instance.new("Part")
	core.Name = "Capsid"
	core.Shape = Enum.PartType.Ball
	core.Size = Vector3.new(4.2, 4.2, 4.2)
	core.Material = Enum.Material.Neon
	core.Color = Color3.fromRGB(110, 255, 80)
	core.Anchored, core.CanCollide, core.CanQuery, core.CanTouch = true, false, false, false
	core.Parent = m
	m.PrimaryPart = core
	local rnd = Random.new(7)
	for i = 1, 14 do
		local a, b = rnd:NextNumber(0, math.pi * 2), rnd:NextNumber(-1.2, 1.2)
		local dir = Vector3.new(math.cos(a) * math.cos(b), math.sin(b), math.sin(a) * math.cos(b))
		local spike = Instance.new("Part")
		spike.Name = "Spike" .. i
		spike.Shape = Enum.PartType.Ball
		spike.Size = Vector3.one * 0.9
		spike.Material = Enum.Material.Neon
		spike.Color = Color3.fromRGB(255, 220, 90)
		spike.Anchored, spike.CanCollide, spike.CanQuery, spike.CanTouch = true, false, false, false
		spike:SetAttribute("Offset", dir * 2.5)
		spike.Parent = m
	end
	local light = Instance.new("PointLight")
	light.Color = core.Color
	light.Range = 14
	light.Parent = core
	m.Parent = workspace
	return m
end

local function placeParticle(m, pos, t)
	local spin = CFrame.Angles(0, t * 2, t * 0.7)
	m.PrimaryPart.CFrame = CFrame.new(pos)
	for _, p in ipairs(m:GetChildren()) do
		local off = p:GetAttribute("Offset")
		if off then
			p.CFrame = CFrame.new(pos + (spin * CFrame.new(off)).Position)
		end
	end
end

local function runSoloDroneRound(player)
	workspace:SetAttribute("VirusPhase", "running")
	workspace:SetAttribute("VirusEnds", workspace:GetServerTimeNow() + SOLO_TIME)
	player:SetAttribute("Virus", "healthy")
	setLook(player, false)
	notify:FireClient(
		player,
		"🤖 تدريب فردي: جزيء فيروس يطاردك! اهرب وجمّع اللقاح 💉",
		"info"
	)
	local y = center.Position.Y + 3.2
	-- spawn on the far side of the arena from the player (a fixed spawn could start right on top of them)
	local start = center.Position + Vector3.new(0, 3.2, -40)
	local proot = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if proot then
		local rel = Vector3.new(proot.Position.X - center.Position.X, 0, proot.Position.Z - center.Position.Z)
		local dir = rel.Magnitude > 1 and rel.Unit or Vector3.zAxis
		start = center.Position - dir * 45 + Vector3.new(0, 3.2, 0)
	end
	local drones = { { model = makeVirusParticle(), pos = start, dash = 0 } }
	spawnVaccine()
	local t0 = os.clock()
	local endsAt = t0 + SOLO_TIME
	local nextVaccine, nextDash, split = t0 + 10, t0 + 9, false
	local caughtAt
	while os.clock() < endsAt do
		local dt = task.wait(0.05)
		local now = os.clock()
		if not (player.Parent and inArena(player)) then
			caughtAt = caughtAt or now
			break
		end
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		if not root then
			caughtAt = now
			break
		end
		local elapsed = now - t0
		-- halfway: the virus replicates
		if not split and elapsed > SOLO_TIME * 0.45 then
			split = true
			table.insert(drones, { model = makeVirusParticle(), pos = drones[1].pos + Vector3.new(6, 0, 0), dash = 0 })
			notify:FireClient(
				player,
				"🧬 الفيروس تضاعف! الفيروسات تتكاثر باستغلال الخلية",
				"wrong"
			)
		end
		local shielded = shieldUntil[player] and now < shieldUntil[player]
		for i, d in ipairs(drones) do
			-- aim where the player will be in ~0.6 s (a straight chase is too easy to circle)
			local vel = root.AssemblyLinearVelocity
			local aim = root.Position + Vector3.new(vel.X, 0, vel.Z) * 0.6
			local to = Vector3.new(aim.X - d.pos.X, 0, aim.Z - d.pos.Z)
			local speed = 12 + elapsed * 0.1 - (i - 1) * 1.5 -- reaches walking speed (16) only near the end; the copy is slower
			if d.dash > now then
				speed *= 1.8
			elseif d.warn and now >= d.warn then
				d.warn = nil
				d.dash = now + 0.6
				d.model.Capsid.Color = Color3.fromRGB(110, 255, 80)
			end
			if to.Magnitude > 0.5 then
				d.pos += to.Unit * math.min(speed * dt, to.Magnitude)
			end
			local here = Vector3.new(d.pos.X, y + math.sin(now * 4 + i) * 0.6, d.pos.Z)
			placeParticle(d.model, here, now)
			local dist = (root.Position - here).Magnitude
			if dist < TOUCH_DIST then
				if shielded then
					-- the vaccine-trained immune system pushes the particle away
					local away = Vector3.new(here.X - root.Position.X, 0, here.Z - root.Position.Z)
					d.pos += (away.Magnitude > 0.1 and away.Unit or Vector3.xAxis) * 18
					d.dash, d.warn = 0, nil
				else
					caughtAt = now
				end
			end
		end
		if caughtAt then
			break
		end
		-- telegraphed dash: the first particle flashes red for 1 s, then lunges (x1.8 for 0.6 s)
		if now > nextDash then
			nextDash = now + math.max(4, 7 - elapsed * 0.06)
			local d = drones[1]
			d.warn = now + 1.0
			d.model.Capsid.Color = Color3.fromRGB(255, 70, 70)
		end
		if now > nextVaccine then
			nextVaccine = now + 10
			spawnVaccine()
		end
	end
	for _, d in ipairs(drones) do
		d.model:Destroy()
	end
	cleanupVaccines()
	table.clear(shieldUntil)
	local lasted = math.floor((caughtAt or os.clock()) - t0)
	if player.Parent then
		local s = Profiles.state[player]
		if not caughtAt then
			if s then
				s.coins += 15
				player:SetAttribute("Coins", s.coins)
			end
			notify:FireClient(player, "💪 نجيت في تدريب المناعة كامل! +15 💰", "ach")
			if Profiles.award then
				Profiles.award(player, "virus_survive")
			end
		else
			local coins = math.floor(lasted / 10) * 2
			if s and coins > 0 then
				s.coins += coins
				player:SetAttribute("Coins", s.coins)
			end
			notify:FireClient(
				player,
				("🤢 مسكك الفيروس بعد %d ثانية%s. جرّب مرة ثانية!"):format(
					lasted,
					coins > 0 and (" (+" .. coins .. " 💰)") or ""
				),
				"wrong"
			)
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
