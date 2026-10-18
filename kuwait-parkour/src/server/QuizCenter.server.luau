-- مركز التحديات العلمية (Science Challenge Center): one kiosk per specialty (QuizKiosk|1..8) + the practical kiosk
-- (QuizKiosk|9). A session = 5 questions at level 1 (easy, Questions.luau), 2 or 3 (QuizBank.luau), or 5 generated
-- practical problems (QuizPractical). Level n+1 unlocks after 3/5 at level n. Answers, tokens, timing and rewards
-- live on the server; the client (QuizCenter.client) only shows what it is sent. Best scores persist in s.quiz.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Profiles = require(script.Parent.Profiles)
local Questions = require(script.Parent.Questions)
local QuizBank = require(script.Parent.QuizBank)
local Practical = require(script.Parent.QuizPractical)
local mapFolder = workspace:WaitForChild("Map")

local openEvent = Instance.new("RemoteEvent")
openEvent.Name = "QuizCenterOpen"
openEvent.Parent = ReplicatedStorage
local fn = Instance.new("RemoteFunction")
fn.Name = "QuizCenter"
fn.Parent = ReplicatedStorage

local PRACTICAL = #Questions + 1
local PER_SESSION = 5
local UNLOCK = 3 -- correct answers needed at level n to open level n+1
local MIN_ANSWER_TIME = 1.0 -- seconds; faster answers are treated as wrong (bots / remote spam)
local SESSION_COOLDOWN = 20 -- seconds between rewarded sessions
local LEVEL_AR = { "سهل", "متوسط", "متقدم" }

local state = Profiles.state
local rng = Random.new()
local sessions = {} -- [player] = { spec, level, items, i, correct, token, askedAt }
local lastSession = {} -- [player] = os.clock() of the last rewarded session

local function specName(spec)
	return spec == PRACTICAL and "🧪 التحديات العملية" or Questions[spec].name
end

local function levelsOf(spec)
	return spec == PRACTICAL and 1 or 3
end

local function best(s, spec, level)
	return (s.quiz or {})[spec .. ":" .. level] or 0
end

local function unlocked(s, spec, level)
	return level == 1 or best(s, spec, level - 1) >= UNLOCK
end

