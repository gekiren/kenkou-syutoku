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

print("--- Step 1: Screen Wake, Unlock & App Launch ---")
collector.wake_device()
run_adb(["shell", "monkey", "-p", config.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"])
time.sleep(4)

print("--- Step 2: Tapping Red-Box Weight Card (X=250, Y=1600) ---")
run_adb(["shell", "input", "tap", "250", "1600"])
print("Waiting 4 seconds for Weight Top Screen...")
time.sleep(4)

save_path = config.SCREENSHOTS_DIR / "body_composition" / "weight_summary_opened.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(save_path)
print(f"Captured Weight Summary Opened Screen: {save_path.name}")
