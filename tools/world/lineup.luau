-- test place: a labelled row of key pack items, to check facing/size in Studio
local fs = require("@lune/fs")
local roblox = require("@lune/roblox")
local L = require("./lib")
local Instance, Vector3, CFrame = roblox.Instance, roblox.Vector3, roblox.CFrame
local game = Instance.new("DataModel")
local ws = game:GetService("Workspace")
local base = Instance.new("Part")
base.Size = Vector3.new(1200, 1, 200)
base.CFrame = CFrame.new(500, -0.5, 0)
base.Anchored = true
base.Parent = ws
local items = { "Bld_CityHall_01", "Bld_Station_01", "Bld_Station_03", "Env_SubwayEntrance_01", "Bld_Shop_01", "Bld_Shop_03",
	"Bld_Shop_Corner_01", "Prop_BusStop_01", "Prop_HotdogStand_01", "Prop_ParkBench_01", "Tree_Round_01", "Tree_TallRound_01",
	"Prop_Bridge_Curved_01", "Rock_Cluster_Large_01", "Bld_OfficeOld_Small_Base_01", "Prop_LargeSign_Coffee_01" }
local x = 0
local f = L.folder(ws, "Lineup")
for _, k in items do
	local p = L.place(f, k, x, 0, 0)
	x += p.Size.X + 14
end
fs.writeFile("lineup_test.rbxl", roblox.serializePlace(game))
print("ok", x)
