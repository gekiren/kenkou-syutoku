import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import config
from src.adb_collector import ADBCollector

def main():
    parser = argparse.ArgumentParser(description="HUAWEI Health App 4-Major Categories Auto Collector")
    parser.add_argument("--days", type=int, default=config.DEFAULT_CAPTURE_DAYS, help="Number of days to capture (default: 7)")
    parser.add_argument("--categories", type=str, default="all", help="Comma-separated categories to capture (sleep,heart_rate,stress,body_composition,all)")
    args = parser.parse_args()

    print("============================================================")
    print("  HUAWEI Health 4-Major Health Data Auto Collector")
    print(f"  Target Days: Past {args.days} Day(s)")
    print("  Order: Sleep -> Heart Rate -> Stress -> Body Composition")
    print("============================================================")

    collector = ADBCollector()
    if not collector.check_connection():
        print(f"[Fatal Error] ADB device '{config.DEVICE_ID}' is not connected.")
        sys.exit(1)

    start_time = time.time()

    if args.categories == "all":
        collector.collect_all_categories(days=args.days)
    else:
        cats = [c.strip().lower() for c in args.categories.split(",")]
        collector.launch_app(config.PACKAGE_NAME)
        
        for cat in ["sleep", "heart_rate", "stress", "body_composition"]:
            if cat in cats:
                if cat == "sleep":
                    collector.collect_sleep(days=args.days)
                elif cat == "heart_rate":
                    collector.collect_heart_rate(days=args.days)
                elif cat == "stress":
                    collector.collect_stress(days=args.days)
                elif cat == "body_composition":
                    collector.collect_body_composition(days=args.days)

    elapsed = time.time() - start_time
    print("\n============================================================")
    print(f" All capture tasks finished! (Elapsed: {elapsed:.1f} sec)")
    print(f" Saved to: {config.SCREENSHOTS_DIR.resolve()}")
    print("============================================================")

if __name__ == "__main__":
    main()
