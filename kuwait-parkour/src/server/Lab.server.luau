-- BSC Research Lab: experiment stations that earn research points (RP), a computer where RP buy projects with
-- real gameplay effects, and the Batch Hall (club batches from Shared/Batches, chosen per player, shown on a tag).
-- The server owns every answer, cost and effect; the client only draws the UI (Lab.client).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local LabData = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("LabData"))
local Batches = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Batches"))
local Micro = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("MicroscopyData"))
local mapFolder = workspace:WaitForChild("Map")

local openEvent = Instance.new("RemoteEvent")
openEvent.Name = "LabOpen"
openEvent.Parent = ReplicatedStorage
local labFn = Instance.new("RemoteFunction")
labFn.Name = "Lab"
labFn.Parent = ReplicatedStorage

local state = Profiles.state
local rng = Random.new()
local pending = {} -- [player] = { kind, answer, token, at }
local lastReward = {} -- [player] = os.clock()

local UPG = {}
for _, u in ipairs(LabData.UPGRADES) do
	UPG[u.id] = u
end
local BATCH = {}
for _, b in ipairs(Batches) do
	BATCH[b.id] = b
end

-- ------------------------------------------------------------------ effects of the upgrades
local function applyUpgrades(player)
	local s = state[player]
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not (s and hum) then
		return
	end
	local up = s.upgrades or {}
	local base = 16 + (up.enzyme and 2 or 0)
	player:SetAttribute("BaseWalkSpeed", base)
	hum.WalkSpeed = base
	if up.spring then
		if hum.UseJumpPower then
			hum.JumpPower = 56
		else
			hum.JumpHeight = 8.2
		end
	end
	player:SetAttribute("Upg_scope", up.scope == true)
	player:SetAttribute("Upg_mito", up.mito == true)
	player:SetAttribute("Research", s.research or 0)
end

local function applyBatchTag(player)
	local s = state[player]
	local char = player.Character
	local head = char and char:FindFirstChild("Head")
	if not (s and head) then
		return
	end
	local old = head:FindFirstChild("BatchTag")
	if old then
		old:Destroy()
	end
	local b = s.batch and BATCH[s.batch]
	player:SetAttribute("Batch", b and b.id or nil)
	if not b then
		return
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "BatchTag"
	bb.Size = UDim2.fromOffset(150, 24)
	bb.StudsOffset = Vector3.new(0, 3.9, 0)
	bb.MaxDistance = 60
	local t = Instance.new("TextLabel")
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundColor3 = Color3.fromRGB(b.color[1], b.color[2], b.color[3])
	t.BackgroundTransparency = 0.25
	t.TextColor3 = Color3.new(1, 1, 1)
	t.TextScaled = true
	t.Font = Enum.Font.GothamBold
	t.Text = "🎓 " .. b.ar
	t.Parent = bb
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0.4, 0)
	corner.Parent = t
	bb.Parent = head
end

local function onCharacter(player)
	task.wait(0.3)
	applyUpgrades(player)
	applyBatchTag(player)
end

local attached = {}
local function attach(player)
	if attached[player] then
		return
	end
	attached[player] = true
	player.CharacterAdded:Connect(function()
		onCharacter(player)
	end)
	if player.Character then
		task.spawn(onCharacter, player)
	end
end
Profiles.on("loaded", attach)
-- profiles that finished loading before this script started
task.delay(1, function()
	for _, p in ipairs(Players:GetPlayers()) do
		if state[p] then
			attach(p)
		end
	end
end)

-- ------------------------------------------------------------------ automatic Lab Coat inside Research Lab
local labSpawnPart = mapFolder:FindFirstChild("LabSpawn", true)

-- v61: the old automatic box coat is gone (it stacked on top of the PPE-rack coat from Labs54 and looked like a box).
-- The coat now comes only from the lab's coat rack (a real safety step); leaving the lab takes it off.
local PPE_PARTS = { Goggles = true, GoggleStrap = true }
local function takeOffPPE(player)
	local char = player.Character
	if char then
		for _, d in ipairs(char:GetChildren()) do
			if d:IsA("BasePart") and (d.Name:sub(1, 7) == "LabCoat" or PPE_PARTS[d.Name]) then
				d:Destroy()
			end
		end
	end
	player:SetAttribute("LabPPE", nil)
