"""
Weekly tracking page for the Activity Tracker app.
"""

import streamlit as st
import pandas as pd
import datetime
from utils.ui_components import (
    render_header, render_calendar, render_metric_card, 
    render_week_navigator, render_progress_bar
)
from utils.data_manager import load_daily_data, load_weekly_data, save_weekly_data
from utils.date_utils import (
    get_today, get_week_start, get_week_end, get_week_dates,
    get_last_n_weeks, format_date, parse_iso_date
)
from config.settings import (
    WEEKLY_ACTIVITIES, MONTH_YEAR_FORMAT, 
    SHORT_DATE_FORMAT, MOOD_RANGE
)

def render_week_selector():
    """
    Render a week selection interface.
    
    Returns:
        datetime.date: Start date of the selected week.
    """
    st.subheader("选择周")
    
    # Get current date
    today = get_today()
    
    # Calculate the start of the current week (Monday)
    current_week_start = get_week_start(today)
    
    # Create a list of weeks to show
    weeks = []
    for i in range(8):  # Show 8 weeks
        week_start = current_week_start - datetime.timedelta(weeks=i)
        week_end = week_start + datetime.timedelta(days=6)
        weeks.append({
            "start": week_start,
            "end": week_end,
            "display": f"{format_date(week_start, '%b %d')} - {format_date(week_end, '%b %d, %Y')}"
        })
    
    selected_week_idx = st.selectbox(
        "选择一周",
        options=list(range(len(weeks))),
        format_func=lambda idx: weeks[idx]["display"],
        index=0
    )
    
    selected_week = weeks[selected_week_idx]
    return selected_week["start"]

def render_month_calendar(selected_week_start):
    """
    Render a month calendar with the selected week highlighted.
    
    Args:
        selected_week_start (datetime.date): Start date of the selected week.
    """
    st.header(f"月视图: {format_date(selected_week_start, MONTH_YEAR_FORMAT)}")
    
    # Render calendar for the month containing the selected week
    render_calendar(
        selected_week_start.year, 
        selected_week_start.month, 
        selected_week_start,
        highlight_week=True
    )

def render_daily_summary(selected_week_start, daily_data):
    """
    Render a summary of daily activities for the selected week.
    
    Args:
        selected_week_start (datetime.date): Start date of the selected week.
        daily_data (dict): Dictionary of daily tracking data.
    """
    week_dates = get_week_dates(selected_week_start)
    
    # Create a summary of daily activities for this week
    daily_summary = {}
    
    for day in week_dates:
        day_str = day.isoformat()
        if day_str in daily_data:
            # Count completed activities (both boolean and complex)
            boolean_activities = ["jung", "english", "going_out", "bowel_movement", "dog_walking",
                               "metaphysics", "drawing", "writing", "watching_shows", "casual_reading", "friends"]
            complex_activities = ["exercise", "thesis"]
            
            activity_count = sum(1 for activity in boolean_activities if daily_data[day_str].get(activity, False))
            activity_count += sum(1 for activity in complex_activities if daily_data[day_str].get(activity, False))
            
            daily_summary[day_str] = {
                "日期": format_date(day, SHORT_DATE_FORMAT),
                "体重": daily_data[day_str].get("weight", None),
                "活动数": activity_count,
                "心情": daily_data[day_str].get("mood", None)
            }
    
    # Show daily summary in a table
    if daily_summary:
        st.subheader("本周每日活动")
        summary_df = pd.DataFrame([daily_summary[day_str] for day_str in daily_summary])
        if not summary_df.empty:
            # Convert mood values to labels
            if "心情" in summary_df.columns:
                summary_df["心情"] = summary_df["心情"].apply(lambda x: next((m["label"] for m in MOOD_RANGE if m["value"] == x), "") if pd.notna(x) else "")
            
            st.dataframe(summary_df.set_index("日期"), use_container_width=True)

