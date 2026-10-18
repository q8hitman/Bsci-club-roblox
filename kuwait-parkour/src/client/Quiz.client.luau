local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local ask = ReplicatedStorage:WaitForChild("QuizAsk")
local answer = ReplicatedStorage:WaitForChild("QuizAnswer")

local gui = Instance.new("ScreenGui")
gui.Name = "QuizGui"
gui.ResetOnSpawn = false
gui.DisplayOrder = 20
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.Size = UDim2.fromScale(0.62, 0.58)
panel.BackgroundColor3 = Color3.fromRGB(22, 38, 32)
panel.Parent = gui
Instance.new("UICorner", panel).CornerRadius = UDim.new(0.05, 0)
local stroke = Instance.new("UIStroke", panel)
stroke.Color = Color3.fromRGB(46, 160, 90)
stroke.Thickness = 3

local function label(size, pos, bold)
	local l = Instance.new("TextLabel")
	l.Size = size
	l.Position = pos
	l.BackgroundTransparency = 1
	l.TextScaled = true
	l.TextColor3 = Color3.new(1, 1, 1)
	l.Font = bold and Enum.Font.GothamBold or Enum.Font.Gotham
	l.Parent = panel
	return l
end

local title = label(UDim2.fromScale(0.9, 0.12), UDim2.fromScale(0.05, 0.04), true)
title.TextColor3 = Color3.fromRGB(120, 230, 160)
local question = label(UDim2.fromScale(0.9, 0.22), UDim2.fromScale(0.05, 0.18), true)
local result = label(UDim2.fromScale(0.9, 0.09), UDim2.fromScale(0.05, 0.89), false)

local close = Instance.new("TextButton")
close.AnchorPoint = Vector2.new(1, 0)
close.Position = UDim2.fromScale(0.98, 0.02)
close.Size = UDim2.fromScale(0.07, 0.1)
close.BackgroundColor3 = Color3.fromRGB(120, 50, 50)
close.TextColor3 = Color3.new(1, 1, 1)
close.TextScaled = true
close.Font = Enum.Font.GothamBold
close.Text = "X"
close.Parent = panel
Instance.new("UICorner", close).CornerRadius = UDim.new(0.3, 0)

local buttons = {}
for i = 1, 3 do
	local b = Instance.new("TextButton")
	b.Size = UDim2.fromScale(0.86, 0.14)
	b.Position = UDim2.fromScale(0.07, 0.43 + (i - 1) * 0.15)
	b.BackgroundColor3 = Color3.fromRGB(40, 70, 58)
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamMedium
	b.AutoButtonColor = true
	b.Parent = panel
	Instance.new("UICorner", b).CornerRadius = UDim.new(0.2, 0)
	buttons[i] = b
end

local current
local busy = false

local function show(payload)
	current = payload
	if payload.level > 0 then
		title.Text = ("سؤال في تخصص: %s  (المرحلة %d)"):format(payload.zone, payload.level)
	else
		title.Text = ("تدريب — %s  (+1 عملة)"):format(payload.zone)
	end
	question.Text = payload.q
	for i, b in ipairs(buttons) do
		b.Text = payload.choices[i]
	end
	result.Text = ""
	busy = false
	gui.Enabled = true
end

for i, b in ipairs(buttons) do
	b.Activated:Connect(function()
		if busy or not current then
			return
		end
		busy = true
		local ok, nextQuestion = answer:InvokeServer(current.token, i)
		if ok then
			result.TextColor3 = Color3.fromRGB(120, 230, 160)
			result.Text = "إجابة صحيحة!"
			task.wait(1.1)
			gui.Enabled = false
			current = nil
		else
			result.TextColor3 = Color3.fromRGB(255, 120, 110)
			result.Text = "إجابة خاطئة، سؤال جديد…"
			task.wait(1.2)
			if nextQuestion then
				show(nextQuestion)
			else
				gui.Enabled = false
			end
		end
		busy = false
	end)
end

close.Activated:Connect(function()
	gui.Enabled = false
	current = nil
	busy = false
end)

ask.OnClientEvent:Connect(show)
