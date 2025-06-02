#!/usr/bin/env python3
"""
simulate_and_send.py

This script generates random telemetry for four predefined drones and POSTs each packet 
to the specified endpoint (https://ashtonrwsmith.pythonanywhere.com/data). It loops indefinitely,
sending one update per drone each second.

Requirements:
    pip install requests

Usage:
    python3 simulate_and_send.py
"""

import time
import random
import requests
from datetime import datetime, timezone

# Configuration
ENDPOINT_URL = "https://ashtonrwsmith.pythonanywhere.com/data"
API_KEY = "your-secret-api-key"

# List of the four drones
DRONES = [
    "Disaster_City_Survey",
    "RELLIS_South_to_AggieFarm",
    "RELLIS_West_to_Caldwell",
    "RELLIS_North_to_Hearne"
]

#geographic bounding box for random positions (example: around College Station, TX)
LAT_CENTER = 30.6280
LON_CENTER = -96.3344
LAT_SPAN = 0.02  # ~1.2 miles
LON_SPAN = 0.02  # ~1.2 miles

def generate_random_packet(call_sign):
    """
    generate random telemetry packet for given call_sign
    """
    latitude = LAT_CENTER + (random.random() - 0.5) * LAT_SPAN
    longitude = LON_CENTER + (random.random() - 0.5) * LON_SPAN
    altitude = random.uniform(100, 300)  # altitude between 100 and 300 ft
    airspeed = random.uniform(10, 60)    # airspeed between 10 and 60 m/s

    packet = {
        "call_sign": call_sign,
        "position": {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "altitude": round(altitude, 2)
        },
        "velocity": {
            "airspeed": round(airspeed, 2)
        },
        "time_measured": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    return packet

def send_packet(packet):
    """
    Send a single telemetry packet to the endpoint.
    """
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    try:
        resp = requests.post(ENDPOINT_URL, json=packet, headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[{packet['call_sign']}] Sent at {packet['time_measured']}")
        else:
            print(f"[ERROR {resp.status_code}] {resp.text}")
    except requests.RequestException as e:
        print(f"[EXCEPTION] Failed to send {packet['call_sign']}: {e}")

def main():
    print("Starting telemetry simulation. Press Ctrl+C to stop.")
    while True:
        start = time.time()
        for call_sign in DRONES:
            pkt = generate_random_packet(call_sign)
            send_packet(pkt)
            time.sleep(0.25)  # stagger 4 updates evenly within each second
        # Ensure roughly 1-second intervals between each 4-drone batch
        elapsed = time.time() - start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

if __name__ == "__main__":
    main()

