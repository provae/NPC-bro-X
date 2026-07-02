"""
main.py
Entrypoint van de NPCBRO X-automation bot.
Start command op Railway: python main.py
"""

import logging
import random
import time
import sys
from datetime import datetime, timedelta

import config
import state as state_mod
from content_pool import PHOTO_SCENES, TEXT_POSTS
from twitter_client import get_client, get_api_v1, post_text, post_photo, authenticate_test

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("npcbro.main")


def do_one_post(client, api_v1, state):
    is_photo = random.random() < config.PHOTO_POST_CHANCE and PHOTO_SCENES
    try:
        if is_photo:
            idx = state_mod.pick_next(len(PHOTO_SCENES), "used_photo_indices", state)
            filename, caption = PHOTO_SCENES[idx]
            post_photo(client, api_v1, filename, caption)
        else:
            idx = state_mod.pick_next(len(TEXT_POSTS), "used_text_indices", state)
            post_text(client, TEXT_POSTS[idx])
        state_mod.save_state(state)
    except Exception:
        logger.exception("Posten mislukt, ga door naar volgende cyclus.")


def run_forever():
    config.validate()
    client = get_client()
    api_v1 = get_api_v1()
    authenticate_test(client)

    state = state_mod.load_state()

    while True:
        do_one_post(client, api_v1, state)

        wait_minutes = random.randint(config.MIN_INTERVAL_MINUTES, config.MAX_INTERVAL_MINUTES)
        logger.info("Volgende post over %d minuten.", wait_minutes)
        time.sleep(wait_minutes * 60)


def run_single_test():
    """Test-mode: post 1x en stop. Gebruik: python main.py test"""
    config.validate()
    client = get_client()
    authenticate_test(client)
    state = state_mod.load_state()
    do_one_post(client, None, state)
    logger.info("Test-post voltooid.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_single_test()
    else:
        run_forever()
