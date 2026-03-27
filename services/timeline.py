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
        "screenname": username,
        "maxTweets": limit,
        "startDate": start_date,
        "endDate": end_date
    }

    logger.warning(f"Apify payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            
            # Accept partial results even if actor crashed mid-run
            if response.status_code not in [200, 201]:
                logger.warning(f"Apify returned status {response.status_code}")
                return {"error": f"Apify returned status {response.status_code}"}

            data = response.json()

        if not isinstance(data, list):
            return {"error": "Unexpected response from Apify"}

        if len(data) == 0:
            return []

        tweets = []
        for item in data:
            author = item.get("author", {})
            tweet_id = str(item.get("tweet_id", ""))
            username_out = author.get("username") or author.get("userName") or username
            tweets.append({
                "id": tweet_id,
                "username": username_out,
                "content": item.get("text", ""),
                "created_at": item.get("created_at", ""),
                "url": f"https://twitter.com/{username_out}/status/{tweet_id}"
            })

        return tweets

    except Exception as e:
        return {"error": f"Apify failed: {str(e)}"}