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
run_adb(["shell", "am", "force-stop", config.PACKAGE_NAME])
time.sleep(1)
run_adb(["shell", "monkey", "-p", config.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"])
print("Waiting 5 seconds for top screen...")
time.sleep(5)

print("--- Step 2: Open Sleep Detail Screen (X=1350, Y=1150) ---")
run_adb(["shell", "input", "tap", "1350", "1150"])
print("Waiting 3 seconds for Sleep detail screen...")
time.sleep(3)

# 1日目 (本日 8/14) 撮影
path_814 = config.SCREENSHOTS_DIR / "sleep" / "sleep_20260814.png"
path_814.parent.mkdir(parents=True, exist_ok=True)
print(f"--- Step 3: Capturing Today (8/14) -> {path_814.name} ---")
collector.capture_screenshot(path_814)
time.sleep(1)

# 赤枠領域 (Y=850) でスワイプして前日 (8/13) へ移動
print("--- Step 4: Swiping Red-Box Area (Y=850) to Previous Day (8/13) ---")
run_adb(["shell", "input", "swipe", "300", "850", "1300", "850", "300"])
time.sleep(2)

# 2日目 (前日 8/13) 撮影
path_813 = config.SCREENSHOTS_DIR / "sleep" / "sleep_20260813.png"
print(f"--- Step 5: Capturing Previous Day (8/13) -> {path_813.name} ---")
collector.capture_screenshot(path_813)
print("Finished Sleep 2-Day Screenshot Process!")
