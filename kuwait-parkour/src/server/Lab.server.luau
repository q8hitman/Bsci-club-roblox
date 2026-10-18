-- BSC Research Lab: experiment stations that earn research points (RP), a computer where RP buy projects with
-- real gameplay effects, and the Batch Hall (club batches from Shared/Batches, chosen per player, shown on a tag).
-- The server owns every answer, cost and effect; the client only draws the UI (Lab.client).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local LabData = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("LabData"))
local Batches = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Batches"))
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
		if kind == "microscope" then
			addPrompt(inst, "افحص العيّنة 🔬", "microscope")
		elseif kind == "pcr" then
			addPrompt(inst, "شغّل جهاز PCR 🧬", "pcr")
		elseif kind == "gel" then
			addPrompt(inst, "اقرا الجل 🧪", "gel")
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
		local g = LabData.GELS[rng:NextInteger(1, #LabData.GELS)]
		local smallest, best = 1, math.huge
		for i, label in ipairs(g) do
			local n = tonumber(label:match("%d+"))
			if n < best then
				smallest, best = i, n
			end
		end
		local token = newToken()
		pending[player] = { kind = "gel", answer = smallest, token = token }
		return { token = token, bands = g, research = s.research }
	elseif action == "pcr" then
		local token = newToken()
		pending[player] = { kind = "pcr", token = token, at = os.clock() }
		return { token = token, research = s.research }
	elseif action == "answer" then
		local p = pending[player]
		if not p or a ~= p.token then
			return { ok = false }
		end
		pending[player] = nil
		local ok
		if p.kind == "microscope" or p.kind == "gel" then
			ok = b == p.answer
		elseif p.kind == "pcr" then
			-- 3 cycles x 3 steps cannot honestly be finished in under ~8 s
			ok = b == true and os.clock() - p.at > 8
		end
		local gained = ok and reward(player, p.kind) or 0
		return { ok = ok, gained = gained, research = s.research, answer = (not ok) and p.answer or nil }
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
