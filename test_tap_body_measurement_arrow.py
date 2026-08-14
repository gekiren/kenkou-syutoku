import subprocess
import time
from pathlib import Path
import config
from src.adb_collector import ADBCollector

collector = ADBCollector()

def run_adb(args):
    cmd = [config.ADB_PATH, "-s", config.DEVICE_ID] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

print("--- Tapping '身体計測データ >' Arrow Icon (X=930, Y=350) ---")
run_adb(["shell", "input", "tap", "930", "350"])
time.sleep(3)

save_path = config.SCREENSHOTS_DIR / "body_composition" / "body_composition_top.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
collector.capture_screenshot(save_path)
print(f"Captured Body Composition Top Screen: {save_path.name}")
