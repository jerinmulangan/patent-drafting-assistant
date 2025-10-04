import os, time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

# --- Environment Variables ---
DATABASE_URL = os.getenv("DATABASE_URL")
MONGO_URL = os.getenv("MONGO_URL")

# --- Retry logic ---
def connect_with_retry(connector, url, retries=5, delay=5):
    for i in range(retries):
        try:
            return connector(url)
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in {delay}s... ({i+1}/{retries})")
            time.sleep(delay)
    raise Exception(f"Could not connect to {url} after {retries} retries.")

# --- PostgreSQL Setup ---
Base = declarative_base()
sql_engine = connect_with_retry(create_engine, DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sql_engine)

# --- MongoDB Setup ---
mongo_client = connect_with_retry(MongoClient, MONGO_URL)
mongo_db = mongo_client.appdb
collection = mongo_db.documents
