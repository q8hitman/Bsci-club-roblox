-- Reasons to come back and share:
--   * daily challenge: one zone per (UTC) day; finishing its time trial pays a bonus once a day
--   * global best times per zone (OrderedDataStore; works once the place is published)
--   * graduation stage: cap + photo moment + achievement
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")

local Profiles = require(script.Parent.Profiles)
local Zones = require(ReplicatedStorage.Shared.Zones)
local notify = ReplicatedStorage:WaitForChild("Notify")
local mapFolder = workspace:WaitForChild("Map")

local DAILY_BONUS = 40

local function today()
	return math.floor(os.time() / 86400)
end
local function todaysZone()
	return today() % #Zones + 1
end

-- ------------------------------------------------------------------ global best times
local boards = {}
for i = 1, #Zones do
	local ok, store = pcall(function()
		return DataStoreService:GetOrderedDataStore("BestTime_Zone" .. i)
	end)
	boards[i] = ok and store or nil
end
local topCache = {} -- zone -> { {name, seconds}, ... }

local function refreshTop(zone)
	local store = boards[zone]
	if not store then
		return
	end
	local ok, pages = pcall(function()
		return store:GetSortedAsync(true, 5) -- ascending: fastest first
	end)
	if not ok then
		return
	end
	local rows = {}
	for _, entry in ipairs(pages:GetCurrentPage()) do
		local name = "؟"
		local okName, n = pcall(function()
			return Players:GetNameFromUserIdAsync(tonumber(entry.key))
		end)
		if okName then
			name = n
		end
		table.insert(rows, { name = name, seconds = entry.value / 100 })
	end
	topCache[zone] = rows
end

local function submitTime(player, zone, seconds)
	local store = boards[zone]
	if not store then
		return
	end
	local centi = math.floor(seconds * 100)
	pcall(function()
		store:UpdateAsync(tostring(player.UserId), function(old)
			if old and old <= centi then
				return nil -- keep the faster time
			end
			return centi
		end)
	end)
	task.defer(refreshTop, zone)
end

-- ------------------------------------------------------------------ daily board
local board = mapFolder:FindFirstChild("DailyBoard", true)
local boardLabel = board and board:FindFirstChild("Label") and board.Label:FindFirstChild("T")

local function fmt(t)
	return ("%d:%05.2f"):format(math.floor(t / 60), t % 60)
end

local function renderBoard()
	if not boardLabel then
		return
	end
	local zi = todaysZone()
	local lines = {
		("📅 تحدي اليوم: %s"):format(Zones[zi].nameAr),
		("خلّصها كاملة بدون ما تطلع = +%d 💰"):format(DAILY_BONUS),
		"🏁 أسرع الأوقات:",
	}
	local rows = topCache[zi]
	if rows and #rows > 0 then
		for i, r in ipairs(rows) do
			table.insert(lines, ("%d. %s  %s"):format(i, r.name, fmt(r.seconds)))
		end
	else
		table.insert(
			lines,
			boards[zi] and "كن أول واحد!" or "(الترتيب يشتغل بعد نشر اللعبة)"
		)
	end
	boardLabel.Text = table.concat(lines, "\n")
end

task.spawn(function()
	while true do
		refreshTop(todaysZone())
		renderBoard()
		task.wait(60)
	end
end)

Profiles.on("trial", function(player, zone, seconds)
	local s = Profiles.state[player]
	if not s then
		return
	end
	submitTime(player, zone, seconds)
	if zone == todaysZone() and (s.daily or 0) < today() then
		s.daily = today()
		s.coins += DAILY_BONUS
		player:SetAttribute("Coins", s.coins)
		notify:FireClient(player, ("📅 خلّصت تحدي اليوم! +%d 💰"):format(DAILY_BONUS), "ach")
		if Profiles.award then
			Profiles.award(player, "daily")
		end
	end
	task.delay(2, renderBoard)
end)

-- ------------------------------------------------------------------ graduation stage
local gradEvent = Instance.new("RemoteEvent")
gradEvent.Name = "Graduate"
gradEvent.Parent = ReplicatedStorage

local function giveCap(char)
	local head = char and char:FindFirstChild("Head")
	if not head or head:FindFirstChild("GradCap") then
		return
	end
	local cap = Instance.new("Model")
	cap.Name = "GradCap"
	local capBoard = Instance.new("Part")
	capBoard.Name = "CapBoard"
	capBoard.Size = Vector3.new(2.6, 0.2, 2.6)
	capBoard.Color = Color3.fromRGB(24, 24, 28)
	local crown = Instance.new("Part")
	crown.Name = "CapCrown"
	crown.Size = Vector3.new(1.5, 0.7, 1.5)
	crown.Color = Color3.fromRGB(24, 24, 28)
	local tassel = Instance.new("Part")
	tassel.Name = "CapTassel"
	tassel.Size = Vector3.new(0.15, 1, 0.15)
	tassel.Color = Color3.fromRGB(230, 190, 70)
	tassel.Material = Enum.Material.Neon
	for _, p in ipairs({ capBoard, crown, tassel }) do
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Massless = true
		p.Parent = cap
	end
	local top = head.CFrame * CFrame.new(0, head.Size.Y / 2, 0)
	crown.CFrame = top * CFrame.new(0, 0.2, 0)
	capBoard.CFrame = top * CFrame.new(0, 0.6, 0) * CFrame.Angles(0, math.rad(45), 0)
	tassel.CFrame = top * CFrame.new(1.1, 0.2, 0)
	for _, p in ipairs({ capBoard, crown, tassel }) do
		local w = Instance.new("WeldConstraint")
		w.Part0, w.Part1 = head, p
		w.Parent = p
	end
	cap.Parent = head
end

local gradCooldown = {}
local pad = mapFolder:FindFirstChild("GradPad", true)
if pad then
	pad.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if not player then
			return
		end
		if gradCooldown[player] and os.clock() - gradCooldown[player] < 12 then
			return
		end
		gradCooldown[player] = os.clock()
		giveCap(player.Character)
		gradEvent:FireClient(player)
		if Profiles.award then
			Profiles.award(player, "grad")
		end
	end)
end
Players.PlayerRemoving:Connect(function(player)
	gradCooldown[player] = nil
end)
