-- v56 optional help: one small "؟" button. It opens a short card with tips for wherever you are (station, lab,
-- arcade, course...). It replaces the big "how to play" boards that used to stand in the world.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local HELP = {
	campus = {
		"🏛️ كلية العلوم",
		"🌍 زر «العوالم» ياخذك لأي مكان",
		"🎒 «أول يوم» مهام قصيرة تعرّفك على اللعبة",
		"🐱 فيه قطاوة مخفية بالكلية… دوّرها",
	},
	hq = {
		"🧬 مقر النادي",
		"⬆️ البوابات الشمالية: باركور 100 مرحلة بتخصصاتنا",
		"❓ كل 5 مراحل سؤال سريع",
		"🚪 القاعة الجنوبية: بوابات كل العوالم",
	},
	cart = {
		"🚆 قطار التخصصات",
		"🟣 دوس الدائرة الوردية عشان تركب",
		"▶ / Enter تشغيل وإيقاف • ＋/－ السرعة",
		"🎥 / V كاميرا سينمائية • الرحلة كاملة حوالي نص ساعة",
	},
	cell = {
		"🚋 قطار الخلية",
		"اركب من الباب الوردي بالمحطة",
		"⚡ زر السرعة • 🔄 زر الكاميرا",
		"الرحلة تدخل النواة نفسها 🔬",
	},
	lab = {
		"🔬 معهد الأبحاث",
		"🥼 البس المعطف والنظارة عند المدخل",
		"🖐️ التقط الأدوات من الرف وحطها بالمكان المناسب",
		"🧪 اتبع خطوات التجربة وشوف النتيجة بعينك",
	},
	arcade = {
		"🎮 محطة الألعاب",
		"كل جولة لعبة مختلفة + طفرة عشوائية",
		"آخر واحد صامد أو صاحب أكثر نقاط يفوز",
		"🏆 الفوز = عملات ونقاط بحث",
	},
	quiz = {
		"📚 مركز التحديات",
		"اختار تخصصك وحل 5 أسئلة",
		"⭐ 3 صح تفتح المستوى اللي بعده",
	},
	course = {
		"🏃 الباركور",
		"كل منطقة تخصص، ونقطة الحفظ تنحسب لحالها",
		"🔬 فيه عيّنة مخفية بكل منطقة",
		"↩ زر الرجوع ياخذك للكلية",
	},
	virus = {
		"🦠 لعبة الفيروس",
		"مع أصحابك: الفيروس يعدي اللي يلمسه",
		"لحالك: اهرب من جزيء الفيروس",
		"💉 اللقاح يحميك ثواني",
	},
}

local function areaAt(p)
	if p.X > 10000 then
		return "course"
	elseif p.X < -7000 and p.Z > 7000 then
		return "cart"
	elseif p.X < -10000 then
		return "cell"
	elseif math.abs(p.X) < 1000 and p.Z < -5000 and p.Z > -7100 then
		return "quiz"
	elseif p.Z < -12300 then
		return "virus"
	elseif p.Z < -10000 then
		return "hq"
	elseif p.X < -4000 and p.Z < -4000 then
		return "arcade"
	elseif p.X > 4000 and p.Z > 4000 then
		return "lab"
	elseif p.X > 90 and p.X < 180 and p.Z > -70 and p.Z < -15 then
		return "cell" -- the Cell Train station on the campus east lawn
	end
	return "campus"
end

local gui = Instance.new("ScreenGui")
gui.Name = "Help"
gui.ResetOnSpawn = false
gui.DisplayOrder = 15
gui.Parent = player:WaitForChild("PlayerGui")

local btn = Instance.new("TextButton")
btn.Name = "HelpBtn"
btn.AnchorPoint = Vector2.new(0, 0.5)
btn.Position = UDim2.new(0, 10, 0.595, 0)
btn.Size = UDim2.fromOffset(40, 40)
btn.BackgroundColor3 = Color3.fromRGB(30, 34, 44)
btn.BackgroundTransparency = 0.2
btn.TextColor3 = Color3.new(1, 1, 1)
btn.TextScaled = true
btn.Font = Enum.Font.GothamBold
btn.Text = "؟"
btn.Parent = gui
Instance.new("UICorner", btn).CornerRadius = UDim.new(1, 0)

local card = Instance.new("Frame")
card.AnchorPoint = Vector2.new(0, 0.5)
card.Position = UDim2.new(0, 58, 0.595, 0)
card.Size = UDim2.fromScale(0.3, 0.26)
card.BackgroundColor3 = Color3.fromRGB(22, 26, 36)
card.BackgroundTransparency = 0.1
card.Visible = false
card.Parent = gui
Instance.new("UICorner", card).CornerRadius = UDim.new(0.08, 0)
local limits = Instance.new("UISizeConstraint")
limits.MinSize = Vector2.new(240, 130)
limits.MaxSize = Vector2.new(420, 220)
limits.Parent = card
local lines = {}
for i = 1, 4 do
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position = UDim2.fromScale(0.05, 0.05 + (i - 1) * 0.23)
	t.Size = UDim2.fromScale(0.9, i == 1 and 0.22 or 0.2)
	t.TextColor3 = i == 1 and Color3.fromRGB(255, 220, 120) or Color3.new(1, 1, 1)
	t.TextScaled = true
	t.TextWrapped = true
	t.Font = Enum.Font.GothamBold
	t.TextXAlignment = Enum.TextXAlignment.Right
	t.Parent = card
	lines[i] = t
end

local openId = 0
btn.Activated:Connect(function()
	if card.Visible then
		card.Visible = false
		return
	end
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	local help = HELP[root and areaAt(root.Position) or "campus"] or HELP.campus
	for i, t in ipairs(lines) do
		t.Text = help[i] or ""
	end
	card.Visible = true
	card.BackgroundTransparency = 1
	TweenService:Create(card, TweenInfo.new(0.2), { BackgroundTransparency = 0.1 }):Play()
	if _G.BSCPlay then
		_G.BSCPlay("click")
	end
	openId += 1
	local my = openId
	task.delay(9, function() -- it tidies itself away
		if my == openId then
			card.Visible = false
		end
	end)
end)
