-- v60 Micro Racers handling checks (shared RacerMath; run: tools/lune/lune.exe run tools/test_racers60.luau)
local M = require("../kuwait-parkour/src/shared/RacerMath")
local D = require("../kuwait-parkour/src/shared/RacerData")
local track = D.get("cell")
local function run(s, input, steps)
	for _ = 1, steps do
		M.step(s, input, 0.05, track)
	end
end

-- acceleration is eased: quick launch, ~2.5 s to near top speed, never above it
local s = M.start(track, 0)
run(s, { throttle = 1 }, 20)
local at1 = s.speed
run(s, { throttle = 1 }, 30)
assert(at1 > 18 and at1 < 36, "launch speed after 1 s: " .. at1)
assert(s.speed > 38 and s.speed <= M.TUNING.top + 1e-6, "near top speed by 2.5 s: " .. s.speed)
-- coasting slows gently (no sudden stop)
local v = s.speed
run(s, {}, 20)
assert(s.speed < v and s.speed > v * 0.5, "coast is gentle: " .. s.speed)

-- steering is smoothed and needs speed (no turning on the spot)
local still = M.start(track, 0)
local h = still.heading
run(still, { steer = 1 }, 10)
assert(still.heading == h, "no turning at standstill")

-- drift: starts only at speed while steering, charges three tiers, pays a mini-turbo on release
local d = M.start(track, 0)
run(d, { throttle = 1 }, 30)
d.x, d.z = 0, -90 -- centre of the first straight
run(d, { throttle = 1, steer = 1 }, 4)
M.step(d, { throttle = 1, steer = 1, drift = true }, 0.05, track)
assert(d.drift == 1, "drift starts toward the steering side")
local tiers = {}
for _ = 1, 60 do
	M.step(d, { throttle = 1, steer = 1, drift = true }, 0.05, track)
	if d.drift == 0 then
		break
	end
	tiers[d.driftTier] = true
end
assert(d.drift == 0 or tiers[2], "the drift charged at least to tier 2 (or ended at a wall without a spin-out)")
local turbo = M.start(track, 0)
run(turbo, { throttle = 1 }, 30)
turbo.drift, turbo.driftCharge, turbo.driftTier = 1, 1.6, 3
M.step(turbo, { throttle = 1 }, 0.05, track) -- release
assert(turbo.drift == 0 and turbo.turboUntil > turbo.time, "release pays a mini-turbo")
assert(turbo.speed > M.TUNING.top, "the mini-turbo lifts the speed above top speed")

-- walls: a kart driven straight into a barrier keeps most of its speed and is never stopped dead
local w = M.start(track, 0)
run(w, { throttle = 1 }, 40)
w.heading += math.rad(60)
local minSpeed = math.huge
for _ = 1, 40 do
	M.step(w, { throttle = 1 }, 0.05, track)
	minSpeed = math.min(minSpeed, w.speed)
end
assert(minSpeed > 15, "wall contact slows gently: min " .. minSpeed)
assert(M.road(track, w.x, w.z).excess < 1e-6, "still on the road")

-- stuck for 3 s with the throttle held -> back to the last checkpoint
local stuck = M.start(track, 0)
stuck.x, stuck.z = 500, 500
stuck.topSpeed = 0 -- a kart that cannot move (guards the division too)
local before = stuck.lastPoint
for _ = 1, 70 do
	M.step(stuck, { throttle = 1 }, 0.05, track)
end
local p = track.points[before]
assert(math.abs(stuck.x - p[1]) < 1e-6 and math.abs(stuck.z - p[2]) < 1e-6, "auto-recovered to the checkpoint")

-- bots with the v59 top speeds still finish well inside the time limit
for _, top in ipairs({ 35, 39 }) do
	local bot = M.start(track, 0)
	bot.topSpeed = top
	for _ = 1, 6000 do
		M.step(bot, M.botInput(bot, track), 0.05, track)
		if bot.done then
			break
		end
	end
	assert(bot.done and bot.finishedAt < D.Duration, "bot at " .. top .. " finishes")
	print(("bot top %d: %.1f s"):format(top, bot.finishedAt))
end
print("PASS racers60: eased speed, smoothed steering, drift tiers + mini-turbo, gentle walls, auto-recover, bots")
-- kart contact pushes overlapping karts apart and keeps both on the road
local track2 = D.get("cell")
local a, b = M.start(track2, 0), M.start(track2, 0)
b.x += 2
assert(M.separate(a, b, track2), "overlap detected")
assert(math.abs(b.x - a.x) >= 4.99, "pushed apart to 5 studs")
assert(M.road(track2, a.x, a.z).excess < 1e-6 and M.road(track2, b.x, b.z).excess < 1e-6, "both stay on the road")
print("PASS racers60 contact")
-- a kart rubbing the wall at a shallow angle recovers its speed (v60 Studio finding: it stayed pinned at ~26)
local rub = M.start(track, 0)
rub.x, rub.z, rub.heading, rub.speed = -120, 40, math.pi + 0.25, 30 -- west straight, heading -z, nosed toward the outer wall
local hits = 0
for _ = 1, 40 do
	M.step(rub, { throttle = 1 }, 0.05, track)
	hits += rub.wall and 1 or 0
end
assert(hits <= 3 and rub.speed > 38, ("shallow wall touch: %d contacts, speed %.1f"):format(hits, rub.speed))
print("PASS racers60 wall rub")
