import subprocess
import time
import re
import config

def record_swipe():
    print("==========================================")
    print("   ユーザー様のスワイプ操作待ち受け中 (20秒間)...")
    print("   タブレット画面の「履歴一覧」で")
    print("   指で1回スワイプ（スクロール）してください！")
    print("==========================================")
    
    cmd = [config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "getevent", "-l", "/dev/input/event4"]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    
    start_x, start_y = None, None
    last_x, last_y = None, None
    cur_x, cur_y = None, None
    
    start_time = time.time()
    touch_active = False
    
    try:
        while time.time() - start_time < 20:
            line = proc.stdout.readline()
            if not line:
                continue
            
            if "ABS_MT_POSITION_X" in line:
                val_hex = line.split()[-1]
                cur_x = int(val_hex, 16)
            elif "ABS_MT_POSITION_Y" in line:
                val_hex = line.split()[-1]
                cur_y = int(val_hex, 16)
            
            if "SYN_REPORT" in line:
                if cur_x is not None and cur_y is not None:
                    if not touch_active:
                        start_x, start_y = cur_x, cur_y
                        touch_active = True
                    last_x, last_y = cur_x, cur_y
            
            # タッチ離されたイベント（UP）またはタイムアウトで判定
            if "BTN_TOUCH" in line and "UP" in line and touch_active:
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
    
    if start_x is not None and start_y is not None and last_x is not None and last_y is not None:
        delta_y = start_y - last_y
        print("\n==========================================")
        print(" SUCCESS! スワイプ操作の計測完了:")
        print(f"  開始座標: (X = {start_x}, Y = {start_y})")
        print(f"  終了座標: (X = {last_x}, Y = {last_y})")
        print(f"  垂直スワイプ移動量 (Y方向): {delta_y} px")
        print("==========================================\n")
        return start_x, start_y, last_x, last_y, delta_y
    else:
        print("\n[Timeout] 20秒以内にスワイプが検出されませんでした。")
        return None

if __name__ == "__main__":
    record_swipe()
