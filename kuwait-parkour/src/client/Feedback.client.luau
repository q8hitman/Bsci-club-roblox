-- Player feedback: toasts with sounds, level-up celebration, coin/collection counters, time-trial clock,
-- area music (crossfaded by where the player is) and hiding sparkles of collectibles already found.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local SoundService = game:GetService("SoundService")

local P = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Progression"))
local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")

-- ------------------------------------------------------------------ sounds
local sfx = {}
for name, id in pairs(P.Sounds) do
	local s = Instance.new("Sound")
	s.Name = "SFX_" .. name
	s.SoundId = "rbxassetid://" .. id
	s.Volume = 0.6
	s.Parent = SoundService
	sfx[name] = s
end
local function play(name)
	local s = sfx[name]
	if s then
		s.TimePosition = 0
		s:Play()
	end
end
_G.BSCPlay = play -- other client scripts (quiz, cart) can reuse the same sounds

-- ------------------------------------------------------------------ UI
local gui = Instance.new("ScreenGui")
gui.Name = "Feedback"
gui.ResetOnSpawn = false
gui.DisplayOrder = 30
gui.Parent = player:WaitForChild("PlayerGui")

local toast = Instance.new("TextLabel")
toast.AnchorPoint = Vector2.new(0.5, 0)
toast.Position = UDim2.fromScale(0.5, 0.68) -- low, so it never covers menus or the stage counter
toast.Size = UDim2.fromScale(0.6, 0.13)
toast.BackgroundColor3 = Color3.fromRGB(30, 34, 44)
toast.BackgroundTransparency = 0.1
toast.TextColor3 = Color3.new(1, 1, 1)
toast.TextScaled = true
toast.TextWrapped = true -- long hints wrap instead of shrinking to an unreadable line on phones
toast.Font = Enum.Font.GothamBold
toast.Visible = false
toast.Parent = gui
Instance.new("UICorner", toast).CornerRadius = UDim.new(0.25, 0)
local stroke = Instance.new("UIStroke", toast)
stroke.Thickness = 2
local pad = Instance.new("UIPadding", toast)
pad.PaddingLeft, pad.PaddingRight = UDim.new(0.03, 0), UDim.new(0.03, 0)
local tsc = Instance.new("UITextSizeConstraint", toast)
tsc.MinTextSize, tsc.MaxTextSize = 11, 30

local KIND = {
	info = { Color3.fromRGB(30, 34, 44), Color3.fromRGB(120, 140, 170), "click" },
	ach = { Color3.fromRGB(70, 50, 10), Color3.fromRGB(255, 210, 80), "achievement" },
	collect = { Color3.fromRGB(30, 60, 50), Color3.fromRGB(120, 255, 200), "collect" },
	record = { Color3.fromRGB(20, 40, 80), Color3.fromRGB(90, 200, 255), "sting" },
	purchase = { Color3.fromRGB(60, 30, 80), Color3.fromRGB(220, 160, 255), "purchase" },
	wrong = { Color3.fromRGB(80, 24, 24), Color3.fromRGB(255, 100, 100), "wrong" },
}

