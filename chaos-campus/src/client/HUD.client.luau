-- Chaos Campus HUD: phase banner with timer, round score, big announcements (game + mutation, results).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = Instance.new("ScreenGui")
gui.Name = "ChaosHUD"
gui.ResetOnSpawn = false
gui.Parent = player:WaitForChild("PlayerGui")

local banner = Instance.new("TextLabel")
banner.AnchorPoint = Vector2.new(0.5, 0)
banner.Position = UDim2.fromScale(0.5, 0.02)
banner.Size = UDim2.fromScale(0.46, 0.07)
banner.BackgroundColor3 = Color3.fromRGB(60, 24, 90)
banner.BackgroundTransparency = 0.1
banner.TextColor3 = Color3.new(1, 1, 1)
banner.TextScaled = true
banner.Font = Enum.Font.GothamBold
banner.Parent = gui
Instance.new("UICorner", banner).CornerRadius = UDim.new(0.3, 0)
local bmin = Instance.new("UISizeConstraint", banner)
bmin.MinSize = Vector2.new(260, 34)

local hint = Instance.new("TextLabel")
hint.AnchorPoint = Vector2.new(0.5, 0)
hint.Position = UDim2.fromScale(0.5, 0.1)
hint.Size = UDim2.fromScale(0.5, 0.045)
hint.BackgroundTransparency = 1
hint.TextColor3 = Color3.fromRGB(255, 236, 160)
hint.TextStrokeTransparency = 0.3
hint.TextScaled = true
hint.Font = Enum.Font.GothamBold
hint.Parent = gui

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

local sounds = {}
for name, id in pairs({ start = 17208327798, result = 9040172806, out = 17208353912 }) do
	local s = Instance.new("Sound")
	s.SoundId = "rbxassetid://" .. id
	s.Volume = 0.6
	s.Parent = gui
	sounds[name] = s
end

ReplicatedStorage:WaitForChild("Announce").OnClientEvent:Connect(function(text, kind)
	big.Text = text
	big.Visible = true
	big.Size = UDim2.fromScale(0.3, 0.09)
	TweenService:Create(big, TweenInfo.new(0.35, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.6, 0.18) }):Play()
	if sounds[kind] then
		sounds[kind]:Play()
	end
	local shown = text
	task.delay(kind == "start" and 3 or 2.5, function()
		if big.Text == shown then
			big.Visible = false
		end
	end)
end)

local LABEL = {
	waiting = "⏳ ننتظر لاعبين…",
	intermission = "☕ الجولة الجاية بعد %d",
	starting = "🎲 %s",
	running = "%s  •  ⏱ %d",
	results = "🏁 النتائج",
}

RunService.Heartbeat:Connect(function()
	local phase = workspace:GetAttribute("Phase") or "waiting"
	local left = math.max(0, math.ceil((workspace:GetAttribute("EndsAt") or 0) - workspace:GetServerTimeNow()))
	local title = workspace:GetAttribute("GameTitle") or ""
	if phase == "intermission" then
		banner.Text = LABEL.intermission:format(left)
		hint.Text = ""
	elseif phase == "starting" then
		banner.Text = LABEL.starting:format(title)
		hint.Text = workspace:GetAttribute("GameHint") or ""
	elseif phase == "running" then
		banner.Text = LABEL.running:format(title, left)
		local score = player:GetAttribute("RoundScore")
		hint.Text = ("%s   👥 %d%s"):format(workspace:GetAttribute("Mutation") or "", workspace:GetAttribute("Alive") or 0,
			score and score > 0 and ("   ⭐ " .. score) or "")
	else
		banner.Text = LABEL[phase] or ""
		hint.Text = ""
	end
end)
