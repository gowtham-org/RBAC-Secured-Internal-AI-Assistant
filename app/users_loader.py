import json, os, logging, bcrypt
from typing import Dict, Optional

logger = logging.getLogger(__name__)

USERS_FILE = os.getenv("USERS_FILE", "/config/users.json")
ALLOWED_ROLES = {"c-levelexecutives", "finance", "marketing", "hr", "engineering", "employee"}


def load_users() -> Dict[str, Dict]:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_user(username: str, password: str) -> Optional[str]:
    """Return the user's role if login is valid, else None."""
    users = load_users()
    user = users.get(username)

    if not user:
        bcrypt.checkpw(password.encode(), bcrypt.gensalt())  # same timing as a real check
        return None

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None

    if user.get("disabled", False):
        logger.warning("login blocked: user=%s is disabled", username)
        return None

    if user.get("role") not in ALLOWED_ROLES:
        logger.error("login blocked: user=%s has invalid role=%r", username, user.get("role"))
        return None

    return user["role"]