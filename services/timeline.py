import os
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "apidojo~tweet-scraper"

async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip()

    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    # Uses Twitter advanced search syntax — most reliable approach
    search_query = f"from:{username} since:{start_date} until:{end_date}"

    payload = {
        "searchTerms": [search_query],
        "maxItems": limit,
        "queryType": "Latest"
    }

    logger.warning(f"Apify payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, list):
            return {"error": "Unexpected response from Apify"}

        tweets = []
        for item in data:
            author = item.get("author", {})
            tweet_id = str(item.get("id") or item.get("tweet_id") or "")
            user = author.get("userName") or author.get("username") or username
            tweets.append({
                "id": tweet_id,
                "username": user,
                "content": item.get("text") or item.get("fullText", ""),
                "created_at": item.get("createdAt") or item.get("created_at", ""),
                "url": item.get("url") or f"https://twitter.com/{user}/status/{tweet_id}"
            })

        return tweets

    except Exception as e:
        return {"error": f"Apify failed: {str(e)}"}