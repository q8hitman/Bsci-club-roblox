-- Virtual practical challenges for the Science Challenge Center: every item is generated and its answer COMPUTED,
-- so there is nothing to memorise and nothing that can be wrong in a table. Same item shape as QuizBank:
-- { question, correct, wrongA, wrongB, wrongC, why }. make(rng) returns one item; the server asks 5 different kinds.
local P = {}

local function distinct(right, wrongs)
	local seen, out = { [right] = true }, {}
	for _, w in ipairs(wrongs) do
		if not seen[w] then
			seen[w] = true
			table.insert(out, w)
		end
	end
	return #out >= 3 and out or nil
end

-- 1) microscope magnification = eyepiece x objective
local function magnification(rng)
	local eye = ({ 10, 10, 15 })[rng:NextInteger(1, 3)]
	local obj = ({ 4, 10, 40, 100 })[rng:NextInteger(1, 4)]
	local right = eye * obj
	local w = distinct(tostring(right) .. "×", {
		tostring(eye + obj) .. "×",
		tostring(obj) .. "×",
		tostring(right * 10) .. "×",
		tostring(eye) .. "×",
	})
	return {
		("🔬 عدسة عينية %d× وعدسة شيئية %d×. كم قوة التكبير الكلية؟"):format(
			eye,
			obj
		),
		tostring(right) .. "×",
		w[1],
		w[2],
		w[3],
		("التكبير الكلي = العينية × الشيئية = %d × %d = %d×"):format(eye, obj, right),
	}
end

-- 2) complementary DNA strand
local PAIR = { A = "T", T = "A", G = "C", C = "G" }
local function complementary(rng)
	local bases = { "A", "T", "G", "C" }
	local seq, comp, rnaLike, swapped = {}, {}, {}, {}
	for i = 1, 6 do
		local b = bases[rng:NextInteger(1, 4)]
		seq[i] = b
		comp[i] = PAIR[b]
		rnaLike[i] = comp[i] == "T" and "U" or comp[i]
		swapped[i] = ({ A = "G", G = "A", T = "C", C = "T" })[comp[i]] -- purine/pyrimidine mix-up
	end
	local s, c = table.concat(seq), table.concat(comp)
	local w = distinct(c, { s, table.concat(rnaLike), table.concat(swapped), c:reverse() })
	if not w then
		return complementary(rng)
	end
	return {
		("🧬 السلسلة: 5′-%s-3′. شنو تسلسل السلسلة المكمّلة (DNA) من 3′ إلى 5′؟"):format(
			s
		),
		c,
		w[1],
		w[2],
		w[3],
		"A يرتبط مع T، وG يرتبط مع C. (الـ U موجود في RNA مو DNA)",
	}
end

-- 3) monohybrid cross: % of offspring with the recessive phenotype
local CROSSES = {
	{ "Aa × Aa", 25, "الاحتمالات: AA وAa وAa وaa، يعني واحد من 4 = 25%" },
	{ "Aa × aa", 50, "الاحتمالات: Aa وAa وaa وaa، يعني 2 من 4 = 50%" },
	{
		"AA × aa",
		0,
		"كل الأبناء Aa، فالصفة السائدة تظهر عندهم كلهم = 0% متنحية",
	},
	{ "aa × aa", 100, "الأبوين ما عندهم إلا a، فكل الأبناء aa = 100%" },
	{ "AA × Aa", 0, "كل ابن ياخذ A من الأب AA، فما يطلع aa أبداً = 0%" },
}
local function punnett(rng)
	local c = CROSSES[rng:NextInteger(1, #CROSSES)]
	local pool = {}
	for _, v in ipairs({ 0, 25, 50, 75, 100 }) do
		if v ~= c[2] then
			table.insert(pool, v .. "%")
		end
	end
	for i = #pool, 2, -1 do
		local j = rng:NextInteger(1, i)
		pool[i], pool[j] = pool[j], pool[i]
	end
	return {
		("🧫 مربع بانيت: تزاوج %s (A سائد). كم نسبة الأبناء اللي تظهر فيهم الصفة المتنحية؟"):format(
			c[1]
		),
		c[2] .. "%",
		pool[1],
		pool[2],
		pool[3],
		c[3],
	}
end

-- 4) dilution C1·V1 = C2·V2 (only combinations with a whole-number answer)
local DILUTIONS = {}
for _, c1 in ipairs({ 10, 20, 50, 100 }) do
	for _, c2 in ipairs({ 1, 2, 5 }) do
		for _, v2 in ipairs({ 50, 100, 200 }) do
			local v1 = c2 * v2 / c1
			if c2 < c1 and v1 == math.floor(v1) and v1 >= 1 then
				table.insert(DILUTIONS, { c1, c2, v2, v1 })
			end
		end
	end
end
local function dilution(rng)
	local d = DILUTIONS[rng:NextInteger(1, #DILUTIONS)]
	local c1, c2, v2, v1 = d[1], d[2], d[3], d[4]
	local w = distinct(v1 .. " mL", {
		(c1 * v2 / c2) .. " mL",
		(v2 - v1) .. " mL",
		(c2 * v2) .. " mL",
		(v1 * 2) .. " mL",
	})
	return {
		("⚗️ عندك محلول مخزون تركيزه %d mM. تبي %d mL بتركيز %d mM. كم mL تاخذ من المخزون؟"):format(
			c1,
			v2,
			c2
		),
		v1 .. " mL",
		w[1],
		w[2],
		w[3],
		("C1×V1 = C2×V2 ← V1 = %d×%d ÷ %d = %d mL، وتكمّل الباقي ماء"):format(c2, v2, c1, v1),
	}
end

-- 5) bacterial growth: doubling every 20 minutes
local function growth(rng)
	local n0 = ({ 10, 50, 100 })[rng:NextInteger(1, 3)]
	local hours = rng:NextInteger(1, 2)
	local gens = hours * 3
	local right = n0 * 2 ^ gens
	local w = distinct(tostring(right), {
		tostring(n0 * 2 ^ hours),
		tostring(n0 * gens * 2),
		tostring(right * 2),
		tostring(n0 * 2 ^ (gens - 1)),
	})
	return {
		("🦠 بكتيريا تتضاعف كل 20 دقيقة. بدأنا بـ %d خلية، كم تصير بعد %d ساعة؟"):format(
			n0,
			hours
		),
		tostring(right),
		w[1],
		w[2],
		w[3],
		("%d ساعة = %d أجيال، فالعدد = %d × 2^%d = %d"):format(hours, gens, n0, gens, right),
	}
end

P.KINDS = { magnification, complementary, punnett, dilution, growth }

-- five practical items, one of each kind, in random order
function P.session(rng)
	local order = { 1, 2, 3, 4, 5 }
	for i = #order, 2, -1 do
		local j = rng:NextInteger(1, i)
		order[i], order[j] = order[j], order[i]
	end
	local items = {}
	for _, k in ipairs(order) do
		table.insert(items, P.KINDS[k](rng))
	end
	return items
end

return P
