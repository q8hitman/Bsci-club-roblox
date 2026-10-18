local Players = game:GetService("Players")
local player = Players.LocalPlayer

local gui = Instance.new("ScreenGui")
gui.Name = "StageHUD"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = false
gui.Parent = player:WaitForChild("PlayerGui")

local label = Instance.new("TextLabel")
label.AnchorPoint = Vector2.new(0.5, 0)
label.Position = UDim2.fromScale(0.5, 0.02)
label.Size = UDim2.fromScale(0.3, 0.07) -- scale-based: fits phone and PC
label.BackgroundColor3 = Color3.fromRGB(20, 40, 30)
label.BackgroundTransparency = 0.25
label.TextColor3 = Color3.new(1, 1, 1)
label.TextScaled = true
label.Font = Enum.Font.GothamBold
label.Parent = gui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0.25, 0)
corner.Parent = label

local limit = Instance.new("UITextSizeConstraint")
limit.MaxTextSize = 28
limit.Parent = label

local function refresh()
	local stage = player:GetAttribute("Stage") or 0
	local total = player:GetAttribute("Total") or 0
	label.Text = ("المرحلة %d / %d"):format(stage, total)
end

player:GetAttributeChangedSignal("Stage"):Connect(refresh)
player:GetAttributeChangedSignal("Total"):Connect(refresh)
refresh()

-- Discord panel: a TextBox so the link can be selected and copied
-- (Roblox cannot open external URLs from a script).
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("LevelConfig"))

local button = Instance.new("TextButton")
button.AnchorPoint = Vector2.new(1, 0)
button.Position = UDim2.fromScale(0.98, 0.02)
button.Size = UDim2.fromScale(0.14, 0.07)
button.BackgroundColor3 = Color3.fromRGB(88, 101, 242)
button.TextColor3 = Color3.new(1, 1, 1)
button.TextScaled = true
button.Font = Enum.Font.GothamBold
button.Text = "Discord"
button.Parent = gui
Instance.new("UICorner", button).CornerRadius = UDim.new(0.25, 0)

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.Size = UDim2.fromScale(0.5, 0.32)
panel.BackgroundColor3 = Color3.fromRGB(20, 40, 30)
panel.Visible = false
panel.Parent = gui
Instance.new("UICorner", panel).CornerRadius = UDim.new(0.06, 0)

local title = Instance.new("TextLabel")
title.Size = UDim2.fromScale(0.9, 0.3)
title.Position = UDim2.fromScale(0.05, 0.08)
title.BackgroundTransparency = 1
title.TextColor3 = Color3.new(1, 1, 1)
title.TextScaled = true
title.Font = Enum.Font.GothamBold
title.Text = "انضموا لمجتمع " .. Config.Club.NameAr
title.Parent = panel

local linkBox = Instance.new("TextBox")
linkBox.Size = UDim2.fromScale(0.9, 0.25)
linkBox.Position = UDim2.fromScale(0.05, 0.42)
linkBox.BackgroundColor3 = Color3.fromRGB(10, 22, 16)
linkBox.TextColor3 = Color3.fromRGB(180, 200, 255)
linkBox.TextScaled = true
linkBox.Font = Enum.Font.Code
linkBox.Text = Config.Club.Discord
linkBox.ClearTextOnFocus = false
linkBox.TextEditable = false
linkBox.Parent = panel
Instance.new("UICorner", linkBox).CornerRadius = UDim.new(0.2, 0)

local hint = Instance.new("TextLabel")
hint.Size = UDim2.fromScale(0.9, 0.15)
hint.Position = UDim2.fromScale(0.05, 0.72)
hint.BackgroundTransparency = 1
hint.TextColor3 = Color3.fromRGB(200, 200, 200)
hint.TextScaled = true
hint.Font = Enum.Font.Gotham
hint.Text = "انسخ الرابط وافتحه في المتصفح"
hint.Parent = panel

button.Activated:Connect(function()
	panel.Visible = not panel.Visible
end)
