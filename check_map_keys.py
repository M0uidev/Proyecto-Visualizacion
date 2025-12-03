import requests
import json

url = "https://code.highcharts.com/mapdata/countries/cl/cl-all.geo.json"
try:
    response = requests.get(url)
    data = response.json()
    print("Keys found in Highcharts map:")
    for feature in data['features']:
        props = feature['properties']
        print(f"Name: {props.get('name')}, hc-key: {props.get('hc-key')}")
except Exception as e:
    print(e)
