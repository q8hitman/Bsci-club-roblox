-- HUD for the island activities: arcade banner (phase/timer/mutation/score), big announcements,
-- the night mutation (local lighting) and the exam timer. Only shown where it matters.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Lighting = game:GetService("Lighting")

local player = Players.LocalPlayer
local gui = Instance.new("ScreenGui")
gui.Name = "IslandHUD"
gui.ResetOnSpawn = false
gui.DisplayOrder = 22
gui.Parent = player:WaitForChild("PlayerGui")

local function label(pos, size, bg)
	local t = Instance.new("TextLabel")
	t.AnchorPoint = Vector2.new(0.5, 0)
	t.Position = pos
	t.Size = size
	t.BackgroundColor3 = bg or Color3.fromRGB(60, 24, 90)
	t.BackgroundTransparency = bg and 0.1 or 1
	t.TextColor3 = Color3.new(1, 1, 1)
	t.TextStrokeTransparency = bg and 1 or 0.3
	t.TextScaled = true
	t.Font = Enum.Font.GothamBold
	t.Visible = false
	t.Parent = gui
	if bg then
		Instance.new("UICorner", t).CornerRadius = UDim.new(0.3, 0)
		local m = Instance.new("UISizeConstraint", t)
		m.MinSize = Vector2.new(240, 30)
	end
	return t
end
local banner = label(UDim2.fromScale(0.5, 0.1), UDim2.fromScale(0.44, 0.06), Color3.fromRGB(60, 24, 90))
local hint = label(UDim2.fromScale(0.5, 0.17), UDim2.fromScale(0.5, 0.04))
hint.TextColor3 = Color3.fromRGB(255, 236, 160)

local big = Instance.new("TextLabel")
big.AnchorPoint = Vector2.new(0.5, 0.5)
big.Position = UDim2.fromScale(0.5, 0.42)
big.Size = UDim2.fromScale(0.6, 0.18)
big.BackgroundTransparency = 1
big.TextColor3 = Color3.new(1, 1, 1)
big.TextStrokeTransparency = 0.1
big.TextStrokeColor3 = Color3.fromRGB(60, 24, 90)
big.TextScaled = true
big.Font = Enum.Font.FredokaOne
big.Visible = false
big.Parent = gui

local function play(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

ReplicatedStorage:WaitForChild("ArcadeAnnounce").OnClientEvent:Connect(function(text, kind)
	big.Text = text
	big.Visible = true
	big.Size = UDim2.fromScale(0.3, 0.09)
	TweenService:Create(big, TweenInfo.new(0.35, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.6, 0.18) }):Play()
	play(kind == "start" and "achievement" or kind == "out" and "wrong" or "sting")
	local shown = text
	task.delay(kind == "start" and 3 or 2.5, function()
		if big.Text == shown then
			big.Visible = false
		end
	end)
end)

-- ------------------------------------------------------------------ exam panel (v31)
-- question + the four options with their zone colours, and which zone you are standing on right now.
local EXAM_COLS = {
	A = Color3.fromRGB(230, 90, 80),
	B = Color3.fromRGB(80, 150, 240),
	C = Color3.fromRGB(90, 200, 110),
	D = Color3.fromRGB(240, 200, 70),
}
local examPanel = Instance.new("Frame")
examPanel.AnchorPoint = Vector2.new(0.5, 0)
examPanel.Position = UDim2.fromScale(0.5, 0.17)
examPanel.Size = UDim2.fromScale(0.5, 0.25)
examPanel.BackgroundColor3 = Color3.fromRGB(20, 30, 46)
examPanel.BackgroundTransparency = 0.15
examPanel.Visible = false
examPanel.Parent = gui
Instance.new("UICorner", examPanel).CornerRadius = UDim.new(0.08, 0)
local examMin = Instance.new("UISizeConstraint", examPanel)
examMin.MinSize = Vector2.new(320, 130)
local examQ = Instance.new("TextLabel")
examQ.Position = UDim2.fromScale(0.03, 0.04)
examQ.Size = UDim2.fromScale(0.94, 0.3)
examQ.BackgroundTransparency = 1
examQ.TextColor3 = Color3.new(1, 1, 1)
examQ.TextScaled = true
examQ.TextWrapped = true
examQ.Font = Enum.Font.GothamBold
examQ.Parent = examPanel
local examOpts = {}
for i, L in ipairs({ "A", "B", "C", "D" }) do
	local o = Instance.new("TextLabel")
	o.Position = UDim2.fromScale(0.03 + ((i - 1) % 2) * 0.48, 0.38 + math.floor((i - 1) / 2) * 0.26)
	o.Size = UDim2.fromScale(0.46, 0.22)
	o.BackgroundColor3 = EXAM_COLS[L]
	o.TextColor3 = Color3.new(1, 1, 1)
	o.TextStrokeTransparency = 0.5
	o.TextScaled = true
	o.TextWrapped = true
	o.Font = Enum.Font.GothamBold
	o.Parent = examPanel
	Instance.new("UICorner", o).CornerRadius = UDim.new(0.25, 0)
	local stroke = Instance.new("UIStroke", o)
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border -- outline the box, not the text
	stroke.Thickness = 0
	stroke.Color = Color3.new(1, 1, 1)
	examOpts[L] = { label = o, stroke = stroke }
