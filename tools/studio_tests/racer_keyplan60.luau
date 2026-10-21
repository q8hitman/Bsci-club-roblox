-- v60 QA helper: plans a keyboard-only drive (W + A/D + Space drift) with the real RacerMath and prints it as
-- MCP user_keyboard_input actions, so a Studio race can be driven through the real input pipeline.
-- Run: tools/lune/lune.exe run tools/studio_tests/racer_keyplan60.luau <track> [nodrift]
local M = require("../../kuwait-parkour/src/shared/RacerMath")
local D = require("../../kuwait-parkour/src/shared/RacerData")
local process = require("@lune/process")
local stdio = require("@lune/stdio")
local args = process.args
local track = D.get(args[1] or "cell")
local useDrift = args[2] ~= "nodrift"
local s = M.start(track, 4)
local target = 2
local plan = {} -- per tick { left, right, drift }
local function angle(a)
	return (a + math.pi) % (2 * math.pi) - math.pi
end
local drifting = false
for _ = 1, 3000 do
	local pt = track.points[target]
	if math.sqrt((pt[1] - s.x) ^ 2 + (pt[2] - s.z) ^ 2) < 16 then
		target = target % #track.points + 1
		pt = track.points[target]
	end
	local delta = angle(math.atan2(pt[1] - s.x, pt[2] - s.z) - s.heading)
	local steer = math.abs(delta) > 0.06 and (delta > 0 and 1 or -1) or 0
	if useDrift then
		if not drifting and math.abs(delta) > 0.55 and s.speed > 25 then
			drifting = true
		elseif drifting and math.abs(delta) < 0.12 then
			drifting = false
		end
	end
	local input = { throttle = 1, steer = steer, drift = drifting }
	table.insert(plan, { left = steer > 0, right = steer < 0, drift = drifting })
	M.step(s, input, 0.05, track)
	if s.done then
		break
	end
end
-- compress into key transitions
local actions = { { action = "keyDown", key_code = "W" } }
local state = { left = false, right = false, drift = false }
local KEY = { left = "A", right = "D", drift = "Space" }
local waitMs = 0
local function flushWait()
	while waitMs > 0 do
		local w = math.min(waitMs, 10000)
		table.insert(actions, { action = "wait", wait_time_ms = w })
		waitMs -= w
	end
end
for _, t in ipairs(plan) do
	for _, k in ipairs({ "left", "right", "drift" }) do
		if t[k] ~= state[k] then
			flushWait()
			table.insert(actions, { action = t[k] and "keyDown" or "keyUp", key_code = KEY[k] })
			state[k] = t[k]
		end
	end
	waitMs += 50
end
flushWait()
for _, k in ipairs({ "left", "right", "drift" }) do
	table.insert(actions, { action = "keyUp", key_code = KEY[k] })
end
table.insert(actions, { action = "keyUp", key_code = "W" })
stdio.ewrite(
	("planned %s: done=%s time=%.1f s, %d actions\n"):format(track.id, tostring(s.done), s.finishedAt or -1, #actions)
)
local parts = {}
for _, a in ipairs(actions) do
	if a.action == "wait" then
		table.insert(parts, ('{"action":"wait","wait_time_ms":%d}'):format(a.wait_time_ms))
	else
		table.insert(parts, ('{"action":"%s","key_code":"%s"}'):format(a.action, a.key_code))
	end
end
print("[" .. table.concat(parts, ",") .. "]")
