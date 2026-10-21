-- محطة الألعاب (Arcade): Chaos Campus rounds for the players inside the arcade.
-- intermission -> random minigame (Minigames/*) + random mutation -> results -> repeat.
-- Mutations are applied per player (attributes read by the client), so the rest of the world is untouched.
-- Client state: workspace attributes ArcadePhase, ArcadeTitle, ArcadeHint, ArcadeMutation, ArcadeEnds, ArcadeAlive.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local Teleport = require(script.Parent.Teleport)
local mapFolder = workspace:WaitForChild("Map")
local lobby = mapFolder:FindFirstChild("ArcadeLobby", true)
local lobbySpawn = mapFolder:FindFirstChild("ArcadeSpawn", true)
local arcadeBoard = mapFolder:FindFirstChild("ArcadeBoard", true)
local boardLabel = arcadeBoard and arcadeBoard:FindFirstChildWhichIsA("TextLabel", true)

local function setBoard(text)
	if boardLabel then
		boardLabel.Text = text
	end
end

local announce = Instance.new("RemoteEvent")
announce.Name = "ArcadeAnnounce"
announce.Parent = ReplicatedStorage
-- v53 results screen (ArcadeResults.client): ranked players, the viewer's own rank and rewards
local resultsEvent = Instance.new("RemoteEvent")
resultsEvent.Name = "ArcadeResults"
resultsEvent.Parent = ReplicatedStorage

local INTERMISSION, RESULTS = 12, 7 -- v53: 7 s so the results screen can be read
local MIN_PLAYERS = RunService:IsStudio() and 1 or 1 -- solo rounds are allowed: the arcade should never feel dead
local MUTATIONS = {
	{ id = "none", ar = "بدون طفرة", weight = 2 },
	{ id = "moon", ar = "🌙 جاذبية القمر", weight = 3 },
	{ id = "speed", ar = "⚡ سرعة الميتوكوندريا", weight = 3 },
	{ id = "giant", ar = "🦖 عمالقة", weight = 2 },
	{ id = "tiny", ar = "🐜 بكتيريا صغيرة", weight = 2 },
	{ id = "night", ar = "🌑 مختبر مظلم", weight = 2 },
}

local games = {}
for _, m in ipairs(script.Parent:WaitForChild("Minigames"):GetChildren()) do
	if m:IsA("ModuleScript") then
		local def = require(m)
		def.arena = mapFolder:FindFirstChild("Arena_" .. def.id, true)
		if def.arena then
			table.insert(games, def)
		end
	end
end

local function inLobby(player)
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if not (root and lobby) then
		return false
	end
	local d = lobby.CFrame:PointToObjectSpace(root.Position)
	local h = lobby.Size / 2
	return math.abs(d.X) < h.X and math.abs(d.Y) < h.Y and math.abs(d.Z) < h.Z
end

local function pickMutation()
	local total = 0
	for _, m in ipairs(MUTATIONS) do
		total += m.weight
	end
	local r = math.random() * total
	for _, m in ipairs(MUTATIONS) do
		r -= m.weight
		if r <= 0 then
			return m
		end
	end
	return MUTATIONS[1]
end

local function applyMutation(mut, players, on)
	for _, p in ipairs(players) do
		p:SetAttribute("Mutation", on and mut.id or nil) -- client: moon gravity / night lighting
		local char = p.Character
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if hum and char.Parent then
			if mut.id == "speed" then
				hum.WalkSpeed = on and 28 or (p:GetAttribute("BaseWalkSpeed") or 16) -- keeps lab upgrades
			elseif mut.id == "giant" or mut.id == "tiny" then
				pcall(function()
					char:ScaleTo(on and (mut.id == "giant" and 1.6 or 0.55) or 1)
				end)
			end
		end
	end
end

local function setPhase(phase, seconds)
	workspace:SetAttribute("ArcadePhase", phase)
	workspace:SetAttribute("ArcadeEnds", workspace:GetServerTimeNow() + (seconds or 0))
end

local function sendToLobby(player)
	if lobbySpawn then
		Teleport.to(player, lobbySpawn, Vector3.new(math.random(-6, 6), 0, math.random(-6, 6)))
	end
end

local lastGame = nil
local lastWinnersText = "بانتظار أول جولة"
-- v30: difficulty tier rises with every round played back to back (1..3) and resets when the arcade empties
local tier = 1
local emptySince = nil -- the tier only resets after the arcade has been empty for a while (not during a respawn)

local function addResearch(p, n)
	local s = p.Parent and Profiles.state[p]
	if s then
		s.research = (s.research or 0) + n
		p:SetAttribute("Research", s.research)
	end
end

local function playRound(players)
	local choices = {}
	for _, g in ipairs(games) do
		if g ~= lastGame or #games == 1 then
			table.insert(choices, g)
		end
	end
	local game_ = choices[math.random(1, #choices)]
	-- Studio-only test hook: workspace attribute ArcadeForce = "<id>" plays that game next (ignored on live servers)
	local force = RunService:IsStudio() and workspace:GetAttribute("ArcadeForce")
	if force then
		for _, g in ipairs(games) do
			if g.id == force then
				game_ = g
			end
		end
	end
	lastGame = game_
	local mut = pickMutation()
	local ctx = { arena = game_.arena, alive = {}, score = {}, outAt = {}, running = false, conns = {}, tier = tier }
	local passportDeparted = {}
	function ctx.connect(c)
		table.insert(ctx.conns, c)
	end
	function ctx.addScore(player, n)
		ctx.score[player] = (ctx.score[player] or 0) + n
		player:SetAttribute("RoundScore", ctx.score[player])
	end
	workspace:SetAttribute("ArcadeTitle", game_.ar)
	workspace:SetAttribute("ArcadeHint", game_.hint)
	workspace:SetAttribute("ArcadeMutation", mut.ar)
	setBoard(
		("🎮 الجولة الحالية: %s\n🧬 الطفرة: %s • المستوى %d\n👑 آخر فوز: %s"):format(
			game_.ar,
			mut.ar,
			tier,
			lastWinnersText
		)
	)

	local spawns = {}
	for _, s in ipairs(game_.arena:GetChildren()) do
		if s.Name == "ArenaSpawn" then
			table.insert(spawns, s)
		end
	end
	for i, p in ipairs(players) do
		local s = spawns[(i - 1) % math.max(#spawns, 1) + 1]
		if p.Character and s then
			Teleport.to(p, s)
			ctx.alive[p] = true
			p:SetAttribute("RoundScore", 0)
			p:SetAttribute("InArcadeRound", true)
		end
	end
	for _, p in ipairs(players) do
		announce:FireClient(p, ("%s • المستوى %d\n%s"):format(game_.ar, tier, mut.ar), "start")
	end
	setPhase("starting", 5) -- v54: 5 s so the one-line rules can actually be read (countdown on the HUD)
	task.wait(5)
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
			local ref = kill or spawns[1]
			local offset = root and ref and (root.Position - ref.Position)
			-- left the arena some other way (portal, admin teleport...): drop out quietly, no teleports or return flag
			local left = offset and Vector3.new(offset.X, 0, offset.Z).Magnitude > 250
			if left then
				passportDeparted[p] = true
				ctx.alive[p] = nil
				p:SetAttribute("Mutation", nil)
				p:SetAttribute("InArcadeRound", nil)
				continue
			end
			local fell = root and kill and root.Position.Y < kill.Position.Y + 3
			if not p.Parent or not hum or hum.Health <= 0 or fell then
				ctx.alive[p] = nil
				ctx.outAt[p] = os.clock() -- v53: elimination order for the results screen
				if p.Parent then
					announce:FireClient(p, "💥 طحت! تفرّج على الباقين", "out")
					p:SetAttribute("Mutation", nil)
					p:SetAttribute("InArcadeRound", nil)
					if fell and hum and hum.Health > 0 then
						sendToLobby(p)
					else
						-- died in the arena (e.g. the enzyme sweeper): respawn next to the arcade, not at the hub
						p:SetAttribute("ArcadeReturn", true)
					end
				end
			else
				count += 1
			end
		end
		workspace:SetAttribute("ArcadeAlive", count)
		if game_.mode == "survive" and (count == 0 or (#players > 1 and count <= 1)) then
			break
		end
		-- v38 co-op: the round ends as soon as the team reaches its goal (or when nobody is left)
		if game_.mode == "coop" and (ctx.teamDone or count == 0) then
			break
		end
	end
	ctx.running = false
	local winners = {}
	if game_.mode == "survive" then
		for p in pairs(ctx.alive) do
			table.insert(winners, p)
		end
	elseif game_.mode == "coop" then
		-- everyone who played wins together when the team goal was met
		if ctx.teamDone then
			for _, p in ipairs(players) do
				if p.Parent then
					table.insert(winners, p)
				end
			end
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
	local names = {}
	for _, p in ipairs(players) do
		local s = p.Parent and Profiles.state[p]
		if s then
			s.coins += 2
			Passport.complete(p, "arcade", {
				departed = passportDeparted[p],
				active = ctx.alive[p] == true,
				present = inLobby(p),
				returning = p:GetAttribute("ArcadeReturn") == true,
			})
			p:SetAttribute("Coins", s.coins)
			addResearch(p, (s.upgrades and s.upgrades.mito) and 2 or 1) -- every round feeds the lab (+1 with mito)
		end
	end
	for _, p in ipairs(winners) do
		local s = p.Parent and Profiles.state[p]
		if s then
			s.coins += 10
			p:SetAttribute("Coins", s.coins)
			addResearch(p, 2 + tier)
			table.insert(names, p.DisplayName)
			if Profiles.award then
				Profiles.award(p, "arcade")
			end
		end
	end
	applyMutation(mut, players, false)
	game_.stop(ctx)
	for _, c in ipairs(ctx.conns) do
		c:Disconnect()
	end
	-- v53: the results card (ArcadeResults.client) replaced the old "winner" announcement toast.
	-- Ranked table. score games: by score; survival: survivors first, then whoever lasted longest; co-op: team
	local isWinner = {}
	for _, p in ipairs(winners) do
		isWinner[p] = true
	end
	local rows = {}
	for _, p in ipairs(players) do
		if p.Parent then
			table.insert(rows, {
				player = p,
				name = p.DisplayName,
				score = ctx.score[p] or 0,
				alive = ctx.alive[p] == true,
				outAt = ctx.outAt[p] or math.huge,
				winner = isWinner[p] == true,
			})
		end
	end
	table.sort(rows, function(a, b)
		if a.winner ~= b.winner then
			return a.winner
		end
		if game_.mode == "survive" then
			return a.outAt > b.outAt
		end
		return a.score > b.score
	end)
	local list = {}
	for i, r in ipairs(rows) do
		list[i] = { name = r.name, score = r.score, alive = r.alive, winner = r.winner }
	end
	for i, r in ipairs(rows) do
		resultsEvent:FireClient(r.player, {
			title = game_.ar,
			mode = game_.mode,
			teamDone = ctx.teamDone == true,
			list = list,
			rank = i,
			coins = 2 + (r.winner and 10 or 0),
			research = (
				(
						Profiles.state[r.player]
						and Profiles.state[r.player].upgrades
						and Profiles.state[r.player].upgrades.mito
					)
					and 2
				or 1
			) + (r.winner and (2 + tier) or 0),
			nextIn = RESULTS + INTERMISSION,
		})
	end
	lastWinnersText = #names > 0 and table.concat(names, "، ") or "لا أحد"
	setBoard(
		("🏆 نهاية الجولة: %s\n👑 الفائز: %s\n⭐ المستوى القادم: %d"):format(
			game_.ar,
			lastWinnersText,
			math.min(tier + 1, 3)
		)
	)
	setPhase("results", RESULTS)
	task.wait(RESULTS)
	for _, p in ipairs(players) do
		if p.Parent then
			p:SetAttribute("RoundScore", nil)
			p:SetAttribute("InArcadeRound", nil)
			-- only survivors are still standing in the arena; players who were knocked out are already in the lobby
			if ctx.alive[p] then
				sendToLobby(p)
			end
		end
	end
end

-- one CharacterAdded connection per player: consume the ArcadeReturn flag on the next spawn
local function onPlayer(player)
	player.CharacterAdded:Connect(function(char)
		if not player:GetAttribute("ArcadeReturn") then
			return
		end
		player:SetAttribute("ArcadeReturn", nil)
		local root = char:WaitForChild("HumanoidRootPart", 5)
		task.wait(0.1) -- let the default spawn placement finish first
		if root and char.Parent and lobbySpawn then
			Teleport.to(player, lobbySpawn, Vector3.new(math.random(-6, 6), 0, math.random(-6, 6)))
		end
	end)
end
Players.PlayerAdded:Connect(onPlayer)
for _, p in ipairs(Players:GetPlayers()) do
	onPlayer(p)
end

task.spawn(function()
	task.wait(3)
	while true do
		local here = {}
		for _, p in ipairs(Players:GetPlayers()) do
			if inLobby(p) then
				table.insert(here, p)
			end
		end
		if #here < MIN_PLAYERS or #games == 0 then
			setPhase("waiting", 0)
			emptySince = emptySince or os.clock()
			if os.clock() - emptySince > 30 then
				tier = 1
			end
			setBoard(
				("🎮 محطة الألعاب (%d ألعاب)\n⭐ المستوى الحالي: %d/3\n👑 آخر فوز: %s"):format(
					#games,
					tier,
					lastWinnersText
				)
			)
			task.wait(1)
		else
			emptySince = nil
			setPhase("intermission", INTERMISSION)
			setBoard(
				("⏳ الجولة تبدأ خلال %d ثانية!\n⭐ المستوى الحالي: %d/3\n👑 آخر فوز: %s"):format(
					INTERMISSION,
					tier,
					lastWinnersText
				)
			)
			task.wait(INTERMISSION)
			here = {}
			for _, p in ipairs(Players:GetPlayers()) do
				if inLobby(p) then
					table.insert(here, p)
				end
			end
			if #here >= MIN_PLAYERS then
				local ok, err = pcall(playRound, here)
				if ok then
					tier = math.min(tier + 1, 3)
				end
				if not ok then
					warn("Arcade round failed: " .. tostring(err))
					for _, p in ipairs(here) do
						if p.Parent then
							p:SetAttribute("Mutation", nil)
							p:SetAttribute("InArcadeRound", nil)
						end
					end
				end
			end
		end
	end
end)
