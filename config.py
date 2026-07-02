"""
config.py
Centrale configuratie: leest alles uit environment variables (Railway).
IMAGES_DIR staat op "" (root van de repo) zodat de foto's niet in een
aparte images/ map hoeven te staan.
"""

import os


def _get_int(name: str, default: int) -> int:
    val = os.environ.get(name)
    return int(val) if val else default


def _get_float(name: str, default: float) -> float:
    val = os.environ.get(name)
    return float(val) if val else default


# --- X (Twitter) API keys ---
X_API_KEY = os.environ.get("TWITTER_API_KEY", "")
X_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")

# --- Anthropic (indien gebruikt door andere delen van de bot) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# --- Accounts om mee te engagen (comma-separated, zonder @) ---
_raw_targets = os.environ.get("TARGET_ACCOUNTS", "")
TARGET_ACCOUNTS = [a.strip() for a in _raw_targets.split(",") if a.strip()]

# --- Foto's staan los in de root van de repo, geen aparte images/ map ---
IMAGES_DIR = ""

# --- Posting-gedrag ---
PHOTO_POST_CHANCE = _get_float("PHOTO_POST_CHANCE", 0.5)  # 50% kans op foto-post
MIN_INTERVAL_MINUTES = _get_int("MIN_INTERVAL_MINUTES", 240)  # 4 uur
MAX_INTERVAL_MINUTES = _get_int("MAX_INTERVAL_MINUTES", 240)  # 4 uur (precies 6 posts per dag)

# --- State-bestand (lokaal op Railway's filesystem) ---
STATE_FILE = os.environ.get("STATE_FILE", "state.json")


def validate():
    missing = []
    for name in ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]:
        if not globals()[name]:
            missing.append(name)
    if missing:
        raise RuntimeError(
            f"Ontbrekende environment variables: {', '.join(missing)}. "
            "Zet deze in Railway onder Variables."
        )
