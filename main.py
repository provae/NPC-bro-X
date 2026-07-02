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
from content_pool import PHOTO_SCENES, TEXT_POSTS, REPLY_POOL
from twitter_client import get_client, get_api_v1, post_text, post_photo, authenticate_test, reply_to_tweet

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


def maybe_engage(client, state):
    if config.ENGAGE_INTERVAL_HOURS <= 0 or not config.TARGET_ACCOUNTS:
        return
    last = state.get("last_engage_timestamp")
    now = datetime.utcnow()
    if last:
        last_dt = datetime.fromisoformat(last)
        if now - last_dt < timedelta(hours=config.ENGAGE_INTERVAL_HOURS):
            return
    try:
        username = random.choice(config.TARGET_ACCOUNTS)
        user = client.get_user(username=username)
        if not user.data:
            return
        tweets = client.get_users_tweets(user.data.id, max_results=5)
        if tweets.data:
            tweet = random.choice(tweets.data)
            client.like(tweet.id)
            logger.info("Geliked: @%s tweet %s", username, tweet.id)
        state["last_engage_timestamp"] = now.isoformat()
        state_mod.save_state(state)
    except Exception:
        logger.exception("Engagen mislukt, ga door.")


def maybe_reply(client, state):
    if not config.REPLY_ENABLED or not REPLY_POOL:
        return
    replies_today = state.get("replies_today", 0)
    last_reply_date = state.get("last_reply_date")
    today = datetime.utcnow().date().isoformat()
    
    # Reset counter als het een nieuwe dag is
    if last_reply_date != today:
        replies_today = 0
        state["replies_today"] = 0
        state["last_reply_date"] = today
    
    # Stop als we het limiet hebben bereikt
    if replies_today >= config.REPLIES_PER_DAY:
        return
    
    try:
        # Zoek tweets met de opgegeven hashtags
        hashtag = random.choice(config.REPLY_HASHTAGS)
        search_results = client.search_recent_tweets(query=hashtag, max_results=10, tweet_fields=["author_id"])
        
        if not search_results.data:
            return
        
        # Filter tweets van onszelf en replies
        my_id = client.get_me().data.id
        valid_tweets = [t for t in search_results.data if t.author_id != my_id and not t.text.startswith("@")]
        
        if not valid_tweets:
            return
        
        # Kies een random tweet om op te reageren
        target_tweet = random.choice(valid_tweets)
        
        # Kies een random reply
        reply_idx = state_mod.pick_next(len(REPLY_POOL), "used_reply_indices", state)
        reply_text = REPLY_POOL[reply_idx]
        
        # Plaats reply
        reply_to_tweet(client, target_tweet.id, reply_text)
        
        # Update state
        state["replies_today"] = replies_today + 1
        state["last_reply_date"] = today
        state_mod.save_state(state)
        
        logger.info("Reply #%d van %d voor vandaag geplaatst", state["replies_today"], config.REPLIES_PER_DAY)
        
    except Exception:
        logger.exception("Reply mislukt, ga door.")


def run_forever():
    config.validate()
    client = get_client()
    api_v1 = get_api_v1()
    authenticate_test(client)

    state = state_mod.load_state()

    while True:
        do_one_post(client, api_v1, state)
        maybe_engage(client, state)
        maybe_reply(client, state)

        wait_minutes = random.randint(config.MIN_INTERVAL_MINUTES, config.MAX_INTERVAL_MINUTES)
        logger.info("Volgende post over %d minuten.", wait_minutes)
        time.sleep(wait_minutes * 60)


def run_single_test():
    """Test-mode: post 1x en stop. Gebruik: python main.py test"""
    config.validate()
    client = get_client()
    api_v1 = get_api_v1()
    authenticate_test(client)
    state = state_mod.load_state()
    do_one_post(client, api_v1, state)
    logger.info("Test-post voltooid.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_single_test()
    else:
        run_forever()
