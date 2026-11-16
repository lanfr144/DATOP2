"""
Exemple du cours Unit 01 (COURS/Unit01/example2.py) : API GraphQL publique (pays).

Difference avec REST : UN seul endpoint, toujours en POST ; c'est la requete GraphQL
(dans le corps JSON) qui choisit exactement les champs voulus.
Usage :  python exercises/example2.py [CODE_PAYS]   (pip install requests)
"""
import sys

import requests

URL = "https://countries.trevorblades.com/"
country_code = sys.argv[1] if len(sys.argv) > 1 else "FR"

# Requete GraphQL avec une variable ($code) plutot qu'une valeur ecrite dans le texte
query = """
query ($code: ID!) {
  country(code: $code) {
    name
    capital
    currency
  }
}
"""

response = requests.post(URL, json={"query": query, "variables": {"code": country_code}}, timeout=10)

if response.status_code == 200:
    data = response.json()
    # GraphQL renvoie souvent 200 meme en cas d'erreur : il faut regarder la cle "errors"
    if data.get("errors"):
        print("❌ GraphQL errors:", data["errors"])
    elif data["data"]["country"] is None:
        print(f"❌ Unknown country code: {country_code}")
    else:
        country = data["data"]["country"]
        print("✅ GraphQL Response:")
        print("Name:", country["name"])
        print("Capital:", country["capital"])
        print("Currency:", country["currency"])
else:
    print(f"❌ Failed with status code {response.status_code}")
    print(response.text)
