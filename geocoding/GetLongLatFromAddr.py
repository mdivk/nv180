import requests
response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA')
resp_json_payload = response.json()

print(resp_json_payload['results'][0]['geometry']['location'])

# Result: {'lat': 37.4222312, 'lng': -122.0857822}
# Note: requests must be 2.19+
