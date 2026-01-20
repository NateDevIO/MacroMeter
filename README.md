# MacroMeter 🍎

A nutrition tracking web application with natural language meal entry, powered by Firebase.

**Live App:** https://macrosfood.web.app

**Coded by Nate**

## Features

- **Natural Language Input** - Add meals by describing them (e.g., "2 eggs and a banana")
- **Smart Quantity Parsing** - Understands "2 scrambled eggs, a banana, and coffee"
- **Real-time Progress Dashboard** - Visual progress bars for calories, protein, carbs, fat
- **Customizable Goals** - Set personalized daily nutrition targets
- **Favorites System** - Save frequently eaten meals for one-click adding
- **Meal History** - Track your nutrition over time with exportable CSV data
- **Offline-Ready** - Data persists in localStorage

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **HTML/CSS/JavaScript** | Frontend web application |
| **Firebase Hosting** | Static site hosting (never sleeps!) |
| **Firebase Functions** | Backend API proxy |
| **USDA FoodData Central API** | Nutrition data source |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Firebase       │────▶│  Firebase       │────▶│  USDA FoodData   │
│  Hosting        │     │  Functions      │     │  Central API     │
│  (Frontend)     │◀────│  (Backend)      │◀────│                  │
└─────────────────┘     └─────────────────┘     └──────────────────┘
```

## Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/NateDevIO/MacroMeter.git
   cd MacroMeter
   ```

2. **Install Firebase CLI** (if not already installed)
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

3. **Install function dependencies**
   ```bash
   cd functions
   npm install
   cd ..
   ```

4. **Set up environment**
   - Create `functions/.env` with your USDA API key:
     ```
     USDA_API_KEY=your_api_key_here
     ```
   - Get a free key at: https://fdc.nal.usda.gov/api-key-signup.html

5. **Run locally**
   ```bash
   firebase serve
   ```

6. **Deploy**
   ```bash
   firebase deploy
   ```

## Project Structure

```
MacroMeter/
├── public/                 # Frontend (Firebase Hosting)
│   ├── index.html          # Main app page
│   ├── styles.css          # Styling
│   └── app.js              # Application logic
├── functions/              # Backend (Firebase Functions)
│   ├── index.js            # API proxy with smart parsing
│   ├── package.json        # Node.js dependencies
│   └── .env                # API key (not in repo)
├── firebase.json           # Firebase configuration
├── .firebaserc             # Firebase project settings
└── README.md               # This file
```

## How It Works

1. Enter a meal like "2 scrambled eggs and a banana"
2. The backend parses this into individual items with quantities
3. Each item is searched in the USDA database
4. Results are multiplied by quantity and summed
5. Total nutrition is displayed for confirmation

## API Information

This app uses the **USDA FoodData Central API** which provides:
- Comprehensive nutrition database (500k+ foods)
- Free unlimited access
- No credit card required

## License

MIT License - Feel free to use and modify for your own projects.

---

*Built with Firebase and the USDA FoodData Central API*
