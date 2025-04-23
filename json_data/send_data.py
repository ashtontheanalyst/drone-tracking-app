import os
import json
import time
import requests
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

# ——— CONFIGURATION ———
URL = "http://127.0.0.1:8000/data"
HEADERS = {"Content-Type": "application/json"}

JSON_DIR = "/home/goose/apps/DroneTracker/json_data"

flight_paths = {
    "Disaster_City_Survey":       "Disaster_City_Survey_V2_converted.xlsx",
    "RELLIS_North_to_Hearne":     "RELLIS_NORTH_-_REL→Hearne_converted.xlsx",
    "RELLIS_South_to_AggieFarm":  "RELLIS_SOUTH_-_REL_→_AggieFarm_converted.xlsx",
    "RELLIS_West_to_Caldwell":    "RELLIS_WEST_-_REL_→_Caldwell_converted.xlsx"
}

# ——— PRELOAD FLIGHT PLANS ———
path_lines = {}
for name, xlsx in flight_paths.items():
    df = (pd.read_excel(xlsx, sheet_name="in")
            [["Latitude","Longitude","Altitude"]]
            .dropna()
            .reset_index(drop=True))
    # build LineString in (lon, lat) order
    coords = list(zip(df["Longitude"], df["Latitude"]))
    path_lines[name] = LineString(coords)

# ——— ITERATE JSON FILES ———
json_files = sorted(f for f in os.listdir(JSON_DIR) if f.endswith(".json"))
for fname in json_files:
    # extract flight key from filename convention
    if "_deviated_telemetry_" not in fname:
        continue
    flight_name = fname.split("_deviated_telemetry_")[0]
    if flight_name not in path_lines:
        print(f"⚠️  Skipping {fname}: no flight plan for '{flight_name}'")
        continue

    # load JSON
    full_path = os.path.join(JSON_DIR, fname)
    with open(full_path) as f:
        packet = json.load(f)

    # compute deviation
    lat = packet["position"]["latitude"]
    lon = packet["position"]["longitude"]
    pt = Point(lon, lat)
    line = path_lines[flight_name]
    nearest = line.interpolate(line.project(pt))
    # approximate degrees→meters (111 km per degree), then →feet
    dist_m = pt.distance(nearest) * 111000
    dist_ft = dist_m * 3.28084
    packet["deviation"] = round(dist_ft, 2)

    # POST to your web endpoint
    resp = requests.post(URL, headers=HEADERS, json=packet)
    print(f"Sent {fname} → deviation {packet['deviation']} ft  |  HTTP {resp.status_code}")

    # wait 1 second before next
    time.sleep(1)

