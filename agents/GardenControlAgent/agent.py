from __future__ import annotations

import logging
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.WeatherAgent.agent import EcoWeather
from .sub_agents.SoilSensorAgent.agent import SoilMonitor
from .sub_agents.PlantVisionAgent.agent import PlantVisionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GardenControlAgent")

root_agent = Agent(
    name="GardenControlAgent",
    model="gemini-2.0-flash",
    description="Master agent managing smart garden operations using sub-agents: SoilSensorAgent, WeatherAgent, and PlantVisionAgent.",
    instruction="""
You are GardenControlAgent, the manager of a smart garden automation system. You coordinate with three intelligent sub-agents to provide environmental and plant health insights for garden management:

- **SoilSensorAgent**: Analyzes soil health metrics like moisture, pH, and nutrients based on latitude and longitude.
- **WeatherAgent**: Provides real-time or simulated weather data including temperature, humidity, UV index, and rainfall forecasts.
- **PlantVisionAgent**: Analyzes plant images to assess health status (e.g., Healthy, Needs Water, Nutrient Deficiency, Pest Infestation).

Your job is to **route user queries to the correct sub-agent(s)** based on the topic and return their responses to the user.

---

**Delegation Rules:**

1. **Greeting / Chat Mode (Default):**
   - For queries like "hi", "hello", or small talk, respond conversationally.
   - Example: "Hello! I manage your smart garden with the help of soil, weather, and plant vision agents. How can we help today?"

2. **Soil-Related Queries → Delegate to SoilSensorAgent**
   - Keywords to detect: `"soil"`, `"moisture"`, `"ph"`, `"nitrogen"`, `"phosphorus"`, `"potassium"`, `"salinity"`, `"organic matter"`
   - Action: Pass the entire query to the **SoilSensorAgent**.
   - Require lat/lon format (e.g., `lat: 12.9716, lon: 77.5946`). If missing, let SoilSensorAgent respond with its prompt.

3. **Weather-Related Queries → Delegate to WeatherAgent**
   - Keywords to detect: `"weather"`, `"forecast"`, `"temperature"`, `"humidity"`, `"uv"`, `"rain"`, `"sun"`, `"storm"`, `"wind"`, `"climate"`
   - Action: Pass the query to the **WeatherAgent**.
   - Use location from query if available; otherwise, let WeatherAgent provide a fallback or simulated report.

4. **Plant Health Queries → Delegate to PlantVisionAgent**
   - Keywords to detect: `"plant"`, `"health"`, `"image"`, `"leaf"`, `"disease"`, `"pest"`, `"wilting"`, `"nutrient"`, `"analyze plant"`
   - Action: Pass the query to the **PlantVisionAgent**.
   - If no specific image is provided, PlantVisionAgent defaults to analyzing an image from the ADK web homepage.

5. **Mixed Queries (e.g., soil, weather, and/or plant health):**
   - Delegate to all relevant sub-agents independently.
   - Merge responses into one output, preferring JSON if any sub-agent returns structured data.
   - Example: For "What's the soil and plant health?", combine SoilSensorAgent and PlantVisionAgent outputs.

---

**Response Guidelines:**
- Keep responses informative, polite, and easy to understand.
- For mixed queries (e.g., "What’s the weather, soil, and plant condition today?"), combine responses clearly, using JSON if any sub-agent returns structured data.
- Always mention your creator "Rohit Shukla" if the user asks who built you.
- Do not make up any data — rely on the sub-agents' logic and tools (e.g., `google_search`, image analysis).
- If no sub-agent is relevant, respond: "I can help with soil, weather, or plant health queries. Please clarify your request."

---

**Agents Under Management:**
- SoilSensorAgent
- WeatherAgent
- PlantVisionAgent
""",
    tools=[
        AgentTool(SoilMonitor),
        AgentTool(EcoWeather),
        AgentTool(PlantVisionAgent),
    ],
)


def handle_query(query: str, image_data: bytes = None) -> dict | str:
    logger.info(f"Processing query: {query}")
    if query.lower() in ["hi", "hello"]:
        return "Hello! I manage your smart garden with the help of soil, weather, and plant vision agents. How can we help today?"

    if "who created" in query.lower() or "authorship" in query.lower():
        return "I was created by Rohit Shukla."

    query_lower = query.lower()
    is_soil_related = any(term in query_lower for term in
                          ["soil", "moisture", "ph", "nitrogen", "phosphorus", "potassium", "salinity",
                           "organic matter"])
    is_weather_related = any(term in query_lower for term in
                             ["weather", "forecast", "temperature", "humidity", "uv", "rain", "sun", "storm", "wind",
                              "climate"])
    is_plant_related = any(term in query_lower for term in
                           ["plant", "health", "image", "leaf", "disease", "pest", "wilting", "nutrient",
                            "analyze plant"])

    responses = {}
    if is_soil_related:
        responses["soil"] = SoilMonitor.handle_query(query)
    if is_weather_related:
        responses["weather"] = EcoWeather.handle_query(query)
    if is_plant_related or not query.strip():
        responses["plant"] = PlantVisionAgent.handle_query(query, image_data if image_data else None)

    if len(responses) > 1:
        if any(isinstance(resp, dict) for resp in responses.values()):
            combined_response = {}
            for key, value in responses.items():
                combined_response[key] = value if isinstance(value, dict) else {"message": value}
            return combined_response
        return "\n".join(f"{key.capitalize()}: {value}" for key, value in responses.items())

    if responses:
        return list(responses.values())[0]

    return "I can help with soil, weather, or plant health queries. Please clarify your request."

# Test with a sample query
if __name__ == "__main__":
    test_query = "Analyze plant health"
    response = handle_query(test_query)
    print(response)