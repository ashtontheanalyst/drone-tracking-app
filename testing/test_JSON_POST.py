# For further testing tomorrow, try to simulate the data from
# the JSON file CROW ARI
import requests

url = "https://ashtonrwsmith.pythonanywhere.com/data"
payload = {
    "name": "Adam",
    "age": 63}
response = requests.post(url, json=payload)

print(response.json())  # Should print {"name": "John", "age": 30}


#--------------------------------------------------------#
# test.json has the telem data from CROW ARI, use this command in the terminal:
# curl -X POST https://ashtonrwsmith.pythonanywhere.com/data -H "Content-Type: application/json" --data-binary @test.json