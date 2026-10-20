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
	{ "Course", "🏃", "كمّل الباركور", "Continue Parkour", Color3.fromRGB(210, 120, 40) },
	{ "Museum", "🦕", "متحف الأحياء", "Bio Museum", Color3.fromRGB(45, 145, 135) },
	{ "Cart", "🚆", "قطار التخصصات", "Specialties Train", Color3.fromRGB(150, 90, 170) },
	{ "Train", "🦠", "قطار الخلية", "Cell Train", Color3.fromRGB(120, 70, 160) },
	{ "Lab", "🔬", "المختبرات", "Biology Labs", Color3.fromRGB(40, 130, 110) },
	{ "Quiz", "🏆", "مركز التحديات", "Challenge Center", Color3.fromRGB(190, 150, 40) },
	{ "Show", "🎤", "استوديو المسابقات", "Game Show", Color3.fromRGB(200, 120, 40) },
	{ "Arcade", "🎮", "الأركيد", "BSC Arcade", Color3.fromRGB(200, 70, 120) },
	{ "Racers", "🏎️", "سباق الجزيئات", "Micro Racers", Color3.fromRGB(50, 150, 175) },
	{ "Laser", "🚨", "هروب الليزر", "Laser Escape", Color3.fromRGB(45, 95, 140) },
	{ "Puzzle", "🧩", "غرف الألغاز", "Puzzle Rooms", Color3.fromRGB(110, 70, 150) },
	{ "Exam", "📝", "الاختبار الجماعي", "Group Exam", Color3.fromRGB(90, 100, 120) },
}

-- Short activity descriptions stay inside the existing cards; travel keys are unchanged.
local DESCRIPTIONS = {
	Campus = "تجوّل في\nكلية العلوم",
	HQ = "استرح واستكشف\nمقر النادي",
	Course = "اقفز وتقدّم\nعبر المراحل",
	Museum = "معارض تفاعلية\nللتخصصات الثمانية",
	Cart = "جولة بين\nتخصصات الأحياء",
	Train = "جولة داخل\nالخلية",
	Arcade = "تنافس وتعاون\nمقترح للبداية",
	Racers = "سباق مركبات\nفي العالم المجهري",
	Laser = "تجاوز أشعة الليزر\nعبر 5 غرف",
	Lab = "جرّب المجهر\nوالتجارب",
	Quiz = "اختبر معلوماتك\nفي الأحياء",
	Exam = "جاوب الأسئلة\nمع المجموعة",
	Puzzle = "حلّ الألغاز\nمع فريقك",
	Show = "خمّن الصور\nوتحدّ الذاكرة",
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
panel.Position = UDim2.fromScale(0.5, 0.51)
panel.Size = UDim2.fromScale(0.94, 0.86)
panel.BackgroundColor3 = Color3.fromRGB(18, 30, 26)
panel.BackgroundTransparency = 0.08
panel.Visible = false
panel.Parent = gui
corner(panel, 0.04)
local aspect = Instance.new("UIAspectRatioConstraint")
aspect.AspectRatio = 1.72
aspect.Parent = panel

label(panel, "🌍 اختر عالمك", UDim2.fromScale(0.05, 0.02), UDim2.fromScale(0.9, 0.085))
label(
	panel,
	"Choose a world",
	UDim2.fromScale(0.05, 0.105),
	UDim2.fromScale(0.9, 0.045),
	Color3.fromRGB(170, 220, 200),
	Enum.Font.Gotham
)

local close = Instance.new("TextButton")
close.AnchorPoint = Vector2.new(1, 0)
close.Position = UDim2.fromScale(0.985, 0.025)
close.Size = UDim2.fromScale(0.065, 0.095)
close.BackgroundColor3 = Color3.fromRGB(150, 50, 50)
close.Text = "X"
close.TextScaled = true
close.TextColor3 = Color3.new(1, 1, 1)
close.Font = Enum.Font.GothamBold
close.Parent = panel
corner(close, 0.3)

local grid = Instance.new("Frame")
grid.BackgroundTransparency = 1
grid.Position = UDim2.fromScale(0.025, 0.165)
grid.Size = UDim2.fromScale(0.95, 0.805)
grid.Parent = panel
local layout = Instance.new("UIGridLayout")
layout.CellSize = UDim2.fromScale(0.188, 0.312)
layout.CellPadding = UDim2.fromScale(0.014, 0.024)
layout.SortOrder = Enum.SortOrder.LayoutOrder
layout.Parent = grid

local busy = false
local function setOpen(v)
	panel.Visible = v
	if v then
		panel.Size = UDim2.fromScale(0.84, 0.76)
		TweenService:Create(panel, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.94, 0.86) })
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
	label(card, w[2], UDim2.fromScale(0.1, 0.02), UDim2.fromScale(0.8, 0.22))
	local title = label(card, w[3], UDim2.fromScale(0.04, 0.25), UDim2.fromScale(0.92, 0.23))
	title.TextWrapped = true
	label(
		card,
		w[4],
		UDim2.fromScale(0.04, 0.49),
		UDim2.fromScale(0.92, 0.13),
		Color3.fromRGB(235, 240, 238),
		Enum.Font.Gotham
	)
	local description = label(
		card,
		DESCRIPTIONS[w[1]],
		UDim2.fromScale(0.03, 0.63),
		UDim2.fromScale(0.94, 0.34),
		if w[1] == "Arcade" then Color3.fromRGB(255, 245, 180) else Color3.new(1, 1, 1),
		Enum.Font.Gotham
	)
	description.Name = "Description"
	description.TextWrapped = true
	local textSize = Instance.new("UITextSizeConstraint")
	textSize.MinTextSize = 8
	textSize.MaxTextSize = 18
	textSize.Parent = description
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
