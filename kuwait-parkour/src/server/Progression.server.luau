-- Progression: achievements (+coins, unlock titles), collectibles (campus cats + specimen cards),
-- the trail shop / title picker, cosmetics on the character, and per-zone time trials.
-- All state lives in Profiles (saved by Main.server). Clients only ask; the server decides.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local P = require(ReplicatedStorage.Shared.Progression)
local Zones = require(ReplicatedStorage.Shared.Zones)

local mapFolder = workspace:WaitForChild("Map")
local notify = ReplicatedStorage:WaitForChild("Notify") -- (text, kind) kinds: info, ach, collect, record, wrong

local shop = Instance.new("RemoteFunction")
shop.Name = "Shop"
shop.Parent = ReplicatedStorage
local event = Instance.new("RemoteEvent") -- client -> server: ride/obby milestones
event.Name = "Milestone"
event.Parent = ReplicatedStorage

local state = Profiles.state

local function count(t)
	local n = 0
	for _ in pairs(t) do
		n += 1
	end
	return n
end

local function setAttributes(player)
	local s = state[player]
	if not s then
		return
	end
	local cats, specs = 0, 0
	for id in pairs(s.found) do
		if P.Cats[id] then
			cats += 1
		elseif P.Specimens[id] then
			specs += 1
		end
	end
	player:SetAttribute("Coins", s.coins)
	player:SetAttribute("Cats", cats)
	player:SetAttribute("Specimens", specs)
	player:SetAttribute("Achievements", count(s.ach))
end

-- ------------------------------------------------------------------ cosmetics on the character
local function titleText(s)
	local a = s.equip.title and s.ach[s.equip.title] and P.achievement(s.equip.title)
	return a and a.title or nil
end

