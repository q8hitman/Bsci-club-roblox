-- v37 world menu: one button (left edge) opens a grid of worlds; a card asks the server to move the player there
-- (Travel remote in Main: the same moves as the portals, so every world stays reachable on foot too).
-- Sized in scale + an aspect-ratio constraint so it reads on phones and PCs alike.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local travel = ReplicatedStorage:WaitForChild("Travel")

local WORLDS = {
	{ "Campus", "🏛️", "كلية العلوم", "College of Science", Color3.fromRGB(70, 110, 150) },
	{ "HQ", "🏠", "مقر النادي", "BSC HQ", Color3.fromRGB(24, 110, 76) },
	{ "Island", "🏝️", "جزيرة المغامرة", "Adventure Island", Color3.fromRGB(40, 140, 160) },
	{ "Course", "🏃", "كمّل الباركور", "Continue Parkour", Color3.fromRGB(210, 120, 40) },
	{ "Cart", "🚆", "قطار التخصصات", "Specialties Train", Color3.fromRGB(150, 90, 170) },
	{ "Train", "🦠", "قطار الخلية", "Cell Train", Color3.fromRGB(120, 70, 160) },
	{ "Arcade", "🎮", "الأركيد", "BSC Arcade", Color3.fromRGB(200, 70, 120) },
	{ "Lab", "🔬", "المختبرات", "Biology Labs", Color3.fromRGB(40, 130, 110) },
	{ "Quiz", "🏆", "مركز التحديات", "Challenge Center", Color3.fromRGB(190, 150, 40) },
	{ "Exam", "📝", "الاختبار الجماعي", "Group Exam", Color3.fromRGB(90, 100, 120) },
	{ "Puzzle", "🧩", "غرف الألغاز", "Puzzle Rooms", Color3.fromRGB(110, 70, 150) },
}

local gui = Instance.new("ScreenGui")
gui.Name = "WorldMenu"
gui.ResetOnSpawn = false
gui.DisplayOrder = 30
gui.IgnoreGuiInset = false
gui.Parent = player:WaitForChild("PlayerGui")

local function corner(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r, 0)
	c.Parent = o
end

local function label(parent, text, pos, size, color, font)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position = pos
	t.Size = size
	t.Text = text
	t.TextScaled = true
	t.TextColor3 = color or Color3.new(1, 1, 1)
	t.Font = font or Enum.Font.GothamBold
	t.Parent = parent
	return t
end

-- toggle button on the left edge, under the bag button of the HUD
local open = Instance.new("TextButton")
open.Name = "WorldsButton"
open.AnchorPoint = Vector2.new(0, 0.5)
open.Position = UDim2.new(0, 10, 0.66, 0)
open.Size = UDim2.fromOffset(118, 42)
open.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
open.Text = "🌍 العوالم"
open.TextScaled = true
open.TextColor3 = Color3.new(1, 1, 1)
open.Font = Enum.Font.GothamBold
open.Parent = gui
corner(open, 0.3)
local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(120, 255, 200)
stroke.Thickness = 2
stroke.Parent = open

local panel = Instance.new("Frame")
panel.Name = "Panel"
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.52)
panel.Size = UDim2.fromScale(0.9, 0.8)
panel.BackgroundColor3 = Color3.fromRGB(18, 30, 26)
panel.BackgroundTransparency = 0.08
panel.Visible = false
panel.Parent = gui
corner(panel, 0.04)
local aspect = Instance.new("UIAspectRatioConstraint")
aspect.AspectRatio = 1.6
aspect.Parent = panel

label(panel, "🌍 اختر عالمك", UDim2.fromScale(0.05, 0.03), UDim2.fromScale(0.9, 0.09))
label(
	panel,
	"Choose a world",
	UDim2.fromScale(0.05, 0.115),
	UDim2.fromScale(0.9, 0.05),
	Color3.fromRGB(170, 220, 200),
	Enum.Font.Gotham
)

local close = Instance.new("TextButton")
close.AnchorPoint = Vector2.new(1, 0)
close.Position = UDim2.fromScale(0.985, 0.025)
close.Size = UDim2.fromScale(0.07, 0.1)
close.BackgroundColor3 = Color3.fromRGB(150, 50, 50)
close.Text = "X"
close.TextScaled = true
close.TextColor3 = Color3.new(1, 1, 1)
close.Font = Enum.Font.GothamBold
close.Parent = panel
corner(close, 0.3)

local grid = Instance.new("Frame")
grid.BackgroundTransparency = 1
grid.Position = UDim2.fromScale(0.03, 0.2)
grid.Size = UDim2.fromScale(0.94, 0.77)
grid.Parent = panel
local layout = Instance.new("UIGridLayout")
layout.CellSize = UDim2.fromScale(0.155, 0.46)
layout.CellPadding = UDim2.fromScale(0.014, 0.04)
layout.SortOrder = Enum.SortOrder.LayoutOrder
layout.Parent = grid

local busy = false
local function setOpen(v)
	panel.Visible = v
	if v then
		panel.Size = UDim2.fromScale(0.8, 0.7)
		TweenService:Create(panel, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.9, 0.8) })
			:Play()
	end
end

for i, w in ipairs(WORLDS) do
	local card = Instance.new("TextButton")
	card.Name = w[1]
	card.LayoutOrder = i
	card.Text = ""
	card.AutoButtonColor = true
	card.BackgroundColor3 = w[5]
	card.Parent = grid
	corner(card, 0.1)
	label(card, w[2], UDim2.fromScale(0.1, 0.06), UDim2.fromScale(0.8, 0.38))
	label(card, w[3], UDim2.fromScale(0.05, 0.48), UDim2.fromScale(0.9, 0.24))
	label(
		card,
		w[4],
		UDim2.fromScale(0.05, 0.74),
		UDim2.fromScale(0.9, 0.16),
		Color3.fromRGB(235, 240, 238),
		Enum.Font.Gotham
	)
	card.Activated:Connect(function()
		if busy then
			return
		end
		busy = true
		if _G.BSCPlay then
			_G.BSCPlay("click")
		end
		travel:FireServer(w[1])
		setOpen(false)
		task.delay(2, function()
			busy = false
		end)
	end)
end

open.Activated:Connect(function()
	setOpen(not panel.Visible)
end)
close.Activated:Connect(function()
	setOpen(false)
end)

-- other scripts (welcome card) can open it
_G.BSCOpenWorlds = function()
	setOpen(true)
end
