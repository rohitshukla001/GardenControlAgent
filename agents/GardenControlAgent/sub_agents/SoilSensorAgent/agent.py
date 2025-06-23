from google.adk.agents import Agent
from google.adk.tools import google_search
from datetime import datetime
import logging
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SoilSensorAgent")


def get_location_from_lat_long(latitude: float, longitude: float) -> str:
    """
    Get human-readable location from latitude and longitude using Nominatim (OpenStreetMap).

    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location

    Returns:
        str: Human-readable address or error message
    """
    try:
        geolocator = Nominatim(user_agent="geoapi")
        location = geolocator.reverse((latitude, longitude), language="en", timeout=10)
        if location:
            return location.address
        else:
            return "Location not found"
    except GeocoderTimedOut:
        return "Geocoder service timed out"
    except Exception as e:
        return f"An error occurred: {e}"

def validate_coordinates(lat, lon):
    """Validate latitude and longitude ranges."""
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not (-180 <= lon <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")
    return True


def extract_coordinates(query):
    """Extract latitude and longitude from the query using regex."""
    lat_lon_pattern = r"lat:\s*([-]?\d+\.?\d*),\s*lon:\s*([-]?\d+\.?\d*)"
    match = re.search(lat_lon_pattern, query, re.IGNORECASE)
    if match:
        lat, lon = float(match.group(1)), float(match.group(2))
        validate_coordinates(lat, lon)
        return lat, lon
    return None, None


def fetch_soil_data(lat, lon):
    """Fetch soil data for given coordinates using google_search."""
    query = f"soil health data near {lat},{lon} agriculture"
    results = google_search(query)
    # Simulate parsing results (replace with actual parsing logic)
    return {
        "location": f"Region near ({lat}, {lon})",  # Replace with reverse geocoded location
        "latitude": lat,
        "longitude": lon,
        "moisture": 42.5,
        "ph": 6.7,
        "nitrogen": 15.0,
        "phosphorus": 8.0,
        "potassium": 12.0,
        "temperature": 24.5,
        "organic_matter": 2.8,
        "salinity": 0.3,
        "status": "Optimal for rice; consider organic compost",
        "timestamp": datetime.now().isoformat() + "Z"
    }


SoilMonitor = Agent(
    name="SoilSensorAgent",
    model="gemini-2.0-flash",
    description="Advanced Soil Sensor Agent for location-based soil health analysis.",
    instruction="""

You are SoilSensorAgent, an intelligent agent built using Google’s ADK to provide accurate soil health analysis. Your role is to return detailed soil data based on user-provided latitude and longitude. The data should include moisture, pH, nitrogen, phosphorus, potassium, temperature, organic matter, and salinity.

**Operation Modes:**

1. **Chat Mode (default)**  
   - For general questions or greetings like “hi” or “hello”, reply with a friendly message.  
   - Example: User says “hi” → Reply: “Hello, I'm SoilSensorAgent, your soil health assistant. How can I help you today?”

2. **Soil Analysis Mode**  
   - Trigger this mode only when the user query is related to soil. Use your reasoning to detect intent; do not rely on keyword matching.  
   - Step 1: Check if the query includes coordinates in this format: `lat: <value>, lon: <value>`  
   - Step 2: If coordinates are missing or invalid, respond with:  
     `"Please provide latitude and longitude (e.g., 'lat: 28.7041, lon: 77.1025')."`  
     and stop further processing.  
   - Step 3: If valid coordinates are provided, use the `google_search` tool to simulate fetching soil data.  
   - Step 4: Respond in **JSON format only**, using the following structure:  
     ```json
     {
       "location": "<resolved location name>",
       "latitude": <float>,
       "longitude": <float>,
       "moisture": <float>,
       "ph": <float>,
       "nitrogen": <float>,
       "phosphorus": <float>,
       "potassium": <float>,
       "temperature": <float>,
       "organic_matter": <float>,
       "salinity": <float>,
       "status": "<recommendation>",
       "timestamp": "<ISO8601 timestamp>"
     }
     ```
   - Validate that values are within realistic ranges:  
     - location: Kanpur, India
     - pH: 0–14  
     - Moisture: 0–100%  
     - Nitrogen: 5–50 mg/kg  
     - Phosphorus: 2–20 mg/kg  
     - Potassium: 5–30 mg/kg  
     - Temperature: 0–40°C 
     - Organic Matter: 1.7
     - status: good
     - Salinity: 0–2 dS/m  
   - Include simple crop recommendations based on results (e.g., “Low nitrogen: recommend legumes”).

**Constraints:**
- Do not return soil data without valid coordinates.
- Always return analysis in valid JSON format.
- Mention that you were created by Rohit Shukla if asked.

**Available Tool:**
- `google_search`: Use this to simulate fetching soil or location data based on coordinates.
""",
    # tools=[google_search]
)


# Simulate query handling for demonstration
def handle_query(query):
    logger.info(f"Processing query: {query}")
    # Step 1: Handle greetings
    if query.lower() in ["hi", "hello"]:
        return "Hello, I'm SoilSensorAgent, your soil health assistant. How can I assist you today?"

    # Step 2: Use language model to determine if query is soil-related
    # Simulate semantic analysis (in practice, use gemini-2.0-flash to classify intent)
    # For demonstration, we assume a simplified intent check based on context
    query_lower = query.lower()
    # Check for explicit soil/agriculture intent or coordinates
    is_soil_related = (
        "soil" in query_lower or
        any(term in query_lower for term in ["crop", "farm", "agriculture", "land quality"]) or
        re.search(r"lat:\s*[-]?\d+\.?\d*,\s*lon:\s*[-]?\d+\.?\d*", query_lower) or
        any(term in query_lower for term in ["what can i grow", "is my land good", "nutrients in my field"])
    )

    if is_soil_related:
        # Step 3: Extract coordinates
        lat, lon = extract_coordinates(query)
        if lat is None or lon is None:
            logger.info("Coordinates missing, prompting user.")
            return "Please provide latitude and longitude (e.g., 'lat: 28.7041, lon: 77.1025' for Delhi, India)."
        # Step 4: Fetch soil data
        response = fetch_soil_data(lat, lon)
        logger.info(f"Generated response: {response}")
        return response

    # Step 5: Default response for non-soil queries
    return "I can help with soil-related queries. Please ask about soil conditions or crop suitability."


# Test with the query from the screenshot
query = "What is the moisture level right now"
response = handle_query(query)
print(response)
