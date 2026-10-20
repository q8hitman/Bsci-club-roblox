-- Shared definitions for progression: achievements (each can grant a title), trails sold for coins,
-- collectibles (campus cats + one specimen card per specialty) and the audio used by the client.
-- Facts are short and checked against standard references (see docs in the project notes).
local P = {}

P.Achievements = {
	{
		id = "first",
		ar = "أول خطوة",
		desc = "خلّص أول مرحلة باركور",
		coins = 10,
		title = "مبتدئ باركور",
	},
	{
		id = "z1",
		ar = "بيولوجيا نبات ✔",
		desc = "خلّص منطقة بيولوجيا نبات",
		coins = 25,
		title = "صديق النبات 🌿",
	},
	{
		id = "z2",
		ar = "بيولوجيا حيوان ✔",
		desc = "خلّص منطقة بيولوجيا حيوان",
		coins = 25,
		title = "حارس الحيوانات 🐢",
	},
	{
		id = "z3",
		ar = "مايكروبيولوجي ✔",
		desc = "خلّص منطقة مايكروبيولوجي",
		coins = 25,
		title = "صياد الميكروبات 🦠",
	},
	{
		id = "z4",
		ar = "بايوكيمستري ✔",
		desc = "خلّص منطقة بايوكيمستري",
		coins = 25,
		title = "سيد الإنزيمات ⚗️",
	},
	{
		id = "z5",
		ar = "مولكلر ✔",
		desc = "خلّص منطقة مولكلر",
		coins = 25,
		title = "فاك شفرة DNA 🧬",
	},
	{
		id = "z6",
		ar = "الزراعة ✔",
		desc = "خلّص منطقة الزراعة",
		coins = 25,
		title = "مزارع العلوم 🌴",
	},
	{
		id = "z7",
		ar = "الأدلة الجنائية ✔",
		desc = "خلّص منطقة الأدلة الجنائية",
		coins = 25,
		title = "المحقق الجنائي 🔎",
	},
	{
		id = "z8",
		ar = "البايوتكنولوجي ✔",
		desc = "خلّص منطقة البايوتكنولوجي",
		coins = 25,
		title = "عالم البايوتكنولوجي 🧪",
	},
	{
		id = "finish",
		ar = "بطل المئة",
		desc = "وصلت المرحلة 100",
		coins = 100,
		title = "أسطورة BSC 🏆",
	},
	{
		id = "cats",
		ar = "صديق القطاوة",
		desc = "لقيت كل قطاوة العلوم",
		coins = 50,
		title = "صديق القطاوة 🐱",
	},
	{
		id = "specimens",
		ar = "جامع العينات",
		desc = "جمعت عيّنة كل تخصص",
		coins = 50,
		title = "عالم ميداني 🔬",
	},
	{
		id = "quiz10",
		ar = "الدافور",
		desc = "جاوبت 10 أسئلة صح بركن الأسئلة",
		coins = 20,
		title = "الدافور 📚",
	},
	{
		id = "cart",
		ar = "رحلة التخصصات الكاملة 🚆",
		desc = "خلّصت رحلة قطار التخصصات",
		coins = 30,
		title = "مسافر القطار 🚆",
	},
	{
		id = "train",
		ar = "رحلة داخل الخلية",
		desc = "ركبت قطار الخلية للنهاية",
		coins = 10,
	},
	{
		id = "speed",
		ar = "سريع كالبرق",
		desc = "خلّصت منطقة كاملة بأقل من 4 دقايق",
		coins = 30,
		title = "سريع كالبرق ⚡",
	},
	{ id = "summit", ar = "قمة المقر", desc = "وصلت قمة تحدي المقر", coins = 10 },
	{
		id = "grad",
		ar = "حفل التخرج",
		desc = "أخذت صورة التخرج عند الشراع",
		coins = 15,
		title = "خريج العلوم 🎓",
	},
	{
		id = "golden",
		ar = "القطوة الذهبية",
		desc = "لقيت المكان السري",
		coins = 50,
		title = "مكتشف الأسرار 🗝️",
	},
	{
		id = "virus_survive",
		ar = "مناعة حديد",
		desc = "نجيت لين نهاية جولة الفيروس",
		coins = 20,
		title = "مناعة حديد 💪",
	},
	{
		id = "virus_zero",
		ar = "المريض صفر",
		desc = "عديت الكل وأنت الفيروس",
		coins = 20,
		title = "المريض صفر 🦠",
	},
	{
		id = "daily",
		ar = "تحدي اليوم",
		desc = "خلّصت منطقة تحدي اليوم كاملة",
		coins = 0,
	},
	{
		id = "exam",
		ar = "نجحت بالاختبار",
		desc = "نجيت لين آخر سؤال بقاعة الاختبارات",
		coins = 20,
		title = "طالب امتياز A+ 🎓",
	},
	{
		id = "arcade",
		ar = "بطل الألعاب",
		desc = "فزت بجولة في محطة الألعاب",
		coins = 10,
		title = "ملك الفوضى 🎮",
	},
}

