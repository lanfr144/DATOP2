"""
Lab 1: FastAPI Fundamentals - Endpoints, Parameters, and Documentation
========================================================================

Course: DATOP2 - Unit 02: Installing and Running FastAPI locally
File: app/lab2a.py (based on app/main.py)
Run  : python -m app.lab2a   (from the api/ folder; host/port read from .env)

========================================================================
❓ CHECK YOUR UNDERSTANDING - ANSWERS & CONCEPTS
========================================================================

1. What is the difference between a path parameter and a query parameter? Give one example of each.
   ------------------------------------------------------------------------------------------------
   - Path Parameter:
     * Definition: A variable part of the URL path itself, delimited by slashes ("/").
     * Purpose: Identifies a specific resource or entity in a hierarchy.
     * Requirement: Mandatory by default. If omitted, the URL path will not match the route (resulting in a 404 Not Found).
     * Declaration in FastAPI: Specified directly inside the decorator path string using curly braces.
     * Example: In `@app.get("/square/{n}")` or `@app.get("/items/{item_id}")`, `n` and `item_id` are path parameters.
       Request: `GET /square/9` -> `n` is `9`.

   - Query Parameter:
     * Definition: Key-value pairs appended at the end of a URL after a question mark ("?"), separated by ampersands ("&").
     * Purpose: Used for filtering, sorting, pagination, or passing optional parameters/modifiers.
     * Requirement: Typically optional (can have default values), though FastAPI allows them to be required if no default is provided.
     * Declaration in FastAPI: Any function argument not declared in the route path string automatically becomes a query parameter.
     * Example: In `@app.get("/add") def add(a: int, b: int):`, `a` and `b` are query parameters.
       Request: `GET /add?a=3&b=4` -> `a` is `3`, `b` is `4`.

2. Why do we use a virtual environment instead of installing packages globally?
   -----------------------------------------------------------------------------
   - Dependency Isolation: Different projects often require different versions of the same package (e.g., Project A needs FastAPI 0.100.0 while Project B requires FastAPI 0.136.0). Virtual environments prevent version conflicts.
   - Reproducibility: Guarantees that the project's exact dependencies can be tracked (via `requirements.txt` or lockfiles) and reproduced reliably across different machines, CI/CD pipelines, and team members.
   - System Stability: Prevents polluting the global operating system Python runtime and avoids permission issues or accidentally breaking system utilities that rely on system Python packages.

3. What does --reload do, and why should it not be used in production?
   ---------------------------------------------------------------------
   - What `--reload` does:
     It instructs Uvicorn (the ASGI server) to monitor source files in the project directory. Whenever any file is modified and saved, Uvicorn automatically restarts the server worker process so new code changes take effect immediately without manually restarting the terminal process.
   - Why it should NOT be used in production:
     * Performance Overhead: Continuous filesystem monitoring consumes substantial CPU and I/O resources.
     * Dropped Connections & Downtime: Restarting the worker process immediately terminates in-flight client requests, causing sudden connection drops and service downtime.
     * Security & Stability: Production code should be immutable and tested. Hot-reloading unexpected code or incomplete edits can lead to corrupted state or runtime crashes.
     * Architecture: Production deployments use robust process managers (e.g., Gunicorn with multiple Uvicorn worker processes, Docker containers, Kubernetes) to handle load balancing, concurrency, and graceful zero-downtime rolling restarts.

4. Which URL shows the interactive documentation, and which one shows the raw OpenAPI schema?
   -------------------------------------------------------------------------------------------
   - Interactive Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
     (Provides interactive "Try it out" buttons to test endpoints directly from the browser).
   - Alternative Interactive Documentation (ReDoc): `http://127.0.0.1:8000/redoc`
     (Provides a clean, three-panel, responsive API reference).
   - Raw OpenAPI Schema (JSON format): `http://127.0.0.1:8000/openapi.json`
     (Provides the complete machine-readable OpenAPI 3.1 schema specification).

========================================================================
"""

from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

from .config import APP_HOST, APP_PORT

# ==============================================================================
# Challenge 4: Give your API a title and a version
# ==============================================================================
# Question: Where does it appear?
# Answer:
#   1. In Swagger UI (`http://127.0.0.1:8000/docs`):
#      It appears prominently at the very top of the page as the main header title and version badge.
#   2. In ReDoc (`http://127.0.0.1:8000/redoc`):
#      It appears at the top left of the navigation panel and main content banner.
#   3. In the OpenAPI schema (`http://127.0.0.1:8000/openapi.json`):
#      It is embedded inside the `"info"` metadata object:
#      `{"info": {"title": "My First API", "version": "1.0.0", ...}}`
# ==============================================================================

app = FastAPI(
    title="My First API",
    description="Lab 1 API implementing query parameters, path parameters, validation, and documentation.",
    version="1.0.0",
)


# ==============================================================================
# Original Endpoints from main.py
# ==============================================================================

@app.get("/", tags=["General"])
def root():
    """
    Root endpoint returning a welcome message.
    Example: GET / -> {"message": "Hello, FastAPI!"}
    """
    return {"message": "Hello, FastAPI!"}


