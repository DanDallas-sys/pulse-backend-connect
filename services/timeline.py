# services/timeline.py

import os
import httpx
from datetime import datetime, timezone

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "powerai~twitter-timeline-scraper"

async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip()

    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    payload = {
        "username": username,
        "maxTweets": limit,
        "startDate": start_date,   # format: YYYY-MM-DD
        "endDate": end_date
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        tweets = []
        for item in data:
            tweets.append({
                "id": str(item.get("id", "")),
                "username": item.get("author", {}).get("userName", username),
                "content": item.get("text", ""),
                "created_at": item.get("createdAt", ""),
                "url": item.get("url", "")
            })

        return tweets

    except Exception as e:
        return {"error": f"Apify failed: {str(e)}"}