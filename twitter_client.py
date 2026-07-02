"""
twitter_client.py
Wrapper rond tweepy voor authenticatie, posten en engagen.
"""

import os
import logging
import tweepy

import config

logger = logging.getLogger("npcbro.twitter")


def get_client() -> tweepy.Client:
    """OAuth 1.0a user-context client voor tweets/media/likes."""
    return tweepy.Client(
        consumer_key=config.X_API_KEY,
        consumer_secret=config.X_API_SECRET,
        access_token=config.X_ACCESS_TOKEN,
        access_token_secret=config.X_ACCESS_SECRET,
    )


def get_api_v1() -> tweepy.API:
    """v1.1 API nodig voor media upload (tweepy v2 Client kan dit niet)."""
    auth = tweepy.OAuth1UserHandler(
        config.X_API_KEY,
        config.X_API_SECRET,
        config.X_ACCESS_TOKEN,
        config.X_ACCESS_SECRET,
    )
    return tweepy.API(auth)


def post_text(client: tweepy.Client, text: str):
    resp = client.create_tweet(text=text)
    logger.info("Tekst-post geplaatst: %s", resp.data)
    return resp


def post_photo(client: tweepy.Client, api_v1: tweepy.API, image_filename: str, caption: str):
    image_path = os.path.join(config.IMAGES_DIR, image_filename)
    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Afbeelding niet gevonden: {image_path}. "
            "Check of de bestandsnaam matcht met content_pool.py."
        )
    media = api_v1.media_upload(image_path)
    resp = client.create_tweet(text=caption, media_ids=[media.media_id])
    logger.info("Foto-post geplaatst: %s (%s)", resp.data, image_filename)
    return resp


def authenticate_test(client: tweepy.Client):
    """Test-call om te checken of de keys werken, zonder te posten."""
    me = client.get_me()
    logger.info("Authenticatie OK, ingelogd als: %s", me.data)
    return me
