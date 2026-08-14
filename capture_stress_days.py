import subprocess
import time
import os
import argparse
from datetime import datetime, timedelta, date
from pathlib import Path
import config
from src.calendar_picker import HealthCalendarPicker

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

def capture_stress_days(days=7):
    print("==========================================")
    print(f"  ストレス（情緒） {days}日間 自動データ取得開始 ")
    print("  方式: カレンダー動的座標自動計算モデル")
    print("==========================================")

    # 1. 画面点灯 & アプリ起動
    wake_and_unlock()
    reset_and_launch_app()

    # 2. 情緒カードタップ (X=606, Y=1780)
    print("[Step 1] 情緒カード (X=606, Y=1780) をタップ...")
    run_adb(["shell", "input", "tap", "606", "1780"])
    time.sleep(4)

    save_dir = config.SCREENSHOTS_DIR / "stress"
    save_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()

    for i in range(days):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%Y%m%d")
        date_fmt = target_date.strftime("%Y/%m/%d")

        # カレンダー上の座標を動的計算
        cx, cy = HealthCalendarPicker.get_date_coords(target_date)

        print(f"\n[{i+1}/{days}] 取得対象: {date_fmt} (カレンダー座標: X={cx}, Y={cy})")

        # 日付ドロップダウンタップ
        run_adb(["shell", "input", "tap", "318", "374"])
        time.sleep(1.8)

        # カレンダー上の該当セルをタップ
        run_adb(["shell", "input", "tap", str(cx), str(cy)])
        time.sleep(2.5)

        # スクリーンショット撮影
        filename = f"stress_{date_str}.png"
        local_path = save_dir / filename
        remote_path = f"/sdcard/temp_stress_{date_str}.png"

        run_adb(["shell", "screencap", "-p", remote_path])
        run_adb(["pull", remote_path, str(local_path)])
        print(f"  └─ 保存完了: {local_path}")

    # トップ画面へ戻る
    print("\n[Finish] トップ画面へ復帰 (BACKキー)...")
    run_adb(["shell", "input", "keyevent", "4"])
    time.sleep(1)

    print("==========================================")
    print(f" SUCCESS: ストレスデータ {days}日分の撮影が完了しました！")
    print("==========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture Stress Data via Dynamic Calendar Picker")
    parser.add_argument("--days", type=int, default=7, help="Number of days to capture (default: 7)")
    args = parser.parse_args()

    capture_stress_days(days=args.days)
