-- World characters: spawned on the "NPC|<id>" markers (tools/island11.npc_markers, placed by role), each with a look,
-- Talking (ProximityPrompt) sends the lines to the client, which shows them in a dialogue box.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local talk = Instance.new("RemoteEvent")
talk.Name = "NPCTalk"
talk.Parent = ReplicatedStorage

local SKIN = { Color3.fromRGB(255, 214, 170), Color3.fromRGB(226, 176, 130), Color3.fromRGB(190, 140, 100) }
local WHITE = Color3.fromRGB(245, 245, 245)

local NPC = {
	dr_sara = {
		hair = 7193454569,
		name = "د. سارة 🔬",
		role = "أستاذة مايكروبيولوجي",
		shirt = WHITE,
		pants = Color3.fromRGB(40, 50, 80),
		skin = 1,
		lines = {
			"هلا بمعهد الأبحاث! جرّب المجهر الضوئي وصبغة جرام على الطاولات 🔬",
			"تدري إن بكتيريا E. coli ممكن تتضاعف كل 20 دقيقة؟ مثل مشاريعي المتأخرة 😅",
			"صبغة جرام تفرّق البكتيريا حسب جدارها: الموجبة بنفسجية والسالبة وردية 🧫",
		},
	},
	abu_ali = {
		hair = 62234425,
		name = "أبو علي 🛡️",
		role = "حارس المقر",
		shirt = Color3.fromRGB(40, 60, 90),
		pants = Color3.fromRGB(30, 30, 34),
		skin = 2,
		lines = {
			"ممنوع الركض بالممرات… إلا ببوابات الباركور 😂",
			"قاعة بوابات العوالم ورا هالباب: كل عالم له بوابته 🌍",
			"شفت قطوة ذهبية فوق مبنى أحمر بالكلية؟ لا تقول لأحد 🤫",
		},
	},
	noura = {
		hair = 9244148336,
		name = "نورة 🎒",
		role = "طالبة مستجدة • كلية العلوم",
		shirt = Color3.fromRGB(200, 150, 220),
		pants = Color3.fromRGB(60, 60, 90),
		skin = 1,
		lines = {
			"أول يوم لي بكلية العلوم ضعت… بعدين عرفت إن الممر الأحمر هو الطريق للمبنى الشمالي 🙈",
			"بوابة مقر النادي هنا باللوبي، ومن المقر تروح لكل العوالم 🏠",
			"يقولون الأركيد فيها طفرة تخليك عملاق! 🦖",
		},
	},
	yousef = {
		hair = 63690008,
		name = "يوسف الدافور 📚",
		role = "بطل الاختبارات العلمية",
		shirt = Color3.fromRGB(70, 140, 100),
		pants = Color3.fromRGB(50, 50, 56),
		skin = 3,
		lines = {
			"سر النجاح بقاعة الاختبارات: لا تمشي ورا الناس… امشِ ورا الجواب العلمي 😎",
			"أي سؤال ما تعرفه؟ الجواب الميتوكوندريا! (مو دايماً 😂)",
			"كل تخصص له ثلاث مستويات هنا بمركز التحديات… كمّلها كلها 🏆",
		},
	},
	chef = {
		hair = 376548738,
		name = "الشيف بروتين 🍔",
		role = "مقهى النادي • المقر",
		shirt = WHITE,
		pants = Color3.fromRGB(30, 30, 34),
		skin = 2,
		lines = {
			"اطلب من الكاونتر مجاناً: كرك، قهوة، شاي أو كوكيز DNA ☕🍪",
			"الكافيين يحجب مستقبلات الأدينوسين… عشان كذا القهوة تصحّيك لمحاضرة 8 الصبح 🥱",
		},
	},
	lifeguard = {
		hair = 376524487,
		name = "مرشد المتحف 🏺",
		role = "متحف العلوم التفاعلي",
		shirt = Color3.fromRGB(230, 70, 60),
		pants = Color3.fromRGB(240, 200, 70),
		skin = 3,
		lines = {
			"المتحف فيه ثمانية معارض تفاعلية، واحد لكل جانب من علوم الأحياء 🧬",
			"جرّب كل معرض: كل واحد يعطيك ختم بجواز BSC ✨",
		},
	},
	gamer = {
		hair = 451221329,
		name = "هيثم القيمر 🎮",
		role = "صالة الألعاب",
		shirt = Color3.fromRGB(240, 110, 200),
		pants = Color3.fromRGB(40, 40, 60),
		skin = 1,
		lines = {
			"كل جولة لعبة غير وطفرة مفاجئة… ادخل وجرّب حظك!",
			"جربت سباق الميكروبات والهروب من الليزر؟ تنافس مع الربع على الصدارة! 🏎️⚡",
		},
	},
	cat_lady = {
		hair = 2956239660,
		name = "أم القطاوة 🐱",
		role = "حديقة كلية العلوم",
		shirt = Color3.fromRGB(250, 222, 170),
		pants = Color3.fromRGB(120, 90, 70),
		skin = 2,
		lines = {
			"بالكلية 12 قطوة مخفية… لقيتهم كلهم؟",
			"أعطيهم أكل بس مو حليب: أغلب القطط البالغة ما تهضم اللاكتوز زين 🥛",
		},
	},
	invigilator = {
		hair = 62234425,
		name = "المراقب 📵",
		role = "قاعة الاختبارات",
		shirt = Color3.fromRGB(60, 60, 70),
		pants = Color3.fromRGB(30, 30, 34),
		skin = 2,
		lines = {
			"الجوالات مقفلة؟ 📵 الاختبار بيبدأ!",
			"اختار جوابك وقف عليه قبل ما ينقفل… والغلط يفتح الأرض تحته 😏",
		},
	},
}

