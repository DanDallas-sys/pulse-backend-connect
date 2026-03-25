import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

async def fetch_tweets(username: str, limit: int = 50):
    url = f"https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": f"from:{username}",
        "max_results": limit  # 🔥 dynamic now
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()

    tweets = []

    if "data" in data:
        for tweet in data["data"]:
            tweets.append({
                "id": tweet["id"],
                "text": tweet["text"]
            })

    return tweets

async def fetch_latest_tweet(handle):
    tweets = await fetch_tweets(handle)
    return tweets[0] if tweets else None