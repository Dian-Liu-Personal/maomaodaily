"""
Data management utilities for loading and saving application data.
"""

import os
import json
from config.settings import DATA_DIR, DAILY_DATA_FILE, WEEKLY_DATA_FILE

def ensure_data_directory():
    """
    Create data directory if it doesn't exist.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_data(filename):
    """
    Load data from a JSON file.
    
    Args:
        filename (str): Name of the file to load.
        
    Returns:
        dict: The loaded data, or an empty dict if the file doesn't exist.
    """
    ensure_data_directory()
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Return empty dict if file is corrupted
            return {}
    return {}

def save_data(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data (dict): Data to save.
        filename (str): Name of the file to save to.
    """
    ensure_data_directory()
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def load_daily_data():
    """
    Load daily tracking data.
    
    Returns:
        dict: Daily tracking data.
    """
    return load_data(DAILY_DATA_FILE)

def save_daily_data(data):
    """
    Save daily tracking data.
    
    Args:
        data (dict): Daily tracking data to save.
    """
    save_data(data, DAILY_DATA_FILE)

def load_weekly_data():
    """
    Load weekly tracking data.
    
    Returns:
        dict: Weekly tracking data.
    """
    return load_data(WEEKLY_DATA_FILE)

def save_weekly_data(data):
    """
    Save weekly tracking data.
    
    Args:
        data (dict): Weekly tracking data to save.
    """
    save_data(data, WEEKLY_DATA_FILE)
