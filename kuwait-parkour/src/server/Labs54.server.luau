-- v54 hands-on wet lab (tools/labs54.py builds the benches). Players put on a lab coat, pick up real equipment, carry it
-- to the workstation and work through the experiment; every step changes the objects themselves, so other players can
-- watch. One player works a bench at a time (it frees itself when they finish, walk away or go idle).
--   Item|<id>  carried in the right hand (one at a time)     Slot|<id>  put an item down / apply a carried reagent
--   Use|<id>   interact (draw with the pipette, heat-fix, connect a lead, power on, start the cycler, look)
-- Results and rewards are decided here; the client (Bench54.client) only shows small overlays and toasts.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local LabData = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("LabData"))

local mapFolder = workspace:WaitForChild("Map")
local event = Instance.new("RemoteEvent")
event.Name = "Bench54"
event.Parent = ReplicatedStorage
local fn = Instance.new("RemoteFunction")
fn.Name = "Bench54Fn"
fn.Parent = ReplicatedStorage
local labOpen = ReplicatedStorage:WaitForChild("LabOpen", 30)

local NAMES = {
	slide = "شريحة عليها لطخة بكتيريا",
	cv = "كريستال بنفسجي",
	iodine = "محلول اليود",
	alcohol = "كحول مزيل للون",
	safranin = "صفرانين",
	water = "قنينة غسيل (ماء)",
	gel = "جل الأجاروز",
	buffer = "محلول منظم (TAE)",
	pipette = "ماصّة دقيقة",
	tube = "أنبوب PCR",
	slide_blood = "شريحة مسحة دم",
	slide_elodea = "شريحة ورقة إلوديا",
	slide_cheek = "شريحة خلايا الخد",
	slide_staph = "شريحة بكتيريا عنقودية",
	tray = "حامل الصبغ فوق المغسلة",
	stage = "منصة المجهر",
	mstage = "منصة المجهر",
	tank = "حوض الفصل الكهربائي",
	uv = "جهاز الأشعة فوق البنفسجية",
	rack = "حامل أنبوب PCR",
	cycler = "جهاز PCR الحراري",
	burner = "موقد بنسن",
	ladder = "سلّم الأحجام (Ladder)",
	sample = "عيّنة DNA مجهولة",
	postNear = "قطب عند الآبار",
	postFar = "قطب بالطرف البعيد",
	power = "مزوّد الطاقة",
	template = "DNA القالب",
	primers = "البادئات (Primers)",
	dntp = "نيوكليوتيدات (dNTPs)",
	pcrbuffer = "محلول PCR المنظم",
	taq = "إنزيم Taq بوليميريز",
	eyepiece = "عدسة المجهر",
	meyepiece = "عدسة المجهر",
	ppe = "معاطف المختبر والنظارات",
}
local ACTION = {
	burner = "ثبّت بالحرارة",
	ladder = "اسحب بالماصّة",
	sample = "اسحب بالماصّة",
	template = "اسحب بالماصّة",
	primers = "اسحب بالماصّة",
	dntp = "اسحب بالماصّة",
	pcrbuffer = "اسحب بالماصّة",
	taq = "اسحب بالماصّة",
	postNear = "وصّل القطب الموجب (+)",
	postFar = "وصّل القطب الموجب (+)",
	power = "شغّل التيار",
	cycler = "برمج وشغّل",
	eyepiece = "شوف بالمجهر",
	meyepiece = "شوف بالمجهر",
	ppe = "البس المعطف والنظارة",
}

local function toast(player, text, tone)
	event:FireClient(player, { kind = "toast", text = text, tone = tone or "info" })
end

local function tween(inst, t, props)
	local tw = TweenService:Create(inst, TweenInfo.new(t, Enum.EasingStyle.Quad), props)
	tw:Play()
	return tw
end

local lastReward = {}
local function reward(player, kind)
	local s = Profiles.state[player]
	if not s then
		return 0
	end
	local now = os.clock()
	if lastReward[player] and now - lastReward[player] < LabData.COOLDOWN then
		return 0
	end
	lastReward[player] = now
	local n = LabData.REWARD[kind] or 1
	s.research = (s.research or 0) + n
	player:SetAttribute("Research", s.research)
	Passport.record(player, "activity", "lab")
	return n
end

-- ------------------------------------------------------------------ benches, items, carrying
local benches = {} -- kind -> bench
local carrying = {} -- player -> { bench, id }

