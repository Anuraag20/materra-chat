from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from openai import OpenAI
import os 

from pydantic import BaseModel

client = OpenAI(
    api_key=os.getenv('LLM_API_KEY'),
    base_url=os.getenv('LLM_BASE_URL')
)


app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str


origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def chat_response(messages):    
    response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Materra clients."},
                *messages
            ],
            stream=True
        )
    for chunk in response:
        yield chunk.choices[0].delta.content

@app.post("/")
async def root(data: list[ChatMessage]):
    return StreamingResponse(chat_response(data))
