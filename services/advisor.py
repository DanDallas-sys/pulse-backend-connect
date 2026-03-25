from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat_with_ai(message, context=None):
    system_prompt = """
You are Pulse AI — a high-level reputation advisor.

You help users:
- Identify risky content
- Improve their public image
- Avoid backlash
- Make smarter posting decisions

Be sharp, practical, and insightful.
Avoid generic advice.
"""

    # Inject scan context if available
    context_text = ""
    if context:
        context_text = f"""
Here is the user's account analysis:

Crisis Score: {context.get("crisis_score")}
Risk Level: {context.get("risk_level")}

Summary:
High: {context.get("summary", {}).get("high")}
Medium: {context.get("summary", {}).get("medium")}
Low: {context.get("summary", {}).get("low")}

Top Risky Tweets:
{context.get("top_risks")}
"""

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_text},
            {"role": "user", "content": message}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content