local function applyCosmetics(player)
	local s = state[player]
	local char = player.Character
	local head = char and char:FindFirstChild("Head")
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not (s and head and root) then
		return
	end
	local old = head:FindFirstChild("BSCTitle")
	if old then
		old:Destroy()
	end
	local text = titleText(s)
	if text then
		local bb = Instance.new("BillboardGui")
		bb.Name = "BSCTitle"
		bb.Size = UDim2.fromOffset(200, 26)
		bb.StudsOffset = Vector3.new(0, 2.6, 0)
		bb.MaxDistance = 80
		bb.AlwaysOnTop = false
		local l = Instance.new("TextLabel")
		l.Size = UDim2.fromScale(1, 1)
		l.BackgroundTransparency = 1
		l.TextColor3 = Color3.fromRGB(255, 236, 160)
		l.TextStrokeTransparency = 0.4
		l.TextScaled = true
		l.Font = Enum.Font.GothamBold
		l.Text = text
		l.Parent = bb
		bb.Parent = head
	end
	for _, name in ipairs({ "BSCTrail", "BSCTrailA0", "BSCTrailA1" }) do
		local x = root:FindFirstChild(name)
		if x then
			x:Destroy()
		end
	end
	local def = s.equip.trail and s.owned[s.equip.trail] and P.trail(s.equip.trail)
	if def then
		local a0 = Instance.new("Attachment")
		a0.Name = "BSCTrailA0"
		a0.Position = Vector3.new(0, 0.9, 0)
		a0.Parent = root
		local a1 = Instance.new("Attachment")
		a1.Name = "BSCTrailA1"
		a1.Position = Vector3.new(0, -0.9, 0)
		a1.Parent = root
		local trail = Instance.new("Trail")
		trail.Name = "BSCTrail"
		trail.Attachment0, trail.Attachment1 = a0, a1
		local keys = {}
		for i, c in ipairs(def.colors) do
			table.insert(keys, ColorSequenceKeypoint.new((i - 1) / math.max(#def.colors - 1, 1), c))
		end
		if #keys == 1 then
			table.insert(keys, ColorSequenceKeypoint.new(1, def.colors[1]))
		end
		trail.Color = ColorSequence.new(keys)
		trail.Lifetime = 0.55
		trail.LightEmission = 0.4
		trail.Transparency = NumberSequence.new(0.1, 1)
		trail.FaceCamera = true
		trail.Parent = root
	end
end

-- ------------------------------------------------------------------ achievements
local function award(player, id)
	local s = state[player]
	local a = P.achievement(id)
	if not (s and a) or s.ach[id] then
		return
	end
	s.ach[id] = true
	s.coins += a.coins or 0
	if a.title and not s.equip.title then
		s.equip.title = id -- first title equips itself so players notice the feature
		applyCosmetics(player)
	end
	setAttributes(player)
	notify:FireClient(
		player,
		("🏅 إنجاز جديد: %s  (+%d عملة)%s"):format(
			a.ar,
			a.coins or 0,
			a.title and ("\nلقب جديد: " .. a.title) or ""
		),
		"ach"
	)
end

local function checkCollections(player)
	if (player:GetAttribute("Cats") or 0) >= P.CatCount then
		award(player, "cats")
	end
	if (player:GetAttribute("Specimens") or 0) >= P.SpecimenCount then
		award(player, "specimens")
	end
end

Profiles.on("stage", function(player, stage)
	if stage >= 1 then
		award(player, "first")
	end
	for i, z in ipairs(Zones) do
		if stage >= z.finish then
			award(player, "z" .. i)
		end
	end
	if stage >= 100 then
		award(player, "finish")
	end
end)

Profiles.award = award -- other server scripts (Extras, VirusTag) grant achievements through this

Profiles.on("practice", function(player, total)
	if total >= 10 then
		award(player, "quiz10")
	end
end)

Profiles.on("loaded", function(player)
	setAttributes(player)
	applyCosmetics(player)
	local stage = player:GetAttribute("Stage") or 0
	Profiles.fire("stage", player, stage) -- catch up achievements earned before this system existed
end)

-- ------------------------------------------------------------------ collectibles
local collectCooldown = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local args = string.split(inst.Name, "|")
		if args[1] == "Collect" then
			local kind, id = args[2], args[3]
			inst.Touched:Connect(function(hit)
				local player = Players:GetPlayerFromCharacter(hit.Parent)
				local s = player and state[player]
				if not s or s.found[id] then
					return
				end
				local key = player.UserId .. id
				if collectCooldown[key] and os.clock() - collectCooldown[key] < 2 then
					return
				end
				collectCooldown[key] = os.clock()
				s.found[id] = true
				local text
				if kind == "cat" and P.Cats[id] then
					s.coins += 10
					text = ("🐱 لقيت «%s»!  (+10)\n%s"):format(P.Cats[id].name, P.Cats[id].text)
				elseif kind == "spec" and P.Specimens[id] then
					s.coins += 20
					text = ("🔬 %s  (+20)\n%s"):format(P.Specimens[id].ar, P.Specimens[id].text)
				elseif kind == "golden" then
					notify:FireClient(
						player,
						"🗝️ القطوة الذهبية! لقيت أسرار كلية العلوم 🤫",
						"collect",
						id
					)
					award(player, "golden")
					Passport.refresh(player)
					return
				else
					return
				end
				setAttributes(player)
				Passport.refresh(player)
				notify:FireClient(player, text, "collect", id)
				checkCollections(player)
			end)
		end
	end
end

-- ------------------------------------------------------------------ time trials (one zone, start to finish, no leaving)
-- checkpoint names: Checkpoint_<level>. A run starts on the zone's first checkpoint (its `start`)
-- and ends on its last (`finish`) if every checkpoint in between was touched in order.
local runs = {} -- [Player] = { zone, t0, next }

local function zoneStartingAt(level)
	for i, z in ipairs(Zones) do
		if z.start == level then
			return i, z
		end
	end
	return nil
end

local function onCheckpoint(player, level)
	local run = runs[player]
	local zi = zoneStartingAt(level)
	if zi then
		runs[player] = { zone = zi, t0 = os.clock(), next = level + 1, finish = Zones[zi].finish }
		player:SetAttribute("TrialZone", zi)
		player:SetAttribute("TrialStart", workspace:GetServerTimeNow())
		run = runs[player]
	end
	if not run or level ~= run.next then
		return
	end
	run.next += 1
	if level == run.finish then
		local t = os.clock() - run.t0
		runs[player] = nil
		player:SetAttribute("TrialZone", 0)
		local s = state[player]
		if not s then
			return
		end
		local key = tostring(run.zone)
		local prev = s.best[key]
		Profiles.fire("trial", player, run.zone, t)
		local timeText = ("%d:%02d"):format(math.floor(t / 60), math.floor(t % 60))
		if not prev or t < prev then
			s.best[key] = t
			notify:FireClient(
				player,
				("⏱️ رقم قياسي شخصي بـ %s: %s"):format(Zones[run.zone].nameAr, timeText),
				"record"
			)
		else
			notify:FireClient(
				player,
				("⏱️ وقتك %s (أفضل وقت %d:%02d)"):format(
					timeText,
					math.floor(prev / 60),
					math.floor(prev % 60)
				),
				"info"
			)
		end
		if t <= P.SpeedSeconds then
			award(player, "speed")
		end
	end
end

local function bindCharacter(player, char)
	local hum = char:WaitForChild("Humanoid", 5)
	if not hum then
		return
	end
	hum.Touched:Connect(function(hit)
		local n = hit.Name:match("^Checkpoint_(%d+)$")
		if n then
			onCheckpoint(player, tonumber(n))
		end
	end)
	task.defer(applyCosmetics, player)
end

local function onPlayer(player)
	player.CharacterAdded:Connect(function(char)
		bindCharacter(player, char)
	end)
	if player.Character then
		task.spawn(bindCharacter, player, player.Character)
	end
	player:GetAttributeChangedSignal("InCourse"):Connect(function()
		if not player:GetAttribute("InCourse") then
			runs[player] = nil
			player:SetAttribute("TrialZone", 0)
		end
	end)
end
Players.PlayerAdded:Connect(onPlayer)
for _, p in ipairs(Players:GetPlayers()) do
	task.spawn(onPlayer, p)
end
Players.PlayerRemoving:Connect(function(player)
	runs[player] = nil
end)

-- ------------------------------------------------------------------ shop + profile snapshot
local function snapshot(player)
	local s = state[player]
	if not s then
		return nil
	end
	local passport = Passport.refresh(player)
	return {
		coins = s.coins,
		owned = s.owned,
		equip = s.equip,
		ach = s.ach,
		found = s.found,
		best = s.best,
		passport = passport,
		batch = s.batch,
	}
end

local lastShop = {}
shop.OnServerInvoke = function(player, action, id)
	local s = state[player]
	if not s or typeof(action) ~= "string" then
		return nil
	end
	local now = os.clock()
	if action ~= "get" then
		if lastShop[player] and now - lastShop[player] < 0.3 then
			return snapshot(player)
		end
		lastShop[player] = now
	end
	if action == "week" then
		Passport.claim(player, id)
	elseif action == "buy" and typeof(id) == "string" then
		local t = P.trail(id)
		if t and not s.owned[id] and s.coins >= t.price then
			s.coins -= t.price
			s.owned[id] = true
			s.equip.trail = id
			setAttributes(player)
			applyCosmetics(player)
			notify:FireClient(player, "✨ اشتريت " .. t.ar, "purchase")
		elseif t and s.coins < t.price then
			notify:FireClient(player, "تحتاج عملات أكثر 💰", "wrong")
		end
	elseif action == "trail" then
		if id == nil or (typeof(id) == "string" and s.owned[id]) then
			s.equip.trail = id
			applyCosmetics(player)
		end
	elseif action == "title" then
		if id == nil or (typeof(id) == "string" and s.ach[id] and P.achievement(id) and P.achievement(id).title) then
			s.equip.title = id
			applyCosmetics(player)
		end
	end
	return snapshot(player)
end

-- ------------------------------------------------------------------ milestones reported by clients
-- Only low-value achievements are accepted this way, and only with a plausibility check.
local rideStart = {}
event.OnServerEvent:Connect(function(player, what)
	if what == "cartStart" or what == "trainStart" then
		rideStart[player] = { what = what, t = os.clock() }
	elseif what == "cartFinish" then
		local r = rideStart[player]
		if r and r.what == "cartStart" and os.clock() - r.t > 60 then
			award(player, "cart")
			Passport.record(player, "train", "cart")
		end
		rideStart[player] = nil
	elseif what == "trainFinish" then
		local r = rideStart[player]
		if r and r.what == "trainStart" and os.clock() - r.t > 45 then
			award(player, "train")
			Passport.record(player, "train", "cell")
		end
		rideStart[player] = nil
	elseif what == "summit" then
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		local top = mapFolder:FindFirstChild("ObbyTop", true)
		if root and top and (root.Position - top.Position).Magnitude < 14 then
			award(player, "summit")
		end
	end
end)
Players.PlayerRemoving:Connect(function(player)
	rideStart[player] = nil
	lastShop[player] = nil
end)
