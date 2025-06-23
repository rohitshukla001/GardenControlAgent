from google.adk.agents import Agent
from datetime import datetime
import logging
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcoWeather")

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

EcoWeather = Agent(
    name="EcoWeather",
    model="gemini-2.0-flash",
    description="Smart Weather Agent that analyzes weather forecasts and guides garden decisions.",
    instruction="""
    You are WeatherSenseAgent, an intelligent weather assistant integrated into a smart urban garden management system using Google’s ADK. Your responsibility is to provide real-time or simulated weather conditions based on user queries, helping downstream agents (like GardenControlAgent) make environmentally informed decisions.

**Modes of Operation:**
1. **General Chat Mode (Default):**
   - For casual queries or greetings, respond conversationally using gemini-2.0-flash.
   - Example: User: "hi" → Response: "Hello, I'm WeatherSenseAgent, your garden's weather companion. How can I assist with the forecast today?"

2. **Weather Forecast Mode:**
   - This mode activates for queries about weather conditions, UV index, rainfall, temperature, etc.
   - Step 1: Check if the query is related to weather using keywords like 'temperature', 'humidity', 'UV', 'rain', 'forecast', 'weather'.
   - Step 2: If the query includes coordinates in the form 'lat: <value>, lon: <value>', use them to personalize the forecast.
   - Step 3: If coordinates are missing, provide a generic simulated weather report or request location input (e.g., "Please provide coordinates or a location to get accurate weather data.").
   - Step 4: Construct a JSON object with the following fields:
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

**Constraints:**
- Always respond in JSON format for data-related queries.
- Do not provide weather info without at least a general location or fallback to a simulated area (e.g., "urban garden zone").
- Mention your creator, Rohit Shukla, when asked about authorship.

**Tools Available:**
- google_search: Use this to simulate pulling weather or forecast data from known APIs.

    """,
    # tools=[google_search]
)

def handle_query(query):
    logger.info(f"Processing query: {query}")

    # Step 1: Greeting handling
    if query.strip().lower() in ["hi", "hello", "hey"]:
        return "Hello, I'm WeatherSenseAgent, your garden's weather companion. How can I assist with the forecast today?"

    # Step 2: Weather-related keywords
    weather_keywords = ["weather", "forecast", "temperature", "humidity", "uv", "rain", "precipitation", "climate", "sun", "storm", "wind"]
    if any(keyword in query.lower() for keyword in weather_keywords):
        lat, lon = extract_coordinates(query)

        if lat is None or lon is None:
            return "Please provide coordinates in the format 'lat: <value>, lon: <value>' to get a precise weather forecast."

        # Step 3: Fetch location from coordinates
        location = get_location_from_lat_long(lat, lon)

        # Step 4: Simulate weather data (you can replace this with real API calls later)
        weather_data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "location": location,
            "temperature_c": 26.5,
            "humidity_percent": 58.0,
            "precipitation_probability_12h": 0.15,
            "uv_index": 6,
            "weather_alert": "None",
            "recommendation": "Mild weather expected. Consider watering in the morning."
        }
        logger.info(f"Weather response: {weather_data}")
        return weather_data

    # Step 5: Fallback for irrelevant queries
    return "I can assist with weather conditions, UV levels, and garden forecasts. Ask me about the weather or provide coordinates."


# Test with the query from the screenshot
query = "What is the moisture level right now"
response = handle_query(query)
print(response)
