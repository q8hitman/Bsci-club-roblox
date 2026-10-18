-- Science Challenge Center UI: level picker per specialty, question cards with an explanation after every answer,
-- and a results card. The server (QuizCenter.server) owns questions, answers and rewards.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local openEvent = ReplicatedStorage:WaitForChild("QuizCenterOpen", 30)
local fn = ReplicatedStorage:WaitForChild("QuizCenter", 30)
if not (openEvent and fn) then
	return
end

local NAVY = Color3.fromRGB(28, 44, 78)
local PAPER = Color3.fromRGB(246, 247, 250)
local INK = Color3.fromRGB(30, 36, 48)
local GOOD = Color3.fromRGB(46, 160, 90)
local BAD = Color3.fromRGB(200, 70, 70)
local OPT = Color3.fromRGB(70, 100, 170)

local function play(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

local gui = Instance.new("ScreenGui")
gui.Name = "QuizCenterPanel"
gui.ResetOnSpawn = false
gui.DisplayOrder = 45
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local function corner(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r or 0.04, 0)
	c.Parent = o
end

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.52)
panel.Size = UDim2.fromScale(0.6, 0.72)
panel.BackgroundColor3 = PAPER
panel.Parent = gui
corner(panel)
local sizeC = Instance.new("UISizeConstraint")
sizeC.MinSize = Vector2.new(340, 300)
sizeC.Parent = panel

local header = Instance.new("TextLabel")
header.Size = UDim2.fromScale(1, 0.12)
header.BackgroundColor3 = NAVY
header.TextColor3 = Color3.new(1, 1, 1)
header.TextScaled = true
header.Font = Enum.Font.GothamBold
header.Parent = panel
corner(header, 0.25)

local body = Instance.new("Frame")
body.Position = UDim2.fromScale(0.04, 0.15)
body.Size = UDim2.fromScale(0.92, 0.73)
body.BackgroundTransparency = 1
body.Parent = panel

local closeBtn = Instance.new("TextButton")
closeBtn.AnchorPoint = Vector2.new(0.5, 1)
closeBtn.Position = UDim2.fromScale(0.5, 0.98)
closeBtn.Size = UDim2.fromScale(0.3, 0.075)
closeBtn.BackgroundColor3 = Color3.fromRGB(150, 50, 60)
closeBtn.TextColor3 = Color3.new(1, 1, 1)
closeBtn.TextScaled = true
closeBtn.Font = Enum.Font.GothamBold
closeBtn.Text = "إغلاق"
closeBtn.Parent = panel
corner(closeBtn, 0.3)

local view = 0 -- bumps on every redraw so late server replies never draw over a newer screen
local function clear()
	view += 1
	for _, c in ipairs(body:GetChildren()) do
		c:Destroy()
	end
	return view
end

local function text(str, pos, sz, color, bold)
	local t = Instance.new("TextLabel")
	t.Position = pos
	t.Size = sz
	t.BackgroundTransparency = 1
	t.TextColor3 = color or INK
	t.TextScaled = true
	t.TextWrapped = true
	t.Font = bold and Enum.Font.GothamBold or Enum.Font.Gotham
	t.Text = str
	t.Parent = body
	return t
end

local function button(str, pos, sz, color, onClick)
	local b = Instance.new("TextButton")
	b.Position = pos
	b.Size = sz
	b.BackgroundColor3 = color
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.Text = str
	b.AutoButtonColor = true
	b.Parent = body
	corner(b, 0.2)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0.03, 0)
	pad.PaddingRight = UDim.new(0.03, 0)
	pad.Parent = b
	b.Activated:Connect(onClick)
	return b
end

local function close()
	clear()
	gui.Enabled = false
	task.spawn(fn.InvokeServer, fn, "quit")
end
closeBtn.Activated:Connect(close)

local showLevels, showQuestion

local function stars(n, per)
	return string.rep("★", n) .. string.rep("☆", per - n)
end

