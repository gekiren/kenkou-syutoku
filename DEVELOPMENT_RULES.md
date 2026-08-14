# ⚠️ 開発・運用ルール (DEVELOPMENT_RULES.md)

このプロジェクト（KENKOU SYUTOKU / HUAWEI Health 自動収集パイプライン）を開発するすべてのAIエージェントおよび開発者は、以下のワークフローおよびルールを無条件で完全に遵守しなければなりません。

---

## 0. プロジェクト概要

> [!IMPORTANT]
> **KENKOU SYUTOKU = 「HUAWEI Health アプリの ADB 自動操作 × Gemini Vision AI 解析」による健康データ自動収集パイプライン（Python製）**

- **取得カテゴリ**: `sleep`（睡眠）/ `heart_rate`（心機能）/ `stress`（ストレス）/ `body_composition`（体組成）/ `spo2`（血中酸素・ADB収集は未実装）
- **パイプライン**:
  1. **ADBキャプチャ** (`src/adb_collector.py`): HUAWEI Health アプリを自動操作しスクリーンショットを取得
  2. **Vision AI解析** (`src/data_extractor.py`): Gemini で JSON 構造化し `data/json/{category}/` に保存
  3. **レポート生成** (`src/report_generator.py`): CSV / Excel / Markdown 生成と Obsidian Vault への同期
- **技術スタック**: Python 3.14 / venv / google-genai / Pillow / pandas / openpyxl / python-dotenv / ADB（実機: 解像度 1600x2560）
- **実行入口**: `main.py`（オプション: `--days`, `--category`, `--skip-adb`, `--skip-extract`）

---

## 1. 環境構築・実行ルール

1. **venv 環境の使用を厳守**:
   - 依存関係のインストール・実行はすべて `venv` 内で行うこと。
   - PowerShell: `.\venv\Scripts\Activate.ps1` でアクティベートしてから実行する。
2. **依存関係は `requirements.txt` で管理**:
   - 新規ライブラリを追加したら必ず `requirements.txt` に反映する。
3. **設定は `.env` ファイルで管理**（`config.py` が `python-dotenv` で読込）:
   - `.env` は Git 管理対象外（`.gitignore` 済み）。追加・変更した環境変数は必ず `.env.example` にも反映する。
   - **個人環境依存の絶対パス（例: `C:\Users\toshi\...`）をコードや設定にハードコードしてはならない。** パスは `config.py` の `BASE_DIR` 基準で解決し、ユーザー固有値は `.env` 経由で取得する。
4. **実行コマンド**:
   ```powershell
   python main.py --days 7                    # 全カテゴリ・7日分を自動収集
   python main.py --category stress --days 7  # 単一カテゴリのみ
   python main.py --skip-adb                  # 既存スクリーンショットのみ解析
   python main.py --skip-extract              # ADBキャプチャのみ実行
   ```
5. **ADB 接続前提**: 実機の USB デバッグ有効化・画面ロック解除が必須。`DEVICE_ID` は `.env` で指定する（複数デバイス接続時は必須）。
---

## 2. 設定管理 (config.py)

- すべての設定・座標・パスは `config.py` に一元定義し、各モジュールでハードコードしない。
- **画面タップ座標は `CARD_COORDS` に一元管理**（解像度 1600x2560 の実測値）。実機の解像度・UI変更時は必ず実測し直して更新する。
- **カテゴリ追加時の更新手順（漏れ防止チェックリスト）**:
  1. `config.CATEGORIES` にカテゴリ名を追加
  2. `config.CARD_COORDS` にタップ座標を追加
  3. `src/adb_collector.py` に `collect_xxx(days=...)` メソッドを実装
  4. `src/data_extractor.py` の解析プロンプトに JSON スキーマ（抽出項目）を追加
  5. `main.py` の `--category` 分岐を追加

---

## 3. アーキテクチャと実装規約

