FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Stretch goal : ne pas executer l'application en root dans le conteneur
RUN useradd -m app && chown -R app /app
USER app
# Port interne lu dans API_PORT (fourni par .env via docker compose), 8080 par defaut
ENV API_PORT=8080
EXPOSE ${API_PORT}
# Healthcheck integre a l'image : Docker appelle /health (qui teste aussi la BD).
# python est utilise car l'image slim n'a ni curl ni wget.
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=10 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"API_PORT\"]}/health', timeout=2)"
# Forme "sh -c" pour que ${API_PORT} soit evalue au demarrage du conteneur
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT}"]
