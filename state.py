"""
state.py
Houdt bij welke posts al gebruikt zijn zodat de pool niet te snel herhaalt.
Wordt weggeschreven naar state.json (lokaal op Railway's filesystem).
"""

import json
import os
import random
import logging

import config

logger = logging.getLogger("npcbro.state")


def _default_state():
    return {
        "used_text_indices": [],
        "used_photo_indices": [],
        "used_reply_indices": [],
        "last_engage_timestamp": None,
        "replies_today": 0,
        "last_reply_date": None,
    }


def load_state() -> dict:
    if not os.path.exists(config.STATE_FILE):
        return _default_state()
    try:
        with open(config.STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.warning("state.json corrupt of onleesbaar, start met lege state.")
        return _default_state()


def save_state(state: dict):
    with open(config.STATE_FILE, "w") as f:
        json.dump(state, f)


def pick_next(pool_len: int, used_key: str, state: dict) -> int:
    """Kiest een index die nog niet recent gebruikt is; reshuffled als pool op is."""
    used = state.get(used_key, [])
    available = [i for i in range(pool_len) if i not in used]
    if not available:
        used = []
        available = list(range(pool_len))
    choice = random.choice(available)
    used.append(choice)
    state[used_key] = used
    return choice
