"""Batch build, static analysis, live Studio sync, and 3D geometry/gameplay verification for BSC Island v49."""
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STUDIO_DIR = r"C:\Users\User\AppData\Local\Roblox\Versions\version-4f087c32742644ab"
MCP_EXE = os.path.join(STUDIO_DIR, "StudioMCP.exe")
CONTENT_DIR = os.path.join(STUDIO_DIR, "content")


def run_step(label, cmd):
    print(f"\n=== {label} ===", flush=True)
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.stdout.strip():
        print(res.stdout.strip(), flush=True)
    if res.stderr.strip():
        print(res.stderr.strip(), flush=True)
    if res.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {res.returncode}")


class MCPClient:
    def __init__(self):
        self.p = subprocess.Popen(
            [MCP_EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
        )
        self.q = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._err, daemon=True).start()
        self.id = 0
        self.send(
            "initialize",
            {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "v49-verify", "version": "1"}},
        )
        self.send("notifications/initialized", notify=True)

    def _read(self):
        while True:
            ch = self.p.stdout.readline()
            if not ch:
                self.q.put(None)
                return
            try:
                self.q.put(json.loads(ch.decode("utf-8")))
            except Exception:
                pass

    def _err(self):
        for _ in self.p.stderr:
            pass

    def send(self, method, params=None, notify=False, timeout=180):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            self.id += 1
            msg["id"] = self.id
        self.p.stdin.write((json.dumps(msg) + "\n").encode("utf-8"))
        self.p.stdin.flush()
        if notify:
            return None
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                m = self.q.get(timeout=1)
            except queue.Empty:
                continue
            if m is None:
                raise RuntimeError("MCP process exited")
            if m.get("id") == self.id:
                return m
        raise TimeoutError(method)

    def call(self, name, args, timeout=180):
        r = self.send("tools/call", {"name": name, "arguments": args}, timeout=timeout)
        res = r.get("result", r)
        texts = []
        if isinstance(res, dict) and "content" in res:
            for c in res["content"]:
                if c.get("type") == "text":
                    texts.append(c["text"])
        return "\n".join(texts), res

    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass


