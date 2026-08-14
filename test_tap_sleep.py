import subprocess
import time
from pathlib import Path
import config

adb_path = config.ADB_PATH
device_id = config.DEVICE_ID

def run_adb(args):
    cmd = [adb_path, "-s", device_id] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

from src.adb_collector import ADBCollector

collector = ADBCollector()

print("--- Step 1: Screen Wake & Unlock ---")
collector.wake_device()

print("--- Step 2: Task Kill & Clean Launch ---")
run_adb(["shell", "am", "force-stop", "com.huawei.health"]) # タスクキル
time.sleep(1)
run_adb(["shell", "monkey", "-p", "com.huawei.health", "-c", "android.intent.category.LAUNCHER", "1"])
print("Waiting 5 seconds for top screen to load...")
time.sleep(5)

print("--- Step 3: Tapping Sleep Card (X=1350, Y=1150) ---")
run_adb(["shell", "input", "tap", "1350", "1150"])
print("Waiting 3 seconds for detail screen to open...")
time.sleep(3)

print("--- Step 4: Capturing Detail Screenshot ---")
save_path = config.SCREENSHOTS_DIR / "test_sleep_detail.png"
collector.capture_screenshot(save_path)
print(f"Captured test screenshot: {save_path}")
