-- Dialogue box for island characters: name + role, one line at a time, tap/click to continue.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = Instance.new("ScreenGui")
gui.Name = "Dialogue"
gui.ResetOnSpawn = false
gui.DisplayOrder = 35
gui.Parent = player:WaitForChild("PlayerGui")

local box = Instance.new("TextButton")
box.AutoButtonColor = false
box.AnchorPoint = Vector2.new(0.5, 1)
box.Position = UDim2.fromScale(0.5, 0.95)
box.Size = UDim2.fromScale(0.62, 0.2)
box.BackgroundColor3 = Color3.fromRGB(250, 246, 236)
box.Text = ""
box.Visible = false
box.Parent = gui
Instance.new("UICorner", box).CornerRadius = UDim.new(0.12, 0)
local stroke = Instance.new("UIStroke", box)
stroke.Color = Color3.fromRGB(24, 80, 56)
stroke.Thickness = 3
local minS = Instance.new("UISizeConstraint", box)
minS.MinSize = Vector2.new(300, 110)

local nameTag = Instance.new("TextLabel")
nameTag.Position = UDim2.fromScale(0.03, -0.22)
nameTag.Size = UDim2.fromScale(0.42, 0.3)
nameTag.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
nameTag.TextColor3 = Color3.new(1, 1, 1)
nameTag.TextScaled = true
nameTag.Font = Enum.Font.GothamBold
nameTag.Parent = box
Instance.new("UICorner", nameTag).CornerRadius = UDim.new(0.3, 0)

local text = Instance.new("TextLabel")
text.Position = UDim2.fromScale(0.04, 0.16)
text.Size = UDim2.fromScale(0.92, 0.6)
text.BackgroundTransparency = 1
text.TextColor3 = Color3.fromRGB(40, 40, 46)
text.TextScaled = true
text.TextWrapped = true
text.Font = Enum.Font.GothamBold
text.Parent = box

local hint = Instance.new("TextLabel")
hint.Position = UDim2.fromScale(0.6, 0.78)
hint.Size = UDim2.fromScale(0.37, 0.18)
hint.BackgroundTransparency = 1
hint.TextColor3 = Color3.fromRGB(120, 120, 130)
hint.TextScaled = true
hint.Font = Enum.Font.Gotham
hint.Text = "اضغط عشان تكمل ▶"
hint.Parent = box

local lines, index, closeAt = {}, 0, 0

local function show(i)
	index = i
	text.Text = ""
	local full = lines[i]
	-- typewriter effect
	task.spawn(function()
		local mine = index
		for n = 1, utf8.len(full) or #full do
			if index ~= mine then
				return
			end
			local cut = utf8.offset(full, n + 1)
			text.Text = cut and full:sub(1, cut - 1) or full
			task.wait(0.02)
		end
	end)
	closeAt = os.clock() + 8
	if _G.BSCPlay then
		_G.BSCPlay("click")
	end
end

box.Activated:Connect(function()
	if index < #lines then
		show(index + 1)
	else
		box.Visible = false
	end
end)

ReplicatedStorage:WaitForChild("NPCTalk").OnClientEvent:Connect(function(name, role, newLines)
	lines = newLines
	nameTag.Text = name .. " • " .. role
	box.Visible = true
	box.Position = UDim2.fromScale(0.5, 1.2)
	TweenService:Create(box, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Position = UDim2.fromScale(0.5, 0.95) })
		:Play()
	show(1)
end)

-- close automatically when idle or when the player walks away
task.spawn(function()
	while true do
		task.wait(0.5)
		if box.Visible and os.clock() > closeAt then
			box.Visible = false
		end
	end
end)
