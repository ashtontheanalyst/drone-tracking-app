# This will send a different JSON file to the /droneJ page every 2 seconds
# The point is to test and see if the website can handle recieving and posting
# SUCCESS!!

import requests, time, random

URL = "http://127.0.0.1:8000/data"
HEADERS = {"Content-Type": "application/json"}

def generate_random_json():
    return {
        "call_sign": "Juliet",
        "latitude": round(27.7123 + random.uniform(-0.005, 0.005), 6),
        "longitude": round(-97.3946 + random.uniform(-0.005, 0.005), 6)
    }

def send_post_request():
    while True:
        data = generate_random_json()
        response = requests.post(URL, headers=HEADERS, json=data)
        print(f"Sent: {data}, Response: {response.status_code}")
        time.sleep(2)  # Wait 2 seconds before sending again

if __name__ == "__main__":
    send_post_request()