@app.get("/items/{item_id}", tags=["Items"])
def read_item(item_id: int, q: Optional[str] = None):
    """
    Retrieve an item by its path parameter `item_id`, with an optional query parameter `q`.
    Example: GET /items/42?q=search_term -> {"item_id": 42, "q": "search_term"}
    """
    return {"item_id": item_id, "q": q}


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True  # Optional field with default value


@app.post("/items/", tags=["Items"])
def create_item(item: Item):
    """
    Create a new item by accepting a JSON request body validated by Pydantic.
    Example: POST /items/ with JSON body -> {"received_item": item}
    """
    return {"received_item": item}


# ==============================================================================
# Challenge 1: Query-parameter endpoint /add
# ==============================================================================
# Tip / Concept:
# In FastAPI, any function parameter that is NOT part of the route path
# automatically becomes a query parameter.
#
# Example call:
#   GET /add?a=3&b=4 -> {"result": 7}
# ==============================================================================

@app.get("/add", tags=["Math Operations"])
def add(a: int = Query(..., description="First integer to add"),
        b: int = Query(..., description="Second integer to add")):
    """
    Calculate and return the sum of two integers `a` and `b`.

    Both parameters are query parameters passed via URL (e.g., /add?a=3&b=4).
    FastAPI automatically validates that both `a` and `b` are valid integers.
    """
    return {"result": a + b}


# ==============================================================================
# Challenge 2: Analysis of /add?a=3&b=abc
# ==============================================================================
# Question:
#   Call /add?a=3&b=abc. What status code do you get, and why? Read the error message carefully.
#
# Answer:
#   - HTTP Status Code: 422 Unprocessable Entity
#
#   - Error Response Body:
#     {
#       "detail": [
#         {
#           "type": "int_parsing",
#           "loc": ["query", "b"],
#           "msg": "Input should be a valid integer, unable to parse string as an integer",
#           "input": "abc"
#         }
#       ]
#     }
#
#   - Why this occurs:
#     1. FastAPI relies on Pydantic and Python type hints (`b: int`) for automatic data parsing
#        and validation.
#     2. When the client sends `b=abc`, FastAPI attempts to coerce the string `"abc"` to an `int`.
#     3. Because `"abc"` cannot be parsed into an integer, validation fails.
#     4. Instead of crashing with an unhandled server error (500), FastAPI automatically catches
#        the validation error and returns HTTP 422 (Unprocessable Entity) with a clear, structured
#        explanation showing the exact location (`["query", "b"]`) and cause of the failure.
# ==============================================================================


# ==============================================================================
# Challenge 3: Path-parameter endpoint /square/{n}
# ==============================================================================
# Example call:
#   GET /square/9 -> {"n": 9, "square": 81}
# ==============================================================================

@app.get("/square/{n}", tags=["Math Operations"])
def square(n: int):
    """
    Calculate and return the square (n²) of a path parameter integer `n`.

    Example:
        GET /square/9 -> {"n": 9, "square": 81}
    """
    return {"n": n, "square": n ** 2}


# ==============================================================================
# Challenge 5: Endpoint /hello/{name} with optional query parameter `lang`
# ==============================================================================
# Accepts:
#   - Path parameter `name`: string representing the person to greet
#   - Optional query parameter `lang`: "en", "fr", "de" (defaults to "en")
#
# Example calls:
#   GET /hello/Ana?lang=fr -> {"greeting": "Bonjour, Ana!"}
#   GET /hello/Ana?lang=de -> {"greeting": "Hallo, Ana!"}
#   GET /hello/Ana?lang=en -> {"greeting": "Hello, Ana!"}
#   GET /hello/Ana         -> {"greeting": "Hello, Ana!"}
# ==============================================================================

# Dictionary mapping supported language codes to greeting templates
GREETING_TEMPLATES = {
    "en": "Hello, {name}!",
    "fr": "Bonjour, {name}!",
    "de": "Hallo, {name}!",
}

@app.get("/hello/{name}", tags=["Greetings"])
def greet(
    name: str,
    lang: str = Query(
        default="en",
        description="Greeting language code: 'en' (English), 'fr' (French), or 'de' (German)"
    )
):
    """
    Greet a person by `name` (path parameter) in the specified language `lang` (optional query parameter).

    Supported languages:
        - 'en': English (default) -> "Hello, {name}!"
        - 'fr': French             -> "Bonjour, {name}!"
        - 'de': German             -> "Hallo, {name}!"
    """
    # Normalize language code to lowercase
    normalized_lang = lang.lower()

    # Look up greeting template with a safe default fallback to English
    template = GREETING_TEMPLATES.get(normalized_lang, GREETING_TEMPLATES["en"])
    return {"greeting": template.format(name=name)}


# ==============================================================================
# Main entrypoint for direct script execution
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    # Correction : le module s'appelle lab2a (et non lab1) ; host/port viennent du .env
    base = f"http://{APP_HOST}:{APP_PORT}"
    print("\nStarting Uvicorn server for app/lab2a.py...")
    print(f"Interactive Documentation: {base}/docs")
    print(f"ReDoc Documentation:       {base}/redoc")
    print(f"OpenAPI JSON Schema:       {base}/openapi.json\n")
    uvicorn.run("app.lab2a:app", host=APP_HOST, port=APP_PORT, reload=True)