-- v45 achievements are cosmetic; existing activity coin/research rewards stay unchanged.
for _, a in ipairs({
	{
		id = "arcade_play",
		ar = "زائر الأركيد",
		desc = "أكمل جولة أركيد",
		coins = 0,
		title = "رفيق الأركيد 🎮",
	},
	{
		id = "lab_first",
		ar = "أول تجربة",
		desc = "أنجز تجربة مختبر صحيحة تستحق مكافأة",
		coins = 0,
		title = "باحث مبتدئ 🔬",
	},
	{
		id = "show_first",
		ar = "أهلًا بالمتسابق",
		desc = "شارك بإجابة في حلقة Game Show حتى نهايتها",
		coins = 0,
		title = "نجم الاستوديو 🎤",
	},
	{
		id = "explorer5",
		ar = "مستكشف العوالم",
		desc = "زُر 5 عوالم مختلفة",
		coins = 0,
		title = "مستكشف BSC 🧭",
	},
	{
		id = "passport5",
		ar = "جواز المستوى الخامس",
		desc = "اجمع 400 XP في الجواز",
		coins = 0,
		title = "رحّالة العلوم ✨",
	},
}) do
	table.insert(P.Achievements, a)
end

table.insert(P.Achievements, {
	id = "museum8",
	ar = "دليل متحف الأحياء",
	desc = "أكمل المعروضات الثماني في المتحف",
	coins = 0,
	title = "دليل الاكتشاف 🔬",
})

table.insert(P.Achievements, {
	id = "racer2",
	ar = "متسابق العالم المجهري",
	desc = "أنهِ ثلاث لفات في كلتا حلبتي Micro Racers",
	coins = 0,
	title = "سائق الجزيئات 🏁",
})

table.insert(P.Achievements, {
	id = "laser48",
	ar = "الهروب الآمن",
	desc = "أكمل غرف Laser Escape الخمس",
	coins = 0,
	title = "خبير التوقيت ✨",
})

table.insert(P.Achievements, {
	id = "puzzle_master",
	ar = "حلّال الألغاز",
	desc = "حلّ غرفة التحكم بالخلية في غرف الألغاز",
	coins = 0,
	title = "خبير الألغاز 🧩",
})

P.Trails = {
	{
		id = "leaf",
		ar = "أثر الأوراق 🌿",
		price = 40,
		colors = { Color3.fromRGB(120, 210, 110), Color3.fromRGB(220, 240, 120) },
	},
	{
		id = "micro",
		ar = "أثر الميكروب 🦠",
		price = 60,
		colors = { Color3.fromRGB(240, 140, 170), Color3.fromRGB(200, 160, 240) },
	},
	{
		id = "dna",
		ar = "أثر الـ DNA 🧬",
		price = 80,
		colors = { Color3.fromRGB(255, 90, 170), Color3.fromRGB(60, 220, 255) },
	},
	{
		id = "club",
		ar = "ألوان النادي 💚",
		price = 100,
		colors = { Color3.fromRGB(24, 120, 80), Color3.fromRGB(250, 250, 248) },
	},
	{
		id = "gold",
		ar = "الأثر الذهبي ✨",
		price = 150,
		colors = { Color3.fromRGB(255, 210, 80), Color3.fromRGB(255, 250, 220) },
	},
	{
		id = "rainbow",
		ar = "قوس الشعار 🌈",
		price = 200,
		colors = {
			Color3.fromRGB(250, 222, 170),
			Color3.fromRGB(205, 232, 60),
			Color3.fromRGB(220, 165, 238),
			Color3.fromRGB(160, 218, 236),
			Color3.fromRGB(232, 150, 166),
		},
	},
}

