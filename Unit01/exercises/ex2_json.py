"""
Unit 01 - Exercise 2, Part D : lire et ecrire du JSON en Python.

Usage :  python exercises/ex2_json.py
"""
import json

# JSON string (from API or file)
book_json = '{"id": 1, "title": "Book Title", "author": "John Doe"}'

# 1. Parse JSON string into Python dict  (json.loads = "load string")
book = json.loads(book_json)
print("Title:", book["title"])
print("Author:", book["author"])

# 2. Create new Python dict and convert to JSON  (True Python -> true JSON)
student = {
    "id": 101,
    "name": "Alice",
    "age": 22,
    "enrolled": True,
    "courses": ["APIs", "Databases", "Networking"],
}
student_json = json.dumps(student, indent=2)
print("Student JSON:", student_json)

# Aller-retour : on retrouve exactement le meme dictionnaire
assert json.loads(student_json) == student
