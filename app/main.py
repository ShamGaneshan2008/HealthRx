from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class ChatRequest(BaseModel):
    message: str

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API ROUTE
@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a helpful health assistant."},
                    {"role": "user", "content": req.message}
                ]
            }
        )

        data = response.json()

        if "choices" not in data:
            return {"reply": "AI error: " + str(data)}

        return {"reply": data["choices"][0]["message"]["content"]}

    except Exception as e:
        return {"reply": "Server error: " + str(e)}


# STATIC (MUST BE LAST)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")