end
local examZones = {}
task.spawn(function()
	local hall = workspace:WaitForChild("Map"):WaitForChild("ExamHall", 30)
	for _, L in ipairs({ "A", "B", "C", "D" }) do
		examZones[L] = hall and hall:WaitForChild("ExamZone|" .. L, 10)
	end
end)
local function examZoneAt(pos)
	for L, z in pairs(examZones) do
		local d = pos - z.Position
		if math.abs(d.X) <= z.Size.X / 2 and math.abs(d.Z) <= z.Size.Z / 2 and d.Y > -6 and d.Y < 10 then
			return L
		end
	end
	return nil
end
local function drawExam(pos)
	local mine = examZoneAt(pos)
	local right = workspace:GetAttribute("ExamRight")
	examQ.Text = workspace:GetAttribute("ExamText") or ""
	for L, o in pairs(examOpts) do
		local you = mine == L and "  ⬅ أنت هنا" or ""
		o.label.Text = ("%s) %s%s"):format(L, workspace:GetAttribute("ExamOpt_" .. L) or "", you)
		o.stroke.Thickness = mine == L and 4 or 0
		o.label.BackgroundTransparency = (right and right ~= L) and 0.7 or 0
	end
	examPanel.Visible = true
end

-- areas (see tools/island11.py)
local function near(pos, cx, cz, r)
	return math.abs(pos.X - cx) < r and math.abs(pos.Z - cz) < r
end

local baseClock, baseBright = Lighting.ClockTime, Lighting.Brightness
local nightOn = false

RunService.Heartbeat:Connect(function()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	local pos = root and root.Position
	-- night mutation: local lighting only
	local wantNight = player:GetAttribute("Mutation") == "night"
	if wantNight ~= nightOn then
		nightOn = wantNight
		Lighting.ClockTime = wantNight and 0.5 or baseClock
		Lighting.Brightness = wantNight and 0.6 or baseBright
	end
	if not pos then
		return
	end
	local now = workspace:GetServerTimeNow()
	examPanel.Visible = false
	if near(pos, -6000, -6000, 420) then
		local phase = workspace:GetAttribute("ArcadePhase") or "waiting"
		local left = math.max(0, math.ceil((workspace:GetAttribute("ArcadeEnds") or 0) - now))
		local title = workspace:GetAttribute("ArcadeTitle") or ""
		banner.Visible = true
		if phase == "intermission" then
			banner.Text = ("☕ الجولة الجاية بعد %d"):format(left)
			hint.Visible = false
		elseif phase == "starting" then
			banner.Text = ("🎲 %s  •  تبدأ بعد %d"):format(title, left)
			hint.Text = workspace:GetAttribute("ArcadeHint") or ""
			hint.Visible = true
		elseif phase == "running" then
			banner.Text = ("%s  •  ⏱ %d"):format(title, left)
			local score = player:GetAttribute("RoundScore")
			local combo = player:GetAttribute("Combo") -- ATP Rush streak multiplier
			hint.Text = ("%s   👥 %d%s%s"):format(
				workspace:GetAttribute("ArcadeMutation") or "",
				workspace:GetAttribute("ArcadeAlive") or 0,
				score and score > 0 and ("   ⭐ " .. score) or "",
				combo and combo > 1 and ("   🔥 ×" .. combo) or ""
			)
			hint.Visible = true
		elseif phase == "results" then
			banner.Text = "🏁 النتائج"
			hint.Visible = false
		else
			banner.Text = "🎮 محطة الألعاب: الجولة تبدأ أول ما يدخل لاعب"
			hint.Visible = false
		end
	elseif near(pos, 6000, -6000, 120) and workspace:GetAttribute("ExamQuestion") then
		local left = math.max(0, math.ceil((workspace:GetAttribute("ExamEnds") or 0) - now))
		banner.Visible = true
		banner.Text = ("📝 %s  •  ⏱ %d"):format(workspace:GetAttribute("ExamQuestion"), left)
		hint.Visible = false
		drawExam(pos)
		return
	else
		banner.Visible = false
		hint.Visible = false
	end
end)
