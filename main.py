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
    try:
        tweets = await fetch_tweets(req.handle)
        results = await analyze_tweets_async(tweets)

        summary = {
            "high": sum(1 for r in results if r["risk"] == "High"),
            "medium": sum(1 for r in results if r["risk"] == "Medium"),
            "low": sum(1 for r in results if r["risk"] == "Low"),
            "safe": sum(1 for r in results if r["risk"] == "Safe"),
        }

        score = (
            summary["high"] * 4 +
            summary["medium"] * 3 +
            summary["low"] * 2
        )

        max_possible = len(results) * 4

        crisis_score = int((score / max_possible) * 100) if max_possible > 0 else 0
        
        if crisis_score > 70:
          risk_level = "High"
        elif crisis_score > 40:
          risk_level = "Medium"
        elif crisis_score > 10:
          risk_level = "Low"
        else:
           risk_level = "Safe" 


        return {
            "handle": req.handle,
            "total": len(tweets),
            "summary": summary,
            "crisis_score": crisis_score,
            "risk_level": risk_level,
            "results": results
        }
       


        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }