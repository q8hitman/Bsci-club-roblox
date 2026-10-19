local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.LevelConfig)
local Codes = require(script.Parent.Codes)
local Questions = require(script.Parent.Questions)
local Zones = require(ReplicatedStorage.Shared.Zones) -- generated with the map: { {start, finish, ...}, ... }
local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local PassportState = require(script.Parent.PassportState)

-- zone index a level belongs to (levels start+1 .. finish)
local function zoneOfLevel(level)
	for i = #Zones, 1, -1 do
		if level > Zones[i].start then
			return i
		end
	end
	return 1
end

-- GetDataStore throws in an unpublished place (or with Studio API access off). Keep the game
-- playable in that case and simply skip saving.
local storeOk, store = pcall(function()
	return DataStoreService:GetDataStore(Config.SaveKey)
end)
if not storeOk then
	warn("DataStore unavailable (publish the place and enable Studio API access to save progress): " .. tostring(store))
	store = nil
end
local mapFolder = workspace:WaitForChild("Map")

-- Checkpoints live in the static map as parts named Checkpoint_<level>.
local checkpoints = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	local n = inst:IsA("BasePart") and inst.Name:match("^Checkpoint_(%d+)$")
	if n then
		checkpoints[tonumber(n)] = inst
	end
end
assert(checkpoints[0] and checkpoints[Config.Total], "map is missing checkpoints")

-- portal destinations: the club HQ is the lobby (players spawn there), everything else is a portal away
local destinations = {
	HQ = mapFolder:FindFirstChild("HQSpawn", true),
	Campus = mapFolder:FindFirstChild("CampusSpawn", true),
	Cart = mapFolder:FindFirstChild("CartSpawnPoint", true),
	Virus = mapFolder:FindFirstChild("VirusSpawn", true),
	Island = mapFolder:FindFirstChild("IslandSpawn", true),
	Exam = mapFolder:FindFirstChild("ExamSpawn", true),
	Arcade = mapFolder:FindFirstChild("ArcadeSpawn", true),
	Lab = mapFolder:FindFirstChild("LabSpawn", true),
	Quiz = mapFolder:FindFirstChild("QuizSpawn", true),
	Train = mapFolder:FindFirstChild("TrainSpawnPoint", true),
	Puzzle = mapFolder:FindFirstChild("PuzzleSpawn", true), -- v39 puzzle rooms (next to the arcade)
	Show = mapFolder:FindFirstChild("GameShowSpawn", true), -- v40 BSC Game Show studio
}

local notify = Instance.new("RemoteEvent")
notify.Name = "Notify"
notify.Parent = ReplicatedStorage

-- Server-authoritative state. Clients never send stage or coin values.
-- stage   = furthest checkpoint reached (saved)
-- respawn = checkpoint the player is currently playing from (can be lower when replaying a zone)
local state = Profiles.state -- [Player] = see Profiles.blank()

local function withRetry(fn, tries)
	for i = 1, tries do
		local ok, result = pcall(fn)
		if ok then
			return true, result
		end
		warn(("DataStore attempt %d/%d failed: %s"):format(i, tries, tostring(result)))
		task.wait(1.5 * i)
	end
	return false, nil
end

local function applyStage(player, stage, gameplay)
	local s = state[player]
	if not s then
		return
	end
	s.stage = stage
	s.respawn = stage
	player:SetAttribute("Stage", stage) -- replicates to client HUD / gate locks
	if gameplay ~= false then
		Passport.record(player, "checkpoint", stage)
	end
	Profiles.fire("stage", player, stage)
end

local Teleport = require(script.Parent.Teleport)

-- every character move goes through Teleport.to (unseat, ground check, client sync; see Teleport.luau)
local function pivotTo(char, part)
	local player = char and Players:GetPlayerFromCharacter(char)
	if player and part then
		return Teleport.to(player, part)
	end
	return false
end

-- ------------------------------------------------------------------ portals
local portalCooldown = {}

local function canUsePortal(player)
	local now = os.clock()
	if portalCooldown[player] and now - portalCooldown[player] < 2 then
		return false
	end
	portalCooldown[player] = now
	return true
end

