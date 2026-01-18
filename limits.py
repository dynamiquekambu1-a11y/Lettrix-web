import json
import os
import datetime

FILE = "data/exports.json"

def can_export(user_id):
    today = str(datetime.date.today())
    os.makedirs("data", exist_ok=True)

    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    user = data.get(user_id, {
        "total": 0,
        "daily": {},
        "first": True
    })

    if user["first"]:
        if user["total"] < 10:
            user["total"] += 1
        else:
            user["first"] = False
    else:
        user["daily"][today] = user["daily"].get(today, 0) + 1
        if user["daily"][today] > 3:
            return False

    data[user_id] = user
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

    return True
