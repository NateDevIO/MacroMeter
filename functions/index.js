const functions = require("firebase-functions");
const cors = require("cors")({ origin: true });

/**
 * Helper to parse natural language query into items
 * e.g. "2 eggs, a banana" -> [{qty: 2, text: "eggs"}, {qty: 1, text: "banana"}]
 */
function parseItems(query) {
    // Split by comma or " and "
    const parts = query.split(/,| and /i).map(s => s.trim()).filter(s => s);

    return parts.map(part => {
        let qty = 1;
        let text = part;

        // Match quantity at start: "2 ", "1.5 ", "a ", "an "
        const match = part.match(/^(\d+(\.\d+)?|a|an)\s+(.*)/i);
        if (match) {
            if (match[1].toLowerCase() === 'a' || match[1].toLowerCase() === 'an') {
                qty = 1;
            } else {
                qty = parseFloat(match[1]);
            }
            text = match[3];
        }

        return { qty, text };
    });
}

/**
 * Search USDA API for a single food item with retry
 */
async function searchFood(apiKey, itemText, retries = 2) {
    const url = new URL("https://api.nal.usda.gov/fdc/v1/foods/search");
    url.searchParams.append("api_key", apiKey);
    url.searchParams.append("query", itemText);
    url.searchParams.append("pageSize", "5");
    // Removed dataType filter for broader, more reliable matching

    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            console.log(`Searching for '${itemText}' (attempt ${attempt + 1})`);
            const response = await fetch(url.toString());

            if (!response.ok) {
                const text = await response.text();
                console.error(`USDA API Error (${response.status}):`, text);
                if (attempt < retries) {
                    await new Promise(r => setTimeout(r, 300)); // Wait before retry
                    continue;
                }
                return null;
            }

            const data = await response.json();
            const foods = data.foods || [];

            if (foods.length > 0) {
                const food = foods[0];
                const nutrients = {};
                for (const n of food.foodNutrients || []) {
                    nutrients[n.nutrientName] = n.value || 0;
                }

                return {
                    name: food.description,
                    calories: nutrients["Energy"] || nutrients["Energy (Atwater General Factors)"] || 0,
                    protein: nutrients["Protein"] || 0,
                    carbs: nutrients["Carbohydrate, by difference"] || 0,
                    fat: nutrients["Total lipid (fat)"] || 0
                };
            }

            // No results found
            console.log(`No results for '${itemText}'`);
            return null;

        } catch (error) {
            console.error(`Error searching for '${itemText}':`, error.message);
            if (attempt < retries) {
                await new Promise(r => setTimeout(r, 300));
                continue;
            }
            return null;
        }
    }
    return null;
}

/**
 * Firebase Cloud Function to proxy USDA FoodData Central API calls.
 * Supports quantity parsing and multiple items with reliable sequential processing.
 */
exports.searchFood = functions.https.onRequest((req, res) => {
    cors(req, res, async () => {
        try {
            const rawQuery = req.query.query || req.body.query;

            if (!rawQuery) {
                return res.status(400).json({ error: "Missing 'query' parameter" });
            }

            const apiKey = process.env.USDA_API_KEY;
            if (!apiKey) {
                return res.status(500).json({ error: "USDA API key not configured" });
            }

            // Parse query into items
            const items = parseItems(rawQuery);
            console.log(`Parsed '${rawQuery}' into:`, JSON.stringify(items));

            let totalNutrients = { calories: 0, protein: 0, carbs: 0, fat: 0 };
            let foundItems = [];
            let notFoundItems = [];

            // Process items SEQUENTIALLY to avoid rate limiting
            for (const item of items) {
                const result = await searchFood(apiKey, item.text);

                if (result) {
                    foundItems.push(`${item.qty} x ${result.name}`);
                    totalNutrients.calories += result.calories * item.qty;
                    totalNutrients.protein += result.protein * item.qty;
                    totalNutrients.carbs += result.carbs * item.qty;
                    totalNutrients.fat += result.fat * item.qty;
                } else {
                    notFoundItems.push(item.text);
                }
            }

            if (foundItems.length === 0) {
                return res.json({
                    found: false,
                    error: `No results for '${rawQuery}'`
                });
            }

            return res.json({
                found: true,
                name: foundItems.join(", "),
                calories: Math.round(totalNutrients.calories),
                protein: Math.round(totalNutrients.protein),
                carbs: Math.round(totalNutrients.carbs),
                fat: Math.round(totalNutrients.fat),
                partial: notFoundItems.length > 0,
                missing: notFoundItems
            });

        } catch (error) {
            console.error("Function error:", error);
            return res.status(500).json({ error: error.message });
        }
    });
});
