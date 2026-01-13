# Standard Operating Procedure (SOP)
## Daily Macro Nutrition Tracker - Streamlit Application

**Document Version:** 1.0  
**Date:** January 13, 2026  
**Project Type:** Portfolio Demonstration Application  
**Target Audience:** AI Development Assistants (Claude Code, Claude, GPT, etc.)

---

## Executive Summary

Build a Streamlit-based daily nutrition tracking application that allows users to log meals throughout the day using natural language input, track macronutrients against personal goals, and visualize their progress with charts and progress bars.

**Core Value Proposition:** Solve the problem of tracking daily nutrition intake in a simple, visual, and goal-oriented way without requiring manual macro calculations.

**Key Differentiator:** Natural language meal input ("2 eggs and a banana") that automatically fetches and calculates nutrition data via API.

---

## Project Overview

### 1.1 Problem Statement
People trying to track their nutrition intake face several challenges:
- Manual calculation of macros is time-consuming
- Existing apps are often overcomplicated or require subscriptions
- Lack of simple visual feedback on daily progress
- Difficult to see if they're on track to meet goals

### 1.2 Solution
A streamlit web application that:
- Accepts natural language food descriptions
- Automatically fetches nutrition data from an API
- Tracks meals throughout the day
- Shows real-time progress toward daily macro goals
- Provides visual feedback through charts and progress bars

### 1.3 Success Criteria
- User can set and save daily nutrition goals
- User can add meals with natural language input
- App displays accurate nutrition data from API
- Progress bars show remaining macros visually
- Session state persists data throughout the day
- Application is portfolio-ready with clean UI/UX

---

## Technical Requirements

### 2.1 Technology Stack
- **Framework:** Streamlit (latest stable version)
- **Language:** Python 3.9+
- **API:** Nutritionix API (primary recommendation)
  - **Alternative:** USDA FoodData Central (free but less NLP capability)
- **Data Visualization:** Plotly or Matplotlib
- **Session Management:** Streamlit session_state
- **HTTP Requests:** requests library

### 2.2 Required Libraries
```
streamlit>=1.30.0
requests>=2.31.0
plotly>=5.18.0
python-dotenv>=1.0.0
pandas>=2.1.0
```

### 2.3 API Requirements

#### Nutritionix API (Recommended)
- **Why:** Best natural language processing, handles conversational input
- **Endpoint:** `/v2/natural/nutrients`
- **Free Tier:** 500 requests/day
- **Sign up:** https://www.nutritionix.com/business/api
- **Authentication:** App ID + App Key
- **Example Query:** "1 banana and 2 eggs" → Parsed nutrition data

#### USDA FoodData Central (Alternative)
- **Why:** Completely free, comprehensive database
- **Endpoint:** `/v1/foods/search`
- **Authentication:** API Key (free)
- **Limitation:** Requires more specific food names

### 2.4 Project Structure
```
nutrition-tracker/
│
├── app.py                 # Main Streamlit application
├── .env                   # API keys (not committed to git)
├── .gitignore            # Ignore .env and cache files
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
│
├── utils/
│   ├── __init__.py
│   ├── api_client.py    # API integration functions
│   ├── nutrition.py     # Nutrition calculation logic
│   └── visualization.py # Chart/graph generation
│
└── config/
    └── settings.py      # Configuration constants
```

---

## Feature Specifications

### 3.1 MVP Features (Phase 1 - Required)

#### Feature 1: Goal Setting
**Priority:** P0 (Critical)

**User Story:** As a user, I want to set my daily nutrition goals so I can track my progress.

**Implementation:**
- Input fields for:
  - Daily calorie target (integer, 1000-5000)
  - Protein target (grams)
  - Carbohydrates target (grams)
  - Fat target (grams)
- Store goals in `st.session_state`
- Display current goals prominently at top of page
- Include "Edit Goals" button to modify

**Acceptance Criteria:**
- Goals persist throughout session
- Validation: calories > 0, macros >= 0
- Default values provided (e.g., 2000 cal, 150g protein, 250g carbs, 65g fat)

