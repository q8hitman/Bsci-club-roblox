-- Light Microscopy lab content (v41). Shared so the client can draw it; the notebook is graded on the server.
-- An educational simulation, simplified: drawings are representative (not photos) and cell sizes are kept in true
-- proportion to each other but drawn larger than life so they stay readable. Needs review by a lab instructor.
local M = {}

M.OCULAR = 10 -- eyepiece magnification: total = ocular x objective

-- objectives: field-of-view width in sim units (true 1 : 0.4 : 0.1 : 0.04 ratio), depth of field, good light range
M.OBJECTIVES = {
	{ mag = 4, fov = 2000, dof = 12, light = { 3, 5 } },
	{ mag = 10, fov = 800, dof = 6, light = { 4, 6 } },
	{ mag = 40, fov = 200, dof = 2.2, light = { 6, 8 } },
	{ mag = 100, fov = 80, dof = 1.1, light = { 7, 9 }, oil = true },
}

M.PARTS = {
	{ ar = "العدسة العينية", en = "Eyepiece (ocular)", fn = "تكبّر 10× وتنظر منها" },
	{
		ar = "العدسات الشيئية",
		en = "Objective lenses",
		fn = "4× و10× و40× و100× زيت. التكبير الكلي = العينية × الشيئية",
	},
	{
		ar = "القرص الدوّار",
		en = "Revolving nosepiece",
		fn = "يبدّل بين العدسات بالترتيب، ومن 100× يرجع لـ4× مباشرة",
	},
	{
		ar = "المنصة والماسكات",
		en = "Stage and clips",
		fn = "تثبّت الشريحة وتحرّكها يمين ويسار وفوق وتحت",
	},
	{
		ar = "الضابط الكبير",
		en = "Coarse focus",
		fn = "تركيز سريع، للتكبير الصغير بس (4× و10×)",
	},
	{
		ar = "الضابط الدقيق",
		en = "Fine focus",
		fn = "تركيز دقيق، الوحيد المسموح مع 40× و100×",
	},
	{
		ar = "المكثّف والحجاب القزحي",
		en = "Condenser and iris diaphragm",
		fn = "يتحكم بكمية الضوء والتباين، ويفيد مع العينات الشفافة",
	},
	{
		ar = "زيت الغمر",
		en = "Immersion oil",
		fn = "نقطة بين الشريحة والعدسة 100×، معامل انكسارها قريب من الزجاج فتمنع تشتت الضوء وترفع قوة التمييز",
	},
}

-- samples: what the player must see (needMag) and the notebook choices (good = true observations)
M.SAMPLES = {
	{
		id = "blood",
		ar = "مسحة دم بشري (مصبوغة)",
		en = "Human blood smear (stained)",
		needMag = 40,
		notes = {
			{ "خلايا دم حمراء قرصية مقعرة الوجهين بدون نواة", true },
			{ "خلايا دم بيضاء أكبر وفيها نواة ملوّنة بنفسجي", true },
			{
				"صفائح دموية تبان كشظايا أو نقاط صغيرة جداً بين الخلايا",
				true,
			},
			{
				"خلايا دم حمراء فيها نواة",
				false,
				"خلايا الدم الحمراء عند الإنسان ما فيها نواة",
			},
			{
				"جدار خلوي حول كل خلية",
				false,
				"الجدار الخلوي للنبات، مو لخلايا الدم",
			},
		},
	},
	{
		id = "elodea",
		ar = "ورقة نبات الإيلوديا",
		en = "Elodea leaf",
		needMag = 40,
		notes = {
			{ "خلايا مستطيلة متراصة لها جدار خلوي", true },
			{ "بلاستيدات خضراء كثيرة داخل الخلايا", true },
			{
				"خلايا دائرية بدون جدار",
				false,
				"خلايا النبات لها جدار خلوي يعطيها شكل منتظم",
			},
			{ "سوط طويل يحرّك الخلية", false, "خلايا الورقة ما لها سوط" },
		},
	},
	{
		id = "cheek",
		ar = "خلايا بطانة الخد (أزرق الميثيلين)",
		en = "Cheek cells (methylene blue)",
		needMag = 40,
		notes = {
			{ "خلايا مسطحة شكلها غير منتظم", true },
			{ "نواة واضحة ملوّنة بالأزرق", true },
			{ "ما في جدار خلوي", true },
			{
				"بلاستيدات خضراء",
				false,
				"الخلايا الحيوانية ما فيها بلاستيدات خضراء",
			},
			{
				"جدار خلوي سميك",
				false,
				"الخلايا الحيوانية لها غشاء بس، بدون جدار",
			},
		},
	},
	{
		id = "staph",
		ar = "بكتيريا كروية (صبغة جرام)",
		en = "Cocci bacteria (Gram stain)",
		needMag = 100,
		notes = {
			{ "خلايا كروية صغيرة جداً متجمعة مثل العناقيد", true },
			{ "لونها بنفسجي، يعني موجبة الجرام", true },
			{ "بدون نواة حقيقية (بدائيات النوى)", true },
			{
				"خلايا كبيرة فيها نواة",
				false,
				"البكتيريا بدائيات نوى، ما لها نواة حقيقية",
			},
			{
				"تبان واضحة بتكبير 4×",
				false,
				"البكتيريا صغيرة جداً، تحتاج 100× مع الزيت",
			},
		},
	},
}

M.REWARD = { research = 6, coins = 5 }
M.COOLDOWN = 10 * 60 -- per sample, per player

return M
