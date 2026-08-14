import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
import config

class ADBCollector:
    def __init__(self, adb_path=config.ADB_PATH, device_id=config.DEVICE_ID):
        self.adb_path = adb_path
        self.device_id = device_id

    def _run_adb(self, args):
        """ADBコマンドを実行するヘルパー関数"""
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if result.returncode != 0:
            print(f"[ADB Warning/Error] {result.stderr.strip()}")
        return result.stdout.strip()

    def check_connection(self):
        """ADB接続確認"""
        output = self._run_adb(["devices"])
        print("--- ADB Connected Devices ---")
        print(output)
        return self.device_id in output if self.device_id else len(output.splitlines()) > 1

    def wake_device(self):
        """画面を点灯させロックを解除する"""
        print(" Waking up device screen and unlocking...")
        # 画面点灯 (Keyevent 26)
        self._run_adb(["shell", "input", "keyevent", "26"])
        time.sleep(1)
        # 上スワイプでロック解除
        self._run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
        time.sleep(1)

    def launch_app(self, package_name=config.PACKAGE_NAME):
        """HUAWEIヘルスアプリの完全クリーン起動 (画面点灯・ロック解除後に実行)"""
        self.wake_device()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Force stopping and launching package: {package_name}...")
        self._run_adb(["shell", "am", "force-stop", package_name])
        time.sleep(1)
        self._run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
        time.sleep(5)  # トップ画面読み込み待ち

    def swipe_prev_day(self):
        """前日のデータ表示画面へスワイプ (画面中央を左から右へスワイプ)"""
        self._run_adb(["shell", "input", "swipe", "200", "1000", "800", "1000", "300"])
        time.sleep(2)  # 描画待ち

    def capture_screenshot(self, save_path: Path):
        """画面をキャプチャし、真っ黒画像チェック後にPCへ保存"""
        remote_path = "/sdcard/screen_temp.png"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        self._run_adb(["shell", "screencap", "-p", remote_path])
        self._run_adb(["pull", remote_path, str(save_path)])
        
        # 真っ黒画像（スリープ状態）のチェック
        try:
            from PIL import Image
            img = Image.open(save_path).convert("L")
            extrema = img.getextrema()
            if extrema == (0, 0) or extrema[1] < 10:  # 完全な黒画像
                print(f"[Warning] Captured screenshot {save_path.name} is BLACK! Attempting screen wake...")
                self.wake_device()
                time.sleep(2)
                # 再撮影
                self._run_adb(["shell", "screencap", "-p", remote_path])
                self._run_adb(["pull", remote_path, str(save_path)])
        except Exception as e:
            print(f"[Image Check Error] {e}")

        print(f" Saved screenshot: {save_path.name}")

    def collect_days(self, days=config.DEFAULT_CAPTURE_DAYS, category="sleep"):
        """各カテゴリのカードをタップして詳細画面を開き、当日および前日のスクリーンショットをキャプチャ"""
        if not self.check_connection():
            raise RuntimeError(f"Device {self.device_id} is not connected via ADB.")

        # カテゴリごとのトップ画面上のカードタップ座標 (解像度 1600x2560)
        card_coords = {
            "sleep": (1350, 1150),
            "heart_rate": (900, 1150),
            "body_composition": (200, 1650),
            "stress": (650, 1650),
            "spo2": (1150, 1650)
        }

        # 全カテゴリ指定時の処理
        target_categories = config.CATEGORIES if category == "all" else [category]

        for cat in target_categories:
            print(f"\n==================================================")
            print(f" Starting Detail Screen Capture for [{cat.upper()}] ({days} days)...")
            print(f"==================================================")
            
            # 1. 画面点灯 ＆ ロック解除
            self.wake_device()
            
            # 2. タスクキル ➔ アプリを新規起動 (クリーンなトップ画面を保証)
            self._run_adb(["shell", "am", "force-stop", config.PACKAGE_NAME])
            time.sleep(1)
            self.launch_app(config.PACKAGE_NAME)
            time.sleep(4)

            # 3. 対象カテゴリのカードをタップして詳細画面を開く
            if cat in card_coords:
                tx, ty = card_coords[cat]
                print(f" Tapping [{cat}] card at (X={tx}, Y={ty}) to open Detail Screen...")
                self._run_adb(["shell", "input", "tap", str(tx), str(ty)])
                time.sleep(3)  # 詳細画面の読み込み待ち

            # 今日の日付から過去N日分をループ撮影
            for i in range(days):
                target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                date_str = target_date.replace("-", "")
                filename = f"{cat}_{date_str}.png"
                save_path = config.SCREENSHOTS_DIR / cat / filename

                print(f"[{i+1}/{days}] Capturing [{cat}] Detail Screen for {target_date} -> {filename}")
                self.capture_screenshot(save_path)

                if i < days - 1:
                    print(f" Swiping to previous day ({i+1} -> {i+2})...")
                    # 詳細画面内で左から右へスワイプ (前日へ移動)
                    self._run_adb(["shell", "input", "swipe", "300", "1000", "1300", "1000", "300"])
                    time.sleep(2)  # 画面切り替え待ち

            # バックボタンでトップ画面へ復帰
            self._run_adb(["shell", "input", "keyevent", "4"])
            time.sleep(1)

        print("\n All requested category screenshots captured successfully!")
        return True

if __name__ == "__main__":
    collector = ADBCollector()
    collector.collect_days(days=1, category="sleep")
