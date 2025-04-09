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
latest_json = {}
comments = []

# Drones is a list of dictionaries, which are collections of key-value pairs
drones = [
    {"call_sign": "alpha", "latitude": 27.7123, "longitude": -97.3946},
    {"call_sign": "bravo", "latitude": 27.7643, "longitude": -97.3239}
]
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

#-----DRONE TAKING JSON INPUT------------------------------------------------------------------------------------------------------#
# This will be drone J for JSON, it will take in user inputted json through a curl
# request, store it in a variable, then push it to a screen like the other drones

@views.route("/droneJ-data")
def droneJ_data():
    global latest_json
    return latest_json

@views.route("/droneJ")
def droneJ():
    global latest_json
    return render_template("droneJ.html", data=latest_json)

#-----DRONE POS. RANDOMIZER--------------------------------------------------------------------------------------------------------#

# Simulate drone movement by updating their positions every time data is fetched
def update_drone_positions():
    global drones
    for drone in drones:
        drone["latitude"] -= 0.001  # Simulate small movement in lat
        drone["longitude"] += 0.0006  # Simulate small movement in lon

#-----HOME PAGE---------------------------------------------------------------------------------------------------------------------#

@views.route("/") 
def home(): # Remember that def means defining a function, i.e. home
    # Renders our index.html file in the templates folder for the home page
    # You can put as many var.'s in the return as you want, they can be gotten from the webpage from there
    return render_template("index.html")

#-----EXTRA PAGES-------------------------------------------------------------------------------------------------------------------#

# This will take in JSON data and then post it on the /data page
# Use the testFile.py file to see if the site can get a JSON POST request
@views.route("/data", methods=["GET", "POST"])
def get_data():
    global latest_json  # Ensure we can update/get the variable

    if request.method == "POST":
        latest_json = request.get_json()  # Store latest JSON data to our glocal as it comes in
        return jsonify(latest_json)  # Send response back

    # When visiting /data in a browser, display the latest JSON
    return render_template("displayJSON.html", data=latest_json)


@views.route("/inputting", methods=["GET", "POST"])
def inputting():
    global comments

    if request.method == "GET":
        return render_template("inputting.html", comments=comments)

    comments.append(request.form["comment"])
    return redirect(url_for('views.inputting'))

#------------------------------------------------------------------------------------------------------------------------------------#
