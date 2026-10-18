-- Cart Ride: touching the "CartStart" pad gives the player their own cart (a clone of "CartTemplate"),
-- welded to its seat and owned by that player's client, so every player sees everyone riding.
-- The rider's client drives it along the track; it tells us "stop" when the ride ends.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local mapFolder = workspace:WaitForChild("Map")
local template, startPad, spawnPoint
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("Model") and inst.Name == "CartTemplate" then
		template = inst
	elseif inst:IsA("BasePart") and inst.Name == "CartStart" then
		startPad = inst
	elseif inst:IsA("BasePart") and inst.Name == "CartSpawnPoint" then
		spawnPoint = inst
	end
end
if not (template and startPad and spawnPoint) then
	warn("CartRide: template, start pad or spawn point missing")
	return
end

local remote = Instance.new("RemoteEvent")
remote.Name = "CartRide"
remote.Parent = ReplicatedStorage

local carts = {} -- [Player] = Model

local function removeCart(player)
	local cart = carts[player]
	carts[player] = nil
	if cart then
		cart:Destroy()
	end
end

local function spawnCart(player)
	if carts[player] then
		return
	end
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not (hum and root and hum.Health > 0) then
		return
	end
	local cart = template:Clone()
	cart.Name = "Cart_" .. player.UserId
	local seat = cart:FindFirstChild("Seat")
	if not seat then
		cart:Destroy()
		return
	end
	for _, p in ipairs(cart:GetDescendants()) do
		if p:IsA("BasePart") then
			p.Anchored = false
			p.CanCollide = false
			p.CanQuery = false
			p.Massless = true
			if p ~= seat then
				p.CanTouch = false
				local weld = Instance.new("WeldConstraint")
				weld.Part0 = seat
				weld.Part1 = p
				weld.Parent = p
			end
		end
	end
	cart.PrimaryPart = seat
	cart:PivotTo(spawnPoint.CFrame + Vector3.new(0, 3, 0))
	cart.Parent = workspace
	carts[player] = cart
	seat:Sit(hum)
	task.defer(function()
		pcall(function()
			seat:SetNetworkOwner(player)
		end)
		remote:FireClient(player, "start", cart)
	end)
end

local touchCooldown = {}
startPad.Touched:Connect(function(hit)
	local player = Players:GetPlayerFromCharacter(hit.Parent)
	if not player then
		return
	end
	if touchCooldown[player] and os.clock() - touchCooldown[player] < 3 then
		return
	end
	touchCooldown[player] = os.clock()
	spawnCart(player)
end)

-- v31 actions from the rider's client: "stop" (train gone, nothing else), "station" (step off onto the platform),
-- "island" (end-of-line button), "again" (a fresh train at the station). Moves always use the safe teleport.
local Teleport = require(script.Parent.Teleport)
local islandSpawn = mapFolder:FindFirstChild("IslandSpawn", true)
local lastAction = {}
remote.OnServerEvent:Connect(function(player, action)
	if typeof(action) ~= "string" then
		return
	end
	local now = os.clock()
	if action ~= "stop" and lastAction[player] and now - lastAction[player] < 1.5 then
		return
	end
	lastAction[player] = now
	removeCart(player)
	if action == "station" then
		Teleport.to(player, spawnPoint)
	elseif action == "island" and islandSpawn then
		Teleport.to(player, islandSpawn)
	elseif action == "again" then
		Teleport.to(player, spawnPoint)
		task.delay(0.4, function()
			if player.Parent then
				spawnCart(player)
			end
		end)
	end
end)

Players.PlayerAdded:Connect(function(player)
	player.CharacterRemoving:Connect(function()
		removeCart(player)
	end)
end)
for _, player in ipairs(Players:GetPlayers()) do
	player.CharacterRemoving:Connect(function()
		removeCart(player)
	end)
end
Players.PlayerRemoving:Connect(function(player)
	removeCart(player)
	touchCooldown[player] = nil
	lastAction[player] = nil
end)
