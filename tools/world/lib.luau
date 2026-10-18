-- Shared helpers for building worlds out of the official Roblox Synty packs (run with Lune).
local fs = require("@lune/fs")
local roblox = require("@lune/roblox")

local CFrame, Vector3, Instance, Color3 = roblox.CFrame, roblox.Vector3, roblox.Instance, roblox.Color3

local M = {}

local PACKS = { "6933438443", "6933556508", "6934021345", "6933790012" }
local library = {} -- MeshPart templates

for _, id in PACKS do
	for _, root in roblox.deserializeModel(fs.readFile("tools/packs/" .. id .. ".rbxm")) do
		if root:IsA("MeshPart") then
			table.insert(library, root)
		end
	end
end

local cache = {}
function M.find(key)
	if cache[key] then
		return cache[key]
	end
	for _, t in library do
		local n = t.Name:gsub("%s+$", "") -- some pack names end with a space
		if n:sub(-#key) == key then
			cache[key] = t
			return t
		end
	end
	error("pack item not found: " .. key)
end

M.origin = Vector3.new(0, 0, 0)

-- place a pack mesh; local x/z around the origin, bottom resting on y (default ground 0)
function M.place(parent, key, x, z, yaw, opt)
	opt = opt or {}
	local p = M.find(key):Clone()
	local s = opt.scale or 1
	if s ~= 1 then
		p.Size = p.Size * s
	end
	local y = (opt.y or 0) + p.Size.Y / 2 + (opt.sink and -opt.sink or 0)
	local o = M.origin
	local oldCF = p.CFrame
	p.CFrame = CFrame.new(o.X + x, o.Y + y, o.Z + z) * CFrame.Angles(math.rad(opt.tilt or 0), math.rad(yaw or 0), 0)
	-- v31: some pack meshes carry child parts (e.g. the bus stop's glass). Children do not follow a CFrame change, so they
	-- used to stay at the pack's original spot (inside the campus). Move them with their parent (and scale offsets).
	for _, d in p:GetDescendants() do
		if d:IsA("BasePart") then
			local rel = oldCF:ToObjectSpace(d.CFrame)
			if s ~= 1 then
				rel = CFrame.new(rel.Position * s) * rel.Rotation
				d.Size = d.Size * s
			end
			d.CFrame = p.CFrame * rel
			d.Anchored = true
			d.CanCollide = false
		end
	end
	p.Color = opt.color or Color3.new(1, 1, 1) -- Synty colours live in the mesh (vertex colours); white = true colours
	p.Anchored = true
	p.CanCollide = opt.collide ~= false
	p.CastShadow = opt.shadow ~= false
	if opt.name then
		p.Name = opt.name
	end
	p.Parent = parent
	return p
end

function M.folder(parent, name)
	local f = Instance.new("Folder")
	f.Name = name
	f.Parent = parent
	return f
end

function M.save(root, path)
	fs.writeFile(path, roblox.serializeModel({ root }))
end

return M
