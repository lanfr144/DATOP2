#!/usr/bin/env bash
# Checkpoint 3 - books module   (ancien "terminal2")
. "$(dirname "$0")/_env.sh"
curl -s -X POST "$API/books" -H "Content-Type: application/json" \
  -d '{"title": "Dune", "author": "Frank Herbert", "stock": 5}'; echo
curl -s -X POST "$API/books" -H "Content-Type: application/json" \
  -d '{"title": "1984", "author": "George Orwell", "stock": 3}'; echo
curl -s "$API/books?search=orwell"; echo
curl -s -X PUT "$API/books/1" -H "Content-Type: application/json" -d '{"stock": 10}'; echo
curl -s -i -X DELETE "$API/books/2" | head -1
curl -s -o /dev/null -w "GET /books/2 -> %{http_code}\n" "$API/books/2"
curl -s -X POST "$API/books" -H "Content-Type: application/json" -d '{"title":"","author":"X","stock":-1}'; echo
