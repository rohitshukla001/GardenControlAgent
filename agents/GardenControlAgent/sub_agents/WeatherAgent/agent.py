import json

from google.adk.agents import Agent
from datetime import datetime
import logging
import re
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WeatherAgent")

def validate_coordinates(lat, lon):
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not (-180 <= lon <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")
    return True

def extract_coordinates(query):
    pattern = r"lat:\s*([-]?\d+\.?\d*),\s*lon:\s*([-]?\d+\.?\d*)"
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        lat, lon = float(match.group(1)), float(match.group(2))
        validate_coordinates(lat, lon)
        return lat, lon
    return None, None

def get_location_from_lat_long(latitude: float, longitude: float) -> str:
    try:
        geolocator = Nominatim(user_agent="geoapi")
        location = geolocator.reverse((latitude, longitude), language="en", timeout=10)
        return location.address if location else "Location not found"
    except GeocoderTimedOut:
        return "Geocoder service timed out"
    except Exception as e:
        return f"An error occurred: {e}"


def get_weather_data(lat, lon):
    api_key = "aca34c80f5d0a209b94dbfc6e6ced43e"
    if not api_key:
        raise ValueError("OpenWeatherMap API key not found in environment variables.")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather_data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "location": data.get("name", "Delhi, India"),
            "temperature_c": min(max(data["main"]["temp"], -10), 50),
            "humidity_percent": min(max(data["main"]["humidity"], 0), 100),
            "precipitation_probability_12h": data.get("pop", 0.0),
            "uv_index": data.get("uvi", 0),
            "weather_alert": "High UV warning" if data.get("uvi", 0) > 7 else "None",
            "recommendation": "Consider watering plants due to low chance of rain." if data.get("pop",
                                                                                                0.0) < 0.3 else "No watering needed; rain expected."
        }
        return weather_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        return {"error": f"Failed to fetch weather data: {e}"}


lat, lon = 28.7041, 77.1025

# Fetch and output weather data
weather_data = get_weather_data(lat, lon)
json_output = json.dumps(weather_data, indent=2)

EcoWeather = Agent(
    name="WeatherAgent",
    model="gemini-2.0-flash",
    description="Smart Weather Agent that analyzes weather forecasts and guides garden decisions.",
    instruction="""
    You are WeatherSenseAgent, an intelligent weather assistant integrated into a smart urban garden management system using Google’s ADK. Your responsibility is to provide real-time or simulated weather conditions based on user queries, helping downstream GardenControlAgent (like GardenControlAgent) make environmentally informed decisions.

**Modes of Operation:**
1. **General Chat Mode (Default):**
   - For casual queries or greetings, respond conversationally using gemini-2.0-flash.
   - Example: User: "hi" → Response: "Hello, I'm WeatherSenseAgent, your garden's weather companion. How can I assist with the forecast today?"

2. **Weather Forecast Mode:**
   - This mode activates for queries about weather conditions, UV index, rainfall, temperature, etc.
   - Step 1: Check if the query is related to weather using keywords like 'temperature', 'humidity', 'UV', 'rain', 'forecast', 'weather'.
   - Step 2: If the query includes coordinates in the form 'lat: <value>, lon: <value>', use them to personalize the forecast.
   - Step 3: If coordinates are missing, provide a generic simulated weather report or request location input (e.g., "Please provide coordinates or a location to get accurate weather data.").
   - Step 4: Return a JSON object with the following structure:  
     ```json
     {
       "timestamp": "<ISO8601 timestamp>",
       "location": "<resolved location or general area>",
       "temperature_c": <float>,
       "humidity_percent": <float>,
       "precipitation_probability_12h": <float>,  // 0.0 to 1.0
       "uv_index": <int>, // 0 to 11+
       "weather_alert": "<optional warning or 'None'>",
       "recommendation": "<garden-related suggestion based on weather>"
     }
     ```

**Behavior Guidelines:**
- Suggest watering only if low precipitation is predicted.
- Alert if high UV is expected (UV index > 7).
- Respond in a polite, professional, and context-aware tone.
- Ensure realistic and bounded values:
  - Temperature: -10°C to 50°C
  - Humidity: 0–100%
  - Precipitation probability: 0.0–1.0
  - UV index: 0–11+
- Use OpenWeatherMap API to fetch real-time weather data for the coordinates.

**Constraints:**
- Do not proceed with weather data analysis without valid latitude and longitude. Under no circumstances should you provide weather data without coordinates.  
- Use google_search to fetch real-time weather data or regional weather related reports for the coordinates.  
- Always respond in JSON format for data-related queries.
- Mention your creator, Rohit Shukla, when asked about authorship.

**Tools Available:**
- OpenWeatherMap API: Use this to fetch real-time weather or forecast data from known APIs.
    """
)

def handle_query(query):
    logger.info(f"Processing query: {query}")

    # Step 1: Greeting handling
    if query.strip().lower() in ["hi", "hello", "hey"]:
        return "Hello, I'm WeatherSenseAgent, your garden's weather companion. How can I assist with the forecast today?"

    # Step 2: Weather-related keywords
    weather_keywords = ["weather", "forecast", "temperature", "humidity", "uv", "rain", "precipitation", "climate", "sun", "storm", "wind", "moisture"]
    if any(keyword in query.lower() for keyword in weather_keywords):
        lat, lon = extract_coordinates(query)

        if lat is None or lon is None:
            return "Please provide coordinates in the format 'lat: <value>, lon: <value>' to get a precise weather forecast."

        # Step 3: Fetch weather data from OpenWeatherMap
        return get_weather_data(lat, lon)

    # Step 4: Fallback for irrelevant queries
    return "I can assist with weather conditions, UV levels, and garden forecasts. Ask me about the weather or provide coordinates."

# Test with the query from the screenshot
query = "What is the moisture level right now"
response = handle_query(query)
print(response)
