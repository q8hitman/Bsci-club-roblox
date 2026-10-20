-- Order point: ShopOrder|10..13 = the club café counter in the HQ (tools/hq_fill.py). v52: the nine island food-street
-- kiosks (ShopOrder|1..9) were removed with the island; the café keeps the same free snack + science fact.
-- Ordering is free: the player gets a small snack to hold (a Tool) and a short, checked food-science fact.
-- Click / tap while holding it to "eat" it. One snack at a time; a short cooldown stops prompt spam.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local notify = ReplicatedStorage:WaitForChild("Notify")
local mapFolder = workspace:WaitForChild("Map")

local MENU = {
	{
		"قهوة ☕",
		Color3.fromRGB(110, 70, 40),
		"الكافيين يحجب مستقبلات الأدينوسين، فيخفّ الإحساس بالنعاس",
	},
	{
		"كرواسون 🥐",
		Color3.fromRGB(220, 170, 90),
		"الخميرة فطر يخمّر السكر ويطلع CO₂ فينتفخ العجين",
	},
	{
		"دونات 🍩",
		Color3.fromRGB(240, 140, 180),
		"شكل DNA الحلزوني انكشف سنة 1953 بمساعدة صور روزاليند فرانكلين",
	},
	{
		"سلطة 🥗",
		Color3.fromRGB(90, 180, 80),
		"الكلوروفيل يمتص الضوء الأحمر والأزرق ويعكس الأخضر",
	},
	{
		"ميلك شيك 🥤",
		Color3.fromRGB(150, 220, 140),
		"إنزيم اللاكتيز يهضم سكر الحليب (اللاكتوز)",
	},
	{
		"آيس كريم 🍦",
		Color3.fromRGB(250, 236, 210),
		"الميتوكوندريا تنتج أغلب الـ ATP في الخلية",
	},
	{
		"برجر 🍔",
		Color3.fromRGB(170, 100, 50),
		"البروتينات تتكوّن من 20 نوع من الأحماض الأمينية",
	},
	{
		"بيتزا 🍕",
		Color3.fromRGB(240, 200, 80),
		"بكتيريا حمض اللاكتيك تُستخدم في صناعة الجبن واللبن",
	},
	{
		"عصير برتقال 🍊",
		Color3.fromRGB(250, 160, 40),
		"فيتامين C ضروري لبناء الكولاجين",
	},
	-- 10..13: the club café in the HQ (tools/hq_fill.py)
	{
		"كرك ☕",
		Color3.fromRGB(200, 150, 90),
		"الهيل (الحبهان) نبات من نفس عائلة الزنجبيل",
	},
	{
		"قهوة عربية ☕",
		Color3.fromRGB(190, 160, 90),
		"حبوب القهوة هي بذور ثمرة نبات البن",
	},
	{
		"شاي 🍵",
		Color3.fromRGB(150, 60, 40),
		"الشاي الأخضر والأسود من نفس النبتة، الفرق بدرجة الأكسدة",
	},
	{
		"كوكيز DNA 🍪",
		Color3.fromRGB(190, 130, 70),
		"الجينوم البشري فيه تقريباً 3 مليار زوج من القواعد",
	},
}

local lastOrder = {} -- [player] = os.clock()

local function makeSnack(item)
	local tool = Instance.new("Tool")
	tool.Name = item[1]
	tool.ToolTip = "اضغط عشان تاكل"
	tool.CanBeDropped = false
	tool:SetAttribute("BSCSnack", true)
	local handle = Instance.new("Part")
	handle.Name = "Handle"
	handle.Shape = Enum.PartType.Ball
	handle.Size = Vector3.new(1.1, 1.1, 1.1)
	handle.Color = item[2]
	handle.Material = Enum.Material.SmoothPlastic
	handle.CanCollide = false
	handle.Massless = true
	handle.Parent = tool
	tool.Activated:Connect(function()
		local owner = tool.Parent and Players:GetPlayerFromCharacter(tool.Parent)
		if owner then
			notify:FireClient(owner, "😋 بالعافية!", "collect")
		end
		tool:Destroy()
	end)
	return tool
end

local function hasSnack(player)
	for _, where in ipairs({ player:FindFirstChild("Backpack"), player.Character }) do
		if where then
			for _, c in ipairs(where:GetChildren()) do
				if c:IsA("Tool") and c:GetAttribute("BSCSnack") then
					return c
				end
			end
		end
	end
	return nil
end

for _, inst in ipairs(mapFolder:GetDescendants()) do
	local idx = inst:IsA("BasePart") and tonumber(inst.Name:match("^ShopOrder|(%d+)$"))
	local item = idx and MENU[idx]
	if item then
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "اطلب " .. item[1]
		prompt.ObjectText = "مجاناً"
		prompt.MaxActivationDistance = 9
		prompt.RequiresLineOfSight = false
		prompt.HoldDuration = 0
		prompt.Parent = inst
		prompt.Triggered:Connect(function(player)
			local now = os.clock()
			if lastOrder[player] and now - lastOrder[player] < 3 then
				return
			end
			lastOrder[player] = now
			local backpack = player:FindFirstChild("Backpack")
			if not backpack then
				return
			end
			local old = hasSnack(player)
			if old then
				old:Destroy() -- one snack at a time: the new order replaces it
			end
			local snack = makeSnack(item)
			snack.Parent = backpack
			local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
			if hum and hum.Health > 0 then
				hum:EquipTool(snack) -- straight into the hand: one tap / click eats it
			end
			notify:FireClient(player, ("%s جاهز! 🧠 %s"):format(item[1], item[3]), "info")
		end)
	end
end

Players.PlayerRemoving:Connect(function(player)
	lastOrder[player] = nil
end)