---

#### Feature 2: Natural Language Meal Input
**Priority:** P0 (Critical)

**User Story:** As a user, I want to describe my food in plain English so I don't have to search databases.

**Implementation:**
- Text input box with placeholder: "e.g., 2 scrambled eggs and a banana"
- Submit button to process input
- Display loading spinner during API call
- Show parsed results before adding to daily log
- Allow user to confirm or cancel before adding

**API Integration:**
```python
def fetch_nutrition(food_query, api_key, app_id):
    """
    Calls Nutritionix API to get nutrition data.
    Returns: dict with calories, protein, carbs, fat
    """
    endpoint = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": app_id,
        "x-app-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"query": food_query}
    
    response = requests.post(endpoint, headers=headers, json=data)
    # Parse response and extract nutrition data
    # Return formatted dictionary
```

**Error Handling:**
- Catch API errors (invalid food, rate limit, network issues)
- Display user-friendly error messages
- Suggest corrections for unrecognized foods

**Acceptance Criteria:**
- API call completes in < 3 seconds
- Returns accurate nutrition data
- Handles multi-food queries ("eggs and bacon")
- Graceful error handling with helpful messages

---

#### Feature 3: Daily Meal Log
**Priority:** P0 (Critical)

**User Story:** As a user, I want to see all meals I've logged today so I can track what I've eaten.

**Implementation:**
- Display meals in reverse chronological order (most recent first)
- Each meal entry shows:
  - Food description
  - Calories
  - Protein (g)
  - Carbs (g)
  - Fat (g)
  - Remove button (red "X")
- Store in `st.session_state['meals']` as list of dicts

**Data Structure:**
```python
meal = {
    "id": unique_id,  # Use timestamp or uuid
    "description": "2 eggs and banana",
    "calories": 350,
    "protein": 15,
    "carbs": 40,
    "fat": 12,
    "timestamp": "2026-01-13 09:30:00"
}
```

**Acceptance Criteria:**
- Meals persist in session
- Can remove individual meals
- Display updates immediately after add/remove
- Show "No meals logged yet" when empty

---

#### Feature 4: Progress Tracking Dashboard
**Priority:** P0 (Critical)

**User Story:** As a user, I want to see my progress toward daily goals so I know what I have left to eat.

**Implementation:**

**Display Sections:**

1. **Summary Cards** (Top of page)
   - Total consumed / Goal for each macro
   - Example: "Calories: 1,450 / 2,000" with color coding
   - Green if on track, yellow if close to goal, red if over

2. **Progress Bars** (Visual indicators)
   - One bar per macro (Calories, Protein, Carbs, Fat)
   - Show percentage completed
   - Color-coded: green (0-80%), yellow (80-100%), red (>100%)

3. **Remaining Macros**
   - Calculate and display: Goal - Consumed = Remaining
   - Example: "You have 550 calories remaining today"
   - Encourage user if close to goals

**Calculations:**
```python
def calculate_totals(meals):
    """Sum all macros from logged meals"""
    totals = {
        "calories": sum(m["calories"] for m in meals),
        "protein": sum(m["protein"] for m in meals),
        "carbs": sum(m["carbs"] for m in meals),
        "fat": sum(m["fat"] for m in meals)
    }
    return totals

def calculate_remaining(goals, totals):
    """Calculate remaining macros"""
    return {k: goals[k] - totals[k] for k in goals}
```

**Acceptance Criteria:**
- Real-time updates when meals added/removed
- Accurate calculations
- Clear visual feedback on progress
- Responsive layout on mobile

---

#### Feature 5: Macro Distribution Chart
**Priority:** P1 (Important)

**User Story:** As a user, I want to see a visual breakdown of my macro distribution so I understand my diet composition.

**Implementation:**
- Pie chart showing percentage breakdown: Protein / Carbs / Fat
- Display both grams and calories (since protein/carbs = 4 cal/g, fat = 9 cal/g)
- Use Plotly for interactivity
- Update dynamically as meals are added

