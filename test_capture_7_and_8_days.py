import subprocess
import time
import os
from datetime import datetime, timedelta
import config

def get_tap_info(days_ago):
    """
    過去何日前に応じたスクロール回数とタップY座標を算出する
    """
    if days_ago <= 0:
        raise ValueError("days_ago must be >= 1")
    
    if days_ago <= 6:
        scroll_count = 0
        y_coords = {1: 640, 2: 1016, 3: 1320, 4: 1630, 5: 1940, 6: 2250}
        tap_y = y_coords[days_ago]
    else:
        offset_index = days_ago - 7
        scroll_count = 1 + (offset_index // 6)
        position_in_block = offset_index % 6
        tap_y = 640 + position_in_block * 310
        
    return scroll_count, tap_y

def reset_and_launch_app():
    print("[App Reset] ヘルスケアアプリを完全フォースストップ & クリーン起動...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "am", "force-stop", config.PACKAGE_NAME])
    time.sleep(1)
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "monkey", "-p", config.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(5)

def capture_day(days_ago):
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y/%m/%d')
    date_str_file = (datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d')
    
    print("\n==========================================")
    print(f"  体組成 ({days_ago}日前: {target_date}) 取得開始 ")
    print("==========================================")
    
    # 1. クリーン起動
    reset_and_launch_app()
    
    # 2. トップ画面の「体重」カード (X=200, Y=1650) をタップして体重トップ画面へ
    print("[Step 1] トップ画面の「体組成(体重)」カード (X=200, Y=1650) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "200", "1650"])
    time.sleep(3)

    # 3. 体重トップ画面から「身体計測データ」 (X=800, Y=950) をタップ
    print("[Step 2] 「身体計測データ」 (X=800, Y=950) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "950"])
    time.sleep(2.5)

    # 4. 本日詳細画面から「履歴ボタン」 (X=1476, Y=159) をタップ
    print("[Step 3] 右上履歴ボタン (X=1476, Y=159) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "1476", "159"])
    time.sleep(2.5)

    scroll_count, tap_y = get_tap_info(days_ago)
    print(f"  [計算結果] スクロール回数: {scroll_count}回, タップY座標: Y={tap_y}")
    
    # 必要回数スクロール (慣性なし: 1500ms, 1860px移動)
    for i in range(scroll_count):
        print(f"[Step 4-{i+1}] 履歴リストを加速なし(1500ms)でスワイプ ({i+1}/{scroll_count})...")
        subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2060", "800", "200", "1500"])
        time.sleep(2.5)

    # 5. 対象データ行をタップ
    print(f"[Step 5] {days_ago}日前データ行 (X=800, Y={tap_y}) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", str(tap_y)])
    time.sleep(3)
    
    # 6. 上部スクリーンショット撮影
    print(f"[Step 6] {days_ago}日前 ({target_date} 上部) スクリーンショット撮影...")
    top_png_sd = f"/sdcard/body_composition_{days_ago}days_ago_top.png"
    top_png_local = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_str_file}_top.png")
    os.makedirs(os.path.dirname(top_png_local), exist_ok=True)
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", top_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", top_png_sd, top_png_local])
    print(f"  └─ 保存完了: {top_png_local}")
    
    # 7. 最下部までスワイプ
    print("[Step 7] 詳細画面の最下部へスワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "500", "500"])
    time.sleep(2)
    
    # 8. 下部スクリーンショット撮影
    print(f"[Step 8] {days_ago}日前 ({target_date} 下部) スクリーンショット撮影...")
    bottom_png_sd = f"/sdcard/body_composition_{days_ago}days_ago_bottom.png"
    bottom_png_local = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_str_file}_bottom.png")
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", bottom_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", bottom_png_sd, bottom_png_local])
    print(f"  └─ 保存完了: {bottom_png_local}")
    
    print(f" SUCCESS: {days_ago}日前 ({target_date}) の体組成データ取得完了！\n")

if __name__ == "__main__":
    # 7日前と8日前を連続実行
    capture_day(7)
    capture_day(8)
