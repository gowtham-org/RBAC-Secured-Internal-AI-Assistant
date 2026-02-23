import json, os
from typing import Dict

USERS_FILE = os.getenv("USERS_FILE", "/config/users.json")

def load_users() -> Dict[str, Dict[str, str]]:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)