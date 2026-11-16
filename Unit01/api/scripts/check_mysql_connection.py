"""
Petit script de diagnostic : verifie que MySQL est joignable avec les identifiants du .env.

Usage (depuis le dossier api/) :  python scripts/check_mysql_connection.py
Correction : host/port/user/mot de passe ne sont plus codes en dur (avant : root sans
mot de passe sur 127.0.0.1:3306), ils viennent du .env.
"""
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

try:
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_HOST_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE"),
    )
    with conn.cursor() as cur:
        cur.execute("SELECT VERSION(), DATABASE(), CURRENT_USER();")
        print("OK", cur.fetchone())
    conn.close()
except Exception as e:  # noqa: BLE001
    print("ERROR", type(e).__name__, e)
