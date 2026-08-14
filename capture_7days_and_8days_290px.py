import subprocess
import time
import os
from datetime import datetime, timedelta
import config

def reset_and_launch_app():
    print("[App Reset] ヘルスケアアプリを完全フォースストップ & クリーン起動...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "am", "force-stop", config.PACKAGE_NAME])
    time.sleep(1)
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "monkey", "-p", config.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(5)

def capture_7days_and_8days():
    date_7days_str = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    date_8days_str = (datetime.now() - timedelta(days=8)).strftime('%Y%m%d')
    date_7days_fmt = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
    date_8days_fmt = (datetime.now() - timedelta(days=8)).strftime('%Y/%m/%d')
    
    print("==========================================")
    print(f"  体組成 (7日前:{date_7days_fmt} & 8日前:{date_8days_fmt}) 自動取得開始 ")
    print("  パラメータ: 290px × 6日分 = 1740px (1500ms等速)")
    print("==========================================")
    
    # 1. アプリをクリーン起動
    reset_and_launch_app()
    
    # 2. 「体組成(体重)」カード -> 「身体計測データ」 -> 時計アイコン(履歴)
    print("[Step 1] トップ画面の「体組成(体重)」カード (X=200, Y=1650) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "200", "1650"])
    time.sleep(3)

    print("[Step 2] 「身体計測データ」 (X=800, Y=950) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "950"])
    time.sleep(2.5)

    print("[Step 3] 右上履歴ボタン (X=1476, Y=159) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "1476", "159"])
    time.sleep(2.5)

    # 3. 290px × 6日分 = 1740px (1500ms) スワイプ
    print("[Step 4] 履歴リストを290px×6日分(1740px, 1500ms)で等速スワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "260", "1500"])
    time.sleep(2.5)

    # ==========================================
    # A. 7日前 (2026/8/7) の取得 (カード領域 Y=220)
    # ==========================================
    print(f"\n--- [7日前: {date_7days_fmt}] データ取得 ---")
    print(f"[Step A-1] 7日前データカード (X=800, Y=220) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "220"])
    time.sleep(3)

    print(f"[Step A-2] 7日前 ({date_7days_fmt} 上部) スクリーンショット撮影...")
    top_png_sd_7 = "/sdcard/body_composition_7days_ago_top.png"
    top_png_local_7 = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_7days_str}_top.png")
    os.makedirs(os.path.dirname(top_png_local_7), exist_ok=True)
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", top_png_sd_7])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", top_png_sd_7, top_png_local_7])
    print(f"  └─ 保存完了: {top_png_local_7}")

    print("[Step A-3] 詳細画面の最下部へスワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "500", "500"])
    time.sleep(2)

    print(f"[Step A-4] 7日前 ({date_7days_fmt} 下部) スクリーンショット撮影...")
    bottom_png_sd_7 = "/sdcard/body_composition_7days_ago_bottom.png"
    bottom_png_local_7 = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_7days_str}_bottom.png")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", bottom_png_sd_7])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", bottom_png_sd_7, bottom_png_local_7])
    print(f"  └─ 保存完了: {bottom_png_local_7}")

    print("[Step A-5] 履歴画面へ戻る (BACKキー)...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "keyevent", "4"])
    time.sleep(2.5)

    # ==========================================
    # B. 8日前 (2026/8/6) の取得 (カード領域 Y=530)
    # ==========================================
    print(f"\n--- [8日前: {date_8days_fmt}] データ取得 ---")
    print(f"[Step B-1] 8日前データカード (X=800, Y=530) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "530"])
    time.sleep(3)

    print(f"[Step B-2] 8日前 ({date_8days_fmt} 上部) スクリーンショット撮影...")
    top_png_sd_8 = "/sdcard/body_composition_8days_ago_top.png"
    top_png_local_8 = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_8days_str}_top.png")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", top_png_sd_8])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", top_png_sd_8, top_png_local_8])
    print(f"  └─ 保存完了: {top_png_local_8}")

    print("[Step B-3] 詳細画面の最下部へスワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "500", "500"])
    time.sleep(2)

    print(f"[Step B-4] 8日前 ({date_8days_fmt} 下部) スクリーンショット撮影...")
    bottom_png_sd_8 = "/sdcard/body_composition_8days_ago_bottom.png"
    bottom_png_local_8 = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_8days_str}_bottom.png")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", bottom_png_sd_8])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", bottom_png_sd_8, bottom_png_local_8])
    print(f"  └─ 保存完了: {bottom_png_local_8}")

    print("[Step B-5] 履歴画面へ戻る (BACKキー)...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "keyevent", "4"])
    time.sleep(2)

    print("\n==========================================")
    print(f" SUCCESS: 7日前({date_7days_fmt}) および 8日前({date_8days_fmt}) の全自動データ取得完了！")
    print("==========================================\n")

if __name__ == "__main__":
    capture_7days_and_8days()
