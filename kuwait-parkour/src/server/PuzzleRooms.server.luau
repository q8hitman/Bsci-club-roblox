-- غرف الألغاز (puzzle rooms). Data-driven: every module in PuzzleRoomDefs describes one room as a list of steps, each
-- step a reusable puzzle type from PuzzleTypes (Circuit, Specimens, Core...). A room's map folder is
-- "PuzzleRoom_<id>" (tools/chaos_gen.py). Adding a room = a map folder + a def module; no framework changes.
-- Co-op without lock-in: all state is shared by whoever is in the room, nothing needs two people at once, nobody owns
-- a step, so a teammate leaving never blocks the others. No timer. Hints come in 3 levels per step.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local mapFolder = workspace:WaitForChild("Map")
local typesFolder = script.Parent:WaitForChild("PuzzleTypes")
local defsFolder = script.Parent:WaitForChild("PuzzleRoomDefs")

-- v61: the code pieces are DNA bases (was random emoji with no meaning); each slot holds two bases
local BASES = { "A", "T", "G", "C" }
local ICONS = { "⚡", "🔬" }
local LAMP_OFF, LAMP_ON = Color3.fromRGB(70, 74, 90), Color3.fromRGB(70, 200, 120)
local REWARD_COOLDOWN = 15 * 60
local EMPTY_RESET = 60

local function notifyPlayer(p, text)
	local ev = ReplicatedStorage:FindFirstChild("Notify")
	if ev and p.Parent then
		ev:FireClient(p, text)
	end
end

local function setScreen(part, text)
	local label = part and part:FindFirstChildWhichIsA("TextLabel", true)
	if label then
		label.Text = text
	end
end

local function makePrompt(part, action, object)
	local pr = Instance.new("ProximityPrompt")
	pr.ActionText = action
	pr.ObjectText = object or ""
	pr.HoldDuration = 0
	pr.MaxActivationDistance = 9
	pr.RequiresLineOfSight = false
	pr.Parent = part
	return pr
end

local function startRoom(def)
	local folder = mapFolder:FindFirstChild("PuzzleRoom_" .. def.id, true)
	if not folder then
		warn("puzzle room map missing: " .. def.id)
		return
	end
	local bounds = folder:FindFirstChild("RoomBounds")
	local room = {
		folder = folder,
		symbols = {},
		steps = {},
		solved = false,
		hintLevel = {},
		rewardedAt = {},
		makePrompt = makePrompt,
		setScreen = setScreen,
	}

	function room.playersInside()
		local list = {}
		for _, p in ipairs(Players:GetPlayers()) do
			local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
			if root and bounds then
				local d = bounds.CFrame:PointToObjectSpace(root.Position)
				local h = bounds.Size / 2
				if math.abs(d.X) < h.X and math.abs(d.Y) < h.Y and math.abs(d.Z) < h.Z then
					table.insert(list, p)
				end
			end
		end
		return list
	end

	function room.tell(text)
		for _, p in ipairs(room.playersInside()) do
			notifyPlayer(p, text)
		end
	end

	function room.isInside(player)
		for _, p in ipairs(room.playersInside()) do
			if p == player then
				return true
			end
		end
		return false
	end

	local function finish()
		room.solved = true
		local core = folder:FindFirstChild("Core")
		if core then
			core.Material = Enum.Material.Neon
			core.Color = Color3.fromRGB(120, 255, 200)
		end
		local now = os.clock()
		for _, p in ipairs(room.playersInside()) do
			local s = Profiles.state[p]
			Passport.record(p, "puzzle", def.id)
			Passport.record(p, "activity", "puzzle")
			if s and (not room.rewardedAt[p] or now - room.rewardedAt[p] > REWARD_COOLDOWN) then
				room.rewardedAt[p] = now
				s.coins += 15
				p:SetAttribute("Coins", s.coins)
				s.research = (s.research or 0) + 3
				p:SetAttribute("Research", s.research)
				notifyPlayer(p, "🎉 حلّيتوا الغرفة! +15 💰 +3 🧪")
			else
				notifyPlayer(p, "🎉 حلّيتوا الغرفة! (المكافأة مرة كل 15 دقيقة)")
			end
		end
	end

	-- the three lamps on the goal wall light up as steps are solved, so progress reads from across the room
	function room.lamps()
		for i, st in ipairs(room.steps) do
			local lamp = folder:FindFirstChild("StepLamp|" .. i)
			if lamp then
				lamp.Color = st.solved and LAMP_ON or LAMP_OFF
				lamp.Material = st.solved and Enum.Material.Neon or Enum.Material.SmoothPlastic
			end
		end
	end

	function room.changed()
		room.lamps()
		if room.solved then
			return
		end
		for _, st in ipairs(room.steps) do
			if not st.solved then
				return
			end
		end
		finish()
	end

	function room.stepSolved(index)
		local st = room.steps[index]
		return st and st.solved
	end

	-- build the steps from the def
	for i, cfg in ipairs(def.steps) do
		local Type = require(typesFolder:WaitForChild(cfg.type))
		local st = Type.new(room, cfg, i)
		room.steps[i] = st
	end

	function room.reset()
		room.solved = false
		table.clear(room.hintLevel)
		-- a fresh random DNA strand, two bases per slot
		for slot = 1, def.symbolSlots or 2 do
			room.symbols[slot] = { BASES[math.random(1, 4)], BASES[math.random(1, 4)] }
			setScreen(folder:FindFirstChild("SymbolScreen|" .. slot), ICONS[slot] .. "  ؟ ؟")
		end
		local core = folder:FindFirstChild("Core")
		if core then
			core.Material = Enum.Material.Glass
			core.Color = Color3.fromRGB(90, 100, 130)
		end
		for _, st in ipairs(room.steps) do
			st:reset()
		end
		room.lamps()
	end

	function room.reveal(slot)
		local b = room.symbols[slot]
		setScreen(folder:FindFirstChild("SymbolScreen|" .. slot), ("%s  %s %s"):format(ICONS[slot], b[1], b[2]))
	end

	-- hint terminal: next hint for the first unsolved step (3 levels each), 4 s cooldown
	local lastHint = 0
	local hintPart = folder:FindFirstChild("HintTerminal")
	if hintPart then
		makePrompt(hintPart, "تلميح", "💡").Triggered:Connect(function(player)
			if os.clock() - lastHint < 4 or not room.isInside(player) then
				return
			end
			lastHint = os.clock()
			if room.solved then
				notifyPlayer(player, "الغرفة محلولة ✅ اضغط «إعادة» تلعبها من جديد")
				return
			end
			for i, st in ipairs(room.steps) do
				if not st.solved then
					room.hintLevel[i] = math.min((room.hintLevel[i] or 0) + 1, 3)
					room.tell("💡 " .. st:hint(room.hintLevel[i]))
					return
				end
			end
		end)
	end
	local resetPart = folder:FindFirstChild("ResetTerminal")
	if resetPart then
		makePrompt(resetPart, "إعادة الغرفة", "🔄").Triggered:Connect(function(player)
			if room.isInside(player) then
				room.reset()
				room.tell("🔄 الغرفة رجعت من جديد بألغاز مختلفة")
			end
		end)
	end

	room.reset()

	-- whoever walks in gets the goal once, in one line
	task.spawn(function()
		local seen = {}
		while true do
			task.wait(1)
			local now = {}
			for _, p in ipairs(room.playersInside()) do
				now[p] = true
				if not seen[p] and def.objective then
					notifyPlayer(p, def.objective)
				end
			end
			seen = now
		end
	end)

	-- an empty room resets itself after a minute, so the next visitors always start clean
	task.spawn(function()
		local emptySince = nil
		while true do
			task.wait(5)
			if #room.playersInside() == 0 then
				emptySince = emptySince or os.clock()
				local touched = room.solved or (next(room.hintLevel) ~= nil)
				for _, st in ipairs(room.steps) do
					touched = touched or st.solved or st.dirty
				end
				if touched and os.clock() - emptySince > EMPTY_RESET then
					room.reset()
					emptySince = nil
				end
			else
				emptySince = nil
			end
		end
	end)
	return room
