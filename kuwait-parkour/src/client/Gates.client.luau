-- Challenge Hall: shows which zone gates are open for this player, and server notices.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")
local Zones = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Zones"))

local gates = {} -- zone -> { portal, lamp }
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local args = string.split(inst.Name, "|")
		local zone = tonumber(args[3])
		if args[1] == "Portal" and args[2] == "Zone" and zone then
			gates[zone] = gates[zone] or {}
			gates[zone].portal = inst
			gates[zone].color = inst.Color
		elseif args[1] == "GateLamp" and tonumber(args[2]) then
			local z = tonumber(args[2])
			gates[z] = gates[z] or {}
			gates[z].lamp = inst
		end
	end
end

local LOCKED = Color3.fromRGB(200, 60, 60)
local OPEN = Color3.fromRGB(90, 230, 140)

local function refresh()
	local stage = player:GetAttribute("Stage") or 0
	for zone, g in pairs(gates) do
		local z = Zones[zone]
		local unlocked = z ~= nil and stage >= z.start
		if g.portal then
			g.portal.Color = unlocked and (g.color or OPEN) or LOCKED
			g.portal.Transparency = unlocked and 0.45 or 0.8
		end
		if g.lamp then
			g.lamp.Color = unlocked and OPEN or LOCKED
		end
	end
end

player:GetAttributeChangedSignal("Stage"):Connect(refresh)
refresh()

-- server notices (e.g. "zone locked") are shown by Feedback.client
