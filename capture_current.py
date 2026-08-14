import subprocess
import os
import config

os.makedirs("data/screenshots", exist_ok=True)
# 画面消灯タイムアウト 30分設定
subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
# スクショ撮影
subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "shell", "screencap", "-p", "/sdcard/current_screen.png"])
subprocess.run([config.ADB_PATH, "-s", config.DEVICE_ID, "pull", "/sdcard/current_screen.png", "data/screenshots/current_screen.png"])
print("Captured current_screen.png successfully.")
