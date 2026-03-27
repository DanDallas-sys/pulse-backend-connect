import os
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "powerai~twitter-timeline-scraper"

async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip()

    trigger_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"

    payload = {
        "screenname": username,
        "maxTweets": limit,
        "startDate": start_date,
        "endDate": end_date
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            # Step 1 — trigger the run async
            run_response = await client.post(trigger_url, json=payload)
            run_response.raise_for_status()
            run_data = run_response.json()
            run_id = run_data["data"]["id"]
            dataset_id = run_data["data"]["defaultDatasetId"]
            logger.warning(f"Apify run started: {run_id}")

            # Step 2 — poll until finished or timeout (max 90 seconds)
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            elapsed = 0
            while elapsed < 90:
                await asyncio.sleep(5)
                elapsed += 5
                status_resp = await client.get(status_url)
                status = status_resp.json()["data"]["status"]
                logger.warning(f"Apify run status: {status} ({elapsed}s)")

                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break

            # Step 3 — fetch whatever results were saved regardless of status
            results_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
            results_resp = await client.get(results_url)
            data = results_resp.json()

        if not isinstance(data, list):
            return {"error": "Unexpected response from Apify"}

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