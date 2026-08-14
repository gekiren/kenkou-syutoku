import os
from pathlib import Path
from dotenv import load_dotenv

# .env ファイルがあれば読み込み
load_dotenv()

# プロジェクトルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent

# ADBおよびデバイス設定
ADB_PATH = os.getenv("ADB_PATH", "")
DEVICE_ID = os.getenv("DEVICE_ID", "")
PACKAGE_NAME = os.getenv("PACKAGE_NAME", "com.huawei.health")

# デフォルト取得日数
DEFAULT_CAPTURE_DAYS = 7

# サポートする全データカテゴリ
CATEGORIES = ["sleep", "spo2", "stress", "body_composition", "heart_rate"]

# トップ画面での各カテゴリカードの正確なタップ座標 (解像度 1600x2560)
CARD_COORDS = {
    "sleep": (1350, 1150),
    "heart_rate": (1015, 1248),
    "body_composition": (200, 1650),
    "stress": (606, 1780),
    "spo2": (1150, 1650)
}

# データ保存ディレクトリ
DATA_DIR = BASE_DIR / "data"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
JSON_DIR = DATA_DIR / "json"
OUTPUT_DIR = DATA_DIR / "output"

# カテゴリ別サブディレクトリ
for category in CATEGORIES:
    (SCREENSHOTS_DIR / category).mkdir(parents=True, exist_ok=True)
    (JSON_DIR / category).mkdir(parents=True, exist_ok=True)

# ルート保存ディレクトリ自動生成
for directory in [SCREENSHOTS_DIR, JSON_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Gemini APIキー設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Obsidian Vault 出力先（環境変数 OBSIDIAN_KENKOU_DIR で任意の Vault ディレクトリへ上書き可能）
# 未設定の場合はプロジェクト内の data/obsidian を既定の出力先として使用する（マシン非依存の共通挙動）。
_obsidian_env = os.getenv("OBSIDIAN_KENKOU_DIR")
if _obsidian_env:
    OBSIDIAN_OUTPUT_DIR = Path(_obsidian_env)
else:
    OBSIDIAN_OUTPUT_DIR = DATA_DIR / "obsidian"
OBSIDIAN_DAILY_DIR = OBSIDIAN_OUTPUT_DIR / "Daily"
OBSIDIAN_DATA_DIR  = OBSIDIAN_OUTPUT_DIR / "data"

# Obsidian 出力フォルダを自動生成
for _obs_dir in [OBSIDIAN_OUTPUT_DIR, OBSIDIAN_DAILY_DIR, OBSIDIAN_DATA_DIR]:
    _obs_dir.mkdir(parents=True, exist_ok=True)

