-- v53 multiplayer QA, client side (see v53.server.luau)
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "V53" then
	return
end
local p = game.Players.LocalPlayer
local rs = game.ReplicatedStorage
local done = rs:WaitForChild("V53QADone")
local ok, result = pcall(function()
	repeat
		task.wait(0.1)
	until p:GetAttribute("V53Go")
	repeat
		task.wait(0.1)
	until _G.BSCCartToggle
	_G.BSCCartToggle() -- press ▶ on our own train
	-- watch the OTHER player's server cart replicate to us while it moves
	local other
	for _, q in ipairs(game.Players:GetPlayers()) do
		if q ~= p then
			other = q
		end
	end
	local cart = workspace:WaitForChild("Cart_" .. other.UserId, 10)
	local p0 = cart and cart.PrimaryPart and cart.PrimaryPart.Position
	task.wait(8)
	local p1 = cart and cart.PrimaryPart and cart.PrimaryPart.Position
	local sawOtherCart = p0 ~= nil and p1 ~= nil and (p1 - p0).Magnitude > 30
	repeat
		task.wait(0.1)
	until p:GetAttribute("V53Lab")
	if _G.BSCEndCart then
		_G.BSCEndCart()
	end
	-- Gram stain through the real remote, both players at the same time, proper decolouriser time
	local labFn = rs:WaitForChild("Lab", 10)
	local g = labFn:InvokeServer("gram")
	assert(g and g.token and g.gram == nil, "gram start must not reveal the answer")
	task.wait(5)
	local v = labFn:InvokeServer("gramView", g.token, 5)
	assert(v and v.quality == "ok", "gramView quality")
	local again = labFn:InvokeServer("gramView", g.token, 5)
	assert(again == nil, "gramView must be single-use")
	local r = labFn:InvokeServer("answer", g.token, v.color == "violet" and "pos" or "neg")
	task.wait(1)
	return {
		ok = true,
		sawOtherCart = sawOtherCart,
		gramOk = r and r.ok,
		gained = r and r.gained or 0,
		firstDay = p:GetAttribute("FirstDay") or "",
	}
end)
done:FireServer(if ok then result else { ok = false, error = tostring(result) })
