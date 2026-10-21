-- v53 "First Day at the College": a small, optional checklist for new players (right side, under the top buttons;
-- hidden while seated so it never covers the ride controls).
-- Four steps that each open a main activity; progress comes from the server (player attribute "FirstDay",
-- e.g. "1010", set by PassportService from verified stamps). Each step has a "go" button (the normal Travel remote).
-- Hidden for experienced players, when all steps are done, or when the player closes it (X, for this session).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local travel = ReplicatedStorage:WaitForChild("Travel", 30)

local STEPS = {
	{ "🏛️ زُر مقر النادي", "HQ" },
	{ "🎮 العب جولة بالأركيد", "Arcade" },
	{ "🔬 سوّ تجربة بالمختبر", "Lab" },
	{ "🚆 اركب قطار للآخر", "Train" },
}

task.wait(6) -- let the saved profile and the welcome card come first
local flags = player:GetAttribute("FirstDay")
if (player:GetAttribute("PassportLevel") or 1) >= 4 or flags == "1111" then
	return
end

local gui = Instance.new("ScreenGui")
gui.Name = "FirstDay"
gui.ResetOnSpawn = false
gui.DisplayOrder = 12
gui.Parent = player:WaitForChild("PlayerGui")

local card = Instance.new("Frame")
card.AnchorPoint = Vector2.new(1, 0)
card.Position = UDim2.fromScale(0.985, 0.2)
card.Size = UDim2.fromScale(0.2, 0.24)
card.BackgroundColor3 = Color3.fromRGB(20, 44, 36)
card.BackgroundTransparency = 0.15
card.Parent = gui
Instance.new("UICorner", card).CornerRadius = UDim.new(0.08, 0)
local minSize = Instance.new("UISizeConstraint")
minSize.MinSize = Vector2.new(170, 120)
minSize.MaxSize = Vector2.new(320, 220)
minSize.Parent = card

local title = Instance.new("TextLabel")
title.BackgroundTransparency = 1
title.Position = UDim2.fromScale(0.04, 0.02)
title.Size = UDim2.fromScale(0.78, 0.2)
title.TextXAlignment = Enum.TextXAlignment.Center
title.TextColor3 = Color3.fromRGB(255, 226, 120)
title.TextScaled = true
title.Font = Enum.Font.GothamBold
title.Text = "🎒 أول يوم بالكلية"
title.Parent = card

local close = Instance.new("TextButton")
close.Position = UDim2.fromScale(0.84, 0.03)
close.Size = UDim2.fromScale(0.13, 0.17)
close.BackgroundColor3 = Color3.fromRGB(120, 50, 50)
close.TextColor3 = Color3.new(1, 1, 1)
close.TextScaled = true
close.Font = Enum.Font.GothamBold
close.Text = "X"
close.Parent = card
Instance.new("UICorner", close).CornerRadius = UDim.new(0.3, 0)
close.Activated:Connect(function()
	gui:Destroy()
end)

local rows = {}
for i, step in ipairs(STEPS) do
	local y = 0.24 + (i - 1) * 0.19
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Position = UDim2.fromScale(0.3, y)
	label.Size = UDim2.fromScale(0.66, 0.16)
	label.TextColor3 = Color3.new(1, 1, 1)
	label.TextScaled = true
	label.Font = Enum.Font.GothamBold
	label.TextXAlignment = Enum.TextXAlignment.Right
	label.Text = step[1]
	label.Parent = card
	local go = Instance.new("TextButton")
	go.Name = "Go_" .. step[2]
	go.Position = UDim2.fromScale(0.04, y + 0.01)
	go.Size = UDim2.fromScale(0.23, 0.15)
	go.BackgroundColor3 = Color3.fromRGB(60, 150, 100)
	go.TextColor3 = Color3.new(1, 1, 1)
	go.TextScaled = true
	go.Font = Enum.Font.GothamBold
	go.Text = "روح"
	go.Parent = card
	Instance.new("UICorner", go).CornerRadius = UDim.new(0.3, 0)
	go.Activated:Connect(function()
		if travel and go.Active then
			if _G.BSCPlay then
				_G.BSCPlay("click")
			end
			travel:FireServer(step[2])
		end
	end)
	rows[i] = { label = label, go = go, text = step[1] }
end

local function refresh()
	local f = player:GetAttribute("FirstDay") or "0000"
	local done = 0
	for i, r in ipairs(rows) do
		local ok = f:sub(i, i) == "1"
		done += ok and 1 or 0
		r.label.Text = (ok and "✅ " or "") .. r.text
		r.label.TextTransparency = ok and 0.45 or 0
		r.go.Visible = not ok
		r.go.Active = not ok
	end
	title.Text = ("🎒 أول يوم بالكلية %d/4"):format(done)
	if done == #rows then
		-- the server awards the achievement + title; say well done, then get out of the way
		title.Text = "🎓 خلصت أول يوم! لقبك: طالب مستجد"
		task.delay(6, function()
			if gui.Parent then
				TweenService:Create(card, TweenInfo.new(0.6), { BackgroundTransparency = 1 }):Play()
				task.wait(0.6)
				gui:Destroy()
			end
		end)
	end
end
refresh()
player:GetAttributeChangedSignal("FirstDay"):Connect(refresh)
task.spawn(function()
	while gui.Parent do
		local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
		card.Visible = not (hum and hum.Sit)
		task.wait(0.5)
	end
end)
