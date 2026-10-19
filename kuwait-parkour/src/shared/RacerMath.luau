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
	s.botTarget = i % #track.points + 1
end
function M.step(s, raw, dt, track)
	if s.done then
		return
	end
	dt = clamp(dt, 0, 0.1)
	local input = M.input(raw)
	s.time += dt
	if input.boost and s.time >= s.boostReadyAt then
		s.boostUntil = s.time + 1.6
		s.boostReadyAt = s.time + 10
	end
	local maxSpeed = s.time < s.boostUntil and 60 or 42
	if s.time < s.slowUntil then
		maxSpeed = 18
	end
	s.speed = math.clamp(s.speed + (input.throttle * 32 - 2 - s.speed * 0.08 - input.brake * 65) * dt, 0, maxSpeed)
	s.heading = angle(s.heading + input.steer * (1.9 - 0.5 * s.speed / 60) * dt)
	local x, z = s.x + math.sin(s.heading) * s.speed * dt, s.z + math.cos(s.heading) * s.speed * dt
	local road = M.road(track, x, z)
	if road.excess > 0 then
		local dx, dz = x - road.x, z - road.z
		x, z = road.x + dx / road.d * road.limit, road.z + dz / road.d * road.limit
		s.speed *= 0.55
	end
	s.x, s.z = x, z
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
				s.speed *= 0.4
				s.slowUntil = s.time + 0.8
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
function M.botInput(s, track)
	local target = track.points[s.botTarget]
	if distance(s.x, s.z, target[1], target[2]) < 13 then
		s.botTarget = s.botTarget % #track.points + 1
		target = track.points[s.botTarget]
	end
	local delta = angle(math.atan2(target[1] - s.x, target[2] - s.z) - s.heading)
	return {
		throttle = math.abs(delta) < 1.2 and 1 or 0.2,
		brake = math.abs(delta) > 0.65 and s.speed > 22 and 1 or 0,
		steer = math.clamp(delta * 2.4, -1, 1),
		boost = false,
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
