#!/usr/bin/env python3
import os
import json
import time
import requests
from collections import defaultdict

# ——— CONFIGURATION ———
URL = "http://127.0.0.1:8000/data"
#URL = "https://ashtonrwsmith.pythonanywhere.com/data"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": "your-secret-api-key"
}
JSON_DIR = "/Users/avery.austin/Desktop/IPG/CROW/DroneTracker/json_data"

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

        # Send raw packet; server will enrich it with deviation + cumulative
        resp = requests.post(URL, headers=HEADERS, json=packet)
        print(f"[{flight_name}] Sent {fname} | HTTP {resp.status_code}")

    time.sleep(1)
