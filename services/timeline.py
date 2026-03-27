import snscrape.modules.twitter as sntwitter
from datetime import datetime

async def fetch_user_timeline_range(username, start_date, end_date, limit=50):
    username = username.replace("@", "").strip()

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    tweets = []

    scraper = sntwitter.TwitterUserScraper(username)

    count = 0

    try:
        for tweet in scraper.get_items():
            tweet_date = tweet.date.replace(tzinfo=None)

            # STOP EARLY if too old
            if tweet_date < start:
                break

            # COLLECT IF IN RANGE
            if start <= tweet_date <= end:
                tweets.append({
                    "id": str(tweet.id),
                    "username": tweet.user.username,
                    "content": tweet.content,
                    "created_at": tweet.date.isoformat(),
                    "url": tweet.url
                })
                count += 1

            # HARD LIMIT
            if count >= limit:
                break

    except Exception as e:
        return {"error": f"Scraper failed: {str(e)}"}

    return tweets