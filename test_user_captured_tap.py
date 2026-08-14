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

print("--- Step 1: Tapping Recorded User Tap Location (X=867, Y=886) ---")
run_adb(["shell", "input", "tap", "867", "886"])
print("Waiting 4 seconds for Body Composition Detail Screen...")
time.sleep(4)

print("--- Step 2: Capturing Top Part (アクセス直後の上部画面) ---")
path_top = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_top.png"
path_top.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(path_top)
print(f"Captured Top Part: {path_top.name}")

print("--- Step 3: Scrolling to Bottom ---")
run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "300"])
time.sleep(2)

print("--- Step 4: Capturing Bottom Part (最下部スクロール後の下部画面) ---")
path_bottom = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_bottom.png"
collector.capture_screenshot(path_bottom)
print(f"Captured Bottom Part: {path_bottom.name}")

print("Successfully Completed Capture with Recorded User Coordinates!")