local function showResult(spec, r)
	clear()
	local pct = r.correct / r.of
	text(
		pct == 1 and "🏆 علامة كاملة!"
			or pct >= 0.6 and "👏 أداء ممتاز"
			or "💪 حاول مرة ثانية",
		UDim2.fromScale(0, 0),
		UDim2.fromScale(1, 0.16),
		NAVY,
		true
	)
	text(
		("%d / %d   %s"):format(r.correct, r.of, stars(r.correct, r.of)),
		UDim2.fromScale(0, 0.18),
		UDim2.fromScale(1, 0.14),
		Color3.fromRGB(200, 150, 20),
		true
	)
	local lines = {}
	if r.rewarded then
		table.insert(lines, ("+%d 💰   +%d 🧪 نقاط بحث"):format(r.coins, r.rp))
	else
		table.insert(lines, "جولة تدريب (الجوائز كل 20 ثانية)")
	end
	if r.improved then
		table.insert(lines, "⭐ رقم قياسي جديد لك بهالمستوى!")
	end
	if r.unlocked then
		table.insert(lines, "🔓 انفتح المستوى: " .. r.unlocked)
	end
	text(table.concat(lines, "\n"), UDim2.fromScale(0, 0.36), UDim2.fromScale(1, 0.3), INK, false)
	button("🔁 العب مرة ثانية", UDim2.fromScale(0.05, 0.75), UDim2.fromScale(0.42, 0.17), OPT, function()
		showLevels(spec)
	end)
	button("✅ خلاص", UDim2.fromScale(0.53, 0.75), UDim2.fromScale(0.42, 0.17), GOOD, close)
	play(pct >= 0.6 and "achievement" or "click")
end

function showQuestion(spec, q)
	local my = clear()
	if q.title then
		header.Text = "📝 " .. q.title
	end
	text(
		("السؤال %d من %d%s"):format(q.n, q.of, q.practice and "  • تدريب" or ""),
		UDim2.fromScale(0, 0),
		UDim2.fromScale(1, 0.07),
		Color3.fromRGB(110, 120, 140),
		false
	)
	text(q.q, UDim2.fromScale(0, 0.08), UDim2.fromScale(1, 0.2), INK, true)
	local buttons = {}
	local answered = false
	for k, o in ipairs(q.options) do
		local row, col = (k - 1) // 2, (k - 1) % 2
		buttons[k] = button(
			o,
			UDim2.fromScale(col * 0.51, 0.31 + row * 0.2),
			UDim2.fromScale(0.49, 0.17),
			OPT,
			function()
				if answered then
					return
				end
				answered = true
				local r = fn:InvokeServer("answer", q.token, k)
				if my ~= view or not r or r.error then
					return
				end
				for i, b in ipairs(buttons) do
					b.AutoButtonColor = false
					b.BackgroundColor3 = i == r.right and GOOD or (i == k and BAD or Color3.fromRGB(150, 156, 170))
				end
				play(r.ok and "coin" or "wrong")
				text(
					(r.ok and "✅ صح! " or "❌ غلط. ") .. r.why,
					UDim2.fromScale(0, 0.72),
					UDim2.fromScale(1, 0.16),
					r.ok and GOOD or BAD,
					false
				)
				button("التالي ⬅", UDim2.fromScale(0.3, 0.9), UDim2.fromScale(0.4, 0.1), NAVY, function()
					if r.summary then
						showResult(spec, r.summary)
					else
						showQuestion(spec, r.next)
					end
				end)
			end
		)
	end
end

function showLevels(spec)
	local my = clear()
	local m = fn:InvokeServer("menu")
	if my ~= view or not m then
		return
	end
	local info = m.specs[spec]
	header.Text = "🎓 " .. info.name
	text(
		("اختار المستوى. كل جولة %d أسئلة، وتحتاج %d صح عشان تفتح اللي بعده.\n🧪 %d نقاط بحث   💰 %d"):format(
			m.per,
			m.unlock,
			m.research,
			m.coins
		),
		UDim2.fromScale(0, 0),
		UDim2.fromScale(1, 0.18),
		INK,
		false
	)
	local colors = { GOOD, Color3.fromRGB(220, 150, 30), Color3.fromRGB(190, 60, 80) }
	for level, lv in ipairs(info.levels) do
		local y = 0.22 + (level - 1) * 0.25
		local label = #info.levels == 1 and "🧪 تحدي عملي (مسائل محسوبة)"
			or ("المستوى %d: %s"):format(level, lv.ar)
		local b = button(
			(lv.open and "" or "🔒 ") .. label .. "\n" .. stars(lv.best, m.per),
			UDim2.fromScale(0.1, y),
			UDim2.fromScale(0.8, 0.21),
			lv.open and colors[level] or Color3.fromRGB(150, 156, 170),
			function()
				if not lv.open then
					return
				end
				local mine = clear()
				local q = fn:InvokeServer("start", spec, level)
				if mine ~= view then
					return
				end
				if not q or q.error then
					text(
						q and q.error or "صار خطأ، جرّب مرة ثانية",
						UDim2.fromScale(0, 0.3),
						UDim2.fromScale(1, 0.2),
						BAD,
						true
					)
					return
				end
				showQuestion(spec, q)
			end
		)
		b.AutoButtonColor = lv.open
	end
end

openEvent.OnClientEvent:Connect(function(spec)
	if typeof(spec) ~= "number" then
		return
	end
	gui.Enabled = true
	header.Text = "🎓 مركز التحديات العلمية"
	play("click")
	showLevels(spec)
end)
