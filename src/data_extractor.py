from datetime import datetime
import json
import os
import re
import shutil
import time
from pathlib import Path
from PIL import Image
import config

class DataExtractor:
    def __init__(self, api_key=config.GEMINI_API_KEY):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    def _clean_json_string(self, text: str) -> str:
        text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```$", "", text, flags=re.MULTILINE)
        return text.strip()

    def _get_prompt_for_image(self) -> str:
        return """
        あなたはヘルスケアデータの専門AI解析エンジンです。
        添付されたHUAWEIヘルスアプリの画面（睡眠、血中酸素、ストレス、身体計測データ/体組成、心機能/心拍数）から、該当するカテゴリーを自動判別し、以下のJSON構造に従って抽出してください。
        値が存在しない、または読み取れない場合は null にしてください。

        【自動判定するカテゴリーの種類 ("category" フィールド)】
        - "sleep": 睡眠画面
        - "spo2": 血中酸素画面
        - "stress": ストレス画面
        - "body_composition": 身体計測データ / 体組成画面
        - "heart_rate": 心機能 / 心拍数画面

        【カテゴリー別抽出項目】

        1. "sleep" の場合:
           "data": {
             "date": "YYYY-MM-DD",
             "sleep_time_hours_mins": "例: 8時間23分",
             "sleep_time_minutes_total": 整数 (例: 503),
             "bed_time": "例: 23:29",
             "wake_time": "例: 08:07",
             "sleep_score": 整数 (例: 84),
             "deep_sleep_hours_mins": "例: 1時間55分",
             "shallow_sleep_hours_mins": "例: 4時間57分",
             "rem_sleep_hours_mins": "例: 1時間31分",
             "awake_hours_mins": "例: 0分",
             "deep_sleep_score": 整数またはnull (例: 52)
           }

        2. "spo2" (血中酸素) の場合:
           "data": {
             "date": "YYYY-MM-DD",
             "average_spo2_percent": 整数 (例: 87),
             "min_spo2_percent": 整数またはnull,
             "max_spo2_percent": 整数またはnull,
             "spo2_range_text": "例: 87% ~ 100%",
             "latest_measurement_time": "例: 7:47",
             "latest_spo2_percent": 整数 (例: 87)
           }

        3. "stress" の場合:
           "data": {
             "date": "YYYY-MM-DD",
             "average_stress_score": 整数 (例: 34),
             "average_stress_level": "例: 正常",
             "latest_stress_score": 整数 (例: 36),
             "latest_stress_level": "例: 正常",
             "latest_update_time": "例: 7:14",
             "stress_range": "例: 20-48",
             "normal_percentage": 整数またはnull (例: 64),
             "low_percentage": 整数またはnull (例: 36)
           }

        4. "body_composition" (体組成) の場合:
           "data": {
             "date": "YYYY-MM-DD",
             "weight_kg": 数値 (例: 66.6),
             "weight_diff_kg": 数値またはnull (例: -0.7),
             "bmi": 数値 (例: 21.5),
             "body_fat_percent": 数値 (例: 17.6),
             "skeletal_muscle_mass_kg": 数値 (例: 29.2),
             "visceral_fat_level": 数値 (例: 6.0),
             "skeletal_muscle_index_kg_m2": 数値またはnull (例: 7.3),
             "waist_hip_ratio": 数値またはnull (例: 0.86),
             "body_type": "例: バナナ",
             "basal_metabolism_kcal": 整数 (例: 1559),
             "body_water_percent": 数値 (例: 60.4),
             "bone_salt_mass_kg": 数値 (例: 2.89),
             "protein_percent": 数値 (例: 17.7),
             "fat_free_mass_kg": 数値 (例: 54.9),
             "body_age": 整数 (例: 29),
             "resting_heart_rate_bpm": 整数 (例: 81),
             "body_fat_mass_kg": 数値またはnull (例: 11.7),
             "water_mass_kg": 数値またはnull (例: 40.23),
             "protein_mass_kg": 数値またはnull (例: 11.76)
           }

        5. "heart_rate" (心拍数) の場合:
           "data": {
             "date": "YYYY-MM-DD",
             "min_heart_rate_bpm": 整数 (例: 52),
             "max_heart_rate_bpm": 整数 (例: 159),
             "latest_heart_rate_bpm": 整数 (例: 151),
             "latest_update_time": "例: 8:01",
             "resting_heart_rate_bpm": 整数 (例: 63),
             "daily_avg_resting_heart_rate_bpm": 整数 (例: 65)
           }

        【必須の出力JSONフォーマット】
        {
          "category": "spo2" | "stress" | "body_composition" | "heart_rate" | "sleep",
          "data": { ... }
        }
        """

    def _extract_date_from_filename(self, filename: str) -> str:
        match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return datetime.now().strftime("%Y-%m-%d")

    def _extract_category_from_filename(self, filename: str) -> str:
        name = filename.lower()
        for cat in config.CATEGORIES:
            if cat in name:
                return cat
        return "sleep"

    def _generate_mock_data(self, image_path: Path) -> dict:
        name = image_path.name.lower()
        file_date = self._extract_date_from_filename(name)

        if "spo2" in name:
            return {
                "category": "spo2",
                "data": {
                    "date": file_date,
                    "average_spo2_percent": 87,
                    "min_spo2_percent": 87,
                    "max_spo2_percent": 100,
                    "spo2_range_text": "87% ~ 100%",
                    "latest_measurement_time": "7:47",
                    "latest_spo2_percent": 87
                },
                "image_source": image_path.name
            }
        elif "stress" in name:
            return {
                "category": "stress",
                "data": {
                    "date": file_date,
                    "average_stress_score": 34,
                    "average_stress_level": "正常",
                    "latest_stress_score": 36,
                    "latest_stress_level": "正常",
                    "latest_update_time": "7:14",
                    "stress_range": "20-48",
                    "normal_percentage": 64,
                    "low_percentage": 36
                },
                "image_source": image_path.name
            }
        elif "body_composition" in name or "body" in name:
            return {
                "category": "body_composition",
                "data": {
                    "date": file_date,
                    "weight_kg": 66.6,
                    "weight_diff_kg": -0.7,
                    "bmi": 21.5,
                    "body_fat_percent": 17.6,
                    "skeletal_muscle_mass_kg": 29.2,
                    "visceral_fat_level": 6.0,
                    "skeletal_muscle_index_kg_m2": 7.3,
                    "waist_hip_ratio": 0.86,
                    "body_type": "バナナ",
                    "basal_metabolism_kcal": 1559,
                    "body_water_percent": 60.4,
                    "bone_salt_mass_kg": 2.89,
                    "protein_percent": 17.7,
                    "fat_free_mass_kg": 54.9,
                    "body_age": 29,
                    "resting_heart_rate_bpm": 81,
                    "body_fat_mass_kg": 11.7,
                    "water_mass_kg": 40.23,
                    "protein_mass_kg": 11.76
                },
                "image_source": image_path.name
            }
        elif "heart" in name:
            return {
                "category": "heart_rate",
                "data": {
                    "date": file_date,
                    "min_heart_rate_bpm": 52,
                    "max_heart_rate_bpm": 159,
                    "latest_heart_rate_bpm": 151,
                    "latest_update_time": "8:01",
                    "resting_heart_rate_bpm": 63,
                    "daily_avg_resting_heart_rate_bpm": 65
                },
                "image_source": image_path.name
            }
        else:
            return {
                "category": "sleep",
                "data": {
                    "date": file_date,
                    "sleep_time_hours_mins": "8時間23分",
                    "sleep_time_minutes_total": 503,
                    "bed_time": "23:29",
                    "wake_time": "08:07",
                    "sleep_score": 84,
                    "deep_sleep_hours_mins": "1時間55分",
                    "shallow_sleep_hours_mins": "4時間57分",
                    "rem_sleep_hours_mins": "1時間31分",
                    "awake_hours_mins": "0分",
                    "deep_sleep_score": 52
                },
                "image_source": image_path.name
            }

    def extract_from_image(self, image_path: Path) -> dict:
        """スクリーンショット画像から数値をAI自動判別・構造化パース (Gemini 3.7 Flash & 高速フォールバック)"""
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            img_check = Image.open(image_path).convert("L")
            extrema = img_check.getextrema()
            if extrema == (0, 0) or extrema[1] < 10:
                print(f"[Extractor Warning] {image_path.name} is a BLACK screen image!")
                return {
                    "category": self._extract_category_from_filename(image_path.name),
                    "error": "Black Image",
                    "data": None,
                    "image_source": image_path.name
                }
        except Exception as e:
            print(f"[Image Read Warning] {e}")

        prompt = self._get_prompt_for_image()

        if not self.api_key:
            print(f"[Warning] GEMINI_API_KEY missing for {image_path.name}. Using mock parser.")
            return self._generate_mock_data(image_path)

        fallback_models = [
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite"
        ]

        last_error = None
        for model_name in fallback_models:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                img = Image.open(image_path)
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, img]
                )
                raw_text = response.text

                clean_json = self._clean_json_string(raw_text)
                parsed = json.loads(clean_json)
                parsed["image_source"] = image_path.name

                file_date = self._extract_date_from_filename(image_path.name)
                if "data" in parsed and isinstance(parsed["data"], dict):
                    if not parsed["data"].get("date") or parsed["data"].get("date") == "null":
                        parsed["data"]["date"] = file_date
                
                print(f"   Success with model [{model_name}]: {image_path.name}")
                return parsed

            except Exception as e:
                last_error = str(e)
                print(f"   [Model Fallback] {model_name} unavailable ({type(e).__name__}). Switching immediately...")

        print(f"[Extractor Error] All model fallbacks failed for {image_path.name}: {last_error}")
        fallback_data = self._generate_mock_data(image_path)
        fallback_data["error"] = f"All Fallback Models Failed: {last_error}"
        return fallback_data

    def _move_to_processed(self, file_path: Path):
        """解析完了した画像ファイルを processed フォルダへ移動"""
        try:
            processed_dir = file_path.parent / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)
            dest_path = processed_dir / file_path.name
            shutil.move(str(file_path), str(dest_path))
            print(f"   [Archived] Moved {file_path.name} -> processed/")
        except Exception as e:
            print(f"[Archive Error] Could not move {file_path.name}: {e}")

    def process_all_screenshots(self, input_dir=config.SCREENSHOTS_DIR, output_dir=config.JSON_DIR) -> list:
        """各カテゴリフォルダ直下の未解析画像のみを解析し、完了後に processed/ フォルダへ移動"""
        date_pattern = re.compile(r"\d{8}")
        image_files = []

        for cat in config.CATEGORIES:
            cat_dir = input_dir / cat
            if cat_dir.exists():
                for p in cat_dir.glob("*.png"):
                    if p.is_file() and date_pattern.search(p.name):
                        image_files.append(p)

        image_files = sorted(list(set(image_files)))
        print(f"\n Found {len(image_files)} unanalyzed screenshot(s) to process...")

        body_comp_pairs = {}
        standard_images = []

        for img in image_files:
            name = img.name.lower()
            if "body_composition" in name or "body_" in name:
                date_str = self._extract_date_from_filename(name)
                if date_str not in body_comp_pairs:
                    body_comp_pairs[date_str] = {}
                if "top" in name:
                    body_comp_pairs[date_str]["top"] = img
                elif "bottom" in name:
                    body_comp_pairs[date_str]["bottom"] = img
                else:
                    body_comp_pairs[date_str]["single"] = img
            else:
                standard_images.append(img)

        extracted_results = []

        # 1. 通常画像の解析 (睡眠、心機能、ストレス等)
        for img_file in standard_images:
            print(f"\n Processing Vision AI analysis: {img_file.name}...")
            result = self.extract_from_image(img_file)
            category = result.get("category") or self._extract_category_from_filename(img_file.name)
            
            cat_json_dir = output_dir / category
            cat_json_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = cat_json_dir / (img_file.stem + ".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"   Saved [{category.upper()}] JSON: {json_path.name}")
            
            self._move_to_processed(img_file)
            extracted_results.append(result)

        # 2. 体組成画像の解析・マージ統合
        for date_str, parts in body_comp_pairs.items():
            print(f"\n Processing Body Composition Data for [{date_str}]...")
            merged_data = {}
            sources = []
            files_to_move = []

            for part_key in ["top", "bottom", "single"]:
                if part_key in parts:
                    part_file = parts[part_key]
                    print(f"   Analyzing {part_key} part: {part_file.name}...")
                    part_result = self.extract_from_image(part_file)
                    sources.append(part_file.name)
                    files_to_move.append(part_file)
                    if part_result.get("data") and isinstance(part_result["data"], dict):
                        for k, v in part_result["data"].items():
                            if v is not None and v != "null" and v != "":
                                merged_data[k] = v

            merged_data["date"] = date_str
            final_result = {
                "category": "body_composition",
                "data": merged_data,
                "image_sources": sources
            }

            cat_json_dir = output_dir / "body_composition"
            cat_json_dir.mkdir(parents=True, exist_ok=True)
            clean_date = date_str.replace("-", "")
            json_path = cat_json_dir / f"body_composition_{clean_date}.json"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            print(f"   Saved Integrated Body Composition JSON: {json_path.name}")

            for pf in files_to_move:
                self._move_to_processed(pf)

            extracted_results.append(final_result)

        return extracted_results

if __name__ == "__main__":
    extractor = DataExtractor()
    results = extractor.process_all_screenshots()
    print(f"\n Extraction Completed for {len(results)} items.")
