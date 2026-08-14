import subprocess
import time
from pathlib import Path
import config
from src.adb_collector import ADBCollector

collector = ADBCollector()

def run_adb(args):
    cmd = [config.ADB_PATH, "-s", config.DEVICE_ID] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

print("--- Step 1: Close Calendar Modal (Tapping 'X' button or overlay) ---")
run_adb(["shell", "input", "tap", "1220", "950"])
time.sleep(1)

print("--- Step 2: Tap User-Specified Red-Box '身体計測データ >' (X=300, Y=720) ---")
run_adb(["shell", "input", "tap", "300", "720"])
print("Waiting 4 seconds for Full Detail Screen...")
time.sleep(4)

print("--- Step 3: Capture Access Screen (Top Part) ---")
path_top = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_top.png"
path_top.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(path_top)
print(f"Captured Top Part: {path_top.name}")

print("--- Step 4: Scroll to Bottom ---")
run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "300"])
time.sleep(2)

print("--- Step 5: Capture Scroll Screen (Bottom Part) ---")
path_bottom = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_bottom.png"
collector.capture_screenshot(path_bottom)
print(f"Captured Bottom Part: {path_bottom.name}")

print("Successfully Completed Red-Box Body Composition Flow!")
