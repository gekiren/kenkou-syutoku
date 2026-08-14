import subprocess
import time
import config

ADB = config.ADB_PATH
DEV = config.DEVICE_ID
PKG = config.PACKAGE_NAME

def run_adb(args):
    cmd = [ADB, "-s", DEV] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

print("[1/3] 画面点灯 & ロック解除...")
run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "1800000"])
run_adb(["shell", "input", "keyevent", "224"])
time.sleep(1)
run_adb(["shell", "input", "swipe", "800", "2000", "800", "500", "200"])
time.sleep(1)

print("[2/3] ヘルスケアアプリ起動...")
run_adb(["shell", "am", "force-stop", PKG])
time.sleep(1)
run_adb(["shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"])
time.sleep(5)

print("[3/3] 情緒（ストレス）カード (X=606, Y=1780) をタップ...")
run_adb(["shell", "input", "tap", "606", "1780"])
time.sleep(3)

print("=== 当日のストレス画面を開きました ===")
