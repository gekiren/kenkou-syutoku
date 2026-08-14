import subprocess
import time
from datetime import datetime, timedelta
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def capture_3days_ago():
    date_3days_ago = datetime.now() - timedelta(days=3)
    date_str = date_3days_ago.strftime("%Y%m%d")
    date_fmt = date_3days_ago.strftime("%Y/%m/%d")

    print(f"=== 3日前 ({date_fmt}) の心機能グラフ取得 ===")
    
    # 1. 画面起こし & ロック解除
    print("1. 画面点灯 & ロック解除...")
    run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
    run_adb(["shell", "input", "keyevent", "224"])
    time.sleep(1)
    run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
    time.sleep(1)

    # 2. アプリ起動
    print("2. ヘルスケアアプリ起動...")
    run_adb(["shell", "am", "force-stop", PKG])
    time.sleep(1)
    run_adb(["shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(5)

    # 3. 心機能カードタップ
    print("3. 心機能カード (X=1015, Y=1248) をタップ...")
    run_adb(["shell", "input", "tap", "1015", "1248"])
    time.sleep(3.5)

    # 4. 3回スワイプして3日前へ移動
    for k in range(3):
        print(f"4-{k+1}. 前日へスワイプ...")
        run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
        time.sleep(2.5)

    # 5. スクリーンショット撮影
    save_dir = config.SCREENSHOTS_DIR / "heart_rate"
    save_dir.mkdir(parents=True, exist_ok=True)
    local_path = save_dir / f"heart_rate_3days_ago_{date_str}.png"
    remote_path = "/sdcard/temp_hr_3days.png"

    print(f"5. 3日前 ({date_fmt}) のスクショ撮影...")
    run_adb(["shell", "screencap", "-p", remote_path])
    run_adb(["pull", remote_path, str(local_path)])
    print(f"保存完了: {local_path}")

    # 6. トップ画面に戻る
    run_adb(["shell", "input", "keyevent", "4"])
    print("完了。")

if __name__ == "__main__":
    capture_3days_ago()
