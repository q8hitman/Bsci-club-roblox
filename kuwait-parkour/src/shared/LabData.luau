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

-- research points per success, and per-experiment cooldown (seconds)
LabData.REWARD = { microscope = 4, gel = 4, pcr = 8 }
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
