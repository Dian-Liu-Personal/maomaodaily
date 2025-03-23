"""
Data management utilities for loading and saving application data.
"""

import os
import json
import streamlit as st
from config.settings import DATA_DIR, DAILY_DATA_FILE, WEEKLY_DATA_FILE

# Import Gist manager
try:
    from utils.gist_manager import (
        load_daily_data as gist_load_daily_data,
        save_daily_data as gist_save_daily_data,
        load_weekly_data as gist_load_weekly_data,
        save_weekly_data as gist_save_weekly_data,
        initialize_gist_config
    )
    GIST_AVAILABLE = True
except ImportError:
    GIST_AVAILABLE = False

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

# Original local file system functions
def load_daily_data_local():
    """
    Load daily tracking data from local file system.
    
    Returns:
        dict: Daily tracking data.
    """
    return load_data(DAILY_DATA_FILE)

def save_daily_data_local(data):
    """
    Save daily tracking data to local file system.
    
    Args:
        data (dict): Daily tracking data to save.
    """
    save_data(data, DAILY_DATA_FILE)

def load_weekly_data_local():
    """
    Load weekly tracking data from local file system.
    
    Returns:
        dict: Weekly tracking data.
    """
    return load_data(WEEKLY_DATA_FILE)

def save_weekly_data_local(data):
    """
    Save weekly tracking data to local file system.
    
    Args:
        data (dict): Weekly tracking data to save.
    """
    save_data(data, WEEKLY_DATA_FILE)

# Hybrid functions that try Gist first, then fall back to local
def load_daily_data():
    """
    Load daily tracking data, trying Gist first, then falling back to local.
    
    Returns:
        dict: Daily tracking data.
    """
    if GIST_AVAILABLE and initialize_gist_config():
        try:
            data = gist_load_daily_data()
            if data:  # If we got data from Gist, use it
                # Also save to local file system for backup
                save_daily_data_local(data)
                return data
        except Exception as e:
            st.warning(f"Failed to load data from Gist, falling back to local: {str(e)}")
    
    # Fall back to local file system
    return load_daily_data_local()

def save_daily_data(data):
    """
    Save daily tracking data to Gist and local file system.
    
    Args:
        data (dict): Daily tracking data to save.
    """
    # Always save to local file system
    save_daily_data_local(data)
    
    # Try to save to Gist if available
    if GIST_AVAILABLE and initialize_gist_config():
        try:
            gist_save_daily_data(data)
        except Exception as e:
            st.warning(f"Failed to save data to Gist: {str(e)}")

def load_weekly_data():
    """
    Load weekly tracking data, trying Gist first, then falling back to local.
    
    Returns:
        dict: Weekly tracking data.
    """
    if GIST_AVAILABLE and initialize_gist_config():
        try:
            data = gist_load_weekly_data()
            if data:  # If we got data from Gist, use it
                # Also save to local file system for backup
                save_weekly_data_local(data)
                return data
        except Exception as e:
            st.warning(f"Failed to load data from Gist, falling back to local: {str(e)}")
    
    # Fall back to local file system
    return load_weekly_data_local()

def save_weekly_data(data):
    """
    Save weekly tracking data to Gist and local file system.
    
    Args:
        data (dict): Weekly tracking data to save.
    """
    # Always save to local file system
    save_weekly_data_local(data)
    
    # Try to save to Gist if available
    if GIST_AVAILABLE and initialize_gist_config():
        try:
            gist_save_weekly_data(data)
        except Exception as e:
            st.warning(f"Failed to save data to Gist: {str(e)}")