**Chart Specifications:**
```python
import plotly.graph_objects as go

def create_macro_pie_chart(totals):
    """Generate interactive pie chart of macro distribution"""
    labels = ['Protein', 'Carbs', 'Fat']
    values = [totals['protein'], totals['carbs'], totals['fat']]
    colors = ['#FF6B6B', '#4ECDC4', '#FFD93D']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value}g<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(title='Macro Distribution')
    return fig
```

**Acceptance Criteria:**
- Chart renders correctly
- Shows accurate percentages
- Interactive hover tooltips
- Responsive sizing

---

### 3.2 Enhancement Features (Phase 2 - Optional)

#### Feature 6: Meal History
**Priority:** P2 (Nice to have)

**User Story:** As a user, I want to see my nutrition history from previous days so I can track trends.

**Implementation:**
- Save daily logs to local file (JSON or CSV)
- Display past 7 days in table format
- Show daily totals for each day
- Optional: Export to CSV

**Technical Notes:**
- Use `pandas` for data handling
- Store in `data/history.json`
- Load on app start

---

#### Feature 7: Quick Add Favorites
**Priority:** P2 (Nice to have)

**User Story:** As a user, I want to save frequently eaten meals so I can add them quickly.

**Implementation:**
- "Save as Favorite" button on meal results
- Display favorite meals as quick-add buttons
- Store in `st.session_state['favorites']`

---

#### Feature 8: Recipe Mode
**Priority:** P3 (Future enhancement)

**User Story:** As a user, I want to paste an entire recipe and get per-serving nutrition.

**Implementation:**
- Text area for recipe ingredients list
- Input for number of servings
- Calculate total nutrition and divide by servings

---

## Development Phases

### Phase 1: Core MVP (Days 1-3)
1. **Day 1:** Project setup, API integration, basic Streamlit structure
2. **Day 2:** Goal setting, meal input, meal log display
3. **Day 3:** Progress tracking dashboard, calculations

**Deliverable:** Working app with Features 1-4

### Phase 2: Visualization & Polish (Days 4-5)
4. **Day 4:** Add macro distribution chart, improve UI/UX
5. **Day 5:** Error handling, loading states, responsive design

**Deliverable:** Portfolio-ready app with Feature 5

### Phase 3: Enhancements (Optional)
6. Meal history
7. Favorites system
8. Recipe mode

---

## Step-by-Step Implementation Guide

### Step 1: Project Setup

```bash
# Create project directory
mkdir nutrition-tracker
cd nutrition-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit requests plotly python-dotenv pandas

# Create requirements.txt
pip freeze > requirements.txt

# Create .env file
echo "NUTRITIONIX_APP_ID=your_app_id_here" > .env
echo "NUTRITIONIX_APP_KEY=your_app_key_here" >> .env

# Create .gitignore
echo ".env" > .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
```

---

### Step 2: API Client Setup

**File: `utils/api_client.py`**

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class NutritionixClient:
    """Client for Nutritionix API"""
    
    def __init__(self):
        self.app_id = os.getenv("NUTRITIONIX_APP_ID")
        self.app_key = os.getenv("NUTRITIONIX_APP_KEY")
        self.base_url = "https://trackapi.nutritionix.com/v2"
        
    def get_nutrition(self, query):
        """
        Fetch nutrition data for natural language food query
        
        Args:
            query (str): Food description, e.g., "2 eggs and a banana"
            
        Returns:
            dict: Nutrition data with calories, protein, carbs, fat
                  or None if error occurs
        """
        endpoint = f"{self.base_url}/natural/nutrients"
        headers = {
            "x-app-id": self.app_id,
            "x-app-key": self.app_key,
            "Content-Type": "application/json"
        }
        data = {"query": query}
        
        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            # Parse response
            foods = response.json().get("foods", [])
            
            # Sum up all foods in query
            total_nutrition = {
                "calories": sum(f.get("nf_calories", 0) for f in foods),
                "protein": sum(f.get("nf_protein", 0) for f in foods),
                "carbs": sum(f.get("nf_total_carbohydrate", 0) for f in foods),
                "fat": sum(f.get("nf_total_fat", 0) for f in foods)
            }
            
            return total_nutrition
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
```

---

### Step 3: Main Streamlit App

**File: `app.py`**

```python
import streamlit as st
from utils.api_client import NutritionixClient
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Daily Macro Tracker",
    page_icon="🍎",
    layout="wide"
)

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