### モジュール責務
| モジュール | 責務 |
| :--- | :--- |
| `config.py` | 全設定の一元管理（環境変数 + デフォルト値） |
| `src/adb_collector.py` | ADB によるアプリ操作・画面遷移・スクリーンショット取得 |
| `src/data_extractor.py` | Gemini Vision AI による JSON 抽出・モックフォールバック・`processed/` アーカイブ |
| `src/report_generator.py` | CSV / Excel / Markdown レポート生成・Obsidian Vault 同期 |
| `src/calendar_picker.py` | ストレス取得用カレンダーの日付→タップ座標の動的計算 |

### ファイル命名規則（厳守）
- スクリーンショット: `{category}_{YYYYMMDD}.png`（例: `sleep_20260814.png`）
- 体組成のみ上下2枚: `body_composition_{YYYYMMDD}_top.png` / `body_composition_{YYYYMMDD}_bottom.png`
- 解析 JSON: 元画像の `stem.json`（`data/json/{category}/` に保存）
- **ファイル名には必ず 8 桁の日付 `YYYYMMDD` を含める**（`data_extractor` の解析対象判定・日付抽出に使用される）。

### データディレクトリ構造
```
data/
├── screenshots/{category}/   # 取得したPNG（解析完了後は processed/ へ移動）
├── json/{category}/          # Gemini 解析結果の JSON
└── output/                   # CSV / Excel / Markdown レポート
```

### その他
- 解析完了画像は `_move_to_processed()` で必ず `processed/` フォルダへ移動する（二重解析防止）。
- 調査用のワンオフスクリプト（`test_*.py`, `capture_*.py`, `record_*.py`）は恒久スクリプトと判別できる名前付けとし、作業完了後は `tests/`・`scripts/` への整理を検討する。
---

## 4. Gemini Vision AI 仕様（データ抽出）

> [!CAUTION]
> **モデルフォールバックチェーン（多重冗長化）を必ず維持すること**

- **プライマリモデル**: `gemini-3.7-flash`
- **フォールバックチェーン**（上から順に自動リトライ）:
  1. `gemini-3.7-flash`
  2. `gemini-3.6-flash`
  3. `gemini-3.5-flash`
  4. `gemini-3.5-flash-lite`
  5. `gemini-3.1-flash-lite`