-- campus cats: the College of Science really has many. Each one has a name and a light, true fact.
P.Cats = {
	c1 = { name = "مشمش", text = "القطط تنام تقريباً 12–16 ساعة باليوم 😴" },
	c2 = { name = "زعفران", text = "مجموعة القطط تسمّى بالإنجليزي clowder 🐾" },
	c3 = { name = "كتكوت", text = "القطة تقدر تلف أذنها تقريباً 180 درجة 👂" },
	c4 = {
		name = "دكتورة لولو",
		text = "القطط تشوف بالإضاءة الخافتة أحسن منّا بكثير 🌙",
	},
	c5 = {
		name = "رئيس النادي",
		text = "القطط تخرخر بتردد منخفض تقريباً 25–150 هرتز 😺",
	},
	c6 = { name = "بسكوت", text = "القطط تمشي على أطراف أصابعها (Digitigrade) 🐈" },
	c7 = {
		name = "نجمة",
		text = "شوارب القطة تساعدها تحس بالمسافات والأماكن الضيقة ✨",
	},
	c8 = {
		name = "صحراوي",
		text = "القط الرملي يعيش بصحاري الجزيرة العربية ويتحمل الحر 🏜️",
	},
	c9 = {
		name = "سائق القطار",
		text = "القطط عندها عضلات كثيرة بالأذن تخليها تلفها بسرعة 🚋",
	},
	c10 = {
		name = "كراج",
		text = "القطط تحب الأماكن الدافية… حتى جنب السيارات 🚗",
	},
	c11 = {
		name = "كركي",
		text = "لا تعطي القطط حليب بقر بكثرة: أغلبها ما تهضم اللاكتوز زين ☕",
	},
	c12 = {
		name = "المتسلّقة",
		text = "القطط تطيح على رجولها بفضل منعكس التعديل (righting reflex) 🧗",
	},
}

-- one specimen card per specialty, hidden just off the parkour route of each zone
P.Specimens = {
	s1 = {
		ar = "عيّنة النبات 🌿",
		text = "النباتات تطلق الأكسجين كناتج للبناء الضوئي",
	},
	s2 = {
		ar = "عيّنة الحيوان 🐢",
		text = "قلب الإنسان فيه أربع حجرات: أذينان وبطينان",
	},
	s3 = {
		ar = "عيّنة الميكروب 🦠",
		text = "بكتيريا E. coli ممكن تنقسم كل 20 دقيقة تقريباً بالظروف المثالية",
	},
	s4 = {
		ar = "عيّنة الإنزيم ⚗️",
		text = "الإنزيمات تسرّع التفاعلات بدون ما تُستهلك فيها",
	},
	s5 = {
		ar = "عيّنة الـ DNA 🧬",
		text = "DNA الخلية البشرية الواحدة لو انفرد طوله تقريباً مترين",
	},
	s6 = {
		ar = "عيّنة النخلة 🌴",
		text = "نخلة التمر من أكثر أشجار الفاكهة تحمّلاً لملوحة التربة",
	},
	s7 = {
		ar = "عيّنة البصمة 🔎",
		text = "البصمات تتكوّن قبل الولادة وتختلف حتى بين التوائم المتطابقة",
	},
	s8 = {
		ar = "عيّنة الإنسولين 🧪",
		text = "الإنسولين البشري يُنتج ببكتيريا معدّلة وراثياً من الثمانينات",
	},
}

P.CatCount = 12
P.SpecimenCount = 8
P.SpeedSeconds = 240

-- audio: Roblox-owned UI sounds and APM music licensed by Roblox for experiences (all verified in Studio)
P.Sounds = {
	checkpoint = 17208361335, -- Roblox GUI - Notification High
	coin = 127645268874265, -- CoinTransfer_01
	wrong = 17208353912, -- Roblox GUI - Negative
	click = 17208396156, -- Roblox GUI - Select
	collect = 17208204604, -- Roblox GUI - Bubble
	achievement = 17208327798, -- Roblox GUI - Aura
	purchase = 17208380755, -- Roblox GUI - Purchase
	whoosh = 15674975792, -- Roblox_UI_Whoosh_03
	sting = 9040172806, -- Small Discoveries (sting b)
}
P.Music = {
	hq = 1838583566, -- Happiness Is Brighter (No Piano)
	campus = 1843382633, -- Wonderful Day
	course = 1847245057, -- Energetic Chill A
	cart = 113554213644551, -- Fantastic Race
	cell = 1840776993, -- Science Mysteries
}

function P.achievement(id)
	for _, a in ipairs(P.Achievements) do
		if a.id == id then
			return a
		end
	end
	return nil
end

function P.trail(id)
	for _, t in ipairs(P.Trails) do
		if t.id == id then
			return t
		end
	end
	return nil
end

return P
