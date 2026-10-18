-- "🎒" menu: achievements, collection (cats + specimens with their facts), trail shop and title picker.
-- Everything shown comes from the server snapshot (Shop:InvokeServer("get")); buying/equipping asks the server.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local P = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Progression"))
local Zones = require(ReplicatedStorage.Shared:WaitForChild("Zones"))
local shop = ReplicatedStorage:WaitForChild("Shop")
local player = Players.LocalPlayer

local GREEN = Color3.fromRGB(24, 80, 56)
local DARK = Color3.fromRGB(22, 28, 38)

local gui = Instance.new("ScreenGui")
gui.Name = "ProfileMenu"
gui.ResetOnSpawn = false
gui.DisplayOrder = 20
gui.Parent = player:WaitForChild("PlayerGui")

local function corner(o, r)
	Instance.new("UICorner", o).CornerRadius = UDim.new(r or 0.2, 0)
end
local function text(parent, t, size, pos, color, font)
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size, l.Position = size, pos or UDim2.new()
	l.TextColor3 = color or Color3.new(1, 1, 1)
	l.TextScaled = true
	l.Font = font or Enum.Font.GothamBold
	l.Text = t
	l.Parent = parent
	return l
end

local open = Instance.new("TextButton")
open.AnchorPoint = Vector2.new(0, 0)
open.Position = UDim2.fromScale(0.01, 0.42) -- below the counters, even when they hit their phone minimum size
open.Size = UDim2.fromScale(0.07, 0.07)
open.BackgroundColor3 = GREEN
open.TextColor3 = Color3.new(1, 1, 1)
open.TextScaled = true
open.Font = Enum.Font.GothamBold
open.Text = "🎒"
open.Parent = gui
corner(open, 0.3)
Instance.new("UIAspectRatioConstraint", open)
local openMin = Instance.new("UISizeConstraint", open) -- touch target of at least 48 px
openMin.MinSize = Vector2.new(48, 48)

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.52)
panel.Size = UDim2.fromScale(0.62, 0.72)
panel.BackgroundColor3 = DARK
panel.Visible = false
panel.Parent = gui
corner(panel, 0.04)
local ar = Instance.new("UIAspectRatioConstraint", panel)
ar.AspectRatio = 1.45
ar.DominantAxis = Enum.DominantAxis.Height

text(panel, "🎒 ملفي | My BSC Profile", UDim2.fromScale(0.7, 0.08), UDim2.fromScale(0.15, 0.02))
local coinsLabel =
	text(panel, "", UDim2.fromScale(0.2, 0.06), UDim2.fromScale(0.02, 0.03), Color3.fromRGB(255, 220, 90))

local close = Instance.new("TextButton")
close.AnchorPoint = Vector2.new(1, 0)
close.Position = UDim2.fromScale(0.98, 0.02)
close.Size = UDim2.fromScale(0.07, 0.08)
close.BackgroundColor3 = Color3.fromRGB(150, 50, 60)
close.TextColor3 = Color3.new(1, 1, 1)
close.TextScaled = true
close.Font = Enum.Font.GothamBold
close.Text = "X"
close.Parent = panel
corner(close, 0.3)

local tabs = { "🏅 إنجازات", "🐱 المجموعة", "✨ الأثر والألقاب", "⏱ أوقاتي" }
local tabButtons, page = {}, Instance.new("ScrollingFrame")
page.Position = UDim2.fromScale(0.03, 0.22)
page.Size = UDim2.fromScale(0.94, 0.75)
page.BackgroundTransparency = 1
page.ScrollBarThickness = 8
page.AutomaticCanvasSize = Enum.AutomaticSize.Y
page.CanvasSize = UDim2.new()
page.Parent = panel
local grid = Instance.new("UIGridLayout", page)
grid.CellSize = UDim2.new(0.48, 0, 0, 64)
grid.CellPadding = UDim2.new(0.02, 0, 0, 8)
grid.SortOrder = Enum.SortOrder.LayoutOrder

local snap = nil
local currentTab = 1

local function clearPage()
	for _, c in ipairs(page:GetChildren()) do
		if c:IsA("GuiObject") then
			c:Destroy()
		end
	end
end

local function card(order, title, sub, color, buttonText, onClick)
	local f = Instance.new("Frame")
	f.LayoutOrder = order
	f.BackgroundColor3 = color
	f.Parent = page
	corner(f, 0.15)
	text(f, title, UDim2.fromScale(buttonText and 0.66 or 0.94, 0.5), UDim2.fromScale(0.03, 0.04))
	text(
		f,
		sub,
		UDim2.fromScale(buttonText and 0.66 or 0.94, 0.4),
		UDim2.fromScale(0.03, 0.54),
		Color3.fromRGB(220, 225, 235),
		Enum.Font.Gotham
	)
	if buttonText then
		local b = Instance.new("TextButton")
		b.AnchorPoint = Vector2.new(1, 0.5)
		b.Position = UDim2.fromScale(0.97, 0.5)
		b.Size = UDim2.fromScale(0.28, 0.66)
		b.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
		b.TextColor3 = Color3.fromRGB(20, 30, 40)
		b.TextScaled = true
		b.Font = Enum.Font.GothamBold
		b.Text = buttonText
		b.Parent = f
		corner(b, 0.3)
		b.Activated:Connect(onClick)
	end
