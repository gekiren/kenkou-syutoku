import subprocess
import time
from pathlib import Path
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

out_dir = config.SCREENSHOTS_DIR / "heart_rate"
out_dir.mkdir(parents=True, exist_ok=True)

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def wake_and_unlock():
    print("1. Waking up device & unlocking...")
    run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
    # KEYCODE_WAKEUP (224): 画面が消えている場合のみ点灯（トグルしない）
    run_adb(["shell", "input", "keyevent", "224"])
    time.sleep(1)
    run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
    time.sleep(1)

def cap(remote="/sdcard/temp_hr.png", local_path=out_dir / "temp.png"):
    run_adb(["shell", "screencap", "-p", remote])
    run_adb(["pull", remote, str(local_path)])
    print(f"Captured -> {local_path}")

print("=== Heart Rate Step 1: Launch & Open Detail ===")
wake_and_unlock()

print("2. Force stopping & launching Health app...")
run_adb(["shell", "am", "force-stop", PKG])
time.sleep(1)
run_adb(["shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"])
time.sleep(5)

# トップ画面キャプチャ
top_img = out_dir / "01_top_screen.png"
cap(local_path=top_img)

# 心拍カードタップ (900, 1150)
print("3. Tapping Heart Rate card at (900, 1150)...")
run_adb(["shell", "input", "tap", "900", "1150"])
time.sleep(4)

# 心拍詳細画面キャプチャ
detail_img = out_dir / "02_detail_screen.png"
cap(local_path=detail_img)

print("Done Step 1.")
