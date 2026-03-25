from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat_with_ai(message, context=None):
    system_prompt = """
You are Pulse AI — an advanced reputation advisor.

You are NOT a generic chatbot.
You ALREADY have access to the user's social media analysis.

Never say:
- "I can't access your posts"
- "Please provide more data"

You MUST use the provided analysis to answer.

Be direct, practical, and specific.
"""

    context_text = ""
    if context:
        context_text = f"""
USER ACCOUNT ANALYSIS (ALREADY AVAILABLE TO YOU):

- Crisis Score: {context.get("crisis_score")}
- Risk Level: {context.get("risk_level")}

- High Risk Tweets: {context.get("summary", {}).get("high")}
- Medium Risk Tweets: {context.get("summary", {}).get("medium")}
- Low Risk Tweets: {context.get("summary", {}).get("low")}

- Top Risky Content:
{context.get("top_risks")}
"""

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_text},  # 👈 IMPORTANT
            {"role": "user", "content": message}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content