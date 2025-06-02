# views.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import os
import pandas as pd
from collections import defaultdict
from shapely.geometry import LineString, Point

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Get the API key from the environment
API_KEY = os.getenv("API_KEY")


views = Blueprint(__name__, "views") # Init/create the Blueprint and call it views

# globals
comments = []
ALLOWED_CALLSIGNS = {
    "Disaster_City_Survey",
    "RELLIS_South_to_AggieFarm",
    "RELLIS_West_to_Caldwell",
    "RELLIS_North_to_Hearne"
}

latest_json = {}
history_by_callsign = {}
cumulative_dev_sum_map = defaultdict(float)

# ——— FLIGHT PATH CONFIG ———
FLIGHT_XLSX_DIR = "/Users/andre/Desktop/BCDC/mysite/json_data"
flight_paths = {
    "Disaster_City_Survey":       "Disaster_City_Survey_V2_converted.xlsx",
    "RELLIS_North_to_Hearne":     "RELLIS_NORTH_-_REL→Hearne_converted.xlsx",
    "RELLIS_South_to_AggieFarm":  "RELLIS_SOUTH_-_REL_→_AggieFarm_converted.xlsx",
    "RELLIS_West_to_Caldwell":    "RELLIS_WEST_-_REL_→_Caldwell_converted.xlsx"
}

path_lines = {}
for name, xlsx in flight_paths.items():
    full_path = os.path.join(FLIGHT_XLSX_DIR, xlsx)
    df = (pd.read_excel(full_path, sheet_name="in")
            [["Latitude", "Longitude", "Altitude"]]
            .dropna()
            .reset_index(drop=True))
    coords = list(zip(df["Longitude"], df["Latitude"]))
    path_lines[name] = LineString(coords)

def _make_initial_positions():
    return {
        cs: [line.coords[0][1], line.coords[0][0]]
        for cs, line in path_lines.items()
    }

#-----HOME PAGE---------------------------------------------------------------------------------------------------------------------#
@views.route("/") 
def home():
    initial_positions = _make_initial_positions()
    return render_template(
        "index.html",
        drones=sorted(ALLOWED_CALLSIGNS),
        initial_positions=initial_positions
    )

#-----DRONE PAGE---------------------------------------------------------------------------------------------------------------------#
@views.route("/drone/<call_sign>")
def drone_page(call_sign):
    if call_sign not in ALLOWED_CALLSIGNS:
        return render_template("404.html"), 404

    initial_positions = _make_initial_positions()
    return render_template(
        "droneJ.html",
        call_sign=call_sign,
        drones=sorted(ALLOWED_CALLSIGNS),
        initial_positions=initial_positions
    )

@views.route("/droneJ")
def droneJ():
    return render_template("droneJ.html")

#-----BACKEND PAGES-------------------------------------------------------------------------------------------------------------------#
API_KEY = "your-secret-api-key"

# This will take in JSON data and then post it on the /data page
# Use the testFile.py file to see if the site can get a JSON POST request
# Define your secret key securely in production
#API_KEY = "your-secret-api-key"  
@views.route("/data", methods=["GET", "POST"])
def get_data():
    global latest_json, history_by_callsign

    if request.method == "POST":
        client_key = request.headers.get("X-API-KEY")
        if client_key != API_KEY:
            return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

        latest_json = request.get_json()
        if not latest_json:
            return jsonify({"error": "No JSON data received"}), 400

        call_sign = latest_json.get("call_sign")
        lat = latest_json.get("position", {}).get("latitude")
        lon = latest_json.get("position", {}).get("longitude")

        if call_sign in path_lines and lat is not None and lon is not None:
            pt = Point(lon, lat)
            line = path_lines[call_sign]
            nearest = line.interpolate(line.project(pt))
            dist_m = pt.distance(nearest) * 111000
            dist_ft = dist_m * 3.28084
            deviation = round(dist_ft, 2)
            latest_json["deviation"] = deviation

            if deviation > 25:
                cumulative_dev_sum_map[call_sign] += (deviation - 25)
            latest_json["cumulative_dev_sum"] = round(cumulative_dev_sum_map[call_sign], 2)

        if call_sign:
            history_by_callsign.setdefault(call_sign, []).append(latest_json)

        return jsonify({"message": "JSON received and deviation calculated"}), 200

    return render_template("displayJSON.html", data=latest_json, drones=sorted(ALLOWED_CALLSIGNS))

@views.route("/data/<call_sign>", methods=["GET"])
def data_by_callsign(call_sign):
    data_list = history_by_callsign.get(call_sign, [])
    return jsonify(data_list)

@views.route("/reset_history", methods=["POST"])
def reset_history():
    history_by_callsign.clear()
    cumulative_dev_sum_map.clear()
    return jsonify({"status": "history reset"}), 200

@views.route("/flight_plan/<call_sign>")
def flight_plan(call_sign):
    line = path_lines.get(call_sign)
    if not line:
        return jsonify({"error": "Unknown call_sign"}), 404
    coords = [[lat, lon] for lon, lat in line.coords]
    return jsonify(coords)

