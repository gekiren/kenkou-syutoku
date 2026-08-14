import subprocess
import time
import os
import config

def capture_2days_ago_body_composition():
    print("==========================================")
    print("  体組成 (2日前: 過去日付) 取得フロー開始 ")
    print("==========================================")
    
    # 1. 履歴ボタンのタップ (X=1476, Y=159)
    print("[Step 1] 履歴ボタン (X=1476, Y=159) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "1476", "159"])
    time.sleep(2)
    
    # 2. 2日前 (8/12等) データ行のタップ (X=798, Y=1016)
    print("[Step 2] 2日前データ行 (X=798, Y=1016) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "798", "1016"])
    time.sleep(3)
    
    # 3. 1枚目 (上部) スクリーンショット撮影
    print("[Step 3] 2日前 (上部) スクリーンショット撮影...")
    top_png_sd = "/sdcard/body_composition_2days_ago_top.png"
    top_png_local = os.path.join(config.SCREENSHOT_DIR, "body_composition", "body_composition_2days_ago_top.png")
    os.makedirs(os.path.dirname(top_png_local), exist_ok=True)
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", top_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", top_png_sd, top_png_local])
    print(f"  └─ 保存完了: {top_png_local}")
    
    # 4. 最下部までスワイプ (800 2000 -> 800 500)
    print("[Step 4] 最下部へスワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "500", "500"])
    time.sleep(2)
    
    # 5. 2枚目 (下部) スクリーンショット撮影
    print("[Step 5] 2日前 (下部) スクリーンショット撮影...")
    bottom_png_sd = "/sdcard/body_composition_2days_ago_bottom.png"
    bottom_png_local = os.path.join(config.SCREENSHOT_DIR, "body_composition", "body_composition_2days_ago_bottom.png")
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", bottom_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", bottom_png_sd, bottom_png_local])
    print(f"  └─ 保存完了: {bottom_png_local}")
    
    print("\n==========================================")
    print(" SUCCESS: 2日前 (過去日付) の体組成データ取得完了！")
    print("==========================================\n")

if __name__ == "__main__":
    capture_2days_ago_body_composition()
