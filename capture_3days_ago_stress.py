import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
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

def capture_3days_ago_stress():
    print("=== 3日前 (2026/08/11 火) のストレスデータ自動取得テスト ===")
    wake_and_unlock()
    reset_and_launch_app()

    # 1. トップ画面から「情緒」カードタップ (実測 606, 1780)
    print("1. 情緒カードタップ (X=606, Y=1780)...")
    run_adb(["shell", "input", "tap", "606", "1780"])
    time.sleep(3.5)

    # 2. 日付ドロップダウンタップ (実測 318, 374)
    print("2. 日付ドロップダウンタップ (X=318, Y=374)...")
    run_adb(["shell", "input", "tap", "318", "374"])
    time.sleep(2)

    # 3. カレンダー上の 8/11 (火) タップ (X=625, Y=1863)
    print("3. カレンダーの「11」日タップ (X=625, Y=1863)...")
    run_adb(["shell", "input", "tap", "625", "1863"])
    time.sleep(3)

    # 4. スクリーンショット撮影
    local_path = out_dir / "stress_3days_ago_20260811.png"
    remote_path = "/sdcard/temp_stress_3days.png"
    print("4. スクリーンショット撮影中...")
    run_adb(["shell", "screencap", "-p", remote_path])
    run_adb(["pull", remote_path, str(local_path)])
    print(f"保存完了: {local_path}")

    # 5. トップ画面へ戻る
    run_adb(["shell", "input", "keyevent", "4"])
    print("完了。")

if __name__ == "__main__":
    capture_3days_ago_stress()
