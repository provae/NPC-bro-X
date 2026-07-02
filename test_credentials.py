"""
Test script om X/Twitter credentials te testen.
Draai dit script lokaal om te checken of je API keys werken.
"""

import tweepy

# Vul hier je credentials in
API_KEY = "5WlVRmZDKnoENLsUkSvXSrJW3"
API_SECRET = "kIEd3pFjPUcB6NBDAEGumiObDvPzUe02rLSRVHSCqFb3ZcvYQo"
ACCESS_TOKEN = "2072413851794944000-YbeTUDZ4uxhxc2k3g5KDXgGygYdgMN"
ACCESS_SECRET = "oLi9mHQXfHvulVKNpAYmWNfLmEpY1y1rPWLP48icR8zcD"

print("Testing X/Twitter credentials...")

try:
    # Test OAuth 1.0a authenticatie
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
    )
    
    # Test call om te checken of authenticatie werkt
    me = client.get_me()
    
    if me.data:
        print(f"✅ SUCCESS! Ingelogd als: @{me.data.username}")
        print(f"User ID: {me.data.id}")
        print(f"Naam: {me.data.name}")
    else:
        print("❌ FAILED: Kon user info niet ophalen")
        
except tweepy.errors.Unauthorized as e:
    print(f"❌ 401 Unauthorized: Je credentials zijn onjuist of hebben geen schrijfrechten")
    print(f"Error: {e}")
    
except tweepy.errors.Forbidden as e:
    print(f"❌ 403 Forbidden: Je app heeft niet de juiste permissions")
    print(f"Error: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")
