-- Pure authoritative planar driving. No client positions, checkpoints, laps or reward claims are inputs.
local M = {}
local function finite(v)
	return type(v) == "number" and v == v and math.abs(v) < 1e8
end
local function clamp(v, lo, hi)
	return finite(v) and math.clamp(v, lo, hi) or 0
end
local function distance(x, z, a, b)
	return math.sqrt((x - a) ^ 2 + (z - b) ^ 2)
end
local function angle(a)
	return (a + math.pi) % (2 * math.pi) - math.pi
end
function M.input(raw)
	raw = type(raw) == "table" and raw or {}
	return {
		throttle = clamp(raw.throttle, 0, 1),
		brake = clamp(raw.brake, 0, 1),
		steer = clamp(raw.steer, -1, 1),
		boost = raw.boost == true,
		drift = raw.drift == true,
	}
end
local function segment(x, z, a, b, width)
	local dx, dz = b[1] - a[1], b[2] - a[2]
	local t = math.clamp(((x - a[1]) * dx + (z - a[2]) * dz) / (dx * dx + dz * dz), 0, 1)
	local qx, qz = a[1] + dx * t, a[2] + dz * t
	local d = distance(x, z, qx, qz)
	return { x = qx, z = qz, d = d, limit = width / 2 - 3.5, excess = math.max(0, d - (width / 2 - 3.5)) }
