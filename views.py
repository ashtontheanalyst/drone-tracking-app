#-----SET UP/INIT----------------------------------------------------------------------------------------------------------------#

# This allows us to de-clutter the app.py page by putting our different links and pages
# 'render_template' is the package that helps us view the html files in templates folder
# Request helps us handle queries like .../profile?name=Joe
# Jsonify helps us return our JSON and handle it when it comes in
# Redirect and url_for help redirect users to other pages
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import random

from collections import defaultdict
import os
import pandas as pd
from shapely.geometry import LineString, Point

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Get the API key from the environment
API_KEY = os.getenv("API_KEY")


views = Blueprint(__name__, "views") # Init/create the Blueprint and call it views

# globals
comments = []
ALLOWED_CALLSIGNS = sorted([
    "DUSKY18", 
    "DUSKY21", 
    "DUSKY24", 
    "DUSKY27"
])


#History dictionaries in place of db
latest_json = {}
history_by_callsign = {}

cumulative_dev_sum_map = defaultdict(float)#maps callsigns to cumulative dev

# ——— FLIGHT PATH CONFIG ———
FLIGHT_XLSX_DIR = "/Users/avery.austin/Desktop/IPG/CROW/DroneTracker/json_data"

flight_paths = {
    "DUSKY27":       "Disaster_City_Survey_V2_converted.xlsx",
    "DUSKY18":     "RELLIS_NORTH_-_REL→Hearne_converted.xlsx",
    "DUSKY24":  "RELLIS_SOUTH_-_REL_→_AggieFarm_converted.xlsx",
    "DUSKY21":    "RELLIS_WEST_-_REL_→_Caldwell_converted.xlsx"
}

# Preload LineStrings for each flight path
path_lines = {}
for name, xlsx in flight_paths.items():
    full_path = os.path.join(FLIGHT_XLSX_DIR, xlsx)
    df = (pd.read_excel(full_path, sheet_name="in")
            [["Latitude", "Longitude", "Altitude"]]
            .dropna()
            .reset_index(drop=True))
    coords = list(zip(df["Longitude"], df["Latitude"]))
    path_lines[name] = LineString(coords)



#-----HOME PAGE---------------------------------------------------------------------------------------------------------------------#

@views.route("/") 
def home(): # Remember that def means defining a function, i.e. home
    # Renders our index.html file in the templates folder for the home page
    # You can put as many var.'s in the return as you want, they can be gotten from the webpage from there
    return render_template("index.html", drones=sorted(ALLOWED_CALLSIGNS))

#-----DRONE TAKING JSON INPUT------------------------------------------------------------------------------------------------------#
# This will be drone J for JSON, it will take in user inputted json through a curl
# request, store it in a variable, then push it to a screen like the other drones
@views.route("/drone/<call_sign>")
def drone_page(call_sign):
    if call_sign not in ALLOWED_CALLSIGNS:
        return render_template("404.html"), 404  # Or redirect to home if preferred

    #drones = sorted(ALLOWED_CALLSIGNS)  # Optional: for dropdown
    return render_template("droneJ.html", call_sign=call_sign, drones=ALLOWED_CALLSIGNS)


@views.route("/droneJ")
def droneJ():
    #global latest_json
    return render_template("droneJ.html")#, data=latest_json)

#-----BACKEND PAGES-------------------------------------------------------------------------------------------------------------------#

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

        # Compute deviation from path
        if call_sign in path_lines and lat is not None and lon is not None:
            pt = Point(lon, lat)
            line = path_lines[call_sign]
            nearest = line.interpolate(line.project(pt))
            dist_m = pt.distance(nearest) * 111000
            dist_ft = dist_m * 3.28084
            deviation = round(dist_ft, 2)
            latest_json["deviation"] = deviation

            # Accumulate deviation sum over 25 ft
            if deviation > 25:
                cumulative_dev_sum_map[call_sign] += (deviation - 25)
            latest_json["cumulative_dev_sum"] = round(cumulative_dev_sum_map[call_sign], 2)

        if call_sign:
            history_by_callsign.setdefault(call_sign, []).append(latest_json)

        return jsonify({"message": "JSON received and deviation calculated"}), 200

    return render_template("displayJSON.html", data=latest_json, drones=ALLOWED_CALLSIGNS)


#Gets data for each callsign at /data/callsign
#will give error if no callsign at page

@views.route("/data/<call_sign>", methods=["GET"])
def data_by_callsign(call_sign):
    global history_by_callsign

    data_list = history_by_callsign.get(call_sign)
    if data_list is None:
        return jsonify({"error": "No data found for this call_sign"}), 404

    return jsonify(data_list)

#clear history button
@views.route("/reset_history", methods=["POST"])
def reset_history():
    global history_by_callsign, cumulative_dev_sum_map, latest_json
    history_by_callsign.clear()
    cumulative_dev_sum_map.clear()
    latest_json.clear()
    return redirect(url_for("views.home"))


#------------------------------------------------------------------------------------------------------------------------------------#
