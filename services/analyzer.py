import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a reputation risk analyzer.

Return ONLY valid JSON:

{
  "risk": "High" | "Medium" | "Low" | "Safe",
  "reason": "short explanation"
}

Rules:
- High = offensive, discriminatory, cancel-worthy
- Medium = controversial or insensitive
- Low = slightly questionable
- Safe = no issue

Tweet: "{tweet}"
"""

async def classify_tweet(tweet_text):
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": PROMPT_TEMPLATE.format(tweet=tweet_text)}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        import json
        parsed = json.loads(content)
        return {
            "tweet": tweet_text,
            "risk": parsed.get("risk", "Unknown"),
            "reason": parsed.get("reason", "")
        }
    except:
        return {
            "tweet": tweet_text,
            "risk": "Unknown",
            "reason": content
        }


async def analyze_tweets_async(tweets):
    tasks = [classify_tweet(t["text"]) for t in tweets]

    results = await asyncio.gather(*tasks)

    return results