# Initialize API client
api_client = NutritionixClient()

# Title
st.title("🍎 Daily Macro Tracker")
st.markdown("Track your nutrition goals with natural language meal entry")

# Sidebar for goals
with st.sidebar:
    st.header("Daily Goals")
    
    goals_calories = st.number_input("Calories", 
                                     min_value=1000, 
                                     max_value=5000, 
                                     value=st.session_state.goals['calories'])
    goals_protein = st.number_input("Protein (g)", 
                                    min_value=0, 
                                    value=st.session_state.goals['protein'])
    goals_carbs = st.number_input("Carbs (g)", 
                                  min_value=0, 
                                  value=st.session_state.goals['carbs'])
    goals_fat = st.number_input("Fat (g)", 
                                min_value=0, 
                                value=st.session_state.goals['fat'])
    
    if st.button("Update Goals"):
        st.session_state.goals = {
            'calories': goals_calories,
            'protein': goals_protein,
            'carbs': goals_carbs,
            'fat': goals_fat
        }
        st.success("Goals updated!")

# Calculate totals
def calculate_totals():
    if not st.session_state.meals:
        return {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    
    return {
        'calories': sum(m['calories'] for m in st.session_state.meals),
        'protein': sum(m['protein'] for m in st.session_state.meals),
        'carbs': sum(m['carbs'] for m in st.session_state.meals),
        'fat': sum(m['fat'] for m in st.session_state.meals)
    }

totals = calculate_totals()
goals = st.session_state.goals

# Progress Dashboard
st.header("Today's Progress")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Calories", f"{int(totals['calories'])} / {goals['calories']}")
    progress_cal = min(totals['calories'] / goals['calories'], 1.0)
    st.progress(progress_cal)

with col2:
    st.metric("Protein", f"{int(totals['protein'])}g / {goals['protein']}g")
    progress_protein = min(totals['protein'] / goals['protein'], 1.0)
    st.progress(progress_protein)

with col3:
    st.metric("Carbs", f"{int(totals['carbs'])}g / {goals['carbs']}g")
    progress_carbs = min(totals['carbs'] / goals['carbs'], 1.0)
    st.progress(progress_carbs)

with col4:
    st.metric("Fat", f"{int(totals['fat'])}g / {goals['fat']}g")
    progress_fat = min(totals['fat'] / goals['fat'], 1.0)
    st.progress(progress_fat)

# Add Meal Section
st.header("Add Meal")

meal_input = st.text_input(
    "Describe your meal",
    placeholder="e.g., 2 scrambled eggs and a banana",
    key="meal_input"
)

if st.button("Add Meal", type="primary"):
    if meal_input:
        with st.spinner("Fetching nutrition data..."):
            nutrition = api_client.get_nutrition(meal_input)
            
            if "error" in nutrition:
                st.error(f"Error: {nutrition['error']}")
            else:
                # Add meal to session state
                meal = {
                    'id': datetime.now().isoformat(),
                    'description': meal_input,
                    'calories': nutrition['calories'],
                    'protein': nutrition['protein'],
                    'carbs': nutrition['carbs'],
                    'fat': nutrition['fat'],
                    'timestamp': datetime.now().strftime("%I:%M %p")
                }
                st.session_state.meals.append(meal)
                st.success(f"Added: {meal_input}")
                st.rerun()
    else:
        st.warning("Please enter a meal description")

# Meal Log
st.header("Today's Meals")

if st.session_state.meals:
    for idx, meal in enumerate(reversed(st.session_state.meals)):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{meal['timestamp']}** - {meal['description']}")
            st.caption(f"Calories: {int(meal['calories'])} | Protein: {int(meal['protein'])}g | Carbs: {int(meal['carbs'])}g | Fat: {int(meal['fat'])}g")
        
        with col2:
            if st.button("Remove", key=f"remove_{idx}"):
                st.session_state.meals.remove(meal)
                st.rerun()
        
        st.divider()
else:
    st.info("No meals logged yet. Add your first meal above!")

# Macro Distribution Chart
if totals['calories'] > 0:
    st.header("Macro Distribution")
    
    # Calculate calories from each macro
    protein_cals = totals['protein'] * 4
    carbs_cals = totals['carbs'] * 4
    fat_cals = totals['fat'] * 9
    
    fig = go.Figure(data=[go.Pie(
        labels=['Protein', 'Carbs', 'Fat'],
        values=[protein_cals, carbs_cals, fat_cals],
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#FFD93D']),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.0f} calories<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Calorie Distribution by Macro',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

---

### Step 4: Testing & Validation

**Test Cases:**

1. **API Integration Test**
   - Input: "1 banana"
   - Expected: Returns ~105 calories, 1g protein, 27g carbs, 0g fat
   
2. **Multiple Food Items Test**
   - Input: "2 eggs and 1 banana"
   - Expected: Returns combined nutrition data
   
3. **Error Handling Test**
   - Input: "asdfasdf" (invalid food)
   - Expected: Graceful error message, app doesn't crash
   
4. **Progress Calculation Test**
   - Add meals totaling 1500 calories
   - Goal: 2000 calories
   - Expected: Progress bar shows 75%, remaining shows 500
   
5. **Session Persistence Test**
   - Add 3 meals
   - Interact with other elements
   - Expected: All meals remain in log
   
6. **Remove Meal Test**
   - Add 2 meals, remove 1
   - Expected: Totals recalculate correctly

---

## UI/UX Requirements

### Design Principles
1. **Simplicity First:** Minimize cognitive load, clear CTAs
2. **Immediate Feedback:** Show results instantly after actions
3. **Visual Hierarchy:** Most important info at top (progress)
4. **Mobile-Friendly:** Responsive design for phone/tablet use

### Color Scheme
- **Primary:** Blue (#4ECDC4) - Goals, buttons
- **Success:** Green (#2ECC71) - On track
- **Warning:** Yellow (#FFD93D) - Near goal
- **Danger:** Red (#FF6B6B) - Over goal
- **Neutral:** Gray (#95A5A6) - Text, borders

### Typography
- **Headers:** Bold, 24-32px
- **Body:** Regular, 16px
- **Captions:** Light, 14px

### Layout
```
┌─────────────────────────────────────────┐
│  Sidebar: Goals                         │
│  - Calories input                       │
│  - Protein input                        │
│  - Carbs input                          │
│  - Fat input                            │
│  [Update Goals Button]                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Main Area:                             │
│                                         │
│  🍎 Daily Macro Tracker                 │
│  Track your nutrition goals...          │
│                                         │
│  Today's Progress                       │
│  ┌─────┬─────┬─────┬─────┐            │
│  │ Cal │ Pro │ Carb│ Fat │            │
│  │ ███ │ ██  │ ████│ ███ │            │
│  └─────┴─────┴─────┴─────┘            │
│                                         │
│  Add Meal                               │
│  [Text Input: "e.g., 2 eggs..."]       │
│  [Add Meal Button]                      │
│                                         │
│  Today's Meals                          │
│  ┌─────────────────────────────────┐   │
│  │ 9:30 AM - 2 eggs and banana     │   │
│  │ Cals: 350 | Pro: 15g | ...  [X]│   │
│  └─────────────────────────────────┘   │
│                                         │
│  Macro Distribution                     │
│  [Pie Chart]                            │
│                                         │
└─────────────────────────────────────────┘
```

---

## Error Handling & Edge Cases

### API Errors
1. **Network Error**
   - Display: "Unable to connect. Please check your internet connection."
   - Action: Allow retry
   
2. **Invalid API Key**
   - Display: "API authentication failed. Please check your credentials."
   - Action: Show setup instructions

3. **Unrecognized Food**
   - Display: "Couldn't find nutrition data for '[food]'. Try being more specific."
   - Action: Keep input field populated for editing

4. **Rate Limit Exceeded**
   - Display: "API rate limit reached. Please try again in a few minutes."
   - Action: Disable input temporarily

### User Input Validation
1. **Empty Input**
   - Display: "Please enter a meal description"
   - Action: Focus input field

2. **Very Long Input** (>200 chars)
   - Display: Warning about accuracy
   - Action: Still process but warn

### Session State Edge Cases
1. **First Visit** (no meals)
   - Display: Helpful message encouraging first entry
   
2. **All Goals at Zero**
   - Display: Prompt to set goals
   - Action: Highlight sidebar

### Data Edge Cases
1. **Negative Remaining Macros**
   - Display: "Over goal by X"
   - Color: Red
   
2. **Zero Calorie Meal**
   - Allow: Some foods (water, black coffee) are legitimately zero
   
3. **Extremely High Values** (>2000 cal single meal)
   - Display: Confirmation dialog "This seems high, add anyway?"

---

## Configuration & Environment Variables

### Required Environment Variables

**File: `.env`**
```
# Nutritionix API Credentials
NUTRITIONIX_APP_ID=your_app_id_here
NUTRITIONIX_APP_KEY=your_app_key_here

# Optional: Set default goals
DEFAULT_CALORIES=2000
DEFAULT_PROTEIN=150
DEFAULT_CARBS=250
DEFAULT_FAT=65
```

### Getting API Credentials

**Nutritionix API:**
1. Go to https://www.nutritionix.com/business/api
2. Sign up for free account
3. Navigate to API Console
4. Copy App ID and App Key
5. Paste into `.env` file

**USDA (Alternative):**
1. Go to https://fdc.nal.usda.gov/api-key-signup.html
2. Sign up for API key
3. Use endpoint: https://api.nal.usda.gov/fdc/v1/foods/search

---

## Deployment Instructions

### Local Development
```bash
# Run the app
streamlit run app.py

# Access at: http://localhost:8501
```

### Streamlit Cloud Deployment
1. Push code to GitHub repository
2. Go to share.streamlit.io
3. Connect GitHub account
4. Select repository and branch
5. Add environment variables in Streamlit Cloud dashboard
6. Deploy

### Requirements for Deployment
- Python 3.9+
- All dependencies in `requirements.txt`
- `.env` file NOT committed (use Streamlit secrets instead)
- Clear README.md with setup instructions

---

## README Template

```markdown
# Daily Macro Tracker 🍎

A Streamlit web application for tracking daily nutrition intake with natural language meal entry.

## Features
- Set personalized daily macro goals
- Add meals using natural language (e.g., "2 eggs and a banana")
- Visual progress tracking with charts and progress bars
- Real-time macro calculations
- Clean, responsive UI

## Tech Stack
- Python 3.9+
- Streamlit
- Nutritionix API
- Plotly

## Setup

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with API credentials
6. Run: `streamlit run app.py`

## API Setup
Get free API credentials at https://www.nutritionix.com/business/api

## License
MIT
```

---

## Success Metrics

### Functional Completeness
- [ ] All P0 features implemented and working
- [ ] API integration functioning correctly
- [ ] Session state persists throughout use
- [ ] Error handling covers common scenarios

### Code Quality
- [ ] Code is well-documented with comments
- [ ] Functions are modular and reusable
- [ ] No hardcoded credentials (uses .env)
- [ ] Follows PEP 8 style guidelines

### User Experience
- [ ] App loads in < 3 seconds
- [ ] API calls complete in < 5 seconds
- [ ] Layout is responsive on mobile
- [ ] Visual feedback for all actions
- [ ] Error messages are helpful and actionable

### Portfolio Readiness
- [ ] Professional README with screenshots
- [ ] Clean, modern UI
- [ ] Demonstrates multiple technical skills
- [ ] Shows understanding of user needs
- [ ] Deployable to Streamlit Cloud

---

## AI Development Assistant Instructions

When using this SOP with an AI assistant (Claude Code, etc.), provide the following prompt:

```
You are assisting with building a Streamlit nutrition tracking application. 
Please follow the attached SOP document precisely. Start with Step 1 (Project Setup) 
and work through each step systematically. Ask for confirmation before moving to 
the next major phase. Prioritize MVP features (P0) first. Follow all code structure 
and naming conventions exactly as specified. Test each feature before marking it 
complete.
```

**Workflow:**
1. Present this SOP to the AI assistant
2. AI reads and confirms understanding
3. AI implements Step 1, shows results
4. Developer reviews and approves
5. AI proceeds to Step 2, and so on
6. Developer can request modifications at any step

**Communication Protocol:**
- AI should explain what it's doing at each step
- AI should show code snippets for review before creating files
- AI should highlight any deviations from the SOP
- AI should ask questions if requirements are unclear

---

## Appendix A: Sample API Responses

### Nutritionix API Response Example
```json
{
  "foods": [
    {
      "food_name": "egg",
      "brand_name": null,
      "serving_qty": 2,
      "serving_unit": "large",
      "nf_calories": 143,
      "nf_total_fat": 9.51,
      "nf_total_carbohydrate": 0.72,
      "nf_protein": 12.56
    },
    {
      "food_name": "banana",
      "brand_name": null,
      "serving_qty": 1,
      "serving_unit": "medium (7\" to 7-7/8\" long)",
      "nf_calories": 105,
      "nf_total_fat": 0.39,
      "nf_total_carbohydrate": 26.95,
      "nf_protein": 1.29
    }
  ]
}
```

### USDA API Response Example
```json
{
  "foods": [
    {
      "fdcId": 746772,
      "description": "Egg, whole, raw, fresh",
      "foodNutrients": [
        {
          "nutrientName": "Protein",
          "value": 12.56
        },
        {
          "nutrientName": "Total lipid (fat)",
          "value": 9.51
        }
      ]
    }
  ]
}
```

---

## Appendix B: Troubleshooting Guide

### Common Issues

**Issue:** Streamlit session state not persisting
- **Cause:** Page reload clears state
- **Solution:** Ensure session state initialized before first use
- **Code:**
```python
if 'meals' not in st.session_state:
    st.session_state.meals = []
```

**Issue:** API returns 401 Unauthorized
- **Cause:** Invalid or missing API credentials
- **Solution:** Verify .env file exists and has correct keys
- **Check:** Print environment variables (without exposing keys)

**Issue:** Progress bars not updating
- **Cause:** Not recalculating totals after meal changes
- **Solution:** Call `st.rerun()` after add/remove operations

**Issue:** Layout breaks on mobile
- **Cause:** Fixed widths instead of responsive columns
- **Solution:** Use Streamlit's column ratios and `use_container_width=True`

---

## Appendix C: Future Enhancement Ideas

### Advanced Features (Post-MVP)
1. **Weekly Reports:** Bar charts showing daily totals over 7 days
2. **Meal Templates:** Save common meals as templates
3. **Barcode Scanner:** Use phone camera to scan food barcodes
4. **Photo Upload:** Take photo of meal, AI estimates nutrition
5. **Social Features:** Share meals with friends, compare progress
6. **Export Data:** Download nutrition history as CSV/Excel
7. **Dark Mode:** Toggle between light and dark themes
8. **Multi-User:** Support multiple profiles in one app
9. **Notification System:** Reminders to log meals
10. **Integration:** Connect with fitness trackers (Fitbit, Apple Health)

### Technical Improvements
1. **Database:** Replace session state with SQLite/PostgreSQL
2. **Authentication:** Add user login system
3. **Caching:** Cache API responses to reduce calls
4. **Testing:** Add unit tests with pytest
5. **Docker:** Containerize for easier deployment
6. **CI/CD:** Automated testing and deployment pipeline

---

## Document Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-13 | Initial SOP creation | Claude |

---

**END OF DOCUMENT**
