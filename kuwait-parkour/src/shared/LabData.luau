-- Research lab content (shared so the client can draw it; answers are checked on the server only).
local LabData = {}

-- Microscope: identify the cell type from what the slide shows. Each answer is one of: plant, animal, bacteria, fungus.
LabData.KINDS = {
	plant = "خلية نباتية 🌿",
	animal = "خلية حيوانية 🐾",
	bacteria = "بكتيريا 🦠",
	fungus = "فطر (خميرة) 🍄",
}
LabData.SLIDES = {
	{ "جدار خلوي + بلاستيدات خضراء + فجوة عصارية كبيرة", "plant" },
	{ "بدون جدار خلوي، نواة واضحة، وشكل غير منتظم", "animal" },
	{ "بدون نواة حقيقية، DNA دائري، وحجم صغير جداً", "bacteria" },
	{ "خلية بيضاوية تتكاثر بالتبرعم، وجدارها من الكايتين", "fungus" },
	{ "خلايا حارسة حول ثغر في بشرة ورقة", "plant" },
	{ "خلايا عصبية لها زوائد طويلة (محاور)", "animal" },
	{ "سوط واحد طويل وبلازميد صغير داخل الخلية", "bacteria" },
	{ "خيوط فطرية (هايفات) متفرعة", "fungus" },
}

-- Gel electrophoresis: DNA is negative and moves toward the + pole; SMALLER fragments travel FARTHER.
-- v53: a DNA size ladder (bp) and the unknown fragments a player has to size against it.
LabData.GEL_LADDER = { 100, 200, 500, 1000, 2000, 5000 }
LabData.GEL_UNKNOWNS = { 150, 250, 400, 700, 1500, 3000 }
-- distance from the wells as a fraction of the gel (0 = wells, 1 = far end): proportional to -log(size)
function LabData.gelDistance(bp)
	return math.clamp(1 - (math.log10(bp) - 1.8) / 2.1, 0.05, 0.95)
end

-- v53 PCR: the primer must pair (A-T, G-C) with the start of the template strand
LabData.PCR_TEMPLATE = "3'-TACGGATC…-5'"
LabData.PCR_PRIMERS = {
	{ seq = "5'-ATGCCTAG-3'", ok = true, why = "صح: كل A مقابل T وكل G مقابل C" },
	{ seq = "5'-TACGGATC-3'", ok = false, why = "هذا نفس شريط القالب، مو مكمّل له" },
	{
		seq = "5'-GATCCGTA-3'",
		ok = false,
		why = "هذا مقلوب: البادئ لازم يقابل القالب قاعدة بقاعدة",
	},
}

-- PCR: one cycle = denaturation (~95 °C) -> annealing (~55 °C) -> extension (~72 °C)
LabData.PCR_STEPS = {
	{ name = "فك الشريطين (Denaturation)", lo = 92, hi = 98 },
	{ name = "التصاق البادئات (Annealing)", lo = 50, hi = 60 },
	{ name = "الاستطالة (Extension)", lo = 68, hi = 76 },
}
LabData.PCR_CYCLES = 3

-- v50 Gram Staining (صبغة جرام): 4-step differential staining protocol + Gram+/Gram- identification
LabData.GRAM_STEPS = {
	{
		id = "cv",
		ar = "1️⃣ كريستال بنفسجي (Crystal Violet)",
		note = "الصبغة الأساسية: تلون جميع الخلايا بالبنفسجي",
	},
	{
		id = "iodine",
		ar = "2️⃣ محلول اليود (Gram's Iodine)",
		note = "المثبّت (Mordant): يكوّن معقد CV-I داخل الجدار الخلوي",
	},
	{
		id = "alcohol",
		ar = "3️⃣ الكحول المزيل للون (Alcohol Decolorizer)",
		note = "يزيل اللون من الجدار الرقيق (Gram-) ويبقى البنفسجي في الجدار السميك (Gram+)",
	},
	{
		id = "safranin",
		ar = "4️⃣ صبغة الصفرانين (Safranin Counterstain)",
		note = "صبغة مقابلة: تلون البكتيريا سالبة الجرام باللون الوردي/الأحمر",
	},
}
LabData.GRAM_SAMPLES = {
	{
		id = "staph",
		name = "مكورات عنقودية (Staphylococcus aureus)",
		shape = "كرويات في عناقيد • جدار ببتيدوغليكان سميك",
		gram = "pos",
		finalColor = "بنفسجي غامق (Violet) 🟣",
	},
	{
		id = "ecoli",
		name = "إشريكية قولونية (Escherichia coli)",
		shape = "عصيات قصيرة • طبقة ببتيدوغليكان رقيقة وغشاء خارجي",
		gram = "neg",
		finalColor = "وردي محمر (Pink/Red) 🌸",
	},
	{
		id = "bacillus",
		name = "عصوية رقيقة (Bacillus subtilis)",
		shape = "عصيات متسلسلة • جدار ببتيدوغليكان سميك يحتفظ بمعقد الصبغة",
		gram = "pos",
		finalColor = "بنفسجي غامق (Violet) 🟣",
	},
	{
		id = "pseudo",
		name = "زائفة زنجارية (Pseudomonas aeruginosa)",
		shape = "عصيات متحركة • غشاء خارجي دهني يفقد الكريستال بالكحول",
		gram = "neg",
		finalColor = "وردي محمر (Pink/Red) 🌸",
	},
}
-- v53 the decolouriser is the step that decides the result: seconds of alcohol before the water rinse.
-- Under min: the thin wall of Gram-negative cells still holds crystal violet (false Gram-positive).
-- Over max: even the thick wall of Gram-positive cells loses it (false Gram-negative). Real labs use ~5-15 s;
-- the window here is the same idea at game pace.
LabData.GRAM_DECOLOR = { min = 3.5, max = 8.5, bar = 12 }
LabData.GRAM_QUALITY = {
	ok = "✅ إزالة اللون مضبوطة: النتيجة موثوقة",
	under = "⚠️ إزالة لون قليلة: البكتيريا السالبة تبقى بنفسجية، فممكن تنخدع وتقول موجبة",
	over = "⚠️ إزالة لون زايدة: حتى الموجبة تفقد البنفسجي وتطلع وردية، فممكن تنخدع وتقول سالبة",
}
LabData.GRAM_ANSWERS = {
	pos = "🟣 موجبة الجرام\nGram-positive",
	neg = "🌸 سالبة الجرام\nGram-negative",
}

-- research points per success, and per-experiment cooldown (seconds)
LabData.REWARD = { microscope = 4, gel = 4, pcr = 8, gram = 6 }
LabData.COOLDOWN = 6

-- projects bought on the lab computer with research points; every one has a real effect in the game
LabData.UPGRADES = {
	{ id = "enzyme", ar = "إنزيم الطاقة ⚡", desc = "سرعة المشي +2", cost = 40 },
	{ id = "spring", ar = "بروتين القفز 🦘", desc = "قفزة أعلى قليلاً", cost = 60 },
	{
		id = "scope",
		ar = "مجهر الحقل 🔬",
		desc = "يكشف القطاوة والعيّنات القريبة",
		cost = 50,
	},
	{
		id = "mito",
		ar = "ميتوكوندريا الطاقة ⚡",
		desc = "+1 نقطة بحث إضافية بكل جولة ألعاب",
		cost = 45,
	},
}

return LabData
