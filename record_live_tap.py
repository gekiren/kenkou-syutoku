import subprocess
import time
import sys
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID

def record_tap(timeout=60):
    print("\n==========================================")
    print("   ユーザー様のタッチ待ち受け中 (60秒間)...")
    print("   タブレット画面の「前日への移動操作」を")
    print("   指で1回タップしてください！")
    print("==========================================")

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
                print(f" SUCCESS! ユーザー様のタップ位置を記録しました:")
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
