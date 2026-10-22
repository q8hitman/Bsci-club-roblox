-- Server setup for PCR lifecycle tests. Run in an unpublished disposable Play session.
local player = game.Players:GetPlayers()[1]
local bench = workspace.Map:FindFirstChild("Bench|pcr", true)
local qa = game.ServerStorage.Labs54QA
player.Character:PivotTo(bench:GetPivot() * CFrame.new(9, 2, 0))
qa:Invoke(player, "ppe")
qa:Invoke(player, "pcr|item|pipette")
for _, reagent in ipairs({ "template", "primers", "dntp", "pcrbuffer", "taq" }) do
	qa:Invoke(player, "pcr|use|" .. reagent)
	qa:Invoke(player, "pcr|slot|rack")
end
qa:Invoke(player, "pcr|item|tube")
qa:Invoke(player, "pcr|slot|cycler")
return { research = player:GetAttribute("Research") }
