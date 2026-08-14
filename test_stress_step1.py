import subprocess
import time
from pathlib import Path
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

out_dir = config.SCREENSHOTS_DIR / "stress"
out_dir.mkdir(parents=True, exist_ok=True)

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def wake_and_unlock():
    print("[Power] Waking up screen and unlocking...")
    run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
    run_adb(["shell", "input", "keyevent", "224"])
    time.sleep(1)
    run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
    time.sleep(1)

def reset_and_launch_app():
    print("[App] Launching Health app...")
    run_adb(["shell", "am", "force-stop", PKG])
    time.sleep(1)
    run_adb(["shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(5)

def cap(remote="/sdcard/temp_stress.png", local_path=out_dir / "temp.png"):
    run_adb(["shell", "screencap", "-p", remote])
    run_adb(["pull", remote, str(local_path)])
    print(f"Captured -> {local_path}")

print("=== Stress Step 1: Open Detail & Capture Past Days ===")
wake_and_unlock()
reset_and_launch_app()

# 実測座標 (X=606, Y=1780)
print("1. Tapping Stress card at (X=606, Y=1780)...")
run_adb(["shell", "input", "tap", "606", "1780"])
time.sleep(4)

# 当日 (8/14)
print("2. Capturing Today (8/14)...")
cap(local_path=out_dir / "01_stress_today_8-14.png")

# 前日 (8/13) へスワイプ
print("3. Swiping to Previous Day (8/13)...")
run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
time.sleep(2.5)
cap(local_path=out_dir / "02_stress_8-13.png")

# 2日前 (8/12) へスワイプ
print("4. Swiping to 2 Days Ago (8/12)...")
run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
time.sleep(2.5)
cap(local_path=out_dir / "03_stress_8-12.png")

# 3日前 (8/11) へスワイプ
print("5. Swiping to 3 Days Ago (8/11)...")
run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
time.sleep(2.5)
cap(local_path=out_dir / "04_stress_8-11.png")

# トップ画面へ戻る
run_adb(["shell", "input", "keyevent", "4"])
print("Done Step 1.")
