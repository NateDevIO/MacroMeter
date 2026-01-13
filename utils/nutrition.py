"""Nutrition calculation utilities"""


def calculate_totals(meals):
    """
    Sum all macros from a list of meals.

    Args:
        meals: List of meal dictionaries

    Returns:
        dict: Totals for calories, protein, carbs, fat
    """
    if not meals:
        return {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}

    return {
        'calories': sum(m.get('calories', 0) for m in meals),
        'protein': sum(m.get('protein', 0) for m in meals),
        'carbs': sum(m.get('carbs', 0) for m in meals),
        'fat': sum(m.get('fat', 0) for m in meals)
    }


def calculate_remaining(goals, totals):
    """
    Calculate remaining macros.

    Args:
        goals: Goals dictionary
        totals: Current totals dictionary

    Returns:
        dict: Remaining for each macro
    """
    return {k: goals[k] - totals[k] for k in goals}


def calculate_per_serving(total_nutrition, servings):
    """
    Calculate nutrition per serving for recipe mode.

    Args:
        total_nutrition: dict with total calories, protein, carbs, fat
        servings: Number of servings (int)

    Returns:
        dict: Nutrition per serving
    """
    if servings <= 0:
        servings = 1

    return {
        'calories': total_nutrition['calories'] / servings,
        'protein': total_nutrition['protein'] / servings,
        'carbs': total_nutrition['carbs'] / servings,
        'fat': total_nutrition['fat'] / servings
    }


def calculate_macro_percentages(totals):
    """
    Calculate percentage breakdown of macros by calories.

    Args:
        totals: dict with protein, carbs, fat in grams

    Returns:
        dict: Percentages and calorie values for each macro
    """
    protein_cals = totals['protein'] * 4
    carbs_cals = totals['carbs'] * 4
    fat_cals = totals['fat'] * 9
    total_cals = protein_cals + carbs_cals + fat_cals

    if total_cals == 0:
        return {
            'protein': {'grams': 0, 'calories': 0, 'percentage': 0},
            'carbs': {'grams': 0, 'calories': 0, 'percentage': 0},
            'fat': {'grams': 0, 'calories': 0, 'percentage': 0}
        }

    return {
        'protein': {
            'grams': totals['protein'],
            'calories': protein_cals,
            'percentage': (protein_cals / total_cals) * 100
        },
        'carbs': {
            'grams': totals['carbs'],
            'calories': carbs_cals,
            'percentage': (carbs_cals / total_cals) * 100
        },
        'fat': {
            'grams': totals['fat'],
            'calories': fat_cals,
            'percentage': (fat_cals / total_cals) * 100
        }
    }


def get_goal_status(current, goal):
    """
    Determine status relative to goal.

    Args:
        current: Current value
        goal: Goal value

    Returns:
        tuple: (status string, percentage, color)
    """
    if goal <= 0:
        return ('no_goal', 0, '#95A5A6')

    percentage = current / goal

    if percentage <= 0.8:
        return ('on_track', percentage, '#2ECC71')  # Green
    elif percentage <= 1.0:
        return ('near_goal', percentage, '#FFD93D')  # Yellow
    else:
        return ('over_goal', percentage, '#FF6B6B')  # Red


def format_nutrition_summary(nutrition):
    """
    Format nutrition data as a readable summary string.

    Args:
        nutrition: dict with calories, protein, carbs, fat

    Returns:
        str: Formatted summary
    """
    return (
        f"{int(nutrition['calories'])} cal | "
        f"{int(nutrition['protein'])}g protein | "
        f"{int(nutrition['carbs'])}g carbs | "
        f"{int(nutrition['fat'])}g fat"
    )
