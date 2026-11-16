"""
Exemple du cours Unit 01 (COURS/Unit01/example1.py) : API REST publique Open-Meteo.

Le cours y fait reference sous le nom "unit01/example1.py".
Ajouts par rapport au cours : timeout, coordonnees modifiables, URL dans des constantes.
Usage :  python exercises/example1.py   (pip install requests)
"""
import os

import requests

LATITUDE = float(os.getenv("WEATHER_LATITUDE", "49.6117"))    # Luxembourg
LONGITUDE = float(os.getenv("WEATHER_LONGITUDE", "6.13"))
BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Les parametres de requete (query parameters) sont passes avec params=... :
# requests construit "?latitude=...&longitude=...&current_weather=true" pour nous.
response = requests.get(
    BASE_URL,
    params={"latitude": LATITUDE, "longitude": LONGITUDE, "current_weather": "true"},
    timeout=10,
)

if response.status_code == 200:
    data = response.json()                 # corps JSON -> dict Python
    current = data["current_weather"]
    print("✅ Current Weather:")
    print("Temperature:", current["temperature"], "°C")
    print("Windspeed:", current["windspeed"], "km/h")
    print("Weather Code:", current["weathercode"])
else:
    print(f"❌ Failed with status code {response.status_code}")
    print(response.text)