def render_weekly_form(selected_week_start, weekly_data):
    """
    Render the form for entering weekly activities.
    
    Args:
        selected_week_start (datetime.date): Start date of the selected week.
        weekly_data (dict): Dictionary of weekly tracking data.
        
    Returns:
        bool: True if the form was submitted, False otherwise.
    """
    # Weekly data is indexed by the start date (Monday) of the week
    week_str = selected_week_start.isoformat()
    
    # Check if data exists for this week
    if week_str not in weekly_data:
        weekly_data[week_str] = {}
    
    week_end = get_week_end(selected_week_start)
    st.header(f"记录每周活动")
    
    # Create form for data entry
    with st.form("weekly_form", clear_on_submit=False):
        st.subheader("身体测量")
        waist = st.number_input(
            "腰围 (cm)", 
            min_value=0.0, 
            max_value=200.0, 
            step=0.1,
            value=float(weekly_data[week_str].get("waist", 0))
        )
        
        arm = st.number_input(
            "臂围 (cm)", 
            min_value=0.0, 
            max_value=100.0, 
            step=0.1,
            value=float(weekly_data[week_str].get("arm", 0))
        )
        
        st.subheader("活动")
        
        activity_values = {}
        for activity in WEEKLY_ACTIVITIES:
            activity_values[activity["id"]] = st.checkbox(
                activity["name"], 
                value=weekly_data[week_str].get(activity["id"], False)
            )
        
        # pattern_tracking = st.text_area(
        #     "可追溯规律", 
        #     value=weekly_data[week_str].get("pattern_tracking", "")
        # )
        
        notes = st.text_area(
            "本周备注", 
            value=weekly_data[week_str].get("notes", "")
        )
        
        submitted = st.form_submit_button("保存")
        
        if submitted:
            # Save form data
            data_to_save = {
                "waist": waist,
                "arm": arm,
                # "pattern_tracking": pattern_tracking,
                "notes": notes
            }
            
            # Add all activity values
            for act_id, value in activity_values.items():
                data_to_save[act_id] = value
            
            # Update the data for this week
            weekly_data[week_str] = data_to_save
            
            # Save to file
            save_weekly_data(weekly_data)
            
            week_range = f"{format_date(selected_week_start, '%b %d')} - {format_date(week_end, '%b %d, %Y')}"
            st.success(f"每周活动已保存 {week_range}!")
            return True
    
    return False

def render_weekly_trends(weekly_data):
    """
    Render trends from weekly tracking data.
    
    Args:
        weekly_data (dict): Dictionary of weekly tracking data.
    """
    st.header("每周趋势")
    
    # 收集所有有数据的周
    all_weeks = []
    for week_str in weekly_data.keys():
        try:
            week_start = parse_iso_date(week_str)
            # 只考虑最近6个月的数据
            if (get_today() - week_start).days <= 180:
                all_weeks.append(week_start)
        except ValueError:
            continue
    
    # 按时间顺序排序
    all_weeks.sort()
    
    # 限制为最近的8周
    relevant_weeks = all_weeks[-8:] if len(all_weeks) > 8 else all_weeks
    
    # 创建统计数据
    stats_data = []
    for week_start in relevant_weeks:
        week_str = week_start.isoformat()
        if week_str in weekly_data:
            week_data = weekly_data[week_str]
            week_end = week_start + datetime.timedelta(days=6)
            
            # 计算完成的活动
            activity_count = sum(1 for activity in [act["id"] for act in WEEKLY_ACTIVITIES]
                                if week_data.get(activity, False))
            
            stats_data.append({
                "Week": week_start,  # 用于排序
                "WeekLabel": f"{format_date(week_start, '%m/%d')}-{format_date(week_end, '%m/%d')}",  # 用于显示
                "腰围": week_data.get("waist", None),
                "臂围": week_data.get("arm", None),
                "活动": activity_count
            })
    
    if stats_data:
        # 创建DataFrame
        stats_df = pd.DataFrame(stats_data)
        
        # 设置索引为周开始日期，确保图表按时间顺序显示
        stats_df.set_index("Week", inplace=True)
        stats_df.sort_index(inplace=True)
        
        # 显示腰围趋势
        if not stats_df["腰围"].isna().all():
            st.subheader("腰围趋势")
            chart_data = pd.DataFrame({'腰围': stats_df["腰围"]})
            st.line_chart(chart_data, use_container_width=True)
        
        # 显示臂围趋势
        if not stats_df["臂围"].isna().all():
            st.subheader("臂围趋势")
            chart_data = pd.DataFrame({'臂围': stats_df["臂围"]})
            st.line_chart(chart_data, use_container_width=True)
        
        # # 显示每周活动趋势
        # st.subheader("每周完成活动数")
        # chart_data = pd.DataFrame({'活动数': stats_df["活动"]})
        # st.bar_chart(chart_data, use_container_width=True)
        
        # 显示原始数据表格（时间排序）
        st.subheader("近期周数据详情")
        display_df = stats_df.copy()
        display_df.index = stats_df["WeekLabel"]
        display_df = display_df.drop(columns=["WeekLabel"])
        st.dataframe(display_df)

