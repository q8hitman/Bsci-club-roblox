-- Exam Hall (قاعة الاختبارات): a group quiz show. Each question shows 4 answers on the screen; players stand on
-- zone A/B/C/D. When time runs out the floors under the wrong zones open. Survivors of the whole exam get a grade.
-- Questions come from Questions.luau (one bank per specialty); every question carries its own three wrong answers.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local Teleport = require(script.Parent.Teleport)
local Questions = require(script.Parent.Questions)
local History = require(script.Parent.QuestionHistory)
local notify = ReplicatedStorage:WaitForChild("Notify")
local hall = workspace:WaitForChild("Map"):WaitForChild("ExamHall")

local QUESTIONS_PER_EXAM = 8
local ANSWER_TIME = 12
local BREAK = 4

local screenLabel = hall.ExamScreen.Label.T
local zones, traps, boards = {}, {}, {}
for _, L in ipairs({ "A", "B", "C", "D" }) do
	zones[L] = hall:FindFirstChild("ExamZone|" .. L)
	traps[L] = hall:FindFirstChild("ExamTrap|" .. L)
	local b = hall:FindFirstChild("ExamLetter|" .. L)
	boards[L] = b and b:FindFirstChild("Label") and b.Label:FindFirstChild("T")
end
local HALF = zones.A and zones.A.Size.X / 2 or 13 -- zones are 28 wide since v31

-- the answer boards in front of the zones show "A) answer" during a question, just the letter otherwise
local function setBoards(answers)
	for i, L in ipairs({ "A", "B", "C", "D" }) do
		if boards[L] then
			boards[L].Text = answers and ("%s) %s"):format(L, answers[i]) or L
		end
	end
end
local spawn = hall:FindFirstChild("ExamSpawn")
local catch = hall:FindFirstChild("ExamPitCatch")
local hallCenter = hall.ExamFloor.Position

local sfx = ReplicatedStorage:WaitForChild("Sfx", 10)

local function inHall(player)
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if not root then
		return false
	end
	local d = root.Position - hallCenter
	return math.abs(d.X) < 72 and math.abs(d.Z - 0) < 95 and d.Y > -80 and d.Y < 50
end

local function zoneOf(player)
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if not root then
		return nil
	end
	for L, z in pairs(zones) do
		local d = root.Position - z.Position
		if math.abs(d.X) <= HALF and math.abs(d.Z) <= HALF and d.Y > -6 and d.Y < 10 then
			return L
		end
	end
	return nil
end

local function pickQuestions(players)
	local pool = {}
	for _, bank in ipairs(Questions) do
		for _, item in ipairs(bank.items) do
			table.insert(
				pool,
				{ q = item[1], right = item[2], wrong = { item[3], item[4], item[5] }, subject = bank.name }
			)
		end
	end
	-- v61: the questions the fewest players in the hall have already seen in any mode
	local out = History.pickMany(players, pool, QUESTIONS_PER_EXAM, function(it)
		return it.q
	end)
	return out
end

local function setScreen(text)
	screenLabel.Text = text
end

local function resetTraps()
	for _, t in pairs(traps) do
		t.CanCollide = true
		t.Transparency = 0
		local g = t:FindFirstChild("Label")
		if g then
			g.Enabled = true
		end
	end
end

local function sendBack(player)
	if spawn then
		Teleport.to(player, spawn, Vector3.new(math.random(-10, 10), 0, math.random(-6, 6)))
	end
end

-- anyone who falls into the retake pit goes back to the desks
task.spawn(function()
	while true do
		task.wait(0.3)
		for _, p in ipairs(Players:GetPlayers()) do
			local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
			if
				root
				and catch
				and math.abs(root.Position.X - catch.Position.X) < 80
				and math.abs(root.Position.Z - catch.Position.Z) < 60
				and root.Position.Y < catch.Position.Y + 30
				and root.Position.Y > catch.Position.Y - 40
			then
				sendBack(p)
			end
		end
	end
end)