local function enterCourse(player, level)
	local s = state[player]
	if not s then
		return
	end
	s.respawn = level
	player:SetAttribute("InCourse", true)
	if pivotTo(player.Character, checkpoints[level]) then
		Passport.record(player, "visit", "Course")
	end
end

local function leaveCourse(player, dest)
	player:SetAttribute("InCourse", false)
	if pivotTo(player.Character, destinations[dest] or destinations.HQ) then
		Passport.record(player, "visit", dest)
	end
end

local function onPortal(player, args)
	if not canUsePortal(player) then
		return
	end
	local s = state[player]
	if not s then
		return
	end
	local kind = args[2]
	if kind == "Course" then
		enterCourse(player, s.stage)
	elseif kind == "Zone" then
		local zone = math.clamp(tonumber(args[3]) or 1, 1, #Zones)
		local startLevel = Zones[zone].start
		if s.stage >= startLevel then
			enterCourse(player, startLevel)
		else
			notify:FireClient(
				player,
				("هذي المنطقة مقفلة 🔒 كمّل لين المرحلة %d"):format(startLevel)
			)
		end
	elseif destinations[kind] then
		leaveCourse(player, kind)
	end
end

-- "back to the island" button (client shows it while InCourse): progress is kept, only the position changes
local leaveEvent = Instance.new("RemoteEvent")
leaveEvent.Name = "LeaveCourse"
leaveEvent.Parent = ReplicatedStorage
leaveEvent.OnServerEvent:Connect(function(player)
	if player:GetAttribute("InCourse") and canUsePortal(player) then
		leaveCourse(player, "Island")
	end
end)

-- v37 world menu (WorldMenu.client): the same moves as the portals, without walking to one. Only these keys are
-- accepted; "Course" continues the parkour from the saved stage (nothing can be skipped).
local TRAVEL = {
	Campus = true,
	HQ = true,
	Island = true,
	Course = true,
	Cart = true,
	Train = true,
	Arcade = true,
	Lab = true,
	Quiz = true,
	Exam = true,
	Puzzle = true,
	Show = true,
}
local travelEvent = Instance.new("RemoteEvent")
travelEvent.Name = "Travel"
travelEvent.Parent = ReplicatedStorage
travelEvent.OnServerEvent:Connect(function(player, kind)
	if typeof(kind) ~= "string" or not TRAVEL[kind] or not state[player] or not player.Character then
		return
	end
	if kind ~= "Course" and not destinations[kind] then
		return
	end
	onPortal(player, { "Portal", kind })
end)

-- ------------------------------------------------------------------ quiz (checkpoint gates + practice stations)
local QUIZ_EVERY = 5
local askEvent = Instance.new("RemoteEvent")
askEvent.Name = "QuizAsk"
askEvent.Parent = ReplicatedStorage
local answerFn = Instance.new("RemoteFunction")
answerFn.Name = "QuizAnswer"
answerFn.Parent = ReplicatedStorage

local pending = {} -- [Player] = { level, bank, correct, token, sentAt }  (level <= 0 means practice)
local quizRng = Random.new()

local function buildQuestion(player, level, bankIndex)
	local bank = Questions[math.clamp(bankIndex, 1, #Questions)]
	local item = bank.items[quizRng:NextInteger(1, #bank.items)]
	local order = { 1, 2, 3 }
	for i = 3, 2, -1 do
		local j = quizRng:NextInteger(1, i)
		order[i], order[j] = order[j], order[i]
	end
	local choices, correct = {}, 1
	for slot, which in ipairs(order) do
		choices[slot] = item[which + 1]
		if which == 1 then
			correct = slot
		end
	end
	local token = tostring(quizRng:NextInteger(1, 2 ^ 30))
	pending[player] = { level = level, bank = bankIndex, correct = correct, token = token, sentAt = os.clock() }
	return { token = token, level = level, zone = bank.name, q = item[1], choices = choices }
end

local function ask(player, level, bankIndex)
	local p = pending[player]
	if p and p.level == level and os.clock() - p.sentAt < 4 then
		return -- already showing; do not spam
	end
	askEvent:FireClient(player, buildQuestion(player, level, bankIndex))
end

answerFn.OnServerInvoke = function(player, token, choice)
	local p = pending[player]
	local s = state[player]
	if not (p and s) or token ~= p.token or typeof(choice) ~= "number" then
		return false, nil
	end
	if choice == p.correct then
		pending[player] = nil
		if p.level > 0 and p.level == s.stage + 1 then
			applyStage(player, p.level)
			s.coins += 5
		elseif p.level <= 0 then
			s.coins += 1 -- practice station
			s.stats.practice = (s.stats.practice or 0) + 1
			Profiles.fire("practice", player, s.stats.practice)
		end
		player:SetAttribute("Coins", s.coins)
		return true, nil
	end
	return false, buildQuestion(player, p.level, p.bank)
end

local stationCooldown = {}

-- ------------------------------------------------------------------ wire map parts
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local args = string.split(inst.Name, "|")
		if args[1] == "Portal" then
			inst.Touched:Connect(function(hit)
				local plr = Players:GetPlayerFromCharacter(hit.Parent)
				if plr then
					onPortal(plr, args)
				end
			end)
		elseif args[1] == "QuizStation" then
			local bankIndex = tonumber(args[2]) or 1
			inst.Touched:Connect(function(hit)
				local plr = Players:GetPlayerFromCharacter(hit.Parent)
				if not plr or not state[plr] then
					return
				end
				local key = plr.UserId .. ":" .. bankIndex
				if stationCooldown[key] and os.clock() - stationCooldown[key] < 6 then
					return
				end
				stationCooldown[key] = os.clock()
				ask(plr, -bankIndex, bankIndex)
			end)
		end
	end
end

-- ------------------------------------------------------------------ persistence
local function save(player)
	local s = state[player]
	if not store or not s or not s.loaded then
		return false -- never overwrite real data after a failed load
	end
	local ok = withRetry(function()
		store:UpdateAsync("u_" .. player.UserId, function(old)
			old = old or {}
			old.stage = math.max(old.stage or 0, s.stage) -- progress only moves forward
			old.coins = s.coins -- coins can now be spent in the shop, so save the balance as is
			old.redeemed = old.redeemed or {}
			for code in pairs(s.redeemed) do
				old.redeemed[code] = true
			end
			-- progression: unions for sets, best (lowest) zone times, current equipment
			for _, key in ipairs({ "found", "owned", "ach" }) do
				old[key] = old[key] or {}
				for id in pairs(s[key]) do
					old[key][id] = true
				end
			end
			old.best = old.best or {}
			for zone, t in pairs(s.best) do
				if not old.best[zone] or t < old.best[zone] then
					old.best[zone] = t
				end
			end
			old.equip = s.equip
			old.stats = old.stats or {}
			old.stats.practice = math.max(old.stats.practice or 0, s.stats.practice or 0)
			old.daily = math.max(old.daily or 0, s.daily or 0)
			old.research = s.research or 0 -- spendable, so the balance is saved as is
			old.upgrades = old.upgrades or {}
			for id in pairs(s.upgrades or {}) do
				old.upgrades[id] = true
			end
			old.batch = s.batch
			old.passport = PassportState.merge(old.passport, s.passport, os.time())
			old.quiz = old.quiz or {}
			for key, n in pairs(s.quiz or {}) do
				old.quiz[key] = math.max(old.quiz[key] or 0, n)
			end
			return old
		end)
	end, 3)
	return ok
end

local function onPlayerAdded(player)
	state[player] = Profiles.blank()
	player:SetAttribute("Total", Config.Total)
	player:SetAttribute("InCourse", false)

	local ok, data = false, nil
	if store then
		ok, data = withRetry(function()
			return store:GetAsync("u_" .. player.UserId)
		end, 3)
	end

	local s = state[player]
	if ok then
		s.loaded = true
		data = data or {}
		s.coins = data.coins or 0
		s.redeemed = data.redeemed or {}
		s.found = data.found or {}
		s.owned = data.owned or {}
		s.ach = data.ach or {}
		s.best = data.best or {}
		s.equip = data.equip or {}
		s.stats = data.stats or { practice = 0 }
		s.daily = data.daily or 0
		s.research = data.research or 0
		s.upgrades = data.upgrades or {}
		s.batch = data.batch
		s.passport = data.passport or {}
		s.quiz = data.quiz or {}
		player:SetAttribute("Coins", s.coins)
		applyStage(player, math.clamp(data.stage or 0, 0, Config.Total), false)
	else
		applyStage(player, 0, false) -- play from start; saving stays disabled this session
		warn("Could not load progress for " .. player.Name .. "; saving disabled")
	end
	player:SetAttribute("Coins", s.coins)
	Profiles.fire("loaded", player)

	local function onCharacter(char)
		local hum = char:WaitForChild("Humanoid", 5)
		if not hum then
			return
		end
		char:WaitForChild("HumanoidRootPart", 5)
		local cur = state[player]
		if cur and player:GetAttribute("InCourse") then
			pivotTo(char, checkpoints[cur.respawn])
		end
		hum.Touched:Connect(function(hit)
			local n = hit.Name:match("^Checkpoint_(%d+)$")
			local level = n and tonumber(n)
			local c = state[player]
			if not (level and c) then
				return
			end
			if level == c.stage + 1 then
				-- Only the very next checkpoint advances progress: no skipping, no re-farming.
				if level % QUIZ_EVERY == 0 then
					ask(player, level, zoneOfLevel(level))
				else
					applyStage(player, level)
				end
			elseif level <= c.stage and level > c.respawn then
				c.respawn = level -- replaying an earlier zone
			end
			if level <= c.stage and player:GetAttribute("InCourse") then
				Passport.record(player, "checkpoint", level)
			end
		end)
	end
	player.CharacterAdded:Connect(onCharacter)
	if player.Character then
		task.spawn(onCharacter, player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, p in ipairs(Players:GetPlayers()) do
	task.spawn(onPlayerAdded, p)
end

-- ------------------------------------------------------------------ codes (announced on Discord)
local redeem = Instance.new("RemoteFunction")
redeem.Name = "RedeemCode"
redeem.Parent = ReplicatedStorage

local lastTry = {}
redeem.OnServerInvoke = function(player, input)
	if typeof(input) ~= "string" or #input > 32 then
		return "invalid"
	end
	local now = os.clock()
	if lastTry[player] and now - lastTry[player] < 2 then
		return "slow"
	end
	lastTry[player] = now

	local s = state[player]
	if not s or not s.loaded then
		return "unavailable"
	end
	local code = (input:gsub("%s", "")):upper()
	local def = Codes[code]
	if not def then
		return "invalid"
	end
	if def.expires and os.time() > def.expires then
		return "expired"
	end
	if s.redeemed[code] then
		return "used"
	end

	s.redeemed[code] = true
	s.coins += def.coins or 0
	if not save(player) then
		s.redeemed[code] = nil
		s.coins -= def.coins or 0
		return "unavailable"
	end
	player:SetAttribute("Coins", s.coins)
	return "ok", def.coins or 0
end

-- ------------------------------------------------------------------ fall recovery
task.spawn(function()
	while true do
		task.wait(0.25)
		for player, s in pairs(state) do
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart")
			local cp = checkpoints[s.respawn]
			-- each zone's floor sits 24 studs under its first checkpoint, so 16 catches every fall
			-- before the player can land and get stuck down there
			if root and cp and player:GetAttribute("InCourse") and root.Position.Y < cp.Position.Y - 16 then
				pivotTo(char, cp)
			end
		end
	end
end)

Players.PlayerRemoving:Connect(function(player)
	save(player)
	state[player] = nil
	lastTry[player] = nil
	pending[player] = nil
	portalCooldown[player] = nil
end)

game:BindToClose(function()
	-- wait for every save to finish (retries included) instead of a fixed 3 s; Roblox allows up to 30 s here
	local pendingSaves = 0
	for _, p in ipairs(Players:GetPlayers()) do
		pendingSaves += 1
		task.spawn(function()
			pcall(save, p)
			pendingSaves -= 1
		end)
	end
	local t0 = os.clock()
	while pendingSaves > 0 and os.clock() - t0 < 25 do
		task.wait(0.2)
	end
end)

task.spawn(function()
	while true do
		task.wait(120)
		for _, p in ipairs(Players:GetPlayers()) do
			task.spawn(save, p)
		end
	end
end)
