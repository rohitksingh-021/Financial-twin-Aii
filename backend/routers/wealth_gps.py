"""Wealth GPS route."""

from fastapi import APIRouter
from store.data_store import store
from engines.gps_engine import compute_wealth_gps

router = APIRouter()


@router.get("/wealth-gps")
def get_wealth_gps():
    data = store.get_customer()
    return compute_wealth_gps(data)