def render_weekly_summary(selected_week_start, weekly_data, daily_data):
    """
    Render a summary of progress for the selected week.
    
    Args:
        selected_week_start (datetime.date): Start date of the selected week.
        weekly_data (dict): Dictionary of weekly tracking data.
        daily_data (dict): Dictionary of daily tracking data.
    """
    st.header("每周进度总结")
    
    week_str = selected_week_start.isoformat()
    
    # Compare with previous week
    prev_week_start = selected_week_start - datetime.timedelta(weeks=1)
    prev_week_str = prev_week_start.isoformat()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("腰围趋势")
        current_waist = weekly_data[week_str].get("waist", 0)
        prev_waist = weekly_data.get(prev_week_str, {}).get("waist", 0)
        
        if current_waist > 0 and prev_waist > 0:
            waist_diff = current_waist - prev_waist
            render_metric_card(
                "腰围变化", 
                f"{waist_diff:.1f} cm", 
                delta=f"{waist_diff:.1f} cm",
                delta_color="inverse" if waist_diff < 0 else "normal"
            )
            
        st.subheader("臂围趋势")
        current_arm = weekly_data[week_str].get("arm", 0)
        prev_arm = weekly_data.get(prev_week_str, {}).get("arm", 0)
        
        if current_arm > 0 and prev_arm > 0:
            arm_diff = current_arm - prev_arm
            render_metric_card(
                "臂围变化", 
                f"{arm_diff:.1f} cm", 
                delta=f"{arm_diff:.1f} cm",
                delta_color="inverse" if arm_diff < 0 else "normal"
            )
    
    with col2:
        st.subheader("每周任务")
        activities = [act["id"] for act in WEEKLY_ACTIVITIES]
        completed = sum(1 for act in activities 
                       if act in weekly_data[week_str] and weekly_data[week_str][act])
        
        render_progress_bar(
            completed, 
            max_value=len(activities),
            label="已完成"
        )
    
    with col3:
        st.subheader("每日一致性")
        week_dates = get_week_dates(selected_week_start)
        days_tracked = sum(1 for day in week_dates if day.isoformat() in daily_data)
        
        render_progress_bar(
            days_tracked, 
            max_value=7,
            label="已跟踪天数"
        )
        
        # Calculate average daily activities
        if days_tracked > 0:
            total_activities = 0
            for day in week_dates:
                day_str = day.isoformat()
                if day_str in daily_data:
                    # Count completed activities
                    boolean_activities = ["jung", "english", "going_out", "bowel_movement", "dog_walking",
                                       "metaphysics", "drawing", "writing", "watching_shows", "casual_reading", "friends"]
                    complex_activities = ["exercise", "thesis"]
                    
                    activity_count = sum(1 for activity in boolean_activities if daily_data[day_str].get(activity, False))
                    activity_count += sum(1 for activity in complex_activities if daily_data[day_str].get(activity, False))
                    
                    total_activities += activity_count
            
            avg_activities = total_activities / days_tracked
            render_metric_card("平均每日活动", f"{avg_activities:.1f}")

def main():
    """Main function for the Weekly tracking page."""
    render_header("每周活动跟踪", "📅")
    
    # Load data
    daily_data = load_daily_data()
    weekly_data = load_weekly_data()
    
    # Week selection
    selected_week_start = render_week_selector()
    
    # Display month calendar with week highlighted
    render_month_calendar(selected_week_start)
    
    # Display week overview
    st.header(f"周概览: {format_date(selected_week_start, '%b %d')} - {format_date(get_week_end(selected_week_start), '%b %d, %Y')}")
    
    # Show daily summary for this week
    render_daily_summary(selected_week_start, daily_data)
    
    # Weekly activity form
    form_submitted = render_weekly_form(selected_week_start, weekly_data)
    
    # If form was submitted, refresh the page
    if form_submitted:
        st.rerun()
    
    # Display weekly trends
    render_weekly_trends(weekly_data)
    
    # Display weekly summary
    # render_weekly_summary(selected_week_start, weekly_data, daily_data)

if __name__ == "__main__":
    main()