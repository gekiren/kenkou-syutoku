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

print("--- Step 1: Screen Wake & Unlock ---")
collector.wake_device()

print("--- Step 2: Tapping Huawei Health Icon on Home Screen (X=870, Y=490) ---")
run_adb(["shell", "input", "tap", "870", "490"])
print("Waiting 5 seconds for App Top Screen...")
time.sleep(5)

save_path = config.SCREENSHOTS_DIR / "app_top_screen.png"
collector.capture_screenshot(save_path)
print(f"Captured App Top Screen: {save_path.name}")
