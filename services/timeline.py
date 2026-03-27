import os
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "powerai~twitter-timeline-scraper"

async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip()

    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    payload = {
        "username": username,
        "maxTweets": limit,
        "startDate": start_date,
        "endDate": end_date
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if data:
                logger.warning("APIFY ITEM KEYS: %s", list(data[0].keys()))

        tweets = []
        for item in data:
            tweets.append({
                "id": str(item.get("id") or item.get("tweetId") or item.get("tweet_id", "")),
                "username": item.get("author", {}).get("userName") or item.get("username", username),
                "content": item.get("text") or item.get("fullText", ""),
                "created_at": item.get("createdAt") or item.get("created_at", ""),
                "url": item.get("url") or f"https://twitter.com/{username}/status/{item.get('id') or item.get('tweetId', '')}"
            })

        return tweets

    except Exception as e:
        return {"error": f"Apify failed: {str(e)}"}