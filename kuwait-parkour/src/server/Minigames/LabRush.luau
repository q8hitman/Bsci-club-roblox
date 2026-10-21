-- مختبر السباق (Lab Rush): a co-op round in a teaching lab. The order board always shows 3 orders; the team works the
-- four stations (ProximityPrompts, so it plays the same on phones) to fill them. Solo works too, a team is faster.
-- v61 (owner: "some minigame ideas are bad"): every station is real science now (was a fantasy lab with a mutation
-- machine making silly creatures):
--   🧬 DNA strand     the board shows one strand; press the complementary bases (A-T, G-C) in order
--   🧪 Enzyme tube    the board names a food molecule; pick the enzyme that digests it, then press the tube
--   🔬 Gram sorter    each bacterium goes to its bin by Gram stain (purple +, pink -) or by shape (round, rod)
--   🌀 Centrifuge     load both balancing tubes together (7 s window solo, 2.5 s with friends)
-- The round ends when the team reaches its goal (all win) or time runs out (nobody loses anything).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local M = {
	id = "LabRush",
	ar = "🧪 مختبر السباق (تعاوني)",
	hint = "خلّصوا طلبات اللوحة مع بعض! اضغط على الأجهزة 👆",
	duration = 150,
	mode = "coop",
}

local LETTERS = { "A", "T", "G", "C" }
local PAIR = { A = "T", T = "A", G = "C", C = "G" }
-- shelf i holds ENZYMES[i]; it digests SUBSTRATES[i] into PRODUCTS[i]
local ENZYMES = { "أميليز", "بروتياز", "ليبيز" }
local SUBSTRATES = { "🍞 نشا", "🥩 بروتين", "🧈 دهون" }
local PRODUCTS = { "سكر", "أحماض أمينية", "أحماض دهنية" }
local PRODUCT_COLORS = { Color3.fromRGB(250, 240, 200), Color3.fromRGB(240, 150, 150), Color3.fromRGB(250, 220, 120) }
local GRAM = {
	{ "🟣 موجبة جرام", Color3.fromRGB(130, 60, 170) },
	{ "🩷 سالبة جرام", Color3.fromRGB(235, 120, 170) },
}
local SHAPE = { "● كروية", "▮ عصوية" }
local KINDS = { "dna", "enzyme", "sort", "centrifuge" }

local function notify(player, text)
	local ev = ReplicatedStorage:FindFirstChild("Notify")
	if ev and player.Parent then
		ev:FireClient(player, text)
	end
end

local function flash(part, color, t)
	if not part or not part.Parent then
		return
	end
	local old = part:GetAttribute("BaseColor") or part.Color
	part:SetAttribute("BaseColor", old)
	part.Color = color
	task.delay(t or 0.35, function()
		if part.Parent then
			part.Color = old
		end
	end)
end

local function setLabel(part, text)
	local l = part and part:FindFirstChildWhichIsA("TextLabel", true)
	if l then
		l.Text = text
	end
end

