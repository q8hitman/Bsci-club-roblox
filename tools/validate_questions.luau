-- Validates kuwait-parkour/src/server/Questions.luau (run: tools/lune/lune.exe run tools/validate_questions.luau)
-- Structural checks + a small list of known "second correct answer" traps found during review.
local process = require("@lune/process")
local Questions = require("../kuwait-parkour/src/server/Questions")

local errors, count = {}, 0
local function fail(where, msg)
	table.insert(errors, where .. ": " .. msg)
end
local function norm(s)
	return (s:gsub("^%s+", ""):gsub("%s+$", ""):lower())
end

-- if a question matches the pattern, none of these words may appear among its WRONG answers
-- (each is biologically correct for that kind of question)
local TRAPS = {
	{ q = "DNA", also = { "الميتوكوندريا", "البلاستيدات", "النواة", "الدم", "اللعاب", "الجلد", "العظم" } },
	{ q = "صغير الضفدع", also = { "اليرقة" } },
	{ q = "تلقّح الأزهار", also = { "البعوض", "الفراشات", "الخنافس", "الذباب" } },
	{ q = "تصنيع البروتين", also = { "الشبكة الإندوبلازمية الخشنة" } },
	{ q = "تمتصه النباتات في البناء الضوئي", also = { "الماء" } },
}

local seenQ = {}
for bi, bank in ipairs(Questions) do
	local where = "bank " .. bi
	if type(bank.name) ~= "string" or bank.name == "" then
		fail(where, "missing name")
	end
	if type(bank.items) ~= "table" or #bank.items < 3 then
		fail(where, "needs at least 3 questions")
		continue
	end
	for qi, item in ipairs(bank.items) do
		count += 1
		local w = ("%s (%s) q%d"):format(where, bank.name, qi)
		if #item ~= 5 then
			fail(w, ("expected 5 strings {q, right, wrong x3}, got %d"):format(#item))
			continue
		end
		for i = 1, 5 do
			if type(item[i]) ~= "string" or norm(item[i]) == "" then
				fail(w, "entry " .. i .. " is empty or not a string")
			end
		end
		local q = item[1]
		if not q:find("؟") and not q:find("%?") then
			fail(w, "question has no question mark: " .. q)
		end
		if seenQ[norm(q)] then
			fail(w, "duplicate question (also " .. seenQ[norm(q)] .. ")")
		end
		seenQ[norm(q)] = w
		local opts = {}
		for i = 2, 5 do
			local n = norm(item[i])
			if opts[n] then
				fail(w, "duplicate option: " .. item[i])
			end
			opts[n] = true
			if i > 2 and (n:find(norm(item[2]), 1, true) or norm(item[2]):find(n, 1, true)) then
				fail(w, ("wrong option '%s' overlaps the correct answer '%s'"):format(item[i], item[2]))
			end
		end
		for _, trap in ipairs(TRAPS) do
			if q:find(trap.q, 1, true) then
				for i = 3, 5 do
					for _, word in ipairs(trap.also) do
						if item[i]:find(word, 1, true) then
							fail(w, ("wrong option '%s' is actually correct for: %s"):format(item[i], q))
						end
					end
				end
			end
		end
	end
end

-- ------------------------------------------------------------ v30: challenge center bank (levels 2-3) + practicals
local QuizBank = require("../kuwait-parkour/src/server/QuizBank")
local Practical = require("../kuwait-parkour/src/server/QuizPractical")
local bankCount = 0
local function checkItem(w, item, needWhy)
	if #item ~= (needWhy and 6 or 5) then
		fail(w, ("expected %d strings, got %d"):format(needWhy and 6 or 5, #item))
		return
	end
	for i = 1, #item do
		if type(item[i]) ~= "string" or norm(item[i]) == "" then
			fail(w, "entry " .. i .. " is empty or not a string")
			return
		end
	end
	if not item[1]:find("؟") and not item[1]:find("%?") then
		fail(w, "question has no question mark: " .. item[1])
	end
	local opts = {}
	for i = 2, 5 do
		local n = norm(item[i])
		if opts[n] then
			fail(w, "duplicate option: " .. item[i])
		end
		opts[n] = true
	end
	for _, trap in ipairs(TRAPS) do
		if item[1]:find(trap.q, 1, true) then
			for i = 3, 5 do
				for _, word in ipairs(trap.also) do
					if item[i]:find(word, 1, true) then
						fail(w, ("wrong option '%s' is actually correct for: %s"):format(item[i], item[1]))
					end
				end
			end
		end
	end
end
if #QuizBank ~= #Questions then
	fail("QuizBank", ("has %d specialties, Questions has %d"):format(#QuizBank, #Questions))
end
for si, spec in ipairs(QuizBank) do
	for _, level in ipairs({ 2, 3 }) do
		local items = spec[level]
		local where = ("QuizBank %s L%d"):format(Questions[si] and Questions[si].name or tostring(si), level)
		if type(items) ~= "table" or #items < 5 then
			fail(where, "needs at least 5 questions (one full session)")
			continue
		end
		for qi, item in ipairs(items) do
			bankCount += 1
			local w = where .. " q" .. qi
			checkItem(w, item, true)
			if seenQ[norm(item[1])] then
				fail(w, "duplicate question (also " .. seenQ[norm(item[1])] .. ")")
			end
			seenQ[norm(item[1])] = w
		end
	end
end
-- practical generators: many random draws, every one must have 4 distinct options and a computed answer
local fakeRng = {}
function fakeRng:NextInteger(a, b)
	return math.random(a, b)
end
for run = 1, 400 do
	for k, make in ipairs(Practical.KINDS) do
		local ok, item = pcall(make, fakeRng)
		if not ok then
			fail("practical kind " .. k, "crashed: " .. tostring(item))
		else
			checkItem(("practical kind %d run %d"):format(k, run), item, true)
		end
	end
end
if #Practical.session(fakeRng) ~= 5 then
	fail("practical", "session must have 5 items")
end

if #errors > 0 then
	print(("FAILED: %d problem(s) in %d questions"):format(#errors, count))
	for _, e in ipairs(errors) do
		print("  - " .. e)
	end
	process.exit(1)
end
print(("OK: %d questions in %d banks, all with 1 correct + 3 distinct wrong answers"):format(count, #Questions))
print(("OK: challenge center %d questions (levels 2-3) + 5 practical generators x 400 draws"):format(bankCount))