end
function M.road(track, x, z)
	local best
	for i, a in ipairs(track.points) do
		local b = track.points[i % #track.points + 1]
		local q = segment(x, z, a, b, track.width)
		if not best or q.excess < best.excess or (q.excess == best.excess and q.d < best.d) then
			best = q
		end
	end
	if track.shortcut then
		local s = track.shortcut
		local q = segment(x, z, track.points[s.a], track.points[s.b], s.width)
		if q.excess < best.excess or (q.excess == best.excess and q.d < best.d) then
			best = q
		end
	end
	return best
end
-- v60 kart contact: two karts closer than 5 studs are pushed apart along the line between them (half each),
-- then kept inside the road corridor. No spin-out and no speed is taken; bumping just shoves.
function M.separate(a, b, track)
	local dx, dz = b.x - a.x, b.z - a.z
	local d = math.sqrt(dx * dx + dz * dz)
	if d < 1e-3 or d >= 5 then
		return false
	end
	local push = (5 - d) / 2
	local nx, nz = dx / d, dz / d
	a.x, a.z = a.x - nx * push, a.z - nz * push
	b.x, b.z = b.x + nx * push, b.z + nz * push
	for _, s in ipairs({ a, b }) do
		local road = M.road(track, s.x, s.z)
		if road.excess > 0 then
			local ex, ez = s.x - road.x, s.z - road.z
			s.x, s.z = road.x + ex / road.d * road.limit, road.z + ez / road.d * road.limit
		end
	end
	return true
end
function M.start(track, offset)
	local a, b = track.points[1], track.points[2]
	local h = math.atan2(b[1] - a[1], b[2] - a[2])
	return {
		x = a[1] - math.cos(h) * (offset or 0),
		z = a[2] + math.sin(h) * (offset or 0),
		heading = h,
		speed = 0,
		time = 0,
		lap = 1,
		gate = 1,
		lastPoint = 1,
		botTarget = 2,
		boostUntil = 0,
		boostReadyAt = 0,
		shieldUntil = 0,
		slowUntil = 0,
		hazardAt = -10,
		pickups = {},
		done = false,
	}
end
function M.recover(s, track)
	if s.done then
		return
	end
	local i = s.lastPoint
	local a, b = track.points[i], track.points[i % #track.points + 1]
	s.x, s.z = a[1], a[2]
	s.heading = math.atan2(b[1] - a[1], b[2] - a[2])
	s.speed = 0
	s.drift, s.driftCharge, s.driftTier, s.steerV = 0, 0, 0, 0
	s.botTarget = i % #track.points + 1
end
-- v60 arcade handling (shared by the server, the driver's client prediction and the bots; deterministic):
-- eased acceleration, smoothed speed-sensitive steering, a hold-to-drift with three charge tiers that pays out a
-- mini-turbo, gentle wall slides, and an automatic recovery when a kart is stuck.
M.TUNING = {
	top = 42, -- studs/s on throttle
	boost = 60, -- manual boost pad / button
	turbo = 54, -- drift mini-turbo
	accel = 1.15, -- ease toward top speed (per second)
	push = 7, -- extra launch from standstill (studs/s^2)
	coast = 5, -- slow down when off the throttle
	brake = 60,
	yaw = 2.3, -- rad/s at full lock
	steerRate = 9, -- how fast the wheel follows the stick (per second)
	driftMin = 20, -- speed needed to start a drift
	driftYaw = 1.25, -- full inward drift turns ~1.25x a normal full-lock turn (v60 Studio test: 1.45 hit the inner wall)
	tiers = { 0.45, 0.9, 1.5 }, -- seconds of inward drifting for blue / orange / purple sparks (MK ratios scaled to
	-- our ~50-stud bends: the v60 Studio test never reached 0.8 s before the bend ended)
	turboTime = { 0.45, 0.8, 1.2 },
	wallKeep = 0.96, -- speed kept per step against a barrier
}
local T = M.TUNING

-- ends a drift; returns true when it paid out a mini-turbo (the caller lifts the speed)
local function endDrift(s, pay)
	local paid = s.drift ~= 0 and pay and (s.driftTier or 0) > 0
	if paid then
		s.turboUntil = s.time + T.turboTime[s.driftTier]
	end
	s.drift, s.driftCharge, s.driftTier = 0, 0, 0
	return paid
end

function M.step(s, raw, dt, track)
	if s.done then
		return
	end
	dt = clamp(dt, 0, 0.1)
	local input = M.input(raw)
	s.time += dt
	s.drift = s.drift or 0
	s.steerV = s.steerV or 0
	s.turboUntil = s.turboUntil or 0
	if input.boost and s.time >= s.boostReadyAt then
		s.boostUntil = s.time + 1.6
		s.boostReadyAt = s.time + 10
	end
	-- speed: eased toward the cap, launch push from standstill, gentle coast, firm brake
	local top = s.topSpeed or T.top -- v59: bots get a lower topSpeed
	local maxSpeed = top
	if s.time < s.boostUntil then
		maxSpeed = T.boost
	elseif s.time < s.turboUntil then
		maxSpeed = math.max(top, T.turbo)
	end
	if s.time < s.slowUntil then
		maxSpeed = math.min(maxSpeed, 22)
	end
	local v = s.speed
	if input.throttle > 0 or s.time < s.boostUntil or s.time < s.turboUntil then
		local want = s.time < s.boostUntil and 1 or math.max(input.throttle, s.time < s.turboUntil and 1 or 0)
		v += ((maxSpeed - v) * T.accel + T.push * math.max(0, 1 - v / math.max(maxSpeed, 1))) * want * dt
	else
		v -= (T.coast + v * 0.12) * dt
	end
	v -= input.brake * T.brake * dt
	if v > maxSpeed then -- over the cap (a boost ended, or a slowdown): ease down instead of snapping
		v = math.max(maxSpeed, v - 30 * dt)
	end
	v = math.clamp(v, 0, T.boost)
	-- steering: the wheel follows the stick smoothly; turn rate grows with speed, then eases off near the top
	s.steerV += math.clamp(input.steer - s.steerV, -T.steerRate * dt, T.steerRate * dt)
	local grip = math.min(1, v / 12) * (1 - 0.3 * math.min(v, T.boost) / T.boost)
	-- drift: hold the drift input while steering at speed; the kart turns tighter toward the drift side, the stick
	-- widens or tightens the arc, and the charge pays out a mini-turbo when the drift is released
	if s.drift == 0 and input.drift and math.abs(s.steerV) > 0.3 and v >= T.driftMin then
		s.drift, s.driftCharge, s.driftTier = s.steerV > 0 and 1 or -1, 0, 0
	elseif s.drift ~= 0 and (not input.drift or v < T.driftMin - 6) then
		if endDrift(s, input.drift == false and v >= T.driftMin - 6) then
			v = math.max(v, T.turbo - 6)
		end
	end
	local yaw
	if s.drift ~= 0 then
		yaw = s.drift * T.yaw * T.driftYaw * grip * (0.5 + 0.5 * s.steerV * s.drift) -- stick: outward 0 .. inward 1
		v *= 0.997
		-- steering into the drift charges 2.5x faster than holding it wide: the skill is in the line
		s.driftCharge += dt * (s.steerV * s.drift >= 0.5 and 1 or 0.4)
		local tier = 0
		for i, need in ipairs(T.tiers) do
			if s.driftCharge >= need then
				tier = i
			end
		end
		s.driftTier = tier
	else
		yaw = s.steerV * T.yaw * grip
	end
	s.yawRate = yaw
	s.heading = angle(s.heading + yaw * dt)
	local x, z = s.x + math.sin(s.heading) * v * dt, s.z + math.cos(s.heading) * v * dt
	local road = M.road(track, x, z)
	s.wall = false
	if road.excess > 0 then
		local dx, dz = x - road.x, z - road.z
		-- step 0.3 off the barrier, so a kart that is now running along it is free on the next tick
		x, z = road.x + dx / road.d * (road.limit - 0.3), road.z + dz / road.d * (road.limit - 0.3)
		-- slide along the barrier: keep most of the speed and turn the heading toward the wall's tangent
		local tx, tz = -dz / road.d, dx / road.d
		if tx * math.sin(s.heading) + tz * math.cos(s.heading) < 0 then
			tx, tz = -tx, -tz
		end
		local along = math.atan2(tx, tz)
		local diff = angle(along - s.heading)
		-- a glancing touch lines the kart up with the wall at once (v60 Studio: 35 % per tick kept a kart rubbing
		-- the wall at ~26 studs/s); a head-on hit turns it gradually
		s.heading = angle(s.heading + diff * (math.abs(diff) < 0.35 and 1 or 0.35))
		v *= T.wallKeep
		s.wall = true
		if s.drift ~= 0 and math.abs(diff) >= 0.35 then
			endDrift(s, false) -- a head-on hit ends the drift without a payout (no spin-out); a glancing touch keeps it
		end
	end
	s.speed = v
	s.x, s.z = x, z
	-- stuck (e.g. nose in a corner) for 3 s while trying to drive: back to the last checkpoint
	if input.throttle > 0 and v < 2 then
		s.stuckFor = (s.stuckFor or 0) + dt
		if s.stuckFor > 3 then
			s.stuckFor = 0
			M.recover(s, track)
		end
	else
		s.stuckFor = 0
	end
	for _, p in ipairs(track.pickups) do
		if s.time >= (s.pickups[p.id] or 0) and distance(x, z, p.x, p.z) < 5 then
			s.pickups[p.id] = s.time + 8
			if p.kind == "boost" then
				s.boostUntil = s.time + 1.6
			else
				s.shieldUntil = s.time + 8
			end
		end
	end
	for _, h in ipairs(track.hazards) do
		if s.time - s.hazardAt > 1.2 and distance(x, z, h.x, h.z) < h.r + 2 then
			s.hazardAt = s.time
			if s.shieldUntil > s.time then
				s.shieldUntil = 0
			else
				s.speed *= 0.6 -- v60: a stumble, not a stop
				s.slowUntil = s.time + 0.6
			end
		end
	end
	local index = track.gates[s.gate]
	local gate = track.points[index]
	if distance(x, z, gate[1], gate[2]) < 12 then
		s.lastPoint = index
		s.gate += 1
		if s.gate > #track.gates then
			s.gate = 1
			s.lap += 1
			if s.lap == 4 then
				s.done = true
				s.finishedAt = s.time
				s.speed = 0
			end
		end
	end
end
-- v60 bots drive like a decent player: look 16 studs ahead, steer proportionally, drift long bends (so they earn
-- mini-turbos too) and never brake; their pace comes from topSpeed (36/38/40, eased +-6 % by the server)
function M.botInput(s, track)
	local target = track.points[s.botTarget]
	if distance(s.x, s.z, target[1], target[2]) < 16 then
		s.botTarget = s.botTarget % #track.points + 1
		target = track.points[s.botTarget]
	end
	local delta = angle(math.atan2(target[1] - s.x, target[2] - s.z) - s.heading)
	if not s.botDrift and math.abs(delta) > 0.55 and s.speed > 25 then
		s.botDrift = true
	elseif s.botDrift and math.abs(delta) < 0.12 then
		s.botDrift = false
	end
	return {
		throttle = 1,
		brake = 0,
		steer = math.clamp(delta * 2.4, -1, 1),
		boost = false,
		drift = s.botDrift == true,
	}
end
function M.progress(s, track)
	if s.done then
		return 1e6 - (s.finishedAt or 0)
	end
	local g = track.points[track.gates[s.gate]]
	return (s.lap - 1) * #track.gates + s.gate - 1 + 1 / (1 + distance(s.x, s.z, g[1], g[2]))
end
return M
