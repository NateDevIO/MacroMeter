"""
MacroMeter - Daily Macro Nutrition Tracker
A Streamlit application for tracking daily nutrition with natural language food input.

Coded by Nate
"""

import streamlit as st
from utils.api_client import NutritionixClient
from utils.visualization import create_macro_pie_chart, create_daily_bar_chart
from utils.data_store import (
    load_favorites, add_favorite, remove_favorite,
    save_day_to_history, get_recent_history, export_history_to_csv
)
from utils.nutrition import calculate_per_serving
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="MacroMeter",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Progress bar color overrides */
    .stProgress > div > div > div > div {
        background-color: #4ECDC4;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }

    /* Card-like containers */
    .meal-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #4ECDC4;
    }

    /* Favorite button styling */
    .favorite-btn {
        background-color: #FFD93D;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }

    /* History table styling */
    .history-good {
        color: #2ECC71;
    }

    .history-over {
        color: #FF6B6B;
    }

    /* Header styling */
    h1 {
        color: #2c3e50;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'goals' not in st.session_state:
    st.session_state.goals = {
        'calories': 2000,
        'protein': 150,
        'carbs': 250,
        'fat': 65
    }

if 'meals' not in st.session_state:
    st.session_state.meals = []

if 'pending_meal' not in st.session_state:
    st.session_state.pending_meal = None

if 'show_api_help' not in st.session_state:
    st.session_state.show_api_help = False

if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = None

if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now().strftime('%Y-%m-%d')

# Initialize API client with caching to ensure stable initialization
@st.cache_resource
def get_api_client():
    """Create a cached API client instance"""
    return NutritionixClient()

api_client = get_api_client()


def calculate_totals():
    """Sum all macros from logged meals"""
    if not st.session_state.meals:
        return {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}

    return {
        'calories': sum(m['calories'] for m in st.session_state.meals),
        'protein': sum(m['protein'] for m in st.session_state.meals),
        'carbs': sum(m['carbs'] for m in st.session_state.meals),
        'fat': sum(m['fat'] for m in st.session_state.meals)
    }


def calculate_remaining(goals, totals):
    """Calculate remaining macros"""
    return {k: goals[k] - totals[k] for k in goals}


def format_macro_display(current, goal, unit=""):
    """Format macro display with color coding"""
    percentage = current / goal if goal > 0 else 0
    remaining = goal - current

    if remaining >= 0:
        return f"{int(current)}{unit} / {goal}{unit}", f"{int(remaining)}{unit} remaining", "normal"
    else:
        return f"{int(current)}{unit} / {goal}{unit}", f"{int(abs(remaining))}{unit} over", "inverse"


def save_current_day():
    """Save current day's meals to history"""
    if st.session_state.meals:
        today = datetime.now().strftime('%Y-%m-%d')
        save_day_to_history(today, st.session_state.meals, st.session_state.goals)


def add_meal_from_favorite(fav):
    """Add a favorite meal to today's log"""
    meal = {
        'id': datetime.now().isoformat(),
        'description': fav['description'],
        'calories': fav['calories'],
        'protein': fav['protein'],
        'carbs': fav['carbs'],
        'fat': fav['fat'],
        'timestamp': datetime.now().strftime("%I:%M %p")
    }
    st.session_state.meals.append(meal)
    save_current_day()


# Title and description
st.title("🍎 MacroMeter")
st.markdown("*Track your nutrition goals with natural language meal entry*")

# Sidebar for goals
with st.sidebar:
    st.header("⚙️ Daily Goals")
    st.caption("Set your personalized nutrition targets")

    st.divider()

    goals_calories = st.number_input(
        "🔥 Calories",
        min_value=1000,
        max_value=5000,
        value=st.session_state.goals['calories'],
        step=50,
        help="Recommended: 1500-2500 for most adults"
    )
    goals_protein = st.number_input(
        "🥩 Protein (g)",
        min_value=0,
        max_value=500,
        value=st.session_state.goals['protein'],
        step=5,
        help="Recommended: 0.8-1g per pound of body weight"
    )
    goals_carbs = st.number_input(
        "🍞 Carbs (g)",
        min_value=0,
        max_value=500,
        value=st.session_state.goals['carbs'],
        step=5,
        help="Recommended: 45-65% of daily calories"
    )
    goals_fat = st.number_input(
        "🥑 Fat (g)",
        min_value=0,
        max_value=300,
        value=st.session_state.goals['fat'],
        step=5,
        help="Recommended: 20-35% of daily calories"
    )

    if st.button("💾 Update Goals", type="primary", use_container_width=True):
        st.session_state.goals = {
            'calories': goals_calories,
            'protein': goals_protein,
            'carbs': goals_carbs,
            'fat': goals_fat
        }
        st.success("Goals updated!")
        st.rerun()

    st.divider()

    # Quick actions
    st.header("🚀 Quick Actions")

    if st.session_state.meals:
        if st.button("💾 Save Day to History", use_container_width=True):
            save_current_day()
            st.success("Day saved to history!")

        if st.button("🗑️ Clear All Meals", use_container_width=True):
            st.session_state.meals = []
            st.rerun()

        st.caption(f"📊 {len(st.session_state.meals)} meal(s) logged today")

# Calculate current totals
totals = calculate_totals()
goals = st.session_state.goals
remaining = calculate_remaining(goals, totals)

# Progress Dashboard
st.header("📊 Today's Progress")

col1, col2, col3, col4 = st.columns(4)

metrics = [
    ('calories', 'Calories', '', col1),
    ('protein', 'Protein', 'g', col2),
    ('carbs', 'Carbs', 'g', col3),
    ('fat', 'Fat', 'g', col4)
]

for key, label, unit, col in metrics:
    with col:
        value, delta, delta_color = format_macro_display(
            totals[key], goals[key], unit
        )
        st.metric(label, value, delta=delta, delta_color=delta_color)

        pct = totals[key] / goals[key] if goals[key] > 0 else 0
        st.progress(min(pct, 1.0))

st.divider()

# Main content with tabs
tab_add, tab_favorites, tab_recipe, tab_history = st.tabs([
    "🍽️ Add Meal",
    "⭐ Favorites",
    "📖 Recipe Mode",
    "📅 History"
])

# ==================== TAB 1: ADD MEAL ====================
with tab_add:
    # Show API setup help if needed
    if st.session_state.show_api_help:
        with st.expander("🔑 API Setup Instructions", expanded=True):
            st.markdown("""
            ### How to get your USDA FoodData Central API key:

            1. Go to [USDA API Signup](https://fdc.nal.usda.gov/api-key-signup.html)
            2. Enter your email and name
            3. Check your email for the API key (instant)
            4. Add it to the `.env` file in the project directory:

            ```
            USDA_API_KEY=your_api_key_here
            ```

            5. Restart the Streamlit app
            """)
            if st.button("Got it, hide this"):
                st.session_state.show_api_help = False
                st.rerun()

    meal_input = st.text_input(
        "Describe your meal in plain English",
        placeholder="e.g., 2 scrambled eggs, a banana, and a cup of coffee",
        key="meal_input",
        help="Try natural descriptions like '1 chicken breast with rice' or 'large pepperoni pizza slice'"
    )

    col_btn1, col_btn2 = st.columns([1, 4])

    with col_btn1:
        search_clicked = st.button("🔍 Look Up", type="primary", use_container_width=True)

    # Handle meal lookup
    if search_clicked:
        if meal_input:
            if len(meal_input) > 200:
                st.warning("⚠️ Long descriptions may affect accuracy. Consider breaking into smaller entries.")

            with st.spinner("🔄 Fetching nutrition data..."):
                nutrition = api_client.get_nutrition(meal_input)

                if "error" in nutrition:
                    st.error(f"❌ {nutrition['error']}")
                    if "credentials" in nutrition['error'].lower() or "authentication" in nutrition['error'].lower():
                        st.session_state.show_api_help = True
                        st.rerun()
                else:
                    # Store as pending meal for confirmation
                    st.session_state.pending_meal = {
                        'description': meal_input,
                        'calories': nutrition['calories'],
                        'protein': nutrition['protein'],
                        'carbs': nutrition['carbs'],
                        'fat': nutrition['fat']
                    }
                    st.rerun()
        else:
            st.warning("⚠️ Please enter a meal description")

    # Show pending meal for confirmation
    if st.session_state.pending_meal:
        pending = st.session_state.pending_meal

        st.info("📋 **Review nutrition data before adding:**")

        preview_cols = st.columns(5)
        with preview_cols[0]:
            st.metric("Food", pending['description'][:25] + "..." if len(pending['description']) > 25 else pending['description'])
        with preview_cols[1]:
            st.metric("Calories", f"{int(pending['calories'])}")
        with preview_cols[2]:
            st.metric("Protein", f"{int(pending['protein'])}g")
        with preview_cols[3]:
            st.metric("Carbs", f"{int(pending['carbs'])}g")
        with preview_cols[4]:
            st.metric("Fat", f"{int(pending['fat'])}g")

        # Warning for high calorie meals
        if pending['calories'] > 2000:
            st.warning(f"⚠️ This meal has {int(pending['calories'])} calories. Please verify this is correct.")

        confirm_cols = st.columns([1, 1, 1, 2])
        with confirm_cols[0]:
            if st.button("✅ Add Meal", type="primary", use_container_width=True):
                meal = {
                    'id': datetime.now().isoformat(),
                    'description': pending['description'],
                    'calories': pending['calories'],
                    'protein': pending['protein'],
                    'carbs': pending['carbs'],
                    'fat': pending['fat'],
                    'timestamp': datetime.now().strftime("%I:%M %p")
                }
                st.session_state.meals.append(meal)
                save_current_day()
                st.session_state.pending_meal = None
                st.success(f"✅ Added: {pending['description']}")
                st.rerun()

        with confirm_cols[1]:
            if st.button("⭐ Add & Save Favorite", use_container_width=True):
                meal = {
                    'id': datetime.now().isoformat(),
                    'description': pending['description'],
                    'calories': pending['calories'],
                    'protein': pending['protein'],
                    'carbs': pending['carbs'],
                    'fat': pending['fat'],
                    'timestamp': datetime.now().strftime("%I:%M %p")
                }
                st.session_state.meals.append(meal)
                save_current_day()
                if add_favorite(pending):
                    st.success(f"✅ Added meal and saved to favorites!")
                else:
                    st.success(f"✅ Added meal (already in favorites)")
                st.session_state.pending_meal = None
                st.rerun()

        with confirm_cols[2]:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.pending_meal = None
                st.rerun()

# ==================== TAB 2: FAVORITES ====================
with tab_favorites:
    st.subheader("⭐ Quick Add from Favorites")
    st.caption("Click any favorite to instantly add it to today's log")

    favorites = load_favorites()

    if favorites:
        # Display favorites in a grid
        cols = st.columns(2)
        for idx, fav in enumerate(favorites):
            with cols[idx % 2]:
                with st.container():
                    col_info, col_actions = st.columns([3, 1])

                    with col_info:
                        st.markdown(f"**{fav['description']}**")
                        st.caption(
                            f"🔥 {int(fav['calories'])} cal • "
                            f"🥩 {int(fav['protein'])}g • "
                            f"🍞 {int(fav['carbs'])}g • "
                            f"🥑 {int(fav['fat'])}g"
                        )

                    with col_actions:
                        if st.button("➕ Add", key=f"add_fav_{idx}", use_container_width=True):
                            add_meal_from_favorite(fav)
                            st.success(f"Added {fav['description']}")
                            st.rerun()

                        if st.button("🗑️", key=f"del_fav_{idx}", help="Remove from favorites"):
                            remove_favorite(fav['id'])
                            st.rerun()

                    st.divider()
    else:
        st.info("⭐ No favorites yet! Add meals and click 'Add & Save Favorite' to save them here for quick access.")

# ==================== TAB 3: RECIPE MODE ====================
with tab_recipe:
    st.subheader("📖 Recipe Mode")
    st.caption("Paste a list of ingredients to calculate nutrition per serving")

    recipe_input = st.text_area(
        "Enter recipe ingredients (one per line or comma-separated)",
        placeholder="Example:\n2 cups flour\n3 eggs\n1 cup milk\n1/2 cup sugar\n1/4 cup butter",
        height=150,
        key="recipe_input"
    )

    col_servings, col_calc = st.columns([1, 2])

    with col_servings:
        num_servings = st.number_input(
            "Number of servings",
            min_value=1,
            max_value=50,
            value=4,
            step=1
        )

    with col_calc:
        st.write("")  # Spacing
        st.write("")
        calc_recipe = st.button("🔢 Calculate Per Serving", type="primary")

    if calc_recipe:
        if recipe_input.strip():
            with st.spinner("🔄 Analyzing recipe ingredients..."):
                # Send entire recipe to API
                nutrition = api_client.get_nutrition(recipe_input)

                if "error" in nutrition:
                    st.error(f"❌ {nutrition['error']}")
                else:
                    # Calculate per serving
                    per_serving = calculate_per_serving(nutrition, num_servings)

                    st.session_state.recipe_result = {
                        'total': nutrition,
                        'per_serving': per_serving,
                        'servings': num_servings,
                        'recipe': recipe_input
                    }
                    st.rerun()
        else:
            st.warning("⚠️ Please enter recipe ingredients")

    # Show recipe results
    if st.session_state.recipe_result:
        result = st.session_state.recipe_result

        st.success(f"✅ Recipe analyzed for {result['servings']} servings")

        col_total, col_serving = st.columns(2)

        with col_total:
            st.markdown("### 📊 Total Recipe")
            total = result['total']
            st.metric("Calories", f"{int(total['calories'])}")
            st.metric("Protein", f"{int(total['protein'])}g")
            st.metric("Carbs", f"{int(total['carbs'])}g")
            st.metric("Fat", f"{int(total['fat'])}g")

        with col_serving:
            st.markdown("### 🍽️ Per Serving")
            serving = result['per_serving']
            st.metric("Calories", f"{int(serving['calories'])}")
            st.metric("Protein", f"{int(serving['protein'])}g")
            st.metric("Carbs", f"{int(serving['carbs'])}g")
            st.metric("Fat", f"{int(serving['fat'])}g")

        st.divider()

        action_cols = st.columns([1, 1, 2])

        with action_cols[0]:
            if st.button("➕ Add 1 Serving to Log", type="primary", use_container_width=True):
                serving = result['per_serving']
                meal = {
                    'id': datetime.now().isoformat(),
                    'description': f"Recipe serving (1/{result['servings']})",
                    'calories': serving['calories'],
                    'protein': serving['protein'],
                    'carbs': serving['carbs'],
                    'fat': serving['fat'],
                    'timestamp': datetime.now().strftime("%I:%M %p")
                }
                st.session_state.meals.append(meal)
                save_current_day()
                st.success("Added 1 serving to today's log!")
                st.rerun()

        with action_cols[1]:
            if st.button("🔄 Clear Result", use_container_width=True):
                st.session_state.recipe_result = None
                st.rerun()

# ==================== TAB 4: HISTORY ====================
with tab_history:
    st.subheader("📅 Meal History")
    st.caption("View your nutrition tracking over the past week")

    history = get_recent_history(7)

    if any(day[1]['meal_count'] > 0 for day in history):
        # Create summary table
        history_data = []
        for date_str, day_data in history:
            # Format date nicely
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_str == datetime.now().strftime('%Y-%m-%d'):
                date_display = "Today"
            elif date_str == (datetime.now().replace(day=datetime.now().day - 1)).strftime('%Y-%m-%d'):
                date_display = "Yesterday"
            else:
                date_display = date_obj.strftime('%a, %b %d')

            totals = day_data['totals']
            goals_data = day_data.get('goals') or {}
            goal = goals_data.get('calories', 2000) or 2000
            pct = (totals['calories'] / goal * 100) if goal > 0 else 0

            history_data.append({
                'Date': date_display,
                'Meals': day_data['meal_count'],
                'Calories': int(totals['calories']),
                'Protein': f"{int(totals['protein'])}g",
                'Carbs': f"{int(totals['carbs'])}g",
                'Fat': f"{int(totals['fat'])}g",
                'Goal %': f"{pct:.0f}%"
            })

        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export option
        st.divider()
        col_export, col_spacer = st.columns([1, 3])
        with col_export:
            csv_data = export_history_to_csv(30)
            st.download_button(
                label="📥 Export Last 30 Days (CSV)",
                data=csv_data,
                file_name=f"nutrition_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Detailed view for a selected day
        st.divider()
        st.markdown("### 📋 Day Details")

        selected_day = st.selectbox(
            "Select a day to view details",
            options=[h[0] for h in history if h[1]['meal_count'] > 0],
            format_func=lambda x: "Today" if x == datetime.now().strftime('%Y-%m-%d') else datetime.strptime(x, '%Y-%m-%d').strftime('%A, %B %d')
        )

        if selected_day:
            day_data = next((h[1] for h in history if h[0] == selected_day), None)
            if day_data and day_data['meals']:
                for meal in day_data['meals']:
                    st.markdown(f"**{meal.get('timestamp', 'N/A')}** — {meal['description']}")
                    st.caption(
                        f"🔥 {int(meal['calories'])} cal • "
                        f"🥩 {int(meal['protein'])}g • "
                        f"🍞 {int(meal['carbs'])}g • "
                        f"🥑 {int(meal['fat'])}g"
                    )
                    st.divider()
    else:
        st.info("📅 No history yet. Start tracking meals to build your history!")

st.divider()

# ==================== MEAL LOG & CHARTS ====================
col_meals, col_charts = st.columns([1, 1])

with col_meals:
    st.header("📝 Today's Meals")

    if st.session_state.meals:
        for idx, meal in enumerate(reversed(st.session_state.meals)):
            actual_idx = len(st.session_state.meals) - 1 - idx

            with st.container():
                meal_col1, meal_col2 = st.columns([5, 1])

                with meal_col1:
                    st.markdown(f"**{meal['timestamp']}** — {meal['description']}")
                    st.caption(
                        f"🔥 {int(meal['calories'])} cal  •  "
                        f"🥩 {int(meal['protein'])}g protein  •  "
                        f"🍞 {int(meal['carbs'])}g carbs  •  "
                        f"🥑 {int(meal['fat'])}g fat"
                    )

                with meal_col2:
                    if st.button("🗑️", key=f"remove_{actual_idx}", help="Remove this meal"):
                        st.session_state.meals.pop(actual_idx)
                        save_current_day()
                        st.rerun()

                st.divider()
    else:
        st.info("🍽️ No meals logged yet. Add your first meal above!")
        st.caption("Try searching for something like '2 eggs and toast'")

with col_charts:
    # Macro Distribution Chart
    if totals['calories'] > 0:
        st.header("📈 Macro Distribution")

        # Use the visualization module
        fig = create_macro_pie_chart(totals)
        st.plotly_chart(fig, use_container_width=True)

        # Macro breakdown stats
        protein_cals = totals['protein'] * 4
        carbs_cals = totals['carbs'] * 4
        fat_cals = totals['fat'] * 9
        total_macro_cals = protein_cals + carbs_cals + fat_cals

        if total_macro_cals > 0:
            st.caption("**Macro Breakdown:**")
            breakdown_cols = st.columns(3)
            with breakdown_cols[0]:
                st.markdown(f"🥩 **Protein**<br>{int(totals['protein'])}g ({protein_cals/total_macro_cals*100:.0f}%)", unsafe_allow_html=True)
            with breakdown_cols[1]:
                st.markdown(f"🍞 **Carbs**<br>{int(totals['carbs'])}g ({carbs_cals/total_macro_cals*100:.0f}%)", unsafe_allow_html=True)
            with breakdown_cols[2]:
                st.markdown(f"🥑 **Fat**<br>{int(totals['fat'])}g ({fat_cals/total_macro_cals*100:.0f}%)", unsafe_allow_html=True)

        # Bar chart for meals breakdown
        if len(st.session_state.meals) > 1:
            st.divider()
            bar_chart = create_daily_bar_chart(st.session_state.meals)
            if bar_chart:
                st.plotly_chart(bar_chart, use_container_width=True)
    else:
        st.header("📈 Macro Distribution")
        st.info("📊 Charts will appear after you log your first meal")

# Footer with remaining summary
st.divider()

if totals['calories'] > 0:
    footer_cols = st.columns(4)

    with footer_cols[0]:
        if remaining['calories'] > 0:
            st.success(f"🎯 **{int(remaining['calories'])}** calories remaining")
        elif remaining['calories'] == 0:
            st.success("🎉 Calorie goal reached!")
        else:
            st.warning(f"⚠️ **{int(abs(remaining['calories']))}** calories over goal")

    with footer_cols[1]:
        if remaining['protein'] > 0:
            st.info(f"🥩 Need **{int(remaining['protein'])}g** more protein")
        else:
            st.success("✅ Protein goal reached!")

    with footer_cols[2]:
        if remaining['carbs'] > 0:
            st.info(f"🍞 Need **{int(remaining['carbs'])}g** more carbs")
        else:
            st.success("✅ Carbs goal reached!")

    with footer_cols[3]:
        if remaining['fat'] > 0:
            st.info(f"🥑 Need **{int(remaining['fat'])}g** more fat")
        else:
            st.success("✅ Fat goal reached!")
else:
    st.info("👋 Welcome! Start tracking your nutrition by adding your first meal above.")

# Footer credits
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888; font-size: 0.8em;'>Coded by Nate</p>", unsafe_allow_html=True)
