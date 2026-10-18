-- Chaos Campus round loop: intermission -> random minigame + random mutation -> results -> repeat.
-- State for clients is published as workspace attributes: Phase, GameTitle, GameHint, Mutation, EndsAt, Alive.
-- Points/Wins are leaderstats (and saved with DataStore when the place is published).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")
local Lighting = game:GetService("Lighting")

local Config = require(ReplicatedStorage.Shared.Config)
local mapFolder = workspace:WaitForChild("Map")
local lobbySpawn = mapFolder:FindFirstChild("LobbySpawn", true)

local announce = Instance.new("RemoteEvent")
announce.Name = "Announce" -- (text, kind) big centre messages
announce.Parent = ReplicatedStorage

-- ------------------------------------------------------------------ minigames
local games = {}
for _, m in ipairs(script.Parent:WaitForChild("Minigames"):GetChildren()) do
	if m:IsA("ModuleScript") then
		local def = require(m)
		def.arena = mapFolder:FindFirstChild("Arena_" .. def.id)
		if def.arena then
			table.insert(games, def)
		else
			warn("ChaosCampus: no arena for minigame " .. def.id)
		end
	end
end

-- ------------------------------------------------------------------ saving (only when published)
local okStore, store = pcall(function()
	return DataStoreService:GetDataStore("ChaosCampus_v1")
end)
if not okStore then
	store = nil
end
local loaded = {}

local function stats(player)
	return player:FindFirstChild("leaderstats")
end

Players.PlayerAdded:Connect(function(player)
	local ls = Instance.new("Folder")
	ls.Name = "leaderstats"
	local points = Instance.new("IntValue")
	points.Name = "Points"
	points.Parent = ls
	local wins = Instance.new("IntValue")
	wins.Name = "Wins"
	wins.Parent = ls
	ls.Parent = player
	if store then
		local ok, data = pcall(function()
			return store:GetAsync("u_" .. player.UserId)
		end)
		if ok then
			loaded[player] = true
			points.Value = data and data.points or 0
			wins.Value = data and data.wins or 0
		end
	end
end)

local function save(player)
	local ls = stats(player)
	if not (store and loaded[player] and ls) then
		return
	end
	pcall(function()
		store:UpdateAsync("u_" .. player.UserId, function(old)
			old = old or {}
			old.points = math.max(old.points or 0, ls.Points.Value)
			old.wins = math.max(old.wins or 0, ls.Wins.Value)
			return old
		end)
	end)
end
Players.PlayerRemoving:Connect(function(player)
	save(player)
	loaded[player] = nil
end)
game:BindToClose(function()
	for _, p in ipairs(Players:GetPlayers()) do
		save(p)
	end
end)

-- ------------------------------------------------------------------ mutations
local function pickMutation()
	local total = 0
	for _, m in ipairs(Config.Mutations) do
		total += m.weight
	end
	local r = math.random() * total
	for _, m in ipairs(Config.Mutations) do
		r -= m.weight
		if r <= 0 then
			return m
		end
	end
	return Config.Mutations[1]
end

local function applyMutation(mut, players, on)
	if mut.id == "moon" then
		workspace.Gravity = on and 60 or 196.2
	elseif mut.id == "night" then
		Lighting.ClockTime = on and 0.5 or 14.5
	end
	for _, p in ipairs(players) do
		local char = p.Character
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if hum then
			if mut.id == "speed" then
				hum.WalkSpeed = on and 28 or 16
			elseif (mut.id == "giant" or mut.id == "tiny") and char.Parent then
				pcall(function()
					char:ScaleTo(on and (mut.id == "giant" and 1.6 or 0.55) or 1)
				end)
			elseif mut.id == "night" then
				local root = char:FindFirstChild("HumanoidRootPart")
				if root and on then
					local l = Instance.new("PointLight")
					l.Name = "NightLight"
					l.Range = 18
					l.Brightness = 2
					l.Parent = root
				elseif root and root:FindFirstChild("NightLight") then
					root.NightLight:Destroy()
				end
			end
		end
	end
end

-- ------------------------------------------------------------------ helpers
local function setPhase(phase, seconds)
	workspace:SetAttribute("Phase", phase)
	workspace:SetAttribute("EndsAt", workspace:GetServerTimeNow() + (seconds or 0))
end

local function sendToLobby(player)
	local char = player.Character
	if char and lobbySpawn then
		char:PivotTo(lobbySpawn.CFrame + Vector3.new(math.random(-6, 6), 4, math.random(-6, 6)))
	end
end

