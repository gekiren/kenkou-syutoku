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

print("--- Step 2: Open Sleep Card & Capture Today (8/14) ---")
run_adb(["shell", "input", "tap", "1350", "1150"])
time.sleep(3)
path_sleep = config.SCREENSHOTS_DIR / "sleep" / "sleep_20260814.png"
path_sleep.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(path_sleep)
print(f"Captured Sleep Today: {path_sleep.name}")

print("--- Step 3: Back to App Top Screen ---")
run_adb(["shell", "input", "keyevent", "4"]) # バックボタンでトップへ復帰
time.sleep(2)

print("--- Step 4: Open Weight (Body Composition) Card (X=200, Y=1650) ---")
run_adb(["shell", "input", "tap", "200", "1650"])
time.sleep(3)

print("--- Step 5: Tapping Body Measurement Data (身体計測データ) ---")
# 体重サマリー画面内の「身体計測データ」ボタン・領域をタップ (画面下部中央)
run_adb(["shell", "input", "tap", "800", "1600"])
time.sleep(3)

print("--- Step 6-A: Capture Access Screen (Top Part) ---")
path_body_top = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_top.png"
path_body_top.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(path_body_top)
print(f"Captured Body Comp Top: {path_body_top.name}")

print("--- Step 6-B: Scroll to Bottom & Capture (Bottom Part) ---")
# 下から上へスクロールして最下部を表示
run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "300"])
time.sleep(2)
path_body_bottom = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_bottom.png"
collector.capture_screenshot(path_body_bottom)
print(f"Captured Body Comp Bottom: {path_body_bottom.name}")

print("Finished Step Sequence!")
