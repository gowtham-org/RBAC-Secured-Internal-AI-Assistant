import json, os, bcrypt
from typing import Dict, Optional

USERS_FILE = os.getenv("USERS_FILE", "/config/users.json")


def load_users() -> Dict[str, Dict[str, str]]:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_user(username: str, password: str) -> Optional[str]:
    """Return the user's role if credentials are valid, else None."""
    users = load_users()
    user = users.get(username)
    if not user:
        bcrypt.checkpw(password.encode(), bcrypt.gensalt())
        return None
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return user["role"]
    return None