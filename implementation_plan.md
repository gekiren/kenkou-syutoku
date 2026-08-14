# 🛠️ 実装計画 / 実施記録: DEVELOPMENT_RULES.md の本プロジェクト向け最適化

## 1. タスク概要

- **依頼**: 「DEVELOPMENT_RULES.md の内容を本プロジェクトに合わせて最適化」
- **対象**: `c:\KENKOU SYUTOKU\DEVELOPMENT_RULES.md`
- **実施日**: 2026-08-14
- **作業ブランチ**: `staging`（グローバルルールのブランチ管理に準拠。`master` 直作業・`origin/master` 直 Push は実施しない）

## 2. 事前調査結果

本プロジェクトの実体は以下であることを確認:

- **KENKOU SYUTOKU = HUAWEI Health アプリの ADB 自動操作 × Gemini Vision AI 解析による健康データ自動収集パイプライン（Python製）**
- 技術スタック: Python 3.14 / venv / google-genai / Pillow / pandas / openpyxl / python-dotenv / ADB（実機 1600x2560）
- 取得カテゴリ: `sleep` / `heart_rate` / `stress` / `body_composition` / `spo2`（未実装）
- パイプライン: ADBキャプチャ → Vision AI解析 → レポート生成・Obsidian同期
- Git: `gekiren/kenkou-syutoku`（従来は master 直運用）

一方、旧 `DEVELOPMENT_RULES.md`（336行）は他プロジェクト（gym-tracker / MEISI / ULANZI）のルールが大半を占めており、本プロジェクトには不整合な状態だった。

## 3. 最適化方針

| 方針 | 対象 |
| :--- | :--- |
| 削除 | Expo/React Native（EAS Build / EAS Update / OTA / AsyncStorage / SQLite / Zustand / 広告）、ULANZI プラグイン、C:\TreNote 絶対パス等の他プロジェクト固有セクション |
| 残す | 会話セッション引き継ぎルール、バックグラウンドタスク残骸防止ルール（本PJ向けに再構成） |
| 新規追加 | プロジェクト概要 / venv・requirements 規約 / .env・絶対パス禁止 / config.py 一元管理 / ファイル命名規則・データディレクトリ構造 / Gemini モデルフォールバックチェーン / ADB 実機操作の鉄則 / テスト・検証手順 / 機密情報保護 / 既知リスク参照 |

## 4. 新ドキュメント構成（12セクション）

0. プロジェクト概要
1. 環境構築・実行ルール
2. 設定管理 (config.py)
3. アーキテクチャと実装規約
4. Gemini Vision AI 仕様（データ抽出）
5. ADB 実機操作の鉄則
6. テスト・検証ルール
7. バージョン管理 (Git) ※ staging / feature・fix ブランチ運用
8. 機密情報保護（最重要）
9. 会話セッション移行・引き継ぎのルール
10. バックグラウンドタスク残骸の自動防止・完全同期化ルール
11. 既知の制約・リスク

## 5. 実施・検証結果

- [x] `staging` ブランチを作成
- [x] `DEVELOPMENT_RULES.md` を全面書き換え（185行・全12セクション）
- [x] セクション順序を検証（Select-String で見出し順序確認）
- [x] UTF-8 BOM を除去（`#` から開始することを確認）
- [x] 旧版の復元可能性: Git 履歴に残存
- [x] `staging` ブランチにローカルコミット（`origin/master` への Push は未実施）
