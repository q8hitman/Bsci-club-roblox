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
LabData.GELS = {
	{ "150 bp", "900 bp", "3000 bp" },
	{ "200 bp", "1200 bp", "500 bp" },
	{ "4000 bp", "350 bp", "1500 bp" },
	{ "700 bp", "2500 bp", "100 bp" },
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
LabData.GRAM_ANSWERS = {
	pos = "موجبة الجرام (Gram-Positive) 🟣",
	neg = "سالبة الجرام (Gram-Negative) 🌸",
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
