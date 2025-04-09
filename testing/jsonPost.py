import requests, time

# CHange this to the URL you need:
# URL = "http://ashtonrwsmith.pythonanywhere.com/droneJ-data"
URL = "http://127.0.0.1:8000/data"
HEADERS = {"Content-Type": "application/json"}

# Initial position of the drone
latitude = 27.7123
longitude = -97.3946

# Define the step size for moving the drone
side_step = 0.0022  # Move by a small constant value
up_step = 0.003

def generate_json():
    global latitude, longitude
    # Move the drone to the right (increasing longitude)
    longitude += side_step
    latitude += up_step
    return {
        "call_sign": "Juliet",
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6)
    }

def send_post_request():
    while True:
        data = generate_json()
        response = requests.post(URL, headers=HEADERS, json=data)
        print(f"Sent: {data}, Response: {response.status_code}")
        time.sleep(2)  # Wait 2 seconds before sending again

if __name__ == "__main__":
    send_post_request()
