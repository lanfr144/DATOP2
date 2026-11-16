@ECHO OFF
REM Unit 02a - installation, lancement et tests curl (Windows).
REM A lancer depuis le dossier fastapi-lab\ :  scripts\set-up.bat
REM Correction : le port n'est plus code en dur (lu dans .env), le serveur est lance
REM dans une fenetre separee (avant, "uvicorn --reload" bloquait le script et les curl
REM ne s'executaient jamais).

IF NOT EXIST .env copy .env.example .env
FOR /F "usebackq eol=# tokens=1,2 delims==" %%A IN (".env") DO SET "%%A=%%B"
SET BASE=http://%APP_HOST%:%APP_PORT%

echo === Installation (FastAPI ne contient pas de serveur web : on utilise Uvicorn, un serveur ASGI)
IF NOT EXIST venv python -m venv venv
call venv\Scripts\activate.bat
pip install -r api\requirements.txt

echo === Lancement de l'API dans une autre fenetre (main = fichier, app = instance FastAPI)
start "uvicorn" cmd /k "cd api && uvicorn app.main:app --reload --host %APP_HOST% --port %APP_PORT%"
timeout /t 5 >NUL

echo === Endpoint racine (attendu : {"message":"Hello, FastAPI!"})
curl -s -w "\nreturn code=%%{http_code}\n" %BASE%/
echo === Documentation Swagger et ReDoc
curl -s -o NUL -w "docs  return code=%%{http_code}\n" %BASE%/docs
curl -s -o NUL -w "redoc return code=%%{http_code}\n" %BASE%/redoc
echo === Definition de l'API (OpenAPI)
curl -s -w "\nreturn code=%%{http_code}\n" %BASE%/openapi.json
echo === Second endpoint (attendu : {"item_id":1967041981140,"q":"Matricule"})
curl -s -w "\nreturn code=%%{http_code}\n" "%BASE%/items/1967041981140?q=Matricule"
echo === Gestion d'erreur (attendu : 422 int_parsing)
curl -s -w "\nreturn code=%%{http_code}\n" %BASE%/items/abd
echo Fermez la fenetre uvicorn pour arreter le serveur.
