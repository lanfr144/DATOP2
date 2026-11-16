"""
Unit 01 - Exercise 1, Part C : requetes HTTP avec "requests" sur JSONPlaceholder.

Usage :  python exercises/ex1_http.py      (pip install requests)
Reponses attendues :
  - GET /posts/1  -> 200, title = "sunt aut facere repellat provident occaecati excepturi optio reprehenderit"
  - POST /posts   -> 201, id = 101 (JSONPlaceholder simule la creation, rien n'est enregistre)
  - GET /posts/999999 -> 404, corps "{}"
"""
import os

import requests

BASE_URL = os.getenv("JSONPLACEHOLDER_URL", "https://jsonplaceholder.typicode.com")
TIMEOUT = 10  # secondes : toujours mettre un timeout sur un appel reseau

# 1. GET : lire une ressource existante
resp = requests.get(f"{BASE_URL}/posts/1", timeout=TIMEOUT)
print("GET Status:", resp.status_code)
print("Response:", resp.json())

# 2. POST : creer une ressource (le corps est envoye en JSON)
new_post = {"title": "DATOP2 Test", "body": "This is a new post.", "userId": 1}
resp = requests.post(f"{BASE_URL}/posts", json=new_post, timeout=TIMEOUT)
print("POST Status:", resp.status_code)
print("Response:", resp.json())

# 3. GET invalide : la ressource n'existe pas -> 404
resp = requests.get(f"{BASE_URL}/posts/999999", timeout=TIMEOUT)
print("Error Status:", resp.status_code)
print("Response:", resp.text)
