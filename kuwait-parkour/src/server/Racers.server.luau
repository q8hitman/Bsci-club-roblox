-- Authoritative fixed-step racing. Only input intent is accepted; positions/laps/results are never supplied by clients.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local Http = game:GetService("HttpService")
local D = require(RS.Shared.RacerData)
local M = require(RS.Shared.RacerMath)
local Passport = require(script.Parent.PassportService)
local Profiles = require(script.Parent.Profiles)
local Teleport = require(script.Parent.Teleport)
local world = workspace:WaitForChild("Map"):WaitForChild("Racers47")
local request = Instance.new("RemoteFunction")
request.Name = "RaceRequest"
request.Parent = RS
local input = Instance.new("RemoteEvent")
input.Name = "RaceInput"
input.Parent = RS
local event = Instance.new("RemoteEvent")
event.Name = "RaceState"
event.Parent = RS
local sessions, rooms, rate = {}, {}, {}
local function root(p)
	return p.Character and p.Character:FindFirstChild("HumanoidRootPart")
end
local function healthy(p)
	local h = p.Character and p.Character:FindFirstChildOfClass("Humanoid")
	return h and h.Health > 0 and root(p)
end
local function near(p, part, r)
	local v = root(p)
	return v and (v.Position - part.Position).Magnitude < r
end
local function release(p)
	local r = root(p)
	if r then
		r.Anchored = false
	end
	p:SetAttribute("InMicroRace", nil)
end
local function leave(p, returnToArcade)
	local s = sessions[p]
	sessions[p] = nil
	if s and s.room and s.car then
		s.car.departed = true
		s.car.input = {}
	end
	release(p)
	if p.Parent then
		event:FireClient(p, { kind = "close" })
		if returnToArcade and healthy(p) then
			Teleport.to(p, workspace.Map:FindFirstChild("ArcadeSpawn", true))
		end
	end
end
local function enter(p)
	if not healthy(p) or p:GetAttribute("InArcadeRound") then
		return { error = "انتظر نهاية جولة الأركيد أولًا" }
	end
	if not near(p, world.Entry.RaceEntrance, 20) and not near(p, world.Lobby.RaceConsole, 55) then
		return { error = "اقترب من بوابة السباق" }
	end
	leave(p, false)
	Teleport.to(p, world.Lobby.RaceLobbySpawn)
	sessions[p] = { character = p.Character, revision = p:GetAttribute("TeleportRevision"), mode = "menu" }
	p:SetAttribute("InMicroRace", true)
	event:FireClient(p, { kind = "menu" })
	return { ok = true }
end
local function sorted(room)
	local list = {}
	for _, c in ipairs(room.cars) do
		if not c.departed then
			table.insert(list, c)
		end
	end
	table.sort(list, function(a, b)
		if a.finishOrder or b.finishOrder then
			if a.finishOrder and b.finishOrder then
				return a.finishOrder < b.finishOrder
			end
			return a.finishOrder ~= nil
		end
		local pa, pb = M.progress(a.state, room.track), M.progress(b.state, room.track)
		if pa == pb then
			return a.id < b.id
		end
		return pa > pb
	end)
	return list
end
local function snapshot(room, kind)
	local cars = {}
	for rank, c in ipairs(sorted(room)) do
		local s = c.state
		table.insert(cars, {
			id = c.id,
			name = c.name,
			bot = c.bot,
			x = s.x,
			z = s.z,
			heading = s.heading,
			speed = s.speed,
			lap = math.min(s.lap, 3),
			gate = s.gate,
			rank = rank,
			finished = s.done,
			finishTime = c.finishTime,
			shield = s.shieldUntil > s.time,
			boost = s.boostUntil > s.time,
			boostReady = math.max(0, s.boostReadyAt - s.time),
		})
	end
	return {
		kind = kind or "state",
		raceId = room.id,
		track = room.track.id,
		phase = room.phase,
		cars = cars,
		elapsed = room.started and workspace:GetServerTimeNow() - room.started or 0,
		countdown = math.max(0, room.startsAt - workspace:GetServerTimeNow()),
		remaining = room.started and math.max(0, D.Duration - (workspace:GetServerTimeNow() - room.started))
			or D.Duration,
	}
