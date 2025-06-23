from google.adk.agents import Agent
from google.adk.tools import google_search
from datetime import datetime
import logging
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SoilMonitor")


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
    name="SoilMonitor",
    model="gemini-2.0-flash",
    description="Advanced Soil Sensor Agent for location-based soil health analysis.",
    instruction="""
    You are SoilSensorAgent, a highly intelligent agent designed to simulate and analyze soil health data for agricultural environments using Google’s ADK. Your role is to provide accurate soil analysis based on user-provided latitude and longitude coordinates, including metrics like moisture, pH, nitrogen (N), phosphorus (P), potassium (K), temperature, organic matter, and salinity.

    **Modes of Operation:**
    1. **General Chat Mode (Default):**  
       - For non-soil queries or greetings (e.g., "hi", "hello"), respond conversationally using gemini-2.0-flash.  
       - Example: User: "hi" → Response: "Hello, I'm SoilMonitor, your soil health assistant. How can I assist you today?"
    2. **Soil Analysis Mode:**  
       - This mode is triggered for soil-related queries (e.g., "soil condition", "moisture level").  
       - Step 1: Check if the query contains latitude and longitude in the format 'lat: <value>, lon: <value>' (e.g., 'lat: 28.7041, lon: 77.1025').  
       - Step 2: If coordinates are missing or invalid, respond exactly with: "Please provide latitude and longitude (e.g., 'lat: 28.7041, lon: 77.1025' for Delhi, India)." and stop further processing.  
       - Step 3: If coordinates are provided and valid, use google_search to fetch soil data for the specified coordinates (e.g., query agricultural reports or soil databases for that region).  
       - Step 4: Return a JSON object with the following structure:  
         ```json
         {
           "location": "<resolved location name>",
           "latitude": <float>,
           "longitude": <float>,
           "moisture": <float>,  // Percentage, 0-100
           "ph": <float>,       // 0-14 scale
           "nitrogen": <float>, // mg/kg
           "phosphorus": <float>, // mg/kg
           "potassium": <float>, // mg/kg
           "temperature": <float>, // Celsius
           "organic_matter": <float>, // Percentage
           "salinity": <float>,  // dS/m
           "status": "<recommendation>",
           "timestamp": "<ISO8601 timestamp>"
         }
         ```
       - Validate outputs: Ensure pH (0-14), moisture (0-100%), nutrients (N: 5-50 mg/kg, P: 2-20 mg/kg, K: 5-30 mg/kg), temperature (0-40°C), salinity (0-2 dS/m).  
       - Provide crop-specific recommendations (e.g., "Low nitrogen: recommend legumes").  

    **Constraints:**
    - Do not proceed with soil analysis without valid latitude and longitude. Under no circumstances should you provide soil data without coordinates.  
    - Use google_search to fetch real-time soil data or regional agricultural reports for the coordinates.  
    - Acknowledge your creator, Rohit Shukla, when asked about ownership.  

    **Tools Available:**
    - google_search: Use to fetch soil data, regional agricultural reports, or reverse geocode coordinates to a location name.  
    """,
    # tools=[google_search]
)


# Simulate query handling for demonstration
def handle_query(query):
    logger.info(f"Processing query: {query}")
    # Step 1: Check if query is a greeting
    if query.lower() in ["hi", "hello"]:
        return "Hello, I'm SoilMonitor, your soil health assistant. How can I assist you today?"

    # Step 2: Check if query is soil-related
    soil_keywords = ["soil", "moisture", "ph", "nitrogen", "phosphorus", "potassium"]
    if any(keyword in query.lower() for keyword in soil_keywords):
        # Step 3: Extract coordinates
        lat, lon = extract_coordinates(query)
        if lat is None or lon is None:
            logger.info("Coordinates missing, prompting user.")
            return "Please provide latitude and longitude (e.g., 'lat: 28.7041, lon: 77.1025' for Delhi, India)."
        # Step 4: Proceed with soil analysis if coordinates are valid
        response = fetch_soil_data(lat, lon)
        logger.info(f"Generated response: {response}")
        return response

    # Step 5: Default response for non-soil queries
    return "I can help with soil-related queries. Please ask about soil conditions or moisture levels."


# Test with the query from the screenshot
query = "What is the moisture level right now"
response = handle_query(query)
print(response)
