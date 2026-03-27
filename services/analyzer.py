import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json
import re

def extract_json(text):
    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except:
        # fallback: try to extract JSON manually
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a reputation risk analyzer.

Be STRICT and realistic.

Return ONLY valid JSON:

{{
  "risk": "High | Medium | Low | Safe",
  "reason": "short explanation"
}}

Rules:
- High = offensive, discriminatory, cancel-worthy
- Medium = controversial, politically sensitive, or could spark backlash
- Low = slightly questionable or could be misinterpreted
- Safe = completely neutral

IMPORTANT:
- Do not default to Safe
- If there is ANY potential backlash, classify at least Low or Medium

Tweet: "{tweet}"
"""

async def classify_tweet(tweet):
    tweet_text = tweet.get("text") or tweet.get("content", "")
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": PROMPT_TEMPLATE.format(tweet=tweet_text)}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        
        parsed = extract_json(content)
        return {
            "tweet": tweet_text,
            "risk": parsed.get("risk", "Unknown"),
            "reason": parsed.get("reason", ""),
            "url": tweet.get("url")  # 🔥 ADD THIS
        }
    except Exception:
        return {
            "tweet": tweet_text,
            "risk": "Unknown",
            "reason": content,
            "url": tweet.get("url")  # 🔥 ADD THIS
        }


async def analyze_tweets_async(tweets):
    tasks = [classify_tweet(t) for t in tweets]

    results = await asyncio.gather(*tasks)

    return results