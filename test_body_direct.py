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

print("--- Step 2: Clean Launch App ---")
run_adb(["shell", "am", "force-stop", config.PACKAGE_NAME])
time.sleep(1)
run_adb(["shell", "monkey", "-p", config.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"])
print("Waiting 6 seconds for Huawei Health Top Screen...")
time.sleep(6)

print("--- Step 3: Tapping Weight Card (X=200, Y=1650) ---")
run_adb(["shell", "input", "tap", "200", "1650"])
print("Waiting 4 seconds for Weight Summary Screen...")
time.sleep(4)

save_path = config.SCREENSHOTS_DIR / "body_composition" / "weight_top_summary.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(save_path)
print(f"Captured Weight Summary Screen: {save_path.name}")
