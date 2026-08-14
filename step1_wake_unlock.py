import subprocess
import time
from pathlib import Path
import config

adb_path = config.ADB_PATH
device_id = config.DEVICE_ID

def run_adb(args):
    cmd = [adb_path, "-s", device_id] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

print("--- Executing Step 1: Screen Wake & Unlock Only ---")
run_adb(["shell", "input", "keyevent", "26"]) # 画面点灯
time.sleep(1)
run_adb(["shell", "input", "swipe", "800", "2200", "800", "200", "200"]) # ロック解除上スワイプ
time.sleep(1)

save_path = config.SCREENSHOTS_DIR / "step1_result.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
run_adb(["shell", "screencap", "-p", "/sdcard/screen_temp.png"])
run_adb(["pull", "/sdcard/screen_temp.png", str(save_path)])
print(f"Step 1 Completed. Saved screenshot: {save_path}")
