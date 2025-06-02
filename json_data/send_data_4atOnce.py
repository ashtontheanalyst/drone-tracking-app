#!/usr/bin/env python3
import os
import json
import time
import requests
from collections import defaultdict
from dotenv import load_dotenv

# ——— CONFIGURATION ———
#URL = "https://ashtonrwsmith.pythonanywhere.com/data"
URL = "http://127.0.0.1:8000/data"

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}
JSON_DIR = "/Users/avery.austin/Desktop/IPG/CROW/DroneTracker/json_data"

# ——— MAP FLIGHT NAMES TO CALLSIGNS ———
FLIGHT_NAME_TO_CALLSIGN = {
    "RELLIS_North_to_Hearne": "DUSKY18",
    "RELLIS_West_to_Caldwell": "DUSKY21",
    "RELLIS_South_to_AggieFarm": "DUSKY24",
    "Disaster_City_Survey": "DUSKY27"
}

# ——— COLLECT JSON FILES BY FLIGHT NAME ———
json_files = sorted(f for f in os.listdir(JSON_DIR) if f.endswith('.json'))
flight_json_map = defaultdict(list)

for fname in json_files:
    if '_deviated_telemetry_' not in fname:
        continue
    flight_name = fname.split('_deviated_telemetry_')[0]
    flight_json_map[flight_name].append(fname)

# ——— CREATE ITERATORS FOR EACH FLIGHT ———
for flist in flight_json_map.values():
    flist.sort()

flight_iters = {name: iter(files) for name, files in flight_json_map.items()}
active_flights = set(flight_iters.keys())

# ——— LOOP: SEND ONE PACKET PER FLIGHT PER SECOND ———
while active_flights:
    for flight_name in list(active_flights):
        try:
            fname = next(flight_iters[flight_name])
        except StopIteration:
            active_flights.remove(flight_name)
            continue

        full_path = os.path.join(JSON_DIR, fname)
        with open(full_path) as f:
            packet = json.load(f)

        # Override the callsign in the packet
        new_callsign = FLIGHT_NAME_TO_CALLSIGN.get(flight_name)
        if new_callsign:
            packet["call_sign"] = new_callsign

        # Print callsign and filename being sent
        print(f"Sending file: {fname} | callsign: {packet.get('call_sign')}")

        # Send the packet
        resp = requests.post(URL, headers=HEADERS, json=packet)
        print(f"→ HTTP Status: {resp.status_code}")

    time.sleep(1)