end

local rooms = {}

-- Studio-only QA hook (like Labs54QA): ServerStorage.PuzzleQA:Invoke(id, op, step) runs the same check paths a
-- player's taps run. op "state" | "solve" (puts the right answer in place for one step and checks it) | "wrong"
-- (pulls the lever with wrong bases) | "reset".
if game:GetService("RunService"):IsStudio() then
	local qa = Instance.new("BindableFunction")
	qa.Name = "PuzzleQA"
	qa.OnInvoke = function(id, op, step)
		local room = rooms[id]
		if not room then
			return "no room " .. tostring(id)
		end
		local st = room.steps[step or 0]
		if op == "solve" and st then
			if st.tiles then
				for t in pairs(st.onPath) do
					t.rot = t.goalRots[1]
				end
				st:draw()
				st:check()
			elseif st.truth then
				for i, ped in ipairs(st.peds) do
					ped.pick = st.truth[i]
				end
				st:refreshTags()
				st:check()
			else
				for i, panel in ipairs(st.panels) do
					panel.pick = table.find(BASES, st:need(i)) or 0
				end
				st:refresh()
				st:activate()
			end
		elseif op == "wrong" and st and st.panels then
			for i, panel in ipairs(st.panels) do
				panel.pick = table.find(BASES, st:need(i) or "A") % 4 + 1
			end
			st:activate()
		elseif op == "reset" then
			room.reset()
		end
		local out = { solved = room.solved, screens = {}, lamps = {}, steps = {} }
		for i, s in ipairs(room.steps) do
			out.steps[i] = s.solved
			local lamp = room.folder:FindFirstChild("StepLamp|" .. i)
			out.lamps[i] = lamp and lamp.Material.Name
		end
		for slot = 1, 2 do
			local scr = room.folder:FindFirstChild("SymbolScreen|" .. slot)
			local l = scr and scr:FindFirstChildWhichIsA("TextLabel", true)
			out.screens[slot] = l and l.Text
		end
		return out
	end
	qa.Parent = game:GetService("ServerStorage")
end

for _, m in ipairs(defsFolder:GetChildren()) do
	if m:IsA("ModuleScript") then
		local ok, err = pcall(function()
			local def = require(m)
			rooms[def.id] = startRoom(def)
		end)
		if not ok then
			warn("puzzle room failed: " .. m.Name .. ": " .. tostring(err))
		end
	end
end