def sync_and_verify_studio():
    print("\n=== Connecting to Live Roblox Studio via StudioMCP ===", flush=True)
    mcp = MCPClient()
    try:
        txt, _ = mcp.call("list_roblox_studios", {})
        print("Studios:", txt, flush=True)
        studios = json.loads(txt).get("studios", [])
        sid = next((s["id"] for s in studios if s.get("name")), studios[-1]["id"])
        mcp.call("set_active_studio", {"studio_id": sid})

        # Copy Map.rbxmx into Studio content folder so game:GetObjects("rbxasset://Map_v49.rbxmx") loads it in 0.2s
        content_map = os.path.join(CONTENT_DIR, "Map_v49.rbxmx")
        shutil.copyfile(os.path.join(ROOT, "kuwait-parkour", "src", "map", "Map.rbxmx"), content_map)

        # Sync scripts into Studio Edit DataModel
        scripts_to_sync = [
            ("ReplicatedStorage.Shared", "PassportDefs", "ModuleScript", r"kuwait-parkour\src\shared\PassportDefs.luau"),
            ("ReplicatedStorage.Shared", "RacerData", "ModuleScript", r"kuwait-parkour\src\shared\RacerData.luau"),
            ("ReplicatedStorage.Shared", "LaserData", "ModuleScript", r"kuwait-parkour\src\shared\LaserData.luau"),
            ("ServerScriptService.Server", "Main", "Script", r"kuwait-parkour\src\server\Main.server.luau"),
            ("ServerScriptService.Server", "GameShowBank", "ModuleScript", r"kuwait-parkour\src\server\GameShowBank.luau"),
            ("ServerScriptService.Server", "GameShow", "Script", r"kuwait-parkour\src\server\GameShow.server.luau"),
            ("StarterPlayer.StarterPlayerScripts.Client", "WorldMenu", "LocalScript", r"kuwait-parkour\src\client\WorldMenu.client.luau"),
            ("StarterPlayer.StarterPlayerScripts.Client", "PhotoMode", "LocalScript", r"kuwait-parkour\src\client\PhotoMode.client.luau"),
        ]

        for parent_path, name, cls_name, rel_file in scripts_to_sync:
            src = open(os.path.join(ROOT, rel_file), encoding="utf-8").read()
            luau = f"""
local root = game
for seg in string.gmatch("{parent_path}", "[^%.]+") do
    root = root:FindFirstChild(seg) or error("Missing " .. seg)
end
local inst = root:FindFirstChild("{name}")
if not inst then
    inst = Instance.new("{cls_name}")
    inst.Name = "{name}"
    inst.Parent = root
end
inst.Source = [====[{src}]====]
return "Synced " .. inst:GetFullName() .. " (" .. tostring(#inst.Source) .. " bytes)"
"""
            out, _ = mcp.call("execute_luau", {"studio_id": sid, "datamodel_type": "Edit", "code": luau})
            print(out, flush=True)

        # Hot-swap Workspace.Map from rbxasset://Map_v49.rbxmx
        swap_map_luau = """
local ok, objs = pcall(function()
    return game:GetObjects("rbxasset://Map_v49.rbxmx")
end)
if not ok or not objs or #objs == 0 then
    return "GETOBJECTS_ERR: " .. tostring(objs)
end
local newMap = objs[1]
newMap.Name = "Map"
local oldMap = workspace:FindFirstChild("Map")
if oldMap then
    oldMap:Destroy()
end
newMap.Parent = workspace
local count = 0
for _, d in ipairs(newMap:GetDescendants()) do
    if d:IsA("BasePart") then count += 1 end
end
return "Swapped Workspace.Map with " .. tostring(count) .. " BaseParts"
"""
        out, _ = mcp.call("execute_luau", {"studio_id": sid, "datamodel_type": "Edit", "code": swap_map_luau})
        print(out, flush=True)

        # 3D Walkability & Doorway Clearance Audit in Studio
        audit_luau = """
local map = workspace:WaitForChild("Map")
local params = OverlapParams.new()
params.FilterType = Enum.RaycastFilterType.Include
params.FilterDescendantsInstances = { map }

local function checkPath(label, x0, y, z0, x1, z1, steps)
    local blockers = {}
    local seen = {}
    for i = 0, steps do
        local t = i / steps
        local x = x0 + (x1 - x0) * t
        local z = z0 + (z1 - z0) * t
        local parts = workspace:GetPartBoundsInBox(CFrame.new(x, y + 0.6, z), Vector3.new(2.6, 4.2, 1.6), params)
        for _, p in ipairs(parts) do
            if p.CanCollide and not seen[p] then
                seen[p] = true
                table.insert(blockers, string.format("%s (%s at %.1f,%.1f,%.1f size %.1f,%.1f,%.1f)",
                    p.Name, p.Parent and p.Parent.Name or "?", p.Position.X, p.Position.Y, p.Position.Z,
                    p.Size.X, p.Size.Y, p.Size.Z))
            end
        end
    end
    return { label = label, ok = #blockers == 0, blockers = blockers }
end

local results = {
    checkPath("Red Corridor (South L1 z=-32 -> North L1 z=134)", -40, 26.5, -32, -40, 134, 80),
    checkPath("South Front West Side Door (x=-17, z=-166..-154)", -17, 3.0, -166, -17, -154, 12),
    checkPath("South Front East Side Door (x=17, z=-166..-154)", 17, 3.0, -166, 17, -154, 12),
    checkPath("South Rear West Door & Cafeteria Corridor (x=-42, z=-84..-24)", -42, 3.0, -84, -42, -24, 30),
    checkPath("South Rear East Door & Corridor (x=42, z=-84..-24)", 42, 3.0, -84, 42, -24, 30),
    checkPath("South West Wing Ground Doorway (x=-86..-96, z=-153)", -86, 3.0, -153, -96, -153, 10),
    checkPath("South East Wing Ground Doorway (x=86..96, z=-153)", 86, 3.0, -153, 96, -153, 10),
    checkPath("South West Wing L1 Doorway (x=-86..-96, z=-167)", -86, 26.5, -167, -96, -167, 10),
    checkPath("South East Wing L1 Doorway (x=86..96, z=-167)", 86, 26.5, -167, 96, -167, 10),
    checkPath("North West Revolving Door Side Pass (x=-5, z=114..136)", -5, 3.0, 114, -5, 136, 15),
    checkPath("North East Revolving Door Side Pass (x=25, z=114..136)", 25, 3.0, 114, 25, 136, 15),
}

local spawns = {}
for _, name in ipairs({"MuseumSpawn", "RaceLobbySpawn", "LaserSpawn", "GameShowSpawn", "ArcadeSpawn", "LabSpawn", "QuizSpawn", "ExamSpawn", "PuzzleSpawn", "TrainSpawnPoint", "IslandSpawn"}) do
    spawns[name] = map:FindFirstChild(name, true) ~= nil
end

return game:GetService("HttpService"):JSONEncode({ audits = results, spawns = spawns })
"""
        audit_out, _ = mcp.call("execute_luau", {"studio_id": sid, "datamodel_type": "Edit", "code": audit_luau})
        print("\n=== 3D Walkability & Doorway Audit ===", flush=True)
        print(audit_out, flush=True)

        # Now run Play Solo test to verify runtime scripts, WorldMenu (15 cards), PhotoModeGui, GameShow, and Travel!
        print("\n=== Starting Studio Play Solo Verification ===", flush=True)
        mcp.call("start_stop_play", {"studio_id": sid, "mode": "start_play"})
        time.sleep(5)

        play_verify_luau = """
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local p = Players.LocalPlayer
local pgui = p:WaitForChild("PlayerGui", 10)
local wm = pgui:WaitForChild("WorldMenu", 10)
local pm = pgui:WaitForChild("PhotoModeGui", 10)
local prof = pgui:WaitForChild("ProfileMenu", 10)

local cards = {}
for _, c in ipairs(wm.Panel:FindFirstChildOfClass("Frame"):GetChildren()) do
    if c:IsA("TextButton") then
        table.insert(cards, c.Name)
    end
end

-- Test PhotoMode toggle on and off
local toggleBtn = pm:FindFirstChild("PhotoModeToggle")
local dock = pm:FindFirstChild("ControlDock")
local overlay = pm:FindFirstChild("Overlay")

-- Test Travel remote to Museum, Racers, Laser, Show, and back to Campus
local travel = RS:WaitForChild("Travel", 5)
local visited = {}
for _, dest in ipairs({"Museum", "Racers", "Laser", "Show", "Campus"}) do
    travel:FireServer(dest)
    task.wait(2.2)
    local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
    visited[dest] = root and { math.floor(root.Position.X), math.floor(root.Position.Y), math.floor(root.Position.Z) } or nil
end

-- Test walking into North Building through the Red Corridor junction (z = 124 -> 136 at x = -40, y = 27.5)
local char = p.Character
local hum = char and char:FindFirstChildOfClass("Humanoid")
local root = char and char:FindFirstChild("HumanoidRootPart")
local redBridgeWalkOk = false
if hum and root then
    char:PivotTo(CFrame.new(-40, 27.5, 120))
    task.wait(0.2)
    hum:MoveTo(Vector3.new(-40, 27.5, 136))
    local t0 = os.clock()
    while os.clock() - t0 < 3.0 do
        if (Vector2.new(root.Position.X, root.Position.Z) - Vector2.new(-40, 136)).Magnitude < 3.0 then
            redBridgeWalkOk = true
            break
        end
        task.wait(0.1)
    end
end

return game:GetService("HttpService"):JSONEncode({
    worldMenuCards = #cards,
    cardNames = cards,
    photoModeLoaded = toggleBtn ~= nil and dock ~= nil and overlay ~= nil,
    profileLoaded = prof ~= nil,
    travelPositions = visited,
    redBridgeWalkOk = redBridgeWalkOk,
    finalRedBridgePos = root and { math.floor(root.Position.X), math.floor(root.Position.Y), math.floor(root.Position.Z) } or nil,
})
"""
        play_out, _ = mcp.call("execute_luau", {"studio_id": sid, "datamodel_type": "Client", "code": play_verify_luau})
        print("Play Solo Verification:", play_out, flush=True)

        logs_out, _ = mcp.call("get_console_output", {"studio_id": sid})
        print("Studio Console Logs:\n", logs_out[:2500], flush=True)

        mcp.call("start_stop_play", {"studio_id": sid, "mode": "stop"})
        time.sleep(2)
    finally:
        mcp.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    run_step("StyLua Check", [r"tools\stylua\stylua.exe", "--check", r"kuwait-parkour\src"])
    print("\n=== Selene Linter ===", flush=True)
    sel = subprocess.run(
        [r"tools\selene\selene.exe", "--config", r"kuwait-parkour\selene.toml", r"kuwait-parkour\src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(sel.stdout[-400:].strip(), flush=True)
    if "0 errors" not in sel.stdout or "0 parse errors" not in sel.stdout:
        raise RuntimeError("Selene found errors!")
    run_step("Lune Question & GameShowBank Validator", [r"tools\lune\lune.exe", "run", r"tools\validate_questions.luau"])
    out_rbxlx = os.path.join(ROOT, "KuwaitParkour_v49.rbxlx")
    run_step(
        "Rojo Build KuwaitParkour_v49.rbxlx",
        [r"tools\rojo\rojo.exe", "build", r"kuwait-parkour\default.project.json", "-o", out_rbxlx],
    )
    shutil.copyfile(out_rbxlx, os.path.join(os.path.dirname(ROOT), "KuwaitParkour_v49.rbxlx"))
    print(f"Built {out_rbxlx} ({os.path.getsize(out_rbxlx) / (1024 * 1024):.2f} MB)", flush=True)
    sync_and_verify_studio()
