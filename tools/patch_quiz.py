p = "kuwait-parkour/src/server/Main.server.luau"
s = open(p, encoding="utf-8").read()

s = s.replace("local Codes = require(script.Parent.Codes)\n",
              "local Codes = require(script.Parent.Codes)\nlocal Questions = require(script.Parent.Questions)\n", 1)

quiz = '''-- Quiz gates: every QUIZ_EVERY-th checkpoint only counts after a correct answer.
local QUIZ_EVERY = 5
local askEvent = Instance.new("RemoteEvent")
askEvent.Name = "QuizAsk"
askEvent.Parent = ReplicatedStorage
local answerFn = Instance.new("RemoteFunction")
answerFn.Name = "QuizAnswer"
answerFn.Parent = ReplicatedStorage

local pending = {} -- [Player] = { level, correct, token, sentAt }
local quizRng = Random.new()

local function buildQuestion(player, level)
	local bank = Questions[math.clamp(math.ceil(level / 10), 1, #Questions)]
	local item = bank.items[quizRng:NextInteger(1, #bank.items)]
	local order = { 1, 2, 3 }
	for i = 3, 2, -1 do
		local j = quizRng:NextInteger(1, i)
		order[i], order[j] = order[j], order[i]
	end
	local choices, correct = {}, 1
	for slot, which in ipairs(order) do
		choices[slot] = item[which + 1]
		if which == 1 then
			correct = slot
		end
	end
	local token = tostring(quizRng:NextInteger(1, 2 ^ 30))
	pending[player] = { level = level, correct = correct, token = token, sentAt = os.clock() }
	return { token = token, level = level, zone = bank.name, q = item[1], choices = choices }
end

local function askQuestion(player, level)
	local p = pending[player]
	if p and p.level == level and os.clock() - p.sentAt < 4 then
		return -- already showing; do not spam
	end
	askEvent:FireClient(player, buildQuestion(player, level))
end

answerFn.OnServerInvoke = function(player, token, choice)
	local p = pending[player]
	local s = state[player]
	if not (p and s) or token ~= p.token or typeof(choice) ~= "number" then
		return false, nil
	end
	if choice == p.correct then
		local level = p.level
		pending[player] = nil
		if level == s.stage + 1 then
			applyStage(player, level)
			s.coins += 5
			player:SetAttribute("Coins", s.coins)
		end
		return true, nil
	end
	return false, buildQuestion(player, p.level)
end

'''
assert "local function save(player)" in s
s = s.replace("local function save(player)", quiz + "local function save(player)", 1)

old = '''			if level and c and level == c.stage + 1 then
				applyStage(player, level)
			end'''
new = '''			if level and c and level == c.stage + 1 then
				if level % QUIZ_EVERY == 0 then
					askQuestion(player, level)
				else
					applyStage(player, level)
				end
			end'''
assert old in s
s = s.replace(old, new, 1)

old2 = "	state[player] = nil\n	lastTry[player] = nil"
assert old2 in s
s = s.replace(old2, old2 + "\n	pending[player] = nil", 1)
open(p, "w", encoding="utf-8").write(s)

pj = "kuwait-parkour/default.project.json"
j = open(pj, encoding="utf-8").read()
if '"Technology"' not in j:
    j = j.replace('"EnvironmentDiffuseScale": 0.5,', '"Technology": "Future",\n        "EnvironmentDiffuseScale": 0.5,', 1)
open(pj, "w", encoding="utf-8").write(j)
print("patched")
