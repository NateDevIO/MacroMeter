# MacroMeter 🍎

A Streamlit web application for tracking daily nutrition intake with natural language meal entry.

**Coded by Nate**

## Features

### Core Features
- **Goal Setting** - Set personalized daily targets for calories, protein, carbs, and fat
- **Natural Language Input** - Add meals by describing them in plain English (e.g., "2 eggs and toast")
- **Real-time Progress Dashboard** - Visual progress bars and metrics showing daily intake vs goals
- **Macro Distribution Chart** - Interactive pie chart showing calorie breakdown by macro

### Additional Features
- **Meal History** - View and export your nutrition tracking history (last 7 days)
- **Quick Add Favorites** - Save frequently eaten meals for one-click adding
- **Recipe Mode** - Paste recipe ingredients and calculate per-serving nutrition
- **CSV Export** - Download your nutrition data for external analysis

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Core programming language |
| **Streamlit** | Web application framework |
| **USDA FoodData Central API** | Nutrition data source (free, comprehensive) |
| **Plotly** | Interactive data visualizations |
| **Pandas** | Data manipulation and export |
| **python-dotenv** | Environment variable management |

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MacroMeter.git
   cd MacroMeter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free USDA API key**
   - Sign up at: https://fdc.nal.usda.gov/api-key-signup.html
   - You'll receive the key instantly via email

4. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your USDA API key:
     ```
     USDA_API_KEY=your_api_key_here
     ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8501`

## Project Structure

```
MacroMeter/
├── app.py                 # Main Streamlit application
├── .env                   # API key configuration (not in repo)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── data/                  # Local data storage
│   ├── history.json       # Meal history
│   └── favorites.json     # Saved favorites
└── utils/
    ├── __init__.py
    ├── api_client.py      # USDA API integration
    ├── data_store.py      # Data persistence
    ├── nutrition.py       # Calculation utilities
    └── visualization.py   # Plotly chart generators
```

## Usage

1. **Set your goals** in the sidebar (calories, protein, carbs, fat)
2. **Add meals** by typing descriptions like "chicken breast with rice"
3. **Review nutrition data** before adding to your log
4. **Track progress** with the dashboard at the top
5. **Save favorites** for meals you eat often
6. **View history** to see your trends over time

## API Information

This app uses the **USDA FoodData Central API** which provides:
- Comprehensive nutrition database
- Free unlimited access
- No credit card required
- Data from USDA food surveys and research

## License

MIT License - Feel free to use and modify for your own projects.

---

*Built with Streamlit and the USDA FoodData Central API*
