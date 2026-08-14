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

print("--- Step 1: Screen Wake, Unlock & App Clean Launch ---")
collector.wake_device()
run_adb(["shell", "am", "force-stop", config.PACKAGE_NAME])
time.sleep(1)
run_adb(["shell", "monkey", "-p", config.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"])
print("Waiting 5 seconds for App Top Screen...")
time.sleep(5)

print("--- Step 2: Tapping Weight Card (X=250, Y=1680) ---")
run_adb(["shell", "input", "tap", "250", "1680"])
print("Waiting 4 seconds for Weight Summary Screen...")
time.sleep(4)

save_path = config.SCREENSHOTS_DIR / "body_composition" / "weight_summary_page.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(save_path)
print(f"Captured Weight Summary Page: {save_path.name}")
