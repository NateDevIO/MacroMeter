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


def get_firebase_url():
    """Get Firebase Function URL from secrets or env"""
    url = None
    try:
        if "FIREBASE_FUNCTION_URL" in st.secrets:
            url = st.secrets["FIREBASE_FUNCTION_URL"]
    except Exception:
        pass
    
    if not url:
        url = os.getenv("FIREBASE_FUNCTION_URL")
    
    return url


def get_api_key():
    """Get API key for fallback direct calls"""
    api_key = None
    try:
        if "USDA_API_KEY" in st.secrets:
            api_key = st.secrets["USDA_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("USDA_API_KEY")
    
    if api_key:
        api_key = str(api_key).strip().strip('"').strip("'")
    
    return api_key


def create_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
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
    """Client for nutrition data - uses Firebase proxy or direct USDA API"""

    def __init__(self):
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.session = create_session()

    def get_nutrition(self, query):
        """
        Fetch nutrition data for food query.
        Uses Firebase Function if configured, falls back to direct USDA API.
        """
        # Try Firebase Function first (more reliable)
        firebase_url = get_firebase_url()
        if firebase_url:
            result = self._call_firebase(firebase_url, query)
            if result:
                return result
        
        # Fallback to direct USDA API
        return self._call_usda_direct(query)

    def _call_firebase(self, firebase_url, query):
        """Call Firebase Function proxy"""
        try:
            response = self.session.get(
                firebase_url,
                params={"query": query.strip()},
                timeout=20
            )
            
            if not response.ok:
                return None  # Fall back to direct call
            
            data = response.json()
            
            if data.get("error") or not data.get("found"):
                if data.get("error"):
                    return {"error": data["error"]}
                return {"error": f"No results for '{query}'"}
            
            return {
                "calories": safe_float(data.get("calories", 0)),
                "protein": safe_float(data.get("protein", 0)),
                "carbs": safe_float(data.get("carbs", 0)),
                "fat": safe_float(data.get("fat", 0))
            }
            
        except Exception as e:
            # Fall back to direct call
            return None

    def _call_usda_direct(self, query):
        """Direct call to USDA API (fallback)"""
        api_key = get_api_key()
        
        if not api_key or api_key == "your_api_key_here":
            return {"error": "API key not configured."}

        search_url = f"{self.base_url}/foods/search"
        params = {
            "api_key": api_key,
            "query": query.strip(),
            "pageSize": 5
        }

        try:
            response = self.session.get(search_url, params=params, timeout=20)
            
            if response.status_code == 400:
                return {"error": "API error. Please try again."}
            elif response.status_code in (401, 403):
                return {"error": "API authentication failed."}
            
            response.raise_for_status()
            data = response.json()
            foods = data.get("foods", [])

            if not foods:
                return {"error": f"No results for '{query}'"}

            food = foods[0]
            nutrients = {n.get("nutrientName", ""): n.get("value", 0) 
                        for n in food.get("foodNutrients", [])}

            result = {
                "calories": safe_float(nutrients.get("Energy", 0)),
                "protein": safe_float(nutrients.get("Protein", 0)),
                "carbs": safe_float(nutrients.get("Carbohydrate, by difference", 0)),
                "fat": safe_float(nutrients.get("Total lipid (fat)", 0))
            }

            if result["calories"] == 0:
                result["calories"] = safe_float(
                    nutrients.get("Energy (Atwater General Factors)", 0))

            return result

        except requests.exceptions.Timeout:
            return {"error": "Request timed out."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection failed."}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}


# Alias for backward compatibility
NutritionixClient = NutritionClient