local queue, showing = {}, false
local function pump()
	if showing or #queue == 0 then
		return
	end
	showing = true
	local item = table.remove(queue, 1)
	local k = KIND[item.kind] or KIND.info
	toast.BackgroundColor3, stroke.Color = k[1], k[2]
	toast.Text = item.text
	toast.Visible = true
	toast.Position = UDim2.fromScale(0.5, 0.74)
	TweenService:Create(toast, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Position = UDim2.fromScale(0.5, 0.68) })
		:Play()
	play(k[3])
	-- longer messages (hints) stay long enough to read: ~14 characters per second
	local t = math.max(item.kind == "info" and 2.6 or 4.2, (utf8.len(item.text) or #item.text) / 14)
	task.delay(math.min(t, 9), function()
		toast.Visible = false
		showing = false
		pump()
	end)
end
local function push(text, kind)
	table.insert(queue, { text = text, kind = kind or "info" })
	pump()
end
_G.BSCToast = push

-- collectibles already found: hide their sparkle locally
local sparkles = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local id = inst.Name:match("^Sparkle|(.+)$")
		if id then
			sparkles[id] = sparkles[id] or {}
			table.insert(sparkles[id], inst)
		end
	end
end
local function hideSparkle(id)
	for _, p in ipairs(sparkles[id] or {}) do
		p.LocalTransparencyModifier = 1
	end
end

ReplicatedStorage:WaitForChild("Notify").OnClientEvent:Connect(function(text, kind, id)
	push(text, kind)
	if kind == "collect" and id then
		hideSparkle(id)
	end
end)

task.spawn(function()
	local remote = ReplicatedStorage:WaitForChild("Sfx", 20)
	if remote then
		remote.OnClientEvent:Connect(play)
	end
end)

task.spawn(function()
	local shop = ReplicatedStorage:WaitForChild("Shop", 20)
	if not shop then
		return
	end
	task.wait(3)
	local snap = shop:InvokeServer("get")
	for id in pairs(snap and snap.found or {}) do
		hideSparkle(id)
	end
end)

-- ------------------------------------------------------------------ counters (coins, cats, specimens) + trial clock
local bar = Instance.new("Frame")
bar.AnchorPoint = Vector2.new(0, 0)
bar.Position = UDim2.fromScale(0.01, 0.12)
bar.Size = UDim2.fromScale(0.16, 0.16)
bar.BackgroundTransparency = 1
bar.Parent = gui
local barMin = Instance.new("UISizeConstraint", bar) -- phones: never smaller than a readable size
barMin.MinSize = Vector2.new(120, 96)
local list = Instance.new("UIListLayout", bar)
list.Padding = UDim.new(0.05, 0)

local function chip(order)
	local l = Instance.new("TextLabel")
	l.LayoutOrder = order
	l.Size = UDim2.fromScale(1, 0.28)
	l.BackgroundColor3 = Color3.fromRGB(20, 26, 36)
	l.BackgroundTransparency = 0.25
	l.TextColor3 = Color3.new(1, 1, 1)
	l.TextScaled = true
	l.Font = Enum.Font.GothamBold
	l.Parent = bar
	Instance.new("UICorner", l).CornerRadius = UDim.new(0.3, 0)
	return l
end
local coinsChip, catsChip, specChip = chip(1), chip(2), chip(3)

local function refreshCounters()
	coinsChip.Text = ("💰 %d"):format(player:GetAttribute("Coins") or 0)
	catsChip.Text = ("🐱 %d/%d"):format(player:GetAttribute("Cats") or 0, P.CatCount)
	specChip.Text = ("🔬 %d/%d"):format(player:GetAttribute("Specimens") or 0, P.SpecimenCount)
end
for _, a in ipairs({ "Coins", "Cats", "Specimens" }) do
	player:GetAttributeChangedSignal(a):Connect(refreshCounters)
end
refreshCounters()

local lastCoins = player:GetAttribute("Coins") or 0
player:GetAttributeChangedSignal("Coins"):Connect(function()
	local c = player:GetAttribute("Coins") or 0
	if c > lastCoins then
		play("coin")
		coinsChip.TextColor3 = Color3.fromRGB(255, 220, 90)
		task.delay(0.6, function()
			coinsChip.TextColor3 = Color3.new(1, 1, 1)
		end)
	end
	lastCoins = c
end)

-- v29: no on-screen parkour timer (it cluttered the HUD and pressured new players). Zone times are still measured
-- on the server (Progression: TrialZone/TrialStart) and shown as best times in the 🎒 menu.

-- ------------------------------------------------------------------ level-up celebration
local big = Instance.new("TextLabel")
big.AnchorPoint = Vector2.new(0.5, 0.5)
big.Position = UDim2.fromScale(0.5, 0.36)
big.Size = UDim2.fromScale(0.4, 0.12)
big.BackgroundTransparency = 1
big.TextColor3 = Color3.fromRGB(255, 255, 255)
big.TextStrokeTransparency = 0.2
big.TextStrokeColor3 = Color3.fromRGB(24, 80, 56)
big.TextScaled = true
big.Font = Enum.Font.FredokaOne
big.Visible = false
big.Parent = gui

local function burst(color)
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then
		return
	end
	local a = Instance.new("Attachment")
	a.Parent = root
	local e = Instance.new("ParticleEmitter")
	e.Color = ColorSequence.new(color, Color3.new(1, 1, 1))
	e.Size = NumberSequence.new(0.5, 0)
	e.Lifetime = NumberRange.new(0.6, 1.1)
	e.Speed = NumberRange.new(14, 24)
	e.SpreadAngle = Vector2.new(180, 180)
	e.LightEmission = 0.6
	e.Rate = 0
	e.Parent = a
	e:Emit(40)
	task.delay(1.5, function()
		a:Destroy()
	end)
end

local lastStage = player:GetAttribute("Stage") or 0
local stageReady = false
task.delay(4, function()
	lastStage = player:GetAttribute("Stage") or 0
	stageReady = true -- ignore the jump from 0 to the saved stage on join
end)
player:GetAttributeChangedSignal("Stage"):Connect(function()
	local stage = player:GetAttribute("Stage") or 0
	if stageReady and stage > lastStage then
		play("checkpoint")
		burst(Color3.fromRGB(120, 255, 200))
		big.Text = stage >= 100 and "🏆 100!" or ("المرحلة " .. stage .. " ✔")
		big.Visible = true
		big.Size = UDim2.fromScale(0.2, 0.06)
		TweenService:Create(big, TweenInfo.new(0.35, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.42, 0.13) })
			:Play()
		task.delay(1.4, function()
			big.Visible = false
		end)
	end
	lastStage = stage
end)

-- ------------------------------------------------------------------ area music
local tracks = {}
for area, id in pairs(P.Music) do
	local s = Instance.new("Sound")
	s.Name = "Music_" .. area
	s.SoundId = "rbxassetid://" .. id
	s.Looped = true
	s.Volume = 0
	s.Parent = SoundService
	tracks[area] = s
end
local MUSIC_VOLUME = 0.32
local current = nil

local function areaAt(pos)
	if math.abs(pos.Z + 6000) < 600 and math.abs(math.abs(pos.X) - 6000) < 600 then
		return "course" -- exam hall / arcade: energetic
	elseif math.abs(pos.X) < 1000 and math.abs(pos.Z + 6000) < 1000 then
		return "hq" -- challenge center: calm
	elseif pos.Z < -10000 then
		return "hq"
	elseif pos.X > 10000 then
		return "course"
	elseif pos.X < -7000 and pos.Z > 7000 then
		return "cart" -- v53: the Grand Tour valleys run past x -10000, so test the cart region before the cell world
	elseif pos.X < -10000 then
		return "cell"
	end
	return "campus"
end

task.spawn(function()
	while true do
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		local cam = workspace.CurrentCamera
		local pos = root and root.Position or (cam and cam.CFrame.Position)
		if pos then
			local area = areaAt(pos)
			if area ~= current then
				local old = current and tracks[current]
				current = area
				local new = tracks[area]
				if old then
					TweenService:Create(old, TweenInfo.new(1.5), { Volume = 0 }):Play()
					task.delay(1.6, function()
						if tracks[current] ~= old then
							old:Pause()
						end
					end)
				end
				if new then
					if not new.IsPlaying then
						new:Play()
					end
					TweenService:Create(new, TweenInfo.new(1.5), { Volume = MUSIC_VOLUME }):Play()
				end
				play("whoosh")
			end
		end
		task.wait(0.5)
	end
end)