local IDLE = "rbxassetid://507766666" -- Roblox default R15 idle

local function makeNPC(marker, id, def)
	local desc = Instance.new("HumanoidDescription")
	local skin = SKIN[def.skin] or SKIN[1]
	desc.HeadColor = skin
	desc.LeftArmColor = def.shirt
	desc.RightArmColor = def.shirt
	desc.TorsoColor = def.shirt
	desc.LeftLegColor = def.pants
	desc.RightLegColor = def.pants
	-- free official Roblox hair (catalog creator "Roblox"); if it fails to load, fall back to no hair
	if def.hair then
		desc.HairAccessory = tostring(def.hair)
	end
	local ok, model = pcall(function()
		return Players:CreateHumanoidModelFromDescription(desc, Enum.HumanoidRigType.R15)
	end)
	if not ok and def.hair then
		desc.HairAccessory = ""
		ok, model = pcall(function()
			return Players:CreateHumanoidModelFromDescription(desc, Enum.HumanoidRigType.R15)
		end)
	end
	if not ok or not model then
		warn("NPC failed: " .. id)
		return
	end
	model.Name = "NPC_" .. id
	local hum = model:FindFirstChildOfClass("Humanoid")
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	-- anchored statue-like NPC: without this, clients see the humanoid stuck in FallingDown (tipped-over pose)
	hum.EvaluateStateMachine = false
	local root = model:FindFirstChild("HumanoidRootPart")
	-- stand the feet on whatever is under the marker (runtime terrain or a floor), facing the path
	local params = RaycastParams.new()
	params.FilterDescendantsInstances = { model, marker }
	params.RespectCanCollide = true -- skip flowers/decor
	local hit = workspace:Raycast(marker.Position + Vector3.new(0, 12, 0), Vector3.new(0, -40, 0), params)
	local groundY = hit and hit.Position.Y or (marker.Position.Y - marker.Size.Y / 2)
	local rootY = groundY + hum.HipHeight + root.Size.Y / 2
	model:PivotTo(
		CFrame.new(marker.Position.X, rootY, marker.Position.Z) * marker.CFrame.Rotation * CFrame.Angles(0, math.pi, 0)
	)
	root.Anchored = true
	model.Parent = workspace
	-- name tag
	local head = model:FindFirstChild("Head")
	local bb = Instance.new("BillboardGui")
	bb.Size = UDim2.fromOffset(220, 46)
	bb.StudsOffset = Vector3.new(0, 2.8, 0)
	bb.MaxDistance = 70
	local t = Instance.new("TextLabel")
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundTransparency = 1
	t.TextColor3 = Color3.new(1, 1, 1)
	t.TextStrokeTransparency = 0.3
	t.TextScaled = true
	t.Font = Enum.Font.GothamBold
	t.Text = def.name .. "\n" .. def.role
	t.Parent = bb
	bb.Parent = head
	-- idle animation
	local animator = hum:FindFirstChildOfClass("Animator") or Instance.new("Animator", hum)
	local anim = Instance.new("Animation")
	anim.AnimationId = IDLE
	pcall(function()
		local track = animator:LoadAnimation(anim)
		track.Looped = true
		track:Play()
	end)
	-- talk prompt
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "تكلّم"
	prompt.ObjectText = def.name
	prompt.MaxActivationDistance = 12
	prompt.RequiresLineOfSight = false
	prompt.Parent = root
	prompt.Triggered:Connect(function(player)
		-- turn to face whoever is talking to them
		local proot = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		if proot then
			local target = Vector3.new(proot.Position.X, root.Position.Y, proot.Position.Z)
			if (target - root.Position).Magnitude > 0.5 then
				root.CFrame = CFrame.lookAt(root.Position, target)
			end
		end
		talk:FireClient(player, def.name, def.role, def.lines, model)
	end)
end

local mapFolder = workspace:WaitForChild("Map")
-- v52: the island terrain is gone, so there is nothing to wait for; give the map a moment to load
task.wait(0.5)
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local id = inst.Name:match("^NPC|(.+)$")
		if id and NPC[id] then
			task.spawn(makeNPC, inst, id, NPC[id])
		end
	end
end
