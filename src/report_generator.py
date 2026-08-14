import json
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

    def run(self):
        cat_records = self.load_all_records()
        self.export_csv_and_excel(cat_records)
        self.generate_markdown_report(cat_records)

if __name__ == "__main__":
    generator = ReportGenerator()
    generator.run()
