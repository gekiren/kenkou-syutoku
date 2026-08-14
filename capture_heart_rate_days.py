import subprocess
import time
import os
import argparse
from datetime import datetime, timedelta
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

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

def capture_heart_rate(days=7):
    print("==========================================")
    print(f"  心拍（Heart Rate） {days}日間 自動データ取得開始 ")
    print("==========================================")

    # 1. 画面起こし & アプリ起動
    wake_and_unlock()
    reset_and_launch_app()

    # 2. 心拍（心機能）カードタップ (X=1015, Y=1248)
    print("[Step 1] 心機能カード (X=1015, Y=1248) をタップ...")
    run_adb(["shell", "input", "tap", "1015", "1248"])
    time.sleep(3.5)

    save_dir = config.SCREENSHOTS_DIR / "heart_rate"
    save_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now()

    for i in range(days):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%Y%m%d")
        date_fmt = target_date.strftime("%Y/%m/%d")
        filename = f"heart_rate_{date_str}.png"
        local_path = save_dir / filename
        remote_path = f"/sdcard/temp_hr_{date_str}.png"

        print(f"\n[{i+1}/{days}] 撮影中: {date_fmt} -> {filename}")
        run_adb(["shell", "screencap", "-p", remote_path])
        run_adb(["pull", remote_path, str(local_path)])
        print(f"  └─ 保存完了: {local_path}")

        if i < days - 1:
            print(f"  └─ 前日へスワイプ (左 -> 右)...")
            run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
            time.sleep(2.5)

    # トップ画面へ復帰
    print("\n[Finish] トップ画面へ復帰 (BACKキー)...")
    run_adb(["shell", "input", "keyevent", "4"])
    time.sleep(1)

    print("==========================================")
    print(f" SUCCESS: 心拍データ {days}日分の撮影が完了しました！")
    print("==========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture Heart Rate Data")
    parser.add_argument("--days", type=int, default=7, help="Number of days to capture (default: 7)")
    args = parser.parse_args()

    capture_heart_rate(days=args.days)
