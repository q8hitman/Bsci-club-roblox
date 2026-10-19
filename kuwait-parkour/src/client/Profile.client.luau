-- "🎒" menu: achievements, collection (cats + specimens with their facts), trail shop and title picker.
-- Everything shown comes from the server snapshot (Shop:InvokeServer("get")); buying/equipping asks the server.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local P = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Progression"))
local Zones = require(ReplicatedStorage.Shared:WaitForChild("Zones"))
local Batches = require(ReplicatedStorage.Shared:WaitForChild("Batches"))
local shop = ReplicatedStorage:WaitForChild("Shop")
local player = Players.LocalPlayer

local GREEN = Color3.fromRGB(24, 80, 56)
local DARK = Color3.fromRGB(22, 28, 38)

local gui = Instance.new("ScreenGui")
gui.Name = "ProfileMenu"
gui.ResetOnSpawn = false
gui.DisplayOrder = 50 -- keep counters/world-menu controls behind the open Passport on small screens
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
	l.TextWrapped = true
	local sizeBounds = Instance.new("UITextSizeConstraint")
	sizeBounds.MinTextSize = 12
	sizeBounds.MaxTextSize = 30
	sizeBounds.Parent = l
	l.Font = font or Enum.Font.GothamBold
	l.Text = t
	l.Parent = parent
	return l
end

local open = Instance.new("TextButton")
open.Name = "ProfileOpen"
open.AnchorPoint = Vector2.new(0, 0)
open.Position = UDim2.fromScale(0.01, 0.42) -- below the counters, even when they hit their phone minimum size
open.Size = UDim2.fromScale(0.07, 0.07)
open.BackgroundColor3 = GREEN
open.TextColor3 = Color3.new(1, 1, 1)
open.TextScaled = true
open.Font = Enum.Font.GothamBold
open.Text = "📘"
open.Parent = gui
corner(open, 0.3)
Instance.new("UIAspectRatioConstraint", open)
local openMin = Instance.new("UISizeConstraint", open) -- touch target of at least 48 px
openMin.MinSize = Vector2.new(48, 48)

local panel = Instance.new("Frame")
panel.Name = "ProfilePanel"
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.Size = UDim2.fromScale(0.92, 0.86)
panel.BackgroundColor3 = DARK
panel.Visible = false
panel.Active = true
panel.Parent = gui
corner(panel, 0.04)
local bounds = Instance.new("UISizeConstraint")
bounds.MaxSize = Vector2.new(950, 650)
bounds.Parent = panel

text(panel, "📘 جواز BSC | Passport", UDim2.fromScale(0.5, 0.08), UDim2.fromScale(0.25, 0.02))
local coinsLabel =
	text(panel, "", UDim2.fromScale(0.2, 0.06), UDim2.fromScale(0.02, 0.03), Color3.fromRGB(255, 220, 90))

local close = Instance.new("TextButton")
close.Name = "Close"
-- The eighth slot avoids the emulated phone CoreGui controls above the panel's right corner.
close.AnchorPoint = Vector2.zero
close.Position = UDim2.new(0.741, 0, 0, 104)
close.Size = UDim2.new(0.225, 0, 0, 44)
close.BackgroundColor3 = Color3.fromRGB(150, 50, 60)
close.TextColor3 = Color3.new(1, 1, 1)
close.TextScaled = true
close.Font = Enum.Font.GothamBold
close.Text = "إغلاق ×"
close.Parent = panel
local closeMin = Instance.new("UISizeConstraint")
closeMin.MinSize = Vector2.new(44, 44)
closeMin.Parent = close
corner(close, 0.3)

local tabs = {
	"📘 جوازي",
	"🏅 إنجازات",
	"🐱 المجموعة",
	"✨ المظهر",
	"⏱ أوقاتي",
	"📅 الأسبوع",
	"🎓 الدفعة",
}
local tabButtons, page = {}, Instance.new("ScrollingFrame")
page.Name = "Page"
page.Position = UDim2.new(0.03, 0, 0, 158)
page.Size = UDim2.new(0.94, 0, 1, -172)
page.BackgroundTransparency = 1
page.ScrollBarThickness = 8
page.AutomaticCanvasSize = Enum.AutomaticSize.Y
page.CanvasSize = UDim2.new()
page.Parent = panel
local grid = Instance.new("UIGridLayout", page)
grid.CellSize = UDim2.new(0.48, 0, 0, 88)
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
	f.Name = "Card" .. order
	f.LayoutOrder = order
	f.BackgroundColor3 = color
	f.Parent = page
	corner(f, 0.15)
	local heading = text(f, title, UDim2.fromScale(buttonText and 0.66 or 0.94, 0.4), UDim2.fromScale(0.03, 0.04))
	heading:FindFirstChildOfClass("UITextSizeConstraint").MaxTextSize = 23
	local description = text(
		f,
		sub,
		UDim2.fromScale(buttonText and 0.66 or 0.94, 0.46),
		UDim2.fromScale(0.03, 0.48),
		Color3.fromRGB(220, 225, 235),
		Enum.Font.Gotham
	)
	description:FindFirstChildOfClass("UITextSizeConstraint").MaxTextSize = 16
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
	return f
