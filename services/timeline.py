# services/timeline.py

import os
from twikit import Client
from datetime import datetime, timezone

# Singleton client - initialized once
_client = None

async def get_client() -> Client:
    global _client
    if _client is not None:
        return _client

    client = Client('en-US')
    cookies_path = 'cookies.json'

    # Reuse saved cookies to avoid logging in every request
    try:
        client.load_cookies(cookies_path)
    except Exception:
        await client.login(
            auth_info_1=os.getenv("TWITTER_USERNAME"),
            auth_info_2=os.getenv("TWITTER_EMAIL"),
            password=os.getenv("TWITTER_PASSWORD"),
            cookies_file=cookies_path
        )

    _client = client
    return client


async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip()

    start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

    tweets_collected = []

    try:
        client = await get_client()

        # Get user object first
        user = await client.get_user_by_screen_name(username)

        # Fetch tweets (twikit returns paginated results)
        tweets = await user.get_tweets('Tweets', count=limit)

        while tweets:
            for tweet in tweets:
                tweet_date = tweet.created_at_datetime

                # Normalize timezone
                if tweet_date.tzinfo is None:
                    tweet_date = tweet_date.replace(tzinfo=timezone.utc)

                # Too old — stop paginating
                if tweet_date < start:
                    return tweets_collected

                # In range — collect
                if start <= tweet_date <= end:
                    tweets_collected.append({
                        "id": str(tweet.id),
                        "username": username,
                        "content": tweet.text,
                        "created_at": tweet.created_at,
                        "url": f"https://twitter.com/{username}/status/{tweet.id}"
                    })

                if len(tweets_collected) >= limit:
                    return tweets_collected

            # Paginate to next batch
            tweets = await tweets.next()

    except Exception as e:
        return {"error": f"Twikit failed: {str(e)}"}

    return tweets_collected