local function updateScoreboard()
	local board = mapFolder:FindFirstChild("ScoreBoard", true)
	local label = board and board:FindFirstChild("Label") and board.Label:FindFirstChild("T")
	if not label then
		return
	end
	local rows = {}
	for _, p in ipairs(Players:GetPlayers()) do
		local ls = stats(p)
		if ls then
			table.insert(rows, { p.DisplayName, ls.Points.Value, ls.Wins.Value })
		end
	end
	table.sort(rows, function(a, b)
		return a[2] > b[2]
	end)
	local lines = { "🏆 النقاط | Points" }
	for i = 1, math.min(#rows, 8) do
		table.insert(lines, ("%d. %s — %d  (👑 %d)"):format(i, rows[i][1], rows[i][2], rows[i][3]))
	end
	label.Text = table.concat(lines, "\n")
end

-- ------------------------------------------------------------------ one round
local lastGame = nil

local function playRound(players)
	local choices = {}
	for _, g in ipairs(games) do
		if g ~= lastGame or #games == 1 then
			table.insert(choices, g)
		end
	end
	local game_ = choices[math.random(1, #choices)]
	lastGame = game_
	local mut = pickMutation()

	local ctx = {
		arena = game_.arena,
		alive = {},
		score = {},
		running = false,
		conns = {},
	}
	function ctx.connect(c)
		table.insert(ctx.conns, c)
	end
	function ctx.addScore(player, n)
		ctx.score[player] = (ctx.score[player] or 0) + n
		player:SetAttribute("RoundScore", ctx.score[player])
	end

	workspace:SetAttribute("GameTitle", game_.ar)
	workspace:SetAttribute("GameHint", game_.hint)
	workspace:SetAttribute("Mutation", mut.ar)

	-- teleport in
	local spawns = {}
	for _, s in ipairs(game_.arena:GetChildren()) do
		if s.Name == "ArenaSpawn" then
			table.insert(spawns, s)
		end
	end
	for i, p in ipairs(players) do
		local s = spawns[(i - 1) % math.max(#spawns, 1) + 1]
		if p.Character and s then
			p.Character:PivotTo(s.CFrame + Vector3.new(0, 4, 0))
			ctx.alive[p] = true
			p:SetAttribute("RoundScore", 0)
		end
	end
	announce:FireAllClients(("%s\n%s"):format(game_.ar, mut.ar), "start")
	setPhase("starting", 3)
	task.wait(3)

	applyMutation(mut, players, true)
	ctx.running = true
	game_.start(ctx)
	setPhase("running", game_.duration)
	local endsAt = os.clock() + game_.duration
	local kill = game_.arena:FindFirstChild("KillFloor|" .. game_.id)

	while os.clock() < endsAt do
		task.wait(0.2)
		local count = 0
		for p in pairs(ctx.alive) do
			local char = p.Character
			local hum = char and char:FindFirstChildOfClass("Humanoid")
			local root = char and char:FindFirstChild("HumanoidRootPart")
			local fell = root and kill and root.Position.Y < kill.Position.Y + 3
			if not p.Parent or not hum or hum.Health <= 0 or fell then
				ctx.alive[p] = nil
				if p.Parent then
					announce:FireClient(p, "💥 طحت! تفرّج على الباقين", "out")
					if fell then
						sendToLobby(p)
					end
				end
			else
				count += 1
			end
		end
		workspace:SetAttribute("Alive", count)
		if game_.mode == "survive" and (count == 0 or (#players > 1 and count <= 1)) then
			break
		end
	end
	ctx.running = false

	-- winners
	local winners = {}
	if game_.mode == "survive" then
		for p in pairs(ctx.alive) do
			table.insert(winners, p)
		end
	else
		local best = 0
		for p, s in pairs(ctx.score) do
			if s > best then
				best, winners = s, { p }
			elseif s == best and s > 0 then
				table.insert(winners, p)
			end
		end
	end
	for _, p in ipairs(players) do
		local ls = p.Parent and stats(p)
		if ls then
			ls.Points.Value += Config.PlayPoints
		end
	end
	local names = {}
	for _, p in ipairs(winners) do
		local ls = p.Parent and stats(p)
		if ls then
			ls.Points.Value += Config.WinPoints
			ls.Wins.Value += 1
			table.insert(names, p.DisplayName)
		end
	end
	applyMutation(mut, players, false)
	game_.stop(ctx)
	for _, c in ipairs(ctx.conns) do
		c:Disconnect()
	end
	announce:FireAllClients(#names > 0 and ("👑 الفائز: " .. table.concat(names, "، ")) or "ما فاز أحد هالمرة 😅", "result")
	setPhase("results", Config.ResultsTime)
	task.wait(Config.ResultsTime)
	for _, p in ipairs(players) do
		if p.Parent then
			p:SetAttribute("RoundScore", nil)
			sendToLobby(p)
		end
	end
	updateScoreboard()
end

-- ------------------------------------------------------------------ main loop
task.spawn(function()
	task.wait(3)
	while true do
		updateScoreboard()
		local players = Players:GetPlayers()
		if #players < Config.MinPlayers or #games == 0 then
			setPhase("waiting", 0)
			task.wait(2)
		else
			setPhase("intermission", Config.Intermission)
			task.wait(Config.Intermission)
			players = {}
			for _, p in ipairs(Players:GetPlayers()) do
				if p.Character and p.Character:FindFirstChildOfClass("Humanoid") then
					table.insert(players, p)
				end
			end
			if #players >= Config.MinPlayers then
				local ok, err = pcall(playRound, players)
				if not ok then
					warn("ChaosCampus round failed: " .. tostring(err))
					workspace.Gravity = 196.2
					Lighting.ClockTime = 14.5
				end
			end
		end
	end
end)