local function newBench(model)
	local b = {
		kind = model.Name:match("^Bench|(.+)$"),
		model = model,
		items = {},
		home = {},
		slots = {},
		uses = {},
		parts = {},
		at = {}, -- item id -> slot id where it rests (nil = home)
		owner = nil,
		touched = 0,
		st = {},
	}
	local top = model:FindFirstChild("BenchTop", true)
	b.topY = top and (top.Position.Y + top.Size.Y / 2) or 0
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Model") and d.Name:match("^Item|") then
			local id = d.Name:match("^Item|(.+)$")
			local h = d:FindFirstChild("Handle")
			if h then
				b.items[id] = d
				b.home[id] = h.CFrame
				for _, p in ipairs(d:GetDescendants()) do
					if p:IsA("BasePart") then
						p.CanCollide = false
						p.CanTouch = false
						p.Massless = true
						if p ~= h then
							p.Anchored = false
							local w = Instance.new("WeldConstraint")
							w.Part0, w.Part1 = h, p
							w.Parent = p
						end
					end
				end
				h.Anchored = true
			end
		elseif d:IsA("BasePart") then
			local sid = d.Name:match("^Slot|(.+)$")
			local uid = d.Name:match("^Use|(.+)$")
			if sid then
				b.slots[sid] = d
			elseif uid then
				b.uses[uid] = d
			else
				b.parts[d.Name] = b.parts[d.Name] or d
			end
		end
	end
	return b
end

local function handOf(player)
	local char = player.Character
	return char and (char:FindFirstChild("RightHand") or char:FindFirstChild("Right Arm"))
end

local function itemLift(b, id)
	return b.home[id].Position.Y - b.topY
end

local function setItemAt(b, id, cf)
	local h = b.items[id].Handle
	local w = h:FindFirstChild("CarryWeld")
	if w then
		w:Destroy()
	end
	h.Anchored = true
	h.CFrame = cf
end

local function returnHome(b, id)
	setItemAt(b, id, b.home[id])
	b.at[id] = nil
end

local function dropCarried(player, toHome)
	local c = carrying[player]
	if not c then
		return
	end
	carrying[player] = nil
	player:SetAttribute("Carrying", nil)
	if toHome then
		returnHome(c.bench, c.id)
	end
end

local function pickUp(player, b, id)
	local hand = handOf(player)
	if not hand then
		return
	end
	local c = carrying[player]
	if c then
		dropCarried(player, true)
	end
	local h = b.items[id].Handle
	if h:FindFirstChild("CarryWeld") then
		return
	end
	b.at[id] = nil
	h.Anchored = false
	h.CFrame = CFrame.new((hand.CFrame * CFrame.new(0, -1.1, -0.6)).Position) * b.home[id].Rotation
	local w = Instance.new("WeldConstraint")
	w.Name = "CarryWeld"
	w.Part0, w.Part1 = hand, h
	w.Parent = h
	carrying[player] = { bench = b, id = id }
	player:SetAttribute("Carrying", NAMES[id] or id)
end

local function placeAt(player, b, id, sid)
	local slotPart = b.slots[sid]
	local cf = CFrame.new(slotPart.Position + Vector3.new(0, slotPart.Size.Y / 2 + itemLift(b, id), 0))
		* b.home[id].Rotation
	dropCarried(player, false)
	setItemAt(b, id, cf)
	b.at[id] = sid
end

-- droplet from the carried bottle onto a target: a small visible "pour"
local function drip(player, target, color)
	local hand = handOf(player)
	if not hand then
		return
	end
	for q = 0, 2 do
		local d = Instance.new("Part")
		d.Shape = Enum.PartType.Ball
		d.Size = Vector3.one * 0.25
		d.Color = color
		d.Material = Enum.Material.Glass
		d.Anchored, d.CanCollide, d.CanQuery, d.CanTouch = true, false, false, false
		d.Position = hand.Position + Vector3.new(0, -1, 0)
		d.Parent = workspace
		task.delay(q * 0.15, function()
			tween(d, 0.35, { Position = target.Position + Vector3.new(0, 0.2, 0) })
			task.delay(0.4, function()
				d:Destroy()
			end)
		end)
	end
end

-- ------------------------------------------------------------------ experiments
local EXP = {}

-- Gram stain: heat-fix, then crystal violet / iodine / alcohol (timed) / safranin, rinsing with water after each.
local GRAM_SEQ = { "cv", "iodine", "alcohol", "safranin" }
local VIOLET, DARKV, PALE, PINK =
	Color3.fromRGB(110, 50, 180),
	Color3.fromRGB(70, 25, 120),
	Color3.fromRGB(226, 214, 236),
	Color3.fromRGB(226, 90, 140)
