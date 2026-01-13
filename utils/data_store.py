import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_data_dir():
    """Ensure the data directory exists"""
    DATA_DIR.mkdir(exist_ok=True)


def get_history_file():
    """Get path to history file"""
    ensure_data_dir()
    return DATA_DIR / "history.json"


def get_favorites_file():
    """Get path to favorites file"""
    ensure_data_dir()
    return DATA_DIR / "favorites.json"


def load_history():
    """
    Load meal history from JSON file.

    Returns:
        dict: History data with dates as keys, each containing meals list and totals
    """
    history_file = get_history_file()

    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_history(history):
    """
    Save meal history to JSON file.

    Args:
        history: dict with dates as keys
    """
    history_file = get_history_file()

    try:
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        print(f"Error saving history: {e}")


def save_day_to_history(date_str, meals, goals):
    """
    Save a day's meals to history.

    Args:
        date_str: Date string in format 'YYYY-MM-DD'
        meals: List of meal dictionaries
        goals: Goals dictionary
    """
    history = load_history()

    # Calculate totals
    totals = {
        'calories': sum(m['calories'] for m in meals),
        'protein': sum(m['protein'] for m in meals),
        'carbs': sum(m['carbs'] for m in meals),
        'fat': sum(m['fat'] for m in meals)
    }

    history[date_str] = {
        'meals': meals,
        'totals': totals,
        'goals': goals,
        'meal_count': len(meals)
    }

    save_history(history)


def get_recent_history(days=7):
    """
    Get history for the last N days.

    Args:
        days: Number of days to retrieve (default 7)

    Returns:
        list: List of tuples (date_str, day_data) sorted by date descending
    """
    history = load_history()
    today = datetime.now().date()

    recent = []
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        if date_str in history:
            recent.append((date_str, history[date_str]))
        else:
            # Include empty day placeholder
            recent.append((date_str, {
                'meals': [],
                'totals': {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0},
                'goals': None,
                'meal_count': 0
            }))

    return recent


def load_favorites():
    """
    Load favorite meals from JSON file.

    Returns:
        list: List of favorite meal dictionaries
    """
    favorites_file = get_favorites_file()

    if favorites_file.exists():
        try:
            with open(favorites_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_favorites(favorites):
    """
    Save favorites to JSON file.

    Args:
        favorites: List of favorite meal dictionaries
    """
    favorites_file = get_favorites_file()

    try:
        with open(favorites_file, 'w') as f:
            json.dump(favorites, f, indent=2)
    except IOError as e:
        print(f"Error saving favorites: {e}")


def add_favorite(meal):
    """
    Add a meal to favorites.

    Args:
        meal: Meal dictionary with description, calories, protein, carbs, fat

    Returns:
        bool: True if added, False if already exists
    """
    favorites = load_favorites()

    # Check if already exists (by description)
    for fav in favorites:
        if fav['description'].lower() == meal['description'].lower():
            return False

    favorite = {
        'id': datetime.now().isoformat(),
        'description': meal['description'],
        'calories': meal['calories'],
        'protein': meal['protein'],
        'carbs': meal['carbs'],
        'fat': meal['fat'],
        'added_date': datetime.now().strftime('%Y-%m-%d')
    }

    favorites.append(favorite)
    save_favorites(favorites)
    return True


def remove_favorite(favorite_id):
    """
    Remove a favorite by ID.

    Args:
        favorite_id: ID of favorite to remove

    Returns:
        bool: True if removed, False if not found
    """
    favorites = load_favorites()

    for i, fav in enumerate(favorites):
        if fav['id'] == favorite_id:
            favorites.pop(i)
            save_favorites(favorites)
            return True

    return False


def export_history_to_csv(days=30):
    """
    Export history to CSV format.

    Args:
        days: Number of days to export

    Returns:
        str: CSV content as string
    """
    history = get_recent_history(days)

    lines = ['Date,Meals,Calories,Protein (g),Carbs (g),Fat (g),Calorie Goal,Goal %']

    for date_str, day_data in history:
        totals = day_data['totals']
        goals = day_data.get('goals') or {}
        cal_goal = goals.get('calories', 0)
        goal_pct = (totals['calories'] / cal_goal * 100) if cal_goal > 0 else 0

        line = f"{date_str},{day_data['meal_count']},{int(totals['calories'])},{int(totals['protein'])},{int(totals['carbs'])},{int(totals['fat'])},{cal_goal},{goal_pct:.1f}"
        lines.append(line)

    return '\n'.join(lines)
