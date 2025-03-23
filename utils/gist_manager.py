"""
Gist-based data management utilities for loading and saving application data.
"""

import os
import json
import requests
import streamlit as st

# GitHub Gist ID and Personal Access Token
# These will be set from environment variables or Streamlit secrets
GIST_ID = None
GITHUB_TOKEN = None

def initialize_gist_config():
    """
    Initialize Gist configuration from environment variables or Streamlit secrets.
    """
    global GIST_ID, GITHUB_TOKEN
    
    # Try to get from environment variables first
    GIST_ID = os.environ.get("GIST_ID")
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    
    # If not found in environment variables, try Streamlit secrets
    if not GIST_ID or not GITHUB_TOKEN:
        try:
            GIST_ID = st.secrets["gist"]["id"]
            GITHUB_TOKEN = st.secrets["gist"]["token"]
        except Exception:
            st.error("GitHub Gist credentials not found. Please set GIST_ID and GITHUB_TOKEN in environment variables or Streamlit secrets.")
            return False
    
    return True

def load_data_from_gist(filename):
    """
    Load data from a file in GitHub Gist.
    
    Args:
        filename (str): Name of the file to load.
        
    Returns:
        dict: The loaded data, or an empty dict if loading fails.
    """
    if not initialize_gist_config():
        return {}
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    
    try:
        response = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers=headers
        )
        response.raise_for_status()
        
        gist_data = response.json()
        if filename in gist_data["files"]:
            file_content = gist_data["files"][filename]["content"]
            return json.loads(file_content)
        else:
            st.warning(f"File {filename} not found in Gist. Starting with empty data.")
            return {}
    except Exception as e:
        st.error(f"Error loading data from Gist: {str(e)}")
        return {}

def save_data_to_gist(data, filename):
    """
    Save data to a file in GitHub Gist.
    
    Args:
        data (dict): Data to save.
        filename (str): Name of the file to save to.
        
    Returns:
        bool: True if saving was successful, False otherwise.
    """
    if not initialize_gist_config():
        return False
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    
    # First, get the current gist to avoid overwriting other files
    try:
        response = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers=headers
        )
        response.raise_for_status()
        
        # Prepare the update data
        gist_data = response.json()
        files_data = {}
        
        # Include all existing files in the update
        for file_name, file_info in gist_data["files"].items():
            if file_name != filename:  # Skip the file we're updating
                files_data[file_name] = {"content": file_info["content"]}
        
        # Add our updated file
        files_data[filename] = {"content": json.dumps(data, indent=2)}
        
        # Update the gist
        update_data = {
            "files": files_data
        }
        
        update_response = requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers=headers,
            json=update_data
        )
        update_response.raise_for_status()
        return True
    
    except Exception as e:
        st.error(f"Error saving data to Gist: {str(e)}")
        return False

def load_daily_data():
    """
    Load daily tracking data from Gist.
    
    Returns:
        dict: Daily tracking data.
    """
    return load_data_from_gist("daily_data.json")

def save_daily_data(data):
    """
    Save daily tracking data to Gist.
    
    Args:
        data (dict): Daily tracking data to save.
    """
    return save_data_to_gist(data, "daily_data.json")

def load_weekly_data():
    """
    Load weekly tracking data from Gist.
    
    Returns:
        dict: Weekly tracking data.
    """
    return load_data_from_gist("weekly_data.json")

def save_weekly_data(data):
    """
    Save weekly tracking data to Gist.
    
    Args:
        data (dict): Weekly tracking data to save.
    """
    return save_data_to_gist(data, "weekly_data.json")

# For local development: implement fallback to local file system
def load_data_with_fallback(filename, load_from_gist_func, load_from_local_func):
    """
    Attempt to load data from Gist, falling back to local file system if needed.
    
    Args:
        filename (str): Name of the file to load.
        load_from_gist_func (callable): Function to load from Gist.
        load_from_local_func (callable): Function to load from local file system.
        
    Returns:
        dict: The loaded data.
    """
    # Try loading from Gist first
    try:
        if initialize_gist_config():
            data = load_from_gist_func()
            # If we got data from Gist, return it
            if data:
                return data
    except Exception:
        pass
        
    # If Gist loading failed or returned empty data, try local file system
    return load_from_local_func()

def save_data_with_fallback(data, filename, save_to_gist_func, save_to_local_func):
    """
    Attempt to save data to Gist, falling back to local file system if needed.
    
    Args:
        data (dict): Data to save.
        filename (str): Name of the file to save to.
        save_to_gist_func (callable): Function to save to Gist.
        save_to_local_func (callable): Function to save to local file system.
        
    Returns:
        bool: True if saving was successful in either location.
    """
    success = False
    
    # Try saving to Gist first
    try:
        if initialize_gist_config():
            if save_to_gist_func(data):
                success = True
    except Exception:
        pass
        
    # Also save to local file system for backup
    try:
        save_to_local_func(data)
        # If Gist failed but local succeeded, mark as success
        success = True
    except Exception:
        # If both failed, we'll return False
        pass
        
    return success
