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

print("--- Step 1: Scroll Back Up to Restore View ---")
run_adb(["shell", "input", "swipe", "800", "500", "800", "1800", "300"])
time.sleep(2)

print("--- Step 2: Precise Tap on '骨格筋量 29.2kg' Card Center (X=200, Y=410) ---")
run_adb(["shell", "input", "tap", "200", "410"])
print("Waiting 4 seconds for Body Composition Detail Screen...")
time.sleep(4)

save_path = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_top.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(save_path)
print(f"Captured Adjusted Screen: {save_path.name}")
