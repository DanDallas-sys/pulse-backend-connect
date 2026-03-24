from fastapi import FastAPI
from pydantic import BaseModel
from services.twitter import fetch_tweets
from services.analyzer import analyze_tweets_async
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-this"
)

#This code is for twitter login connection
oauth = OAuth()

oauth.register(
    name="twitter",
    client_id=os.getenv("TWITTER_CLIENT_ID"),
    client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
    request_token_url="https://api.twitter.com/oauth/request_token",
    authorize_url="https://api.twitter.com/oauth/authorize",
    access_token_url="https://api.twitter.com/oauth/access_token",
    api_base_url="https://api.twitter.com/1.1/",
)

#This is the code the login button will hit
@app.get("/auth/twitter/login")
async def twitter_login(request: Request):
    try:
        redirect_uri = request.url_for("twitter_callback")
        return await oauth.twitter.authorize_redirect(request, redirect_uri)
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

#This is the code that sends the user back to the app after successful twitter login
@app.get("/auth/twitter/callback")
async def twitter_callback(request: Request):
    token = await oauth.twitter.authorize_access_token(request)

    # token contains:
    # oauth_token, oauth_token_secret, user_id, screen_name

    user = await oauth.twitter.get(
        "account/verify_credentials.json",
        token=token
    )

    profile = user.json()

    return {
        "message": "Twitter connected successfully",
        "user": profile,
        "tokens": token
    }

"THIS IS THE CODE USED FOR SEARCHING THROUGH TWITTER HANDLES"
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

        dangerous = [r for r in results if r["risk"] in ["High", "Medium"]]
        top_risks = dangerous[:3]


        return {
            "handle": req.handle,
            "crisis_score": crisis_score,
            "risk_level": risk_level,
            "top_risks": top_risks,
            "summary": summary,
            "results": results
        }
       


        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }