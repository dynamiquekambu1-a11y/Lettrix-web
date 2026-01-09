import json
import os

FILE = "data/stats.json"

def load():
    if not os.path.exists(FILE):
        save({"visitors": 0, "users": 0})
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {"visitors": 0, "users": 0}

def save(data):
    os.makedirs("data", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def inc(key):
    data = load()
    data[key] = data.get(key, 0) + 1
    save(data)
