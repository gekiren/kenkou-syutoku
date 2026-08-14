import calendar
from datetime import datetime, date

class HealthCalendarPicker:
    """
    HUAWEIヘルスケアアプリの日付選択カレンダーダイアログ（解像度 1600x2560）における
    任意日付（年月日時）のタップ座標 (X, Y) を動的計算するモジュール。
    """
    # 基準グリッド定数（実測ベース）
    COL_START_X = 279   # 日曜日 (col=0) の中心X座標
    COL_STEP_X = 173    # 曜日列ごとのXステップ (px)
    ROW_STEP_Y = 173    # 週行ごとのYステップ (px)

    # 2026年8月の第3週 (row=2, 8/9〜8/15) の実測Y基準
    # 8/13 (row=2, col=4) -> Y = 1863
    BASE_MONTH_ROW0_Y = 1517  # 当月第1週 (row=0) の中心Y座標

    @classmethod
    def get_date_coords(cls, target_date: date, current_month_anchor: date = None):
        """
        指定された target_date のカレンダー上の (X, Y) 座標を計算する。
        カレンダーは「日曜日始まり」。
        """
        if current_month_anchor is None:
            current_month_anchor = date.today()

        year = target_date.year
        month = target_date.month
        day = target_date.day

        # 日曜日始まりのカレンダーマトリクスを取得 (0=日, 1=月, ..., 6=土)
        # Pythonのcalendarモジュールはデフォルト月曜始まり(0=月)なので SUNDAY=6 を先頭に設定
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        month_days = cal.monthdayscalendar(year, month)

        target_row = None
        target_col = None

        for r_idx, week in enumerate(month_days):
            if day in week:
                target_row = r_idx
                target_col = week.index(day)
                break

        if target_row is None or target_col is None:
            raise ValueError(f"Date {target_date} not found in calendar for {year}-{month}")

        # X座標の算出: COL_START_X + col * COL_STEP_X
        x = cls.COL_START_X + target_col * cls.COL_STEP_X

        # Y座標の算出: 当月内の row に応じた位置
        y = cls.BASE_MONTH_ROW0_Y + target_row * cls.ROW_STEP_Y

        return x, y

if __name__ == "__main__":
    # テスト検証
    test_dates = [
        date(2026, 8, 14), # 今日 (金)
        date(2026, 8, 13), # 昨日 (木) -> 実測 (971, 1863)
        date(2026, 8, 12), # 2日前 (水)
        date(2026, 8, 11), # 3日前 (火) -> 実測 (625, 1863)
        date(2026, 8, 8),  # 6日前 (土, 第2週)
        date(2026, 8, 7),  # 7日前 (金, 第2週)
    ]
    for d in test_dates:
        cx, cy = HealthCalendarPicker.get_date_coords(d)
        print(f"Date: {d} (Weekday: {d.strftime('%a')}) -> Calculated Tap Coords: (X={cx}, Y={cy})")
