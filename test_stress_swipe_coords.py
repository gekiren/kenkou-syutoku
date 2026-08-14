import subprocess
import time
from pathlib import Path
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

out_dir = config.SCREENSHOTS_DIR / "stress"

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def reset_to_stress():
    run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
    run_adb(["shell", "input", "keyevent", "224"])
    time.sleep(1)
    run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
    time.sleep(1)
    run_adb(["shell", "am", "force-stop", PKG])
    time.sleep(1)
    run_adb(["shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(5)
    # 実測 (606, 1780) で情緒カードタップ
    run_adb(["shell", "input", "tap", "606", "1780"])
    time.sleep(4)

print("=== Testing Stress Swipe Area ===")
reset_to_stress()

# テスト1: 下部領域 (Y=2000) でのスワイプ
print("Test 1: Swipe at Y=2000 (300 -> 1300)...")
run_adb(["shell", "input", "swipe", "300", "2000", "1300", "2000", "300"])
time.sleep(2.5)
run_adb(["shell", "screencap", "-p", "/sdcard/temp_swipe1.png"])
run_adb(["pull", "/sdcard/temp_swipe1.png", str(out_dir / "swipe_test_y2000.png")])

# テスト2: グラフ上部・日付付近 (Y=380) のタップやスワイプ
print("Test 2: Swipe at Y=600 (300 -> 1300)...")
run_adb(["shell", "input", "swipe", "300", "600", "1300", "600", "300"])
time.sleep(2.5)
run_adb(["shell", "screencap", "-p", "/sdcard/temp_swipe2.png"])
run_adb(["pull", "/sdcard/temp_swipe2.png", str(out_dir / "swipe_test_y600.png")])

print("Done.")