EXP.gram = {
	reset = function(b)
		local smear = b.items.slide:FindFirstChild("Smear")
		if smear then
			smear.Color = Color3.fromRGB(238, 232, 214)
		end
		b.st = {
			sample = LabData.GRAM_SAMPLES[math.random(1, #LabData.GRAM_SAMPLES)],
			fixed = false,
			step = 1,
			rinse = false,
		}
	end,
	use = function(b, player, uid, held)
		local st = b.st
		if uid == "burner" then
			if held ~= "slide" then
				return toast(
					player,
					"🔥 جيب الشريحة ومرّرها على اللهب عشان تثبّت البكتيريا"
				)
			end
			st.fixed = true
			tween(b.items.slide.Smear, 0.6, { Color = Color3.fromRGB(222, 212, 186) })
			return toast(
				player,
				"🔥 تثبيت بالحرارة: البكتيريا التصقت بالشريحة. حطها على حامل الصبغ",
				"good"
			)
		elseif uid == "eyepiece" then
			if b.at.slide ~= "stage" then
				return toast(player, "🔬 حط الشريحة المصبوغة على منصة المجهر أول")
			end
			st.looking = true
			event:FireClient(player, {
				kind = "scope",
				cocci = st.sample.id == "staph",
				color = st.violet and "violet" or "pink",
			})
		end
	end,
	slot = function(b, player, sid, held)
		local st = b.st
		local smear = b.items.slide:FindFirstChild("Smear")
		if sid == "tray" then
			if held == "slide" then
				if not st.fixed then
					return toast(
						player,
						"⚠️ ثبّت اللطخة بالحرارة أول، وإلا البكتيريا تنغسل مع الماي"
					)
				end
				return "place"
			end
			if not held or held == "slide" then
				return
			end
			if b.at.slide ~= "tray" then
				return toast(player, "🧫 حط الشريحة على حامل الصبغ أول")
			end
			local reagentColor = {
				cv = VIOLET,
				iodine = Color3.fromRGB(150, 90, 30),
				alcohol = Color3.fromRGB(220, 235, 250),
				safranin = PINK,
				water = Color3.fromRGB(170, 220, 255),
			}
			drip(player, smear, reagentColor[held] or Color3.new(1, 1, 1))
			if held == "water" then
				if not st.rinse then
					return toast(player, "💧 ما في صبغة تغسلها الحين")
				end
				st.rinse = false
				if st.alcoholAt then
					local secs = os.clock() - st.alcoholAt
					st.alcoholAt = nil
					local D = LabData.GRAM_DECOLOR
					st.quality = secs < D.min and "under" or secs > D.max and "over" or "ok"
					local pos = st.sample.gram == "pos"
					st.violet = (pos and st.quality ~= "over") or (not pos and st.quality == "under")
					tween(smear, 0.5, { Color = st.violet and VIOLET or PALE })
					event:FireClient(player, { kind = "timer", stop = true })
					return toast(
						player,
						("💧 غسلت بعد %.1f ثانية من الكحول. %s"):format(
							secs,
							st.quality == "ok" and "توقيت ممتاز 👌" or LabData.GRAM_QUALITY[st.quality]
						),
						st.quality == "ok" and "good" or "warn"
					)
				end
				return toast(player, "💧 غسلت الزيادة بالماء", "good")
			end
			if st.rinse then
				return toast(player, "💧 اغسل بقنينة الماء أول قبل الكاشف الجاي")
			end
			local want = GRAM_SEQ[st.step]
			if not want then
				return toast(player, "✅ الصبغ خلص. انقل الشريحة للمجهر")
			end
			if held ~= want then
				local note
				for _, s in ipairs(LabData.GRAM_STEPS) do
					if s.id == held then
						note = s.note
					end
				end
				return toast(
					player,
					("❌ مو هذا الحين. %s"):format(
						st.step == 1
								and "أول شي الصبغة الأساسية اللي تلوّن كل الخلايا"
							or (note and ("هذا الكاشف: " .. note) or "")
					),
					"warn"
				)
			end
			st.step += 1
			st.rinse = true
			if held == "cv" then
				tween(smear, 0.6, { Color = VIOLET })
				toast(
					player,
					"🟣 كريستال بنفسجي: كل الخلايا صارت بنفسجية. اغسل بالماء",
					"good"
				)
			elseif held == "iodine" then
				tween(smear, 0.6, { Color = DARKV })
				toast(
					player,
					"🟤 اليود يثبّت الصبغة داخل الجدار. اغسل بالماء",
					"good"
				)
			elseif held == "alcohol" then
				st.alcoholAt = os.clock()
				tween(smear, LabData.GRAM_DECOLOR.bar, { Color = Color3.fromRGB(190, 160, 220) })
				event:FireClient(player, {
					kind = "timer",
					min = LabData.GRAM_DECOLOR.min,
					max = LabData.GRAM_DECOLOR.max,
					bar = LabData.GRAM_DECOLOR.bar,
				})
				toast(
					player,
					"⏱️ الكحول يزيل اللون… اغسل بالماء بالوقت المناسب (مو فوراً ولا متأخر)",
					"warn"
				)
			elseif held == "safranin" then
				tween(smear, 0.6, { Color = st.violet and Color3.fromRGB(120, 50, 170) or PINK })
				toast(
					player,
					"🌸 الصفرانين يلوّن اللي فقد البنفسجي بالوردي. اغسل، وبعدها للمجهر",
					"good"
				)
			end
			return
		elseif sid == "stage" then
			if held ~= "slide" then
				return toast(player, "🔬 المنصة للشريحة")
			end
			if st.step <= #GRAM_SEQ or st.rinse then
				return toast(player, "🧪 كمّل خطوات الصبغ والغسيل أول")
			end
			return "place"
		end
	end,
	answer = function(b, player, ans)
		local st = b.st
		if not st.looking or st.answered then
			return nil
		end
		st.answered = true
		local ok = st.quality == "ok" and ans == st.sample.gram
		local gained = ok and reward(player, "gram") or 0
		return {
			ok = ok,
			gained = gained,
			quality = st.quality,
			truth = st.sample.gram,
			name = st.sample.name,
		}
	end,
}

-- Gel electrophoresis: gel into the tank, buffer, load ladder + sample, connect the + lead, run, read under UV.
EXP.gel = {
	reset = function(b)
		local sizes = LabData.GEL_UNKNOWNS
		local pick = math.random(1, #sizes)
		local options = { sizes[pick] }
		for _, d in ipairs({ -2, 2, -3, 3 }) do
			if sizes[pick + d] and #options < 3 then
				table.insert(options, sizes[pick + d])
			end
		end
		for i = #options, 2, -1 do
			local j = math.random(1, i)
			options[i], options[j] = options[j], options[i]
		end
		for _, p in ipairs(b.items.gel:GetChildren()) do
			if p.Name == "Band" then
				p:Destroy()
			elseif p.Name:match("^Well|") then
				p.Color = Color3.fromRGB(190, 200, 210)
			end
		end
		local buf = b.parts["Liquid|buffer"]
		if buf then
			buf.Size = Vector3.new(buf.Size.X, 0.02, buf.Size.Z)
		end
		local uv = b.parts["Liquid|uv"]
		if uv then
			uv.Transparency = 0.85
		end
		for _, lead in ipairs({ b.parts["Lead|red"], b.parts["Lead|black"] }) do
			if lead then
				lead.Transparency = 1
			end
		end
		local scr = b.parts["Screen|power"]
		if scr then
			scr:FindFirstChildWhichIsA("TextLabel", true).Text = "0 V"
		end
		b.st = { size = sizes[pick], options = options, answer = table.find(options, sizes[pick]), wells = {} }
	end,
	use = function(b, player, uid, held)
		local st = b.st
		if uid == "ladder" or uid == "sample" then
			if held ~= "pipette" then
				return toast(player, "🧪 امسك الماصّة أول")
			end
			st.pip = uid
			b.items.pipette.Tip.Color = uid == "ladder" and Color3.fromRGB(60, 90, 220) or Color3.fromRGB(220, 80, 150)
			return toast(
				player,
				"💧 سحبت " .. NAMES[uid] .. ". حمّله ببئر بالجل (حوض الفصل)"
			)
		elseif uid == "postNear" or uid == "postFar" then
			st.plusFar = uid == "postFar"
			local power = b.uses.power
			local function lead(part, post)
				local a, c = power.Position + Vector3.new(0, 0.9, -1.2), post.Position + Vector3.new(0, 0.3, 0)
				part.Size = Vector3.new(0.15, 0.15, (c - a).Magnitude)
				part.CFrame = CFrame.lookAt((a + c) / 2, c)
				part.Transparency = 0
			end
			lead(b.parts["Lead|red"], b.uses[uid])
			lead(b.parts["Lead|black"], b.uses[uid == "postFar" and "postNear" or "postFar"])
			return toast(
				player,
				"🔌 وصّلت القطب الموجب (+) "
					.. (st.plusFar and "بالطرف البعيد" or "عند الآبار")
			)
		elseif uid == "power" then
			if b.at.gel ~= "tank" or not st.buffer or not (st.wells[1] and st.wells[2]) or st.plusFar == nil then
				return toast(
					player,
					"⚡ قبل التشغيل: الجل بالحوض + المحلول المنظم + تحميل البئرين + توصيل القطب الموجب"
				)
			end
			if st.running or st.ran then
				return
			end
			st.running = true
			local gel = b.items.gel
			local h = gel.Handle
			local scr = b.parts["Screen|power"]:FindFirstChildWhichIsA("TextLabel", true)
			scr.Text = "100 V"
			local bubbles = {}
			for _, post in ipairs({ b.uses.postNear, b.uses.postFar }) do
				local pe = Instance.new("ParticleEmitter")
				pe.Rate, pe.Lifetime, pe.Speed = 25, NumberRange.new(0.6, 1), NumberRange.new(1, 2)
				pe.Size = NumberSequence.new(0.08)
				pe.Color = ColorSequence.new(Color3.new(1, 1, 1))
				pe.Parent = post
				table.insert(bubbles, pe)
			end
			-- bands start in the wells and move along the gel (local -Z..+Z of the handle = wells..far end)
			local function band(lane, bp, col)
				local p = Instance.new("Part")
				p.Name = "Band"
				p.Size = Vector3.new(0.5, 0.06, 0.12)
				p.Color = col
				p.Material = Enum.Material.SmoothPlastic
				p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.Massless = true, false, false, false, true
				local x = lane == 1 and -0.5 or 0.5
				p.CFrame = h.CFrame * CFrame.new(x, 0.2, -1.8)
				p.Parent = gel
				local d = LabData.gelDistance(bp)
				local goal = st.plusFar and (h.CFrame * CFrame.new(x, 0.2, -1.8 + d * 3.8))
					or (h.CFrame * CFrame.new(x, 0.2, -2.6))
				tween(p, 6, { CFrame = goal, Transparency = st.plusFar and 0 or 1 })
				return p
			end
			local made = {}
			for _, bp in ipairs(LabData.GEL_LADDER) do
				local p = band(1, bp, Color3.fromRGB(60, 90, 220))
				p:SetAttribute("bp", bp)
				table.insert(made, p)
			end
			table.insert(made, band(2, st.size, Color3.fromRGB(220, 80, 150)))
			toast(player, "⚡ التيار شغّال… راقب الصبغة تتحرك", "info")
			task.delay(6.2, function()
				for _, pe in ipairs(bubbles) do
					pe:Destroy()
				end
				scr.Text = "0 V"
				st.running = false
				if not st.plusFar then
					for _, p in ipairs(made) do
						p:Destroy()
					end
					st.wells = {}
					for _, w in ipairs(gel:GetChildren()) do
						if w.Name:match("^Well|") then
							w.Color = Color3.fromRGB(190, 200, 210)
						end
					end
					return toast(
						player,
						"❌ الـ DNA طلع من الآبار للخلف وضاع! شحنته سالبة فيمشي للقطب الموجب: لازم + يكون بالطرف البعيد. حمّل من جديد",
						"warn"
					)
				end
				for _, p in ipairs(made) do
					p.Anchored = false
					local w = Instance.new("WeldConstraint")
					w.Part0, w.Part1 = h, p
					w.Parent = p
				end
				st.ran = true
				toast(
					player,
					"✅ خلص التشغيل. انقل الجل لجهاز الأشعة فوق البنفسجية عشان تقرأ الشرائط",
					"good"
				)
			end)
		end
	end,
	slot = function(b, player, sid, held)
		local st = b.st
		if sid == "tank" then
			if held == "gel" then
				return "place"
			elseif held == "buffer" then
				if b.at.gel ~= "tank" then
					return toast(player, "🧊 حط الجل بالحوض أول")
				end
				st.buffer = true
				drip(player, b.slots.tank, Color3.fromRGB(150, 210, 255))
				local buf = b.parts["Liquid|buffer"]
				tween(buf, 1.2, {
					Size = Vector3.new(buf.Size.X, 1.0, buf.Size.Z),
					Position = buf.Position + Vector3.new(0, 0.5, 0),
				})
				return toast(
					player,
					"🌊 المحلول المنظم يغطي الجل ويوصل الكهرباء",
					"good"
				)
			elseif held == "pipette" then
				if not st.pip then
					return toast(
						player,
						"💧 الماصّة فاضية: اسحب من أنبوب الـ Ladder أو العيّنة"
					)
				end
				if not st.buffer or b.at.gel ~= "tank" then
					return toast(
						player,
						"🌊 الجل لازم يكون بالحوض ومغطّى بالمحلول قبل التحميل"
					)
				end
				local n = st.pip == "ladder" and 1 or 2
				local well = b.items.gel:FindFirstChild("Well|" .. n)
				well.Color = st.pip == "ladder" and Color3.fromRGB(60, 90, 220) or Color3.fromRGB(220, 80, 150)
				st.wells[n] = true
				st.pip = nil
				b.items.pipette.Tip.Color = Color3.fromRGB(240, 246, 250)
				return toast(player, ("✅ حمّلت البئر %d"):format(n), "good")
			end
		elseif sid == "uv" then
			if held ~= "gel" then
				return
			end
			if not st.ran then
				return toast(player, "⚡ شغّل الفصل الكهربائي أول")
			end
			placeAt(player, b, "gel", "uv")
			b.parts["Liquid|uv"].Transparency = 0.3
			for _, p in ipairs(b.items.gel:GetChildren()) do
				if p.Name == "Band" then
					-- under UV the stained DNA glows: bright and easy to read against the dark gel
					p.Material = Enum.Material.Neon
					p.Size = Vector3.new(0.6, 0.08, 0.16)
					p.Color = p:GetAttribute("bp") and Color3.fromRGB(170, 230, 255) or Color3.fromRGB(255, 120, 220)
					local bp = p:GetAttribute("bp")
					if bp then
						local bb = Instance.new("BillboardGui")
						bb.Size = UDim2.fromOffset(46, 18)
						bb.StudsOffset = Vector3.new(-0.9, 0, 0)
						bb.MaxDistance = 25
						local t = Instance.new("TextLabel")
						t.Size = UDim2.fromScale(1, 1)
						t.BackgroundTransparency = 1
						t.TextColor3 = Color3.new(1, 1, 1)
						t.TextStrokeTransparency = 0.3
						t.TextScaled = true
						t.Font = Enum.Font.GothamBold
						t.Text = tostring(bp)
						t.Parent = bb
						bb.Parent = p
					end
				end
			end
			st.reading = true
			event:FireClient(player, { kind = "gelRead", options = st.options })
			return
		end
	end,
	answer = function(b, player, i)
		local st = b.st
		if not st.reading or st.answered then
			return nil
		end
		st.answered = true
		local ok = i == st.answer
		return { ok = ok, gained = ok and reward(player, "gel") or 0, truth = st.size }
	end,
}

-- PCR: pipette the five components into the tube, put it in the cycler, program three temperatures, run 30 cycles.
local PCR_PARTS = { "template", "primers", "dntp", "pcrbuffer", "taq" }
local PCR_MISSING = {
	template = "بدون DNA القالب ما في شي ينسخ",
	primers = "بدون البادئات الإنزيم ما يعرف من وين يبدأ",
	dntp = "بدون النيوكليوتيدات ما في وحدات يبني منها الشريط الجديد",
	pcrbuffer = "بدون المحلول المنظم (وفيه المغنيسيوم) الإنزيم ما يشتغل صح",
	taq = "بدون إنزيم Taq ما يصير نسخ أبداً",
}
EXP.pcr = {
	reset = function(b)
		local liq = b.items.tube:FindFirstChild("Liquid|tube")
		if liq then
			liq.Transparency = 1
		end
		b.parts["Screen|cycler"]:FindFirstChildWhichIsA("TextLabel", true).Text = "READY"
		b.st = { added = {}, n = 0 }
		b.at.tube = "rack" -- the tube's home is its rack
	end,
	use = function(b, player, uid, held)
		local st = b.st
		if table.find(PCR_PARTS, uid) then
			if held ~= "pipette" then
				return toast(player, "🧪 امسك الماصّة أول")
			end
			st.pip = uid
			b.items.pipette.Tip.Color = Color3.fromRGB(250, 220, 120)
			return toast(player, "💧 سحبت " .. NAMES[uid] .. ". ضيفه للأنبوب اللي بالحامل")
		elseif uid == "cycler" then
			if b.at.tube ~= "cycler" then
				return toast(player, "🧬 حط الأنبوب داخل الجهاز أول")
			end
			if st.running then
				return
			end
			event:FireClient(player, { kind = "pcrProgram" })
		end
	end,
	slot = function(b, player, sid, held)
		local st = b.st
		if sid == "rack" then
			if held == "tube" then
				return "place"
			end
			if held ~= "pipette" then
				return
			end
			if b.at.tube ~= "rack" then
				return toast(player, "🧪 رجّع الأنبوب للحامل عشان تضيف فيه")
			end
			if not st.pip then
				return toast(player, "💧 الماصّة فاضية: اسحب مكوّن من الرف أول")
			end
			if not st.added[st.pip] then
				st.added[st.pip] = true
				st.n += 1
			end
			st.pip = nil
			b.items.pipette.Tip.Color = Color3.fromRGB(240, 246, 250)
			local liq = b.items.tube:FindFirstChild("Liquid|tube")
			liq.Transparency = 0.1
			liq.Size = Vector3.new(0.12 + st.n * 0.12, 0.3, 0.3)
			return toast(player, ("✅ أضفت للأنبوب (%d/5 مكوّنات)"):format(st.n), "good")
		elseif sid == "cycler" then
			if held == "tube" then
				return "place"
			end
		end
	end,
	program = function(b, player, den, ann, ext)
		local st = b.st
		if b.at.tube ~= "cycler" or st.running then
			return { ok = false, msg = "حط الأنبوب بالجهاز أول" }
		end
		if not (den >= 90 and den <= 98) then
			return {
				ok = false,
				msg = "🌡️ فك الشريطين يحتاج حوالي 95°م: أقل من 90 الشريطين ما ينفصلون",
			}
		elseif not (ann >= 50 and ann <= 65) then
			return {
				ok = false,
				msg = "🌡️ التصاق البادئات حوالي 55°م: لو أعلى بوايد ما تلصق، ولو أقل بوايد تلصق بأماكن غلط",
			}
		elseif not (ext >= 68 and ext <= 75) then
			return { ok = false, msg = "🌡️ إنزيم Taq يشتغل أحسن شي عند 72°م" }
		end
		st.running = true
		local scr = b.parts["Screen|cycler"]:FindFirstChildWhichIsA("TextLabel", true)
		task.spawn(function()
			local temps = { den, ann, ext }
			for cycle = 1, 30 do
				for _, tmp in ipairs(temps) do
					scr.Text = ("دورة %d/30 • %d°م"):format(cycle, tmp)
					task.wait(0.12)
				end
			end
			st.running = false
			local missing
			for _, k in ipairs(PCR_PARTS) do
				if not st.added[k] then
					missing = k
					break
				end
			end
			if missing then
				scr.Text = "NO PRODUCT"
				st.done = true
				if b.owner == player then
					b.finish() -- clear the bench so the player can mix a new tube
				end
				return toast(
					player,
					"❌ ما صار تضاعف: " .. PCR_MISSING[missing] .. ". جرّب من جديد",
					"warn"
				)
			end
			scr.Text = "2³⁰ ≈ 1,000,000,000 نسخة ✅"
			local gained = reward(player, "pcr")
			st.done = true
			toast(
				player,
				("✅ 30 دورة: كل دورة تضاعف النسخ، يعني أكثر من مليار نسخة من القطعة! +%d 🧪"):format(
					gained
				),
				"good"
			)
			task.delay(4, function()
				if b.owner == player then
					b.finish()
				end
			end)
		end)
		return { ok = true }
	end,
}

-- Light microscopy: put a prepared slide on the stage, then look through the eyepiece (the focus/magnification
-- simulation is LightMicroscope.client, graded by Lab.server).
EXP.micro = {
	reset = function(b)
		b.st = {}
	end,
	use = function(b, player, uid)
		if uid == "meyepiece" then
			local sid
			for id, at in pairs(b.at) do
				if at == "mstage" then
					sid = id:match("^slide_(.+)$")
				end
			end
			if not sid then
				return toast(
					player,
					"🔬 اختار شريحة من العلبة وحطها على منصة المجهر"
				)
			end
			if labOpen then
				labOpen:FireClient(player, "lightmicro", sid)
			end
		end
	end,
	slot = function(b, _player, sid, held)
		if sid == "mstage" and held and held:match("^slide_") then
			for id, at in pairs(b.at) do
				if at == "mstage" then
					returnHome(b, id)
				end
			end
			return "place"
		end
	end,
}

-- ------------------------------------------------------------------ bench ownership + prompts
local handlers = {} -- "<kind>|item|<id>" / "|slot|" / "|use|" / "ppe" -> prompt handler (also used by the QA hook)
local function bind(key, p, handler)
	handlers[key] = handler
	p.Triggered:Connect(handler)
end
local function prompt(part, action, object, hold)
	local p = Instance.new("ProximityPrompt")
	p.ActionText = action
	p.ObjectText = object or ""
	p.MaxActivationDistance = 9
	p.RequiresLineOfSight = false
	p.HoldDuration = hold or 0
	p.Style = Enum.ProximityPromptStyle.Default
	p.Parent = part
	return p
end

local function claim(player, b)
	if b.owner and b.owner ~= player and b.owner.Parent then
		toast(
			player,
			("🧑‍🔬 %s يشتغل على هالطاولة الحين. جرّب طاولة ثانية أو انتظر شوي"):format(
				b.owner.DisplayName
			)
		)
		return false
	end
	if not player:GetAttribute("LabPPE") then
		toast(player, "🥼 البس معطف المختبر والنظارة أول (عند المدخل)", "warn")
		return false
	end
	if b.owner ~= player then
		b.owner = player
		EXP[b.kind].reset(b)
	end
	b.touched = os.clock()
	return true
end

local function resetBench(b)
	for player, c in pairs(carrying) do
		if c.bench == b then
			dropCarried(player, false)
		end
	end
	for id in pairs(b.items) do
		returnHome(b, id)
	end
	b.owner = nil
	EXP[b.kind].reset(b)
end

for _, model in ipairs(mapFolder:GetDescendants()) do
	if model:IsA("Model") and model.Name:match("^Bench|") then
		local b = newBench(model)
		if EXP[b.kind] then
			benches[b.kind] = b
			EXP[b.kind].reset(b)
			b.finish = function()
				task.delay(2.5, function()
					resetBench(b)
				end)
			end
			for id, m in pairs(b.items) do
				local p = prompt(m.Handle, "التقط", NAMES[id] or id)
				bind(b.kind .. "|item|" .. id, p, function(player)
					if not claim(player, b) then
						return
					end
					local c = carrying[player]
					if c and c.bench == b and c.id == id then
						dropCarried(player, true) -- tap again: put it back where it came from
						return
					end
					pickUp(player, b, id)
				end)
			end
			for sid, part in pairs(b.slots) do
				local p = prompt(part, "حط / استخدم هنا", NAMES[sid] or sid)
				bind(b.kind .. "|slot|" .. sid, p, function(player)
					if not claim(player, b) then
						return
					end
					local c = carrying[player]
					local held = c and c.bench == b and c.id or nil
					local r = EXP[b.kind].slot(b, player, sid, held)
					if r == "place" and held then
						placeAt(player, b, held, sid)
					elseif r == nil and not held then
						toast(player, "✋ " .. (NAMES[sid] or sid) .. ": جيب الأداة المناسبة")
					end
				end)
			end
			for uid, part in pairs(b.uses) do
				local p = prompt(part, ACTION[uid] or "استخدم", NAMES[uid] or uid)
				bind(b.kind .. "|use|" .. uid, p, function(player)
					if not claim(player, b) then
						return
					end
					local c = carrying[player]
					EXP[b.kind].use(b, player, uid, c and c.bench == b and c.id or nil)
				end)
			end
		end
	end
end

-- lab coat + goggles on the character
local ppe = mapFolder:FindFirstChild("Use|ppe", true)
if ppe then
	bind("ppe", prompt(ppe, ACTION.ppe, NAMES.ppe), function(player)
		local char = player.Character
		local torso = char and (char:FindFirstChild("UpperTorso") or char:FindFirstChild("Torso"))
		local head = char and char:FindFirstChild("Head")
		if not (torso and head) or player:GetAttribute("LabPPE") then
			return
		end
		local function wear(name, size, attach, offset, color, mat, transp)
			local p = Instance.new("Part")
			p.Name = name
			p.Size = size
			p.Color = color
			p.Material = mat
			p.Transparency = transp or 0
			p.CanCollide, p.CanQuery, p.CanTouch, p.Massless = false, false, false, true
			p.CFrame = attach.CFrame * offset
			local w = Instance.new("WeldConstraint")
			w.Part0, w.Part1 = attach, p
			w.Parent = p
			p.Parent = char
		end
		wear(
			"LabCoat",
			Vector3.new(2.25, 2.1, 1.25),
			torso,
			CFrame.new(0, -0.05, 0),
			Color3.fromRGB(248, 248, 246),
			Enum.Material.Fabric
		)
		wear(
			"LabCoatTail",
			Vector3.new(2.2, 1.3, 1.15),
			torso,
			CFrame.new(0, -1.6, 0),
			Color3.fromRGB(244, 244, 242),
			Enum.Material.Fabric
		)
		wear(
			"Goggles",
			Vector3.new(1.3, 0.4, 0.3),
			head,
			CFrame.new(0, 0.2, -0.62),
			Color3.fromRGB(190, 230, 250),
			Enum.Material.Glass,
			0.3
		)
		player:SetAttribute("LabPPE", true)
		toast(player, "🥼 جاهز! اختار طاولة تجربة وابدأ", "good")
	end)
end

-- answers from the small client overlays
fn.OnServerInvoke = function(player, action, a, b2, c2)
	if action == "gram" then
		local b = benches.gram
		if b and b.owner == player then
			local r = EXP.gram.answer(b, player, a)
			if r then
				b.finish()
			end
			return r
		end
	elseif action == "gel" then
		local b = benches.gel
		if b and b.owner == player and typeof(a) == "number" then
			local r = EXP.gel.answer(b, player, a)
			if r then
				b.finish()
			end
			return r
		end
	elseif action == "pcr" then
		local b = benches.pcr
		if b and b.owner == player and typeof(a) == "number" and typeof(b2) == "number" and typeof(c2) == "number" then
			b.touched = os.clock()
			return EXP.pcr.program(b, player, a, b2, c2)
		end
	end
	return nil
end

-- Studio-only QA hook: run a prompt's handler exactly as if the player had pressed it (tools/studio_tests/labs54.*)
if game:GetService("RunService"):IsStudio() then
	local qa = Instance.new("BindableFunction")
	qa.Name = "Labs54QA"
	qa.OnInvoke = function(player, key)
		local h = handlers[key]
		if not h then
			return false
		end
		h(player)
		return true
	end
	qa.Parent = game:GetService("ServerStorage")
end

-- free a bench when its owner leaves, walks away or goes idle
task.spawn(function()
	while true do
		task.wait(2)
		for _, b in pairs(benches) do
			local o = b.owner
			if o then
				local root = o.Parent and o.Character and o.Character:FindFirstChild("HumanoidRootPart")
				local far = not root or (root.Position - b.model:GetPivot().Position).Magnitude > 60
				if not o.Parent or far or os.clock() - b.touched > 180 then
					resetBench(b)
				end
			end
		end
	end
end)

Players.PlayerRemoving:Connect(function(player)
	carrying[player] = nil
	lastReward[player] = nil
end)
Players.PlayerAdded:Connect(function(player)
	-- dying or resetting while carrying: the item goes back to its shelf instead of falling out of the world
	player.CharacterRemoving:Connect(function()
		dropCarried(player, true)
	end)
	player.CharacterAdded:Connect(function()
		player:SetAttribute("LabPPE", nil) -- a fresh character has no coat
		player:SetAttribute("Carrying", nil)
		carrying[player] = nil
	end)
end)
