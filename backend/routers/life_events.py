"""Life Events route."""

from fastapi import APIRouter
from store.data_store import store
from engines.life_event_engine import predict_life_events

router = APIRouter()


@router.get("/life-events")
def get_life_events():
    data = store.get_customer()
    return predict_life_events(data)
