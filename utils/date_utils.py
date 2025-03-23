"""
Date handling utilities for the Activity Tracker app.
"""

import datetime
import calendar
import pandas as pd

def get_today():
    """
    Get today's date.
    
    Returns:
        datetime.date: Today's date.
    """
    return datetime.date.today()

def get_week_start(date):
    """
    Get the Monday of the week containing the given date.
    
    Args:
        date (datetime.date): The date to get the week start for.
        
    Returns:
        datetime.date: The Monday of the week.
    """
    return date - datetime.timedelta(days=date.weekday())

def get_week_end(date):
    """
    Get the Sunday of the week containing the given date.
    
    Args:
        date (datetime.date): The date to get the week end for.
        
    Returns:
        datetime.date: The Sunday of the week.
    """
    return get_week_start(date) + datetime.timedelta(days=6)

def get_week_dates(date):
    """
    Get all dates in the week containing the given date.
    
    Args:
        date (datetime.date): The date to get the week for.
        
    Returns:
        list: List of datetime.date objects for the week.
    """
    week_start = get_week_start(date)
    return [week_start + datetime.timedelta(days=i) for i in range(7)]

def get_month_calendar(year, month):
    """
    Get a calendar representation of the given month.
    
    Args:
        year (int): Year.
        month (int): Month (1-12).
        
    Returns:
        pandas.DataFrame: Calendar DataFrame with weekdays as columns.
    """
    # Get first day of the month and number of days
    first_day = datetime.date(year, month, 1)
    _, num_days = calendar.monthrange(year, month)
    
    # Create a list of dates for the month
    dates = [datetime.date(year, month, day) for day in range(1, num_days+1)]
    
    # Create a calendar layout
    weeks = []
    week = [None] * first_day.weekday()
    for date in dates:
        week.append(date)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week + [None] * (7 - len(week)))
    
    # Return as DataFrame
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return pd.DataFrame(weeks, columns=weekdays)

def get_last_n_days(n, end_date=None):
    """
    Get a list of the last n days.
    
    Args:
        n (int): Number of days to get.
        end_date (datetime.date, optional): End date (defaults to today).
        
    Returns:
        list: List of date strings in ISO format.
    """
    if end_date is None:
        end_date = get_today()
    return [(end_date - datetime.timedelta(days=i)).isoformat() for i in range(n)]

def get_last_n_weeks(n, end_date=None):
    """
    Get a list of the start dates of the last n weeks.
    
    Args:
        n (int): Number of weeks to get.
        end_date (datetime.date, optional): End date (defaults to today).
        
    Returns:
        list: List of date strings in ISO format for the start of each week.
    """
    if end_date is None:
        end_date = get_today()
    start_of_week = get_week_start(end_date)
    return [(start_of_week - datetime.timedelta(weeks=i)).isoformat() for i in range(n)]

def format_date(date, format_str):
    """
    Format a date according to the specified format string.
    
    Args:
        date (datetime.date): Date to format.
        format_str (str): Format string.
        
    Returns:
        str: Formatted date string.
    """
    return date.strftime(format_str)

def parse_iso_date(date_str):
    """
    Parse an ISO format date string to a datetime.date object.
    
    Args:
        date_str (str): ISO format date string (YYYY-MM-DD).
        
    Returns:
        datetime.date: Date object.
    """
    return datetime.date.fromisoformat(date_str)
