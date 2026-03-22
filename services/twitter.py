import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

async def fetch_tweets(username: str):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=from:{username}&max_results=50"

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()

    tweets = []

    if "data" in data:
        for tweet in data["data"]:
            tweets.append({
                "id": tweet["id"],
                "text": tweet["text"]
            })

    return tweets