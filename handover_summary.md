# 会話引き継ぎサマリー (Handover Summary)

本ドキュメントは、HUAWEIヘルスケアアプリからの4大健康データ（**睡眠・体組成・心機能・ストレス**）の自動取得手順の確立実績と、次のセッションで実施する「4要素一括統合取得スクリプト」の設計・実装方針をまとめたものです。

---

## 1. 確立・確定した4大健康データの取得仕様 (Confirmed Specifications)

| データカテゴリ | トップ画面タップ座標 (X, Y) | 撮影仕様 | 過去日ナビゲーション方式 | 確定スクリプト / モジュール |
| :--- | :--- | :--- | :--- | :--- |
| **① 睡眠 (Sleep)** | `X = 1350, Y = 1150` | 1日1枚 (スクロール不要) | スワイプ方式 (左 ➔ 右: `input swipe 300 1000 1300 1000 300`) | [src/adb_collector.py](file:///c:/KENKOU%20SYUTOKU/src/adb_collector.py) |
| **② 体組成 (Body Comp)** | `X = 200, Y = 1650`<br>➔ 身体計測 `X=800, Y=950`<br>➔ 履歴 `X=1476, Y=159` | 上部・下部 2枚分割撮影<br>(スクロール移動 `Y: 2000->500`) | 履歴リスト等速スワイプ (`1740px, 1500ms`)<br>7日前実測: `X=800, Y=410`<br>8日前実測: `X=800, Y=720` | [capture_7days_and_8days_real_coords.py](file:///c:/KENKOU%20SYUTOKU/capture_7days_and_8days_real_coords.py) |
| **③ 心機能 (Heart Rate)** | `X = 1015, Y = 1248` | 1日1枚 (スクロール不要) | スワイプ方式 (左 ➔ 右: `input swipe 300 1000 1300 1000 300`) | [capture_heart_rate_days.py](file:///c:/KENKOU%20SYUTOKU/capture_heart_rate_days.py) |
| **④ ストレス (Stress)** | `X = 606, Y = 1780` | 1日1枚 (スクロール不要) | カレンダー動的座標計算方式<br>日付ドロップダウン `X=318, Y=374`<br>動的計算: `X(col)=279+col*173`, `Y(row)=1517+row*173` | [src/calendar_picker.py](file:///c:/KENKOU%20SYUTOKU/src/calendar_picker.py)<br>[capture_stress_days.py](file:///c:/KENKOU%20SYUTOKU/capture_stress_days.py) |

---

## 2. 共通のデバイス制御・安定起動仕様 (Device Control)

- **対象デバイス**: HarmonyOSタブレット (`QBK6R20519000806`, 解像度 `1600x2560`)
- **画面点灯**: `input keyevent 224` (KEYCODE_WAKEUP) を使用（画面が消えている場合のみ点灯）
- **ロック解除**: `input swipe 800 2000 800 500 200`
- **スリープ防止**: `settings put system screen_off_timeout 1800000` (30分)
- **クリーン起動**: `am force-stop com.huawei.health` ➔ `monkey -p com.huawei.health -c android.intent.category.LAUNCHER 1` ➔ 5秒待機

---

## 3. 次のセッションで最初に行う作業 (Next Action Plan)

1. **4大カテゴリ（睡眠、体組成、心機能、ストレス）の全自動一括収集メインスクリプトの作成**:
   - `capture_all_health_data.py`（または `main.py` のパイプライン拡張）を実装。
   - コマンドライン引数 `--days N`（例: `--days 7`）で、4カテゴリすべての過去N日分のスクリーンショットを一発で全自動収集・整理保存するフローを構築。
2. **Vision AI（Gemini / DeepSeek）によるOCR・データ構造化抽出パイプラインの動作検証**:
   - 撮影された各カテゴリのスクリーンショットから数値を抽出し、JSONおよび統合レポートを作成する処理の結合テスト。

---

## 4. Gitリポジトリ状態 (Git Status)
- リポジトリ: `https://github.com/gekiren/kenkou-syutoku.git`
- ブランチ: `master`
- 最新コミット: `837591a` (すべてのスクリプト・設定が同期済み)
