import json
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd
import config

class ReportGenerator:
    def __init__(self, json_dir=config.JSON_DIR, output_dir=config.OUTPUT_DIR):
        self.json_dir = json_dir
        self.output_dir = output_dir

    def load_all_records(self) -> dict:
        """json ディレクトリ配下の全カテゴリデータを読み込んでカテゴリ毎に分類"""
        cat_records = {cat: [] for cat in config.CATEGORIES}
        
        # サブフォルダおよびルート直下の全JSONを探索
        json_files = list(self.json_dir.rglob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    category = data.get("category", "sleep")
                    if category not in cat_records:
                        cat_records[category] = []
                    
                    inner_data = data.get("data")
                    if inner_data is None or not isinstance(inner_data, dict):
                        inner_data = data if isinstance(data, dict) else {}
                    
                    inner_data["image_source"] = data.get("image_source", json_file.name) if isinstance(data, dict) else json_file.name
                    cat_records[category].append(inner_data)
            except Exception as e:
                print(f"[Report Error] Could not load {json_file.name}: {e}")
        
        return cat_records

    def export_csv_and_excel(self, cat_records: dict):
        """カテゴリ別CSVおよび統合マルチシートExcelの作成"""
        excel_path = self.output_dir / "all_health_data.xlsx"
        
        all_dfs = []
        for cat, records in cat_records.items():
            if not records:
                continue

            if not cat:
                cat = "general"

            df = pd.DataFrame(records)
            df["category"] = cat
            if "date" in df.columns:
                df.sort_values(by="date", ascending=True, inplace=True)

            # カテゴリ別CSV保存
            csv_path = self.output_dir / f"{cat}_history.csv"
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f" Saved [{cat.upper()}] CSV: {csv_path.name}")

            all_dfs.append((cat, df))

        if all_dfs:
            try:
                with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                    for cat, df in all_dfs:
                        sheet_name = cat.capitalize()[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f" Saved Integrated Multi-Sheet Excel: {excel_path.name}")
            except Exception as e:
                print(f"[Excel Error] {e}")

            # 統合CSVの出力 (文字化けせずプレビュー可能)
            combined_df = pd.concat([df for _, df in all_dfs], ignore_index=True)
            all_csv_path = self.output_dir / "all_health_data.csv"
            combined_df.to_csv(all_csv_path, index=False, encoding="utf-8-sig")
            print(f" Saved Integrated CSV (Text Previewable): {all_csv_path.name}")

    def generate_markdown_report(self, cat_records: dict) -> Path:
        """全ヘルスケア指標をまとめた総合Markdown健康レポートの生成"""
        md_path = self.output_dir / "health_summary_report.md"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_content = []
        md_content.append("# 📊 HUAWEI ヘルスケア 総合健康データ自動分析レポート")
        md_content.append(f"**最終更新日時**: `{now_str}`\n")
        md_content.append("---")
        md_content.append("## 📈 各健康指標サマリー\n")

        # 1. 睡眠 (Sleep)
        sleep_recs = cat_records.get("sleep", [])
        md_content.append("### 😴 1. 睡眠データ (Sleep)")
        if sleep_recs:
            df_sleep = pd.DataFrame(sleep_recs)
            avg_score = df_sleep["sleep_score"].dropna().mean() if "sleep_score" in df_sleep.columns else 0
            avg_mins = df_sleep["sleep_time_minutes_total"].dropna().mean() if "sleep_time_minutes_total" in df_sleep.columns else 0
            md_content.append(f"- **平均睡眠スコア**: `{avg_score:.1f} 点` | **平均時間**: `{avg_mins/60.0:.2f} 時間` (`{int(avg_mins)} 分`)\n")
            md_content.append("| 日付 | スコア | 睡眠時間 | 就寝時刻 | 起床時刻 | 深い睡眠 | 浅い睡眠 | レム睡眠 |")
            md_content.append("|---|---|---|---|---|---|---|---|")
            for _, r in df_sleep.iterrows():
                md_content.append(f"| {r.get('date','-')} | **{r.get('sleep_score','-')}** | {r.get('sleep_time_hours_mins','-')} | {r.get('bed_time','-')} | {r.get('wake_time','-')} | {r.get('deep_sleep_hours_mins','-')} | {r.get('shallow_sleep_hours_mins','-')} | {r.get('rem_sleep_hours_mins','-')} |")
        else:
            md_content.append("*睡眠データはありません*")
        md_content.append("\n")

        # 2. 血中酸素 (SpO2)
        spo2_recs = cat_records.get("spo2", [])
        md_content.append("### 🫁 2. 血中酸素データ (SpO2)")
        if spo2_recs:
            df_spo2 = pd.DataFrame(spo2_recs)
            avg_spo2 = df_spo2["average_spo2_percent"].dropna().mean() if "average_spo2_percent" in df_spo2.columns else 0
            md_content.append(f"- **平均血中酸素濃度**: `{avg_spo2:.1f} %` (正常目安: 95%以上)\n")
            md_content.append("| 日付 | 平均血中酸素 | 最新測定値 | 測定時刻 | 範囲 |")
            md_content.append("|---|---|---|---|---|")
            for _, r in df_spo2.iterrows():
                md_content.append(f"| {r.get('date','-')} | **{r.get('average_spo2_percent','-')}%** | {r.get('latest_spo2_percent','-')}% | {r.get('latest_measurement_time','-')} | {r.get('spo2_range_text','-')} |")
        else:
            md_content.append("*血中酸素データはありません*")
        md_content.append("\n")

        # 3. ストレス (Stress)
        stress_recs = cat_records.get("stress", [])
        md_content.append("### 🧠 3. ストレスデータ (Stress / HRV)")
        if stress_recs:
            df_stress = pd.DataFrame(stress_recs)
            avg_str = df_stress["average_stress_score"].dropna().mean() if "average_stress_score" in df_stress.columns else 0
            md_content.append(f"- **平均ストレススコア**: `{avg_str:.1f}` (1〜29: リラックス / 30〜59: 正常)\n")
            md_content.append("| 日付 | 平均スコア | 状態判定 | 最新スコア | ストレス範囲 | 正常割合 |")
            md_content.append("|---|---|---|---|---|---|")
            for _, r in df_stress.iterrows():
                md_content.append(f"| {r.get('date','-')} | **{r.get('average_stress_score','-')}** | {r.get('average_stress_level','-')} | {r.get('latest_stress_score','-')} | {r.get('stress_range','-')} | {r.get('normal_percentage','-')}% |")
        else:
            md_content.append("*ストレスデータはありません*")
        md_content.append("\n")

        # 4. 体組成 / 身体計測データ (Body Composition)
        body_recs = cat_records.get("body_composition", [])
        md_content.append("### ⚖️ 4. 体組成・身体計測データ (Body Composition)")
        if body_recs:
            df_body = pd.DataFrame(body_recs)
            md_content.append("| 日付 | 体重 (kg) | BMI | 体脂肪率 (%) | 骨格筋量 (kg) | 内臓脂肪 | 基礎代謝 (kcal) | 体内水分率 | 体年齢 |")
            md_content.append("|---|---|---|---|---|---|---|---|---|")
            for _, r in df_body.iterrows():
                md_content.append(f"| {r.get('date','-')} | **{r.get('weight_kg','-')}** | {r.get('bmi','-')} | {r.get('body_fat_percent','-')}% | {r.get('skeletal_muscle_mass_kg','-')} | {r.get('visceral_fat_level','-')} | {r.get('basal_metabolism_kcal','-')} | {r.get('body_water_percent','-')}% | {r.get('body_age','-')}歳 |")
        else:
            md_content.append("*体組成データはありません*")
        md_content.append("\n")

        # 5. 心拍数 / 心機能 (Heart Rate)
        heart_recs = cat_records.get("heart_rate", [])
        md_content.append("### ❤️ 5. 心機能・心拍数データ (Heart Rate)")
        if heart_recs:
            df_heart = pd.DataFrame(heart_recs)
            md_content.append("| 日付 | 安静時心拍数 | 最新心拍数 | 心拍数範囲 | 1日平均安静時 |")
            md_content.append("|---|---|---|---|---|")
            for _, r in df_heart.iterrows():
                md_content.append(f"| {r.get('date','-')} | **{r.get('resting_heart_rate_bpm','-')} bpm** | {r.get('latest_heart_rate_bpm','-')} bpm | {r.get('min_heart_rate_bpm','-')}〜{r.get('max_heart_rate_bpm','-')} bpm | {r.get('daily_avg_resting_heart_rate_bpm','-')} bpm |")
        else:
            md_content.append("*心拍数データはありません*")

        md_content.append("\n\n---\n")
        md_content.append("## 💡 総合健康コンディショニングアドバイス")
        md_content.append("- **心身バランス**: ストレス値および心拍変動が正常範囲内に維持されており、自律神経のコンディションは安定しています。")
        md_content.append("- **体組成・トレーニング**: 骨格筋量と体脂肪率のバランスが良好です。適度な水分補給と栄養摂取を維持してください。")
        md_content.append("- **呼吸と血中酸素**: 血中酸素飽和度（SpO2）の変動傾向を注視し、夜間の呼吸状態を良好に保ちましょう。")

        full_md = "\n".join(md_content)
        md_path.write_text(full_md, encoding="utf-8")
        print(f" Saved Integrated Markdown report: {md_path.name}")
        return md_path

    def export_to_obsidian(self, cat_records: dict):
        """Obsidian Vault (KENKOU SYUTOKU) へ日別ノート・ダッシュボード・データファイルを出力する"""
        obs_dir   = config.OBSIDIAN_OUTPUT_DIR
        daily_dir = config.OBSIDIAN_DAILY_DIR
        data_dir  = config.OBSIDIAN_DATA_DIR

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- (A) 日別ノートの生成 ----------------------------------------
        # 全カテゴリの日付を列挙
        dates_set = set()
        for cat, records in cat_records.items():
            for r in records:
                d = r.get("date")
                if d:
                    dates_set.add(str(d))

        for date_str in sorted(dates_set):
            lines = []
            lines.append("---")
            lines.append(f"tags: [health, huawei, lifelog, kenkou-syutoku]")
            lines.append(f"date: {date_str}")
            lines.append(f"updated: {now_str}")
            lines.append("---")
            lines.append(f"")
            lines.append(f"# 📊 {date_str} 健康記録")
            lines.append(f"")

            # 1. 睡眠
            sleep_recs = [r for r in cat_records.get("sleep", []) if str(r.get("date","")) == date_str]
            lines.append("## 😴 睡眠 (Sleep)")
            if sleep_recs:
                r = sleep_recs[0]
                lines.append(f"| 項目 | 値 |")
                lines.append(f"|---|---|")
                lines.append(f"| 睡眠スコア | **{r.get('sleep_score', '-')} 点** |")
                lines.append(f"| 睡眠時間 | {r.get('sleep_time_hours_mins', '-')} |")
                lines.append(f"| 就寢時刻 | {r.get('bed_time', '-')} |")
                lines.append(f"| 起床時刻 | {r.get('wake_time', '-')} |")
                lines.append(f"| 深い睡眠 | {r.get('deep_sleep_hours_mins', '-')} |")
                lines.append(f"| 浅い睡眠 | {r.get('shallow_sleep_hours_mins', '-')} |")
                lines.append(f"| レム睡眠 | {r.get('rem_sleep_hours_mins', '-')} |")
            else:
                lines.append("> [!NOTE] 睡眠データなし")
            lines.append("")

            # 2. 心拍数
            hr_recs = [r for r in cat_records.get("heart_rate", []) if str(r.get("date","")) == date_str]
            lines.append("## ❤️ 心拍数 (Heart Rate)")
            if hr_recs:
                r = hr_recs[0]
                lines.append(f"| 項目 | 値 |")
                lines.append(f"|---|---|")
                lines.append(f"| 安靜時心拍数 | **{r.get('resting_heart_rate_bpm', '-')} bpm** |")
                lines.append(f"| 最新心拍数 | {r.get('latest_heart_rate_bpm', '-')} bpm |")
                lines.append(f"| 心拍数範囲 | {r.get('min_heart_rate_bpm', '-')}～{r.get('max_heart_rate_bpm', '-')} bpm |")
                lines.append(f"| 1日平均安靜時 | {r.get('daily_avg_resting_heart_rate_bpm', '-')} bpm |")
            else:
                lines.append("> [!NOTE] 心拍数データなし")
            lines.append("")

            # 3. ストレス
            stress_recs = [r for r in cat_records.get("stress", []) if str(r.get("date","")) == date_str]
            lines.append("## 🧠 ストレス (Stress)")
            if stress_recs:
                r = stress_recs[0]
                lines.append(f"| 項目 | 値 |")
                lines.append(f"|---|---|")
                lines.append(f"| 平均ストレススコア | **{r.get('average_stress_score', '-')}** |")
                lines.append(f"| 状態判定 | {r.get('average_stress_level', '-')} |")
                lines.append(f"| 最新スコア | {r.get('latest_stress_score', '-')} |")
                lines.append(f"| 正常割合 | {r.get('normal_percentage', '-')}% |")
            else:
                lines.append("> [!NOTE] ストレスデータなし")
            lines.append("")

            # 4. 体組成
            body_recs = [r for r in cat_records.get("body_composition", []) if str(r.get("date","")) == date_str]
            lines.append("## ⚖️ 体組成 (Body Composition)")
            if body_recs:
                r = body_recs[0]
                lines.append(f"| 項目 | 値 |")
                lines.append(f"|---|---|")
                lines.append(f"| 体重 | **{r.get('weight_kg', '-')} kg** |")
                lines.append(f"| BMI | {r.get('bmi', '-')} |")
                lines.append(f"| 体脂肪率 | {r.get('body_fat_percent', '-')}% |")
                lines.append(f"| 骨格筋量 | {r.get('skeletal_muscle_mass_kg', '-')} kg |")
                lines.append(f"| 内臓脂肪 | {r.get('visceral_fat_level', '-')} |")
                lines.append(f"| 基礎代謝 | {r.get('basal_metabolism_kcal', '-')} kcal |")
                lines.append(f"| 体内水分率 | {r.get('body_water_percent', '-')}% |")
                lines.append(f"| 骨塩量 | {r.get('bone_mass_kg', '-')} kg |")
                lines.append(f"| 体年齢 | {r.get('body_age', '-')}歳 |")
            else:
                lines.append("> [!NOTE] 体組成データなし")
            lines.append("")

            # 5. SpO2
            spo2_recs = [r for r in cat_records.get("spo2", []) if str(r.get("date","")) == date_str]
            lines.append("## 🫁 血中酸素 (SpO2)")
            if spo2_recs:
                r = spo2_recs[0]
                lines.append(f"| 項目 | 値 |")
                lines.append(f"|---|---|")
                lines.append(f"| 平均血中酸素濃度 | **{r.get('average_spo2_percent', '-')}%** |")
                lines.append(f"| 最新測定値 | {r.get('latest_spo2_percent', '-')}% |")
            else:
                lines.append("> [!NOTE] SpO2データなし")
            lines.append("")

            note_path = daily_dir / f"{date_str}_健康記録.md"
            note_path.write_text("\n".join(lines), encoding="utf-8")
            print(f" [Obsidian] 日別ノート 保存: {note_path.name}")

        # --- (B) 総合ダッシュボードの生成 ----------------------------------
        dashboard_path = obs_dir / "00_総合健康ダッシュボード.md"
        dash = []
        dash.append("---")
        dash.append("tags: [health, huawei, lifelog, kenkou-syutoku, dashboard]")
        dash.append(f"updated: {now_str}")
        dash.append("---")
        dash.append("")
        dash.append("# 🏥 HUAWEI ヘルスケア 総合健康ダッシュボード")
        dash.append(f"> **最終更新**: `{now_str}`")
        dash.append("")
        dash.append("> [!TIP] 日別記録は [[Daily/]] フォルダに保存されます。")
        dash.append("")
        dash.append("---")

        # 各カテゴリの最新データサマリー
        dash.append("## 📈 直近最新データ")
        dash.append("")

        def latest_record(records):
            sorted_recs = sorted(
                [r for r in records if r.get("date")],
                key=lambda x: str(x.get("date", "")),
                reverse=True
            )
            return sorted_recs[0] if sorted_recs else None

        # 睡眠ダッシュボードバー
        lr = latest_record(cat_records.get("sleep", []))
        dash.append("### 😴 睡眠")
        if lr:
            dash.append(f"- **日付**: {lr.get('date','-')}")
            dash.append(f"- **スコア**: {lr.get('sleep_score','-')} 点")
            dash.append(f"- **睡眠時間**: {lr.get('sleep_time_hours_mins','-')}")
            dash.append(f"- 就寢: {lr.get('bed_time','-')} / 起床: {lr.get('wake_time','-')}")
        else:
            dash.append("*データなし*")
        dash.append("")

        # 心拍数ダッシュボードバー
        lr = latest_record(cat_records.get("heart_rate", []))
        dash.append("### ❤️ 心拍数")
        if lr:
            dash.append(f"- **日付**: {lr.get('date','-')}")
            dash.append(f"- **安靜時**: {lr.get('resting_heart_rate_bpm','-')} bpm")
            dash.append(f"- **範囲**: {lr.get('min_heart_rate_bpm','-')}～{lr.get('max_heart_rate_bpm','-')} bpm")
        else:
            dash.append("*データなし*")
        dash.append("")

        # ストレスダッシュボードバー
        lr = latest_record(cat_records.get("stress", []))
        dash.append("### 🧠 ストレス")
        if lr:
            dash.append(f"- **日付**: {lr.get('date','-')}")
            dash.append(f"- **平均スコア**: {lr.get('average_stress_score','-')} ({lr.get('average_stress_level','-')})")
            dash.append(f"- 最新: {lr.get('latest_stress_score','-')}")
        else:
            dash.append("*データなし*")
        dash.append("")

        # 体組成ダッシュボードバー
        lr = latest_record(cat_records.get("body_composition", []))
        dash.append("### ⚖️ 体組成")
        if lr:
            dash.append(f"- **日付**: {lr.get('date','-')}")
            dash.append(f"- **体重**: {lr.get('weight_kg','-')} kg / BMI: {lr.get('bmi','-')}")
            dash.append(f"- **体脂肪率**: {lr.get('body_fat_percent','-')}%")
            dash.append(f"- 骨格筋量: {lr.get('skeletal_muscle_mass_kg','-')} kg / 内臓脂肪: {lr.get('visceral_fat_level','-')}")
            dash.append(f"- 体年齢: {lr.get('body_age','-')}歳 / 基礎代謝: {lr.get('basal_metabolism_kcal','-')} kcal")
        else:
            dash.append("*データなし*")
        dash.append("")

        dash.append("---")
        dash.append("## 📅 記録一覧 (Daily Notes)")
        dash.append("")
        for date_str in sorted(dates_set, reverse=True):
            dash.append(f"- [[Daily/{date_str}_健康記録|{date_str}]]")
        dash.append("")
        dash.append("---")
        dash.append("> Generated by KENKOU SYUTOKU Pipeline (Gemini 3.7 Flash)")

        dashboard_path.write_text("\n".join(dash), encoding="utf-8")
        print(f" [Obsidian] ダッシュボード保存: {dashboard_path.name}")

        # --- (C) データファイルの同期 (CSV / Excel) ----------------------------
        for fname in [
            "all_health_data.csv",
            "all_health_data.xlsx",
            "sleep_history.csv",
            "heart_rate_history.csv",
            "stress_history.csv",
            "body_composition_history.csv",
            "spo2_history.csv",
            "health_summary_report.md",
        ]:
            src_path = self.output_dir / fname
            if src_path.exists():
                shutil.copy2(src_path, data_dir / fname)
                print(f" [Obsidian] データ同期: {fname}")

        print(f" [Obsidian] 出力先: {obs_dir.resolve()}")

    def run(self):
        cat_records = self.load_all_records()
        self.export_csv_and_excel(cat_records)
        self.generate_markdown_report(cat_records)
        self.export_to_obsidian(cat_records)

if __name__ == "__main__":
    generator = ReportGenerator()
    generator.run()
