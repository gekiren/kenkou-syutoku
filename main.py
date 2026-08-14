import argparse
import sys
from pathlib import Path
import config
from src.adb_collector import ADBCollector
from src.data_extractor import DataExtractor
from src.report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="HUAWEI Health App Multi-Category Auto Collector & Reporter")
    parser.add_argument("--days", type=int, default=config.DEFAULT_CAPTURE_DAYS, help="Number of days to capture (default: 7)")
    parser.add_argument("--category", type=str, default="all", choices=config.CATEGORIES + ["all"], help="Category to process (sleep, heart_rate, stress, body_composition, spo2, all)")
    parser.add_argument("--skip-adb", action="store_true", help="Skip ADB capture step and process existing screenshots")
    parser.add_argument("--skip-extract", action="store_true", help="Skip Vision AI extraction step and regenerate report")
    args = parser.parse_args()

    print("==================================================")
    print(" HUAWEI Health App Multi-Category Auto System")
    print("==================================================")

    # Step 1: ADB Capture
    if not args.skip_adb:
        print(f"\n--- Step 1: ADB Screen Auto Capture ({args.days} days) ---")
        collector = ADBCollector()
        try:
            if args.category == "all":
                collector.collect_all_categories(days=args.days)
            else:
                collector.launch_app(config.PACKAGE_NAME)
                if args.category == "sleep":
                    collector.collect_sleep(days=args.days)
                elif args.category == "heart_rate":
                    collector.collect_heart_rate(days=args.days)
                elif args.category == "stress":
                    collector.collect_stress(days=args.days)
                elif args.category == "body_composition":
                    collector.collect_body_composition(days=args.days)
        except Exception as e:
            print(f"[ADB Error] Failed during capture: {e}")
            print("Tip: Ensure your device is unlocked and USB debugging is enabled.")
    else:
        print("\n--- Step 1: Skipped ADB Capture ---")

    # Step 2: Vision AI Data Extraction
    if not args.skip_extract:
        print("\n--- Step 2: Vision AI Data Extraction ---")
        extractor = DataExtractor()
        results = extractor.process_all_screenshots()
        print(f" Extracted data from {len(results)} screenshot(s).")
    else:
        print("\n--- Step 2: Skipped AI Extraction ---")

    # Step 3: Report Generation
    print("\n--- Step 3: Generating Integrated Multi-Category Reports ---")
    reporter = ReportGenerator()
    reporter.run()

    print("\n==================================================")
    print(" All Pipeline Tasks Completed Successfully!")
    print(f" Output Location: {config.OUTPUT_DIR.resolve()}")
    print("==================================================")

if __name__ == "__main__":
    main()
