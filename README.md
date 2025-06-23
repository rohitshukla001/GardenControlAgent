# FloraOS: The Intelligent Bloom - Autonomous Urban Garden Management System

![resized floraos_official](https://github.com/user-attachments/assets/8a8359be-a0af-42d6-a9af-a5aafb523832)

The Smart Garden Automation System, FloraOS, is an intelligent platform for urban garden management, built using Google's Agent Development Kit (ADK). It demonstrates the power of multi-agent systems to automate complex environmental monitoring and decision-making processes. FloraOS coordinates weather, soil health, and plant vision data to provide actionable insights and simulated automated responses for gardeners, showcasing how sophisticated automation, typically seen in robotics or IT, can be applied to biological and environmental systems. This project directly addresses the "Automation of Complex Processes" challenge by designing a multi-agent workflow to manage the intricate tasks of urban gardening.

## Core Problem & Our Solution

Managing urban gardens involves constant monitoring of diverse data (soil, weather, plant health) and coordinating actions (watering, nutrients). Manual management is inefficient.

**FloraOS automates this by orchestrating four distinct agents via ADK:**

1.  **SoilSensorAgent:** Simulates soil sensor readings (moisture, pH, NPK) from a predefined dataset, publishing structured data.
2.  **WeatherAgent:** Fetches current weather and forecasts using the OpenWeatherMap API (or simulated data), publishing structured weather updates.
3.  **PlantVisionAgent:** Analyzes plant images using **Google Cloud Vertex AI Vision** (Custom Classification Model) to assess health status (e.g., "Needs Water," "Nutrient Deficient"), publishing these assessments.
4.  **GardenControlAgent (The Brain):** Subscribes to data from all other agents. Applies rule-based logic (e.g., if soil is dry, no rain forecasted, and plant is wilting, then trigger watering) and publishes (simulated) action commands.

This creates an automated feedback loop for garden care.

## ✨ Features & Functionality

**Overview:** FloraOS automates the monitoring and management of a simulated urban garden by orchestrating specialized agents that gather diverse environmental data, analyze it, and determine appropriate actions.

**Key Features & Innovation**

*   **Multi-Agent Orchestration with ADK:** Demonstrates ADK's power to coordinate specialized agents for a complex task.
*   **AI-Powered Perception:** Integrates Vertex AI Vision for intelligent plant health assessment from images.
*   **Autonomous Decision-Making:** The GardenControlAgent makes data-driven decisions based on inputs from multiple sources.
*   **Environmental Automation:** Applies sophisticated automation concepts to a biological/environmental system.
*   **Structured Data Flow:** Clear JSON message schemas for robust inter-agent communication.

**Detailed Breakdown & Agent Orchestration:**

FloraOS employs a multi-agent system where each agent has a distinct role, communicating and collaborating via ADK to automate the garden management workflow:
  
1.  **SoilSensorAgent:**
    *   **Function:** Simulates reading and publishing crucial soil sensor data.
    *   **Data:** Generates or reads from a predefined dataset (CSV/JSON) mimicking soil conditions (moisture %, pH, nutrient levels - NPK). This data is structured similarly to an IoT Core message payload.
    *   **Output:** Publishes structured soil data (e.g., `{ "timestamp": "...", "location": "Bed A", "moisture": 45.2, "ph": 6.5, "nitrogen": 10, "phosphorus": 5, "potassium": 8 }`).
    *   **Automation Role:** Provides foundational ground-truth data for decision-making.

2.  **WeatherAgent:**
    *   **Function:** Fetches current weather conditions and short-term forecast data.
    *   **Data:** Uses a public API (e.g., OpenWeatherMap) for real-time data or a simulated forecast dataset for reliability.
    *   **Output:** Publishes structured weather data (e.g., `{ "timestamp": "...", "location": "Garden Area", "temp_c": 22.0, "humidity": 60, "precipitation_prob_next_12h": 0.1, "uv_index": 5 }`).
    *   **Automation Role:** Introduces external environmental factors into the decision matrix.

3.  **PlantVisionAgent:**
    *   **Function:** Analyzes simulated images of plants to assess their health status.
    *   **Data:** Takes pre-selected image files representing different plant states (healthy, wilting, nutrient deficient, pest infestation).
    *   **GCP Integration:** Utilizes **Google Cloud Vertex AI Vision API** (a Custom Classification model trained on example images) to classify the plant's condition.
    *   **Output:** Publishes plant health assessment (e.g., `{ "timestamp": "...", "plant_id": "Tomato Plant 1", "image_ref": "sim_img_001.jpg", "status": "Needs Water", "confidence": 0.85 }`).
    *   **Automation Role:** Adds a sophisticated perception layer, enabling direct assessment of plant well-being.

4.  **GardenControlAgent (The "Brain"):**
    *   **Function:** Subscribes to data streams from the SoilSensorAgent, WeatherAgent, and PlantVisionAgent. It applies decision logic to determine necessary actions for garden management.
    *   **Decision Logic (MVP):** Rule-based. Examples:
        *   `IF SoilSensorAgent.moisture < threshold AND WeatherAgent.precipitation_prob_next_12h < low_threshold AND PlantVisionAgent.status == "Needs Water" THEN trigger watering.`
        *   `IF PlantVisionAgent.status == "Potential Nutrient Deficiency" THEN trigger specific nutrient delivery.`
        *   `IF SoilSensorAgent.ph outside optimal range THEN recommend pH adjustment action.`
    *   **Output:** Publishes simulated actuation commands (e.g., `{ "timestamp": "...", "action": "ACTIVATE_WATERING", "target": "Bed A", "duration_minutes": 5 }`).
    *   **Automation Role:** Orchestrates the overall process by consuming information from specialized agents, making intelligent decisions, and dispatching commands, thus automating a complex multi-step feedback loop.

## 🛠️ Tech Stack 

*   **Core Orchestration:** Google Agent Development Kit (ADK)
*   **Programming Language:** Python 3.7+
*   **Google Cloud Platform (GCP):**
    *   **Vertex AI Vision:** For image-based plant health classification by the PlantVisionAgent (Custom Image Classification Model).
    *   *(Conceptual Link for future extension: Cloud IoT Core for real-world sensor integration, Cloud Functions for serverless agent logic).*
*   **APIs:** OpenWeatherMap API (for WeatherAgent)
*   **Data Handling:** JSON (for inter-agent messages), CSV/JSON (for simulated sensor data).
*   **Version Control:** Git

## 📊 Data Sources

*   **Soil Data:** Simulated data generated by the `SoilSensorAgent` or read from local CSV/JSON files. This data is curated based on horticultural knowledge to represent various soil states (e.g., optimal, dry, nutrient-deficient).
*   **Weather Data:**
    *   **Primary:** Real-time weather data fetched from the OpenWeatherMap API by the `WeatherAgent`.
    *   **Fallback:** Simulated weather data read from local JSON files for offline testing and controlled demo scenarios.
*   **Plant Image Data:** A curated library of local image files (`.jpg`, `.png`) representing different plant health conditions (healthy, wilting, nutrient-deficient). These images are fed to the `PlantVisionAgent` for analysis via Vertex AI. Images were sourced from public datasets, Wikimedia Commons, and organized for model training and agent input.

## 🏛️ Architecture

1.  **Data Agents (Soil, Weather, PlantVision via Vertex AI)** independently gather and publish specific environmental data to ADK topics.
2.  **ADK Message Bus** facilitates communication.
3.  **GardenControlAgent** subscribes to all relevant data, analyzes the combined information, and publishes action commands.
<img width="1176" alt="image" src="https://github.com/user-attachments/assets/8f9c4379-c158-47f2-bc78-8777cc74328a" />

## 🚀 Getting Started

**Prerequisites:**

*   Python 3.7+ & `pip`
*   Google Cloud SDK (`gcloud` CLI) authenticated (for Vertex AI)
*   OpenWeatherMap API Key
*   Git
*   Google ADK (see official docs for installation)

**Installation & Setup:**

1.  **Clone:**
    ```bash
    git clone [Insert URL to your public GitHub repository here]
    cd flora-os
    ```
2.  **Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # or venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install google-adk # Or specific ADK package
    ```
4.  **Environment Variables:**
    *   Create a `.env` file (see example in repo or detailed docs).
    *   Add `OPENWEATHER_API_KEY=your_key_here`.
    *   Configure GCP Project ID, Region, and Vertex AI Endpoint ID (e.g., in `.env` or ensure `gcloud` is set).
        *   `GCP_PROJECT_ID=your-gcp-project-id`
        *   `GCP_REGION=your-gcp-region`
        *   `VERTEX_AI_ENDPOINT_ID=your-vertex-ai-endpoint-id`

## ⚙️ How to Run & Use

1.  **Ensure ADK runtime/broker is active** (as per your ADK setup).
2.  **Start each agent** in separate terminals (adjust paths as needed):
    ```bash
    python agents/soilsensor_agent/agent.py
    python agents/weather_agent/agent.py
    python agents/plantvision_agent/agent.py
    python agents/gardencontrol_agent/agent.py
    ```
3.  **Observe:** Monitor agent console logs to see data publishing, Vertex AI classifications, and `GardenControlAgent` decisions and actions. Trigger different scenarios by changing input data/images.

## 🔗 Project Links

*   **Hosted Project:** [Insert URL to your deployed FloraOS application here - *If not applicable, state "The project is designed to be run locally. Please see GitHub repository for setup."*]
*   **Public Code Repository:** (https://github.com/rohitshukla001/GardenControlAgent)
*   **Demonstration Video:** [Insert URL to your YouTube or Vimeo demo video here]

## 👥 Team

*   Chichi (AI PM): https://www.linkedin.com/in/chinwenduiwuorie/
*   Susree (Lead AI/ML Engineer): https://www.linkedin.com/in/susree-jyotrimayee-jena-2a110824b/ 
*   Rohit (Software Engineer): https://www.linkedin.com/in/rohitshukla001/



---
