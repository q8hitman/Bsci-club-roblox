-- BSC Game Show: a studio quiz with two real formats (supervisor's plan, v40):
--   🖼️ Guess the picture: a big picture behind 25 cover tiles that fall away; answer early for more points.
--   📚 Category challenge: everyone votes a category on the pods, then a question from it (points by difficulty).
-- Solo or teams (2+ players are split Red/Blue). Answers are taps on the four pods (ProximityPrompts, phone-friendly).
-- A question closes as soon as everyone has answered; the long safety limit only stops an AFK player stalling the
-- show. Players who leave are dropped; if nobody is left the show stops. Rewards are server-side with a cooldown.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local Bank = require(script.Parent.GameShowBank)
local studio = workspace:WaitForChild("Map"):FindFirstChild("GameShowStudio", true)
if not studio then
	return
end

local function find(name)
	return studio:FindFirstChild(name)
end
local bounds = find("StudioBounds")
local mainScreen, scoreBoard = find("MainScreen"), find("ScoreBoard")
local teamScreens = { Red = find("TeamScreen|Red"), Blue = find("TeamScreen|Blue") }
local pictureBoard = find("PictureBoard")
local pods, covers = {}, {}
local podLights = {} -- v59 lit strip on each podium (tools/gameshow.py)
for i = 1, 4 do
	pods[i] = find("AnswerPod|" .. i)
	podLights[i] = find("PodLight|" .. i)
end
for i = 1, 25 do
	covers[i] = find("PictureCover|" .. i)
end

local LETTERS = { "A", "B", "C", "D" }
-- v59: "A) <Arabic>" rendered as "<Arabic>A)" (mixed direction); the Arabic text goes first, the pod letter after it
local function opt(i, text)
	return text .. "  •  " .. LETTERS[i]
end
local CATS = { "bio", "general", "games", "consoles" }
local ROUNDS = { "picture", "category", "memory", "picture", "category", "memory" }
local SAFETY = 40 -- seconds: only stops an AFK player from stalling everyone
local REWARD_COOLDOWN = 10 * 60

local function setText(part, text)
	local label = part and part:FindFirstChildWhichIsA("TextLabel", true)
	if label then
		label.Text = text
	end
end

local function notify(p, text, kind)
	local ev = ReplicatedStorage:FindFirstChild("Notify")
	if ev and p.Parent then
		ev:FireClient(p, text, kind)
	end
end

-- "Arabic (English)" on one line renders scrambled in Roblox: show the Arabic part only
local function clean(s)
	if s:find("[\216-\219]") then
		s = s:gsub("%s*%([%w%s%-%./#']+%)", "")
	end
	return s
end

local function inside(p)
	local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
	if not (root and bounds) then
		return false
	end
	local d = bounds.CFrame:PointToObjectSpace(root.Position)
	local h = bounds.Size / 2
	return math.abs(d.X) < h.X and math.abs(d.Y) < h.Y and math.abs(d.Z) < h.Z
end

local function playersInside()
	local list = {}
	for _, p in ipairs(Players:GetPlayers()) do
		if inside(p) then
			table.insert(list, p)
		end
	end
	return list
end

-- no repeats until a pool runs out
local used = {}
local function pick(pool, key, filter)
	used[key] = used[key] or {}
	local fresh = {}
	for i, item in ipairs(pool) do
		if not used[key][i] and (not filter or filter(item)) then
			table.insert(fresh, i)
		end
	end
	if #fresh == 0 then
		for i, item in ipairs(pool) do
			if not filter or filter(item) then
				used[key][i] = nil
				table.insert(fresh, i)
			end
		end
	end
	local i = fresh[math.random(1, #fresh)]
	used[key][i] = true
	return pool[i]
end

local function shuffledOptions(item)
	local opts = { item.right, item.wrong[1], item.wrong[2], item.wrong[3] }
	for i = 4, 2, -1 do
		local j = math.random(1, i)
		opts[i], opts[j] = opts[j], opts[i]
	end
	return opts, table.find(opts, item.right)
end

local show = nil -- running show state, or nil when idle
local rewardedAt = {}

local function scoreText()
	if not show then
		return "🏆"
	end
	if show.teams then
		return ("🔴 الأحمر %d    —    🔵 الأزرق %d"):format(show.teamScore.Red, show.teamScore.Blue)
	end
	local p = next(show.score)
	return ("⭐ النقاط: %d"):format(p and show.score[p] or 0)
end

local function refreshBoards()
	setText(scoreBoard, scoreText())
	for name, screen in pairs(teamScreens) do
		local lines = { name == "Red" and "🔴 الفريق الأحمر" or "🔵 الفريق الأزرق" }
		if show and show.teams then
			for p, t in pairs(show.team) do
				if t == name and p.Parent then
					table.insert(lines, ("%s  %d"):format(p.DisplayName, show.score[p] or 0))
				end
			end
		end
		setText(screen, table.concat(lines, "\n"))
	end
end

local function addPlayer(p)
	if show.score[p] then
		return
	end
	show.score[p] = 0
	if show.teams then
		local red, blue = 0, 0
		for _, t in pairs(show.team) do
			if t == "Red" then
				red += 1
			else
				blue += 1
			end
		end
		show.team[p] = red <= blue and "Red" or "Blue"
		notify(
			p,
			show.team[p] == "Red" and "🔴 إنت بالفريق الأحمر"
				or "🔵 إنت بالفريق الأزرق",
			"info"
		)
	end
end

-- active participants (still in the game and in the studio)
local function participants()
	local list = {}
	for p in pairs(show.score) do
		if p.Parent and inside(p) then
			table.insert(list, p)
		end
	end
	return list
end

-- collect answers until everyone answered (or the safety limit); returns answers[player] = {choice, at}
local function ask(onTick)
	show.answers, show.asking = {}, true
	local t0 = os.clock()
	show.askStart = t0
	while os.clock() - t0 < SAFETY do
		local list = participants()
		if #list == 0 then
			break
		end
		local all = true
		for _, p in ipairs(list) do
			if not show.answers[p] then
				all = false
			end
		end
		if all then
			break
		end
		if onTick then
			onTick(os.clock() - t0)
		end
		task.wait(0.25)
	end
	show.asking = false
	return show.answers
end

local function flashPods(correct)
	for i, pod in ipairs(pods) do
		if pod then
			local base = pod:GetAttribute("Base") or pod.Color
			pod:SetAttribute("Base", base)
			pod.Color = i == correct and Color3.fromRGB(120, 255, 160) or Color3.fromRGB(70, 70, 80)
			pod.Material = i == correct and Enum.Material.Neon or Enum.Material.SmoothPlastic
		end
	end
	for i, light in pairs(podLights) do
		local base = light:GetAttribute("Base") or light.Color
		light:SetAttribute("Base", base)
		light.Color = i == correct and Color3.fromRGB(120, 255, 160) or Color3.fromRGB(40, 40, 48)
	end
	task.delay(2.6, function()
		for _, light in pairs(podLights) do
			light.Color = light:GetAttribute("Base") or light.Color
		end
		for _, pod in ipairs(pods) do
			if pod then
				pod.Color = pod:GetAttribute("Base") or pod.Color
				pod.Material = Enum.Material.SmoothPlastic
			end
		end
	end)
end

local function settle(correct, pointsFor)
	flashPods(correct)
	local sfx = ReplicatedStorage:FindFirstChild("Sfx")
	for p, a in pairs(show.answers) do
		if p.Parent then
			if a.choice == correct then
				local pts = pointsFor(a)
				show.score[p] = (show.score[p] or 0) + pts
				if show.teams and show.team[p] then
					show.teamScore[show.team[p]] += pts
				end
				notify(p, ("✅ صح! +%d"):format(pts), "collect")
				if sfx then
					sfx:FireClient(p, "coin")
				end
			else
				notify(p, "❌ غلط! الجواب " .. LETTERS[correct], "wrong")
			end
		end
	end
	for _, p in ipairs(participants()) do
		if not show.answers[p] then
			notify(p, "⏳ ما جاوبت هالمرة", "info")
		end
	end
	refreshBoards()
	task.wait(3.2)
end

local function pictureRound(n)
	local item = pick(Bank.pictures, "pic")
	local opts, correct = shuffledOptions(item)
	setText(pictureBoard, item.pic)
	for _, c in ipairs(covers) do
		c.Transparency = 0
	end
	local order = {}
	for i = 1, #covers do
		order[i] = i
	end
	for i = #order, 2, -1 do
		local j = math.random(1, i)
		order[i], order[j] = order[j], order[i]
	end
	show.revealed = 0
	local lines = { ("🖼️ خمن الصورة • جولة %d/%d"):format(n, #ROUNDS) }
	for i, o in ipairs(opts) do
		table.insert(lines, opt(i, o))
	end
	setText(mainScreen, table.concat(lines, "\n"))
	local nextReveal = 1.2
	ask(function(t)
		while t >= nextReveal and show.revealed < #order do
			show.revealed += 1
			covers[order[show.revealed]].Transparency = 1
			if show.revealed % 2 == 0 then
				nextReveal += 1.5
			end
		end
	end)
	for _, c in ipairs(covers) do
		c.Transparency = 1
	end
	setText(mainScreen, "✅ الجواب: " .. opt(correct, item.right))
	settle(correct, function(a)
		return math.max(3, 10 - math.floor(a.at / 3)) -- the earlier, the more points
	end)
end

local function categoryRound(n)
	-- 1) vote a category on the pods
	local lines = { ("📚 تحدي الفئة • جولة %d/%d"):format(n, #ROUNDS), "اختاروا الفئة:" }
	for i, c in ipairs(CATS) do
		table.insert(lines, opt(i, Bank.categories[c]))
	end
	setText(mainScreen, table.concat(lines, "\n"))
	local votes = ask()
	local tally = { 0, 0, 0, 0 }
	for _, a in pairs(votes) do
		tally[a.choice] += 1
	end
	local best, bestN = math.random(1, 4), -1
	for i, v in ipairs(tally) do
		if v > bestN or (v == bestN and math.random() < 0.5) then
			best, bestN = i, v
		end
	end
	local cat = CATS[best]
	-- 2) the question
	local item = pick(Bank.questions, "q", function(q)
		return q.cat == cat
	end)
	local opts, correct = shuffledOptions(item)
	local q = { Bank.categories[cat] .. ("  •  صعوبة %d"):format(item.diff), clean(item.q) }
	for i, o in ipairs(opts) do
		table.insert(q, opt(i, clean(o)))
	end
	setText(mainScreen, table.concat(q, "\n"))
	task.wait(0.6)
	ask()
	setText(mainScreen, "✅ الجواب: " .. opt(correct, clean(item.right)))
	local pts = ({ 5, 8, 10 })[item.diff] or 5
	settle(correct, function()
		return pts
	end)
end

local function memoryRound(n)
	local item = pick(Bank.memory, "mem")
	local opts, correct = shuffledOptions(item)
	for _, c in ipairs(covers) do
		c.Transparency = 1
	end
	setText(pictureBoard, item.seq)
	setText(
		mainScreen,
		("🧠 تحدي الذاكرة والتسلسل • جولة %d/%d\nاحفظ السلسلة العلمية قبل ما تختفي! 👀\n%s"):format(
			n,
			#ROUNDS,
			item.seq
		)
	)
	task.wait(4.2)
	for _, c in ipairs(covers) do
		c.Transparency = 0
	end
	show.revealed = nil
	local lines = {
		("🧠 تحدي الذاكرة والتسلسل • جولة %d/%d"):format(n, #ROUNDS),
		clean(item.q),
	}
	for i, o in ipairs(opts) do
		table.insert(lines, opt(i, clean(o)))
	end
	setText(mainScreen, table.concat(lines, "\n"))
	ask()
	for _, c in ipairs(covers) do
		c.Transparency = 1
	end
	setText(mainScreen, ("✅ السلسلة: %s\nالجواب: %s"):format(item.seq, opt(correct, clean(item.right))))
	settle(correct, function(a)
		return math.max(5, 10 - math.floor((a.at or 0) / 4))
	end)
end

local function runShow(starter)
	local present = playersInside()
	show = { score = {}, team = {}, played = {}, teamScore = { Red = 0, Blue = 0 }, teams = #present >= 2 }
	table.sort(present, function(a, b)
		return a.UserId < b.UserId
	end)
	for _, p in ipairs(present) do
		addPlayer(p)
	end
	refreshBoards()
	setText(
		mainScreen,
		("🎙️ الحلقة بدأت! %s\nاضغطوا أو قفوا على المنصات A B C D للإجابة"):format(
			starter.DisplayName
		)
	)
	task.wait(3)
	for n, kind in ipairs(ROUNDS) do
		if #participants() == 0 then
			break
		end
		if kind == "picture" then
			pictureRound(n)
		elseif kind == "memory" then
			memoryRound(n)
		else
			categoryRound(n)
		end
	end
	-- results + rewards
	local winners = {}
	if show.teams then
		-- a tie rewards both teams (the old `x and nil or y` form always picked a winner)
		local w = if show.teamScore.Red == show.teamScore.Blue
			then nil
			elseif show.teamScore.Red > show.teamScore.Blue then "Red"
			else "Blue"
		for p, t in pairs(show.team) do
			if w == nil or t == w then
				table.insert(winners, p)
			end
		end
		setText(
			mainScreen,
			w
					and ((w == "Red" and "🔴 الفريق الأحمر" or "🔵 الفريق الأزرق") .. " فاز! 🎉")
				or "🤝 تعادل! الكل فايز"
		)
	else
		local p = next(show.score)
		if p and show.score[p] >= 20 then
			table.insert(winners, p)
		end
		setText(mainScreen, ("🎉 خلصت الحلقة! نقاطك %d"):format(p and show.score[p] or 0))
	end
	-- only players who answered at least once are rewarded (someone who walked out at the start gets nothing)
	local now = os.clock()
	for p in pairs(show.played) do
		local s = p.Parent and Profiles.state[p]
		if s and (not rewardedAt[p] or now - rewardedAt[p] > REWARD_COOLDOWN) then
			rewardedAt[p] = now
			local win = table.find(winners, p) ~= nil
			local coins = win and 13 or 3
			s.coins += coins
			Passport.complete(p, "show", { answered = show.played[p] == true, present = inside(p) })
			p:SetAttribute("Coins", s.coins)
			if win then
				s.research = (s.research or 0) + 2
				p:SetAttribute("Research", s.research)
			end
			notify(p, ("🎮 شكراً على المشاركة! +%d 💰"):format(coins), win and "ach" or "info")
		end
	end
	task.wait(6)
	show = nil
	setText(mainScreen, "🎮 BSC Game Show\nاضغط «ابدأ الحلقة» على مكتب المقدم")
	refreshBoards()
end

-- pods: tap OR step on a pod to answer (you can change your answer until the question closes)
local function selectPod(p, i)
	if not (show and show.asking and inside(p)) then
		return
	end
	addPlayer(p) -- late joiners join the show
	if show.answers[p] and show.answers[p].choice == i then
		return
	end
	local elapsed = show.revealed or math.max(0, os.clock() - (show.askStart or os.clock()))
	show.answers[p] = { choice = i, at = elapsed }
	show.played[p] = true
	notify(p, "اخترت " .. LETTERS[i], "info")
end

for i, pod in ipairs(pods) do
	if pod then
		local pr = Instance.new("ProximityPrompt")
		pr.ActionText = "اختار " .. LETTERS[i]
		pr.HoldDuration = 0
		pr.MaxActivationDistance = 12
		pr.RequiresLineOfSight = false
		pr.Parent = pod
		pr.Triggered:Connect(function(p)
			selectPod(p, i)
		end)
		pod.Touched:Connect(function(hit)
			local p = Players:GetPlayerFromCharacter(hit.Parent)
			if p then
				selectPod(p, i)
			end
		end)
	end
end

local desk = find("HostDesk")
if desk then
	local pr = Instance.new("ProximityPrompt")
	pr.ActionText = "ابدأ الحلقة"
	pr.ObjectText = "🎙️ BSC Game Show"
	pr.HoldDuration = 0.5
	pr.MaxActivationDistance = 12
	pr.RequiresLineOfSight = false
	pr.Parent = desk
	pr.Triggered:Connect(function(p)
		if show or not inside(p) then
			return
		end
		task.spawn(function()
			local ok, err = pcall(runShow, p)
			if not ok then
				warn("Game show failed: " .. tostring(err))
				show = nil
			end
		end)
	end)
end
for _, c in ipairs(covers) do
	c.Transparency = 1
end
setText(mainScreen, "🎮 BSC Game Show\nاضغط «ابدأ الحلقة» على مكتب المقدم")
refreshBoards()

-- v59 Studio-only QA hook (like ServerStorage.Labs54QA): lets tools/studio_tests/gameshow59 start a show and press the
-- same pod for every contestant at the same instant, to check a Red/Blue tie end to end. Never exists in a live server.
if game:GetService("RunService"):IsStudio() then
	local qa = Instance.new("BindableFunction")
	qa.Name = "GameShowQA"
	qa.OnInvoke = function(action, arg)
		if action == "start" and not show then
			task.spawn(function()
				local ok, err = pcall(runShow, arg)
				if not ok then
					warn("Game show failed: " .. tostring(err))
					show = nil
				end
			end)
			return true
		elseif action == "state" then
			return show
				and { asking = show.asking, red = show.teamScore.Red, blue = show.teamScore.Blue, teams = show.teams }
		elseif action == "answerAll" and show and show.asking then
			for _, p in ipairs(participants()) do
				selectPod(p, arg)
			end
			return true
		end
		return false
	end
	qa.Parent = game:GetService("ServerStorage")
end
