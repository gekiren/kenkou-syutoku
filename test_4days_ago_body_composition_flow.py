import subprocess
import time
import os
import config

def capture_4days_ago_body_composition():
    print("==========================================")
    print("  体組成 (4日前: 2026/8/10) 取得フロー開始 ")
    print("==========================================")
    
    # 4日前データ行 (X=800, Y=1630) をタップ
    print("[Step 1] 4日前データ行 (X=800, Y=1630) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "1630"])
    time.sleep(3)
    
    # 上部スクリーンショット撮影
    print("[Step 2] 4日前 (上部) スクリーンショット撮影...")
    top_png_sd = "/sdcard/body_composition_4days_ago_top.png"
    top_png_local = os.path.join(config.SCREENSHOTS_DIR, "body_composition", "body_composition_4days_ago_top.png")
    os.makedirs(os.path.dirname(top_png_local), exist_ok=True)
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", top_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", top_png_sd, top_png_local])
    print(f"  └─ 保存完了: {top_png_local}")
    
    # 最下部までスワイプ
    print("[Step 3] 最下部へスワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "500", "500"])
    time.sleep(2)
    
    # 下部スクリーンショット撮影
    print("[Step 4] 4日前 (下部) スクリーンショット撮影...")
    bottom_png_sd = "/sdcard/body_composition_4days_ago_bottom.png"
    bottom_png_local = os.path.join(config.SCREENSHOTS_DIR, "body_composition", "body_composition_4days_ago_bottom.png")
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", bottom_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", bottom_png_sd, bottom_png_local])
    print(f"  └─ 保存完了: {bottom_png_local}")
    
    # 履歴画面へ戻る (BACKキー)
    print("[Step 5] 履歴画面へ戻る...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "keyevent", "4"])
    time.sleep(2)
    
    print("\n==========================================")
    print(" SUCCESS: 4日前 (2026/8/10) の体組成データ取得完了！")
    print("==========================================\n")

if __name__ == "__main__":
    capture_4days_ago_body_composition()
