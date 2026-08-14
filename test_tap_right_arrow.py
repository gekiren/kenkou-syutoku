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

print("--- Step 1: Tapping '身体計測データ >' Right Arrow (X=930, Y=350) ---")
run_adb(["shell", "input", "tap", "930", "350"])
print("Waiting 4 seconds for Target Body Data Detail Screen...")
time.sleep(4)

print("--- Step 2: Capturing Access Screen ---")
path_top = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_top.png"
path_top.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(path_top)
print(f"Captured Screen: {path_top.name}")
