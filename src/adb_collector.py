import subprocess
import time
import os
from datetime import datetime, timedelta, date
from pathlib import Path
from PIL import Image
import config
from src.calendar_picker import HealthCalendarPicker

class ADBCollector:
    def __init__(self, adb_path=config.ADB_PATH, device_id=config.DEVICE_ID):
        self.adb_path = str(adb_path)
        self.device_id = str(device_id)

    def _run_adb(self, args):
        """ADBコマンドを実行するヘルパー関数"""
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if result.returncode != 0 and "warning" not in result.stderr.lower():
            print(f"[ADB Notice] {result.stderr.strip()}")
        return result.stdout.strip()

    def check_connection(self):
        """ADB接続確認"""
        output = self._run_adb(["devices"])
        print("--- ADB Connected Devices ---")
        print(output)
        return self.device_id in output if self.device_id else len(output.splitlines()) > 1

    def wake_device(self):
        """画面を点灯させロックを解除する"""
        print("[Power] Waking up device screen and unlocking...")
        self._run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
        self._run_adb(["shell", "input", "keyevent", "224"])
        time.sleep(1)
        self._run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
        time.sleep(1)

    def launch_app(self, package_name=config.PACKAGE_NAME):
        """HUAWEIヘルスアプリの完全クリーン起動"""
        self.wake_device()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Force stopping and launching package: {package_name}...")
        self._run_adb(["shell", "am", "force-stop", package_name])
        time.sleep(1)
        self._run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
        print("Waiting 5 seconds for app top screen...")
        time.sleep(5)

    def back_to_top_gesture(self):
        """画面右端から左へスワイプ（戻るジェスチャー）でトップ画面へ復帰"""
        print("[Nav] Returning to Top Screen via right-edge back gesture...")
        self._run_adb(["shell", "input", "swipe", "1580", "1200", "1200", "1200", "200"])
        time.sleep(2)

    def capture_screenshot(self, save_path: Path):
        """画面をキャプチャし、真っ黒画像チェック後にPCへ保存"""
        remote_path = "/sdcard/screen_temp.png"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        self._run_adb(["shell", "screencap", "-p", remote_path])
        self._run_adb(["pull", remote_path, str(save_path)])
        
        # 描画不完全・消灯時のセーフティチェック
        try:
            img = Image.open(save_path).convert("L")
            # 画面中央部 (Y: 400〜2000) の輝度をチェック
            w, h = img.size
            crop_center = img.crop((100, 400, w - 100, h - 400))
            center_extrema = crop_center.getextrema()
            
            if center_extrema == (0, 0) or center_extrema[1] < 10:
                print(f"[Warning] Captured screenshot {save_path.name} content is empty/black! Waiting 4s and re-capturing...")
                time.sleep(4)
                self._run_adb(["shell", "screencap", "-p", remote_path])
                self._run_adb(["pull", remote_path, str(save_path)])
        except Exception as e:
            print(f"[Image Check Error] {e}")

        print(f"  Saved screenshot: {save_path.name}")

    # ==========================================
    # 1. 睡眠 (Sleep) 取得フロー
    # ==========================================
    def collect_sleep(self, days=config.DEFAULT_CAPTURE_DAYS):
        print(f"\n==================================================")
        print(f" [1/4] Sleep Data Capture ({days} days)")
        print(f"==================================================")
        
        print("[Sleep] Tapping Sleep Card (X=1350, Y=1150)...")
        self._run_adb(["shell", "input", "tap", "1350", "1150"])
        time.sleep(4)

        save_dir = config.SCREENSHOTS_DIR / "sleep"
        save_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now()

        for i in range(days):
            target_date = today - timedelta(days=i)
            date_str = target_date.strftime("%Y%m%d")
            filename = f"sleep_{date_str}.png"
            save_path = save_dir / filename

            print(f"[{i+1}/{days}] Capturing Sleep for {target_date.strftime('%Y/%m/%d')} -> {filename}")
            self.capture_screenshot(save_path)

            if i < days - 1:
                print("  Swiping to previous day (Left -> Right)...")
                self._run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
                time.sleep(2.5)

        self.back_to_top_gesture()
        print(" [Sleep] Completed and Returned to Top Screen.")

    # ==========================================
    # 2. 心機能 (Heart Rate) 取得フロー
    # ==========================================
    def collect_heart_rate(self, days=config.DEFAULT_CAPTURE_DAYS):
        print(f"\n==================================================")
        print(f" [2/4] Heart Rate Data Capture ({days} days)")
        print(f"==================================================")
        
        print("[Heart Rate] Tapping Heart Rate Card (X=1015, Y=1248)...")
        self._run_adb(["shell", "input", "tap", "1015", "1248"])
        time.sleep(4)

        save_dir = config.SCREENSHOTS_DIR / "heart_rate"
        save_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now()

        for i in range(days):
            target_date = today - timedelta(days=i)
            date_str = target_date.strftime("%Y%m%d")
            filename = f"heart_rate_{date_str}.png"
            save_path = save_dir / filename

            print(f"[{i+1}/{days}] Capturing Heart Rate for {target_date.strftime('%Y/%m/%d')} -> {filename}")
            self.capture_screenshot(save_path)

            if i < days - 1:
                print("  Swiping to previous day (Left -> Right)...")
                self._run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
                time.sleep(2.5)

        self.back_to_top_gesture()
        print(" [Heart Rate] Completed and Returned to Top Screen.")

    # ==========================================
    # 3. ストレス (Stress) 取得フロー
    # ==========================================
    def collect_stress(self, days=config.DEFAULT_CAPTURE_DAYS):
        print(f"\n==================================================")
        print(f" [3/4] Stress Data Capture ({days} days)")
        print(f"==================================================")
        
        print("[Stress] Tapping Stress Card (X=606, Y=1780)...")
        self._run_adb(["shell", "input", "tap", "606", "1780"])
        time.sleep(4.5)

        save_dir = config.SCREENSHOTS_DIR / "stress"
        save_dir.mkdir(parents=True, exist_ok=True)
        today = date.today()

        for i in range(days):
            target_date = today - timedelta(days=i)
            date_str = target_date.strftime("%Y%m%d")

            cx, cy = HealthCalendarPicker.get_date_coords(target_date)
            print(f"[{i+1}/{days}] Selecting {target_date.strftime('%Y/%m/%d')} (Calendar Coords: X={cx}, Y={cy})")

            self._run_adb(["shell", "input", "tap", "318", "374"])
            time.sleep(2)

            self._run_adb(["shell", "input", "tap", str(cx), str(cy)])
            time.sleep(3)

            filename = f"stress_{date_str}.png"
            save_path = save_dir / filename
            self.capture_screenshot(save_path)

        self.back_to_top_gesture()
        print(" [Stress] Completed and Returned to Top Screen.")

    # ==========================================
    # 4. 体組成 (Body Composition) 取得フロー
    # ==========================================
    def _get_past_body_comp_tap_info(self, days_ago):
        """過去日（1日前以降）の履歴画面でのスクロール回数とタップY座標を算出"""
        if days_ago <= 6:
            y_coords = {1: 640, 2: 1016, 3: 1320, 4: 1630, 5: 1940, 6: 2250}
            return 0, y_coords.get(days_ago, 640)
        else:
            offset_index = days_ago - 7
            scroll_count = 1 + (offset_index // 6)
            position_in_block = offset_index % 6
            tap_y = 410 + position_in_block * 310
            return scroll_count, tap_y

    def collect_body_composition(self, days=config.DEFAULT_CAPTURE_DAYS):
        print(f"\n==================================================")
        print(f" [4/4] Body Composition Data Capture ({days} days)")
        print("==================================================")
        
        save_dir = config.SCREENSHOTS_DIR / "body_composition"
        save_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now()

        # Step 1: トップ画面の体組成カードをタップ (X=200, Y=1650)
        print("[Body Comp] Step 1: Tapping Body Composition Card (X=200, Y=1650)...")
        self._run_adb(["shell", "input", "tap", "200", "1650"])
        print("  Waiting 6 seconds for Weight Summary loading...")
        time.sleep(6)

        # Step 2: 「身体計測データ」カードをタップ (X=800, Y=950) -> 当日詳細画面が開く
        print("[Body Comp] Step 2: Tapping Body Measurement Data (X=800, Y=950)...")
        self._run_adb(["shell", "input", "tap", "800", "950"])
        print("  Waiting 6 seconds for Target Body Data Detail Screen rendering...")
        time.sleep(6)

        # A. 当日 (0日前: 今日) の撮影
        today_str = today.strftime("%Y%m%d")
        print(f"\n[Body Comp Today] Capturing Today ({today.strftime('%Y/%m/%d')})...")
        top_path = save_dir / f"body_composition_{today_str}_top.png"
        self.capture_screenshot(top_path)

        print("  Scrolling to detail bottom...")
        self._run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "500"])
        time.sleep(2.5)

        bottom_path = save_dir / f"body_composition_{today_str}_bottom.png"
        self.capture_screenshot(bottom_path)

        # 当日のみの取得指示であれば、トップ画面へ戻って終了
        if days <= 1:
            print("[Body Comp] Finished Today capture. Returning to Top Screen...")
            self.back_to_top_gesture()
            self.back_to_top_gesture()
            print(" [Body Comp] Completed and Returned to Top Screen.")
            return

        # B. 過去日 (1日前〜N-1日前) の取得: 右上「履歴」ボタン (X=1476, Y=159) を開く
        print("\n[Body Comp History] Opening History List (X=1476, Y=159)...")
        self._run_adb(["shell", "input", "tap", "1476", "159"])
        time.sleep(3.5)

        for days_ago in range(1, days):
            target_date = today - timedelta(days=days_ago)
            date_str = target_date.strftime("%Y%m%d")
            date_fmt = target_date.strftime("%Y/%m/%d")

            scroll_count, tap_y = self._get_past_body_comp_tap_info(days_ago)
            print(f"\n[{days_ago+1}/{days}] Body Comp for {date_fmt} ({days_ago} days ago) -> Tap Y={tap_y}, Scrolls={scroll_count}")

            for s in range(scroll_count):
                print(f"  Scrolling history list ({s+1}/{scroll_count})...")
                self._run_adb(["shell", "input", "swipe", "800", "2000", "800", "260", "1500"])
                time.sleep(2.5)

            print(f"  Tapping item row at (X=800, Y={tap_y})...")
            self._run_adb(["shell", "input", "tap", "800", str(tap_y)])
            print("  Waiting 5 seconds for detail rendering...")
            time.sleep(5)

            top_path = save_dir / f"body_composition_{date_str}_top.png"
            self.capture_screenshot(top_path)

            print("  Scrolling to detail bottom...")
            self._run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "500"])
            time.sleep(2.5)

            bottom_path = save_dir / f"body_composition_{date_str}_bottom.png"
            self.capture_screenshot(bottom_path)

            print("  Returning to history list (BACK)...")
            self._run_adb(["shell", "input", "keyevent", "4"])
            time.sleep(2.5)

        for _ in range(3):
            self._run_adb(["shell", "input", "keyevent", "4"])
            time.sleep(1)

        print(" [Body Comp] Completed and Returned to Top Screen.")

    # ==========================================
    # 4大カテゴリ統合実行メソッド
    # ==========================================
    def collect_all_categories(self, days=config.DEFAULT_CAPTURE_DAYS):
        """睡眠 -> 心機能 -> ストレス -> 体組成 の順序で全自動連続取得"""
        if not self.check_connection():
            raise RuntimeError(f"Device {self.device_id} is not connected via ADB.")

        print("\n============================================================")
        print(f" Starting 4-Major Health Data Auto-Collector ({days} days)")
        print(f" Order: Sleep -> Heart Rate -> Stress -> Body Composition")
        print("============================================================")

        self.launch_app(config.PACKAGE_NAME)
        self.collect_sleep(days=days)
        self.collect_heart_rate(days=days)
        self.collect_stress(days=days)
        self.collect_body_composition(days=days)

        print("\n============================================================")
        print(f" All 4 Categories ({days} days) Successfully Captured!")
        print("============================================================\n")
        return True

if __name__ == "__main__":
    collector = ADBCollector()
    collector.collect_all_categories(days=1)