function M.start(ctx)
	local arena = ctx.arena
	local tier = ctx.tier or 1
	local function find(name)
		return arena:FindFirstChild(name)
	end
	local board = find("OrderBoard")
	local boardText = board and board:FindFirstChildWhichIsA("TextLabel", true)

	local nPlayers = 0
	for _ in pairs(ctx.alive) do
		nPlayers += 1
	end
	local goal = math.clamp(4 + 2 * (nPlayers - 1) + (tier - 1), 4, 14)
	local done = 0
	ctx.prompts, ctx.temp = {}, {}
	local orders = {}

	local function temp(inst)
		table.insert(ctx.temp, inst)
		return inst
	end

	local function prompt(part, action, object)
		local p = Instance.new("ProximityPrompt")
		p.ActionText = action
		p.ObjectText = object or ""
		p.HoldDuration = 0
		p.MaxActivationDistance = 11
		p.RequiresLineOfSight = false
		p.Parent = part
		table.insert(ctx.prompts, p)
		return p
	end

	local function orderText(o)
		if o.kind == "dna" then
			local s = {}
			for i, L in ipairs(o.seq) do
				s[i] = i < o.idx and ("✅" .. L) or L
			end
			return "🧬 كمّلوا الشريط: " .. table.concat(s, " ")
		elseif o.kind == "enzyme" then
			return "🧪 هضم " .. SUBSTRATES[o.target] .. ": أي إنزيم؟"
		elseif o.kind == "sort" then
			return ("🔬 افرزوا البكتيريا حسب %s (%d/3)"):format(
				o.rule == "gram" and "صبغة جرام" or "الشكل",
				o.count
			)
		else
			return "🌀 الطرد المركزي: حطّوا الأنبوبين مع بعض"
		end
	end

	local function refresh()
		if not boardText then
			return
		end
		local lines = { ("✅ الفريق %d/%d"):format(done, goal) }
		if ctx.teamDone then
			table.insert(lines, "🎉 خلّصتوا كل الطلبات!")
		else
			for _, o in ipairs(orders) do
				table.insert(lines, orderText(o))
			end
		end
		boardText.Text = table.concat(lines, "\n")
	end

	local spawnSample -- forward

	local function newOrder()
		local used = {}
		for _, o in ipairs(orders) do
			used[o.kind] = true
		end
		local free = {}
		for _, k in ipairs(KINDS) do
			if not used[k] then
				table.insert(free, k)
			end
		end
		local kind = free[math.random(1, #free)]
		local o = { kind = kind }
		if kind == "dna" then
			o.seq, o.idx = {}, 1
			for i = 1, 3 + math.min(tier, 2) do
				o.seq[i] = LETTERS[math.random(1, 4)]
			end
		elseif kind == "enzyme" then
			o.target = math.random(1, 3)
		elseif kind == "sort" then
			o.rule = math.random() < 0.5 and "gram" or "shape"
			o.count = 0
			for i = 1, 2 do
				setLabel(find("SortBin|" .. i), o.rule == "gram" and GRAM[i][1] or SHAPE[i])
			end
		end
		table.insert(orders, o)
		if kind == "sort" then
			spawnSample()
		end
	end

	local function orderOf(kind)
		for _, o in ipairs(orders) do
			if o.kind == kind then
				return o
			end
		end
		return nil
	end

	local function complete(o, player)
		for i, x in ipairs(orders) do
			if x == o then
				table.remove(orders, i)
				break
			end
		end
		done += 1
		if player then
			ctx.addScore(player, 2)
		end
		for p in pairs(ctx.alive) do
			notify(p, ("✅ طلب خلص! الفريق %d/%d"):format(done, goal))
		end
		if done >= goal then
			ctx.teamDone = true
		else
			task.delay(1, function()
				if ctx.running and not ctx.teamDone then
					newOrder()
					refresh()
				end
			end)
		end
		refresh()
	end

	-- 🧬 DNA strand: press the partner of each base on the board
	local console = find("DNAConsole")
	for _, L in ipairs(LETTERS) do
		local bin = find("DNABin|" .. L)
		if bin then
			ctx.connect(prompt(bin, "حط " .. L, "DNA").Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				local o = orderOf("dna")
				if not o then
					notify(player, "ما في طلب DNA الحين")
					return
				end
				if PAIR[o.seq[o.idx]] == L then
					o.idx += 1
					flash(console, Color3.fromRGB(80, 220, 120))
					if o.idx > #o.seq then
						complete(o, player)
					else
						refresh()
					end
				else
					flash(console, Color3.fromRGB(230, 70, 70))
					notify(
						player,
						("❌ شريك %s هو %s (A مع T، و G مع C)"):format(o.seq[o.idx], PAIR[o.seq[o.idx]])
					)
				end
			end))
		end
	end

	-- 🧪 enzyme tube: pick one enzyme from the shelves, then press the tube
	local selected = nil
	local shelves = {}
	for i = 1, 3 do
		local part = find("MutIngredient|" .. i)
		shelves[i] = part
		if part then
			ctx.connect(prompt(part, "اختار", "إنزيم " .. ENZYMES[i]).Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				for j, s in ipairs(shelves) do
					s.Material = (j == i) and Enum.Material.Neon or Enum.Material.SmoothPlastic
				end
				selected = i
			end))
		end
	end
	local machine = find("MutMachine")
	local output = find("MutOutput")
	local function product(ok, i)
		if not output then
			return
		end
		local drop = temp(Instance.new("Part"))
		drop.Name = ok and "Product" or "NoReaction"
		drop.Shape = Enum.PartType.Ball
		drop.Size = Vector3.new(3, 3, 3)
		drop.Anchored, drop.CanCollide = true, false
		drop.Material = ok and Enum.Material.Neon or Enum.Material.Slate
		drop.Color = ok and PRODUCT_COLORS[i] or Color3.fromRGB(120, 120, 120)
		drop.CFrame = CFrame.new(output.Position + Vector3.new(0, 1.8, 0))
		drop.Parent = arena
		if ok then
			TweenService:Create(drop, TweenInfo.new(0.4, Enum.EasingStyle.Sine, Enum.EasingDirection.Out, 3, true), {
				CFrame = drop.CFrame + Vector3.new(0, 1.5, 0),
			}):Play()
		end
		task.delay(ok and 3 or 1.5, function()
			if drop.Parent then
				drop:Destroy()
			end
		end)
	end
	if machine then
		ctx.connect(
			prompt(machine, "شغّل التفاعل", "أنبوب التفاعل").Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				local o = orderOf("enzyme")
				if not o then
					notify(player, "ما في طلب هضم الحين")
					return
				end
				if not selected then
					notify(player, "اختاروا إنزيم من الرف أول")
					return
				end
				local ok = selected == o.target
				product(ok, o.target)
				for _, s in ipairs(shelves) do
					s.Material = Enum.Material.SmoothPlastic
				end
				if ok then
					notify(
						player,
						("✅ %s هضم %s ← %s"):format(ENZYMES[o.target], SUBSTRATES[o.target], PRODUCTS[o.target])
					)
					complete(o, player)
				else
					notify(
						player,
						("💨 ما صار تفاعل: %s ما يهضم %s"):format(
							ENZYMES[selected],
							SUBSTRATES[o.target]
						)
					)
				end
				selected = nil
			end)
		)
	end

	-- 🔬 Gram sorter: round (cocci) or rod (bacilli) bacteria, stained purple (Gram +) or pink (Gram -)
	local belt = find("SorterBelt")
	local sample = nil
	spawnSample = function()
		if sample and sample.part.Parent then
			sample.part:Destroy()
		end
		sample = nil
		if not (belt and ctx.running and orderOf("sort")) then
			return
		end
		local shape, gram = math.random(1, 2), math.random(1, 2)
		local part = temp(Instance.new("Part"))
		part.Name = "Sample"
		part.Shape = shape == 1 and Enum.PartType.Ball or Enum.PartType.Cylinder
		part.Size = shape == 1 and Vector3.new(2.2, 2.2, 2.2) or Vector3.new(3.4, 1.6, 1.6)
		part.Anchored, part.CanCollide = true, false
		part.Color = GRAM[gram][2]
		part.Material = Enum.Material.SmoothPlastic
		part.CFrame = belt.CFrame + Vector3.new(0, 1.2, 0)
		part.Parent = arena
		TweenService
			:Create(part, TweenInfo.new(2.5, Enum.EasingStyle.Sine), { CFrame = belt.CFrame + Vector3.new(6, 1.2, 0) })
			:Play()
		sample = { part = part, shape = shape, gram = gram }
	end
	for i = 1, 2 do
		local bin = find("SortBin|" .. i)
		if bin then
			ctx.connect(prompt(bin, "حط العيّنة هنا", "صندوق " .. i).Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				local o = orderOf("sort")
				if not (o and sample) then
					notify(player, "ما في عيّنة للفرز الحين")
					return
				end
				local want = o.rule == "gram" and sample.gram or sample.shape
				if want == i then
					o.count += 1
					flash(bin, Color3.fromRGB(80, 220, 120))
					if o.count >= 3 then
						complete(o, player)
						if sample and sample.part.Parent then
							sample.part:Destroy()
						end
						sample = nil
						return
					end
				else
					flash(bin, Color3.fromRGB(230, 70, 70))
					notify(
						player,
						o.rule == "gram"
								and "❌ البنفسجي = موجبة جرام، الوردي = سالبة جرام"
							or "❌ الكروية مدوّرة، والعصوية شكلها عصا"
					)
				end
				refresh()
				task.delay(0.6, spawnSample)
			end))
		end
	end

	-- 🌀 centrifuge: two tubes on opposite sides keep it balanced, so both go in together
	local window = nPlayers <= 1 and 7 or 2.5
	local lastPull = {}
	local core = find("ReactorCore")
	for i = 1, 2 do
		local lever = find("ReactorLever|" .. i)
		if lever then
			ctx.connect(prompt(lever, "حط الأنبوب", "أنبوب " .. i).Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				local o = orderOf("centrifuge")
				if not o then
					notify(player, "ما في طلب طرد مركزي الحين")
					return
				end
				lastPull[i] = os.clock()
				flash(lever, Color3.fromRGB(120, 255, 200), 0.6)
				local other = lastPull[3 - i]
				if other and os.clock() - other <= window then
					table.clear(lastPull)
					if core then
						flash(core, Color3.fromRGB(255, 255, 160), 1.2)
						task.spawn(function() -- the rotor spins (a full-turn tween would take the short way round)
							for _ = 1, 24 do
								if not core.Parent then
									break
								end
								core.CFrame *= CFrame.Angles(0, math.rad(45), 0)
								task.wait(0.05)
							end
						end)
					end
					complete(o, player)
				else
					notify(
						player,
						("⚖️ الجهاز مو متوازن! الأنبوب الثاني خلال %d ثواني"):format(
							window
						)
					)
				end
			end))
		end
	end

	for _ = 1, 3 do
		newOrder()
	end
	refresh()
end

function M.stop(ctx)
	for _, p in ipairs(ctx.prompts or {}) do
		p:Destroy()
	end
	for _, t in ipairs(ctx.temp or {}) do
		if t.Parent then
			t:Destroy()
		end
	end
	for _, part in ipairs(ctx.arena:GetChildren()) do
		if part:IsA("BasePart") then
			local base = part:GetAttribute("BaseColor")
			if base then
				part.Color = base
			end
			if part.Name:match("^MutIngredient") then
				part.Material = Enum.Material.SmoothPlastic
			end
		end
	end
	local board = ctx.arena:FindFirstChild("OrderBoard")
	local label = board and board:FindFirstChildWhichIsA("TextLabel", true)
	if label then
		label.Text = "🧪 مختبر السباق\nLab Rush"
	end
end

return M