end

local render

local function act(action, id)
	if _G.BSCPlay then
		_G.BSCPlay("click")
	end
	local s
	if action == "batch" then
		ReplicatedStorage:WaitForChild("Lab"):InvokeServer("setBatch", id)
		s = shop:InvokeServer("get")
	else
		s = shop:InvokeServer(action, id)
	end
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
		local p = snap.passport
		if not p then
			return
		end
		local levelCard = card(
			1,
			("المستوى %d"):format(p.level),
			("إجمالي XP: %d\nتحتاج %d XP للمستوى التالي"):format(p.xp, p.nextXP - p.progress),
			GREEN
		)
		local bar = Instance.new("Frame")
		bar.Name = "XPProgress"
		bar.BorderSizePixel = 0
		bar.Position = UDim2.fromScale(0.03, 0.96)
		bar.Size = UDim2.fromScale(0.94 * p.progress / p.nextXP, 0.035)
		bar.BackgroundColor3 = Color3.fromRGB(255, 220, 90)
		bar.Parent = levelCard
		card(
			2,
			"كيف تجمع XP؟",
			"مرحلة جديدة: 10 • مقتنى جديد: 25\nأول نشاط أركيد/مختبر/مسابقات: 40",
			Color3.fromRGB(35, 60, 80)
		)
		card(
			3,
			"مستكشف العوالم",
			("زرت %d عالمًا من أصل 12\nاللقب بعد زيارة 5 عوالم"):format(p.visits),
			Color3.fromRGB(38, 75, 68)
		)
		card(
			4,
			"تقدم تجميلي",
			"الألقاب وXP ما تغيّر توازن الألعاب\nاختر لقبك من صفحة المظهر",
			Color3.fromRGB(55, 48, 72)
		)
		card(
			5,
			"تحديات أسبوعية",
			"تتجدد الاثنين 00:00 UTC\n75 XP لكل تحدٍ مكتمل • صفحة الأسبوع",
			Color3.fromRGB(38, 62, 82)
		)
		card(
			6,
			"دفعتك اختيارية",
			"اختيار داخل اللعبة، بدون معلومات شخصية\nتقدر تغيّرها أو تلغيها من صفحة الدفعة",
			Color3.fromRGB(64, 54, 38)
		)
	elseif currentTab == 2 then
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
	elseif currentTab == 3 then
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
	elseif currentTab == 4 then
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
	elseif currentTab == 5 then
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
	elseif currentTab == 6 then
		for i, c in ipairs(snap.passport.weekly) do
			local earned = c.progress >= c.goal
			card(
				i,
				(c.claimed and "✅ " or "📅 ") .. c.ar,
				("%s\nالتقدم: %d من %d • المكافأة: %d XP"):format(c.desc, c.progress, c.goal, c.xp),
				c.claimed and GREEN or DARK,
				earned and not c.claimed and "استلم" or nil,
				function()
					act("week", c.id)
				end
			)
		end
		card(
			4,
			"موعد التجدد",
			DateTime.fromUnixTimestamp(snap.passport.resetAt):FormatUniversalTime("YYYY-MM-DD HH:mm", "en-us") .. " UTC",
			Color3.fromRGB(35, 55, 70)
		)
	elseif currentTab == 7 then
		card(
			1,
			"بدون دفعة",
			"اختياري • إلغاء الاختيار لا يمس تقدمك",
			GREEN,
			snap.batch == nil and "الحالية" or "اختار",
			function()
				act("batch", nil)
			end
		)
		for i, b in ipairs(Batches) do
			card(
				i + 1,
				b.ar,
				"اختيار داخل اللعبة • تقدر تغيّره بأي وقت",
				Color3.fromRGB(35, 55, 70),
				snap.batch == b.id and "الحالية" or "اختار",
				function()
					act("batch", b.id)
				end
			)
		end
	end
end

for i, name in ipairs(tabs) do
	local b = Instance.new("TextButton")
	b.Name = "Tab" .. i
	b.Position = UDim2.new(0.03 + ((i - 1) % 4) * 0.237, 0, 0, 56 + math.floor((i - 1) / 4) * 48)
	b.Size = UDim2.new(0.225, 0, 0, 44)
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Text = name
	b.Parent = panel
	corner(b, 0.3)
	tabButtons[i] = b
	b.Activated:Connect(function()
		currentTab = i
		page.CanvasPosition = Vector2.zero
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

-- Refresh while open, including across the server's weekly rollover; clients never calculate rewards.
task.spawn(function()
	while gui.Parent do
		task.wait(15)
		if panel.Visible then
			local fresh = shop:InvokeServer("get")
			local a, b = snap and snap.passport, fresh and fresh.passport
			local changed = not a or not b or a.week ~= b.week or a.xp ~= b.xp or a.visits ~= b.visits
			if a and b then
				for i, c in ipairs(b.weekly) do
					changed = changed or c.progress ~= a.weekly[i].progress or c.claimed ~= a.weekly[i].claimed
				end
			end
			if fresh then
				snap = fresh
			end
			if changed then
				render()
			end
		end
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
		currentTab = 4
		toggle(true)
	end)
end
