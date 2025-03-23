"""
Utility package for the Activity Tracker app.
"""

# Import main modules to make them available when importing the package
from utils.data_manager import (
    load_daily_data, save_daily_data,
    load_weekly_data, save_weekly_data
)

from utils.date_utils import (
    get_today, get_week_start, get_week_end, get_week_dates,
    get_month_calendar, get_last_n_days, get_last_n_weeks,
    format_date, parse_iso_date
)

from utils.ui_components import (
    render_header, render_calendar, render_date_selector,
    render_week_navigator, render_metric_card, render_progress_bar,
    render_activity_summary
)
