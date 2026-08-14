# 会話引き継ぎサマリー (Handover Summary)

---

## 1. 確立・確定した実績 (Accomplishments & Confirmed Procedures)

### ① 画面ロック解除 & アプリ安定起動（確定済み）
- デバイス: HarmonyOSタブレット (`QBK6R20519000806`, 解像度 `1600x2560`)
- 画面点灯: `input keyevent 224` (KEYCODE_WAKEUP) を使用して画面を安定点灯。
- スリープ防止: ADB `screen_off_timeout` を 30分 (1800000ms) に設定。

### ② 体組成データ（7日以前・過去日）自動取得（確定済み！）
- 慣性なし等速スワイプ: 移動量 `1740 px` (`290 px × 6日分`)、時間 `1500 ms`
- 7日前実測: `X = 800, Y = 410` / 8日前実測: `X = 800, Y = 720`

### ③ 心拍（心機能）データ全自動取得（確定済み！）
- **確定タップ座標**: **`X = 1015, Y = 1248`**
- **キャプチャ仕様**: **縦スクロール不要（1日1枚で全データ完結）**
- **過去日移動**: 詳細画面内で左から右へスワイプ (`input swipe 300 1000 1300 1000 300`)

### ④ ストレス（情緒）データ全自動取得（今回確定！）
- **確定タップ座標**: **`X = 606, Y = 1780`** （ユーザー様のリアルタイムタップ検出により確定）
- **キャプチャ仕様**: **縦スクロール不要（1日1枚で全データ完結）**
- **日付選択・過去日ナビゲーション**:
  - 日付ドロップダウン（`X = 318, Y = 374`）をタップしてカレンダーダイアログを表示。
  - カレンダー上の対象日付（例: 8/13なら `X=971, Y=1863`、8/11なら `X=625, Y=1863`）を直接タップして瞬時に切り替え可能。
- **実績**: 3日前 (2026/08/11) のストレスデータ自動取得テストに完全成功！

---

## 2. 確定スクリプト & 関連ファイル (Files & Code)

- [config.py](file:///c:/KENKOU%20SYUTOKU/config.py): 心機能 (`1015, 1248`) & ストレス (`606, 1780`) 反映済み
- [src/adb_collector.py](file:///c:/KENKOU%20SYUTOKU/src/adb_collector.py): 自動収集コレクターの座標更新済み
- [capture_3days_ago_stress.py](file:///c:/KENKOU%20SYUTOKU/capture_3days_ago_stress.py): 3日前ストレスデータ自動取得スクリプト
- [capture_3days_ago_heart_rate.py](file:///c:/KENKOU%20SYUTOKU/capture_3days_ago_heart_rate.py): 3日前心拍データ自動取得スクリプト
- [capture_heart_rate_days.py](file:///c:/KENKOU%20SYUTOKU/capture_heart_rate_days.py): N日数分心拍データ全自動取得スクリプト
- [capture_7days_and_8days_real_coords.py](file:///c:/KENKOU%20SYUTOKU/capture_7days_and_8days_real_coords.py): 体組成過去データ自動取得決定版

---

## 3. 次のセッションで行う作業 (Next Steps)

- 「血中酸素（SpO2）」や「睡眠」など残りのデータカテゴリの取得手順確立
- または、全自動データ収集メインスクリプト（`main.py`）への全カテゴリ自動取得処理の統合
