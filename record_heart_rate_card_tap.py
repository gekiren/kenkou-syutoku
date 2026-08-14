import subprocess
import time
import sys
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def prepare_top_screen():
    print("[1/2] 画面を点灯し、ヘルスケアアプリのトップ画面を表示します...")
    run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
    run_adb(["shell", "input", "keyevent", "224"])
    time.sleep(1)
    run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
    time.sleep(1)
    run_adb(["shell", "am", "force-stop", PKG])
    time.sleep(1)
    run_adb(["shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(5)

def record_tap(timeout=30):
    prepare_top_screen()

    print("\n==========================================")
    print("   ユーザー様のタッチ待ち受け中 (30秒間)...")
    print("   タブレット画面の「心機能」カードを")
    print("   指で1回タップしてください！")
    print("==========================================")

    # getevent のすべてのイベントデバイスを監視
    cmd = [ADB, "-s", DEV, "shell", "getevent", "-l"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")

    x = None
    y = None
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            line = proc.stdout.readline()
            if not line:
                continue

            if "ABS_MT_POSITION_X" in line:
                val_hex = line.split()[-1]
                x = int(val_hex, 16)
            elif "ABS_MT_POSITION_Y" in line:
                val_hex = line.split()[-1]
                y = int(val_hex, 16)

            if "SYN_REPORT" in line and x is not None and y is not None:
                print("\n==========================================")
                print(f" SUCCESS! ユーザー様の「心機能」カードタップ位置を記録しました:")
                print(f" X 座標 = {x}")
                print(f" Y 座標 = {y}")
                print("==========================================\n")
                proc.terminate()
                return x, y
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()

    if x is not None and y is not None:
        return x, y

    print("\n[Timeout] タッチが検出されませんでした。")
    return None, None

if __name__ == "__main__":
    record_tap()
