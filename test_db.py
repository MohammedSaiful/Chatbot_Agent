import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("Trying to connect to:", DATABASE_URL)

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("Connected successfully!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
