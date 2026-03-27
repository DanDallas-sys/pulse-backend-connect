import snscrape.modules.twitter as sntwitter
from datetime import datetime

async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip().lower()

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    tweets = []

    scraper = sntwitter.TwitterUserScraper(username)

    try:
        for tweet in scraper.get_items():
            tweet_date = tweet.date.replace(tzinfo=None)

            # 🔥 FILTER BY DATE (Fix 2)
            if tweet_date < start:
                break  # stop early (important for performance)

            if start <= tweet_date <= end:
                tweets.append({
                    "id": str(tweet.id),
                    "username": tweet.user.username,
                    "content": tweet.content,
                    "created_at": tweet.date.isoformat(),
                    "url": tweet.url
                })

            if len(tweets) >= limit:
                break

    except Exception as e:
        return {"error": str(e)}

    return tweets