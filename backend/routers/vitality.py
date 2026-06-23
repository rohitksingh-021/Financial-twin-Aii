"""Vitality Score route."""

from fastapi import APIRouter
from store.data_store import store
from engines.vitality_engine import compute_vitality_score

router = APIRouter()


@router.get("/vitality")
def get_vitality():
    data = store.get_customer()
    return compute_vitality_score(data)
