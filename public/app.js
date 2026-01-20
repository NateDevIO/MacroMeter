/**
 * MacroMeter - Application JavaScript
 * Daily Nutrition Tracker with Firebase Backend
 * Coded by Nate
 */

// Firebase Function URL
const API_URL = 'https://us-central1-macrosfood.cloudfunctions.net/searchFood';

// State
let state = {
    goals: { calories: 2000, protein: 150, carbs: 250, fat: 65 },
    meals: [],
    favorites: [],
    history: [],
    pendingMeal: null
};

// DOM Elements
const elements = {
    // Progress
    caloriesValue: document.getElementById('calories-value'),
    caloriesBar: document.getElementById('calories-bar'),
    caloriesRemaining: document.getElementById('calories-remaining'),
    proteinValue: document.getElementById('protein-value'),
    proteinBar: document.getElementById('protein-bar'),
    proteinRemaining: document.getElementById('protein-remaining'),
    carbsValue: document.getElementById('carbs-value'),
    carbsBar: document.getElementById('carbs-bar'),
    carbsRemaining: document.getElementById('carbs-remaining'),
    fatValue: document.getElementById('fat-value'),
    fatBar: document.getElementById('fat-bar'),
    fatRemaining: document.getElementById('fat-remaining'),
    // Tabs
    tabs: document.querySelectorAll('.tab'),
    tabContents: document.querySelectorAll('.tab-content'),
    // Add Meal
    mealInput: document.getElementById('meal-input'),
    lookupBtn: document.getElementById('lookup-btn'),
    pendingMeal: document.getElementById('pending-meal'),
    pendingName: document.getElementById('pending-name'),
    pendingCalories: document.getElementById('pending-calories'),
    pendingProtein: document.getElementById('pending-protein'),
    pendingCarbs: document.getElementById('pending-carbs'),
    pendingFat: document.getElementById('pending-fat'),
    addMealBtn: document.getElementById('add-meal-btn'),
    addFavoriteBtn: document.getElementById('add-favorite-btn'),
    cancelBtn: document.getElementById('cancel-btn'),
    mealsContainer: document.getElementById('meals-container'),
    // Favorites
    favoritesContainer: document.getElementById('favorites-container'),
    // History
    historyContainer: document.getElementById('history-container'),
    clearHistoryBtn: document.getElementById('clear-history-btn'),
    // Settings
    goalCalories: document.getElementById('goal-calories'),
    goalProtein: document.getElementById('goal-protein'),
    goalCarbs: document.getElementById('goal-carbs'),
    goalFat: document.getElementById('goal-fat'),
    saveGoalsBtn: document.getElementById('save-goals-btn'),
    clearMealsBtn: document.getElementById('clear-meals-btn'),
    exportBtn: document.getElementById('export-btn'),
    // Toast
    toast: document.getElementById('toast')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadState();
    setupEventListeners();
    updateUI();
});

// Load state from localStorage
function loadState() {
    const saved = localStorage.getItem('macrometerState');
    if (saved) {
        const parsed = JSON.parse(saved);
        state.goals = parsed.goals || state.goals;
        state.favorites = parsed.favorites || [];
        state.history = parsed.history || [];
    }

    // Load today's meals
    const today = getToday();
    const todayMeals = localStorage.getItem(`meals_${today}`);
    if (todayMeals) {
        state.meals = JSON.parse(todayMeals);
    }

    // Set goal inputs
    elements.goalCalories.value = state.goals.calories;
    elements.goalProtein.value = state.goals.protein;
    elements.goalCarbs.value = state.goals.carbs;
    elements.goalFat.value = state.goals.fat;
}

// Save state to localStorage
function saveState() {
    localStorage.setItem('macrometerState', JSON.stringify({
        goals: state.goals,
        favorites: state.favorites,
        history: state.history
    }));
}

// Save today's meals
function saveTodayMeals() {
    const today = getToday();
    localStorage.setItem(`meals_${today}`, JSON.stringify(state.meals));
}

// Get today's date string
function getToday() {
    return new Date().toISOString().split('T')[0];
}

