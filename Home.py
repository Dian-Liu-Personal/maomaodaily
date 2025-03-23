"""
Activity Tracker - Main Application

This is the main entry point for the Activity Tracker application.
"""

import streamlit as st
import os
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT
from utils.ui_components import render_header
from utils.data_manager import ensure_data_directory
from summary_dashboard import render_activity_dashboard

def setup_app():
    """
    Setup the application by configuring Streamlit, creating necessary
    directories, and setting theme.
    """
    # Configure Streamlit page
    st.set_page_config(
        page_title=f"{APP_ICON} {APP_TITLE}",
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Apply custom CSS if available
    if os.path.exists("static/styles.css"):
        with open("static/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
def main():
    """
    Main application function that sets up and runs the app.
    """
    # Initialize the app
    setup_app()
    
    # Home page is automatically loaded by Streamlit
    render_header(APP_TITLE)
    
    # st.write("""
    # 欢迎来到猫猫日历
    # """)
    
    # # Add Getting Started section
    # st.subheader("Getting Started")
    # st.markdown("""
    # 1. Use the **Daily Check-in** page to track your daily activities and metrics
    # 2. Use the **Weekly Check-in** page for your weekly measurements and activities
    # 3. View your progress and trends on both pages
    # """)
    
    # # Navigation in the sidebar
    # st.sidebar.title("Navigation")
    # st.sidebar.info("""
    # Select a page from the dropdown above to navigate to different sections of the app.
    # """)
    
    # Show app info in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{APP_TITLE}** v1.0.0")
    st.sidebar.markdown("Track your daily and weekly activities to improve your habits.")

    render_activity_dashboard()

if __name__ == "__main__":
    main()
