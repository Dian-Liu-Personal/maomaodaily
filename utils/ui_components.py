"""
Reusable UI components for the Activity Tracker app.
"""

import streamlit as st
import pandas as pd
import datetime
from utils.date_utils import get_today, get_week_start, get_week_end, get_month_calendar
from config.settings import MOOD_RANGE

def render_header(title, emoji="📊"):
    """
    Render a styled header for a page.
    
    Args:
        title (str): Page title.
        emoji (str, optional): Emoji to display next to title.
    """
    st.markdown(f"<h1>{emoji} {title}</h1>", unsafe_allow_html=True)
    st.markdown("---")

def render_calendar(year, month, selected_date=None, highlight_week=False):
    """
    Render an interactive month calendar.
    
    Args:
        year (int): Year to display.
        month (int): Month to display (1-12).
        selected_date (datetime.date, optional): Date to highlight as selected.
        highlight_week (bool, optional): Whether to highlight the week of the selected date.
        
    Returns:
        pandas.DataFrame: Calendar DataFrame.
    """
    # Create the calendar DataFrame
    calendar_df = get_month_calendar(year, month)
    
    # Determine the dates to highlight
    today = get_today()
    highlight_dates = [today]
    
    if selected_date and highlight_week:
        week_start = get_week_start(selected_date)
        week_end = get_week_end(selected_date)
        highlight_week_dates = [week_start + datetime.timedelta(days=i) for i in range(7)]
        highlight_dates.extend(highlight_week_dates)
    
    # Function to apply styles to the calendar
    def style_calendar(df):
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        
        # Apply styles based on conditions
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell = df.iloc[i, j]
                if cell is None:
                    styles.iloc[i, j] = 'background-color: #f9f9f9; color: #f9f9f9;'
                elif cell == today:
                    styles.iloc[i, j] = 'background-color: #e6f3ff; font-weight: bold; text-align: center;'
                elif selected_date and cell == selected_date:
                    styles.iloc[i, j] = 'background-color: #ffe6cc; font-weight: bold; text-align: center;'
                elif highlight_week and selected_date and cell >= week_start and cell <= week_end:
                    styles.iloc[i, j] = 'background-color: #fff5e6; text-align: center;'
                else:
                    styles.iloc[i, j] = 'background-color: #ffffff; text-align: center;'
        return styles
    
    # Format the calendar for display
    styled_calendar = calendar_df.style.apply(style_calendar, axis=None)
    
    # Display the calendar
    st.dataframe(styled_calendar, use_container_width=True, height=250)
    
    return calendar_df

def render_metric_card(title, value, delta=None, delta_color="normal", help_text=None):
    """
    Render a metric card with title and value.
    
    Args:
        title (str): Metric title.
        value (str): Metric value.
        delta (str, optional): Delta value to display.
        delta_color (str, optional): Color for delta ("normal", "inverse", "off").
        help_text (str, optional): Help text to display on hover.
    """
    if help_text:
        with st.expander(title, expanded=True):
            st.metric(label="", value=value, delta=delta, delta_color=delta_color, help=help_text)
    else:
        st.metric(label=title, value=value, delta=delta, delta_color=delta_color)

def render_activity_summary(activities, activity_data, columns=2):
    """
    Render a summary of activities.
    
    Args:
        activities (list): List of activity dictionaries with 'id' and 'name' keys.
        activity_data (dict): Dictionary of activity data where keys are activity IDs.
        columns (int, optional): Number of columns to display activities in.
    """
    cols = st.columns(columns)
    
    for i, activity in enumerate(activities):
        col_idx = i % columns
        activity_id = activity["id"]
        activity_name = activity["name"]
        
        with cols[col_idx]:
            is_completed = activity_data.get(activity_id, False)
            icon = "✅" if is_completed else "❌"
            st.markdown(f"{icon} {activity_name}")

def render_progress_bar(value, min_value=0, max_value=100, label=None):
    """
    Render a progress bar.
    
    Args:
        value (float): Current value.
        min_value (float, optional): Minimum value.
        max_value (float, optional): Maximum value.
        label (str, optional): Label to display above the progress bar.
    """
    if label:
        st.write(label)
    
    # Ensure value is within range
    normalized_value = max(min_value, min(value, max_value))
    percentage = int((normalized_value - min_value) / (max_value - min_value) * 100)
    
    # Create progress bar
    st.progress(percentage / 100)
    st.write(f"{percentage}% ({normalized_value}/{max_value})")

def render_week_navigator(selected_date):
    """
    Render a week navigation component.
    
    Args:
        selected_date (datetime.date): Currently selected date.
        
    Returns:
        datetime.date: New selected date after navigation.
    """
    week_start = get_week_start(selected_date)
    week_end = get_week_end(selected_date)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("← 上一周"):
            return week_start - datetime.timedelta(days=7)
    
    with col2:
        st.markdown(f"### 周: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
    
    with col3:
        if st.button("下一周 →"):
            return week_start + datetime.timedelta(days=7)
    
    return selected_date

def render_date_selector(default_date=None):
    """
    Render a date selection component with calendar view.
    
    Args:
        default_date (datetime.date, optional): Default selected date.
        
    Returns:
        datetime.date: Selected date.
    """
    if default_date is None:
        default_date = get_today()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        month = st.selectbox("月份", range(1, 13), index=default_date.month - 1)
        year = st.selectbox("年份", range(get_today().year - 2, get_today().year + 2), 
                           index=2)
    
    # Render calendar
    with col2:
        calendar_df = render_calendar(year, month, default_date)
    
    # Date input for precise selection
    selected_date = st.date_input("选择日期", default_date)
    
    return selected_date

def render_mood_slider(current_value=3):
    """
    Render a slider for mood tracking.
    
    Args:
        current_value (int, optional): Current mood value (1-5).
        
    Returns:
        int: Selected mood value.
    """
    # Create labels for the slider
    mood_labels = {mood["value"]: mood["label"] for mood in MOOD_RANGE}
    
    # Display the slider
    mood_value = st.slider(
        "今日心情",
        min_value=1,
        max_value=5,
        value=current_value,
        step=1
    )
    
    # Display mood emoji and label
    mood_emojis = {1: "😞", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}
    st.write(f"{mood_emojis.get(mood_value, '')} {mood_labels.get(mood_value, '')}")
    
    return mood_value