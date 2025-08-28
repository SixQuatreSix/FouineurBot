# utils/db_handler.py
import json
import os

DB_FILE = "seen_ads.json"

def load_seen_ads():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(json.load(f))

def save_seen_ads(seen_ads):
    with open(DB_FILE, "w") as f:
        json.dump(list(seen_ads), f)