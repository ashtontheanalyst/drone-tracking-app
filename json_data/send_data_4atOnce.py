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
if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set")

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}
JSON_DIR = "/Users/andre/Desktop/BCDC/mysite 2/json_data"

# ——— MAP FLIGHT NAMES TO CALLSIGNS ———
FLIGHT_NAME_TO_CALLSIGN = {
    "RELLIS_North_to_Hearne": "DUSKY18",
    "RELLIS_West_to_Caldwell": "DUSKY21",
    "RELLIS_South_to_AggieFarm": "DUSKY24",
    "Disaster_City_Survey": "DUSKY27"
}

# ——— CARDINAL DIRECTION HELPERS ———
def get_cardinal(angle):
    """Convert degrees (0–360) to one of 8 cardinal directions."""
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    # each sector is 360/8 = 45°, offset so 0° is centered on 'N'
    idx = int((angle + 22.5) // 45) % 8
    return dirs[idx]

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

        # Extract heading & compute cardinal
        heading = None
        cardinal = None
        if ("velocity" in packet and
            isinstance(packet["velocity"], dict) and
            "track" in packet["velocity"]):
            heading = packet["velocity"]["track"]
            cardinal = get_cardinal(heading)

        # Print detailed info
        info = [
            f"Sending file: {fname}",
            f"callsign: {packet.get('call_sign')}"
        ]
        if heading is not None:
            info.append(f"heading: {heading:.2f}° ({cardinal})")
        print(" | ".join(info))

        # Send the packet
        resp = requests.post(URL, headers=HEADERS, json=packet)
        print(f"→ HTTP Status: {resp.status_code}")

    time.sleep(1)