end
local function send(room, kind)
	local data = snapshot(room, kind)
	for p, s in pairs(sessions) do
		if s.room == room and p.Parent then
			local personal = table.clone(data)
			personal.you = s.car.id
			event:FireClient(p, personal)
		end
	end
end
local function grid(track, i)
	local s = M.start(track, (i % 2 == 1 and -1 or 1) * 4)
	local back = math.floor((i - 1) / 2) * 9
	s.x -= math.sin(s.heading) * back
	s.z -= math.cos(s.heading) * back
	return s
end
local function compactQueue(room)
	local active = {}
	for _, car in ipairs(room.cars) do
		if not car.departed then
			table.insert(active, car)
			car.state = grid(room.track, #active)
		end
	end
	room.cars = active
end
local function join(p, id)
	local s = sessions[p]
	local track = D.get(id)
	if not s or not track or not healthy(p) then
		return { error = "افتح بوابة السباق من جديد" }
	end
	if s.room and s.room.phase ~= "results" then
		return { error = "أنت داخل سباق؛ اخرج أولًا" }
	end
	local room = rooms[id]
	if room and room.phase == "running" then
		return {
			error = "الحلبة مشغولة؛ جرّب الحلبة الثانية أو انتظر النتيجة",
		}
	end
	if not room or room.phase == "results" then
		room = {
			id = Http:GenerateGUID(false),
			track = track,
			cars = {},
			phase = "queue",
			startsAt = workspace:GetServerTimeNow() + 5,
			finishCount = 0,
		}
		rooms[id] = room
	end
	compactQueue(room)
	if #room.cars >= D.MaxPlayers then
		return { error = "السباق ممتلئ" }
	end
	local car = {
		id = tostring(p.UserId),
		name = p.DisplayName,
		player = p,
		bot = false,
		state = grid(track, #room.cars + 1),
		input = {},
		lastPacket = os.clock(),
		seq = 0,
	}
	table.insert(room.cars, car)
	s.room, s.car, s.mode = room, car, "race"
	root(p).Anchored = true
	send(room)
	return { ok = true, raceId = room.id }
end
request.OnServerInvoke = function(p, action, arg)
	if type(action) ~= "string" or not Profiles.state[p] then
		return { error = "طلب غير صالح" }
	end
	local now = os.clock()
	if rate[p] and now - rate[p] < 0.15 then
		return { error = "تمهّل ثم أعد المحاولة" }
	end
	rate[p] = now
	if action == "enter" then
		return enter(p)
	end
	if action == "leave" then
		leave(p, true)
		return { ok = true }
	end
	local s = sessions[p]
	if not s or s.character ~= p.Character or s.revision ~= p:GetAttribute("TeleportRevision") or not healthy(p) then
		leave(p, false)
		return { error = "انتهت جلسة السباق" }
	end
	if action == "join" and type(arg) == "string" then
		return join(p, arg)
	end
	if action == "menu" and (not s.room or s.room.phase == "results") then
		if s.car then
			s.car.departed = true
		end
		s.room, s.car, s.mode = nil, nil, "menu"
		release(p)
		p:SetAttribute("InMicroRace", true)
		event:FireClient(p, { kind = "menu" })
		return { ok = true }
	end
	if action == "recover" and s.room and s.room.phase == "running" and not s.car.state.done then
		if now - (s.recoveredAt or -10) < 2 then
			return { error = "الاستعادة متاحة كل ثانيتين" }
		end
		s.recoveredAt = now
		M.recover(s.car.state, s.room.track)
		s.car.input = {}
		return { ok = true }
	end
	return { error = "هذا الطلب غير متاح" }
end
input.OnServerEvent:Connect(function(p, raceId, seq, intent)
	local s = sessions[p]
	if not s or not s.car or not s.room or s.room.id ~= raceId or s.room.phase ~= "running" or s.car.state.done then
		return
	end
	if type(seq) ~= "number" or seq ~= seq or seq % 1 ~= 0 or seq <= s.car.seq or seq > 1e9 then
		return
	end
	local now = os.clock()
	if now - s.car.lastPacket < 0.035 then
		return
	end
	s.car.seq, s.car.lastPacket = seq, now
	s.car.input = M.input(intent)
end)
local function prompt(part, name, text, fn)
	local p = Instance.new("ProximityPrompt")
	p.Name = name
	p.ActionText = text
	p.ObjectText = "Micro Racers"
	p.MaxActivationDistance = 12
	p.RequiresLineOfSight = false
	p.Parent = part
	p.Triggered:Connect(fn)
end
prompt(world.Entry.RaceEntrance, "RaceEnter", "ادخل السباق", function(p)
	local result = enter(p)
	if result.error then
		event:FireClient(p, { kind = "error", message = result.error })
	end
end)
prompt(world.Lobby.RaceConsole, "RaceChoose", "اختر الحلبة", function(p)
	if sessions[p] and not sessions[p].room then
		event:FireClient(p, { kind = "menu" })
	end
end)
prompt(world.Lobby.RaceExit, "RaceReturn", "ارجع للأركيد", function(p)
	if sessions[p] then
		leave(p, true)
	end
end)
Players.PlayerRemoving:Connect(function(p)
	leave(p, false)
	rate[p] = nil
end)
local accumulated, broadcast = 0, 0
Run.Heartbeat:Connect(function(dt)
	accumulated = math.min(0.3, accumulated + dt)
	broadcast += dt
	for p, s in pairs(sessions) do
		if
			not p.Parent
			or s.character ~= p.Character
			or not healthy(p)
			or s.revision ~= p:GetAttribute("TeleportRevision")
			or not near(p, world.Lobby.RaceLobbySpawn, 90)
		then
			leave(p, false)
		end
	end
	for _, room in pairs(rooms) do
		local humans = 0
		for _, c in ipairs(room.cars) do
			if not c.bot and not c.departed then
				humans += 1
			end
		end
		if humans == 0 then
			rooms[room.track.id] = nil
			continue
		end
		if room.phase == "queue" and workspace:GetServerTimeNow() >= room.startsAt then
			compactQueue(room)
			for i = #room.cars + 1, math.max(4, #room.cars) do
				table.insert(
					room.cars,
					{ id = "bot" .. i, name = "متسابق آلي " .. i, bot = true, state = grid(room.track, i) }
				)
				-- v59: bots at 35/37/39 (players 42) so a clean driver can win; they used to lap at full speed
				room.cars[#room.cars].state.topSpeed = 33 + 2 * math.min(i - 1, 3)
			end
			room.phase = "running"
			room.started = workspace:GetServerTimeNow()
		end
	end
	while accumulated >= 0.05 do
		accumulated -= 0.05
		for _, room in pairs(rooms) do
			if room.phase == "running" then
				local unfinished = 0
				for _, car in ipairs(room.cars) do
					if not car.departed then
						if not car.state.done then
							local intent = car.bot and M.botInput(car.state, room.track)
								or (os.clock() - car.lastPacket > 0.7 and { brake = 1 } or car.input)
							M.step(car.state, intent, 0.05, room.track)
							if car.state.done then
								room.finishCount += 1
								car.finishOrder = room.finishCount
								car.finishTime = workspace:GetServerTimeNow() - room.started
								if car.player and sessions[car.player] and sessions[car.player].car == car then
									Passport.record(car.player, "race", room.track.id)
								end
							else
								unfinished += 1
							end
						end
					end
				end
				if unfinished == 0 or workspace:GetServerTimeNow() - room.started >= D.Duration then
					room.phase = "results"
					for _, car in ipairs(room.cars) do
						if car.player and not car.departed then
							local r = root(car.player)
							if r then
								r.Anchored = false
							end
						end
					end
					send(room, "results")
				end
			end
		end
	end
	if broadcast >= 0.1 then
		broadcast = 0
		for _, room in pairs(rooms) do
			if room.phase ~= "results" then
				send(room)
			end
		end
	end
end)
