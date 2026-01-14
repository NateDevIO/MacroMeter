import requests
import os
from dotenv import load_dotenv
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()


def safe_float(value, default=0):
    """Safely convert a value to float"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_api_key():
    """Get API key fresh each time to handle Streamlit Cloud secrets timing"""
    api_key = None
    try:
        if "USDA_API_KEY" in st.secrets:
            api_key = st.secrets["USDA_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("USDA_API_KEY")
    
    # Clean up API key
    if api_key:
        api_key = str(api_key).strip().strip('"').strip("'")
    
    return api_key


def create_session():
    """Create a requests session with retry logic built-in"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session


class NutritionClient:
    """Client for USDA FoodData Central API (free, no restrictions)"""

    def __init__(self):
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.session = create_session()

    def get_nutrition(self, query):
        """
        Fetch nutrition data for food query

        Args:
            query (str): Food description, e.g., "2 eggs and a banana"

        Returns:
            dict: Nutrition data with calories, protein, carbs, fat
                  or dict with 'error' key if error occurs
        """
        # Get API key fresh each request to handle Streamlit Cloud timing
        api_key = get_api_key()
        
        if not api_key or api_key == "your_api_key_here":
            return {"error": "API key not configured. Please add your USDA API key to the .env file."}

        # Search for foods
        search_url = f"{self.base_url}/foods/search"
        params = {
            "api_key": api_key,
            "query": query.strip(),
            "pageSize": 5
        }

        try:
            response = self.session.get(search_url, params=params, timeout=20)
            
            # Check for errors with detailed message
            if response.status_code == 400:
                try:
                    error_detail = response.json()
                    return {"error": f"API error: {error_detail.get('message', 'Bad request')}"}
                except:
                    return {"error": f"API error (400). Please try again."}
            elif response.status_code == 401 or response.status_code == 403:
                return {"error": "API authentication failed. Please check your API key."}
            elif response.status_code == 429:
                return {"error": "Rate limit reached. Please wait a moment."}
            
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
            return {"error": "Request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Unable to connect. Please check your internet connection."}
        except requests.exceptions.HTTPError as e:
            return {"error": f"API error (HTTP {e.response.status_code})"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection issue: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


# Alias for backward compatibility
NutritionixClient = NutritionClient
