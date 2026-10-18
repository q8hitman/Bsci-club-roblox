-- Server-only (never replicated to clients). Add codes here, then announce them
-- in Discord. Each code can be redeemed once per player.
--   coins   : number granted
--   expires : optional unix timestamp (os.time()); omit for no expiry
local RunService = game:GetService("RunService")

local Codes = {
	-- ["BSC2026"] = { coins = 100, expires = 1798761600 },
}

if RunService:IsStudio() then
	Codes["STUDIO-TEST"] = { coins = 50 } -- only exists when testing in Studio
end

return Codes