end

local render

local function act(action, id)
	if _G.BSCPlay then
		_G.BSCPlay("click")
	end
	local s = shop:InvokeServer(action, id)
	if s then
		snap = s
		render()
	end
end

render = function()
	if not snap then
		return
	end
	coinsLabel.Text = ("💰 %d"):format(snap.coins)
	for i, b in ipairs(tabButtons) do
		b.BackgroundColor3 = i == currentTab and GREEN or Color3.fromRGB(40, 48, 62)
	end
	clearPage()
	local n = 0
	if currentTab == 1 then
		for _, a in ipairs(P.Achievements) do
			n += 1
			local got = snap.ach[a.id]
			card(
				n,
				(got and "✅ " or "🔒 ") .. a.ar,
				a.desc .. ("  (+%d)"):format(a.coins or 0),
				got and Color3.fromRGB(40, 90, 60) or Color3.fromRGB(44, 50, 64)
			)
		end
	elseif currentTab == 2 then
		local ids = {}
		for id in pairs(P.Cats) do
			table.insert(ids, id)
		end
		table.sort(ids, function(a, b)
			return tonumber(a:sub(2)) < tonumber(b:sub(2))
		end)
		for _, id in ipairs(ids) do
			n += 1
			local got = snap.found[id]
			card(
				n,
				got and ("🐱 " .. P.Cats[id].name) or "🐱 ؟؟؟",
				got and P.Cats[id].text
					or "قطوة مخفية بالكلية أو المقر… دوّر عليها ✨",
				got and Color3.fromRGB(60, 70, 40) or Color3.fromRGB(44, 50, 64)
			)
		end
		for i = 1, P.SpecimenCount do
			local id = "s" .. i
			n += 1
			local got = snap.found[id]
			card(
				n,
				got and P.Specimens[id].ar or ("🔬 عيّنة " .. Zones[i].nameAr),
				got and P.Specimens[id].text or "مخفية جنب مسار الباركور بهالمنطقة ✨",
				got and Color3.fromRGB(30, 70, 70) or Color3.fromRGB(44, 50, 64)
			)
		end
	elseif currentTab == 3 then
		n += 1
		card(n, "بدون أثر", "", Color3.fromRGB(44, 50, 64), snap.equip.trail and "إلبس" or "✔", function()
			act("trail", nil)
		end)
		for _, t in ipairs(P.Trails) do
			n += 1
			local owned, on = snap.owned[t.id], snap.equip.trail == t.id
			card(
				n,
				t.ar,
				owned and "عندك" or ("💰 " .. t.price),
				Color3.fromRGB(50, 44, 72),
				on and "✔" or (owned and "إلبس" or "اشتري"),
				function()
					act(owned and "trail" or "buy", t.id)
				end
			)
		end
		n += 1
		card(
			n,
			"بدون لقب",
			"",
			Color3.fromRGB(44, 50, 64),
			snap.equip.title and "اختار" or "✔",
			function()
				act("title", nil)
			end
		)
		for _, a in ipairs(P.Achievements) do
			if a.title then
				n += 1
				local got, on = snap.ach[a.id], snap.equip.title == a.id
				card(
					n,
					a.title,
					got and "لقب مفتوح" or ("🔒 " .. a.desc),
					got and Color3.fromRGB(70, 56, 20) or Color3.fromRGB(44, 50, 64),
					got and (on and "✔" or "اختار") or nil,
					function()
						act("title", a.id)
					end
				)
			end
		end
	else
		for i, z in ipairs(Zones) do
			n += 1
			local t = snap.best[tostring(i)]
			card(
				n,
				z.nameAr,
				t and ("أفضل وقت ⏱ %d:%02d"):format(math.floor(t / 60), math.floor(t % 60))
					or "ما خلّصتها كاملة بعد",
				Color3.fromRGB(30, 50, 80)
			)
		end
	end
end

for i, name in ipairs(tabs) do
	local b = Instance.new("TextButton")
	b.Position = UDim2.fromScale(0.03 + (i - 1) * 0.237, 0.12)
	b.Size = UDim2.fromScale(0.225, 0.08)
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Text = name
	b.Parent = panel
	corner(b, 0.3)
	tabButtons[i] = b
	b.Activated:Connect(function()
		currentTab = i
		render()
	end)
end

local function toggle(show)
	panel.Visible = show
	if show then
		snap = shop:InvokeServer("get")
		render()
	end
end
open.Activated:Connect(function()
	toggle(not panel.Visible)
end)
close.Activated:Connect(function()
	toggle(false)
end)
player:GetAttributeChangedSignal("Coins"):Connect(function()
	if panel.Visible then
		snap = shop:InvokeServer("get")
		render()
	end
end)

-- the shop counter in the HQ opens this menu on the cosmetics tab
local kiosk = workspace:WaitForChild("Map"):FindFirstChild("ShopKiosk", true)
if kiosk then
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "افتح المتجر"
	prompt.ObjectText = "✨ متجر الأثر والألقاب"
	prompt.MaxActivationDistance = 12
	prompt.Parent = kiosk
	prompt.Triggered:Connect(function()
		currentTab = 3
		toggle(true)
	end)
end
