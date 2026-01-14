import requests
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


def safe_float(value, default=0):
    """Safely convert a value to float"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class NutritionClient:
    """Client for USDA FoodData Central API (free, no restrictions)"""

    def __init__(self):
        # Try Streamlit secrets first (for Streamlit Cloud), then fall back to env var (local dev)
        self.api_key = None
        try:
            if "USDA_API_KEY" in st.secrets:
                self.api_key = st.secrets["USDA_API_KEY"]
        except Exception:
            pass
        
        if not self.api_key:
            self.api_key = os.getenv("USDA_API_KEY")
        self.base_url = "https://api.nal.usda.gov/fdc/v1"

    def get_nutrition(self, query):
        """
        Fetch nutrition data for food query

        Args:
            query (str): Food description, e.g., "2 eggs and a banana"

        Returns:
            dict: Nutrition data with calories, protein, carbs, fat
                  or dict with 'error' key if error occurs
        """
        if not self.api_key or self.api_key == "your_api_key_here":
            return {"error": "API key not configured. Please add your USDA API key to the .env file."}

        # Search for foods
        search_url = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": 5,
            "dataType": "Survey (FNDDS),Foundation,SR Legacy"
        }

        # Retry logic for intermittent failures
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.get(search_url, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()
                foods = data.get("foods", [])

                if not foods:
                    return {"error": f"Couldn't find nutrition data for '{query}'. Try being more specific."}

                # Get the best match (first result)
                food = foods[0]
                nutrients = {n.get("nutrientName", ""): n.get("value", 0) for n in food.get("foodNutrients", [])}

                # Extract macros (USDA uses specific nutrient names)
                total_nutrition = {
                    "calories": safe_float(nutrients.get("Energy", 0)),
                    "protein": safe_float(nutrients.get("Protein", 0)),
                    "carbs": safe_float(nutrients.get("Carbohydrate, by difference", 0)),
                    "fat": safe_float(nutrients.get("Total lipid (fat)", 0))
                }

                # If no calories found, try alternate name
                if total_nutrition["calories"] == 0:
                    total_nutrition["calories"] = safe_float(nutrients.get("Energy (Atwater General Factors)", 0))

                return total_nutrition

            except requests.exceptions.Timeout:
                last_error = "Request timed out. Please try again."
            except requests.exceptions.ConnectionError:
                last_error = "Unable to connect. Please check your internet connection."
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status == 400:
                    # Don't retry on 400 - it's a client error
                    return {"error": f"API error (400). Try a simpler search term."}
                elif status == 401 or status == 403:
                    return {"error": "API authentication failed. Please check your API key."}
                elif status == 429:
                    last_error = "API rate limit reached. Please wait a moment."
                elif status >= 500:
                    # Server errors - worth retrying
                    last_error = f"USDA API temporarily unavailable (HTTP {status}). Retrying..."
                else:
                    return {"error": f"API error (HTTP {status})"}
            except requests.exceptions.RequestException as e:
                last_error = f"Connection issue: {str(e)}"
            
            # Wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                import time
                time.sleep(0.5 * (attempt + 1))
        
        return {"error": last_error or "Failed after multiple attempts. Please try again."}


# Alias for backward compatibility
NutritionixClient = NutritionClient
