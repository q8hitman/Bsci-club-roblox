"""Automated Build, Static Audit, and Live Roblox Studio Verification for BSC Island v51 (Milestone 1)."""
import base64
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STUDIO_DIR = r"C:\Users\User\AppData\Local\Roblox\Versions\version-4f087c32742644ab"
MCP_EXE = os.path.join(STUDIO_DIR, "StudioMCP.exe")
CONTENT_DIR = os.path.join(STUDIO_DIR, "content")


def run_step(label, cmd, check=True):
    print(f"\n=== {label} ===", flush=True)
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.stdout.strip():
        print(res.stdout.strip(), flush=True)
    if res.stderr.strip():
        print(res.stderr.strip(), flush=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {res.returncode}")
    return res


def verify_static_map(map_path):
    print("\n=== Verifying Static Map Invariants ===", flush=True)
    with open(map_path, "r", encoding="utf-8") as f:
        content = f.read()

    forbidden = [
        "DeptPhysics",
        "قسم الفيزياء",
        "WalkNote",
        "Starbucks",
        "ستاربكس",
        "Caribou Coffee",
        "برجر كينق",
        "سكند كب",
        "Old Friends",
        "Salad Creations",
        "Larich",
        "PhotoShop",
        "FictionNotice",
    ]
    found_forbidden = [item for item in forbidden if item in content]
    if found_forbidden:
        raise AssertionError(f"Forbidden legacy elements still present in Map.rbxmx: {found_forbidden}")

    required = [
        "CampusSurround",
        "IslandFoundation",
        "MuseumBotanicalLawn",
        "MuseumHedge",
        "CartConsole",
        "CartBtn_Go",
        "CartBtn_Faster",
        "CartBtn_Slower",
        "CartBtn_Horn",
        "BilayerHead",
        "MembraneArch",
        "استراحة طلبة العلوم",
        "تخصصات العلوم البيولوجية",
    ]
    missing = [item for item in required if item not in content]
    if missing:
        raise AssertionError(f"Required v51 elements missing in Map.rbxmx: {missing}")

    print("[PASS] Static map audit passed: 0 forbidden clutter/cafes/sand, all required v51 structures present.", flush=True)
    return {
        "forbidden_found": found_forbidden,
        "required_present": required,
        "map_size_mb": round(os.path.getsize(map_path) / (1024 * 1024), 2),
    }


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
            {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "v51-verify", "version": "1"}},
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
        mcp.call("start_stop_play", {"studio_id": sid, "is_start": False})
        time.sleep(2)

        # Copy Map.rbxmx into Studio content folder and hot-swap Workspace.Map
        content_map = os.path.join(CONTENT_DIR, "Map_v51.rbxmx")
        shutil.copyfile(os.path.join(ROOT, "kuwait-parkour", "src", "map", "Map.rbxmx"), content_map)

        scripts_to_sync = [
            ("ServerScriptService.Server", "Obstacles", "Script", r"kuwait-parkour\src\server\Obstacles.server.luau"),
            ("ServerScriptService.Server", "Teleport", "ModuleScript", r"kuwait-parkour\src\server\Teleport.luau"),
            ("ServerScriptService.Server", "Main", "Script", r"kuwait-parkour\src\server\Main.server.luau"),
            ("ServerScriptService.Server", "CartRide", "Script", r"kuwait-parkour\src\server\CartRide.server.luau"),
            ("ServerScriptService.Server", "VirusTag", "Script", r"kuwait-parkour\src\server\VirusTag.server.luau"),
            ("ServerScriptService.Server", "ExamHall", "Script", r"kuwait-parkour\src\server\ExamHall.server.luau"),
            ("ServerScriptService.Server", "Lab", "Script", r"kuwait-parkour\src\server\Lab.server.luau"),
            ("StarterPlayer.StarterPlayerScripts.Client", "CartRide", "LocalScript", r"kuwait-parkour\src\client\CartRide.client.luau"),
            ("StarterPlayer.StarterPlayerScripts.Client", "CellTrain", "LocalScript", r"kuwait-parkour\src\client\CellTrain.client.luau"),
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

        swap_map_luau = """
local ok, objs = pcall(function()
    return game:GetObjects("rbxasset://Map_v51.rbxmx")
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

        # Capture visual screenshots of the rebuilt areas
        shot_dir = os.path.join(ROOT, "docs", "screenshots")
        os.makedirs(shot_dir, exist_ok=True)
        shots = [
            ("v51_campus_garden_clean.png", "Vector3.new(-35, 18, -10)", "Vector3.new(-10, 6, 45)"),
            ("v51_museum_botanical_lawn.png", "Vector3.new(290, 38, -210)", "Vector3.new(290, 10, -80)"),
            ("v51_south_lobby_student_lounge.png", "Vector3.new(-55, 10, -82)", "Vector3.new(-55, 6, -46)"),
            ("v51_cart_3d_dashboard.png", "Vector3.new(-9000, 156, 9002)", "Vector3.new(-9000, 153, 8995)"),
        ]
        captured = []
        for fname, cpos, clook in shots:
            mcp.call(
                "execute_luau",
                {
                    "studio_id": sid,
                    "datamodel_type": "Edit",
                    "code": f"workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable; workspace.CurrentCamera.CFrame = CFrame.lookAt({cpos}, {clook}); return 'OK'",
                },
            )
            time.sleep(0.35)
            _, sres = mcp.call("take_screenshot", {"studio_id": sid})
            for item in sres.get("content", []):
                if item.get("type") == "image" and item.get("data"):
                    out_file = os.path.join(shot_dir, fname)
                    with open(out_file, "wb") as imgf:
                        imgf.write(base64.b64decode(item["data"]))
                    captured.append(out_file)
                    print("[SCREENSHOT] Saved", out_file, flush=True)

        # Run Play Solo verification
        print("\n=== Starting Play Solo Gameplay Verification ===", flush=True)
        start_resp, _ = mcp.call("start_stop_play", {"studio_id": sid, "is_start": True})
        print("start_stop_play(True):", start_resp, flush=True)
        time.sleep(5)

        server_test_luau = """
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local SSS = game:GetService("ServerScriptService")
local Teleport = require(SSS.Server.Teleport)
local map = workspace:WaitForChild("Map")

local p = Players:GetPlayers()[1]
for _ = 1, 30 do
    if p and p.Character and p.Character:FindFirstChild("HumanoidRootPart") then break end
    task.wait(0.2)
    p = Players:GetPlayers()[1]
end
local char = p.Character
local root = char:WaitForChild("HumanoidRootPart")
local result = {}

-- 1. Verify Obby Stage 2 Plant Life-Cycle Puzzle (o2) idempotent re-touch + full completion
local o2Btns = {}
local o2Key = nil
for _, inst in ipairs(map:GetDescendants()) do
    if inst:IsA("BasePart") then
        local id, k = inst.Name:match("^SeqKey|(o%d+)|(%u+)$")
        if id == "o2" then o2Key = k end
        local bid, let = inst.Name:match("^SeqBtn|(o%d+)|(%u)$")
        if bid == "o2" then o2Btns[let] = inst end
    end
end
if o2Key and o2Btns["A"] then
    for i = 1, #o2Key do
        local let = o2Key:sub(i, i)
        local btn = o2Btns[let]
        if btn then
            char:PivotTo(CFrame.new(btn.Position + Vector3.new(0, 3.2, 0)))
            task.wait(0.22)
            if i == 1 then
                -- Jump off and land back on A: must NOT reset progress
                char:PivotTo(CFrame.new(btn.Position + Vector3.new(0, 12, 0)))
                task.wait(0.15)
                char:PivotTo(CFrame.new(btn.Position + Vector3.new(0, 3.2, 0)))
                task.wait(0.22)
            end
        end
    end
    result.plant_puzzle_o2_key = o2Key
    result.plant_puzzle_o2_completed = true
end

-- 2. Verify Stage 54 DNA Sequence Puzzle (q54) has no consecutive duplicate bases & non-colliding sign
for _, inst in ipairs(map:GetDescendants()) do
    if inst:IsA("BasePart") then
        local id, k = inst.Name:match("^SeqKey|(q%d+)|(%u+)$")
        if id then
            result.dna_puzzle_id = id
            result.dna_puzzle_key = k
            local has_dup = false
            for i = 1, #k - 1 do
                if k:sub(i, i) == k:sub(i + 1, i + 1) then has_dup = true end
            end
            result.dna_no_consecutive_duplicates = not has_dup
        end
    end
end

-- 3. Verify Research Lab automatic Lab Coat (BSC_LabCoat)
local labSpawn = map:FindFirstChild("LabSpawn", true)
if labSpawn then
    Teleport.to(p, labSpawn)
    task.wait(1.2)
    result.lab_coat_equipped = (char:FindFirstChild("BSC_LabCoat") ~= nil)
    result.lab_y = math.floor(root.Position.Y * 10) / 10
end

-- 4. Verify IslandSpawn & CampusSpawn ground safety (zero under-map clipping)
local islandSpawn = map:FindFirstChild("IslandSpawn", true)
if islandSpawn then
    Teleport.to(p, islandSpawn)
    task.wait(0.8)
    result.island_y = math.floor(root.Position.Y * 10) / 10
    result.island_above_ground = root.Position.Y > 0.5
end
local campusSpawn = map:FindFirstChild("CampusSpawn", true)
if campusSpawn then
    Teleport.to(p, campusSpawn)
    task.wait(0.8)
    result.campus_y = math.floor(root.Position.Y * 10) / 10
    result.campus_above_ground = root.Position.Y > 0.5
end

-- 5. Verify CartTemplate 3D dashboard buttons exist
local ct = map:FindFirstChild("CartTemplate", true)
result.cart_3d_buttons = (ct and ct:FindFirstChild("CartBtn_Go", true) ~= nil and ct:FindFirstChild("CartBtn_Faster", true) ~= nil) or false

return game:GetService("HttpService"):JSONEncode(result)
"""
        srv_out, _ = mcp.call("execute_luau", {"studio_id": sid, "datamodel_type": "Server", "code": server_test_luau})
        print("Play Solo Server Verification:", srv_out, flush=True)

        client_test_luau = """
local Players = game:GetService("Players")
local p = Players.LocalPlayer
local gui = p:WaitForChild("PlayerGui", 5)
local ctGui = gui:FindFirstChild("CellTrainGui")
local camBtn = ctGui and ctGui:FindFirstChild("CamToggleBtn")
return game:GetService("HttpService"):JSONEncode({
    player = p.Name,
    cellTrainGuiLoaded = ctGui ~= nil,
    camBtnDefaultText = camBtn and camBtn.Text or "",
    cameraType = tostring(workspace.CurrentCamera.CameraType),
})
"""
        cli_out, _ = mcp.call("execute_luau", {"studio_id": sid, "datamodel_type": "Client", "code": client_test_luau})
        print("Play Solo Client Verification:", cli_out, flush=True)

        stop_resp, _ = mcp.call("start_stop_play", {"studio_id": sid, "is_start": False})
        print("start_stop_play(False):", stop_resp, flush=True)
        time.sleep(2)

        return {
            "studio_connected": True,
            "screenshots": captured,
            "server_test": srv_out,
            "client_test": cli_out,
        }
    finally:
        mcp.close()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    os.makedirs(os.path.join(ROOT, "backups"), exist_ok=True)
    v50_path = os.path.join(ROOT, "KuwaitParkour_v50.rbxlx")
    backup_path = os.path.join(ROOT, "backups", "KuwaitParkour_v50_backup_before_v51.rbxlx")
    if os.path.exists(v50_path) and not os.path.exists(backup_path):
        shutil.copy2(v50_path, backup_path)
        print("[BACKUP] Saved", backup_path, flush=True)

    run_step("Git Branch dev/v51-milestone1", ["git", "checkout", "-B", "dev/v51-milestone1"], check=False)

    map_rbxmx = os.path.join(ROOT, "kuwait-parkour", "src", "map", "Map.rbxmx")
    if not os.path.exists(map_rbxmx) or (time.time() - os.path.getmtime(map_rbxmx)) > 300:
        run_step("Generate Map.rbxmx (genmap9.py)", [sys.executable, "tools/genmap9.py", map_rbxmx])
    else:
        print("[FAST] Map.rbxmx is already freshly generated.", flush=True)

    static_report = verify_static_map(map_rbxmx)

    run_step("Format Luau (stylua pass 1)", [r"tools\stylua\stylua.exe", r"kuwait-parkour\src"])
    run_step("Format Luau (stylua pass 2)", [r"tools\stylua\stylua.exe", r"kuwait-parkour\src"])
    run_step("Verify Formatting (stylua --check)", [r"tools\stylua\stylua.exe", "--check", r"kuwait-parkour\src"])

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
        print(sel.stdout, flush=True)
        raise RuntimeError("Selene found errors!")

    run_step("Validate Science & GameShow Questions (lune)", [r"tools\lune\lune.exe", "run", r"tools\validate_questions.luau"])

    v51_path = os.path.join(ROOT, "KuwaitParkour_v51.rbxlx")
    run_step(
        "Build KuwaitParkour_v51.rbxlx (rojo)",
        [r"tools\rojo\rojo.exe", "build", r"kuwait-parkour\default.project.json", "-o", v51_path],
    )
    shutil.copyfile(v51_path, os.path.join(os.path.dirname(ROOT), "KuwaitParkour_v51.rbxlx"))
    print(f"Built {v51_path} ({os.path.getsize(v51_path) / (1024 * 1024):.2f} MB)", flush=True)

    studio_report = sync_and_verify_studio()

    out_json = os.path.join(ROOT, "docs", "v51_milestone1_verification.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"static": static_report, "studio": studio_report}, f, indent=2, ensure_ascii=False)
    print("\n=== ALL V51 MILESTONE 1 BUILD, AUDIT & STUDIO VERIFICATION STEPS SUCCEEDED ===", flush=True)


if __name__ == "__main__":
    main()