local function runExam(players)
	local questions = pickQuestions(players)
	local alive = {}
	for _, p in ipairs(players) do
		alive[p] = true
	end
	for qi, item in ipairs(questions) do
		-- Count only questions actually displayed, including spectators currently in the hall.
		for _, p in ipairs(Players:GetPlayers()) do
			if inHall(p) then
				History.mark(p, item.q)
			end
		end
		-- shuffle the 4 answers written for this question: right + its 3 wrong answers
		local answers = { item.right, item.wrong[1], item.wrong[2], item.wrong[3] }
		for i = #answers, 2, -1 do
			local j = math.random(1, i)
			answers[i], answers[j] = answers[j], answers[i]
		end
		local letters = { "A", "B", "C", "D" }
		local rightLetter
		for i, a in ipairs(answers) do
			if a == item.right then
				rightLetter = letters[i]
			end
		end
		workspace:SetAttribute("ExamEnds", workspace:GetServerTimeNow() + ANSWER_TIME)
		workspace:SetAttribute("ExamQuestion", ("سؤال %d/%d • %s"):format(qi, #questions, item.subject))
		-- the client panel (IslandHUD) lists the question + the four options; the right letter never leaves the server
		workspace:SetAttribute("ExamText", item.q)
		for i, L in ipairs(letters) do
			workspace:SetAttribute("ExamOpt_" .. L, answers[i])
		end
		setBoards(answers)
		local qPrompt = ("❓ %s\nA) %s   B) %s\nC) %s   D) %s"):format(
			item.q,
			answers[1],
			answers[2],
			answers[3],
			answers[4]
		)
		setScreen(qPrompt)
		local committed = {} -- [Player] = locked answer letter 2s before floor drops
		for rem = ANSWER_TIME, 1, -1 do
			if rem == 2 then
				for p in pairs(alive) do
					if p.Parent and inHall(p) then
						committed[p] = zoneOf(p)
						if committed[p] then
							notify:FireClient(
								p,
								("🔒 تم قفل إجابتك على (%s)!"):format(committed[p]),
								"info"
							)
						else
							notify:FireClient(
								p,
								"⚠️ لم تقف داخل منطقة إجابة واضحة قبل القفل!",
								"wrong"
							)
						end
					end
				end
				setScreen(qPrompt .. "\n🔒 تم قفل الإجابات!")
			end
			task.wait(1)
		end
		-- open the wrong floors
		for L, t in pairs(traps) do
			if L ~= rightLetter then
				t.CanCollide = false
				t.Transparency = 0.8
				local g = t:FindFirstChild("Label")
				if g then
					g.Enabled = false
				end
			end
		end
		setScreen(("✅ الجواب الصح: %s) %s"):format(rightLetter, item.right))
		workspace:SetAttribute("ExamRight", rightLetter) -- revealed only after the answer time is over
		for p in pairs(alive) do
			local finalZone = zoneOf(p)
			local lockedZone = committed[p] or finalZone
			if not p.Parent or not inHall(p) or lockedZone ~= rightLetter or finalZone ~= rightLetter then
				alive[p] = nil
				if p.Parent then
					notify:FireClient(p, "📉 إجابة غلط… انتظر الاختبار الجاي", "wrong")
				end
			elseif sfx then
				sfx:FireClient(p, "click")
			end
		end
		task.wait(BREAK)
		resetTraps()
		workspace:SetAttribute("ExamRight", nil)
		local left = 0
		for _ in pairs(alive) do
			left += 1
		end
		if left == 0 then
			break
		end
	end
	local winners = {}
	for p in pairs(alive) do
		if p.Parent then
			table.insert(winners, p)
			local s = Profiles.state[p]
			if s then
				s.coins += 25
				p:SetAttribute("Coins", s.coins)
			end
			Passport.record(p, "exam", "pass")
			Passport.record(p, "activity", "exam")
			notify:FireClient(p, "🎓 نجحت بالاختبار! تقدير A+  (+25 💰)", "ach")
			if Profiles.award then
				Profiles.award(p, "exam")
			end
		end
	end
	local names = {}
	for _, p in ipairs(winners) do
		table.insert(names, p.DisplayName)
	end
	setScreen(
		#winners > 0 and ("🎓 الناجحين: " .. table.concat(names, "، "))
			or "📉 ما نجح أحد هالمرة… الاختبار الجاي أسهل؟ 😅"
	)
	workspace:SetAttribute("ExamQuestion", nil)
	workspace:SetAttribute("ExamText", nil)
	setBoards(nil)
	task.wait(6)
end

task.spawn(function()
	while true do
		local here = {}
		for _, p in ipairs(Players:GetPlayers()) do
			if inHall(p) then
				table.insert(here, p)
			end
		end
		if #here == 0 then
			setScreen(
				"📝 قاعة الاختبارات\nقف على الجواب الصح قبل لا يخلص الوقت"
			)
			task.wait(2)
		else
			for t = 10, 1, -1 do
				setScreen(
					("📝 الاختبار يبدأ بعد %d…\nامشوا لمنطقة الأجوبة قدام الشاشة"):format(
						t
					)
				)
				task.wait(1)
			end
			here = {}
			for _, p in ipairs(Players:GetPlayers()) do
				if inHall(p) then
					table.insert(here, p)
				end
			end
			if #here > 0 then
				local ok, err = pcall(runExam, here)
				if not ok then
					warn("Exam failed: " .. tostring(err))
				end
				resetTraps()
				setBoards(nil)
				for _, k in ipairs({ "ExamQuestion", "ExamText", "ExamRight" }) do
					workspace:SetAttribute(k, nil)
				end
			end
		end
	end
end)
