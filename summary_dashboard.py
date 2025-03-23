"""
Home page for the Activity Tracker app.
"""

import streamlit as st
import datetime
import pandas as pd
from utils.ui_components import render_header, render_metric_card, render_progress_bar
from utils.data_manager import load_daily_data, load_weekly_data
from utils.date_utils import get_today, get_week_start, get_last_n_days, parse_iso_date, format_date
from config.settings import (
    DAILY_ACTIVITIES, WEEKLY_ACTIVITIES, MOOD_RANGE,
    SHORT_DATE_FORMAT, DATE_FORMAT
)

def render_activity_dashboard():
    """Render the home page dashboard with quick stats and activity history."""
    # render_header("概览")
    
    # Current date information
    today = get_today()
    st.subheader(f"今日: {today.strftime(DATE_FORMAT)}")
    
    # Load data
    daily_data = load_daily_data()
    weekly_data = load_weekly_data()
    
    # Dashboard with quick stats
    st.markdown("### 快速统计")
    
    # Create columns for daily and weekly summaries
    col1, col2 = st.columns(2)
    
    # Daily summary
    with col1:
        st.markdown("#### 今日活动")
        today_str = today.isoformat()
        
        if today_str in daily_data:
            st.success("你已完成今日活动登记!")
            
            # Display some key metrics
            if "weight" in daily_data[today_str]:
                render_metric_card(
                    "今日体重", 
                    f"{daily_data[today_str]['weight']} kg"
                )
            
            if "calories" in daily_data[today_str]:
                render_metric_card(
                    "卡路里摄入", 
                    f"{daily_data[today_str]['calories']} kcal"
                )
            
            if "mood" in daily_data[today_str]:
                mood_value = daily_data[today_str]['mood']
                mood_label = next((m["label"] for m in MOOD_RANGE if m["value"] == mood_value), "")
                mood_emojis = {1: "😞", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}
                mood_emoji = mood_emojis.get(mood_value, "")
                
                render_metric_card(
                    "今日心情", 
                    f"{mood_emoji} {mood_label}"
                )
            
            # Count completed activities (both boolean and complex)
            boolean_activity_ids = [activity["id"] for activity in DAILY_ACTIVITIES if activity["type"] == "boolean"]
            complex_activity_ids = [activity["id"] for activity in DAILY_ACTIVITIES if activity["type"] == "complex"]
            
            completed = sum(1 for act in boolean_activity_ids 
                         if act in daily_data[today_str] and daily_data[today_str][act])
            completed += sum(1 for act in complex_activity_ids
                         if act in daily_data[today_str] and daily_data[today_str][act])
            
            # render_progress_bar(
            #     completed, 
            #     max_value=len(boolean_activity_ids) + len(complex_activity_ids),
            #     label="已完成活动"
            # )
        else:
            st.warning("你还没有完成今日活动登记。")
            if st.button("前往每日登记页面", key="go_daily"):
                st.switch_page("pages/Daily.py")
    
    # Weekly summary
    with col2:
        st.markdown("#### 本周活动")
        # Calculate the current week start date (Monday)
        start_of_week = get_week_start(today)
        week_str = start_of_week.isoformat()
        
        if week_str in weekly_data:
            st.success("你已完成本周活动登记!")
            
            # Display some key metrics
            if "waist" in weekly_data[week_str]:
                render_metric_card(
                    "腰围测量", 
                    f"{weekly_data[week_str]['waist']} cm"
                )
            
            if "arm" in weekly_data[week_str]:
                render_metric_card(
                    "臂围测量", 
                    f"{weekly_data[week_str]['arm']} cm"
                )
            
            # Count completed activities
            weekly_activity_ids = [activity["id"] for activity in WEEKLY_ACTIVITIES]
            completed = sum(1 for act in weekly_activity_ids 
                          if act in weekly_data[week_str] and weekly_data[week_str][act])
            
            # render_progress_bar(
            #     completed, 
            #     max_value=len(weekly_activity_ids),
            #     label="已完成活动"
            # )
        else:
            st.warning("你还没有完成本周活动登记。")
            if st.button("前往每周登记页面", key="go_weekly"):
                st.switch_page("pages/Weekly.py")
    
    # Activity History
    st.markdown("---")
    st.header("活动历史")
    
    # 获取所有日期数据并按时间排序
    all_dates = []
    for date_str in daily_data.keys():
        try:
            date_obj = parse_iso_date(date_str)
            # 只考虑最近60天的数据
            if (get_today() - date_obj).days <= 60:
                all_dates.append(date_obj)
        except ValueError:
            continue
    
    # 按时间顺序排序
    all_dates.sort()
    
    # 最近7天的每日活动
    st.subheader("每日活动 (最近7天)")
    
    # 限制为最近的7天
    recent_dates = all_dates[-7:] if len(all_dates) > 7 else all_dates
    
    # 获取活动字段
    daily_metrics = ["weight", "calories", "mood"]
    # 获取布尔型活动
    daily_activity_ids = [activity["id"] for activity in DAILY_ACTIVITIES if activity["type"] == "boolean"]
    # 获取复合活动
    complex_activity_ids = []
    for activity in DAILY_ACTIVITIES:
        if activity["type"] == "complex":
            if activity["id"] == "exercise":
                complex_activity_ids.append(f"{activity['id']}_time")
            elif activity["id"] == "thesis":
                complex_activity_ids.append(f"{activity['id']}_wordcount")
            complex_activity_ids.append(activity["id"])
    
    all_daily_fields = daily_metrics + daily_activity_ids + complex_activity_ids
    
    # 创建空DataFrame，按时间顺序排列列
    date_columns = [d.strftime(SHORT_DATE_FORMAT) for d in recent_dates]
    daily_df = pd.DataFrame(
        index=all_daily_fields, 
        columns=date_columns
    )
    
    # 填充数据
    for date_obj in recent_dates:
        date_str = date_obj.isoformat()
        col = date_obj.strftime(SHORT_DATE_FORMAT)
        
        if date_str in daily_data:
            for field in all_daily_fields:
                if field in daily_data[date_str]:
                    if field == "weight":
                        daily_df.at[field, col] = f"{daily_data[date_str][field]} kg"
                    elif field == "calories":
                        daily_df.at[field, col] = f"{daily_data[date_str][field]} kcal"
                    elif field == "mood":
                        mood_value = daily_data[date_str][field]
                        mood_label = next((m["label"] for m in MOOD_RANGE if m["value"] == mood_value), "")
                        daily_df.at[field, col] = mood_label
                    elif field == "exercise_time":
                        daily_df.at[field, col] = f"{daily_data[date_str][field]} min"
                    elif field == "thesis_wordcount":
                        daily_df.at[field, col] = f"{daily_data[date_str][field]} 字"
                    elif isinstance(daily_data[date_str][field], bool):
                        daily_df.at[field, col] = "✅" if daily_data[date_str][field] else "❌"
                    else:
                        daily_df.at[field, col] = daily_data[date_str][field]
    
    st.dataframe(daily_df, use_container_width=True)
    
    # 获取所有周数据并按时间排序
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
    
    # 最近4周的每周活动
    st.subheader("每周活动 (最近4周)")
    
    # 限制为最近的4周
    recent_weeks = all_weeks[-4:] if len(all_weeks) > 4 else all_weeks
    
    # 创建列显示标签
    week_labels = []
    for week_start in recent_weeks:
        week_end = week_start + datetime.timedelta(days=6)
        week_labels.append(f"{format_date(week_start, '%m/%d')}-{format_date(week_end, '%m/%d')}")
    
    weekly_metrics = ["waist", "arm"]
    weekly_activity_ids = [activity["id"] for activity in WEEKLY_ACTIVITIES]
    all_weekly_fields = weekly_metrics + weekly_activity_ids + ["pattern_tracking"]
    
    # 创建空DataFrame
    weekly_df = pd.DataFrame(
        index=all_weekly_fields, 
        columns=week_labels
    )
    
    # 填充数据
    for i, week_start in enumerate(recent_weeks):
        week_str = week_start.isoformat()
        week_end = week_start + datetime.timedelta(days=6)
        label = f"{format_date(week_start, '%m/%d')}-{format_date(week_end, '%m/%d')}"
        
        if week_str in weekly_data:
            for field in all_weekly_fields:
                if field in weekly_data[week_str]:
                    if field == "waist":
                        weekly_df.at[field, label] = f"{weekly_data[week_str][field]} cm"
                    elif field == "arm":
                        weekly_df.at[field, label] = f"{weekly_data[week_str][field]} cm"
                    elif isinstance(weekly_data[week_str][field], bool):
                        weekly_df.at[field, label] = "✅" if weekly_data[week_str][field] else "❌"
                    else:
                        weekly_df.at[field, label] = weekly_data[week_str][field]
    
    st.dataframe(weekly_df, use_container_width=True)

# def main():
#     """Main function for the Home page."""
#     render_activity_dashboard()

# if __name__ == "__main__":
#     main()