"""AI Advisor route."""

from fastapi import APIRouter
from pydantic import BaseModel
from store.data_store import store
from engines.advisor_engine import generate_recommendations, generate_chat_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.get("/advisor/recommendations")
def get_recommendations():
    data = store.get_customer()
    return generate_recommendations(data)


@router.post("/advisor/chat")
def chat(req: ChatRequest):
    data = store.get_customer()
    return generate_chat_response(data, req.message)
