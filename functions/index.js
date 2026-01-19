const functions = require("firebase-functions");
const cors = require("cors")({ origin: true });

/**
 * Firebase Cloud Function to proxy USDA FoodData Central API calls.
 * This resolves intermittent 400 errors experienced on Streamlit Cloud.
 */
exports.searchFood = functions.https.onRequest((req, res) => {
    cors(req, res, async () => {
        try {
            // Get query from request
            const query = req.query.query || req.body.query;

            if (!query) {
                return res.status(400).json({ error: "Missing 'query' parameter" });
            }

            // Get API key from environment variable
            const apiKey = process.env.USDA_API_KEY;

            if (!apiKey) {
                return res.status(500).json({ error: "USDA API key not configured" });
            }

            // Call USDA API
            const url = new URL("https://api.nal.usda.gov/fdc/v1/foods/search");
            url.searchParams.append("api_key", apiKey);
            url.searchParams.append("query", query.trim());
            url.searchParams.append("pageSize", "5");

            const response = await fetch(url.toString());

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`USDA API error: ${response.status} - ${errorText}`);
                return res.status(response.status).json({
                    error: `USDA API error: ${response.status}`,
                    details: errorText
                });
            }

            const data = await response.json();
            const foods = data.foods || [];

            if (foods.length === 0) {
                return res.json({
                    found: false,
                    error: `No results for '${query}'`
                });
            }

            // Extract nutrition from first (best) match
            const food = foods[0];
            const nutrients = {};

            for (const n of food.foodNutrients || []) {
                nutrients[n.nutrientName] = n.value || 0;
            }

            // Calculate macros
            const result = {
                found: true,
                name: food.description,
                calories: nutrients["Energy"] || nutrients["Energy (Atwater General Factors)"] || 0,
                protein: nutrients["Protein"] || 0,
                carbs: nutrients["Carbohydrate, by difference"] || 0,
                fat: nutrients["Total lipid (fat)"] || 0
            };

            return res.json(result);

        } catch (error) {
            console.error("Function error:", error);
            return res.status(500).json({ error: error.message });
        }
    });
});
