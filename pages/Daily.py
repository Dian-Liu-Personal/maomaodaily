"""
Daily tracking page for the Activity Tracker app.
"""

import streamlit as st
import pandas as pd
import datetime
import altair as alt
from utils.ui_components import (
    render_header, render_calendar, render_date_selector, 
    render_activity_summary, render_metric_card, render_mood_slider
)
from utils.data_manager import load_daily_data, save_daily_data
from utils.date_utils import (
    get_today, get_week_dates, get_last_n_days, 
    format_date, parse_iso_date
)
from config.settings import (
    DAILY_ACTIVITIES, MOOD_RANGE,
    DATE_FORMAT, SHORT_DATE_FORMAT
)

def render_week_view(selected_date, daily_data):
    """
    Render a view of the entire week with activity data.
    
    Args:
        selected_date (datetime.date): The currently selected date.
        daily_data (dict): Dictionary of daily tracking data.
    """
    # Get the Monday of the selected week
    week_start = selected_date - datetime.timedelta(days=selected_date.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    
    st.header(f"Week of {format_date(week_start, '%B %d')} - {format_date(week_end, '%B %d, %Y')}")
    
    # Create a list of dates for the selected week
    week_dates = get_week_dates(selected_date)
    
    # Get all activity names by category
    activity_names = ["体重 (kg)", "卡路里"]
    activity_keys = ["weight", "calories"]
    
    # Add mood
    activity_names.append("心情")
    activity_keys.append("mood")
    
    # Add complex activities
    for act in DAILY_ACTIVITIES:
        if act["type"] == "complex":
            if act["id"] == "exercise":
                activity_names.append(f"{act['name']} (分钟)")
                activity_keys.append(f"{act['id']}_time")
            elif act["id"] == "thesis":
                activity_names.append(f"{act['name']} (字数)")
                activity_keys.append(f"{act['id']}_wordcount")
    
    # Add all boolean activities
    for act in DAILY_ACTIVITIES:
        if act["type"] == "boolean":
            activity_names.append(act["name"])
            activity_keys.append(act["id"])
    
    # Initialize empty DataFrame
    week_df = pd.DataFrame(
        index=activity_names, 
        columns=[format_date(d, SHORT_DATE_FORMAT) for d in week_dates]
    )
    
    # Fill in existing data
    for day in week_dates:
        day_str = day.isoformat()
        col = format_date(day, SHORT_DATE_FORMAT)
        
        if day_str in daily_data:
            for i, key in enumerate(activity_keys):
                if key in daily_data[day_str]:
                    value = daily_data[day_str][key]
                    if key == "mood" and value is not None:
                        # Find the mood label for the value
                        for mood in MOOD_RANGE:
                            if mood["value"] == value:
                                week_df.at[activity_names[i], col] = mood["label"]
                                break
                    elif isinstance(value, bool):
                        week_df.at[activity_names[i], col] = "✅" if value else "❌"
                    else:
                        week_df.at[activity_names[i], col] = value
    
    # Display the week view
    st.dataframe(week_df, use_container_width=True)

def render_daily_form(selected_date, daily_data):
    """
    Render the form for entering daily activities.
    
    Args:
        selected_date (datetime.date): The currently selected date.
        daily_data (dict): Dictionary of daily tracking data.
        
    Returns:
        bool: True if the form was submitted, False otherwise.
    """
    date_str = selected_date.isoformat()
    
    # Ensure data exists for this date
    if date_str not in daily_data:
        daily_data[date_str] = {}
    
    st.header(f"记录活动 {format_date(selected_date, DATE_FORMAT)}")
    
    # Create form for data entry
    with st.form("daily_form", clear_on_submit=False):
        st.subheader("身体数据")
        weight = st.number_input(
            "体重 (kg)", 
            min_value=0.0, 
            max_value=300.0, 
            step=0.1, 
            value=float(daily_data[date_str].get("weight", 0))
        )
        
        calories = st.number_input(
            "卡路里摄入", 
            min_value=0, 
            max_value=10000, 
            step=50, 
            value=int(daily_data[date_str].get("calories", 0))
        )
        
        # Mood value
        st.subheader("心情")
        mood_value = daily_data[date_str].get("mood", 3)  # Default to middle value
        mood_labels = {mood["value"]: mood["label"] for mood in MOOD_RANGE}
        
        # Display the slider within the form
        mood = st.slider(
            "今日心情",
            min_value=1,
            max_value=5,
            value=mood_value,
            step=1
        )
        
        # Display mood emoji and label
        mood_emojis = {1: "😞", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}
        st.write(f"{mood_emojis.get(mood, '')} {mood_labels.get(mood, '')}")
        
        # Group activities by category
        study_activities = [act for act in DAILY_ACTIVITIES if act.get("category") == "学习安排"]
        life_activities = [act for act in DAILY_ACTIVITIES if act.get("category") == "生活"]
        entertainment_activities = [act for act in DAILY_ACTIVITIES if act.get("category") == "娱乐"]
        special_activities = [act for act in DAILY_ACTIVITIES if act.get("category") == "特殊"]
        
        # Create activity checkboxes grouped by category
        st.subheader("学习安排")
        study_values = {}
        for activity in study_activities:
            if activity["type"] == "boolean":
                study_values[activity["id"]] = st.checkbox(
                    activity["name"], 
                    value=daily_data[date_str].get(activity["id"], False)
                )
            elif activity["type"] == "complex" and activity["id"] == "thesis":
                col1, col2 = st.columns(2)
                with col1:
                    study_values[activity["id"]] = st.checkbox(
                        activity["name"], 
                        value=daily_data[date_str].get(activity["id"], False)
                    )
                with col2:
                    wordcount_key = f"{activity['id']}_wordcount"
                    study_values[wordcount_key] = st.number_input(
                        "字数",
                        min_value=0,
                        max_value=100000,
                        step=100,
                        value=int(daily_data[date_str].get(wordcount_key, 0))
                    )
            
        st.subheader("生活活动")
        life_values = {}
        for activity in life_activities:
            if activity["type"] == "boolean":
                life_values[activity["id"]] = st.checkbox(
                    activity["name"], 
                    value=daily_data[date_str].get(activity["id"], False)
                )
            elif activity["type"] == "complex" and activity["id"] == "exercise":
                col1, col2 = st.columns(2)
                with col1:
                    life_values[activity["id"]] = st.checkbox(
                        activity["name"], 
                        value=daily_data[date_str].get(activity["id"], False)
                    )
                with col2:
                    time_key = f"{activity['id']}_time"
                    life_values[time_key] = st.number_input(
                        "时长 (分钟)",
                        min_value=0,
                        max_value=1440,  # 24 hours max
                        step=5,
                        value=int(daily_data[date_str].get(time_key, 0))
                    )
            
        st.subheader("娱乐活动")
        entertainment_values = {}
        col1, col2 = st.columns(2)
        for i, activity in enumerate(entertainment_activities):
            col = col1 if i % 2 == 0 else col2
            with col:
                entertainment_values[activity["id"]] = st.checkbox(
                    activity["name"], 
                    value=daily_data[date_str].get(activity["id"], False)
                )
        
        # # Special activities
        # if special_activities:
        #     st.subheader("特殊活动")
        #     special_values = {}
        #     for activity in special_activities:
        #         special_values[activity["id"]] = st.checkbox(
        #             activity["name"], 
        #             value=daily_data[date_str].get(activity["id"], False)
        #         )
        
        notes = st.text_area(
            "今日备注", 
            value=daily_data[date_str].get("notes", "")
        )
        
        submitted = st.form_submit_button("保存")
        
        if submitted:
            # Save form data
            data_to_save = {
                "weight": weight,
                "calories": calories,
                "mood": mood,
                "notes": notes
            }
            
            # Add all activity values
            for act_id, value in study_values.items():
                data_to_save[act_id] = value
                
            for act_id, value in life_values.items():
                data_to_save[act_id] = value
                
            for act_id, value in entertainment_values.items():
                data_to_save[act_id] = value
                
            # for act_id, value in special_values.items():
            #     data_to_save[act_id] = value
            
            # Update the data for this date
            daily_data[date_str] = data_to_save
            
            # Save to file
            save_daily_data(daily_data)
            
            st.success(f"活动已保存 {format_date(selected_date, DATE_FORMAT)}!")
            return True
    
    return False

def render_statistics(daily_data):
    """
    Render statistics and charts for daily activities.
    
    Args:
        daily_data (dict): Dictionary of daily tracking data.
    """
    st.header("统计数据")
    
    # 收集所有有数据的日期
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
    
    # 限制为最近的7天
    relevant_dates = all_dates[-7:] if len(all_dates) > 7 else all_dates
    
    # 创建统计数据
    stats_data = []
    for date_obj in relevant_dates:
        date_str = date_obj.isoformat()
        if date_str in daily_data:
            day_data = daily_data[date_str]
            
            stats_data.append({
                "Date": date_obj,  # 用于排序
                "DateStr": format_date(date_obj, SHORT_DATE_FORMAT),  # 用于显示
                "Weight": day_data.get("weight", None),
                "Calories": day_data.get("calories", None),
                "Mood": day_data.get("mood", None)
            })
    
    if stats_data:
        # 创建DataFrame
        stats_df = pd.DataFrame(stats_data)
        
        # 设置索引为日期，确保图表按时间顺序显示
        stats_df.set_index("Date", inplace=True)
        stats_df.sort_index(inplace=True)
        
        # 显示体重趋势
        # if not stats_df["Weight"].isna().all():
        #     st.subheader("体重趋势")
        #     chart_data = pd.DataFrame({'体重': stats_df["Weight"]})
        #     st.line_chart(chart_data, use_container_width=True)
        if not stats_df["Weight"].isna().all():
            st.subheader("体重趋势")
            chart_data = pd.DataFrame({
                '日期': stats_df.index,
                '体重': stats_df["Weight"]
            }).reset_index(drop=True)

            line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                x='日期:T',
                y=alt.Y('体重:Q', scale=alt.Scale(domain=[55, 65])),
                tooltip=['日期', '体重']
            ).properties(
                width='container',
                height=300
            )

            st.altair_chart(line_chart, use_container_width=True)
        
        # 显示卡路里趋势
        if not stats_df["Calories"].isna().all():
            st.subheader("卡路里摄入趋势")
            chart_data = pd.DataFrame({'卡路里': stats_df["Calories"]})
            st.line_chart(chart_data, use_container_width=True)
        
        # 显示心情趋势
        if not stats_df["Mood"].isna().all():
            st.subheader("心情趋势")
            chart_data = pd.DataFrame({'心情': stats_df["Mood"]})
            st.line_chart(chart_data, use_container_width=True)
        
        # 显示原始数据表格（时间排序）
        st.subheader("近期数据详情")
        display_df = stats_df.copy()
        display_df.index = stats_df["DateStr"]
        display_df = display_df.drop(columns=["DateStr"])
        st.dataframe(display_df)

        st.subheader("今日备注历史")
        notes_dates = {}
        for date_obj in all_dates:
            date_str = date_obj.isoformat()
            if date_str in daily_data and "notes" in daily_data[date_str] and daily_data[date_str]["notes"].strip():
                formatted_date = format_date(date_obj, DATE_FORMAT)
                notes_dates[formatted_date] = date_str

        if notes_dates:
            selected_date_for_notes = st.selectbox("选择日期查看备注:", options=list(notes_dates.keys()))
            selected_date_str = notes_dates[selected_date_for_notes]
            st.text_area("备注内容:", value=daily_data[selected_date_str]["notes"], height=150)
        else:
            st.info("暂无备注记录")

def main():
    """Main function for the Daily tracking page."""
    render_header("每日活动跟踪", "📆")
    
    # Load data
    daily_data = load_daily_data()
    
    # Date selection
    selected_date = render_date_selector()
    
    # Display week view
    render_week_view(selected_date, daily_data)
    
    # Daily activity form
    form_submitted = render_daily_form(selected_date, daily_data)
    
    # If form was submitted, refresh the page to update the calendar and weekly view
    if form_submitted:
        st.rerun()
    
    # Display statistics
    render_statistics(daily_data)

if __name__ == "__main__":
    main()