// Setup event listeners
function setupEventListeners() {
    // Tabs
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Lookup
    elements.lookupBtn.addEventListener('click', lookupMeal);
    elements.mealInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') lookupMeal();
    });

    // Pending meal actions
    elements.addMealBtn.addEventListener('click', addMeal);
    elements.addFavoriteBtn.addEventListener('click', addMealAndFavorite);
    elements.cancelBtn.addEventListener('click', cancelPending);

    // Settings
    elements.saveGoalsBtn.addEventListener('click', saveGoals);
    elements.clearMealsBtn.addEventListener('click', clearMeals);
    elements.exportBtn.addEventListener('click', exportHistory);
    elements.clearHistoryBtn.addEventListener('click', clearHistory);
}

// Switch tab
function switchTab(tabId) {
    elements.tabs.forEach(t => t.classList.remove('active'));
    elements.tabContents.forEach(c => c.classList.remove('active'));

    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

// Lookup meal from API
async function lookupMeal() {
    const query = elements.mealInput.value.trim();
    if (!query) {
        showToast('Please enter a meal description', 'error');
        return;
    }

    elements.lookupBtn.disabled = true;
    elements.lookupBtn.innerHTML = '<span class="loading"></span>';

    try {
        const response = await fetch(`${API_URL}?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.error || !data.found) {
            showToast(data.error || `No results for "${query}"`, 'error');
            return;
        }

        state.pendingMeal = {
            name: query,
            calories: Math.round(data.calories),
            protein: Math.round(data.protein),
            carbs: Math.round(data.carbs),
            fat: Math.round(data.fat)
        };

        showPendingMeal();

    } catch (error) {
        console.error('API Error:', error);
        showToast('Failed to fetch nutrition data. Please try again.', 'error');
    } finally {
        elements.lookupBtn.disabled = false;
        elements.lookupBtn.innerHTML = '🔍 Look Up';
    }
}

// Show pending meal preview
function showPendingMeal() {
    const meal = state.pendingMeal;
    elements.pendingName.textContent = meal.name;
    elements.pendingCalories.textContent = meal.calories;
    elements.pendingProtein.textContent = `${meal.protein}g`;
    elements.pendingCarbs.textContent = `${meal.carbs}g`;
    elements.pendingFat.textContent = `${meal.fat}g`;
    elements.pendingMeal.classList.remove('hidden');
}

// Hide pending meal preview
function hidePendingMeal() {
    elements.pendingMeal.classList.add('hidden');
    state.pendingMeal = null;
}

// Add meal to today's log
function addMeal() {
    if (!state.pendingMeal) return;

    const meal = {
        ...state.pendingMeal,
        id: Date.now(),
        time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    };

    state.meals.push(meal);
    saveTodayMeals();
    saveToHistory();

    elements.mealInput.value = '';
    hidePendingMeal();
    updateUI();
    showToast(`Added: ${meal.name}`, 'success');
}

// Add meal and save to favorites
function addMealAndFavorite() {
    if (!state.pendingMeal) return;

    // Add to favorites if not already there
    const exists = state.favorites.some(f => f.name.toLowerCase() === state.pendingMeal.name.toLowerCase());
    if (!exists) {
        state.favorites.push({ ...state.pendingMeal, id: Date.now() });
        saveState();
    }

    addMeal();
    showToast(`Added to meals and favorites!`, 'success');
}

// Cancel pending meal
function cancelPending() {
    hidePendingMeal();
    elements.mealInput.value = '';
}

// Remove meal
function removeMeal(id) {
    state.meals = state.meals.filter(m => m.id !== id);
    saveTodayMeals();
    saveToHistory();
    updateUI();
    showToast('Meal removed', 'success');
}

// Add favorite to today's meals
function addFavoriteToMeals(id) {
    const fav = state.favorites.find(f => f.id === id);
    if (!fav) return;

    const meal = {
        ...fav,
        id: Date.now(),
        time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    };

    state.meals.push(meal);
    saveTodayMeals();
    saveToHistory();
    updateUI();
    showToast(`Added: ${meal.name}`, 'success');
}

// Remove favorite
function removeFavorite(id) {
    state.favorites = state.favorites.filter(f => f.id !== id);
    saveState();
    updateUI();
    showToast('Favorite removed', 'success');
}

// Save goals
function saveGoals() {
    state.goals = {
        calories: parseInt(elements.goalCalories.value) || 2000,
        protein: parseInt(elements.goalProtein.value) || 150,
        carbs: parseInt(elements.goalCarbs.value) || 250,
        fat: parseInt(elements.goalFat.value) || 65
    };
    saveState();
    updateUI();
    showToast('Goals updated!', 'success');
}

// Clear all meals
function clearMeals() {
    if (!confirm('Clear all meals for today?')) return;
    state.meals = [];
    saveTodayMeals();
    updateUI();
    showToast('Meals cleared', 'success');
}

// Save to history
function saveToHistory() {
    const today = getToday();
    const totals = calculateTotals();

    // Update or add today's entry
    const existingIndex = state.history.findIndex(h => h.date === today);
    const entry = {
        date: today,
        ...totals,
        goals: { ...state.goals }
    };

    if (existingIndex >= 0) {
        state.history[existingIndex] = entry;
    } else {
        state.history.unshift(entry);
    }

    // Keep only last 30 days
    state.history = state.history.slice(0, 30);
    saveState();
}

// Clear history
function clearHistory() {
    if (!confirm('Clear all history? This cannot be undone.')) return;
    state.history = [];
    saveState();
    updateUI();
    showToast('History cleared', 'success');
}

// Export history to CSV
function exportHistory() {
    if (state.history.length === 0) {
        showToast('No history to export', 'error');
        return;
    }

    const headers = ['Date', 'Calories', 'Protein', 'Carbs', 'Fat', 'Cal Goal', 'Protein Goal', 'Carbs Goal', 'Fat Goal'];
    const rows = state.history.map(h => [
        h.date,
        h.calories,
        h.protein,
        h.carbs,
        h.fat,
        h.goals.calories,
        h.goals.protein,
        h.goals.carbs,
        h.goals.fat
    ]);

    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `macrometer_history_${getToday()}.csv`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('History exported!', 'success');
}

// Calculate totals
function calculateTotals() {
    return state.meals.reduce((acc, meal) => ({
        calories: acc.calories + meal.calories,
        protein: acc.protein + meal.protein,
        carbs: acc.carbs + meal.carbs,
        fat: acc.fat + meal.fat
    }), { calories: 0, protein: 0, carbs: 0, fat: 0 });
}

// Update UI
function updateUI() {
    updateProgress();
    updateMealsList();
    updateFavoritesList();
    updateHistoryList();
}

// Update progress bars
function updateProgress() {
    const totals = calculateTotals();
    const { goals } = state;

    // Calories
    const calPct = Math.min((totals.calories / goals.calories) * 100, 100);
    const calRemaining = goals.calories - totals.calories;
    elements.caloriesValue.textContent = `${totals.calories} / ${goals.calories}`;
    elements.caloriesBar.style.width = `${calPct}%`;
    elements.caloriesRemaining.textContent = calRemaining >= 0 ? `${calRemaining} remaining` : `${Math.abs(calRemaining)} over`;
    elements.caloriesRemaining.className = `progress-remaining ${calRemaining < 0 ? 'over' : ''}`;

    // Protein
    const proPct = Math.min((totals.protein / goals.protein) * 100, 100);
    const proRemaining = goals.protein - totals.protein;
    elements.proteinValue.textContent = `${totals.protein}g / ${goals.protein}g`;
    elements.proteinBar.style.width = `${proPct}%`;
    elements.proteinRemaining.textContent = proRemaining >= 0 ? `${proRemaining}g remaining` : `${Math.abs(proRemaining)}g over`;
    elements.proteinRemaining.className = `progress-remaining ${proRemaining < 0 ? 'over' : ''}`;

    // Carbs
    const carbPct = Math.min((totals.carbs / goals.carbs) * 100, 100);
    const carbRemaining = goals.carbs - totals.carbs;
    elements.carbsValue.textContent = `${totals.carbs}g / ${goals.carbs}g`;
    elements.carbsBar.style.width = `${carbPct}%`;
    elements.carbsRemaining.textContent = carbRemaining >= 0 ? `${carbRemaining}g remaining` : `${Math.abs(carbRemaining)}g over`;
    elements.carbsRemaining.className = `progress-remaining ${carbRemaining < 0 ? 'over' : ''}`;

    // Fat
    const fatPct = Math.min((totals.fat / goals.fat) * 100, 100);
    const fatRemaining = goals.fat - totals.fat;
    elements.fatValue.textContent = `${totals.fat}g / ${goals.fat}g`;
    elements.fatBar.style.width = `${fatPct}%`;
    elements.fatRemaining.textContent = fatRemaining >= 0 ? `${fatRemaining}g remaining` : `${Math.abs(fatRemaining)}g over`;
    elements.fatRemaining.className = `progress-remaining ${fatRemaining < 0 ? 'over' : ''}`;
}

// Update meals list
function updateMealsList() {
    if (state.meals.length === 0) {
        elements.mealsContainer.innerHTML = '<p class="empty-state">No meals logged yet. Add your first meal above!</p>';
        return;
    }

    elements.mealsContainer.innerHTML = state.meals.map(meal => `
        <div class="meal-item">
            <div class="meal-info">
                <div class="meal-name">${escapeHtml(meal.name)}</div>
                <div class="meal-macros">${meal.calories} cal • ${meal.protein}g protein • ${meal.carbs}g carbs • ${meal.fat}g fat</div>
                <div class="meal-time">${meal.time}</div>
            </div>
            <div class="meal-actions">
                <button onclick="removeMeal(${meal.id})" title="Remove">🗑️</button>
            </div>
        </div>
    `).join('');
}

// Update favorites list
function updateFavoritesList() {
    if (state.favorites.length === 0) {
        elements.favoritesContainer.innerHTML = '<p class="empty-state">No favorites yet. Add meals to your favorites for quick access!</p>';
        return;
    }

    elements.favoritesContainer.innerHTML = state.favorites.map(fav => `
        <div class="favorite-item">
            <div class="meal-info">
                <div class="meal-name">${escapeHtml(fav.name)}</div>
                <div class="meal-macros">${fav.calories} cal • ${fav.protein}g protein • ${fav.carbs}g carbs • ${fav.fat}g fat</div>
            </div>
            <div class="meal-actions">
                <button onclick="addFavoriteToMeals(${fav.id})" title="Add to today">➕</button>
                <button onclick="removeFavorite(${fav.id})" title="Remove">🗑️</button>
            </div>
        </div>
    `).join('');
}

// Update history list
function updateHistoryList() {
    if (state.history.length === 0) {
        elements.historyContainer.innerHTML = '<p class="empty-state">No history yet. Your daily totals will appear here.</p>';
        elements.clearHistoryBtn.classList.add('hidden');
        return;
    }

    elements.clearHistoryBtn.classList.remove('hidden');
    elements.historyContainer.innerHTML = state.history.map(day => {
        const calClass = day.calories <= day.goals.calories ? 'achieved' : 'over';
        const proClass = day.protein >= day.goals.protein ? 'achieved' : '';
        return `
            <div class="history-item">
                <div class="history-date">${formatDate(day.date)}</div>
                <div class="history-macros">
                    <span class="${calClass}">🔥 ${day.calories}/${day.goals.calories} cal</span>
                    <span class="${proClass}">🥩 ${day.protein}/${day.goals.protein}g protein</span>
                    <span>🍞 ${day.carbs}/${day.goals.carbs}g carbs</span>
                    <span>🥑 ${day.fat}/${day.goals.fat}g fat</span>
                </div>
            </div>
        `;
    }).join('');
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (dateStr === getToday()) return 'Today';
    if (dateStr === yesterday.toISOString().split('T')[0]) return 'Yesterday';
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show toast notification
function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast ${type} show`;

    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}
