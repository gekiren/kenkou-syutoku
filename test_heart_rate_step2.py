import subprocess
import time
from pathlib import Path
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
out_dir = config.SCREENSHOTS_DIR / "heart_rate"
out_dir.mkdir(parents=True, exist_ok=True)

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def cap(remote="/sdcard/temp_hr.png", local_path=out_dir / "temp.png"):
    run_adb(["shell", "screencap", "-p", remote])
    run_adb(["pull", remote, str(local_path)])
    print(f"Captured -> {local_path}")

print("=== Heart Rate Step 2: Test Scroll & Prev Day Swipe ===")

# 1. 現在の詳細画面で下方向へスクロールしてみる
print("1. Swiping down to inspect lower content...")
run_adb(["shell", "input", "swipe", "800", "1800", "800", "600", "400"])
time.sleep(2)
cap(local_path=out_dir / "03_detail_bottom.png")

# 2. 元の上部へスクロール
print("2. Swiping back up to top...")
run_adb(["shell", "input", "swipe", "800", "600", "800", "1800", "400"])
time.sleep(2)

# 3. 前日（8/13）へスワイプ (左 -> 右)
print("3. Swiping to previous day (1 day ago)...")
run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
time.sleep(2.5)
cap(local_path=out_dir / "04_prev_day_8-13.png")

# 4. 2日前（8/12）へスワイプ
print("4. Swiping to 2 days ago...")
run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
time.sleep(2.5)
cap(local_path=out_dir / "05_prev_day_8-12.png")

print("Done Step 2.")