local function pickItems(spec, level)
	if spec == PRACTICAL then
		return Practical.session(rng)
	end
	local pool = level == 1 and Questions[spec].items or QuizBank[spec][level]
	local idx = {}
	for i = 1, #pool do
		idx[i] = i
	end
	for i = #idx, 2, -1 do
		local j = rng:NextInteger(1, i)
		idx[i], idx[j] = idx[j], idx[i]
	end
	local items = {}
	for k = 1, math.min(PER_SESSION, #pool) do
		table.insert(items, pool[idx[k]])
	end
	return items
end

-- the next question for the client: shuffled options, the correct index stays on the server
local function ask(sess)
	local item = sess.items[sess.i]
	local opts = { item[2], item[3], item[4], item[5] }
	local order = { 1, 2, 3, 4 }
	for i = 4, 2, -1 do
		local j = rng:NextInteger(1, i)
		order[i], order[j] = order[j], order[i]
	end
	local shown = {}
	for k, o in ipairs(order) do
		shown[k] = opts[o]
		if o == 1 then
			sess.right = k
		end
	end
	sess.token = tostring(rng:NextInteger(1, 2 ^ 30))
	sess.askedAt = os.clock()
	return { token = sess.token, n = sess.i, of = #sess.items, q = item[1], options = shown }
end

local function menu(s)
	local list = {}
	for spec = 1, PRACTICAL do
		local lv = {}
		for level = 1, levelsOf(spec) do
			lv[level] = { best = best(s, spec, level), open = unlocked(s, spec, level), ar = LEVEL_AR[level] }
		end
		list[spec] = { name = specName(spec), levels = lv }
	end
	return { specs = list, research = s.research or 0, coins = s.coins, per = PER_SESSION, unlock = UNLOCK }
end

local function finish(player, s, sess)
	sessions[player] = nil
	local key = sess.spec .. ":" .. sess.level
	s.quiz = s.quiz or {}
	local before = s.quiz[key] or 0
	local improved = sess.correct > before
	if improved then
		s.quiz[key] = sess.correct
	end
	-- rewards: coins per correct answer x level; research for a strong session (4+), bonus for perfect
	local coins, rp = 0, 0
	if sess.rewarded then
		coins = sess.correct * sess.level
		if sess.correct >= 4 then
			rp = sess.level * 2 + (sess.correct == PER_SESSION and 2 or 0)
		end
		s.coins += coins
		s.research = (s.research or 0) + rp
		player:SetAttribute("Coins", s.coins)
		player:SetAttribute("Research", s.research)
	end
	local unlockedNow = sess.level < levelsOf(sess.spec)
		and before < UNLOCK
		and sess.correct >= UNLOCK
		and LEVEL_AR[sess.level + 1]
	return {
		done = true,
		correct = sess.correct,
		of = #sess.items,
		coins = coins,
		rp = rp,
		rewarded = sess.rewarded,
		best = math.max(before, sess.correct),
		improved = improved,
		unlocked = unlockedNow or nil,
	}
end

fn.OnServerInvoke = function(player, action, a, b)
	local s = state[player]
	if not s or typeof(action) ~= "string" then
		return nil
	end
	if action == "menu" then
		return menu(s)
	elseif action == "start" then
		local spec, level = tonumber(a), tonumber(b)
		if not (spec and level and Questions[spec] or spec == PRACTICAL) then
			return { error = "bad" }
		end
		if not (level and level >= 1 and level <= levelsOf(spec) and level == math.floor(level)) then
			return { error = "bad" }
		end
		if not unlocked(s, spec, level) then
			return {
				error = ("يفتح هالمستوى لما تجيب %d من %d في المستوى اللي قبله"):format(
					UNLOCK,
					PER_SESSION
				),
			}
		end
		local now = os.clock()
		local rewarded = not lastSession[player] or now - lastSession[player] >= SESSION_COOLDOWN
		if rewarded then
			lastSession[player] = now
		end
		local sess = {
			spec = spec,
			level = level,
			items = pickItems(spec, level),
			i = 1,
			correct = 0,
			rewarded = rewarded,
		}
		sessions[player] = sess
		local q = ask(sess)
		q.title = ("%s • %s"):format(specName(spec), spec == PRACTICAL and "عملي" or LEVEL_AR[level])
		q.practice = not rewarded or nil
		return q
	elseif action == "answer" then
		local sess = sessions[player]
		if not sess or a ~= sess.token then
			return { error = "stale" }
		end
		sess.token = nil -- one answer per question
		local choice = tonumber(b)
		local tooFast = os.clock() - sess.askedAt < MIN_ANSWER_TIME
		local ok = choice == sess.right and not tooFast
		if ok then
			sess.correct += 1
		end
		local item = sess.items[sess.i]
		local res = {
			ok = ok,
			right = sess.right,
			why = item[6] or ("الإجابة الصحيحة: " .. item[2]),
			score = sess.correct,
		}
		sess.i += 1
		if sess.i > #sess.items then
			res.summary = finish(player, s, sess)
		else
			res.next = ask(sess)
		end
		return res
	elseif action == "quit" then
		sessions[player] = nil
		return { ok = true }
	end
	return nil
end

-- kiosks
for _, inst in ipairs(mapFolder:GetDescendants()) do
	local spec = inst:IsA("BasePart") and tonumber(inst.Name:match("^QuizKiosk|(%d+)$"))
	if spec and (Questions[spec] or spec == PRACTICAL) then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "ابدأ التحدي 📝"
		prompt.ObjectText = specName(spec)
		prompt.MaxActivationDistance = 10
		prompt.RequiresLineOfSight = false
		prompt.HoldDuration = 0
		prompt.Parent = inst
		prompt.Triggered:Connect(function(player)
			openEvent:FireClient(player, spec)
		end)
	end
end

Players.PlayerRemoving:Connect(function(player)
	sessions[player] = nil
	lastSession[player] = nil
end)
