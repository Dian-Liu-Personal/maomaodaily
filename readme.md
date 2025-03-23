# Activity Tracker

## Overview

Activity Tracker is a personal productivity and health tracking application built with Streamlit. It allows users to record, visualize, and analyze their daily and weekly activities, helping them build better habits and track their progress over time.

## Features

- **Daily Activity Tracking**: Record daily metrics like weight, calories, and completion of various activities
- **Weekly Check-ins**: Track weekly measurements and activities
- **Dashboard**: Get a quick overview of your current status and recent history
- **Data Visualization**: View trends and statistics through charts and tables
- **Calendar Interface**: Select dates through an intuitive calendar interface

## Project Structure

```
activity_tracker/
│
├── app.py                 # Main entry point for the application
│
├── pages/                 # Streamlit pages
│   ├── Home.py            # Home page/dashboard
│   ├── Daily.py           # Daily tracking page
│   └── Weekly.py          # Weekly tracking page
│
├── utils/                 # Utility modules
│   ├── __init__.py        # Package initialization
│   ├── data_manager.py    # Data loading/saving functions
│   ├── date_utils.py      # Date handling utilities
│   └── ui_components.py   # Reusable UI components
│
├── config/                # Configuration
│   ├── __init__.py        # Package initialization
│   └── settings.py        # Application settings
│
├── static/                # Static assets
│   └── styles.css         # Custom CSS styles
│
├── data/                  # Data storage (created at runtime)
│   ├── daily_data.json    # Daily tracking data
│   └── weekly_data.json   # Weekly tracking data
│
└── README.md              # This documentation file
```

## How It Works

### Module Responsibilities

1. **app.py**
   - Entry point for the application
   - Sets up the application environment
   - Configures Streamlit settings
   - Renders the home page if directly accessed

2. **pages/Home.py**
   - Displays the dashboard with current status
   - Shows activity history for the past 7 days and 4 weeks
   - Provides quick navigation to daily and weekly check-ins

3. **pages/Daily.py**
   - Allows selection of a specific date through a calendar interface
   - Displays a weekly view of activities
   - Provides a form to record daily activities and metrics
   - Shows statistics and trends for daily data

4. **pages/Weekly.py**
   - Allows selection of a specific week
   - Shows a month calendar with the selected week highlighted
   - Summarizes daily activities for the selected week
   - Provides a form to record weekly measurements and activities
   - Displays statistics and trends for weekly data

5. **utils/data_manager.py**
   - Handles loading and saving data to JSON files
   - Ensures data directory exists
   - Provides functions to access daily and weekly data

6. **utils/date_utils.py**
   - Provides utilities for date manipulation and formatting
   - Functions to get week dates, month calendars, etc.
   - Helpers for date parsing and formatting

7. **utils/ui_components.py**
   - Contains reusable UI components
   - Renders calendars, metric cards, progress bars, etc.
   - Maintains consistent styling across the application

8. **config/settings.py**
   - Stores application-wide settings
   - Defines activity types and display formats
   - Centralizes configuration for easy updates

### Data Flow

1. User interactions are handled through Streamlit's interface
2. Data is stored in JSON files within the `data/` directory:
   - `daily_data.json` - Indexed by ISO date strings (e.g., "2023-03-22")
   - `weekly_data.json` - Indexed by the ISO date string of each week's Monday
3. Data is loaded at the start of each page and saved when forms are submitted
4. Visualizations are generated from the processed data

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/yourusername/activity-tracker.git
   cd activity-tracker
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   
   Or install them manually:
   ```
   pip install streamlit pandas
   ```

### Running the Application

1. Start the Streamlit server:
   ```
   streamlit run app.py
   ```

2. The application will open in your default web browser. If it doesn't, navigate to the URL displayed in the terminal (typically http://localhost:8501).

## Customization

### Adding New Activities

To add new activity types, edit the `config/settings.py` file:

```python
# Add to DAILY_ACTIVITIES list
DAILY_ACTIVITIES = [
    # Existing activities...
    {"id": "new_activity", "name": "New Activity Name"},
]

# Add to WEEKLY_ACTIVITIES list
WEEKLY_ACTIVITIES = [
    # Existing activities...
    {"id": "new_weekly_activity", "name": "New Weekly Activity Name"},
]
```

### Styling

The application styling can be customized by editing the `static/styles.css` file. The styles are automatically applied when the application starts.

## Data Storage

All data is stored locally in JSON files in the `data/` directory:

- `data/daily_data.json`: Contains all daily tracking information
- `data/weekly_data.json`: Contains all weekly tracking information

The data is structured as follows:

### Daily Data Format

```json
{
  "2023-03-22": {
    "weight": 70.5,
    "calories": 2000,
    "workout": true,
    "tabletennis": false,
    "tv_shows": true,
    "dog_walking": true,
    "reading": false,
    "friends": true,
    "doi": false,
    "notes": "Felt good today!"
  },
  "2023-03-23": {
    // Another day's data...
  }
}
```

### Weekly Data Format

```json
{
  "2023-03-20": {
    "waist": 80.5,
    "housework": true,
    "eating_out": false,
    "notes": "Productive week!"
  },
  "2023-03-27": {
    // Another week's data...
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Inspired by habit tracking and personal analytics applications