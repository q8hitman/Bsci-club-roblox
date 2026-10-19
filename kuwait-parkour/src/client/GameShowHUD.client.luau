-- Game Show HUD (v42): on a phone the studio's main screen is too far away to read, so while the player is inside
-- StudioBounds the main-screen and scoreboard texts are mirrored into a small panel. Read-only: the server still
-- owns the show and its screens; this only copies their text.
local Players = game:GetService("Players")

local player = Players.LocalPlayer
local map = workspace:WaitForChild("Map")
local studio = map:FindFirstChild("GameShowStudio", true)
for _ = 1, 60 do
	if studio then
		break
	end
	task.wait(1)
	studio = map:FindFirstChild("GameShowStudio", true)
end
if not studio then
	return
end
local bounds = studio:WaitForChild("StudioBounds")
local function labelOf(name)
	local part = studio:WaitForChild(name)
	return part:FindFirstChildWhichIsA("TextLabel", true)
end
local mainLabel, scoreLabel = labelOf("MainScreen"), labelOf("ScoreBoard")

local gui = Instance.new("ScreenGui")
gui.Name = "GameShowHUD"
gui.ResetOnSpawn = false
gui.DisplayOrder = 21
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(1, 0) -- right side, so the picture board in the middle stays visible
panel.Position = UDim2.fromScale(0.985, 0.2)
panel.Size = UDim2.fromScale(0.36, 0.48)
panel.BackgroundColor3 = Color3.fromRGB(24, 20, 48)
panel.BackgroundTransparency = 0.15
panel.Parent = gui
Instance.new("UICorner", panel).CornerRadius = UDim.new(0.08, 0)
local stroke = Instance.new("UIStroke", panel)
stroke.Color, stroke.Thickness = Color3.fromRGB(200, 120, 255), 2
local limit = Instance.new("UISizeConstraint", panel)
limit.MaxSize = Vector2.new(440, 360)

local function text(y, h, color)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position = UDim2.fromScale(0.04, y)
	t.Size = UDim2.fromScale(0.92, h)
	t.TextColor3 = color
	t.TextScaled, t.TextWrapped = true, true
	t.Font = Enum.Font.GothamBold
	t.Parent = panel
	local c = Instance.new("UITextSizeConstraint", t)
	c.MinTextSize, c.MaxTextSize = 10, 32
	return t
end
local score = text(0.03, 0.13, Color3.fromRGB(255, 220, 110))
local body = text(0.17, 0.8, Color3.new(1, 1, 1))

local function sync()
	body.Text = mainLabel.Text
	score.Text = scoreLabel.Text
end
mainLabel:GetPropertyChangedSignal("Text"):Connect(sync)
scoreLabel:GetPropertyChangedSignal("Text"):Connect(sync)
sync()

local function inside()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if not root then
		return false
	end
	local d = bounds.CFrame:PointToObjectSpace(root.Position)
	local h = bounds.Size / 2
	return math.abs(d.X) < h.X and math.abs(d.Y) < h.Y and math.abs(d.Z) < h.Z
end

while true do
	gui.Enabled = inside()
	task.wait(0.5)
end
