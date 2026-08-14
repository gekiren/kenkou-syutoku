import subprocess
import time
import os
import argparse
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

def capture_past_day_body_composition(days_ago, start_from_top=True):
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y/%m/%d')
    date_str_file = (datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d')
    
    print("==========================================")
    print(f"  体組成 ({days_ago}日前: {target_date}) 慣性なし自動取得フロー開始 ")
    print("==========================================")
    
    if start_from_top:
        # Step 0-1: 体重トップから「身体計測データ」カード (X=800, Y=950) をタップ
        print("[Step 0-1] 「身体計測データ」カード (X=800, Y=950) をタップ...")
        subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", "950"])
        time.sleep(2.5)
        
        # Step 0-2: 本日詳細画面から右上の履歴ボタン (X=1476, Y=159) をタップ
        print("[Step 0-2] 履歴ボタン (X=1476, Y=159) をタップして「すべてのデータ」画面を開く...")
        subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "1476", "159"])
        time.sleep(2.5)

    scroll_count, tap_y = get_tap_info(days_ago)
    print(f"  [計算結果] スクロール回数: {scroll_count}回, タップY座標: Y={tap_y}")
    
    # 必要回数スクロール (慣性なし: 1500ms, 1860px移動)
    for i in range(scroll_count):
        print(f"[Step 1-{i+1}] 履歴リストを加速なし(1500ms)でスワイプ ({i+1}/{scroll_count})...")
        subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2060", "800", "200", "1500"])
        time.sleep(2.5)

    # 対象データ行をタップ
    print(f"[Step 2] {days_ago}日前データ行 (X=800, Y={tap_y}) をタップ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "tap", "800", str(tap_y)])
    time.sleep(3)
    
    # 上部スクリーンショット撮影
    print(f"[Step 3] {days_ago}日前 ({target_date} 上部) スクリーンショット撮影...")
    top_png_sd = f"/sdcard/body_composition_{days_ago}days_ago_top.png"
    top_png_local = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_str_file}_top.png")
    os.makedirs(os.path.dirname(top_png_local), exist_ok=True)
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", top_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", top_png_sd, top_png_local])
    print(f"  └─ 保存完了: {top_png_local}")
    
    # 最下部までスワイプ
    print("[Step 4] 詳細画面の最下部へスワイプ...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "swipe", "800", "2000", "800", "500", "500"])
    time.sleep(2)
    
    # 下部スクリーンショット撮影
    print(f"[Step 5] {days_ago}日前 ({target_date} 下部) スクリーンショット撮影...")
    bottom_png_sd = f"/sdcard/body_composition_{days_ago}days_ago_bottom.png"
    bottom_png_local = os.path.join(config.SCREENSHOTS_DIR, "body_composition", f"body_composition_{date_str_file}_bottom.png")
    
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", bottom_png_sd])
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", bottom_png_sd, bottom_png_local])
    print(f"  └─ 保存完了: {bottom_png_local}")
    
    # 履歴画面へ戻る (BACKキー)
    print("[Step 6] 履歴画面へ戻る (BACKキー)...")
    subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "input", "keyevent", "4"])
    time.sleep(2)
    
    print("\n==========================================")
    print(f" SUCCESS: {days_ago}日前 ({target_date}) の体組成データ取得完了！")
    print("==========================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指定した過去日数の体組成データを自動取得")
    parser.add_argument("--days-ago", type=int, default=7, help="何日前のデータを取得するか (1以上)")
    parser.add_argument("--no-start-from-top", action="store_true", help="トップ画面からの遷移ステップをスキップする")
    args = parser.parse_args()
    
    capture_past_day_body_composition(args.days_ago, start_from_top=not args.no_start_from_top)
