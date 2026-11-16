FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Port interne du conteneur : lu dans la variable APP_PORT (fournie par docker compose / .env)
ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000
EXPOSE ${APP_PORT}
# Healthcheck integre a l'image (python car l'image slim n'a ni curl ni wget)
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=10 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"APP_PORT\"]}/healthy', timeout=2)"
# Forme "shell" (sh -c) pour que ${APP_PORT} soit remplace au demarrage du conteneur
CMD ["sh", "-c", "uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT}"]
