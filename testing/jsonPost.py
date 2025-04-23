import requests, time, random, datetime

# Update the URL to match your Drone J endpoint.
URL = "http://127.0.0.1:8000/data"
HEADERS = {"Content-Type": "application/json"}

# Initial global values for the drone data.
latitude = 27.7123
longitude = -97.3946
altitude = 288.0101
airspeed = 50.0
ground_speed = 50.0
verticle_speed = 0.0
battery_voltage = 12.6
battery_current = 1.0
battery_percentage = 100.0

# Initial orientation values.
pitch = 0.0
roll = 0.0
yaw = 0.0
pitch_rate = 0.0
roll_rate = 0.0
yaw_rate = 0.0

def generate_json():
    global latitude, longitude, altitude
    global airspeed, ground_speed, verticle_speed
    global battery_voltage, battery_current, battery_percentage
    global pitch, roll, yaw, pitch_rate, roll_rate, yaw_rate

    # Update position: move the drone with small variations.
    side_step = 0.0022
    forward_step = 0.0021
    up_step = 0.003
    latitude += forward_step + random.uniform(-0.0005, 0.0005)
    longitude += side_step + random.uniform(-0.0005, 0.0005)
    altitude += up_step + random.uniform(-0.1, 0.1)
    
    # Update velocity.
    airspeed += random.uniform(-0.5, 0.5)
    ground_speed += random.uniform(-0.5, 0.5)
    verticle_speed = random.uniform(-0.2, 0.2)
    track = random.uniform(0, 360)

    # Update time to the current time in ISO format.
    time_measured = datetime.datetime.utcnow().isoformat() + "Z"

    # Update battery parameters.
    battery_voltage = max(battery_voltage - random.uniform(0.01, 0.05), 10.0)
    battery_current = 1.0 + random.uniform(-0.1, 0.1)
    battery_percentage = max(battery_percentage - random.uniform(0.1, 0.5), 0)

    # Update orientation parameters.
    pitch = random.uniform(-5, 5)
    roll = random.uniform(-5, 5)
    yaw = random.uniform(0, 360)
    pitch_rate = random.uniform(-1, 1)
    roll_rate = random.uniform(-1, 1)
    yaw_rate = random.uniform(-1, 1)

    # Simulate deviation from course (in feet). Values > 25 will be highlighted on the client.
    deviation = random.randint(0, 40)

    data = {
        "call_sign": "Juliet",
        "position": {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "altitude": round(altitude, 6)
        },
        "velocity": {
            "airspeed": round(airspeed, 2),
            "ground_speed": round(ground_speed, 2),
            "verticle_speed": round(verticle_speed, 2),
            "units_speed": "MetersPerSecond",
            "track": round(track, 2)
        },
        "time_measured": time_measured,
        "battery": {
            "voltage": round(battery_voltage, 2),
            "current": round(battery_current, 2),
            "percentage": round(battery_percentage, 2)
        },
        "orientation": {
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "yaw": round(yaw, 2),
            "pitch_rate": round(pitch_rate, 2),
            "roll_rate": round(roll_rate, 2),
            "yaw_rate": round(yaw_rate, 2)
        },
        "airframe": "Generic",
        "deviation": deviation
    }
    return data

def send_post_request():
    while True:
        data = generate_json()
        response = requests.post(URL, headers=HEADERS, json=data)
        print(f"Sent: {data}, Response: {response.status_code}")
        time.sleep(1)  # Wait 1 second before sending the next update.

if __name__ == "__main__":
    send_post_request()

