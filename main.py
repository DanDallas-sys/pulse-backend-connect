from fastapi import FastAPI
from pydantic import BaseModel
from services.twitter import fetch_tweets
from services.analyzer import analyze_tweets_async
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ScanRequest(BaseModel):
    handle: str

@app.post("/scan")
async def scan_account(req: ScanRequest):
    tweets = await fetch_tweets(req.handle)

    results = await analyze_tweets_async(tweets)

    summary = {
        "high": sum(1 for r in results if r["risk"] == "High"),
        "medium": sum(1 for r in results if r["risk"] == "Medium"),
        "low": sum(1 for r in results if r["risk"] == "Low"),
        "safe": sum(1 for r in results if r["risk"] == "Safe"),
    }

    return {
        "handle": req.handle,
        "total": len(tweets),
        "summary": summary,
        "results": results
    }