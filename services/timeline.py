import snscrape.modules.twitter as sntwitter

async def fetch_user_timeline_range(username: str, start_date: str, end_date: str, limit: int = 50):
    username = username.replace("@", "").strip().lower()

    query = f"from:{username} since:{start_date} until:{end_date}"

    tweets = []

    for i, tweet in enumerate(
        sntwitter.TwitterSearchScraper(query).get_items()
    ):
        tweets.append({
            "id": str(tweet.id),
            "username": tweet.user.username,
            "content": tweet.content,
            "created_at": tweet.date.isoformat(),
            "url": tweet.url
        })

        if i >= limit:
            break

    return tweets