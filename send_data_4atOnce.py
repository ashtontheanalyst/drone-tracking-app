#!/usr/bin/env python3
import os
import json
import time
import requests
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point
from collections import defaultdict

# ——— CONFIGURATION ———
URL = "http://127.0.0.1:8000/data"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": "your-secret-api-key"
}
JSON_DIR = "/home/andrew/Desktop/summerCROW/json_data"

flight_paths = {
    "Disaster_City_Survey":       "Disaster_City_Survey_V2_converted.xlsx",
    "RELLIS_North_to_Hearne":     "RELLIS_NORTH_-_REL→Hearne_converted.xlsx",
    "RELLIS_South_to_AggieFarm":  "RELLIS_SOUTH_-_REL_→_AggieFarm_converted.xlsx",
    "RELLIS_West_to_Caldwell":    "RELLIS_WEST_-_REL_→_Caldwell_converted.xlsx"
}

# ——— LOAD FLIGHT PATH LINES ———
path_lines = {}
for name, xlsx in flight_paths.items():
    df = (
        pd.read_excel(os.path.join(JSON_DIR, xlsx), sheet_name="in")[['Latitude','Longitude','Altitude']]
        .dropna()
        .reset_index(drop=True)
    )
    coords = list(zip(df['Longitude'], df['Latitude']))
    path_lines[name] = LineString(coords)

# ——— GROUP TELEMETRY JSON FILES BY FLIGHT NAME ———
json_files = sorted(f for f in os.listdir(JSON_DIR) if f.endswith('.json'))
flight_json_map = defaultdict(list)
for fname in json_files:
    if '_deviated_telemetry_' not in fname:
        continue
    flight_name = fname.split('_deviated_telemetry_')[0]
    if flight_name in path_lines:
        flight_json_map[flight_name].append(fname)

# ——— CREATE ITERATORS FOR EACH FLIGHT PATH ———
for flist in flight_json_map.values():
    flist.sort()
flight_iters = {name: iter(files) for name, files in flight_json_map.items()}
active_flights = set(flight_iters.keys())

# ——— INITIALIZE CUMULATIVE DEVIATION COUNTERS ———
cumulative_dev_sum_map = {name: 0.0 for name in flight_iters.keys()}

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

        # compute instantaneous deviation
        lat = packet['position']['latitude']
        lon = packet['position']['longitude']
        pt = Point(lon, lat)
        path = path_lines[flight_name]
        nearest = path.interpolate(path.project(pt))
        dist_m = pt.distance(nearest) * 111000  # degrees → meters
        dist_ft = dist_m * 3.28084
        packet['deviation'] = round(dist_ft, 2)

        # accumulate only the 'over-25 ft' portion
        if packet['deviation'] > 25:
            cumulative_dev_sum_map[flight_name] += (packet['deviation'] - 25)
        packet['cumulative_dev_sum'] = round(cumulative_dev_sum_map[flight_name], 2)

        # send enriched packet
        resp = requests.post(URL, headers=HEADERS, json=packet)
        print(f"[{flight_name}] Sent {fname} → deviation {packet['deviation']} ft | "
              f"cum_sum {packet['cumulative_dev_sum']} ft | HTTP {resp.status_code}")

    time.sleep(1)