- **旧モデル名の禁止**: `gemini-2.x` 以前のモデル名を指定すると `404 NOT_FOUND` で失敗するため使用禁止。
- **`generationConfig` に `temperature` / `top_p` を含めない**（Gemini 3.7 系では HTTP 400 エラーになるため）。
- **API キー未設定時**: 警告を出し、モックデータ（`_generate_mock_data()`）で代替する。全モデル失敗時は `"error"` フィールドを付与する。
- レスポンスの ```` ```json ```` フェンスは `_clean_json_string()` で除去し、`json.loads()` でパースする。

---

## 5. ADB 実機操作の鉄則

1. **解像度 1600x2560 前提**: 全タップ・スワイプ座標はこの解像度で実測された値。異なる実機では必ず再実測する。
2. **座標は `config.CARD_COORDS` / `calendar_picker` 経由で参照**（ハードコード禁止）。
3. **画面復帰は `back_to_top_gesture()`（右端スワイプ）または `launch_app()`（クリーン起動）で確実に行う**。固定回数のバックキー連打は不安定（既知リスク）なため、詳細画面の深さに応じて判断する。
4. **ブラック画像チェックは必須**: `capture_screenshot()` は保存後、中央部の輝度が閾値以下なら再キャプチャする。このセーフティチェックを無効化・削除しない。
5. **描画待機**: 画面遷移後は十分な待機時間を確保する（体組成詳細画面は 5〜6 秒）。
6. **カレンダー選択（ストレス）**: `src/calendar_picker.py` の `get_date_coords()` を使用する。**月跨ぎ・年跨ぎのUI操作は現状未対応**（既知リスク）のため注意する。
---

## 6. テスト・検証ルール

- **構文チェック**:
  ```powershell
  python -m py_compile config.py main.py src\*.py
  ```
- **実機レス検証**: `python main.py --skip-adb` で既存スクリーンショットのみ再解析できる。
- **単体確認**: `python main.py --days 1` でパイプライン全体を短時間確認する。
- **座標・UI変更時**: 該当カテゴリの実機動作確認を必ず行い、変更点をコミットメッセージに明記する。

---

## 7. バージョン管理 (Git)

> [!CAUTION]
> **`master`（本番用）ブランチでの直接作業・`origin/master` への直接 Push は厳禁（グローバルルール準拠）**

- **作業ブランチの作成**: 開発・修正は必ず **`staging` ブランチ**、または作業内容に応じた **`feature/xxx`・`fix/xxx` ブランチ** を作成して行う。
- **本番マージ**: `master` へのマージ・`origin/master` への Push は、ユーザーからの明確な承認が得られた場合のみ実行する。
- **コミットメッセージ規約**: `feat:` / `fix:` / `refactor:` / `docs:` / `chore:` プレフィックスを使用する。
- **コミット禁止物**: `.env`・`data/` 配下の生成物（スクリーンショット・JSON・レポート）はコミットしない（`.gitignore` で除外済み。`git add -f` による強制追加は禁止）。
- コミット前に `git status` で追跡対象を必ず確認する。
---

## 8. 機密情報保護（最重要）

- `GEMINI_API_KEY` 等の API キー・パスワード・個人を特定できる情報（`DEVICE_ID` 等）が含まれる（または含まれる可能性がある）内容を、**外部API（MCPサーバー等）へ送信しない**。ローカルのツール実行のみで完結させる。
- API キーをコード中に直書きせず、必ず `.env` 経由で取得する。
- チャット上で API キーの値をやり取りしない。

---

## 9. 会話セッション移行・引き継ぎのルール

AI エージェントのコンテキストメモリの肥大化による誤判断・コード品質低下を防ぐため、以下のタイミングを検知した際、自発的に新しいセッションへの移行を提案し、引き継ぎサマリー（`handover_summary.md`）を作成する。

### 推奨タイミング
1. 【実装】から【ビルド・検証】へのフェーズ移行時
2. 【トラブルシューティング（デバッグ）】完了直後
3. 【設計（プランニング）】から【実装】へのフェーズ移行時
4. 会話の往復（ターン数）が 30〜40 ターンを超えたとき

### AI の行動ガイドライン
- 上記タイミングで自発的に「新しい会話への移行」を提案する。
- 移行承認後、会話ディレクトリ直下に `handover_summary.md` を作成し、次セッションで最初に行うアクションを明記して終了する。
- **新しい会話で即座に貼り付けられるよう、以下の引き継ぎ指示テンプレートを最後に出力する**:

  ```text
  作業前にルートにある DEVELOPMENT_RULES.md を確認してください。
  下記のファイルの内容を読み込んで、指示に従って進めてください。
  file:///C:/Users/toshi/.gemini/antigravity/brain/[Conversation-ID]/handover_summary.md
  ```

---

## 10. バックグラウンドタスク残骸の自動防止・完全同期化ルール

1. **コマンド実行の完全同期化 (`WaitMsBeforeAsync: 10000`)**: PowerShell スクリプト・Git 操作・ファイルコピーを実行する際は、原則として待機ミリ秒数に最大値 `10000` を指定し、バックグラウンド化させず同期完結させる。
2. **作業完了時の自律クリーンアップ**: 一連の作業完了時、残存している一時プロセス（バックグラウンドタスク）があれば完全消去・クリーンアップしてから完了報告を行う。

---

## 11. 既知の制約・リスク

詳細は `REMAINING_TASKS_AND_RISKS.md` を参照。

- **未実装**: `spo2`（血中酸素）の ADB 自動収集（`config.CATEGORIES` には定義済み）
- **リスク**:
  - ストレス取得用カレンダー座標の月跨ぎ・年跨ぎ非対応（`src/calendar_picker.py`）
  - 体組成取得後の画面復帰（固定3回バックキー）の不安定性
  - 体組成画像ペアリング判定条件の曖昧さ（誤マッチリスク）
  - JSON 全件再走査によるレポート生成パフォーマンス低下
