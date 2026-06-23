"""Stress Monitor route."""

from fastapi import APIRouter
from store.data_store import store
from engines.stress_engine import analyze_stress

router = APIRouter()


@router.get("/stress")
def get_stress():
    data = store.get_customer()
    return analyze_stress(data)
