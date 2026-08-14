import subprocess
import time
import os
import config

def record_7days_tap():
    print("==========================================")
    print(" 履歴一覧の初期表示を開き、")
    print(" 「290px × 6日分 (1740px, 1500ms)」慣性なしスワイプを実行します...")
    print("==========================================")
    
    # 1. 履歴一覧（初期表示）へ移動
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "keyevent", "4"])
    time.sleep(1)
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "keyevent", "4"])
    time.sleep(1)
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "950"])
    time.sleep(2)
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "1476", "159"])
    time.sleep(2)

    # 2. 290px × 6日分 = 1740px スワイプ
    print("[Action] 290px×6日分 (1740px, 1500ms) スワイプ中...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "260", "1500"])
    time.sleep(2)

    print("\n==========================================")
    print(" スワイプ完了！")
    print(" 画面上の「7日前 (2026/8/7)」のデータ行を")
    print(" 指で1回タップしてください！ (待ち受け20秒間)")
    print("==========================================")

    cmd = [config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "getevent", "-l", "/dev/input/event4"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    
    x, y = None, None
    start_time = time.time()
    try:
        while time.time() - start_time < 20:
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
                print(f" SUCCESS! ユーザー様の「7日前」タップ位置を記録しました:")
                print(f"  X 座標 = {x}")
                print(f"  Y 座標 = {y}")
                print("==========================================\n")
                proc.terminate()
                return x, y
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
    
    print("\n[Timeout] 20秒以内にタップが検出されませんでした。")
    return None, None

if __name__ == "__main__":
    record_7days_tap()
