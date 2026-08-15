from fastapi import FastAPI
from pydantic import BaseModel

from answer import ask


app = FastAPI(
    title="RegRadar",
    description="RBI Regulatory Intelligence API",
    version="1.0.0",
)


class Question(BaseModel):
    text: str


@app.post("/ask")
def ask_endpoint(q: Question):
    return {
        "answer": ask(q.text)
    }


@app.get("/health")
def health():
    return {
        "status": "alive"
    }