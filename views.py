#-----SET UP/INIT----------------------------------------------------------------------------------------------------------------#

# This allows us to de-clutter the app.py page by putting our different links and pages
# 'render_template' is the package that helps us view the html files in templates folder
# Request helps us handle queries like .../profile?name=Joe
# Jsonify helps us return our JSON and handle it when it comes in
# Redirect and url_for help redirect users to other pages
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import random
views = Blueprint(__name__, "views") # Init/create the Blueprint and call it views

# globals
comments = []
ALLOWED_CALLSIGNS = {"Disaster_City_Survey", "RELLIS_South_to_AggieFarm", "RELLIS_West_to_Caldwell", "RELLIS_North_to_Hearne"}


#History dictionaries in place of db
latest_json = {}
history_by_callsign = {}




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
API_KEY = "your-secret-api-key"  # TODO: move to environment variable later
@views.route("/data", methods=["GET", "POST"])
def get_data():
    global latest_json, history_by_callsign  # Ensure we can update/get the variable

    if request.method == "POST":
        # 1. Check API key from headers
        client_key = request.headers.get("X-API-KEY")
        if client_key != API_KEY:
            return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

        # 2. Parse incoming JSON
        latest_json = request.get_json()
        if not latest_json:
            return jsonify({"error": "No JSON data received"}), 400

        # 3. Extract call_sign and update history
        call_sign = latest_json.get("call_sign")
        print("call_sign:", call_sign)
        if call_sign:
            if call_sign not in history_by_callsign:
                history_by_callsign[call_sign] = []
            history_by_callsign[call_sign].append(latest_json)

        return jsonify({"message": "JSON received and stored"}), 200

    # GET request → display latest JSON on /data page
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


#------------------------------------------------------------------------------------------------------------------------------------#

'''
# Drones is a list of dictionaries, which are collections of key-value pairs
drones = [
    {"call_sign": "alpha", "latitude": 27.7123, "longitude": -97.3946},
    {"call_sign": "bravo", "latitude": 27.7643, "longitude": -97.3239}
]

unsecured gathering of data
@views.route("/data", methods=["GET", "POST"])
def get_data():
    global latest_json, history_by_callsign # Ensure we can update/get the variable

    if request.method == "POST":
        latest_json = request.get_json()  # Store latest JSON data to our glocal as it comes in

         # Extract call_sign from JSON
        call_sign = latest_json.get("call_sign")
        print("call_sign:", call_sign)
        if call_sign:
            # Initialize list for call_sign if not exists
            if call_sign not in history_by_callsign:
                history_by_callsign[call_sign] = []
            # Append the full incoming JSON to the history
            history_by_callsign[call_sign].append(latest_json)
        
        return jsonify({"message": "JSON received and stored"}), 200   
        #return jsonify(latest_json)  # Send response back

        
    
    # When visiting /data in a browser, display the latest JSON
    return render_template("displayJSON.html", data=latest_json)
'''

'''
#-----DRONE PAGES----------------------------------------------------------------------------------------------------------------#

# Below is a simulation of aircraft on the map
# Example aircraft positions around College Station, TX
@views.route("/drone-data")
def all_drones():
    global drones
    update_drone_positions()
    return jsonify(drones)

@views.route("/droneA-data")
def droneA_data():
    global drones
    update_drone_positions()
    return jsonify(drones[0])

@views.route("/droneA")
def droneA():
    return render_template("droneA.html")

@views.route("/droneB-data")
def droneB_data():
    global drones
    update_drone_positions()
    return jsonify(drones[1])

@views.route("/droneB")
def droneB():
    return render_template("droneB.html")


#-----DRONE POS. RANDOMIZER--------------------------------------------------------------------------------------------------------#

# Simulate drone movement by updating their positions every time data is fetched
def update_drone_positions():
    global drones
    for drone in drones:
        drone["latitude"] -= 0.001  # Simulate small movement in lat
        drone["longitude"] += 0.0006  # Simulate small movement in lon


#-----EXTRA PAGES--------------------------------------------------------------------------------------------------------#
@views.route("/inputting", methods=["GET", "POST"])
def inputting():
    global comments

    if request.method == "GET":
        return render_template("inputting.html", comments=comments)

    comments.append(request.form["comment"])
    return redirect(url_for('views.inputting'))


#-----Database-------------------------------------------------------------------------------------------------------------------#
import sqlite3

@views.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    json_blob = json.dumps(data)

    with sqlite3.connect("telemetry.db") as conn:
        conn.execute(
            "INSERT INTO telemetry (aircraft_id, timestamp, json_data) VALUES (?, ?, ?)",
            (
                data["call_sign"],
                data["time_measured"],
                json_blob
            )
        )
    return jsonify({"status": "received"})

@views.route("/history")
def all_history():
    with sqlite3.connect("telemetry.db") as conn:
        cursor = conn.execute(
            "SELECT timestamp, aircraft_id, json_data FROM telemetry ORDER BY timestamp"
        )
        rows = cursor.fetchall()
    return render_template("JSONHistory.html", history=rows)

@views.route("/history/download")
def download_json_history():
    with sqlite3.connect("telemetry.db") as conn:
        cursor = conn.execute("SELECT json_data FROM telemetry ORDER BY timestamp")
        json_list = [json.loads(row[0]) for row in cursor.fetchall()]
    return Response(
        json.dumps(json_list, indent=2),
        mimetype='application/json',
        headers={"Content-Disposition": "attachment;filename=telemetry_history.json"}
    )
#------------------------------------------------------------------------------------------------------------------------------------#

'''