end

if labSpawnPart then
	task.spawn(function()
		while true do
			task.wait(0.8)
			for _, p in ipairs(Players:GetPlayers()) do
				local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
				if root then
					local d = root.Position - labSpawnPart.Position
					local inLab = math.abs(d.X) < 85 and math.abs(d.Z) < 85 and math.abs(d.Y) < 40
					if not inLab and p:GetAttribute("LabPPE") then
						takeOffPPE(p)
					end
				end
			end
		end
	end)
end

-- ------------------------------------------------------------------ station prompts
local function addPrompt(part, action, kind)
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = action
	prompt.ObjectText = "مختبر BSC"
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.HoldDuration = 0
	prompt.Parent = part
	prompt.Triggered:Connect(function(player)
		openEvent:FireClient(player, kind)
	end)
end

for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local kind = inst.Name:match("^LabStation|(.+)$")
		if kind == "lightmicro" then
			addPrompt(inst, "مختبر المجهر الضوئي 🔬", "lightmicro")
		elseif kind == "microscope" then
			addPrompt(inst, "افحص العيّنة 🔬", "microscope")
		elseif kind == "pcr" then
			addPrompt(inst, "شغّل جهاز PCR 🧬", "pcr")
		elseif kind == "gel" then
			addPrompt(inst, "اقرا الجل 🧪", "gel")
		elseif kind == "gram" then
			addPrompt(inst, "صبغة جرام 🧪", "gram")
		elseif inst.Name == "LabComputer" then
			addPrompt(inst, "المشاريع 💻", "computer")
		elseif inst.Name == "BatchPicker" then
			addPrompt(inst, "اختار دفعتك 🎓", "batch")
		end
	end
end

-- ------------------------------------------------------------------ rewards
local function reward(player, kind)
	local s = state[player]
	if not s then
		return 0
	end
	local now = os.clock()
	if lastReward[player] and now - lastReward[player] < LabData.COOLDOWN then
		return 0
	end
	lastReward[player] = now
	local n = LabData.REWARD[kind] or 1
	s.research = (s.research or 0) + n
	player:SetAttribute("Research", s.research)
	return n
end

local function newToken()
	return tostring(rng:NextInteger(1, 2 ^ 30))
end

