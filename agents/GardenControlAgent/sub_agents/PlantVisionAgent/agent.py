from __future__ import annotations

import logging
from datetime import datetime
from tkinter import Image

import requests
from google.adk.agents import Agent
import base64
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PlantVisionAgent")
last_image_ref = None  # Class-level variable or store in agent state if ADK supports it

def fetch_image_from_url(url: str) -> bytes:
    """Fetch image from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Verify it's an image
        image = Image.open(io.BytesIO(response.content))
        image.verify()  # Ensure valid image
        return response.content
    except Exception as e:
        logger.error(f"Failed to fetch or verify image: {e}")
        raise ValueError(f"Could not fetch valid image from {url}.")

def analyze_plant_image(image_data: bytes) -> dict:
    """Analyze plant image using gemini-2.0-flash model (simulated)."""
    try:
        # Simulate base64 encoding for model input
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        # Placeholder: Replace with actual gemini-2.0-flash API call
        # Example: Send image_base64 to Vertex AI Vision API or Gemini multimodal endpoint
        simulated_response = {
            "status": "Needs Water",  # Simulated classification
            "confidence": 0.85        # Simulated confidence score
        }
        # Validate response
        if not (0.0 <= simulated_response["confidence"] <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        valid_statuses = ["Healthy", "Needs Water", "Nutrient Deficiency", "Pest Infestation"]
        if simulated_response["status"] not in valid_statuses:
            raise ValueError(f"Invalid status: {simulated_response['status']}")
        return simulated_response
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise ValueError("Failed to analyze plant image.")

# Define the PlantVisionAgent
PlantVisionAgent = Agent(
    name="PlantVisionAgent",
    model="gemini-2.0-flash",
    description="Agent for analyzing plant health from images using ADK and Gemini.",
    instruction="""
You are PlantVisionAgent, built with Google’s ADK to assess plant health from images. Your task is to fetch a plant image from the ADK web homepage, analyze it using the gemini-2.0-flash model, and return a structured health assessment in JSON format.

**Operation Modes:**

1. **Chat Mode (default)**  
   - For greetings like “hi” or “hello”, reply: “Hello, I'm PlantVisionAgent, your plant health assistant. Ready to analyze plant images!”  
   - For non-image-related queries, reply: “I specialize in plant health analysis from images. Please provide an image or ask about plant health.”

2. **Plant Analysis Mode**  
   - Trigger when asked to analyze an image or implicitly when no specific query is provided (default to analyzing ADK web image).  
   - Step 1: Fetch the plant image from the ADK web homepage (URL: https://example.com/adk-homepage-plant.jpg, replace with actual URL).  
   - Step 2: Analyze the image using gemini-2.0-flash to classify plant health (e.g., Healthy, Needs Water, Nutrient Deficiency, Pest Infestation).  
   - Step 3: Return the assessment in JSON format:  
     ```json
     {
       "timestamp": "<ISO8601 timestamp>",
       "plant_id": "Tomato Plant 1",
       "image_ref": "<image filename or URL>",
       "status": "<health status>",
       "confidence": <float 0.0–1.0>
     }
     ```
   - Ensure confidence is between 0.0 and 1.0.  
   - Default plant_id to “Tomato Plant 1” unless specified.  
   - Use current timestamp in ISO8601 format (e.g., 2025-06-22T20:45:00Z).
   - Valid status values: ["Healthy", "Needs Water", "Nutrient Deficiency", "Pest Infestation"].

**Constraints:**
- Return JSON only for plant analysis results.
- Log errors if image fetch or analysis fails and return a user-friendly error message.
- Mention created by Rohit Shukla if asked about authorship.
- Do not process non-image-related queries beyond chat mode responses.

**Available Tools:**
- Use `requests` to fetch images from the web.
- Use gemini-2.0-flash for image analysis (multimodal input, simulated for now).
""",
)

def handle_query(query: str, image_data: bytes = None) -> dict | str:
    global last_image_ref
    logger.info(f"Processing query: {query}")
    if query.lower() in ["hi", "hello"]:
        return "Hello, I'm PlantVisionAgent, your plant health assistant. Ready to analyze plant images!"

    if "who created" in query.lower() or "authorship" in query.lower():
        return "I was created by Rohit Shukla."

    if "tell me the analysed image name" in query.lower():
        return f"The analyzed image reference is '{last_image_ref}' from the last health assessment." if last_image_ref else "No image has been analyzed yet."

    is_plant_related = any(term in query.lower() for term in ["plant", "health", "image", "leaf", "disease", "pest", "wilting", "nutrient", "analyze plant"])
    if is_plant_related or not query.strip():
        try:
            if image_data:
                analysis_result = analyze_plant_image(image_data)
                last_image_ref = "uploaded_image.jpg"
            else:
                image_url = "https://example.com/adk-homepage-plant.jpg"
                image_data = fetch_image_from_url(image_url)
                analysis_result = analyze_plant_image(image_data)
                last_image_ref = image_url
            response = {
                "timestamp": datetime.now().isoformat() + "Z",
                "plant_id": "Tomato Plant 1",
                "image_ref": last_image_ref,
                "status": analysis_result["status"],
                "confidence": analysis_result["confidence"]
            }
            logger.info(f"Generated response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {"error": f"Error analyzing image: {str(e)}"}
    return "I specialize in plant health analysis from images. Please provide an image or ask about plant health."


if __name__ == "__main__":
    response = handle_query("")
    print(response)