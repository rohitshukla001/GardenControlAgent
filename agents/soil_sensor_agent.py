import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "soil_sensor_data"
LOCATIONS = ["Bed A", "Bed B", "Bed C"]

# Simulate soil sensor data
def generate_soil_data(location):
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": location,
        "moisture": round(random.uniform(20.0, 80.0), 1),  # 20-80%
        "ph": round(random.uniform(5.5, 7.5), 1),         # 5.5-7.5
        "nitrogen": random.randint(5, 20),                # 5-20 ppm
        "phosphorus": random.randint(3, 15),              # 3-15 ppm
        "potassium": random.randint(5, 20)                # 5-20 ppm
    }

# MQTT client setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Main loop
def run_soil_sensor_agent():
    try:
        while True:
            for location in LOCATIONS:
                # Generate data
                soil_data = generate_soil_data(location)
                # Format as IoT Core-like payload
                payload = json.dumps(soil_data)
                # Publish to ADK topic
                client.publish(MQTT_TOPIC, payload)
                print(f"Published: {payload}")
            time.sleep(10)  # Simulate data every 10 seconds
    except KeyboardInterrupt:
        print("Stopping SoilSensorAgent...")
        client.disconnect()

if __name__ == "__main__":
    run_soil_sensor_agent()