-- ------------------------------------------------------------------ remote API
labFn.OnServerInvoke = function(player, action, a, b)
	local s = state[player]
	if not s or typeof(action) ~= "string" then
		return nil
	end
	if action == "slide" then
		local slide = LabData.SLIDES[rng:NextInteger(1, #LabData.SLIDES)]
		local token = newToken()
		pending[player] = { kind = "microscope", answer = slide[2], token = token }
		return { token = token, text = slide[1], research = s.research }
	elseif action == "gel" then
		-- v53: an unknown DNA fragment run next to a size ladder. The client only gets three size options now;
		-- band positions arrive after a correct run (gelRun), and the player reads the size against the ladder.
		local sizes = LabData.GEL_UNKNOWNS
		local pick = rng:NextInteger(1, #sizes)
		local options = { sizes[pick] }
		for _, d in ipairs({ -2, 2, -3, 3 }) do
			local q = sizes[pick + d]
			if q and #options < 3 then
				table.insert(options, q)
			end
		end
		for i = #options, 2, -1 do
			local j = rng:NextInteger(1, i)
			options[i], options[j] = options[j], options[i]
		end
		local answer = table.find(options, sizes[pick])
		local token = newToken()
		pending[player] = { kind = "gel", answer = answer, size = sizes[pick], token = token }
		return { token = token, options = options, research = s.research }
	elseif action == "gelRun" then
		-- a = token, b = true when the + electrode is at the far end (DNA is negative and runs toward +)
		local p = pending[player]
		if not p or p.kind ~= "gel" or a ~= p.token then
			return nil
		end
		if b ~= true then
			return { reversed = true }
		end
		p.ran = true
		local ladder = {}
		for _, bp in ipairs(LabData.GEL_LADDER) do
			table.insert(ladder, { bp = bp, y = LabData.gelDistance(bp) })
		end
		return { ladder = ladder, sample = LabData.gelDistance(p.size) }
	elseif action == "pcr" then
		local token = newToken()
		pending[player] = { kind = "pcr", token = token, at = os.clock() }
		return { token = token, research = s.research }
	elseif action == "gram" then
		local sample = LabData.GRAM_SAMPLES[rng:NextInteger(1, #LabData.GRAM_SAMPLES)]
		local token = newToken()
		-- v53: the answer never leaves the server; the client first runs the procedure (gramView), then identifies
		pending[player] = { kind = "gram", answer = sample.gram, token = token, at = os.clock() }
		return {
			token = token,
			name = sample.name,
			shape = sample.shape,
			cocci = sample.id == "staph",
			research = s.research,
		}
	elseif action == "gramView" then
		-- a = token, b = seconds of decolouriser. What the player sees depends on the cell wall AND on that timing.
		local p = pending[player]
		if not p or p.kind ~= "gram" or a ~= p.token or typeof(b) ~= "number" or p.quality then
			return nil
		end
		local D = LabData.GRAM_DECOLOR
		-- the claimed time can never exceed the time that really passed since the stain started
		local secs = math.clamp(math.min(b, os.clock() - p.at), 0, D.bar)
		p.quality = secs < D.min and "under" or secs > D.max and "over" or "ok"
		local violet = (p.answer == "pos" and p.quality ~= "over") or (p.answer == "neg" and p.quality == "under")
		return { color = violet and "violet" or "pink", quality = p.quality }
	elseif action == "answer" then
		local p = pending[player]
		if not p or a ~= p.token then
			return { ok = false }
		end
		pending[player] = nil
		local ok
		if p.kind == "microscope" then
			ok = b == p.answer
		elseif p.kind == "gel" then
			ok = p.ran == true and b == p.answer -- only after the gel was actually run
		elseif p.kind == "gram" then
			-- only a properly decolourised slide counts, and the whole procedure takes real time
			ok = p.quality == "ok" and b == p.answer
		elseif p.kind == "pcr" then
			-- 3 cycles x 3 steps cannot honestly be finished in under ~8 s
			ok = b == true and os.clock() - p.at > 8
		end
		local gained = ok and reward(player, p.kind) or 0
		if gained > 0 then
			Passport.record(player, "activity", "lab")
		end
		return {
			ok = ok,
			gained = gained,
			research = s.research,
			answer = (not ok) and p.answer or nil,
			quality = p.quality,
		}
	elseif action == "lmStart" then
		-- v41 Light Microscopy: one session per player; the notebook is graded on lmSubmit
		local sample
		for _, sm in ipairs(Micro.SAMPLES) do
			if sm.id == a then
				sample = sm
			end
		end
		if not sample then
			return nil
		end
		local token = newToken()
		pending[player] = { kind = "lightmicro", sample = sample, token = token, at = os.clock() }
		return { token = token }
	elseif action == "lmSubmit" then
		local p = pending[player]
		local info = typeof(b) == "table" and b or {}
		if not p or p.kind ~= "lightmicro" or a ~= p.token then
			return { ok = false, reason = "session" }
		end
		local sample = p.sample
		local picked = {}
		for _, i in ipairs(typeof(info.picks) == "table" and info.picks or {}) do
			if typeof(i) == "number" and sample.notes[i] then
				picked[i] = true
			end
		end
		local results, allRight = {}, true
		for i, n in ipairs(sample.notes) do
			local right = (picked[i] == true) == n[2]
			allRight = allRight and right
			table.insert(results, { i = i, right = right, why = (not right) and n[3] or nil })
		end
		local maxMag = typeof(info.maxMag) == "number" and info.maxMag or 0
		local sawIt = maxMag >= sample.needMag and (sample.needMag < 100 or info.oil == true)
		local ok = allRight and sawIt
		local gained = 0
		if ok and info.eval == true and os.clock() - p.at >= 12 then
			s.microDone = s.microDone or {}
			local last = s.microDone[sample.id]
			local now = os.time()
			if not last or now - last >= Micro.COOLDOWN then
				s.microDone[sample.id] = now
				s.research = (s.research or 0) + Micro.REWARD.research
				player:SetAttribute("Research", s.research)
				s.coins += Micro.REWARD.coins
				player:SetAttribute("Coins", s.coins)
				gained = Micro.REWARD.research
				Passport.record(player, "activity", "lab")
			end
		end
		pending[player] = nil
		return { ok = ok, sawIt = sawIt, results = results, gained = gained, research = s.research }
	elseif action == "projects" then
		local list = {}
		for _, u in ipairs(LabData.UPGRADES) do
			table.insert(
				list,
				{ id = u.id, ar = u.ar, desc = u.desc, cost = u.cost, owned = (s.upgrades or {})[u.id] == true }
			)
		end
		return { list = list, research = s.research }
	elseif action == "buy" then
		local u = typeof(a) == "string" and UPG[a]
		s.upgrades = s.upgrades or {}
		if u and not s.upgrades[a] and (s.research or 0) >= u.cost then
			s.research -= u.cost
			s.upgrades[a] = true
			applyUpgrades(player)
			return { ok = true, research = s.research }
		end
		return { ok = false, research = s.research }
	elseif action == "batches" then
		local list = {}
		for _, bt in ipairs(Batches) do
			table.insert(list, { id = bt.id, ar = bt.ar, color = bt.color })
		end
		return { list = list, current = s.batch }
	elseif action == "setBatch" then
		if a == nil or (typeof(a) == "string" and BATCH[a]) then
			s.batch = a
			applyBatchTag(player)
			return { ok = true }
		end
		return { ok = false }
	end
	return nil
end

Players.PlayerRemoving:Connect(function(player)
	pending[player] = nil
	lastReward[player] = nil
	attached[player] = nil
end)

-- ------------------------------------------------------------------ Batch Hall board (live)
local board = mapFolder:FindFirstChild("BatchBoard", true)
if board then
	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Back
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 24
	gui.LightInfluence = 0
	gui.Parent = board
	local title = Instance.new("TextLabel")
	title.Size = UDim2.fromScale(1, 0.14)
	title.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
	title.TextColor3 = Color3.new(1, 1, 1)
	title.TextScaled = true
	title.Font = Enum.Font.GothamBold
	title.Text = "🎓 قاعة الدفعات | Batch Hall"
	title.Parent = gui
	local list = Instance.new("Frame")
	list.Position = UDim2.fromScale(0.02, 0.17)
	list.Size = UDim2.fromScale(0.96, 0.8)
	list.BackgroundTransparency = 1
	list.Parent = gui
	local layout = Instance.new("UIGridLayout")
	layout.CellSize = UDim2.fromScale(0.48, 0.46)
	layout.CellPadding = UDim2.fromScale(0.02, 0.03)
	layout.Parent = list
	local cards = {}
	for i, bt in ipairs(Batches) do
		local card = Instance.new("TextLabel")
		card.LayoutOrder = i
		card.BackgroundColor3 = Color3.fromRGB(bt.color[1], bt.color[2], bt.color[3])
		card.BackgroundTransparency = 0.1
		card.TextColor3 = Color3.new(1, 1, 1)
		card.TextScaled = true
		card.TextWrapped = true
		card.Font = Enum.Font.GothamBold
		card.Parent = list
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.08, 0)
		c.Parent = card
		cards[bt.id] = { label = card, batch = bt }
	end
	task.spawn(function()
		while true do
			local online = {}
			for _, p in ipairs(Players:GetPlayers()) do
				local id = p:GetAttribute("Batch")
				if id then
					online[id] = (online[id] or 0) + 1
				end
			end
			for id, c in pairs(cards) do
				c.label.Text = ("%s\n%s\n🟢 متصلين الحين: %d"):format(
					c.batch.ar,
					table.concat(c.batch.achievements, "\n"),
					online[id] or 0
				)
			end
			task.wait(8)
		end
	end)
end
